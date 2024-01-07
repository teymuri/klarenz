
import klarenz as k


k.proc(
    k.Part(
        events={
            "pchs": [60 + i for i in (0, 2, 4, 5, 7, 9, 11, 12)],
            "onsets": range(12)
        }
    )
)
