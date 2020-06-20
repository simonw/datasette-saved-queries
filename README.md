# datasette-saved-queries

[![PyPI](https://img.shields.io/pypi/v/datasette-saved-queries.svg)](https://pypi.org/project/datasette-saved-queries/)
[![Changelog](https://img.shields.io/github/v/release/simonw/datasette-saved-queries?label=changelog)](https://github.com/simonw/datasette-saved-queries/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-saved-queries/blob/master/LICENSE)

Datasette plugin that lets users save and execute queries

## Installation

Install this plugin in the same environment as Datasette.

    $ pip install datasette-saved-queries

## Usage

Usage instructions go here.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:

    cd datasette-saved-queries
    python -mvenv venv
    source venv/bin/activate

Or if you are using `pipenv`:

    pipenv shell

Now install the dependencies and tests:

    pip install -e '.[test]'

To run the tests:

    pytest
