"""

"""

def durs_to_beats(durs, init_beat=0):
    """Returns a list of (accumulated onset, corresponding duration).
    The initial onset is the desired starting onset."""
    durs = list(durs) # convert to pop
    beats = []
    while durs:
        beats.append(init_beat)
        init_beat += durs.pop(0)
    return beats

