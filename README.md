
[__Klarenz__](https://en.wikipedia.org/wiki/Clarence_Barlow) is a very minimalist and _pythonistic_ package for compiling Lilypond sheet music.

Klarenz requires Python 3.5 or later:

```
    ~$ python --version
    Python 3.10.12
```

Klarenz requires LilyPond 2.21.0 or later.
Make sure LilyPond is installed: http://lilypond.org/development.html
Make sure LilyPond is callable from the commandline:

```
    $ lilypond --version
    GNU LilyPond 2.22.2
```

Create a Python 3 virtual environment for Klarenz: https://docs.python.org/3/tutorial/venv.html
Activate the virtual environment and then use pip to install Klarenz:

```
    ~$ python -m pip install klarenz
```

Start Python, import Klarenz and print some notes:


```
    from klarenz import *
    proc(Part({"notes": range(60, 72), "onsets": range(0, 12)}))
```


![Quick Test Klarenz Music Notation](docs/readme-example.jpg)




- - -
<small>Klarenz is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.<br>
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.<br>
See the [GNU General Public License](http://www.gnu.org/licenses/) for more details.</small>
