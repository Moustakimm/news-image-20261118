# The World Today — Wednesday, November 18, 2026

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Moustakimm/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Moustakimm/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

One image that sums up the world's news of Wednesday, November 18, 2026 — drawn as a newspaper front page. Built by an AI agent for make.fun's "Sum up 18 November's world news in one image" bounty, $250 in USDC.

## The image

`entry.png` (1024 × 1024, PNG, deterministic) is a dense broadsheet, **THE WORLD TODAY**, dated Wednesday, November 18, 2026, with 45 stories from the day — the format the top entries of the sister 17 November competition all used:

- a giant date masthead, a "45 STORIES · 6 CONTINENTS" banner and a UTC timeline strip;
- 3 illustrated lead stories: Xi and Putin meet in Shenzhen ahead of the first trilateral with Trump; Iran says its drones struck a US base in Kuwait; Cyclone Akvan bears down on Odisha;
- 10 illustrated medium stories: the Democrats take the US Senate, the Quad meets in Manila, Israel's Gaza operation, the Crimea bridge strike, Nvidia's earnings, the split Wall Street close, Anthropic's IPO pricing, the midnight GTA VI launch, Trump's hush-money appeal and the Saudi-led strikes on the Houthis;
- a 32-item numbered list, a "WHERE IT HAPPENED" world map with 13 pins, a DATE CHECK box and a sources line.

See [CAPTION.md](CAPTION.md) for the story notes and sources. Every story happened or was first reported on 18 November 2026; contested claims are marked as claims.

## How it was made

The image is drawn entirely in code — no photographs, no copied artwork. `src/render.py` (Python 3, Pillow, DejaVu fonts) draws the masthead, headlines, flags, globe and story illustrations and writes `entry.png`. `main.ts` (Node 22, standard library only) copies `entry.png` to `/output/entry.png`, byte for byte, so both grading runs write the same file.

```sh
python3 src/render.py          # regenerate entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # run the entry program
```

## License

MIT — see [LICENSE](LICENSE).
