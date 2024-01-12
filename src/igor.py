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
bar_patt = [next(g) for _ in range(14*3)]

cello_part = K.Part({"notes": cello_notes, "beats": cello_beats}, 
                  {
                      "clef": {"default": "bass"},
                      "timesig": {k:v for k,v in bar_patt},
                      "barline": {}
                  })

##### v1

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
) * 5
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
) * 5
v1_beats = list(accumulate(v1_durs, initial=0))
v1_part = K.Part({"notes": v1_notes, "beats": v1_beats, "durs": v1_durs},
               {"clef": {"default": "treble"}, "timesig": {k: v for k, v in bar_patt}})

# K.proc([v1_part])

# proc(K.Part({"notes": range(60, 78), "beats": range(78-60)}))
