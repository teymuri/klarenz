"""
72-tone equal-temperament system (72-EDO) up to the five-quarter-tone,
i.e. 15 twelfth-tones up and down
http://www.ekmelic-music.org/en/extra/alter.htm#note-enh
"""

from fractions import Fraction
from math import (floor, modf)

# german
UPWARD_CHROMATIC_SCALE = {0: "c", 1: "cis", 2: "d", 3: "dis",
                          4: "e", 5: "f", 6: "fis", 7: "g",
                          8: "gis", 9: "a", 10: "ais", 11: "h"}
DOWNWARD_CHROMATIC_SCALE = {0: "c", 1: "des", 2: "d", 3: "es",
                            4: "e", 5: "f", 6: "ges", 7: "g",
                            8: "as", 9: "a", 10: "b", 11: "h"}
UPWARD_MICROTONES = {0: "",
                     Fraction(1/6).limit_denominator(): "ir",
                     Fraction(1/3).limit_denominator(): "il",
                     Fraction(1/2).limit_denominator(): "ih",
                     Fraction(2/3).limit_denominator(): "isel",
                     Fraction(5/6).limit_denominator(): "iser"}
DOWNWARD_MICROTONES = {0: "",
                       Fraction(1/6).limit_denominator(): "er",
                       Fraction(1/3).limit_denominator(): "el",
                       Fraction(1/2).limit_denominator(): "esih",
                       Fraction(2/3).limit_denominator(): "esil",
                       Fraction(5/6).limit_denominator(): "esir"}

def midi_to_name(midi, step):
    octave = int(floor(midi // 12) - 4)  # 4th octave is without sign in lilypond
    oct_sign = "," if octave < 0 else ("'" if octave > 0 else "")
    oct_sign *=  abs(octave)
    microtones, pitch = modf(midi % 12)
    if step < 0:
        p = DOWNWARD_CHROMATIC_SCALE[pitch]
        m = DOWNWARD_MICROTONES[Fraction(microtones).limit_denominator()]
    elif step >= 0:
        p = UPWARD_CHROMATIC_SCALE[pitch]
        m = UPWARD_MICROTONES[Fraction(microtones).limit_denominator()]
    return p + m + oct_sign
