# demo video source

The README's GIF and `assets/demo.mp4` are rendered from this [Remotion](https://remotion.dev) project.
`public/*.mp3` are the actual macOS system sounds the plugin plays, so the video has real audio.

```bash
npm i
npx remotion studio                       # preview
npx remotion render Demo out/demo.mp4     # render
```

To regenerate the README GIF from the rendered mp4:

```bash
ffmpeg -ss 2.6 -t 12.9 -i out/demo.mp4 \
  -vf "fps=12,scale=760:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=3" \
  -loop 0 ../assets/demo.gif
```
