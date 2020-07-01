from setuptools import setup
import os

VERSION = "0.2"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-saved-queries",
    description="Datasette plugin that lets users save and execute queries",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-saved-queries",
    project_urls={
        "Issues": "https://github.com/simonw/datasette-saved-queries/issues",
        "CI": "https://github.com/simonw/datasette-saved-queries/actions",
        "Changelog": "https://github.com/simonw/datasette-saved-queries/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["datasette_saved_queries"],
    entry_points={"datasette": ["saved_queries = datasette_saved_queries"]},
    install_requires=["datasette>=0.45", "sqlite-utils"],
    extras_require={"test": ["pytest", "pytest-asyncio", "httpx"]},
    tests_require=["datasette-saved-queries[test]"],
)
