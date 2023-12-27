
from string import ascii_uppercase
from itertools import product
from copy import (copy, deepcopy)
from sys import maxsize
from numbers import Number
from fractions import Fraction
from operator import(le, lt, gt)
from math import (floor, ceil, modf)

from .pitch import midi_to_name
from .rhythm import (superior_x, disassemble_rhythm)
from .process import (dict_integration_ip, distribute_voice_staff,
                      parse_lilyvals, _glue, _process_beat)
from .const import (LIMIT, PHRASING_SLUR_TYPES, SLUR_TYPES,
                        USER_DEFINE_OPERATOR, STAFF_BINDING_TYPES, STAFF_TYPES)



class Part:
    """a Part object can be thought of as a single instrument.
    Parts can be monophon or polyphon."""
    def __init__(self, events, metadata={}):
        self.events = _Events(events)
        self.metadata = metadata
        
    # def interpose(self, fun):
    #     """grants access to every attr of a _Note obj (mt, note, beat),
    #     things here will overwrite everything else (md, note, beat)
    #     everywhere else!
    #     It is part of _Note creation before sending _Notes for final processing"""
    #     args = []
    #     if self.events.polyphon:
    #         for voice in sorted(self.events.stream):
    #             l = []
    #             for beat in sorted(self.events.stream[voice]):
    #                 l.append(self.events.stream[voice][beat])
    #             args.append(l)
    #     else:
    #         for beat in sorted(self.events.stream):
    #             args.append(self.events.stream[beat])
    #     out = fun(args)


class _Note:    
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class _Space:
    
    def __init__(self, time_points, end_point=maxsize):
        self.time_points = copy(time_points)
        self.time_points[(0, end_point)] = time_points["default"]  # time_points must have default key
        self.time_points.__delitem__("default")
        self.singles = dict(filter(lambda kv: isinstance(kv[0], Number), self.time_points.items()))
        self.intervals = list(filter(lambda k: isinstance(k, tuple) or isinstance(k, list), self.time_points))
        self.intervals = sorted(sorted(self.intervals, key=lambda x: -x[1]), key=lambda x: x[0])

    def _process_intervals(self, ):
        D = {}
        for i, interval in enumerate(self.intervals, 1):
            interval_start, interval_end = interval
            D[interval_start] = self.time_points[interval]
            covered = False
            for next_interval in self.intervals[i:]:
                next_interval_start, next_interval_end = next_interval
                if next_interval_start <= interval_end <= next_interval_end:
                    covered = True
                    break           # dont continue, interval_end is covered
            if not covered:
                for last_interval in self.intervals[i - 1::-1]:
                    _, last_interval_end = last_interval
                    # auf was wird zurückgesetzt?
                    if interval_end < last_interval_end:
                        D[interval_end] = self.time_points[last_interval]
                        break   # gefunden
        return D
    
    def arrange(self, ):
        singles = self.singles
        if singles:
            spaces = dict(filter(lambda kv: kv[0] < min(singles), self._process_intervals().items()))
            spaces.update(singles)
        else:
            spaces = self._process_intervals()
        return spaces


class _Events:
    """dict with keys: beats, pchs, opt:durations"""
    def __init__(self, events):
        beats = events["onsets"]
        notes = events["pchs"]
        # create the stream
        self.stream = dict()
        # notes have been specified at creation time
        if notes:
            if hasattr(beats[0], "__iter__"):
                assert all(
                    [isinstance(B, list) or \
                     isinstance(B, tuple) or \
                     isinstance(B, range) for B in beats]
                ), "Event's beat streams should be of type list, tuple or range!"
                assert all(
                    [isinstance(N, list) or \
                     isinstance(N, tuple) or \
                     isinstance(N, range) for N in notes]
                ), "Event's note streams should be of type list, tuple or range!"
                self.polyphon = True
                for voice in range(len(beats[:len(notes)])):
                    D = {}
                    for i, beat in enumerate(beats[voice][:len(notes[voice])]):
                        # if note a []/() its a chord
                        note = notes[voice][i]
                        D[beat] = _Note(beat=beat, note=note)
                    self.stream[voice] = D
            else:
                assert all([isinstance(B, float) or isinstance(B, int) for B in beats]), \
                "Beats should be of type int or float!"
                self.polyphon = False
                for i, beat in enumerate(beats[:len(notes)]):
                    note = notes[i]
                    # if note a []/() its a chord
                    self.stream[beat] = _Note(beat=beat, note=note)
        # no notes specified at creation time
        else:
            if hasattr(beats[0], "__iter__"):
                assert all([isinstance(B, list) or \
                            isinstance(B, tuple) or \
                            isinstance(B, range) for B in beats]
                ), "Event's beat streams should be of type list, tuple or range!"
                self.polyphon = True
                for voice in range(len(beats)):
                    D = {}
                    for beat in beats[voice]:
                        D[beat] = _Note(beat=beat)
                    self.stream[voice] = D
            else:
                assert all([isinstance(beat, float) or isinstance(beat, int) for beat in beats]), \
                "Beats should be of type int or float!"
                self.polyphon = False
                for beat in beats:
                    self.stream[beat] = _Note(beat=beat)                    
        # convert the stream
        self.stream = self.convert(self.stream)        
        # durations is an optional parameter: a dict {beat: duration}
        # this only runs the assertions and does nothing more.
        # If events.get("durations") is None, fractionized is an
        # empty dict and assertions iterats over an empty dict.
        durations = events.get("durations")
        if durations:
            self.with_duration = True
            self.duration_obj = _Duration(durations, self.stream)
        else:
            self.with_duration = False

            
    def _find_step(self, note, prev_note):
        """will be called only if """
        if prev_note:
            try:
                base = note[0]  # note is a chord
                try:
                    prev_base = prev_note[0]  # last note was also a chord
                except TypeError:  # last note was a single note
                    prev_base = prev_note
            except TypeError:
                base = note  # note is a single note
                try:
                    prev_base = prev_note[0]  # last note was a chord
                except TypeError:  # last note was also a single note
                    prev_base = prev_note
            step = base - prev_base
        else:
            step = 0
        return step

    
    def _note_to_name(self, note, prev_note):
            if isinstance(note, list) or isinstance(note, tuple):
                name = ["<", ">"]
                for i, n in enumerate(note, 1):
                    if isinstance(n, str):
                        name.insert(i, n)
                    else:
                        if isinstance(prev_note, Number):
                            step = self._find_step(note, prev_note)
                        else:
                            step = 0
                        name.insert(i, midi_to_name(n, step))
                name = " ".join(name)
            else:
                if isinstance(note, str):
                    name = note
                else:
                    if isinstance(prev_note, Number):
                        step = self._find_step(note, prev_note)
                    else:
                        step = 0
                    name = midi_to_name(note, step)
            return name

        
    def convert(self, stream):
        """beat => Fraction, note => ly_name"""
        D = dict()
        if self.polyphon:
            sorted_stream = sorted(stream)
            for voice in sorted_stream:
                sorted_voice = sorted(stream[voice])
                d = dict()
                for i, beat in enumerate(sorted_voice):
                    fract_beat = Fraction(beat).limit_denominator(LIMIT)
                    obj = copy(stream[voice][beat])
                    note = obj.note
                    if i > 0:
                        prev_note = stream[voice][sorted_voice[i - 1]].note
                    else:
                        prev_note = None
                    obj.note = self._note_to_name(note, prev_note)
                    d[fract_beat] = obj
                D[voice] = d
        else:
            sorted_stream = sorted(stream)
            for i, beat in enumerate(sorted_stream):
                fract_beat = Fraction(beat).limit_denominator(LIMIT)
                obj = copy(stream[beat])  # don't touch the stream itself! :-(
                note = obj.note
                if i > 0:
                    prev_note = stream[sorted_stream[i - 1]].note
                else:
                    prev_note = None
                obj.note = self._note_to_name(note, prev_note)
                D[fract_beat] = obj
        return D

    
    
