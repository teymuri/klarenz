"""
Helper functions
"""

def dur_to_onset(durs, initos=0):
    """Returns a list of (accumulated onset, corresponding duration).
    The initial onset is the desired starting onset."""
    durs = list(durs) # convert to pop
    onsets = []
    while durs:
        d = durs.pop(0)
        onsets.append((d, initos))
        initos += d
    return onsets

