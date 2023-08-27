from setuptools import setup

version = {}
with open("datasette_sqlite_robotstxt/version.py") as fp:
    exec(fp.read(), version)

VERSION = version['__version__']


setup(
    name="datasette-sqlite-robotstxt",
    description="",
    long_description="",
    long_description_content_type="text/markdown",
    author="Alex Garcia",
    url="https://github.com/asg017/sqlite-robotstxt",
    project_urls={
        "Issues": "https://github.com/asg017/sqlite-robotstxt/issues",
        "CI": "https://github.com/asg017/sqlite-robotstxt/actions",
        "Changelog": "https://github.com/asg017/sqlite-robotstxt/releases",
    },
    license="MIT License, Apache License, Version 2.0",
    version=VERSION,
    packages=["datasette_sqlite_robotstxt"],
    entry_points={"datasette": ["sqlite_robotstxt = datasette_sqlite_robotstxt"]},
    install_requires=["datasette", "sqlite-robotstxt"],
    extras_require={"test": ["pytest"]},
    python_requires=">=3.6",
)