class _Duration:
    
    """instances add beats to events.stream if necessary"""
    
    def __init__(self, durations, stream):
        # Convert to Fractions
        self.fractionized_durations = self.fractionize(durations)
        
        # only assertions will be called by the Part instance
        # to ensure early recognition of non existing beats
        self.assertions(self.fractionized_durations, stream)

        
    def with_duration_endpoints_ip(self, durations, stream):
        if self.polyphon:
            for voice in sorted(durations):
                self.set_endpoints_ip(durations[voice], stream[voice])
        else:
            self.set_endpoints_ip(durations, stream)

            
    def set_endpoints_ip(self, durations, stream):
        """Find the endpoints of each duration and set it in the stream
        if stream doesn't have such a beat already."""
        sorted_durations = sorted(durations)
        sorted_stream = sorted(stream)
        for dur_beat in sorted_durations:
            # 1. where is dur_beat in the stream
            dur_beat_idx = sorted_stream.index(dur_beat)
            # 2. Is there another beat with note attr in the stream after this?
            next_possible_note_beats = filter(lambda bt: hasattr(stream[bt], "note"), sorted_stream[dur_beat_idx + 1:])
            try:
                dur_from_durations, dur_from_stream = dur_beat + durations[dur_beat], next(next_possible_note_beats)
                end_point = min(dur_from_durations, dur_from_stream)
                if end_point != dur_from_durations:
                    # Also overwrite this duration in durations.
                    durations[dur_beat] = end_point - dur_beat
                if end_point not in stream:
                    stream[end_point] = _Note(beat=end_point)
            # If there isn't any beat in the stream after it,
            # it is free to have any durations
            except StopIteration:
                end_point = dur_beat + durations[dur_beat]
                # Add the end_point to the stream if not existing.
                # This will be removed after beeing processed.
                if end_point not in stream:
                    stream[end_point] = _Note(beat=end_point, remove=True)

            
    # Also fractionize duration values for arithmetic with stream beats
    def fractionize(self, durations):
        """in order for duration beats to be comparable
        with stream beats, they should be also Fractions"""
        fractionized = dict()
        if any([isinstance(v, dict) for v in durations.values()]):
            self.polyphon = True
            for voice in sorted(durations):
                fractionized[voice] = dict()
                for beat in sorted(durations[voice]):
                    F_beat = Fraction(beat).limit_denominator()
                    F_duration = Fraction(durations[voice][beat]).limit_denominator()
                    fractionized[voice][F_beat] = F_duration
        else:
            self.polyphon = False
            for beat in sorted(durations):
                F_beat = Fraction(beat).limit_denominator()
                F_duration = Fraction(durations[beat]).limit_denominator()
                fractionized[F_beat] = F_duration
        return fractionized

    
    def assertions(self, durations, stream):
        """Check that stream is also polyphon."""
        if self.polyphon:
            # voices which want durations exist in stream
            for voice in durations.keys():
                if voice not in stream.keys():
                    raise KeyError("Duration voice {} not found!".format(voice))
                else:
                    # check if all beats are present
                    for beat in sorted(durations[voice]):
                        if beat not in stream[voice].keys():
                            raise KeyError("Duration beat {} of duration voice {} not found!".format(beat, voice))
        else:
            # check if all beats are present
            for beat in sorted(durations):
                if beat not in stream.keys():
                    raise KeyError("Duration beat {} not found!".format(beat))

                
    def _durations(self, durations, stream):
        """returns final ready-to-use durations!"""
        D = dict()
        if self.polyphon:
            assert all([isinstance(v, dict) for v in durations.values()])
            for voice in sorted(durations):
                stream = stream[voice]
                D[voice] = self.final_durations(durations[voice], stream)
        else:
            D = self.final_durations(durations, stream)
        return D

    
    def find_dur(self, beat, stream, durations, plus=1):
        """if a beat in stream hasattr _metadata_artefact:
        it has been created by a metadata, so that beat is considered as free"""
        idx = sorted(stream).index(beat)
        try:
            nxt_note_idx = sorted(stream)[idx + plus]
            # check wether this object is only a rest created by a metadata
            # if so it will be not taken into account,
            # or is only a rest object added by add_missing_integer_beats_ip for example
            if hasattr(stream[nxt_note_idx], "_metadata_artefact") or \
               not hasattr(stream[nxt_note_idx], "note"):
               # don't care, keep searching 
               plus += 1
               return self.find_dur(beat, stream, durations, plus)
            else:
                max_possible_dur = nxt_note_idx - beat
                duration = min(durations[beat], max_possible_dur)
        # if no next note exists accepts the specified duration
        except IndexError:
            duration = durations[beat]
        return duration

    
    def final_durations(self, durations, stream):
        D = dict()
        for beat in sorted(durations):
            D[beat] = self.find_dur(beat, stream, durations)
        return D





class _Metadata:

    def __init__(self, md_dict, x_part, md_name, md_space_types, md_types):
        self.md_dict = md_dict
        self.x_part = x_part      # x_part is the paper_part / Midi Part object
        self.md_name = md_name
        self.md_space_types = md_space_types
        self.md_types = md_types




class _UnstickyMetadata(_Metadata):
    """in lilypond terms is applied only to its own object,
    doesn't affect remaining objects"""
    def __init__(self, *args):
        super().__init__(*args)
        self.assertions()
        
    def assertions(self, ):
        if any([isinstance(k, dict) for k in self.md_dict.values()]):  # {voice: {(x, y): "staccato"}}
            assert self.x_part.polyphon, "Can't set polyphon {} for a monophon Part!".format(self.md_name)
            assert all([isinstance(k, int) for k in self.md_dict.keys()]), "Voice should be of type int!"
            for voice in self.md_dict.keys():
                assert isinstance(self.md_dict[voice], dict), "Metadata should be of type dict, not {}!".format(type(self.md_dict[voice]))
                assert all(
                    [any([isinstance(k, t) for t in self.md_space_types]) for k in self.md_dict[voice].keys()]
                ), "{} space should be one of types: {}!".format(self.md_name, self.md_space_types)
                assert all(
                    [any([isinstance(k, t) for t in self.md_types]) for k in self.md_dict[voice].values()]
                ), "{} should be one of types: {}!".format(self.md_name, self.md_types)
            self.voice_dependent_metadata = True
        else:
            assert all(
                [any([isinstance(k, t) for t in self.md_space_types]) for k in self.md_dict.keys()]
            ), "{} space should be one of types: {}!".format(self.md_name, self.md_space_types)
            assert all(
                [any([isinstance(k, t) for t in self.md_types]) for k in self.md_dict.values()]
            ), "{} should be one of types: {}!".format(self.md_name, self.md_types)
            self.voice_dependent_metadata = False
    

class _StickyMetadata(_Metadata):
    """in lilypond terms applies to the remaining stream untill 
    explicitly canceled out"""
    def __init__(self, *args):
        super().__init__(*args)

    def assertions(self, ):
        if any([isinstance(v, dict) for v in self.md_dict.values()]):  # {voice: {(x, y): "staccato"}}
            for voice in set(self.md_dict.keys()).difference(("default",)):
                self.md_dict[voice]["default"] = self.md_dict["default"]  # all notehead_dicts need default
            self.md_dict_cp = copy(self.md_dict)
            self.md_dict_cp.__delitem__("default")
            assert self.x_part.polyphon, "Can't set polyphon {} for a monophon Part!".format(self.md_name)
            assert all([isinstance(k, int) for k in self.md_dict_cp.keys()]), "Voice should be of type int!"
            for voice in self.md_dict_cp.keys():
                assert isinstance(self.md_dict_cp[voice], dict), "Metadata should be of type dict, not {}!".format(type(self.md_dict[voice]))
                assert all(
                    [any(
                        [isinstance(k, t) for t in self.md_space_types]
                    ) for k in set(self.md_dict_cp[voice].keys()).difference(("default",))]
                ), "{} space should be one of types: {}!".format(self.md_name, self.md_space_types)
                assert all(
                    [any(
                        [isinstance(v, t) for t in self.md_types]
                    ) for v in self.md_dict_cp[voice].values()]
                ), "{} should be one of types: {}!".format(self.md_name, self.md_types)
            self.voice_dependent_metadata = True
        else:
            assert all(
                [any(
                    [isinstance(k, t) for t in self.md_space_types]
                ) for k in set(self.md_dict.keys()).difference(("default",))]
            ), "{} space should be one of types: {}!".format(self.md_name, self.md_space_types)
            assert all(
                [any(
                    [isinstance(k, t) for t in self.md_types]
                ) for k in self.md_dict.values()]
            ), "{} should be one of types: {}!".format(self.md_name, self.md_types)
            self.voice_dependent_metadata = False


class PostponedMD():
    """A class for metadata which should come on impossible beats!
    i.e.: a barline at the end of an integral beat: this can not be done
    at Barline creation time (what if i have smaller subbeats to come after
    the integer beat? Integer barline should come at the end of the beat, not
    at the end of some objects!) and can not be done during the processing of the beat,
    since by then i still cant know where the beat processing finds its end!
    So the integer barline should be appended after all these steps (at the end of
    processing the beat)"""
    # Put all postponed_md in this tank,
    # loop over it at the end of porcessing a beat
    def __init__(self, md, md_val, md_constant_idx, post_tuplet, where="back"):
        self.md = md
        self.md_val = md_val
        self.md_constant_idx = md_constant_idx
        self.post_tuplet = post_tuplet
        self.pre_tuplet = not(post_tuplet)
        self.where = where


