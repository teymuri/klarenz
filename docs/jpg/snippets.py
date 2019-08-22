from kodou import *



kodou(Part(events={"notes": range(60, 84),
                   "beats": range(24)},
           metadata={"clef": {
               (0.5, 8+1/3): "alto",
               (4, 6): "tenor",
               8+2/3: "treble+9",
               13.5: "treble-8",
               16: "soprano"
           }}))


kodou(Part(events={"notes": range(60, 84),
                   "beats": range(24)},
           metadata={"notehead": {
               (.5, 8+1/3): "mensural",
               (4, 6): "harmonic",
               8+2/3: "cross",
               13.5: "triangle",
               16: "xcircle"
           }}))


kodou(Part(events={"notes": range(60, 84),
                   "beats": range(24)},
           metadata={"legato": {
               "solid": ((1, 15.5),
                         (3+1/3, 5),
                         (5, 7)),
               "halfdashed": [(7, 12.5),
                              (12.5, 17)],
               "dotted": ((8, 9),
                          (16, 23))
           }}))


kodou(Part(events={"notes": range(60, 84),
                   "beats": range(24)},
           metadata={"dynamic": {
               (0, 6): "<",
               (2, 5.1): ">",
               5.5: "sf",
               4: "mp",
               (6.5, 23): "dim",
               (10+2/3, 15.5): "cr",
               13+3/7: "p",
               23: "rfz"
           }}))


kodou(Part(events={"notes": range(60, 84),
                   "beats": range(24)},
           metadata={"timesig": {
               (1, 12): (3, 8),
               (4, 7): [2, 32],
               17: (5, 4),
               (19, 20): (1, 8)
           }}))





kodou(Part(events={"notes": range(60, 72),
                   "beats": range(12)},
           metadata={"articulation": {
	        3: (">", "."),
		(1, 7): "staccatissimo",
		(4, 6): ["prall", "^", "trill", "turn"],
		10.5: ("fermata", "trill"),
		11: "<>"
	   }}))



