import sys
import re
import time
import os

import clingo
import numpy as np
import matplotlib.pyplot as plt


def parse_instance(path):
    text = open(path).read()
    rows = int(re.search(r"rows\((\d+)\)", text).group(1))
    cols = int(re.search(r"cols\((\d+)\)", text).group(1))
    clues = {}
    for m in re.finditer(r"clue\((\d+),\s*(\d+),\s*(\d+)\)", text):
        r, c, n = int(m.group(1)), int(m.group(2)), int(m.group(3))
        clues[(r, c)] = n
    return {"rows": rows, "cols": cols, "clues": clues}


def solve(encoding_path, instance_path):
    ctl = clingo.Control(["--warn=none"])
    ctl.load(encoding_path)
    ctl.load(instance_path)

    t0 = time.perf_counter()
    ctl.ground([("base", [])])
    t1 = time.perf_counter()
    ground_time = t1 - t0

    model_symbols = None

    def on_model(model):
        nonlocal model_symbols
        model_symbols = model.symbols(shown=True)

    timeout_seconds = 300.0
    t2 = time.perf_counter()
    with ctl.solve(on_model=on_model, async_=True) as handle:
        finished = handle.wait(timeout_seconds)
        if not finished:
            return {
                "model": None,
                "satisfiable": False,
                "timed_out": True,
                "ground_time": ground_time,
                "solve_time": timeout_seconds,
                "stats": ctl.statistics,
            }
        result = handle.get()
    t3 = time.perf_counter()
    solve_time = t3 - t2

    return {
        "model": model_symbols,
        "satisfiable": not result.unsatisfiable,
        "timed_out": False,
        "ground_time": ground_time,
        "solve_time": solve_time,
        "stats": ctl.statistics,
    }


def build_grid(model_symbols, rows, cols):
    grid = np.zeros((rows, cols), dtype=int)
    for sym in model_symbols:
        if sym.name == "black":
            r = sym.arguments[0].number
            c = sym.arguments[1].number
            grid[r - 1, c - 1] = 1
    return grid


def render(grid, clues, title, save_path):
    rows, cols = grid.shape
    fig_w = max(8, cols * 0.8 + 2)
    fig_h = max(6, rows * 0.8 + 2)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    ax.imshow(grid, cmap="gray_r", vmin=0, vmax=1)

    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which="minor", color="grey", linewidth=0.5)
    ax.tick_params(
        which="both", bottom=False, left=False, labelbottom=False, labelleft=False
    )

    for (r, c), n in clues.items():
        ax.text(
            c - 1, r - 1, str(n),
            ha="center", va="center",
            fontsize=14, color="black", fontweight="bold",
        )

    ax.set_title(title)
    ax.set_aspect("equal")

    fig.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def main():
    instance_path = sys.argv[1]
    encoding_path = sys.argv[2]

    instance_name = os.path.basename(instance_path).replace(".lp", "")
    encoding_name = os.path.basename(encoding_path).replace(".lp", "")

    print(f"Encoding: {encoding_name}")
    print(f"Instance: {instance_name}")

    info = parse_instance(instance_path)
    print(f"Grid: {info['rows']}x{info['cols']}")

    result = solve(encoding_path, instance_path)
    gt = result["ground_time"]
    st = result["solve_time"]

    if result["timed_out"]:
        result_label = "TIMEOUT"
    elif result["satisfiable"]:
        result_label = "SATISFIABLE"
    else:
        result_label = "UNSATISFIABLE"

    print(f"Result: {result_label}")
    print(f"Grounding: {gt*1000:.1f}ms")
    print(f"Solving: {st*1000:.1f}ms")
    if result["satisfiable"]:
        print(f"Atoms in model: {len(result['model'])}")

    try:
        stats = result["stats"]
        print(f"\n--- Clingo Statistics ---")
        print(f"Clingo total time: {stats['summary']['times']['total']*1000:.1f}ms")
        print(f"Clingo solve time: {stats['summary']['times']['solve']*1000:.1f}ms")
        print(f"Ground atoms: {int(stats['problem']['lp']['atoms'])}")
        print(f"Ground rules: {int(stats['problem']['lp']['rules'])}")
        print(f"Choices: {int(stats['solving']['solvers']['choices'])}")
        print(f"Conflicts: {int(stats['solving']['solvers']['conflicts'])}")
    except (KeyError, TypeError):
        pass

    if result["satisfiable"]:
        grid = build_grid(result["model"], info["rows"], info["cols"])
        title = (
            f"{instance_name} ({encoding_name}) | {info['rows']}x{info['cols']} | "
            f"grounding {gt*1000:.1f}ms | solving {st*1000:.1f}ms"
        )
    else:
        grid = np.zeros((info["rows"], info["cols"]), dtype=int)
        title = (
            f"{instance_name} ({encoding_name}) | {info['rows']}x{info['cols']} | {result_label} | "
            f"grounding {gt*1000:.1f}ms | solving {st*1000:.1f}ms"
        )

    rel_path = os.path.relpath(instance_path, "instances")
    save_path = os.path.join("output_images", encoding_name, rel_path.replace(".lp", ".png"))
    render(grid, info["clues"], title, save_path)


if __name__ == "__main__":
    main()