# unsticky metadata
class _Legato(_UnstickyMetadata):
    """Simultaneous or overlapping slurs are not permitted, 
    but a phrasing slur can overlap a slur.
    Slurs can be solid, dotted, or dashed, half-dashed, half-solid
    Solid is the default slur style"""    
    def __init__(self, md_dict, x_part):
        super().__init__(md_dict, x_part, "Legato", (str,), (tuple, list, set))
        self.assertions()

    def _space_legatotype(self, md_dict):
        D = {}
        for legatotype in md_dict.keys():
            for space in md_dict[legatotype]:
                D.update({space : legatotype})
        return D
    
    def _arrange_spaces(self, md_dict):
        D = {}
        space_legatotype = self._space_legatotype(md_dict)
        sorted_space_legatotype = sorted(space_legatotype)
        while sorted_space_legatotype:
            phrasing_slur = max(sorted_space_legatotype,
                                key=lambda tpl: tpl[1] - tpl[0])  # biggest interval
            # remove phrasing_slur and possible duplicates
            for space in list(filter(lambda space: space == phrasing_slur,
                                     sorted_space_legatotype)):
                sorted_space_legatotype.remove(space)
            # gather all included spaces
            L = list(
                filter(
                    lambda space:
                    phrasing_slur[0] < space[0] < phrasing_slur[1] or \
                    phrasing_slur[0] < space[1] < phrasing_slur[1],
                    sorted_space_legatotype
                )
            )
            if L:
                for space in L:
                    sorted_space_legatotype.remove(space)
                R = [L[0]]
                i = 0
                for space in L[1:]:
                    prev_space = L[i]
                    if not space[0] < prev_space[1]:
                        R.append(space)
                        i += 1
            else:
                R = ()
            D[(phrasing_slur, space_legatotype[phrasing_slur])] = [(r, space_legatotype[r]) for r in R]
        return D

    def _end_point(self, beat, stream):
        """i want end_point of a legato to be the note before the beat"""
        smaller_beats = filter(lambda x: x < beat, stream)
        return list(smaller_beats)[-1]
    
    def _attach_legatos(self, stream, space_legato, type_):
        """types=phrasing, normal"""
        space, legato = space_legato
        if type_ == "phrasing":
            slur_dict = PHRASING_SLUR_TYPES
            on, off = "phrasing_slur_on", "phrasing_slur_off"
        else:                   # normal slur
            slur_dict = SLUR_TYPES
            on, off = "slur_on", "slur_off"
        fract_beats = [Fraction(bt).limit_denominator() for bt in space]
        obj_on = stream.setdefault(fract_beats[0], _Note(beat=fract_beats[0], _metadata_artefact=True))
        # legato exclusive fract_beats[1]
        end_point = self._end_point(fract_beats[1], sorted(stream))
        obj_off = stream[end_point]
        # obj_off = stream.setdefault(fract_beats[1], _Note(beat=fract_beats[1], _metadata_artefact=True))
        # on
        if hasattr(obj_on, "slur_type"):
            obj_on.slur_type.add(slur_dict[legato])
        else:
            setattr(obj_on, "slur_type", {slur_dict[legato]})
        if hasattr(obj_on, "slur"):
            obj_on.slur.add(on)
        else:
            setattr(obj_on, "slur", {on})
        # off doesn't get any slur_type!
        if hasattr(obj_off, "slur"):
            obj_off.slur.add(off)
        else:
            setattr(obj_off, "slur", {off})
    
    def apply_(self, ):
        if self.voice_dependent_metadata:
            for voice in self.md_dict.keys():
                stream = self.x_part.events.stream[voice]
                legatos = self._arrange_spaces(self.md_dict[voice])
                for phrasing_slur in legatos.keys():
                    self._attach_legatos(stream, phrasing_slur, "phrasing")
                    for space_legato in legatos[phrasing_slur]:
                        self._attach_legatos(stream, space_legato, "normal")
        else:
            legatos = self._arrange_spaces(self.md_dict)
            if self.x_part.polyphon:
                for voice in self.x_part.events.stream.keys():
                    stream = self.x_part.events.stream[voice]
                    for phrasing_slur in legatos.keys():
                        self._attach_legatos(stream, phrasing_slur, "phrasing")
                        for space_legato in legatos[phrasing_slur]:
                            self._attach_legatos(stream, space_legato, "normal")
            else:
                stream = self.x_part.events.stream
                for phrasing_slur in legatos.keys():
                    self._attach_legatos(stream, phrasing_slur, "phrasing")
                    for space_legato in legatos[phrasing_slur]:
                        self._attach_legatos(stream, space_legato, "normal")
                

class _Articulation(_UnstickyMetadata):
    
    def __init__(self, md_dict, x_part):
        super().__init__(md_dict, x_part, "Articulation", (int, float, tuple), (str, tuple, list, set))
        self.assertions()

    def _obj_with_articulation(self, obj_articulation, articulation):
        if isinstance(articulation, (list, tuple, set)):
            obj_articulation.update(articulation)  # md_dict_cp[beat] is iterable
        else:                                      # its str
            obj_articulation.add(articulation)

    def _obj_without_articulation(self, obj, articulation):
        if isinstance(articulation, (list, tuple, set)):
            setattr(obj, "articulation", set(articulation))
        else:                                                # its str
            setattr(obj, "articulation", set([articulation]))
            
    def apply_(self, ):
        if self.voice_dependent_metadata:  # made by _Metadata.assertions()
            for voice in sorted(self.md_dict):
                stream = self.x_part.events.stream[voice]
                for beat in self.md_dict[voice].keys():
                    articulation = self.md_dict[voice][beat]
                    try:        # beat is a tuple
                        beat_s = list(filter(lambda x: beat[0] <= x < beat[1], stream))
                        self.process_articulations(beat_s, stream, articulation, False)
                    except TypeError:  # beat is a Number
                        fract_beat = Fraction(beat).limit_denominator()
                        self.process_articulations(fract_beat, stream, articulation)
        # unified articulations for all voice/s
        else:                   # {beat: articulation / space: articulation(articulations)}
            if self.x_part.polyphon:
                for voice in sorted(self.x_part.events.stream):
                    stream = self.x_part.events.stream[voice]
                    for beat in self.md_dict.keys():  # muss nicht sortiert sein
                        articulation = self.md_dict[beat]
                        try:        # beat is a tuple
                            beat_s = list(filter(lambda x: beat[0] <= x < beat[1], stream))
                            self.process_articulations(beat_s, stream, articulation, False)
                        except TypeError:  # beat is a Number
                            fract_beat = Fraction(beat).limit_denominator()
                            self.process_articulations(fract_beat, stream, articulation)
            else:
                for beat in self.md_dict.keys():  # muss nicht sortiert sein
                    articulation = self.md_dict[beat]
                    try:        # beat is an iterable
                        beat_s = list(filter(lambda x: beat[0] <= x < beat[1], self.x_part.events.stream))
                        self.process_articulations(beat_s, self.x_part.events.stream, articulation, False)
                    except TypeError:  # beat is a Number
                        fract_beat = Fraction(beat).limit_denominator()
                        self.process_articulations(fract_beat, self.x_part.events.stream, articulation)

    def process_articulations(self, beat_s, stream, articulation, rest_compatible=True):
        """rest_compatible sind diejenigen die auch auf Pausen kommen können
        ,allerdings nur als Number"""
        if rest_compatible:
            if set(("shortfermata", "fermata",
                    "longfermata", "verylongfermata",
                    "segno", "coda", "varcoda")).intersection(
                        [articulation] if isinstance(articulation, str) else articulation
                    ):
                obj = stream.setdefault(beat_s, _Note(beat=beat_s))
                if hasattr(obj, "articulation"):
                    self._obj_with_articulation(obj.articulation, articulation)
                else:
                    self._obj_without_articulation(obj, articulation)
            elif beat_s in stream:
                obj = stream[beat_s]
                if hasattr(obj, "articulation"):
                    self._obj_with_articulation(obj.articulation, articulation)
                else:
                    self._obj_without_articulation(obj, articulation)
        else:            
            for beat in beat_s:
                obj = stream[beat]
                if hasattr(obj, "articulation"):
                    self._obj_with_articulation(obj.articulation, articulation)
                else:
                    self._obj_without_articulation(obj, articulation)


