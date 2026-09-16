#!/usr/bin/env bash
# 把 src/ 下的分片和训练曲线数据拼成单文件讲义：lab/lecture/dist/duck-rl.html
set -euo pipefail
cd "$(dirname "$0")"
DATA=${1:-../runs/2026-09-08_walk_v1/metrics.json}
mkdir -p dist
OUT=dist/duck-rl.html
cat src/part1.html src/part2.html src/part3.html src/part4.html src/part5.html src/part6.html > "$OUT"
printf '<script>const TB=' >> "$OUT"
cat "$DATA" >> "$OUT"
printf ';</script>\n' >> "$OUT"
cat src/part7.html >> "$OUT"
echo "built $OUT ($(wc -c < "$OUT") bytes)"
