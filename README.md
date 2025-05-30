<br />

<div align="center">
    <h1>Prisma Client Python</h1>
    <p><h3 align="center">Type-safe database access for Python</h3></p>
    <div align="center">
    <a href="https://discord.gg/HpFaJbepBH">
        <img src="https://img.shields.io/discord/933860922039099444?color=blue&label=chat&logo=discord" alt="Chat on Discord">
    </a>
    <a href="https://prisma.io">
        <img src="https://img.shields.io/static/v1?label=prisma&message=5.19.0&color=blue&logo=prisma" alt="Supported Prisma version is 5.19.0">
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2FJacobCoffee%2Fbfb02a83c8da3cbf53f7772f2cee02ec%2Fraw%2Facb94daa3aedecda67e2c7d8c5aec9765db0734d%2Fformat-badge.json" alt="Code style: ruff">
    </a>
    <a href="https://robertcraigie.github.io/prisma-client-py/htmlcov/index.html">
        <img src="https://raw.githubusercontent.com/RobertCraigie/prisma-client-py/static/coverage/coverage.svg" alt="Code coverage report">
    </a>
    <img src="https://img.shields.io/github/actions/workflow/status/RobertCraigie/prisma-client-py/test.yml?branch=main&label=tests" alt="GitHub Workflow Status (main)">
    <img src="https://img.shields.io/pypi/pyversions/prisma" alt="Supported python versions">
    <img src="https://img.shields.io/pypi/v/prisma" alt="Latest package version">
    </div>
</div>

