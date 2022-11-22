from kodou import *
def ntimesx(n, x):
    return [x for _ in range(n)]
kodou(
    (
        Part(
            {"notes": [ntimesx(60, 60), 
                      #  ntimesx(60, 60),
                      # ntimesx(60, 60)
                      ],
             "beats": [[x*.5 for x in range(60)], 
                       [x*1/3 for x in range(60)],
                      [x*1/5 for x in range(60)]]}
        )
    )
)
