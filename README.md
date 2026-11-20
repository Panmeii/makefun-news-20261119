# makefun-news-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Panmeii/makefun-news-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Panmeii/makefun-news-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

**The World on 19 November 2026** — one 1024×1024 front-page image summing up the world news of Thursday 19 November 2026 in forty verified stories: the World Court's ruling that Myanmar committed genocide against the Rohingya; Trump, Xi and Putin issuing a joint "peace declaration" after their Shenzhen trilateral summit; Anthropic's record $81.3bn IPO and first-day surge; Denmark's approval of the Greenland–US Arctic security pact; Russian missiles hitting three Kyiv bridges; Severe Cyclone Akvan bearing down on Odisha; the worldwide midnight launch of Grand Theft Auto VI; and twenty-eight further one-line briefs across seven regions. The image (`entry.png`) is drawn with a Python PIL script (`build_image.py`, a dense newspaper-style layout with illustrated lead panels, a pinned world map, stat boxes and a date-check box); `main.ts` copies it to the output directory and verifies the delivered PNG chunk by chunk, CRC-32 included.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=8nt1dqan&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
