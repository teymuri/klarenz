from random import randint
from kodou import *
pyly(
    [
        Part(
            {
                "notes": range(72, 84),
                "beats": [2/3 * i for i in range(12)],
                # "durations": {
                #     0: {
                #         i:3/26 for i in range(12)
                #     }
                # }
            },
            # metadata
            {
                "what": {"name": "fofo"},
                # "staff": {"n": 3}
            }
        ),
        Part(
            {
                "notes": range(72, 84),
                "beats": [2/3 * i for i in range(12)],
                # "durations": {
                #     0: {
                #         i:3/26 for i in range(12)
                #     }
                # }
            },
            # metadata
            {
                "what": {"name": "yoyo"},
                # "staff": {"n": 3}
            }
        )
    ]
)
