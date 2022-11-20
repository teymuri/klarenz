# import it
from kodou import *

# kodou(Part(events={"notes": range(60, 84),
#                    "beats": range(24)},
#            # metadata={"timesig": {
#            #     (1, 12): (3, 8),
#            #     (4, 7): [2, 32],
#            #     17: (5, 4),
#            #     (19, 20): (1, 8)
#            # }}
#           ))

# kodou(Part(events={"notes": range(60, 84),
#                    "beats": range(24)},
#            metadata={"clef": {
#                (0.5, 8+1/3): "alto",
#                (4, 6): "tenor",
#                8+2/3: "treble+9",
#                13.5: "treble-8",
#                16: "soprano"
#            }}))
def b():
    i = 0
    while True:
        yield 60 + 12 * (i % 4)
        i += 1
B = b()
print([next(B) for _ in range(10)])
kodou(Part(events={"notes": [next(B) for _ in range(53)],
                   "beats": range(3, 480, 9)}))
