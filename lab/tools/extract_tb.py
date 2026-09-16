"""把一个 rsl_rl run 的 tensorboard 事件文件降采样成小 JSON（讲义与 run 记录用）。

用法：
    uv run python lab/tools/extract_tb.py <run_dir> <out.json> [--buckets 250]

输出格式：{tag: [[iteration, value], ...]}，每条曲线按桶取均值，数值保留 4 位有效数字。
"""
import argparse
import glob
import json
import math
import os

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

DEFAULT_TAGS = [
    "Train/mean_reward", "Train/mean_episode_length",
    "Loss/surrogate", "Loss/value", "Loss/entropy", "Loss/learning_rate",
    "Policy/mean_std", "Perf/total_fps", "Perf/collection_time", "Perf/learning_time",
    "Metrics/twist/error_vel_xy", "Metrics/twist/error_vel_yaw",
    "Episode_Termination/fell_over", "Episode_Termination/time_out",
]
PREFIXES = ("Episode_Reward/", "Curriculum/")


def sig4(x):
    if x == 0 or not math.isfinite(x):
        return 0.0
    return float(f"{x:.4g}")


def bucket(pairs, nb):
    if len(pairs) <= nb:
        return [[int(s), sig4(v)] for s, v in pairs]
    out, size = [], len(pairs) / nb
    for i in range(nb):
        chunk = pairs[int(i * size):int((i + 1) * size)]
        if chunk:
            out.append([int(chunk[len(chunk) // 2][0]), sig4(sum(v for _, v in chunk) / len(chunk))])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("out")
    ap.add_argument("--buckets", type=int, default=250)
    args = ap.parse_args()

    files = glob.glob(os.path.join(args.run_dir, "events.out.tfevents.*"))
    if not files:
        raise SystemExit(f"no tfevents file in {args.run_dir}")
    ea = EventAccumulator(files[0], size_guidance={"scalars": 0})
    ea.Reload()
    have = ea.Tags()["scalars"]
    tags = sorted({t for t in DEFAULT_TAGS if t in have} | {t for t in have if t.startswith(PREFIXES)})

    data = {t: bucket([(e.step, e.value) for e in ea.Scalars(t)], args.buckets) for t in tags}
    with open(args.out, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    print(f"{len(data)} series -> {args.out} ({os.path.getsize(args.out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
