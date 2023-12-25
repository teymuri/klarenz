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
