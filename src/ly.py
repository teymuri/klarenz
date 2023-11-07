
# polymetric notation
UNEQUAL_LENGTH_MEASURES_POLYMETRY = """
\layout {
  \context {
    \Score
    \\remove "Timing_translator"
    \\remove "Default_bar_line_engraver"
  }
  \context {
    \Staff
    \consists "Timing_translator"
    \consists "Default_bar_line_engraver"
    \RemoveEmptyStaves
  }
}
"""

HEADER_TAGLINE = """
\header {
tagline = ##f
}
"""

PAPER = """
\paper {
	left-margin = 20
	right-margin = 20
	score-system-spacing = #'( (basic-distance . 10) (minimum-distance . 10) (padding . 10) (stretchability . 0) )
	system-system-spacing = #'( (basic-distance . 0) (minimum-distance . 0) (padding . 10) (stretchability . 0) )
	top-margin = 20
	bottom-margin = 20
	indent = 0
    %% entfernt die Trennline oberhalb der Fußnotentexte am Seitenende
    footnote-separator-markup = ##f  
}
"""