class _BarLine(_UnstickyMetadata):
    """In scores with many staves, a \bar command in one staff 
    is automatically applied to all staves"""
    def __init__(self, md_dict, x_part):
        super().__init__(md_dict, x_part, "Barline", (int, float), (str,))
        self.assertions()
        self.user_definitions = set()

    def _parse_barline_definition(self, barline_str, placeholder="_"):
        """barline_str is a barline definition"""
        barline_str, args = barline_str.split(USER_DEFINE_OPERATOR)
        barline_str = barline_str.rstrip()  # remove trailing whitespace
        args = args.lstrip().split(" ")
        define = ["""\defineBarLine "{}" #'(""".format(barline_str), ")"]
        for i, arg in enumerate(args, 1):
            if arg == placeholder:
                define.insert(i, '""')
            else:
                define.insert(i, '"{}"'.format(arg))
        return barline_str, " ".join(define)
         
    def _attach_barlines(self, barlines, stream):
        for beat in barlines.keys():
            barline_str = barlines[beat]
            # check for define
            if USER_DEFINE_OPERATOR in barline_str:
                barline_str, definition = self._parse_barline_definition(barline_str)
                # This definition will be written at top of the ly file.
                self.user_definitions.add(definition)
            # Should barline come at the end of a beat? (beat is integer)
            if not modf(beat)[0]:
                # Since its an integer no need for conversion to Fraction
                obj = stream.setdefault(beat, _Note(beat=beat))
                postponed_md = PostponedMD(md="int_barline",
                                           md_val=barline_str,
                                           # The idx of int_barline in cnst.POST_TUPLET_METADATA
                                           md_constant_idx=7,
                                           post_tuplet=True)
                if hasattr(obj, "postponed_md_tank"):
                    obj.postponed_md_tank.append(postponed_md)
                else:
                    setattr(obj, "postponed_md_tank", [postponed_md])
                
                # # find all note objects btwn. beat and beat+1
                # # barline comes after the last one of them                
                # F = filter(lambda bt: beat <= bt < beat + 1, sorted(stream))
                # LF = list(F)
                # if LF:           # there are some notes
                #     fract_beat = LF[-1]
                # else:           # put the barline on beat itself
                #     fract_beat = Fraction(beat).limit_denominator()
                #     # x = beat
                # obj = stream.setdefault(fract_beat, _Note(beat=fract_beat))
                
                # integer barline comes after the note object
                # if not hasattr(obj, "int_barline"): # perhaps interpose has already setattr?
                #     setattr(obj, "int_barline", barline_str)
            else:
                fract_beat = Fraction(beat).limit_denominator()
                obj = stream.setdefault(fract_beat, _Note(beat=fract_beat))
                # float barline comes before the note object
                if not hasattr(obj, "float_barline"): # perhaps interpose has already setattr?
                    setattr(obj, "float_barline", barline_str)
    
    def apply_(self):
        if self.voice_dependent_metadata:
            for voice in self.md_dict.keys():
                barlines = self.md_dict[voice]
                stream = self.x_part.events.stream[voice]
                self._attach_barlines(barlines, stream)
        else:
            if self.x_part.polyphon:
                for voice in self.x_part.events.stream.keys():
                    stream = self.x_part.events.stream[voice]
                    self._attach_barlines(self.md_dict, stream)
            else:
                self._attach_barlines(self.md_dict, self.x_part.events.stream)


# sticky metadata
class _Clef(_StickyMetadata):

    def __init__(self, md_dict, x_part):
        super().__init__(md_dict, x_part, "Clef", (int, float, tuple), (str,))
        self.assertions()

    def attach_clefs(self, clefs, stream):
        x, y = min(stream), max(stream)
        usable_clefs_beats = list(filter(lambda bt: x <= bt <= y, clefs))
        for beat in usable_clefs_beats:
            fract_beat = Fraction(beat).limit_denominator()
            obj = stream.setdefault(fract_beat, _Note(beat=fract_beat))
            if not hasattr(obj, "clef"): # perhaps interpose has already setattr?
                setattr(obj, "clef", clefs[beat])
    
    def apply_(self, ):
        if self.voice_dependent_metadata:
            for voice in sorted(self.md_dict_cp):
                clefs = _Space(self.md_dict_cp[voice], max(self.x_part.longest_stream())).arrange()
                stream = self.x_part.events.stream[voice]
                self.attach_clefs(clefs, stream)
        else:                   # gibt es auch kein md_dict_cp
            clefs = _Space(self.md_dict, max(self.x_part.longest_stream())).arrange()
            if self.x_part.polyphon:
                for voice in sorted(self.x_part.events.stream):
                    stream = self.x_part.events.stream[voice]
                    self.attach_clefs(clefs, stream)
            else:
                stream = self.x_part.events.stream
                self.attach_clefs(clefs, stream)



class _Dynamic(_StickyMetadata):
    
    """Dynamic can also happen over rests, 
    so don't try to put them only on existing note objects!
    create rests if needed"""
    
    def __init__(self, md_dict, x_part):
        super().__init__(md_dict, x_part, "Dynamic", (int, float, tuple), (str,))
        self.assertions()
        self.user_definitions = set()

    def _parse_dynamic_definition(self, md_string, dyn_identifier="D"):
        """md_string is a dynamic definition"""
        dyn_type, args = md_string.split(USER_DEFINE_OPERATOR)
        dyn_type = dyn_type.rstrip()  # remove trailing whitespace
        args = args.lstrip().split(" ")
        try:
            dyn_token = next(filter(lambda tkn: tkn.startswith(dyn_identifier), args))
        except StopIteration:
            raise SyntaxError("Dynamic definition should contain dynamic characters!")
        # assert all letters are dynamic fonts
        for letter in dyn_token.strip(dyn_identifier):
            if letter not in "fmprsz":
                raise SyntaxError("Invalid dynamic character {} found in dynamic!".format(letter))
        # define
        definition = ["{} = #(make-dynamic-script (markup\n".format(dyn_type)]
        for token in args:
            if token == dyn_token:
                definition.append('\t#:dynamic "{}"\n'.format(dyn_token.strip(dyn_identifier)))
            else:
                definition.append('\t#:normal-text "{}"\n'.format(token))
        definition.append("))")
        return dyn_type, " ".join(definition)
    
    def _attach_dynamics(self, dynamics, stream):
        x, y = min(stream), max(stream)
        # last relative dynamic
        try:
            max_dynamic_beat = max(dynamics)
            if dynamics[max_dynamic_beat] in ("<", "cresc", "cr",
                                              ">", "dim", "decresc"):
                dynamics.update({y: "!"})
        except ValueError:      # dynamics is empty
            pass
        finally:
            # usable_dynamics_beats = list(filter(lambda bt: x <= bt <= y, dynamics))
            for beat in dynamics.keys():
                fract_beat = Fraction(beat).limit_denominator()
                obj = stream.setdefault(fract_beat, _Note(beat=fract_beat, _metadata_artefact=True))
                if not hasattr(obj, "dynamic"): # perhaps interpose has already setattr?
                    setattr(obj, "dynamic", dynamics[beat].split("+"))

    def _process_dynamics(self, md_dict):
        """an absolute and a relative dynamics can appear on the same beat"""
        # , max(self.x_part.longest_stream()) + 1
        dynamics_space = _Space(md_dict)
        processed_dynamics_intervals = dynamics_space._process_intervals()
        # remove the first automatic !
        # it was only useful for organizing spaces
        # 0 could have been overwritten by user, so check things
        if 0 in processed_dynamics_intervals and processed_dynamics_intervals[0] == "!":
           processed_dynamics_intervals.__delitem__(0)
        dynamics_singles = dynamics_space.singles        
        # check if an absolute dynamic comes inbetween a relative dynamic.
        # Work with a copy of processed_dynamics_intervals to not change by iterating over it
        D = copy(processed_dynamics_intervals)
        for single in sorted(dynamics_singles):
            absolute_dyn = dynamics_singles[single]
            # check for definitions (can define only absolute)
            if USER_DEFINE_OPERATOR in absolute_dyn:
                dyn_type, definition = self._parse_dynamic_definition(absolute_dyn)
                self.user_definitions.add(definition)
                absolute_dyn = dyn_type
            superior_beat = superior_x(single, sorted(processed_dynamics_intervals))
            if isinstance(superior_beat, Number): # superior_beat can be None, also 0 = Number!
                relative_dyn = processed_dynamics_intervals[superior_beat]
                # if they come on the same beat:
                # first write the relative part, then the absolute part: \<\p
                if single == superior_beat:
                    D.update({superior_beat: "+".join([relative_dyn, absolute_dyn])})
                # if relative beat is before absolute beat:
                # means absolute part interrupt relative part
                # change the absolute part to: absolute part + continuation of relative part
                # then add the new absolute part to the output dict
                else:
                    D.update({single: "+".join([absolute_dyn, relative_dyn])})
            else:    # just add the single to the output dict
                D.update({single: absolute_dyn})
        return D
                
    def apply_(self, ):
        if self.voice_dependent_metadata:
            for voice in self.md_dict_cp.keys():
                dynamics = self._process_dynamics(self.md_dict_cp[voice])
                stream = self.x_part.events.stream[voice]
                self._attach_dynamics(dynamics, stream)
        else:                   # there is no md_dict_cp
            dynamics = self._process_dynamics(self.md_dict)
            if self.x_part.polyphon:
                for voice in sorted(self.x_part.events.stream):
                    stream = self.x_part.events.stream[voice]
                    self._attach_dynamics(dynamics, stream)
            else:
                stream = self.x_part.events.stream
                self._attach_dynamics(dynamics, stream)
        
                
