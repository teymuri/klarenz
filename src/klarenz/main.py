from subprocess import *
from time import sleep
from os.path import (expanduser, abspath)

from .version import *
from .classes import (Part, _PaperPart)
from .process import (
    prepare_ly_ip, dict_integration_ip, dict_integrate,
    get_dotfile_commands
)
from .const import (
    GLOBAL_METADATA, LP_OUTPUT_FORMATS, 
    PDFVIEW_WAIT, DOTFILE,
    PDF_VIEWER, LY_BIN
)



def proc(score,
         metadata={},
         file_name="klarenz",
         path="/tmp",
         dotfile=DOTFILE,
         outputs=["pdf"],
         viewpdf=True,
         write_score_items_only=False
        ):
    """the main processing function"""
    dotfile = expanduser(dotfile)
    path_ = expanduser(path)
    # add missing md from GLOBALS to metadata
    # dict_integration_ip(metadata, GLOBAL_METADATA)
    updated_md = dict_integrate(metadata, GLOBAL_METADATA)
    # Check whether solo or ensemble
    if isinstance(score, list) or isinstance(score, tuple):
        solo = False
        score_template = ["\n\\score {\n<<\n", " >>\n}"]
        updated_part_md = []
        for part in score:
            updated_part_md.append(dict_integrate(part.metadata, updated_md))
    elif isinstance(score, Part):
        solo = True
        score_template = ["\n\\score {\n", "\n}"]
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
            staff = "\n".join(["".join(part.staff.deploy()) for part in paper_parts])
        # prepare ly file (BAD: prepare_ly_ip also writes to file, not only preparing...)
        ly_name = ".".join((file_name, "ly"))
        ly_path = "/".join((path_, ly_name))
        if not write_score_items_only:
            prepare_ly_ip(ly_path, dotfile, parts_global_ly_commands)
        else: # Clean up the ly file, otherwise the open with 'a' flag below will append to the lastly written ly_path
            open(ly_path, 'w').close()
        dotfile_commands_dict = get_dotfile_commands(dotfile)
        viewer = dotfile_commands_dict.get("pdf_viewer", PDF_VIEWER)
        lilypond = dotfile_commands_dict.get("ly_bin", LY_BIN)
        # write to ly file
        with open(ly_path, "a") as ly:
            ly.write("%%% Load parts and score %%%\n")
            ly.write(staff)
            ly.write("\n") # Can I get rid of this newline?
            ly.write("".join(score_template))
        # Compiling only if we need corresponding formats
        if "pdf" in outputs: # or svg or png or jpg ....
            compile_flags = set(LP_OUTPUT_FORMATS.keys()).intersection(non_midi_formats)
            compile_flags = " ".join([LP_OUTPUT_FORMATS[flag] for flag in compile_flags])
            lilypond_popenargs = [lilypond, "-o", "/".join((path_, file_name)), compile_flags, ly_path]
            print(f"%%% Klarenz {version} %%%")
            Popen(lilypond_popenargs)
            # Viewing the pdf
            if viewpdf:
                pdf_name = ".".join((file_name, "pdf"))
                pdf_path = "/".join((path_, pdf_name))
                viewer_popenargs = [viewer, pdf_path]
                sleep(PDFVIEW_WAIT)
                Popen(viewer_popenargs)
        # Check if str-return needed (mainly for testing purposes)
        if "str" in outputs:
            with open(ly_path, "r") as file:
                return file.read()
