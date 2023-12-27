
from math import modf
from copy import copy
from fractions import Fraction

from .rhythm import (_superior_binary, lcm, superior_x, factorize,
                    nearest_binary, tuplet_label)
from .ly import (TAGLINE, PAPER, HEADER_TAGLINE,
                UNEQUAL_LENGTH_MEASURES_POLYMETRY, make_header)
from .const import (LIMIT, NOTEHEADS, CLEFS,
                   PRE_TUPLET_METADATA, POST_TUPLET_METADATA,
                   ARTICULATIONS, GLOBAL_METADATA, LY_MIN_VERSION,
                   LY_DEFAULT_LANG, LY_DEFAULT_STAFF_SZ, LY_DEFAULT_PAPER_SZ,
                   LOAD_EKMELILY)
from .cfg import _copyright


def group_by(L, pred=lambda x, y: x == y):
    """"""
    groups = []
    group = []
    for i, item in enumerate(L):
        group.append(item)
        try:
            next_item = L[i + 1]
            if not pred(item, next_item):
                groups.append(group)
                group = []
        except IndexError:
            # group is always at least 1 item long.
            groups.append(group)
    return groups


def parse_lilyvals(lilyvals):
    # First sum up adjecant identical values
    # untill no adjecant identical values exist.
    identity_groups = group_by(lilyvals)
    summed_lilyvals = []
    for group in identity_groups:
        sup_bin = _superior_binary(len(group))
        summed_lilyvals.append(group[0] // sup_bin)
        still_remaining = divmod(len(group), sup_bin)[1]
        if still_remaining:
            summed_lilyvals.extend(still_remaining * [group[0]])
    if summed_lilyvals == lilyvals:
        # No more adjecant identical values
        return group_by(summed_lilyvals, lambda x, y: x * 2 == y)
    else:
        return parse_lilyvals(summed_lilyvals)
    

def _next_dict_key(D, inc=1):
    """"""
    return max(D) + inc


def _equivalent_fractions(f1, f2):
    """make two fractions equivalent"""
    d1, d2 = f1.denominator, f2.denominator
    n1, n2 = f1.numerator, f2.numerator
    lcm_ = lcm(d1, d2)
    fact1, fact2 = lcm_ // d1, lcm_ // d2
    return (n1 * fact1, lcm_), (n2 * fact2, lcm_)


def distribute_voice_staff(voice, staff):
    """divide voices btwn. stave"""
    assert voice >= staff, "Number of stave should be less than number of voices!"
    d, m = divmod(voice, staff)
    L = staff * [d]
    for i in range(m):
        L[i] += 1
    return L


def dict_integration_ip(to_update, update_from):
    """Doesn't touch existing k, v in to_update,
    only integrates missing ones from update_from,
    alters to_update in-place"""
    for k, v in update_from.items():
        if isinstance(v, dict):
            dict_integration_ip(to_update.setdefault(k, {}), v)
        else:
            # If k exists do nothing!
            to_update.setdefault(k, v)


# Use this in kodou.py
def dict_integrate(to_update, update_from):
    """Same as above, without side effect"""
    to_update_cp = copy(to_update)
    for k, v in update_from.items():
        if isinstance(v, dict):
            to_update_cp[k] = dict_integrate(to_update_cp.setdefault(k, {}), v)
        else:
            if not k in to_update_cp:
                to_update_cp[k] = v
    return to_update_cp

# d1, d2 = {1:{0:1, 6:{9:{22:11, 11:22}}}, 4:{5}}, {1:{2:4, 5:6, 6: {7: 8, 9: {22: 33}}}, 3:4}
# dict_integrate(d1, d2)
# dict_integration_ip(d1, d2)

# processing metadata should happen here,
# damit auch die Sachen von interpose Wirkung haben
def _process_barline(barline):
    return ' \\bar "{}"'.format(barline)


def _process_clef(clef):
    if "+" in clef:
        clef, octave = clef.split("+")
        index = CLEFS.index(clef)
        return '\clef "{}^{}" '.format(CLEFS[index], octave)
    elif "-" in clef:
        clef, octave = clef.split("-")
        index = CLEFS.index(clef)
        return '\clef "{}_{}" '.format(CLEFS[index], octave)
    else:
        # assert that only letters are in clef
        index = CLEFS.index(clef)
        return '\clef "{}" '.format(CLEFS[index])

    
def _process_timesig(timesig):
    return "\\time {}/{} ".format(timesig[0], timesig[1])

class LilyNoteheadError(Exception):
    pass

def _process_notehead(notehead):
    if notehead.startswith("\\revert"):
        return notehead
    else:
        if notehead not in NOTEHEADS:
            raise LilyNoteheadError(f"{notehead} is not a valid notehead")
        return NOTEHEADS[notehead]
    
    
def _process_articulation(articulation):
    if isinstance(articulation, set):
        # lilypond findet es besser wenn breathe am ende kommt?
        # False < True, True geht nach hinten
        with_breathe_as_last = sorted(articulation, key=lambda i: i == "breathe")
        # rekursiv, evtl. ändern?
        return "".join([_process_articulation(a) for a in with_breathe_as_last])
    else:
        return ARTICULATIONS[articulation]

        
def _process_dynamic(dynamic):
    return "".join(['\{}'.format(d) for d in dynamic])


def _process_slur_type(slur_type):
    """slur_type is a set"""
    return "{} ".format("".join(slur_type))


def _process_slur(slur):
    """slur is a set
    an obj may have at most 2 slures of any combination"""
    S = []
    for s in slur:
        if s == "phrasing_slur_on":
            S.append("\(")
        elif s == "phrasing_slur_off":
            S.append("\)")
        elif s == "slur_on":
            S.append("(")
        else:                       # slur_off
            S.append(")")
    return "".join(S)

    
def _md_processor(md, md_val):
    """verarbeiten des metadatas"""
    if md == "float_barline":
        return _process_barline(md_val)
    elif md == "clef":
        return _process_clef(md_val)
    elif md == "timesig":
        return _process_timesig(md_val)
    elif md == "notehead":
        return _process_notehead(md_val)
    elif md == "slur_type":
        return _process_slur_type(md_val)
    elif md == "slur":
        return _process_slur(md_val)
    elif md == "int_barline":
        return _process_barline(md_val)
    elif md == "articulation":
        return _process_articulation(md_val)
    elif md == "dynamic":
        return _process_dynamic(md_val)


def _make_obj(note_obj, lily_val):
    """rhythm is a tuple: (number of notes, lilypond_value)"""
    if hasattr(note_obj, "note"):
        note = "O" + note_obj.note
    else:
        note = "Or"
    obj = note + str(lily_val)
    # now metadata
    # Keep the order of things
    # The order of const is important
    pre_tuplet_metadata = dict()
    for i, md in enumerate(PRE_TUPLET_METADATA):
        if hasattr(note_obj, md):
            pre_tuplet_metadata[i] = _md_processor(md, getattr(note_obj, md))
    post_tuplet_metadata = dict()
    for i, md in enumerate(POST_TUPLET_METADATA):
        # The note itself
        if md == "_":
            post_tuplet_metadata[i] = obj
        # Other metadata
        elif hasattr(note_obj, md):
            post_tuplet_metadata[i] = _md_processor(md, getattr(note_obj, md))
    return [pre_tuplet_metadata, post_tuplet_metadata]


def _normalize(rng):
    """set back rng btwn 0 and ..."""
    start_int = modf(rng[0])[1]
    return [x - start_int for x in rng]


# the real main function! :-)
def _process_beat(beatgroup, init_val):
    """beatgroup is a dict containing a beat,
    process one single beat on every call
    """
    first_beat = min(beatgroup)
    beat_first_item = beatgroup[first_beat]
    timesig_check = beat_first_item.timesig_check
    try:
        postponed_md_tank = beat_first_item.postponed_md_tank
    except AttributeError:
        postponed_md_tank = None
    try:
        barcheck = beat_first_item.barcheck
    except AttributeError:
        barcheck = False        
    # constrain to one beat
    beatgroup = {kv[0] % 1: kv[1] for kv in beatgroup.items()}
    # Starting output_dict with some default values:
    output_dict = {
        0: {
            "timesig_check": timesig_check,
            "val": init_val,
            "obj": _make_obj(None, init_val),
            "tuplet_start": [],
            "tuplet_end": []}
    }
    for idx, beat in enumerate(sorted(beatgroup)):
        # if not hasattr(beatgroup[beat], "remove_this"):
        output_keys = sorted(output_dict)
        supbeat = superior_x(beat, output_keys)
        dnm, supdnm = beat.denominator, supbeat.denominator
        lcm_ = lcm(dnm, supdnm)
        primes = factorize(lcm_ // supdnm)
        if primes:
            for prime in primes:
                next_beat = list(filter(lambda x: x > supbeat, output_keys + [1]))[0]
                remaining_space = next_beat - supbeat
                val = output_dict[supbeat]["val"] * nearest_binary(prime)
                r = (1, val)                
                tuplet_info = tuplet_label(Fraction(pow(prime, -1)).limit_denominator(LIMIT))
                tuplet = tuplet_info[0]
                if tuplet:
                    # If there is a tuplet update beat_division
                    beat_division = tuplet_info[1]                
                for p in range(prime):
                    x = supbeat + Fraction(p, int(prime / remaining_space)).limit_denominator(LIMIT)                    
                    obj = _make_obj(beatgroup.get(x), val)                    
                    # TUPLETS
                    if p == 0:
                        n_tuplet_ends = len(output_dict[supbeat]["tuplet_end"])
                        if tuplet:
                            tuplet_start = output_dict[supbeat]["tuplet_start"] + [tuplet]
                        else:
                            tuplet_start = output_dict[supbeat]["tuplet_start"]
                        tuplet_end = []
                    elif p == prime - 1:
                        tuplet_start = []
                        if tuplet:
                            tuplet_end = output_dict[supbeat]["tuplet_end"] + ["}"] * (n_tuplet_ends + 1)
                        else:
                            tuplet_end = n_tuplet_ends * ["}"]
                    else:
                        tuplet_start = []
                        tuplet_end = []
                    # update the output_dict
                    output_dict.update({
                        x: {
                            "timesig_check": timesig_check,
                            "val": val,
                            "obj": obj,
                            "tuplet_start": tuplet_start,
                            "tuplet_end": tuplet_end,
                            # For Fractional beats never remove the last beat
                            "remove": False
                    }})
                output_keys = sorted(output_dict.keys())
                supbeat = superior_x(beat, output_keys)
        # Still multiples, ratio is 1 (whole-beats)!
        else:
            val = output_dict[supbeat]["val"]
            obj = _make_obj(beatgroup.get(beat), val)            
            # TUPLETS
            tuplet_start = []
            tuplet_end = output_dict[supbeat]["tuplet_end"]
            # Is it the last beat calculated from durations?
            # Then it should be removed. This is set in classes._Duration.set_endpoints_ip
            try:
                remove = beatgroup[beat].remove
            except AttributeError:
                remove = False
            output_dict.update({
                beat: {
                    "timesig_check": timesig_check,
                    "val": val,
                    "obj": obj,
                    "tuplet_start": tuplet_start,
                    "tuplet_end": tuplet_end,
                    "remove": remove
                }})
    # Set beats back to original values
    output_dict = _change_keys(output_dict, lambda k: first_beat + k)
    # Add possibly barcheck key to the very last item of the output_dict 
    if barcheck:
        output_dict[max(output_dict)]["barcheck"] = barcheck
    # 
    if postponed_md_tank:
        for postponed_md in postponed_md_tank:
            # Position of the postponed_md in the beat
            if postponed_md.where == "back":
                obj_dict = output_dict[max(output_dict)]["obj"]
            else:
                pass
            # Is postponed_md a post_tuplet_metadata or a pre_tuplet_metadata?
            if postponed_md.post_tuplet:
                obj_dict[1][postponed_md.md_constant_idx] = _md_processor(postponed_md.md, postponed_md.md_val)
            else:
                obj_dict[0][postponed_md.md_constant_idx] = _md_processor(postponed_md.md, postponed_md.md_val)
    # Remove the last beat calced from durations
    for k in sorted(output_dict):
        if output_dict[k]["remove"]:
            del output_dict[k]
    return output_dict


# def endswith(string, sub_string):
#     """opposite of startswith"""
#     sub_string_len = len(sub_string)
#     return sub_string[-1::-1] == string[-1::-1][:sub_string_len]


def _change_keys(dictionary, func=lambda k: k):
    """return the dictionary with func applied to its keys"""
    dictionary_cp = copy(dictionary)
    for k, v in dictionary.items():
        del dictionary_cp[k]
        dictionary_cp[func(k)] = v
    return dictionary_cp



def _glue(final_beat_item):
    """final_beat_item is a dict or a string
    if coming from a duration processing"""
    glued = []
    prtmd, pstmd = final_beat_item["obj"]
    prtmd = [prtmd[k] for k in sorted(prtmd)]
    pstmd = [pstmd[k] for k in sorted(pstmd)]
    # pre_tuplet_metadata is not always present
    if prtmd:
        glued.append(" ".join(prtmd))
    tuplet_start = final_beat_item["tuplet_start"]
    if tuplet_start:
        for start in tuplet_start:
            glued.append(start)
    # post_tuplet_metadata contains at least note/rest
    glued.append(" ".join(pstmd))
    tuplet_end = final_beat_item["tuplet_end"]
    if tuplet_end:
        for end in tuplet_end:
            glued.append(end)
    try:
        glued.append(final_beat_item["barcheck"])
    except KeyError:
        pass
    return glued
    



# def tokenize_beat(processed_beat):
#     tokens = list()
#     # beat is closing beat of the bar?
#     output_dict, barcheck = processed_beat
#     for beat in sorted(output_dict):
#         # Either an empty str() or a tuplet of:
#         # pre and post tuplet metadata
#         obj = output_dict[beat]["obj"]
#         if obj:
#             prtm, potm = obj
        
#         # Since pre_tuplet_metadata can be empty
#         if prtm:
#             tokens.append("".join(prtm))
        
#         tuplet_start = output_dict[beat]["tuplet_start"]
#         if tuplet_start:
#             for start in tuplet_start:
#                 tokens.append(start)

#         # post_tuplet_metadata
#         # This includes the note itself
#         tokens.append("".join(potm))
        
#         tuplet_end = output_dict[beat]["tuplet_end"]
#         if tuplet_end:
#             for end in tuplet_end:
#                 tokens.append(end)
        
#     # put the barcheck
#     if barcheck:
#         tokens.append(barcheck)
        
#     return tokens


VALID_KODOURC_KEYS = (
    "ly_version", "ly_language", "pdf_viewer",
    "ly_bin", "ly_paper_size", "ly_staff_size",
    "load_ekmelily"
)

def is_valid_kodourc_key(key):
    return key.lower() in VALID_KODOURC_KEYS

def prepare_ly(ly_path, kodourc, paperpart_global_ly_commands):
    """paperpart_global_ly_commands is a list of commands different Part()s want 
    to add at the top of the ly file before writing their stave"""
    dot_kodou_commands = dict()
    with open(kodourc, "r") as f:
        for line in f.read().splitlines():
            if line and not line.startswith("#"):  # pound sign is .kodou comment
                k, v = [x.strip() for x in line.split("=")]
                if is_valid_kodourc_key(k):
                    dot_kodou_commands[k] = v
                else:
                    raise NameError(f"{k} is not a valid kodourc key")
    with open(ly_path, "w") as f:
        f.write("%%% {0} %%%\n".format(TAGLINE))
        f.write("%%% Load modules, setup & configurations %%%\n")
        paper_size = dot_kodou_commands.get("ly_paper_size", LY_DEFAULT_PAPER_SZ)
        f.write('#(set-default-paper-size "{}")\n'.format(paper_size))
        staff_size = dot_kodou_commands.get("ly_staff_size", LY_DEFAULT_STAFF_SZ)
        f.write('#(set-global-staff-size {})\n'.format(staff_size))
        version = dot_kodou_commands.get("ly_version", LY_MIN_VERSION)
        f.write('\\version "{}"\n'.format(version))
        language = dot_kodou_commands.get("ly_language", LY_DEFAULT_LANG)
        f.write('\\language "{}"\n'.format(language))
        load_ekmelily = dot_kodou_commands.get("load_ekmelily", LOAD_EKMELILY)
        if load_ekmelily == "yes":
            f.write('\\include "ekmel.ily"\n')
            # In order to choose a style, ekmelily should be loaded!
            ekmelic_style = dot_kodou_commands.get("ekmelic_style", "rhm")
            f.write('\\ekmelicStyle {}\n'.format(ekmelic_style))
        # what r these?
        f.write("\n")
        f.write(make_header(_copyright))
        f.write(UNEQUAL_LENGTH_MEASURES_POLYMETRY)
        f.write(PAPER)
        f.write("\n")
        # things parts want to add, before writing actual stave
        f.write("\n")
        for command in paperpart_global_ly_commands:
            f.write(command)
            f.write("\n")
        f.write("\n" * 4)
    viewer = dot_kodou_commands.get("pdf_viewer", "/usr/bin/zathura")
    lilypond = dot_kodou_commands.get("ly_bin", "/usr/local/bin/lilypond")
    return viewer, lilypond