class _TimeSignature(_StickyMetadata):

    def __init__(self, md_dict, x_part):
        super().__init__(md_dict, x_part, "Time signature", (int, tuple), (list, tuple))
        self.assertions()

    def _positions(self, D):
        positions = _Space(D, max(self.x_part.longest_stream())).arrange()
        sorted_positions = sorted(positions)
        for i, beat in enumerate(sorted_positions[1:]):
            prev_beat = sorted_positions[i]
            prev_timesig_num, prev_timesig_den = positions[prev_beat]
            diff = beat - prev_beat
            full_bars, single_bars = divmod(diff, prev_timesig_num)
            if single_bars:
                single_bar_beat = prev_beat + full_bars * prev_timesig_num
                positions[single_bar_beat] = (single_bars, prev_timesig_den)
        return positions

    def apply_(self, ):
        if self.voice_dependent_metadata:
            # since its polyphon, set for each voice a distinct timesig_dict
            # in order to make polymetric possible
            for voice in self.x_part.events.stream:  # voice are voice numbers
                dict_integration_ip(
                    self.md_dict_cp.setdefault(voice, {}),
                    {"default": self.md_dict["default"]})
            for voice in sorted(self.md_dict_cp):
                timesig_pos = self._positions(self.md_dict_cp[voice])
                for beat in timesig_pos.keys():
                    fract_beat = Fraction(beat).limit_denominator()
                    obj = self.x_part.events.stream[voice].setdefault(fract_beat, _Note(beat=fract_beat))
                    if not hasattr(obj, "timesig"): # perhaps interpose has already set something?
                        setattr(obj, "timesig", timesig_pos[beat])
        # unified timesig for all voice/s
        else:                   # {beat: timesig, space: timesig}
            timesig_pos = self._positions(self.md_dict)
            if self.x_part.polyphon:
                for voice in sorted(self.x_part.events.stream):
                    usable_timesig_beats = list(
                        filter(lambda bt: bt < max(self.x_part.events.stream[voice]),
                               timesig_pos)
                    )
                    for beat in usable_timesig_beats:
                        fract_beat = Fraction(beat).limit_denominator()
                        obj = self.x_part.events.stream[voice].setdefault(fract_beat, _Note(beat=fract_beat))
                        if not hasattr(obj, "timesig"): # perhaps interpose has already set something?
                            setattr(obj, "timesig", timesig_pos[beat])
            else:
                for beat in timesig_pos.keys():
                    fract_beat = Fraction(beat).limit_denominator()
                    obj = self.x_part.events.stream.setdefault(fract_beat, _Note(beat=fract_beat))
                    if not hasattr(obj, "timesig"): # perhaps interpose has already set something?
                        setattr(obj, "timesig", timesig_pos[beat])

class _Staff:
    """{, "type": "drum"} #"n": 1, "bind":basic
    {"type":{0:"drum",1:"basic",...}}"""
    def __init__(self, md_dict, x_part):
        self.n = md_dict.get("n", 1)
        self.bind = STAFF_BINDING_TYPES[md_dict.get("bind", "basic")]
        self.types = md_dict["types"]  # str or dict
        if isinstance(self.types, dict):
            assert all([isinstance(k, int) for k in self.types.keys()]), "Staff voice should be of type int!"
            assert self.n >= (len(self.types)), "Can't fit {} staff types into {} systems!".format(len(self.types), self.n)
            # set a default staff for missing voices
            if len(self.types) < self.n:
                s = set(range(self.n))
                for missing_voice in s.difference(self.types.keys()):
                    self.types[missing_voice] = "basic"
        self.x_part = x_part
    
    def _make_polyphon_staff(self, ):
        # processed_part = self.x_part.process()
        processed_part = self.x_part.render()
        if self.bind:           # could be "": None
            staff = ['\n{} = \\new {} \with {{instrumentName = #"{}" shortInstrumentName = #"{}"}}'.format(
                self.x_part.who,
                self.bind,
                self.x_part.name,
                self.x_part.abbr)]
        else:
            staff = ["{} = ".format(self.x_part.who)]
        staff.append("\n<<")
        start = end = 0
        if isinstance(self.types, dict):
            for idx, i in enumerate(distribute_voice_staff(len(processed_part), self.n)):  # self.n is number of stave
                # if i:               # i can be 0
                end += i
                if i > 1:
                    staff.append("\n\\new {}".format(STAFF_TYPES[self.types[idx]]))
                    staff.append("\n <<")
                    L = []
                    for p in processed_part[start : end]:
                        L.append("\n {{ {} }}\n".format(" ".join(p)))
                    staff.append(" \\\\".join(L))
                    staff.append(" >>\n")
                else:           # i == 1
                    staff.append("\n\\new {}\n".format(STAFF_TYPES[self.types[idx]]))
                    staff.append(" {{ {} }}\n".format(" ".join(processed_part[start])))
                start = end
            staff.append(">>\n\n")
        else:                   # self.types is str
            for i in distribute_voice_staff(len(processed_part), self.n):  # self.n is number of stave
                end += i
                if i > 1:
                    staff.append("\n\\new {}".format(STAFF_TYPES[self.types]))
                    staff.append("\n <<")
                    L = []
                    for p in processed_part[start : end]:
                        L.append("\n {{ {} }}\n".format(" ".join(p)))
                    staff.append(" \\\\".join(L))
                    staff.append(" >>\n")
                else:           # i == 1
                    staff.append("\n\\new {}\n".format(STAFF_TYPES[self.types]))
                    staff.append(" {{ {} }}\n".format(" ".join(processed_part[start])))
                start = end
            staff.append(">>\n\n")
        return staff
    
    def _make_monophon_staff(self):
        staff = ['\n{} = \\new {} \with {{instrumentName = #"{}" shortInstrumentName = #"{}"}}'.format(
            self.x_part.who,
            STAFF_TYPES[self.types],
            self.x_part.name,
            self.x_part.abbr)]
        staff.append("\n{\n")
        # staff.append(" ".join(self.x_part.process()))
        staff.append(" ".join(self.x_part.render()))
        staff.append("\n}")
        return staff
    
    def deploy(self):
        """to be called by kodou()"""
        if self.x_part.polyphon:
            return self._make_polyphon_staff()
        else:
            return self._make_monophon_staff()





        
class _NoteHead(_StickyMetadata):

    def __init__(self, md_dict, x_part):
        super().__init__(md_dict, x_part, "Notehead", (int, float, tuple), (str,))
        self.assertions()
        
    def attach_noteheads(self, noteheads, stream):
        x, y = min(stream), max(stream)
        usable_notehead_beats = list(filter(lambda bt: x <= bt <= y, noteheads))
        for beat in usable_notehead_beats:
            fract_beat = Fraction(beat).limit_denominator()
            if fract_beat in stream:  # this note exists, it can have another notehead
                obj = stream[fract_beat]
            else:               # find the nearest beat in stream
                nearest_stream_beat = min(stream.keys(), key=lambda x: abs(fract_beat - x))
                obj = stream[nearest_stream_beat]
            if not hasattr(obj, "notehead"): # perhaps interpose has already setattr?
                setattr(obj, "notehead", noteheads[beat])
    
    def apply_(self, ):
        if self.voice_dependent_metadata:
            for voice in sorted(self.md_dict_cp):
                noteheads = _Space(self.md_dict_cp[voice], max(self.x_part.longest_stream())).arrange()
                # remove the first automatic revert notehead style,
                # it was only useful for finding Spaces
                if 0 in noteheads and noteheads[0].startswith("\\revert"):
                    noteheads.__delitem__(0)
                stream = self.x_part.events.stream[voice]
                self.attach_noteheads(noteheads, stream)
        else:                   # gibt es auch kein md_dict_cp
            noteheads = _Space(self.md_dict, max(self.x_part.longest_stream())).arrange()
            # remove the first automatic revert notehead style,
            # it was only useful for finding Spaces
            if 0 in noteheads and noteheads[0].startswith("\\revert"):
                noteheads.__delitem__(0)
            if self.x_part.polyphon:
                for voice in sorted(self.x_part.events.stream):
                    stream = self.x_part.events.stream[voice]
                    self.attach_noteheads(noteheads, stream)
            else:
                stream = self.x_part.events.stream
                self.attach_noteheads(noteheads, stream)




                
