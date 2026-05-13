import os
import re
import sys
import glob
import subprocess
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    encoding_path = sys.argv[1]
    encoding_name = os.path.basename(encoding_path).replace(".lp", "")

    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"

    instances = sorted(glob.glob("instances/**/*.lp", recursive=True))
    print(f"Running {len(instances)} instances with {encoding_name}...\n")

    results = []

    for inst in instances:
        print(f"=== {inst} ===")
        proc = subprocess.run(
            [sys.executable, "demo.py", inst, encoding_path],
            env=env, capture_output=True, text=True,
        )
        print(proc.stdout)

        out = proc.stdout
        sat = re.search(r"Result:\s*(\w+)", out)
        gt = re.search(r"Grounding:\s*([\d.]+)ms", out)
        st = re.search(r"Solving:\s*([\d.]+)ms", out)
        atoms = re.search(r"Atoms in model:\s*(\d+)", out)

        results.append((
            inst,
            sat.group(1) if sat else "?",
            float(gt.group(1)) if gt else None,
            float(st.group(1)) if st else None,
            int(atoms.group(1)) if atoms else None,
        ))

    # Summary table
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"{'Instance':<40} {'Result':<14} {'Ground (ms)':>12} {'Solve (ms)':>12}")
    print("-" * 80)
    for inst, res, gt, st, _ in results:
        gt_s = f"{gt:>12.1f}" if gt is not None else f"{'-':>12}"
        st_s = f"{st:>12.1f}" if st is not None else f"{'-':>12}"
        print(f"{inst:<40} {res:<14} {gt_s} {st_s}")

    plot_summary(results, encoding_name)


def plot_summary(results, encoding_name):
    by_size = defaultdict(lambda: {"ground": [], "solve": []})
    for inst, _, gt, st, _ in results:
        if gt is None or st is None:
            continue
        parts = inst.replace("\\", "/").split("/")
        if len(parts) >= 2 and "x" in parts[1]:
            size = parts[1]
            by_size[size]["ground"].append(gt)
            by_size[size]["solve"].append(st)

    if not by_size:
        print("\nNo data to plot.")
        return

    sizes = sorted(by_size.keys(), key=lambda s: int(s.split("x")[0]))
    ground_means = [sum(by_size[s]["ground"]) / len(by_size[s]["ground"]) for s in sizes]
    solve_means = [sum(by_size[s]["solve"]) / len(by_size[s]["solve"]) for s in sizes]

    fig, ax = plt.subplots(figsize=(10, 6))

    floor = 0.01
    solve_bottoms = [floor + g for g in ground_means]

    bars_g = ax.bar(sizes, ground_means, bottom=floor,
                    label="Grounding", color="#4C72B0")
    bars_s = ax.bar(sizes, solve_means, bottom=solve_bottoms,
                    label="Solving", color="#DD8452")

    ax.set_yscale("log")
    ax.set_ylim(bottom=floor)

    for bar, val in zip(bars_g, ground_means):
        ax.text(bar.get_x() + bar.get_width() / 2, floor + val,
                f"g={val:.1f}", ha="center", va="bottom", fontsize=9,
                color="#4C72B0")
    for bar, val, base in zip(bars_s, solve_means, solve_bottoms):
        ax.text(bar.get_x() + bar.get_width() / 2, base + val,
                f"s={val:.1f}", ha="center", va="bottom", fontsize=9,
                color="#DD8452")

    ax.set_xlabel("Grid size")
    ax.set_ylabel("Mean time (ms, log scale)")
    ax.set_title(f"Mean grounding + solving time per puzzle size ({encoding_name})")
    ax.legend(loc="upper left")
    ax.margins(y=0.2)
    fig.tight_layout()

    out_path = os.path.join("output_images", f"summary_runtime_{encoding_name}.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nSummary plot saved to {out_path}")


if __name__ == "__main__":
    main()
