<h1><center>Kodou</center></h1>
<h2><center>a minimalist Python package for engraving music</center></h2>

<br>
<br>


[Kodou](https://www.urbandictionary.com/define.php?term=kodou) is a small interface for the [Lilypond](http://lilypond.org/) compiler (versions 2.18 to 2.21.0) written in Python 3.5.3.

- - -

A fast demo:

<pre><code>
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
</code></pre>

![Kodou's output](attachimage?page=Kodou&file=start_kodou_out.jpg)
<br>

For more information please visit the [__Documentation__](https://chiselapp.com/user/amirt/repository/Kodou/doc/tip/kodou.markdown) page.
<br>
For discussion and questions please join [kodou's googlegroup](https://groups.google.com/d/forum/kodou-discuss) or send an email to <a href="mailto:kodou-discuss@googlegroups.com">the mailing list</a>: [kodou-discuss@googlegroups.com].
<br>

- - -

<small>Kodou is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.<br>
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.<br>
See the [GNU General Public License](http://www.gnu.org/licenses/) for more details.</small>



<h5>© Copyright 2018 Amir Teymuri</h5>


