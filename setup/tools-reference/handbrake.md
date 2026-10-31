# HandBrake (command line)

Converts and shrinks video files, using the same engine as the HandBrake app.

```
HandBrakeCLI -i input.mov -o output.mp4 --preset "Fast 1080p30"
HandBrakeCLI --preset-list
```

**Gotcha:** The command is `HandBrakeCLI`, with capital letters. Big files take a long time; it uses every processor core while it runs.
