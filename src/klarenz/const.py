

# limit fractions denominator
LIMIT = pow(10, 6)



# the define separator
USER_DEFINE_OPERATOR = "=>"



# md will be processed in _make_obj in this order
# _ is the placeholder for the _Note obj
# ORDERED_METADATA = ("float_barline", "clef", "timesig",
#                     "notehead", "slur_type", "_",
#                     "slur", "articulation", "dynamic",
#                     "int_barline")
PRE_TUPLET_METADATA = ("clef", "timesig")
POST_TUPLET_METADATA = ("float_barline", "notehead", "slur_type", "_",
                        "slur", "articulation", "dynamic", "int_barline")



# for one voice
STAFF_TYPES = {
    "basic": "Staff",
    "drum": "DrumStaff",
    "rhythmic": "RhythmicStaff",
    "tablature": "TabStaff",
    "mensural": "MensuralStaff",
    "vaticana": "VaticanaStaff",
    "gregorian": "GregorianTranscriptionStaff"
}
# for polyphony
STAFF_BINDING_TYPES = {
    "basic": None,
    "group": "StaffGroup",
    "choir": "ChoirStaff",
    "grand": "GrandStaff",
    "piano": "PianoStaff"
}


PHRASING_SLUR_TYPES = {
    "solid" : "\phrasingSlurSolid",
    "halfsolid" : "\phrasingSlurHalfSolid",
    "dashed" : "\phrasingSlurDashed",
    "halfdashed" : "\phrasingSlurHalfDashed",
    "dotted" : "\phrasingSlurDotted"
}
SLUR_TYPES = {
    "solid" : "\slurSolid",
    "halfsolid" : "\slurHalfSolid",
    "dashed" : "\slurDashed",
    "halfdashed" : "\slurHalfDashed",
    "dotted" : "\slurDotted",
}
# DYNAMICS = {
#     "ppppp" : "\ppppp",
#     "pppp" : "\pppp",
#     "ppp" : "\ppp",
#     "pp" : "\pp",
#     "p" : "\p",
#     "mp" : "\mp",
#     "mf" : "\mf",
#     "f" : "\\f",
#     "ff" : "\\ff",
#     "fff" : "\\fff",
#     "ffff" : "\\ffff",
#     "fffff" : "\\fffff",
#     "fp" : "\\fp",
#     "sf" : "\sf",
#     "sff" : "\sff",
#     "sp" : "\sp",
#     "spp" : "\spp",
#     "sfz" : "\sfz",
#     "rfz" : "\\rfz",
#     # growing dynamics
#     "<" : "\<",
#     "cresc" : "\cresc",
#     ">" : "\>",
#     "decresc" : "\decresc",
#     "dim" : "\dim"
# }


# These can be used as transposing clefs,
# which will be processed in proc.py
CLEFS = ("C", "F", "G", "G2", "GG", "alto", "altovarC", "baritone", "baritonevarC", "baritonevarF", "bass", "blackmensural-c1", "blackmensural-c2", "blackmensural-c3", "blackmensural-c4", "blackmensural-c5", "french", "hufnagel-do-fa", "hufnagel-do1", "hufnagel-do2", "hufnagel-do3", "hufnagel-fa1", "hufnagel-fa2", "kievan-do", "medicaea-do1", "medicaea-do2", "medicaea-do3", "medicaea-fa1", "medicaea-fa2", "mensural-c1", "mensural-c2", "mensural-c3", "mensural-c4", "mensural-c5", "mensural-f", "mensural-g", "mezzosoprano", "moderntab", "neomensural-c1", "neomensural-c2", "neomensural-c3", "neomensural-c4", "neomensural-c5", "percussion", "petrucci-c1", "petrucci-c2", "petrucci-c3", "petrucci-c4", "petrucci-c5", "petrucci-f", "petrucci-f2", "petrucci-f3", "petrucci-f4", "petrucci-f5", "petrucci-g", "petrucci-g1", "petrucci-g2", "soprano", "subbass", "tab", "tenor", "tenorG", "tenorvarC", "treble", "varC", "varbaritone", "varpercussion", "vaticana-do1", "vaticana-do2", "vaticana-do3", "vaticana-fa1", "vaticana-fa2", "violin")


_make_notehead = lambda notehead: "\override NoteHead.style = #'{} ".format(notehead)
NOTEHEADS = {notehead: _make_notehead(notehead) for notehead in (
    "default", "altdefault", "baroque", "neomensural",
    "mensural", "petrucci", "harmonic", "harmonic-black",
    "harmonic-mixed", "diamond", "cross", "xcircle",
    "triangle", "slash",
    "do", "re", "mi", "fa", "#f", "la", "ti"
)}

_make_articulation = lambda articulation: "\{}".format(articulation)
ARTICULATIONS = {articulation: _make_articulation(articulation) for articulation in (
    "accent", "espressivo", "marcato", "portato",
    "staccatissimo", "staccato", "tenuto",
    "prall", "prallup", "pralldown", "upprall",
    "downprall", "prallprall", "lineprall", "prallmordent",
    "mordent", "upmordent", "downmordent", "trill", "turn",
    "reverseturn", "shortfermata", "fermata", "longfermata",
    "verylongfermata", "upbow", "downbow", "flageolet",
    "open", "halfopen", "lheel", "rheel", "ltoe", "rtoe",
    "snappizzicato", "stopped", "segno", "coda", "varcoda",
    "accentus", "circulus", "ictus", "semicirculus", "signumcongruentiae"
)}
_make_abbreviated_articulation = lambda articulation: "-{}".format(articulation)
ARTICULATIONS.update({articulation: _make_abbreviated_articulation(articulation) for articulation in (
    ">", "^", "_",
    "!", ".", "-", "+", 
)})
ARTICULATIONS.update({"<>": "\espressivo"})


# global metadata
# sticky metadata has a default for setting things back to it
GLOBAL_METADATA = {
    # "invisible": None,
    # "enharmonics": None,
    # "note_type": "midi",
    # string, herz

    # "who": "Klarenz",
    "who": "_klarenz",
    "what": {},
    # sticky metadata
    "timesig": {"default": (4, 4)},
    "notehead": {"default": "\\revert NoteHead.style "},
    "clef": {"default": "treble"},
    "dynamic": {"default": "!"},
    # unsticky metadata
    "articulation": {},
    "barline": {},
    "legato": {},
    # ganz anderes md
    "staff": {"types": "basic"},
    "copyright": []
}


# lilypond output formats
LP_OUTPUT_FORMATS = {
    "pdf": "-fpdf",           # generate PDF files (default)
    "png": "-fpng",           # generate PNG files
    "ps": "-dbackend=ps",             # generate PostScript files
    "eps": "-dbackend=eps",             # generate Encapsulated PostScript files
    "svg": "-dbackend=svg",
    # "eps": "-dbackend=eps"
}

# Seconds to wait before opening the pdf with the pdf viewer
PDFVIEW_WAIT = 4


DOTFILE = "~/.klarenz"

# default settings for dotfile parameter
LY_MIN_VERSION = "2.21.0"
LY_DEFAULT_LANG = "deutsch"
LOAD_EKMELILY = "no"
LY_DEFAULT_STAFF_SZ = "14"
LY_DEFAULT_PAPER_SZ = "quarto"