class _PaperPart:
    """instances generate LilyPond data"""
    IDS = product(ascii_uppercase, repeat=5)  # 26**5 distinct ids

    def __init__(self, part_events, part_metadata):
    # def __init__(self, part):
        # here comes any thing a Part wants to write on top of ly file
        # like user_defined_barlines
        self.global_ly_commands = []
        # self.events = part.events
        self.events = part_events
        self.polyphon = self.events.polyphon
        # self.check_interpose_effects()
        # self.apply_metadata(part.metadata)
        self.apply_metadata(part_metadata)
        if self.events.with_duration:
            self.events.duration_obj.with_duration_endpoints_ip(
                # fractionized_durations is either polyphon or monophon
                self.events.duration_obj.fractionized_durations,
                self.events.stream)
            # Since metadata is allowed to add beats to the stream
            # the adding of missing beats takes place after applying all metadata
            self.add_missing_integer_beats_ip()
            self.set_barchecks_and_timesigchecks_ip()
            self.pb = self.processed_beats()
            self.apply_durations_ip(self.events.duration_obj.fractionized_durations, self.pb)
            # self._prepare_durations_carrier_beats_ip(self.events.duration_obj.fractionized_durations, self.pb)
        else:
            # Since metadata is allowed to add beats to the stream
            # the adding of missing beats takes place after applying all metadata
            self.add_missing_integer_beats_ip()            
            self.set_barchecks_and_timesigchecks_ip()
            self.pb = self.processed_beats()        
        self.cleanup_ip()
        self.render()

    def apply_durations_ip(self, durations, processed_beats):
        if self.events.duration_obj.polyphon:
            for voice in sorted(durations):
                notes = [self.events.stream[voice][dur_beat].note for dur_beat in sorted(durations[voice])]
                self._prepare_durations_carrier_beats_ip(durations[voice], notes, processed_beats[voice])
        else:
            notes = [self.events.stream[dur_beat].note for dur_beat in sorted(durations)]
            self._prepare_durations_carrier_beats_ip(durations, notes, processed_beats)
        
    def _prepare_durations_carrier_beats_ip(self, durations, notes, processed_beats):
        sorted_duration_beats = sorted(durations)
        sorted_processed_beats = sorted(processed_beats)
        # carrier_beats are those holding a note with tied durations
        carrier_beats = dict()

        for k, dur_beat in enumerate(sorted_duration_beats):
            # end_point will be a Fraction
            end_point = dur_beat + durations[dur_beat]
            carrier_beats[dur_beat] = dict()
            beats = list(filter(lambda beat: dur_beat <= beat < end_point, sorted_processed_beats))
            carrier_beat = beats[0]
            protected_beats = [carrier_beat]
            # note = self.events.stream[dur_beat].note
            note = notes[k]
            for i, beat in enumerate(beats):
                # Extract infromations of this beat
                beat_dict = processed_beats[beat]
                prtmd, pstmd = beat_dict["obj"]
                tuplet_start, tuplet_end = beat_dict["tuplet_start"], beat_dict["tuplet_end"]
                lily_val = beat_dict["val"]
                
                if carrier_beat == "empty":
                    carrier_beat = beat
                    carrier_beats[dur_beat][carrier_beat] = {
                        "ts": tuplet_start,
                        "te": tuplet_end,
                        "pstmd": pstmd,
                        "prtmd": prtmd,
                        "note": note,
                        "lily_vals": [lily_val]}
                    if tuplet_end:
                        carrier_beat = "empty"
                    if "barcheck" in beat_dict:
                        carrier_beats[dur_beat][carrier_beat]["barcheck"] = beat_dict["barcheck"]
                        if beat in protected_beats:
                            del processed_beats[beat]["barcheck"]
                        carrier_beat = "empty"
                else:
                    if carrier_beat not in carrier_beats[dur_beat]:
                        carrier_beats[dur_beat][carrier_beat] = {
                            "ts": tuplet_start,
                            "te": tuplet_end,
                            "pstmd": pstmd,
                            "prtmd": prtmd,
                            "note": note,
                            "lily_vals": []}
                    # New carrier_beat
                    if len(pstmd) > 1 or prtmd or tuplet_start:
                        carrier_beat = beat
                        carrier_beats[dur_beat][carrier_beat] = {
                            "ts": tuplet_start,
                            "te": tuplet_end,
                            "pstmd": pstmd,
                            "prtmd": prtmd,
                            "note": note,
                            "lily_vals": [lily_val]}
                        # Protect this beat from being removed,
                        # but unset properties for not being glued for a second time.
                        processed_beats[beat]["tuplet_end"] = None
                        processed_beats[beat]["tuplet_start"] = None
                        processed_beats[beat]["obj"] = [{}, {3: ""}]
                        protected_beats.append(beat)
                        if "barcheck" in beat_dict:
                            carrier_beat = "empty"
                        
                    elif tuplet_end:
                        # This beat will be removed, so save the te-infromation.
                        carrier_beats[dur_beat][carrier_beat]["lily_vals"].append(lily_val)
                        carrier_beats[dur_beat][carrier_beat]["te"] = tuplet_end
                        # i.e. if beat is the head of carrier_beats, it is protected
                        if beat in protected_beats:
                            processed_beats[beat]["tuplet_end"] = None
                        carrier_beat = "empty"
                        
                    elif "barcheck" in beat_dict:
                        # This beat will be removed.
                        carrier_beats[dur_beat][carrier_beat]["lily_vals"].append(lily_val)
                        carrier_beats[dur_beat][carrier_beat]["barcheck"] = beat_dict["barcheck"]
                        # i.e. if beat is the head of carrier_beats, it is protected
                        if beat in protected_beats:
                            del processed_beats[beat]["barcheck"]
                        carrier_beat = "empty"
                        
                    else:
                        # This beat will also be removed.
                        carrier_beats[dur_beat][carrier_beat]["lily_vals"].append(lily_val)
                    
            for beat in beats:
                if beat not in protected_beats:
                    del processed_beats[beat]
        
        # print(carrier_beats)
        # From here things will be sent to cleanup and render.
        for dur_beat in sorted(carrier_beats):
            sorted_carrier_beats = sorted(carrier_beats[dur_beat])
            last_carrier_beat_idx = len(sorted_carrier_beats) - 1
            # All prtmd and pstmd of an obj belongs only to the carrier_beat.
            duration_tied = []
            for i, carrier_beat in enumerate(sorted_carrier_beats):
                # ALL THIS SHIT IS ONE DURATION!
                lilyvals = parse_lilyvals(carrier_beats[dur_beat][carrier_beat]["lily_vals"])
                note = carrier_beats[dur_beat][carrier_beat]["note"]
                prtmd, pstmd = carrier_beats[dur_beat][carrier_beat]["prtmd"], carrier_beats[dur_beat][carrier_beat]["pstmd"]
                ts, te = carrier_beats[dur_beat][carrier_beat]["ts"], carrier_beats[dur_beat][carrier_beat]["te"]
                try:
                    bch = carrier_beats[dur_beat][carrier_beat]["barcheck"]
                except KeyError:
                    bch = None

                # Start with 1. pre_tuplet_metadata in order
                carrier_beat_tied = [prtmd[key] for key in sorted(prtmd)]

                # 2. tuplet_start
                if ts:
                    for ts_ in ts:
                        carrier_beat_tied.append(ts_)

                # 3. post_tuplet_metadata in order
                tmp_note = ""
                for md_key in sorted(pstmd):
                    if md_key != 3:
                        tmp_note += pstmd[md_key]
                    else:
                        # lilyvals[0] is the head of a carrier_beat
                        lv_head = lilyvals[0]
                        for j, dot_val in enumerate(lv_head):
                            if j == 0:
                                tmp_note += (note + str(dot_val))
                            else:
                                tmp_note += "."

                        # Is this the last of carrier_beats?
                        # If no it gets a tie.
                        if i < len(sorted_carrier_beats) - 1:
                            tmp_note += "~"
                        else:   # If yes:
                            # it gets a tie only if there are more than 1 lilyvals,
                            # and since i am on the head of lilyvals, it gets a tie.
                            if len(lilyvals) > 1:
                                tmp_note += "~"

                # 4. After all metadata was attached, look for tails of the duration of this carrier_beat.
                lv_tail = lilyvals[1:]
                for j, tail in enumerate(lv_tail, 1):
                    tmp_note += " "
                    for k, dot_val in enumerate(tail):
                        if k == 0:
                            tmp_note += (note + str(dot_val))
                        else:
                            tmp_note += "."

                    if i < len(sorted_carrier_beats) - 1:
                        tmp_note += "~"
                    else:
                        if j < len(lilyvals) - 1:
                            tmp_note += "~"
                
                carrier_beat_tied.append(tmp_note)

                # 5. tuplet_end
                if te:
                    for te_ in te:
                        carrier_beat_tied.append(te_)

                # 5. barcheck
                if bch:
                    carrier_beat_tied.append(bch)
                
                duration_tied.append(" ".join(carrier_beat_tied))

            processed_beats[dur_beat]["obj"][1][3] = " ".join(duration_tied)
    
    
    def render(self):
        """glue everything together"""
        rendered = []
        if self.polyphon:
            for voice in sorted(self.pb):
                rendered_voice = []
                for beat in sorted(self.pb[voice]):
                    beat_dict = self.pb[voice][beat]
                    glued_beat_dict = _glue(beat_dict)
                    rendered_voice.append(" ".join(glued_beat_dict))
                rendered.append(rendered_voice)
        else:
            for beat in sorted(self.pb):
                beat_dict = self.pb[beat]
                glued_beat_dict = _glue(beat_dict)
                rendered.append(" ".join(glued_beat_dict))
        return rendered

    
    def longest_stream(self, ):
        """returns the stream itself, not a copy of it"""
        if self.polyphon:
            voice = sorted(
                self.events.stream,
                key=lambda voice: max(self.events.stream[voice]),
                reverse=True)[0]
            return self.events.stream[voice]
        else:
            return self.events.stream
        
    # def apply_non_beat_generator_metadata(self, metadata):
    #     barline = _BarLine(metadata["barline"], self)
    #     barline.apply_()
    #     # user_definitions will be ready after apply_
    #     self.global_ly_commands.extend(barline.user_definitions)

    # def apply_beat_generator_metadata(self, metadata):
    #     self.apply_who(metadata["who"])
    #     self.apply_what(metadata["what"])
    #     # sticky
    #     _TimeSignature(metadata["timesig"], self).apply_()
    #     _NoteHead(metadata["notehead"], self).apply_()
    #     _Clef(metadata["clef"], self).apply_()
    #     # unsticky
    #     _Articulation(metadata["articulation"], self).apply_()
    #     # barline = _BarLine(metadata["barline"], self)
    #     # barline.apply_()
    #     # # user_definitions will be ready after apply_
    #     # self.global_ly_commands.extend(barline.user_definitions)
    #     dynamic = _Dynamic(metadata["dynamic"], self)
    #     # user_definitions will be generated by apply_
    #     dynamic.apply_()
    #     self.global_ly_commands.extend(dynamic.user_definitions)
    #     _Legato(metadata["legato"], self).apply_()
    #     # self.staff.deploy will be called be kodou()
    #     self.staff = _Staff(metadata["staff"], self)
        
    def apply_metadata(self, metadata):
        """will be called by kodou.kodou()
        metadata is guaranteed to have these keys by now,
        all of following methodes change the self.events.stream in-place
        or set new attrs"""
        self.apply_who(metadata["who"])
        self.apply_what(metadata["what"])
        # sticky
        _TimeSignature(metadata["timesig"], self).apply_()
        _NoteHead(metadata["notehead"], self).apply_()
        _Clef(metadata["clef"], self).apply_()
        # unsticky
        _Articulation(metadata["articulation"], self).apply_()
        barline = _BarLine(metadata["barline"], self)
        barline.apply_()
        # user_definitions will be ready after apply_
        self.global_ly_commands.extend(barline.user_definitions)
        dynamic = _Dynamic(metadata["dynamic"], self)
        # user_definitions will be generated by apply_
        dynamic.apply_()
        self.global_ly_commands.extend(dynamic.user_definitions)
        _Legato(metadata["legato"], self).apply_()
        # self.staff.deploy will be called be kodou()
        self.staff = _Staff(metadata["staff"], self)

    def apply_who(self, who):
        """id"""
        if who == "_klarenz":       # no id declared
            self.who = "KLARENZ" + "".join(next(_PaperPart.IDS))
        else:
            self.who = who
            
    def apply_what(self, what):
        self.name = what.get("name", "")
        self.abbr = what.get("abbr", "")

        
    # stream is by now Fractional
    def add_missing_integer_beats_ip(self, ):
        if self.polyphon:
            for voice in sorted(self.events.stream):
                missing_beats = dict()
                max_bt = int(floor(max(self.events.stream[voice]))) + 1
                existing_beats = [floor(beat) for beat in self.events.stream[voice].keys()]
                # difference = set(range(int(max_bt))).difference(existing_beats)
                difference = set(range(max_bt)).difference(self.events.stream[voice].keys())
                for beat in difference:
                    f = Fraction(beat).limit_denominator()
                    missing_beats[f] = _Note(beat=f)
                self.events.stream[voice].update(missing_beats)
        else:
            missing_beats = dict()
            max_bt = int(floor(max(self.events.stream))) + 1
            # existing_beats = {floor(beat) for beat in self.events.stream.keys()}
            difference = set(range(max_bt)).difference(self.events.stream.keys())
            # add missing_beats to the stream
            for beat in difference:
                FB = Fraction(beat).limit_denominator()
                missing_beats[FB] = _Note(beat=FB, from_miss=True)
            self.events.stream.update(missing_beats)

            
    def make_beat_groups(self, ):
        """returns a list of grouped beats as dicts"""
        L = []
        if self.polyphon:
            for voice in sorted(self.events.stream):
                l = []
                max_bt = floor(max(self.events.stream[voice])) + 1
                for i in range(int(max_bt)):
                    group = list(
                        filter(
                            lambda beat: i <= beat < i + 1, self.events.stream[voice]
                        )
                    )
                    if group:
                        # pack beatwise
                        group = {bt: self.events.stream[voice][bt] for bt in group}
                        l.append(group)
                L.append(l)
        else:
            max_bt = floor(max(self.events.stream)) + 1
            for i in range(int(max_bt)):
                group = list(filter(lambda beat: i <= beat < i + 1,
                                    sorted(self.events.stream)))
                if group:
                    # packing single beats
                    group = {bt: self.events.stream[bt] for bt in group}
                    L.append(group)
        return L

    
    def pstmd_contains_rest(self, pstmd):
        """post_tuplet_metadata contains a rest?"""
        return pstmd[3].startswith("Or")


    def pstmd_contains_note(self, pstmd):
        """post_tuplet_metadata contains a note?"""
        return not self.pstmd_contains_rest(pstmd)
        

    def pstmd_cleanup_chunks(self, processed_beats, identity_test_func):
        """group chunks of ascending notes/rests based on the identity_test_func"""
        chunks = []
        chunk = []        
        for beat in sorted(processed_beats):
            _, pstmd = processed_beats[beat]["obj"]
            if identity_test_func(pstmd):
                chunk.append(beat)
            else:
                if chunk:
                    chunks.append(chunk)
                chunk = []
        if chunk:
            chunks.append(chunk)
        return chunks


    def chunk_slices(self, chunks, processed_beats):
        """Slice rest_chunks based on their properties/positions"""
        chunk_slices = []
        for chunk in chunks:
            i = 0
            chunk_slice = []
            while True:
                try:
                    beat = chunk[i]
                    # beat_dict = self.pb[beat]
                    beat_dict = processed_beats[beat]
                    prtmd, pstmd = beat_dict["obj"]
                    # If there is some metadata this will be a standalone,
                    # no matter what other properties it has.
                    if len(pstmd) > 1:
                        # Save things
                        if chunk_slice:
                            chunk_slices.append(chunk_slice)
                        # Append the standalone
                        chunk_slices.append([beat])
                        # Start an empty slice
                        chunk_slice = []
                    else:       # len(pstmd) is at least 1
                        if "barcheck" in beat_dict or \
                           beat_dict["tuplet_end"]:
                            # Include the rest itself
                            chunk_slice.append(beat)
                            # Save all till now
                            if chunk_slice:
                                chunk_slices.append(chunk_slice)
                            # Then start a new empty slice
                            chunk_slice = []
                        elif beat_dict["tuplet_start"] or \
                             prtmd:
                            # Save things till now
                            if chunk_slice:
                                chunk_slices.append(chunk_slice)
                            # Start a new slice with this beat included
                            chunk_slice = [beat]
                        else:
                            chunk_slice.append(beat)
                except IndexError:
                    if chunk_slice:
                        chunk_slices.append(chunk_slice)
                    break
                i += 1
                
        return chunk_slices
        

    def cleanup_ip(self):
        if self.polyphon:
            for voice in sorted(self.pb):
                self._prepare_and_cleanup_ip(self.pb[voice])
        else:
            self._prepare_and_cleanup_ip(self.pb)
        
    # Removes O identifiers
    def _prepare_and_cleanup_ip(self, processed_beats):
        rest_chunks = self.pstmd_cleanup_chunks(processed_beats, self.pstmd_contains_rest)
        rest_chunk_slices = self.chunk_slices(rest_chunks, processed_beats)
        for rest_chunk_slice in rest_chunk_slices:
            carrier_beat_dict = processed_beats[rest_chunk_slice[0]]
            carrier_timesig = carrier_beat_dict["timesig_check"]
            carrier_beat_unit = carrier_timesig[1]
            n_beat_units = carrier_beat_unit / carrier_beat_dict["val"]
            for beat in rest_chunk_slice[1:]:
                beat_dict = processed_beats[beat]
                prtmd, pstmd = beat_dict["obj"]
                timesig = beat_dict["timesig_check"]
                beat_unit = timesig[1]
                n = beat_unit / beat_dict["val"]
                n_beat_units += n
                if "barcheck" in beat_dict or \
                   beat_dict["tuplet_end"]:
                    # Then keep the beat_dict since i need those keys
                    pstmd[3] = ""
                    # for i in range(len(pstmd)):
                    #     if pstmd[i].startswith("Or"):
                    #         pstmd[i] = ""
                    #         break
                else:
                    del processed_beats[beat]
                    
            carrier_beat_pstmd = carrier_beat_dict["obj"][1]
            # carrier_beat_onbeat = carrier_beat_dict["onbeat"]
            for i in range(len(carrier_beat_pstmd)):
                if carrier_beat_pstmd[3].startswith("Or"):
                # if carrier_beat_pstmd[i].startswith("Or"):
                    # Rhythm
                    rhythm_items, full_measure_rest = disassemble_rhythm(n_beat_units,
                                                                             carrier_beat_unit,
                                                                             # onbeat=carrier_beat_onbeat,
                                                                             timesig=carrier_timesig)
                    if full_measure_rest:
                        carrier_beat_pstmd[3] = full_measure_rest
                        # carrier_beat_pstmd[i] = full_measure_rest
                    else:
                        summed_rest = []
                        for n, lily_val in rhythm_items:
                            for _ in range(n):
                                summed_rest.append("r" + str(lily_val))
                        carrier_beat_pstmd[3] = " ".join(summed_rest)
                        # carrier_beat_pstmd[i] = " ".join(summed_rest)
                    break

        # Remove O identifiers from notes which still have it
        note_chunks = self.pstmd_cleanup_chunks(processed_beats, self.pstmd_contains_note)        
        for chunk in note_chunks:
            for beat in chunk:                
                note_dict = processed_beats[beat]
                note_dict_pstmd = note_dict["obj"][1]
                if note_dict_pstmd[3].startswith("O"):
                    # if note_dict_pstmd[i].startswith("O"):
                    processed_beats[beat]["obj"][1][3] = note_dict_pstmd[3].replace("O", "")


            
    # This method calls prc._process_beat
    def processed_beats(self):
        processed_beats = dict()
        if self.polyphon:
            for voice, beatgroups in enumerate(self.make_beat_groups()):
                x = dict()
                for beatgroup in beatgroups:
                    first_item = min(beatgroup)
                    try:            # a new timesig encountered
                        # If there would be a timesig it is only an attr
                        # of the first element of the beat
                        # Default timesig comes from the const.GLOBAL_METADATA,
                        # if no timesig set for the first element
                        init_val = beatgroup[first_item].timesig[1]
                    except AttributeError:
                        # This beat has no timesig.
                        # The init_val have been already set above
                        # and will be used again.
                        pass
                    output_dict = _process_beat(beatgroup, init_val)
                    for beat in sorted(output_dict):
                        x[beat] = output_dict[beat]
                processed_beats[voice] = x
        else:
            for beatgroup in self.make_beat_groups():
                first_item = min(beatgroup)
                try:            # a new timesig encountered
                    # If there would be a timesig it is only an attr
                    # of the first element of the beat
                    # Default timesig comes from the const.GLOBAL_METADATA,
                    # if no timesig set for the first element
                    init_val = beatgroup[first_item].timesig[1]
                except AttributeError:
                    # This beat has no timesig.
                    # The init_val have been already set above
                    # and will be used again.
                    pass
                output_dict = _process_beat(beatgroup, init_val)                
                for beat in sorted(output_dict):
                    processed_beats[beat] = output_dict[beat]
        return processed_beats

    # # This i dont need daan
    # def process(self):
    #     """returns a list of processed beats"""
    #     L = []
    #     if self.polyphon:
    #         # for voice in self.make_beat_groups():
    #         for voice_beatgroups in self.make_beat_groups():
    #             l = []
    #             for beatgroup in voice_beatgroups:
    #                 first_item = min(beatgroup)
    #                 try:            # a new timesig encountered
    #                     # If there would be a timesig it is only an attr
    #                     # of the first element of the beat
    #                     # Default timesig comes from the const.GLOBAL_METADATA,
    #                     # if no timesig set for the first element
    #                     init_val = beatgroup[first_item].timesig[1]
    #                 except AttributeError:
    #                     # This beat has no timesig.
    #                     # The init_val have been already set above
    #                     # and will be used again.
    #                     pass
    #                 processed_beat = prc._process_beat(beatgroup, init_val)
    #                 l.append(" ".join(prc.tokenize_beat(processed_beat)))
    #             L.append(l)
    #     else:
    #         for beatgroup in self.make_beat_groups():
    #             first_item = min(beatgroup)
    #             # if hasattr(beatgroup[first_item], "timesig"):
    #             #     init_val = beatgroup[first_item].timesig[1]
    #             try:            # a new timesig encountered
    #                 # If there would be a timesig it is only an attr
    #                 # of the first element of the beat
    #                 # Default timesig comes from the const.GLOBAL_METADATA,
    #                 # if no timesig set for the first element
    #                 init_val = beatgroup[first_item].timesig[1]
    #             except AttributeError:
    #                 # This beat has no timesig.
    #                 # The init_val have been already set above
    #                 # and will be used again.
    #                 pass
    #             processed_beat = prc._process_beat(beatgroup, init_val)
    #             L.append(" ".join(prc.tokenize_beat(processed_beat)))
    #     return L

    def set_barchecks_and_timesigchecks_ip(self):
        """sets barcheck attr for _Note objects, is useful for drawing lilypond-file barlines
        and in drawing possible ties for new durations"""
        if self.polyphon:
            for voice in sorted(self.events.stream):
                sorted_stream = sorted(self.events.stream[voice])
                upto = floor(max(sorted_stream)) + 1
                for i in range(upto):
                    # Since i is int no need to be fractionized.
                    stream_item = self.events.stream[voice][i]
                    # beats_in_question = list(filter(lambda x: i <= x < i + 1, sorted_stream))
                    # # since this method is called after add_missing_integer_beats_ip
                    # # there is always at list one item in the list
                    # first_beat_in_question = beats_in_question[0]
                    try:
                        current_timesig = stream_item.timesig
                        current_timesig_numer = current_timesig[0]                        
                        # current_timesig = self.events.stream[voice][first_beat_in_question].timesig
                        # current_timesig_numer = current_timesig[0]
                        # there was a new timesig, start counting beats from 0
                        beat_num = 0
                    except AttributeError:
                        beat_num += 1


                    # Set timesig_check at the beginnig of each beat item!
                    # This allows for calculating beat_units for apply_duration
                    # or _prepare_and_cleanup_ip even if a duration begins at a beat middle of a bar
                    setattr(stream_item, "timesig_check", current_timesig)

                    # # Mark the start of e bar.
                    # if not beat_num % current_timesig_numer:
                    #     setattr(stream_item, "bar_offset", True)

                    # Set barcheck at the end of each bar. This will be given later
                    # by prc._process_beat to the very last beat item of a bar.
                    if beat_num % current_timesig_numer == current_timesig_numer - 1:
                        setattr(stream_item, "barcheck", "|\n")

                    
                    # if beat_num % current_timesig_numer == current_timesig_numer - 1:
                    #     barcheck = True
                    # else:
                    #     barcheck = False
                    # setattr(self.events.stream[voice][first_beat_in_question], "barcheck", barcheck)                
        else:
            sorted_stream = sorted(self.events.stream)
            upto = floor(max(sorted_stream)) + 1
            for i in range(upto):
                stream_item = self.events.stream[i]
                try:
                    current_timesig = stream_item.timesig
                    current_timesig_numer = current_timesig[0]
                    # there was a new timesig, start counting beats from 0
                    beat_num = 0
                except AttributeError:
                    beat_num += 1
                
                # Set timesig_check at the beginnig of each beat item!
                # This allows for calculating beat_units for apply_duration
                # or _prepare_and_cleanup_ip even if a duration begins at a beat middle of a bar
                setattr(stream_item, "timesig_check", current_timesig)

                # # Mark the start of e bar.
                # if not beat_num % current_timesig_numer:
                #     setattr(stream_item, "bar_offset", True)
                
                # Set barcheck at the end of each bar. This will be given later
                # by prc._process_beat to the very last beat item of a bar.
                if beat_num % current_timesig_numer == current_timesig_numer - 1:
                    setattr(stream_item, "barcheck", "|\n")


    
