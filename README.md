# Nurikabe ASP Demo

Comparing two ASP encodings of Nurikabe puzzles using clingo. The goal is to show how encoding choices affect grounding and solving time across instances of different sizes.

## Steps to run

1. Clone the repo to local.

2. ```bash
   pip install -r requirements.txt
   ```
Then run the following for single instance, or use the command for all instances as given below.

## Run a single instance

```bash
python demo.py instances/6x6/instance1.lp encoding/nurikabe_01.lp
python demo.py instances/6x6/instance1.lp encoding/nurikabe_02.lp
```

The solver prints timing stats and clingo's internal stats in terminal, and saves the rendered grid to `output_images/<encoding>/<size>/<instance>.png`.

## Run all instances for one encoding

```bash
python run_all.py encoding/nurikabe_01.lp
python run_all.py encoding/nurikabe_02.lp
```

Each run saves per-instance PNGs under `output_images/<encoding>/` and a summary bar chart to `output_images/summary_runtime_<encoding>.png`.

## Encodings

In `encoding/`:

- `nurikabe_01.lp` — derived from [Honu08/Nurikabe](https://github.com/Honu08/Nurikabe) (Texas Tech, Omar Rodriguez Santiago / Dr. Richard Watson).
- `nurikabe_02.lp` — same logic as `nurikabe_01.lp` but fake inefficiencies introduced. For example:
  - adds a redundant `pair/4` predicate which enumerates more combinations
  - remoeved explicit check done for overlapping clue cells in same region. This is then passively caught when
    checking that clue number matches the island size.

## Instances

Source from [janko.at/Raetsel/Nurikabe](https://www.janko.at/Raetsel/Nurikabe/), grouped by size in `instances/`:

- `6x6/`, `8x8/`, `10x10/`, `12x12/`, `15x15/` — 10 puzzles each
- `*/instance4.lp` are in all cases unsatisfiable.

## AI assistance

AI assisstance was used in helping to derive and adapt the ASP encoding from the Honu08 repository and adjusting matplotlib renderings.

## References

- Honu08/Nurikabe: https://github.com/Honu08/Nurikabe
- Janko.at puzzles: https://www.janko.at/Raetsel/Nurikabe/