> [!WARNING]
> Prisma Client Python is no longer being maintained. See [this issue](https://github.com/RobertCraigie/prisma-client-py/issues/1073) for more information.

<hr>

## What is Prisma Client Python?

Prisma Client Python is a next-generation ORM built on top of [Prisma](https://github.com/prisma/prisma) that has been designed from the ground up for ease of use and correctness.

[Prisma](https://www.prisma.io/) is a TypeScript ORM with zero-cost type safety for your database, although don't worry, Prisma Client Python [interfaces](#how-does-prisma-python-interface-with-prisma) with Prisma using Rust, you don't need Node or TypeScript.

Prisma Client Python can be used in _any_ Python backend application. This can be a REST API, a GraphQL API or _anything_ else that needs a database.

![GIF showcasing Prisma Client Python usage](https://raw.githubusercontent.com/RobertCraigie/prisma-client-py/main/docs/showcase.gif)

> _Note that the only language server that is known to support this form of autocompletion is Pylance / Pyright._

## Why should you use Prisma Client Python?

Unlike other Python ORMs, Prisma Client Python is **fully type safe** and offers native support for usage **with and without** `async`. All you have to do is [specify the type of client](https://prisma-client-py.readthedocs.io/en/stable/getting_started/setup/) you would like to use for your project in the [Prisma schema file](#the-prisma-schema).

However, the arguably best feature that Prisma Client Python provides is [autocompletion support](#auto-completion-for-query-arguments) (see the GIF above). This makes writing database queries easier than ever!

Core features:

- [Prisma Migrate](https://www.prisma.io/docs/concepts/components/prisma-migrate)
- [Full type safety](https://prisma-client-py.readthedocs.io/en/stable/getting_started/type-safety/)
- [With / without async](https://prisma-client-py.readthedocs.io/en/stable/getting_started/setup/)
- [Recursive and pseudo-recursive types](https://prisma-client-py.readthedocs.io/en/stable/reference/config/#recursive-type-depth)
- [Atomic updates](https://prisma-client-py.readthedocs.io/en/stable/reference/operations/#updating-atomic-fields)
- [Complex cross-relational queries](https://prisma-client-py.readthedocs.io/en/stable/reference/operations/#filtering-by-relational-fields)
- [Partial type generation](https://prisma-client-py.readthedocs.io/en/stable/reference/partial-types/)
- [Batching write queries](https://prisma-client-py.readthedocs.io/en/stable/reference/batching/)

Supported database providers:

- PostgreSQL
- MySQL
- SQLite
- CockroachDB
- MongoDB (experimental)
- SQL Server (experimental)

## Support

Have any questions or need help using Prisma? Join the [community discord](https://discord.gg/HpFaJbepBH)!

If you don't want to join the discord you can also:

- Create a new [discussion](https://github.com/RobertCraigie/prisma-client-py/discussions/new)
- Ping me on the [Prisma Slack](https://slack.prisma.io/) `@Robert Craigie`

## How does Prisma work?

This section provides a high-level overview of how Prisma works and its most important technical components. For a more thorough introduction, visit the [documentation](https://prisma-client-py.readthedocs.io).

### The Prisma schema

Every project that uses a tool from the Prisma toolkit starts with a [Prisma schema file](https://www.prisma.io/docs/concepts/components/prisma-schema). The Prisma schema allows developers to define their _application models_ in an intuitive data modeling language. It also contains the connection to a database and defines a _generator_:

```prisma
// database
datasource db {
  provider = "sqlite"
  url      = "file:database.db"
}

// generator
generator client {
  provider             = "prisma-client-py"
  recursive_type_depth = 5
}

// data models
model Post {
  id        Int     @id @default(autoincrement())
  title     String
  content   String?
  views     Int     @default(0)
  published Boolean @default(false)
  author    User?   @relation(fields: [author_id], references: [id])
  author_id Int?
}

model User {
  id    Int     @id @default(autoincrement())
  email String  @unique
  name  String?
  posts Post[]
}
```

In this schema, you configure three things:

- **Data source**: Specifies your database connection. In this case we use a local SQLite database however you can also use an environment variable.
- **Generator**: Indicates that you want to generate Prisma Client Python.
- **Data models**: Defines your application models.

---

On this page, the focus is on the generator as this is the only part of the schema that is specific to Prisma Client Python. You can learn more about [Data sources](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-schema/data-sources) and [Data models](https://www.prisma.io/docs/concepts/components/prisma-schema/data-model/) on their respective documentation pages.

### Prisma generator

A prisma schema can define one or more generators, defined by the `generator` block.

A generator determines what assets are created when you run the `prisma generate` command. The `provider` value defines which Prisma Client will be created. In this case, as we want to generate Prisma Client Python, we use the `prisma-client-py` value.

You can also define where the client will be generated to with the `output` option. By default Prisma Client Python will be generated to the same location it was installed to, whether that's inside a virtual environment, the global python installation or anywhere else that python packages can be imported from.

For more options see [configuring Prisma Client Python](https://prisma-client-py.readthedocs.io/en/stable/reference/config/).

---

### Accessing your database with Prisma Client Python

Just want to play around with Prisma Client Python and not worry about any setup? You can try it out online on [gitpod](https://gitpod.io/#https://github.com/RobertCraigie/prisma-py-async-quickstart).

#### Installing Prisma Client Python

The first step with any python project should be to setup a virtual environment to isolate installed packages from your other python projects, however that is out of the scope for this page.

In this example we'll use an asynchronous client, if you would like to use a synchronous client see [setting up a synchronous client](https://prisma-client-py.readthedocs.io/en/stable/getting_started/setup/#synchronous-client).

```sh
pip install -U prisma
```

#### Generating Prisma Client Python

Now that we have Prisma Client Python installed we need to actually generate the client to be able to access the database.

Copy the Prisma schema file shown above to a `schema.prisma` file in the root directory of your project and run:

```sh
prisma db push
```

This command will add the data models to your database and generate the client, you should see something like this:

```
Prisma schema loaded from schema.prisma
Datasource "db": SQLite database "database.db" at "file:database.db"

SQLite database database.db created at file:database.db


🚀  Your database is now in sync with your schema. Done in 26ms

✔ Generated Prisma Client Python to ./.venv/lib/python3.9/site-packages/prisma in 265ms
```

It should be noted that whenever you make changes to your `schema.prisma` file you will have to re-generate the client, you can do this automatically by running `prisma generate --watch`.

The simplest asynchronous Prisma Client Python application will either look something like this:

```py
import asyncio
from prisma import Prisma

async def main() -> None:
    prisma = Prisma()
    await prisma.connect()

    # write your queries here
    user = await prisma.user.create(
        data={
            'name': 'Robert',
            'email': 'robert@craigie.dev'
        },
    )

    await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
```

or like this:

```py
import asyncio
from prisma import Prisma
from prisma.models import User

async def main() -> None:
    db = Prisma(auto_register=True)
    await db.connect()

    # write your queries here
    user = await User.prisma().create(
        data={
            'name': 'Robert',
            'email': 'robert@craigie.dev'
        },
    )

    await db.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
```

#### Query examples

For a more complete list of queries you can perform with Prisma Client Python see the [documentation](https://prisma-client-py.readthedocs.io/en/stable/reference/operations/).

All query methods return [pydantic models](https://pydantic-docs.helpmanual.io/usage/models/).

**Retrieve all `User` records from the database**

```py
users = await db.user.find_many()
```

**Include the `posts` relation on each returned `User` object**

```py
users = await db.user.find_many(
    include={
        'posts': True,
    },
)
```

**Retrieve all `Post` records that contain `"prisma"`**

```py
posts = await db.post.find_many(
    where={
        'OR': [
            {'title': {'contains': 'prisma'}},
            {'content': {'contains': 'prisma'}},
        ]
    }
)
```

**Create a new `User` and a new `Post` record in the same query**

```py
user = await db.user.create(
    data={
        'name': 'Robert',
        'email': 'robert@craigie.dev',
        'posts': {
            'create': {
                'title': 'My first post from Prisma!',
            },
        },
    },
)
```

**Update an existing `Post` record**

```py
post = await db.post.update(
    where={
        'id': 42,
    },
    data={
        'views': {
            'increment': 1,
        },
    },
)
```

#### Usage with static type checkers

All Prisma Client Python methods are fully statically typed, this means you can easily catch bugs in your code without having to run it!

For more details see the [documentation](https://prisma-client-py.readthedocs.io/en/stable/getting_started/type-safety/).

#### How does Prisma Client Python interface with Prisma?

Prisma Client Python connects to the database and executes queries using Prisma's rust-based Query Engine, of which the source code can be found here: https://github.com/prisma/prisma-engines.

Prisma Client Python exposes a CLI interface which wraps the [Prisma CLI](https://www.prisma.io/docs/reference/api-reference/command-reference). This works by downloading a Node binary, if you don't already have Node installed on your machine, installing the CLI with `npm` and running the CLI using Node.

The CLI interface is the exact same as the standard [Prisma CLI](https://www.prisma.io/docs/reference/api-reference/command-reference) with [some additional commands](https://prisma-client-py.readthedocs.io/en/stable/reference/command-line/).

## Affiliation

Prisma Client Python is _not_ an official Prisma product although it is very generously sponsored by Prisma.

## Room for improvement

Prisma Client Python is a fairly new project and as such there are some features that are missing or incomplete.

### Auto completion for query arguments

Prisma Client Python query arguments make use of `TypedDict` types. Support for completion of these types within the Python ecosystem is now fairly widespread. This section is only here for documenting support.

Supported editors / extensions:

- VSCode with [pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) v2021.9.4 or higher
- Sublime Text with [LSP-Pyright](https://github.com/sublimelsp/LSP-pyright) v1.1.196 or higher
- PyCharm [2022.1 EAP 3](<https://youtrack.jetbrains.com/articles/PY-A-233537928/PyCharm-2022.1-EAP-3-(221.4994.44-build)-Release-Notes>) added support for completing `TypedDict`s
  - This does not yet work for Prisma Client Python unfortunately, see [this issue](https://youtrack.jetbrains.com/issue/PY-54151/TypedDict-completion-at-callee-does-not-work-for-methods)
- Any editor that supports the Language Server Protocol and has an extension supporting Pyright v1.1.196 or higher
  - vim and neovim with [coc.nvim](https://github.com/fannheyward/coc-pyright)
  - [emacs](https://github.com/emacs-lsp/lsp-pyright)

```py
user = await db.user.find_first(
    where={
        '|'
    }
)
```

Given the cursor is where the `|` is, an IDE should suggest the following completions:

- id
- email
- name
- posts

### Performance

While there has currently not been any work done on improving the performance of Prisma Client Python queries, they should be reasonably fast as the core query building and connection handling is performed by Prisma.
Performance is something that will be worked on in the future and there is room for massive improvements.

### Supported platforms

Windows, MacOS and Linux are all officially supported.

## Version guarantees

Prisma Client Python is _not_ stable.

Breaking changes will be documented and released under a new **MINOR** version following this format.

`MAJOR`.`MINOR`.`PATCH`

New releases are scheduled bi-weekly, however as this is a solo project, no guarantees are made that this schedule will be stuck to.

## Contributing

We use [conventional commits](https://www.conventionalcommits.org) (also known as semantic commits) to ensure consistent and descriptive commit messages.

See the [contributing documentation](https://prisma-client-py.readthedocs.io/en/stable/contributing/contributing/) for more information.

## Attributions

This project would not be possible without the work of the amazing folks over at [prisma](https://www.prisma.io).

Massive h/t to [@steebchen](https://github.com/steebchen) for his work on [prisma-client-go](https://github.com/prisma/prisma-client-go) which was incredibly helpful in the creation of this project.

This README is also heavily inspired by the README in the [prisma/prisma](https://github.com/prisma/prisma) repository.
