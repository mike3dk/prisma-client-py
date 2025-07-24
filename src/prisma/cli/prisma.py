from __future__ import annotations

import os
import re
import sys
import json
import logging
import subprocess
from typing import Any, Dict, List, Optional, NamedTuple
from pathlib import Path

import click

from .. import config
from ._node import npm, node
from ..errors import PrismaError

log: logging.Logger = logging.getLogger(__name__)


# Generator property ordering for consistent schema formatting
GENERATOR_PROPERTY_ORDER = [
    'provider',
    'interface', 
    'recursive_type_depth',
    'output',
    'enable_experimental_decimal',
    'partial_type_generator',
    'engine_type',
]


def _format_schema_file(schema_path: Path) -> bool:
    """Format generator properties in a Prisma schema file.
    
    Returns True if the file was modified, False otherwise.
    """
    if not schema_path.exists():
        return False
    
    content = schema_path.read_text()
    
    def format_generator_block(match: re.Match[str]) -> str:
        name = match.group(1)
        block_content = match.group(2)
        
        # Parse properties from the generator block
        properties = {}
        for line in block_content.strip().split('\n'):
            line = line.strip()
            if '=' in line and not line.startswith('//'):
                key, value = line.split('=', 1)
                properties[key.strip()] = value.strip()
        
        # Format with consistent ordering
        lines = [f'generator {name} {{']
        
        # Add properties in the desired order
        for prop in GENERATOR_PROPERTY_ORDER:
            if prop in properties:
                lines.append(f'  {prop:<23} = {properties[prop]}')
        
        # Add any remaining properties not in the predefined order
        for prop, value in properties.items():
            if prop not in GENERATOR_PROPERTY_ORDER:
                lines.append(f'  {prop:<23} = {value}')
        
        lines.append('}')
        return '\n'.join(lines)
    
    # Replace all generator blocks with formatted versions
    generator_pattern = r'generator\s+([\w-]+)\s*\{([^}]+)\}'
    formatted_content = re.sub(generator_pattern, format_generator_block, content, flags=re.MULTILINE | re.DOTALL)
    
    # Only write if content changed
    if formatted_content != content:
        schema_path.write_text(formatted_content)
        return True
    
    return False


def run(
    args: List[str],
    check: bool = False,
    env: Optional[Dict[str, str]] = None,
) -> int:
    """Run a Prisma CLI command with automatic schema formatting.
    
    This function automatically formats generator properties in schema files
    after successful `db pull` and `format` commands to ensure consistent
    property ordering. This behavior can be disabled by setting the
    PRISMA_PY_DISABLE_AUTO_FORMAT environment variable.
    """
    log.debug('Running prisma command with args: %s', args)

    default_env = {
        **os.environ,
        'PRISMA_HIDE_UPDATE_MESSAGE': 'true',
        'PRISMA_CLI_QUERY_ENGINE_TYPE': 'binary',
    }
    env = {**default_env, **env} if env is not None else default_env

    # Check if this is a command that might modify the schema
    is_db_pull = len(args) >= 2 and args[0] == 'db' and args[1] == 'pull'
    is_format = len(args) >= 1 and args[0] == 'format'
    should_format_schema = is_db_pull or is_format
    schema_path = None
    
    # Extract schema path from args if present
    if should_format_schema:
        for i, arg in enumerate(args):
            if arg.startswith('--schema='):
                schema_path = Path(arg.split('=', 1)[1])
                break
            elif arg == '--schema' and i + 1 < len(args):
                schema_path = Path(args[i + 1])
                break
        
        # Default schema path if not specified
        if schema_path is None:
            schema_path = Path('prisma/schema.prisma')

    # TODO: ensure graceful termination
    entrypoint = ensure_cached().entrypoint
    process = node.run(
        str(entrypoint),
        *args,
        env=env,
        check=check,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    # Post-process schema file if command was successful and formatting is enabled
    # Can be disabled with PRISMA_PY_DISABLE_AUTO_FORMAT=1 environment variable
    if (should_format_schema and process.returncode == 0 and schema_path and schema_path.exists() 
        and not os.environ.get('PRISMA_PY_DISABLE_AUTO_FORMAT')):
        try:
            if _format_schema_file(schema_path) and is_db_pull:
                click.echo(f'✓ Formatted generator properties in {schema_path}')
        except Exception as e:
            log.warning(f'Failed to format schema file {schema_path}: {e}')

    if args and args[0] in {'--help', '-h'}:
        click.echo(click.style('Python Commands\n', bold=True))
        click.echo('  ' + 'For Prisma Client Python commands run ' + click.style('prisma py --help', bold=True))

    return process.returncode


class CLICache(NamedTuple):
    cache_dir: Path
    entrypoint: Path


DEFAULT_PACKAGE_JSON: dict[str, Any] = {
    'name': 'prisma-binaries',
    'version': '1.0.0',
    'private': True,
    'description': 'Cache directory created by Prisma Client Python to store Prisma Engines',
    'main': 'node_modules/prisma/build/index.js',
    'author': 'RobertCraigie',
    'license': 'Apache-2.0',
}


def ensure_cached() -> CLICache:
    cache_dir = config.binary_cache_dir
    entrypoint = cache_dir / 'node_modules' / 'prisma' / 'build' / 'index.js'

    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)

    # We need to create a dummy `package.json` file so that `npm` doesn't try
    # and search for it elsewhere.
    #
    # If it finds a different `package.json` file then the `prisma` package
    # will be installed there instead of our cache directory.
    package = cache_dir / 'package.json'
    if not package.exists():
        package.write_text(json.dumps(DEFAULT_PACKAGE_JSON))

    if not entrypoint.exists():
        click.echo('Installing Prisma CLI')

        try:
            proc = npm.run(
                'install',
                f'prisma@{config.prisma_version}',
                cwd=config.binary_cache_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if proc.returncode != 0:
                click.echo(
                    f'An error ocurred while installing the Prisma CLI; npm install log: {proc.stdout.decode("utf-8")}'
                )
                proc.check_returncode()
        except Exception:
            # as we use the entrypoint existing to check whether or not we should run `npm install`
            # we need to make sure it doesn't exist if running `npm install` fails as it will otherwise
            # lead to a broken state, https://github.com/RobertCraigie/prisma-client-py/issues/705
            if entrypoint.exists():
                try:
                    entrypoint.unlink()
                except Exception:
                    pass
            raise

    if not entrypoint.exists():
        raise PrismaError(
            f'CLI installation appeared to complete but the expected entrypoint ({entrypoint}) could not be found.'
        )

    return CLICache(cache_dir=cache_dir, entrypoint=entrypoint)
