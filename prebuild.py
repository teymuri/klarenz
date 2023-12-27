from src.klarenz.version import *


toml = f"""
[build-system]
requires = [ "setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "klarenz"
version = "{version}"
authors = [
    {{ name="Amir Teymuri", email="amiratwork22@gmail.com" }}, 
]
description = "Programmatically generate Lilypond scores, with ease and elegance of pure Python"
readme = "README.md"
requires-python = ">=3.5"
classifiers = [ 
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU Affero General Public License v3",
    "Operating System :: OS Independent",
]

[project.urls]
"Homepage" = "https://github.com/teymuri/klarenz.git"
"Bug Tracker" = "https://github.com/teymuri/klarenz/issues"
"""

with open("pyproject.toml", "w") as f:
    f.write(toml)


readme = f"""
[__Klarenz__](https://en.wikipedia.org/wiki/Clarence_Barlow) is a highly minimalist (the entire API consists of a single class `Part` and a main processor function `proc`!) and Pythonic package for compiling Lilypond sheet music.

For more information check the [documentation page](https://teymuri.github.io/klarenz-docs/).

# Current release: v{version}

# Packaging
Ensure to update the `src/klarenz/version.py` file and run `python prebuild.py` (and push them!) before initiating the build-upload process for each release.
"""

with open("README.md", "w") as f:
    f.write(readme)
