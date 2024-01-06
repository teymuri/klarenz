import pytest
import klarenz as K



def test_solid():
    output = K.proc(
        K.Part(
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
        outputs=["str"]
    ).replace("\n", "").replace(" ", "")
    lystr = r"""%%%GeneratedbyKlarenzv1.2.0%%%%%%Loadmodules,setup&configurations%%%#(set-default-paper-size"quarto")#(set-global-staff-size14)\version"2.22.2"\language"deutsch"\header{tagline="GeneratedbyKlarenzv1.2.0"}\layout{\context{\Score\remove"Timing_translator"\remove"Default_bar_line_engraver"}\context{\Staff\consists"Timing_translator"\consists"Default_bar_line_engraver"\RemoveEmptyStaves}}\paper{left-margin=20right-margin=20score-system-spacing=#'((basic-distance.10)(minimum-distance.10)(padding.10)(stretchability.0))system-system-spacing=#'((basic-distance.0)(minimum-distance.0)(padding.10)(stretchability.0))top-margin=20bottom-margin=20indent=0%%entferntdieTrennlineoberhalbderFußnotentexteamSeitenendefootnote-separator-markup=##f}%%%%%%%%%%%%%%%%Parts%%%%%%%%%%%%%%%%KLARENZAAAAA=\newStaff\with{instrumentName=#""shortInstrumentName=#""}{\clef"treble"\time4/4\tieSolidc'4~\tieSolidc'4~c'4\tieSolidg'4~|\tieSolidg'4~g'4\tieSolidc'''4~c'''4|}%%%%%%%%%%%%%%%%Score%%%%%%%%%%%%%%%%\score{\KLARENZAAAAA}"""
    assert output == lystr
