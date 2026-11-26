# world-news-2026-11-25

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/GAD2412/world-news-2026-11-25/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/GAD2412/world-news-2026-11-25/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

One front page summing up the world news of Wednesday 25 November 2026: 40 stories across
9 regions plus global items, each tagged CONFIRMED, OFFICIAL, REPORTED or CLAIM, with a UTC
timeline, the day in numbers, a dotted world map and a date check of earlier news left out.
`render.py` draws the page with Pillow and macOS system fonts (2x, LANCZOS, 240 colours);
`main.ts` checks the PNG limits and copies `entry.png` to `/output`. Every story's sources
are in `FACTS.md`.

## Run it

```sh
node main.ts            # writes /output/entry.png (set MAKEFUN_OUTPUT_DIR to change)
python3 render.py       # optional: redraw entry.png (macOS fonts, Pillow)
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=z1s7h5w8&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
