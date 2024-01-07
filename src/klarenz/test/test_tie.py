import pytest
from .. import *





def test_solid():
    output = proc(
        Part(
            {
                "notes": (60, 60, 60, 67, 67, 67, 84, 84),
                "beats": range(8),
            },
            {
                "tie": {
                    "solid": (
                        (0, 2),
                        (3, 5),
                        (6, 7)
                    )
                }
            }
        ),
        outputs=["str"],
        write_score_items_only=1
    ).replace("\n", "").replace(" ", "")
    lystr = r"""%%%Loadpartsandscore%%%KLARENZAAAAA=\newStaff\with{instrumentName=#""shortInstrumentName=#""}{\clef"treble"\time4/4\tieSolidc'4~\tieSolidc'4~c'4\tieSolidg'4~|\tieSolidg'4~g'4\tieSolidc'''4~c'''4|}\score{\KLARENZAAAAA}"""
    assert output == lystr
