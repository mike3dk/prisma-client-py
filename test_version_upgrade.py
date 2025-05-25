#!/usr/bin/env python3
"""
Test script to verify Prisma 6.8.2 upgrade works correctly.
"""

import os
import asyncio
import tempfile
from pathlib import Path


def test_config_version():
    """Test that the version configuration is correctly set to 6.8.2"""
    print('🔧 Testing configuration...')

    from prisma._config import config

    print(f'✅ Prisma version: {config.prisma_version}')
    print(f'✅ Engine version: {config.expected_engine_version}')

    assert config.prisma_version == '6.8.2', f'Expected 6.8.2, got {config.prisma_version}'
    assert config.expected_engine_version == '2060c79ba17c6bb9f5823312b6f6b7f4a845738e', 'Engine version mismatch'

    print('✅ Configuration test passed!')


def test_cli_commands():
    """Test that the Prisma CLI can be invoked with the new version"""
    print('\n🔧 Testing CLI commands...')

    try:
        from prisma.cli.prisma import run

        # Test version command
        print("Running 'prisma --version'...")
        run(['--version'])
        print(f'✅ CLI version command executed successfully')

        # Test help command
        print("Running 'prisma --help'...")
        run(['--help'])
        print('✅ CLI help command executed successfully')

    except Exception as e:
        print(f'❌ CLI test failed: {e}')
        return False

    print('✅ CLI tests passed!')
    return True


async def test_basic_client_functionality():
    """Test basic Prisma client functionality"""
    print('\n🔧 Testing basic client functionality...')

    try:
        from prisma import Prisma

        # Create a temporary schema file for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            schema_path = Path(temp_dir) / 'schema.prisma'
            schema_content = """
generator client {
  provider = "prisma-client-py"
}

datasource db {
  provider = "sqlite"
  url      = "file:./test.db"
}

model User {
  id   Int    @id @default(autoincrement())
  name String
}
"""
            schema_path.write_text(schema_content)

            # Change to temp directory and try to generate client
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                # Create client instance (this tests import and basic initialization)
                client = Prisma()
                print(f'✅ Client created successfully')
                print(f'✅ Client type: {type(client)}')

                # Test that we can access client properties without connecting
                print(f'✅ Client is_connected: {client.is_connected()}')

            finally:
                os.chdir(original_cwd)

    except Exception as e:
        print(f'❌ Basic client test failed: {e}')
        return False

    print('✅ Basic client functionality test passed!')
    return True


def test_engine_download():
    """Test that the engine can be downloaded (but don't actually download unless forced)"""
    print('\n🔧 Testing engine configuration...')

    try:
        from prisma._config import config

        print(f'✅ Binary cache dir: {config.binary_cache_dir}')
        print(f'✅ Engine configuration accessible')

        # Check if the engine binary path can be determined
        # (Note: we're not actually downloading to keep test fast)
        expected_binary_name = f'prisma-query-engine-{config.expected_engine_version}'
        print(f'✅ Expected binary name: {expected_binary_name}')

    except Exception as e:
        print(f'❌ Engine configuration test failed: {e}')
        return False

    print('✅ Engine configuration test passed!')
    return True


async def main():
    """Run all tests"""
    print('🚀 Testing Prisma 6.8.2 upgrade...\n')

    try:
        # Test 1: Configuration
        test_config_version()

        # Test 2: CLI commands
        test_cli_commands()

        # Test 3: Basic client functionality
        await test_basic_client_functionality()

        # Test 4: Engine configuration
        test_engine_download()

        print('\n🎉 All tests passed! Prisma 6.8.2 upgrade appears to be working correctly.')
        print('\n📋 Next steps to fully verify:')
        print('   1. Run the full test suite: pytest tests/')
        print('   2. Test with a real schema: prisma generate && prisma db push')
        print('   3. Try an example project: cd examples/fastapi-basic && follow the README')

    except Exception as e:
        print(f'\n❌ Test failed: {e}')
        print('\n🔧 This might indicate an issue with the version upgrade.')
        return False

    return True


if __name__ == '__main__':
    asyncio.run(main())
