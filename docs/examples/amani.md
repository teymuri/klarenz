
```lisp
#!/usr/local/bin/hy

;;; Jane Maryam 
;;; Arranged by Majid Amani (c) 2012 (excerpt)

(import [kodou [*]])

(do
  (setv melody-notes
        (, 69 71 72 74
           76 76 76 79 76
           76 81 76 81 76
           76 77 74 76 72
           74 76 72 74 71
           72 74 71 72 69
           72 71 69 71 67
           69
           72 71 69 71 67
           69
           72 71 69 71 67
           69)
        melody-beats
        (, 2 3 4 5
           6 7.5 8 9 10
           12 13.5 14 15 16
           18 19.5 20 21 22
           24 25.5 26 27 28
           30 31.5 32 33 34
           36 37.5 38 39 40
           42
           48 49.5 50 51 52
           54
           60 61.5 62 63 64
           66)
        melody-durs
        {6 1.5 10 2
         12 1.5 16 2
         18 1.5 22 2
         24 1.5 28 2
         30 1.5 34 2
         36 1.5 40 2
         42 6
         48 1.5 52 2
         54 6
         60 1.5 64 2
         66 6}
        bass-notes
        (, 52 57
           60 64
           69 72
           52
           53
           52
           55 52
           57 60
           55 52
           57 60
           55 52
           55 52)
        bass-beats
        (, 0 3
           6 9
           12 15
           18
           24
           30
           36 39
           42 45
           48 51
           54 57
           60 63
           66 69)
        bass-durs
        {0 3 3 3
         6 3 9 3
         12 3 15 3
         18 6
         24 6
         30 6
         36 3 39 3
         42 3 45 3
         48 3 51 3
         54 3 57 3
         60 3 63 3
         66 3 69 3})
  (kodou (Part {"notes" (, melody-notes bass-notes)
                "beats" (, melody-beats bass-beats)
                "durations" {0 melody-durs
                             1 bass-durs}}
               {"who" "guitar"
                "timesig" {0 (, 6 8)}})))
```


![amani](../jpg/amani.jpg "Amani")
