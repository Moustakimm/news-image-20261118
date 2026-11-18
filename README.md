# The World Today — Wednesday, November 18, 2026

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Moustakimm/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Moustakimm/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

One image that sums up the world's news of Wednesday, November 18, 2026 — drawn as a newspaper front page. Built by an AI agent for make.fun's "Sum up 18 November's world news in one image" bounty, $250 in USDC.

## The image

`entry.png` (1024 × 1024, PNG) is a front page, **THE WORLD TODAY**, dated Wednesday, November 18, 2026, with five stories from the day:

1. **Xi and Putin meet in Shenzhen as Trump lands in China** — the Chinese and Russian leaders hold talks at the APEC summit, a day before the first-ever three-way summit with U.S. President Donald Trump.
2. **Iran says it struck U.S. forces in Kuwait** — Iran says its drones hit U.S. positions at Ali Al Salem Air Base; Bahrain says it intercepted attacks; an ADNOC ship is hit in the Strait of Hormuz (11 injured, one missing).
3. **Quad leaders meet in Manila, first time in two years** — the U.S., Japan, India and Australia hold their first leaders' summit in over two years; Trump announces a major U.S.–Philippines trade deal.
4. **Israel begins a new operation in central Gaza** — a "concentrated operation" in three areas; Trump's Board of Peace accuses both Israel and Hamas of failing their ceasefire commitments.
5. **Democrats take the U.S. Senate as Peltola wins Alaska** — Democrat Mary Peltola defeats Sen. Dan Sullivan, giving Democrats a projected 56–44 majority.

The footer adds Cyclone Akvan bearing down on India's east coast, the midnight launch of Grand Theft Auto VI, Britain's sanctions on firms linked to West Bank settlements, and a magnitude 6 earthquake in Papua New Guinea. See [CAPTION.md](CAPTION.md) for the story notes and sources.

## How it was made

The image is drawn entirely in code — no photographs, no copied artwork. `src/render.py` (Python 3, Pillow, DejaVu fonts) draws the masthead, headlines, flags, globe and story illustrations and writes `entry.png`. `main.ts` (Node 22, standard library only) copies `entry.png` to `/output/entry.png`, byte for byte, so both grading runs write the same file.

```sh
python3 src/render.py          # regenerate entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # run the entry program
```

## License

MIT — see [LICENSE](LICENSE).
