from random import randint
import computil
from kodou import *

print(computil.utils.note_to_number)



# bts = []
with open("/tmp/bar.txt", "r") as file:
    for line in file.readlines():
        main = [float(x) for x in line.strip().split(" ")]
        # bts = set(bts + next(g_))
        # bts = sorted(list(bts))

# bts = sorted(list(bts))
print(main)


# pyly(
#     [
#         Part(
#             {
#                 "notes": list(range(48, 96)) * 10,
#                 "beats": main,
#                 # "durations": {
#                 #     0: {
#                 #         i:3/26 for i in range(12)
#                 #     }
#                 # }
#             },
#             # metadata
#             {
#                 "what": {"name": "Leonie"},
#                 # "staff": {"n": 3}
#                 "articulation": {x: "accent" for x in main}
#             }
#         ),
#         # Part(
#         #     {
#         #         "notes": range(72, 84),
#         #         "beats": [2/3 * i for i in range(12)],
#         #         # "durations": {
#         #         #     0: {
#         #         #         i:3/26 for i in range(12)
#         #         #     }
#         #         # }
#         #     },
#         #     # metadata
#         #     {
#         #         "what": {"name": "yoyo"},
#         #         # "staff": {"n": 3}
#         #     }
#         # )
#     ]
# )