# class _SoloMidiStream:    
#     def __init__(self, part):
#         self.events = part.events
#         self.metadata = self.extract_metadata(part.metadata)

#     def extract_metadata(self, metadata):
#         """
#         instrument = channel, duration = duration, dynamic = velocity
#         """
#         D = {}
#         D["channel"] = metadata["instrument"]["instr"]
#         D["velocity"] = metadata["dynamic"]
#         D["duration"] = metadata["duration"]
#         return D

#     def prepare(self, ):
#         if self.events.polyphon:
#             num_of_tracks = len(self.events.stream)
#             self._midifile = MidiFile.MIDIFile(num_of_tracks)
#             for track in range(num_of_tracks):
#                 for beat in sorted(self.events.stream[track]):
#                     pitch = self.events.stream[track][beat].note
#                     self._midifile.addNote(track, 0, pitch, beat, .1, 127)
#         else:
#             self._midifile = MidiFile.MIDIFile(1)
#             for beat in sorted(self.events.stream):
#                 pitch = self.events.stream[beat].note
#                 #  addNote(track, channel, pitch, time, duration, volume, annotation=None)
#                 self._midifile.addNote(0, 0, pitch, beat, .1, 127)

#     def write_file(self, path):
#         with open(path, "wb") as f:
#             self._midifile.writeFile(f)
#         if f.closed:
#             print("Solo MIDI written to {}".format(path))
