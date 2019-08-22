
__Kodou__ is a small package for engraving music written in Python 3.5.3. It was originally inspired by [a tutorial by Bernd Klein](https://www.python-course.eu/python_scores.php) on creating musical scores using Python.


A fast demo:

```python
import kodou


# create a Part object
part = kodou.Part(events={
    # specify some microtonal notes and some beats
    "notes": [n + 1/6 for n in range(60, 85)] + [85],
    "beats":
    [n * 1/7 for n in range(7)] + \
    [1 + (n * 1/6) for n in range(6)] + \
    [2 + (n * 1/5) for n in range(5)] + \
    [3 + (n * 1/4) for n in range(4)] + \
    [4 + (n * 1/3) for n in range(3)] + [5]},
            # add some metadata to them
            metadata={
                "articulation": {(0, 1): ("^", ".", "-"),
                                 (1, 2): (">", "trill"),
                                 (2, 3): ("marcato", "prallprall", "+"),
                                 (3, 4): "reverseturn",
                                 (4, 5): ("shortfermata", "prallmordent", "<>"),
                                 5: "marcato"},
                "dynamic": {0: "sf", 1: "sf", 2: "sf", 3: "sf", 4: "sf", 5: "fff",
                            (0, 1): ">", (1, 2): "dim", (2, 3): "<", (3, 4): ">", (4, 5): "cresc"},
                "legato": {"solid": [(0, 1), (4, 5)],
                           "dotted": [(1, 2), (3, 4)],
                           "halfdashed": [(2, 3)]},
                "barline": {4: "!", 5: "|."}
            })
# and process everything
kodou.kodou(part)
```

Kodou outputs:
![Kodou's output](./docs/jpg/start_kodou_out.jpg)


Kodou is under active development. Feel free to report bugs, instabilities or feature wishes.


For more information please visit [Kodou's Homepage](https://kodou.readthedocs.io).
<br>
For discussion and questions please join [kodou's googlegroup](https://groups.google.com/d/forum/kodou-discuss) or send an email to the mailing list: [kodou-discuss@googlegroups.com].
<br>

- - -

<small>Kodou is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.<br>
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.<br>
See the [GNU General Public License](http://www.gnu.org/licenses/) for more details.</small>
