# Rhythm in Kodou

Suppose you want to have a the note middle c as the second eight-note of a triole:

![triole_A](./jpg/about_time_triole.png)

In LilyPond (and almost all other music notation software) you have to supply the software excplicitely about with durations, in order to construct the rhythm. This approach also requires durational indications of all rests. In LilyPond you would do this as:

```lilypond
{\tuplet 3/2 { r8 c'8 r8 }}
```

which looks very strighforward, as the example is still very basic. Now consider a slightly more complex example, where you want the second triplet eight note to be subdivided itself into five thirty-second notes, from which the third is again the middle c and the remaining are rests:

```lilypond
{\tuplet 3/2 
 { 
   r8 
   \tuplet 5/4
   {
     r32 r c' r r
   }
   r8
 }
}
```

Although still quite basic in terms of rhythm, you are starting to do more typing work by nesting the second ```\tuplet``` command inside the first one, and calculating the correct duration indications for the new notes. 