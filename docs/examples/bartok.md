```lisp

#!/usr/local/bin/hy

;;; Last five measures of Bartók’s “Wandering” from Mikrokosmos, 
;;; Volume III,
;;; Friday 15 Feb. 2019, 12:17


(import [kodou [*]])

;;; Notes
(setv +rh-notes+
      (, 69 67 65 64
         62 67 65 64 62
         60 62 64 65 64
         62
         62)
      +lh-notes-up+
      (, 59 62 60
         59 57 56 60 58
         57 55 54 55 57
         59
         59)
      +lh-notes-down+
      (, 59 57
         55))

;;; Beats
(setv +rh-beats+
      (, 0 .5 1 1.5
         2 3 3.5 4 4.5
         5 5.5 5.75 6 6.5
         7
         9)
      +lh-beats-up+
      (, 0 1 1.5
         2 2.5 3 4 4.5
         5 5.5 6 6.5 6.75
         7
         9)
      +lh-beats-down+
      (, 7 8
         9))

(setv events
      {"notes" [+rh-notes+ +lh-notes-up+ +lh-notes-down+]
       "beats" [+rh-beats+ +lh-beats-up+ +lh-beats-down+]
       "durations" {0 {7 2 9 2}
                    1 {7 2 9 2}
                    2 {9 2}}})
(setv metadata
      {"what" {"name" "PIANO"}
       "clef" {1 {0 "bass"}
               2 {0 "bass"}}
       "staff" {"n" 3 "bind""piano"}
       "timesig" {(, 0 2) (, 2 4)
                  (, 2 5) (, 3 4)
                  5 (, 2 4)}
       "dynamic" {0 {(, 0 3) "pp"
                     3 "mp"
                     (, 5 7) "<"
                     (, 7 8) ">"}
                  1 {(, 1 4) "pp"
                     4 "mp"}}
       "legato" {0 {"solid" [(, 0 3) (, 3 11)]}
                 1 {"solid" [(, 1 4) (, 7 11)]}
                 2 {"solid" [(, 7 11)]}}
       "barline" {10 "|."}})

(kodou (Part events metadata))
```

![bartok](../jpg/bartok.jpg "Bartok")
