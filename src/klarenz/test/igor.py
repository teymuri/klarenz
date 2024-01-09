from itertools import accumulate
from klarenz import *


def x():
    timesigs = ((3, 4), (2, 4), (2, 4))
    bar_count_patt = (3, 2, 2)
    i = 0
    init = 0
    while 1:
        next_bar = init + bar_count_patt[i]
        yield ((init, next_bar), timesigs[i])
        i += 1
        i %= len(bar_count_patt)
        init = next_bar

cello_notes = (
    51, (49, 36), 49, 51, 49,
    51, (49, 36), 49,
    51, (49, 36), 49
) * 14
cello_durs = (
    .5, .5, 1, .5, .5,
    .5, .5, 1,
    .5, .5, 1
) * 14
cello_beats = list(accumulate(cello_durs, initial=0))
g=x()

proc(
    Part({"notes": cello_notes, "beats": cello_beats}, 
         {
             "clef": {"default": "bass"},
             "timesig": {k:v for k,v in [next(g) for _ in range(14*3)]},
             # "barline": {cello_beats[-1]-1: "|."}
         })
)

# proc(Part({"notes": range(60, 78), "beats": range(78-60)}))
