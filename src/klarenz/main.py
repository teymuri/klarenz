from subprocess import *
from time import sleep
from os.path import (expanduser, abspath)

from .classes import (Part, _PaperPart)
from .process import (prepare_ly, dict_integration_ip, dict_integrate)
from .const import (GLOBAL_METADATA, LP_OUTPUT_FORMATS, 
                          PDFVIEW_WAIT, DOTFILE)



def proc(score,
          metadata={},
          file_name="klarenz",
          path="/tmp",
          dotfile=DOTFILE,
          outputs=["pdf"],
          view=True):
    """the main processing function"""
    dotfile = expanduser(dotfile)
    path_ = expanduser(path)
    # add missing md from GLOBALS to metadata
    # dict_integration_ip(metadata, GLOBAL_METADATA)
    updated_md = dict_integrate(metadata, GLOBAL_METADATA)
    # check whether solo or ensemble
    if isinstance(score, list) or isinstance(score, tuple):
        solo = False
        score_template = ["\n\\score {\n<<\n", " >>\n}"]
        updated_part_md = []
        for part in score:
            # dict_integration_ip(part.metadata, metadata)
            updated_part_md.append(dict_integrate(part.metadata, updated_md))
    elif isinstance(score, Part):
        solo = True
        score_template = ["\n\\score {\n", "\n}"]
        # dict_integration_ip(score.metadata, metadata)
        updated_score_md = dict_integrate(score.metadata, updated_md)
    else:
        raise TypeError("Invalid Parts!")
    # process midi
    if set(outputs).intersection(["midi", "mid"]):
        raise NotImplementedError("Midi output is not there yet :-(")
    # process papers
    non_midi_formats = set(outputs).difference(("midi", "mid"))
    if non_midi_formats: # write ly data
        if solo: # score is a Part object
            paper_part = _PaperPart(score.events, updated_score_md)
            # paper_part = _PaperPart(score)
            # part want add something at top of the ly file
            parts_global_ly_commands = paper_part.global_ly_commands  #  a list of strings
            score_template.insert(1, " \{}".format(paper_part.who))
            staff = "".join(paper_part.staff.deploy())
        else:
            paper_parts = [_PaperPart(part.events, part_md) for part, part_md in zip(score, updated_part_md)]
            parts_global_ly_commands = []
            for idx, part in enumerate(paper_parts, 1):
                score_template.insert(idx, " \{}\n".format(part.who))
                # does part want add something at the top of the ly file?
                parts_global_ly_commands.extend(part.global_ly_commands)
            staff = "".join(["".join(part.staff.deploy()) for part in paper_parts])
        # prepare ly file
        ly_name = ".".join((file_name, "ly"))
        ly_path = "/".join((path_, ly_name))
        viewer, lilypond = prepare_ly(ly_path, dotfile, parts_global_ly_commands)
        # write to ly file
        with open(ly_path, "a") as ly:
            ly.write("%%%%%%%%%%%%%\n%%% Parts %%%\n%%%%%%%%%%%%%\n")
            ly.write(staff)
            ly.write("\n\n%%%%%%%%%%%%%\n%%% Score %%%\n%%%%%%%%%%%%%\n")
            ly.write("".join(score_template))
        # compiling + viewing
        compile_flags = set(LP_OUTPUT_FORMATS.keys()).intersection(non_midi_formats)
        compile_flags = " ".join([LP_OUTPUT_FORMATS[flag] for flag in compile_flags])
        lilypond_popenargs = [lilypond, "-o", "/".join((path_, file_name)), compile_flags, ly_path]
        Popen(lilypond_popenargs)
        if view:
            pdf_name = ".".join((file_name, "pdf"))
            pdf_path = "/".join((path_, pdf_name))
            viewer_popenargs = [viewer, pdf_path]
            sleep(PDFVIEW_WAIT)
            Popen(viewer_popenargs)
