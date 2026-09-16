"""Warp / MuJoCo Warp / mjlab 自检：确认 Warp 能在当前显卡上 JIT 编译 kernel。

必须从文件运行（Warp 不接受 python -c 里定义的 kernel）。
用法：CUDA_VISIBLE_DEVICES=<gpu> uv run python lab/tools/env/warpcheck.py
"""
import warp as wp
wp.init()
d = wp.get_device("cuda:0")

@wp.kernel
def k(a: wp.array(dtype=float)):
    i = wp.tid()
    a[i] = a[i] * 2.0 + 1.0

a = wp.zeros(8, dtype=float, device=d)
wp.launch(k, dim=8, inputs=[a], device=d)
wp.synchronize()
print("JIT kernel ok ->", a.numpy()[:4])

import mujoco, mujoco_warp
print("mujoco", mujoco.__version__, "| mujoco_warp import ok")
import mjlab
print("mjlab ok")
