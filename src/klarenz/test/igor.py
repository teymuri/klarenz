from itertools import accumulate
import klarenz as K


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

cello_start_durs = (3, 2, 2)
cello_start_rests = ("r", "r", "r")
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
cello_end_rests = ("r", "r", "r")
cello_end_durs = (3, 2, 2)
cello_beats = list(accumulate(cello_start_durs + cello_durs + cello_end_durs, initial=0))
g=x()
bar_patt = [next(g) for _ in range(16*3)]

cello_part = K.Part(
    {"notes": cello_start_rests + cello_notes + cello_end_rests, "beats": cello_beats}, 
    {
        "clef": {"default": "bass"},
        "timesig": {k:v for k,v in bar_patt},
        "barline": {}
    })

##### v1

v1_start_rests = ("r", "r", "r")
v1_start_durs = (3, 2, 2)
v1_notes = (
    67, 69, 71, 72, 69,
    71, 72, 71, 69, 67,
    69, 71, 67,
    69, 67, "r", 69,
    67, "r", 69, 67, 69,
    71, 72, 71, 69,
        67, 69, 67, "r",
    72, 71, 69, 67, 69,
    71, 72, 71, 69,
        67, 69,
) * 4
v1_durs = (
    .5, .5, 1, .5, .5, 
    .5, .5, .5, .25, .25,
    .5, 1, .5,
    1, .5, .5, 1,
    .5, .5, .5, .25, .25,
    .5, .5, .5, 1,
    .5, 1, .5, .5, 
    .5, .5, .5, .25, .25,
    .5, .5, .5, 1,
    .5, 1
) * 4
v1_last_cycle_notes = (
    67, 69, 71, 
    72, 69, 71, 72,
    71, 72, 71, 69, 67,
    "r", "r"
)
v1_last_cylce_durs = (
    .5, .5, 1,
    .5, .5, .5, .5, 
    .5, .25, .25, .5, 3.5,
    2, 2
)
v1_durs = v1_start_durs + v1_durs + v1_last_cylce_durs
v1_beats = list(accumulate(v1_durs, initial=0))
# print(v1_durs)
# print(v1_beats)
# print(len(v1_durs) == len(v1_beats), len(v1_notes + v1_start_rests + v1_last_cycle_notes), len(v1_beats), len(v1_durs))
v1_part = K.Part({"notes": v1_start_rests + v1_notes + v1_last_cycle_notes, "beats": v1_beats, "durs": {k:v for k, v in zip(v1_beats, v1_durs)}},
               {"clef": {"default": "treble"}, "timesig": {k: v for k, v in bar_patt}})

K.proc([v1_part, cello_part])

# proc(K.Part({"notes": range(60, 78), "beats": range(78-60)}))
