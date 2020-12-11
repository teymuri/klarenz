# Rhythm in Kodou

Suppose you want to have the C4 (c' or MIDI-Keynumber 60) as the second eight note of a triplet:

![triole_A](./jpg/about_time_triole.png)

In LilyPond (and almost all music notation software) you have to supply the software excplicitely with duration values, in order to construct the rhythm. This approach also requires you to indicate all values for possible rests. In LilyPond you would write this as:

```
{\tuplet 3/2 { r8 c'8 r8 }}
```

which looks very straighforward, as the example is still very basic.

Now consider a slightly more complex example, where you want the second triplet eight note to be subdivided itself into five thirty-second notes, from which the third one is C4 and the remaining are rests:

![triole_A](./jpg/about_time-2.png)

Again in LilyPond:

```
{\tuplet 3/2 { r8 \tuplet 5/4 { r32 r c' r r } r8 }}
```

Although still quite basic in terms of rhythm, you are starting to do more typing work by nesting the second ```\tuplet``` command inside the first one, and also thinking about the correct duration values for the new notes and rests (32). 