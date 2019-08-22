
## A minimalist Python package for algorithmic music notation

[Kodou](https://www.urbandictionary.com/define.php?term=kodou) is a small package for engraving music written in Python 3.5.3. It uses the [Lilypond](http://lilypond.org/) compiler (versions 2.18 to 2.21.0) for rendering and generating its output data.

Kodou was originally inspired by [a tutorial by Bernd Klein](https://www.python-course.eu/python_scores.php) on creating musical scores using Python.

Kodou is under active development. Feel free to report bugs, instabilities or feature wishes.


A fast demo:

```python
# import it
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
![output](/jpg/start_kodou_out.jpg)

# Installation
Get Kodou's source from it's [GitHub repository](https://github.com/amirteymuri/Kodou) and put it on your Python path. Of course you also need [LilyPond](http://lilypond.org/). For some fine microtonal adjustments you might want to have [Ekmelily](http://www.ekmelic-music.org/en/extra/ekmelily.htm) installed besides LilyPond.

# [Documentation](./documentation.md)