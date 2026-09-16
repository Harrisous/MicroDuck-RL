"""GPU 吞吐自检：bf16 下 8192×8192 矩阵乘，报 ms/iter 和 TFLOP/s。

用法：CUDA_VISIBLE_DEVICES=<gpu> uv run python lab/tools/env/gpubench.py
"""
import torch, time
d = torch.device("cuda:0")
print("device:", torch.cuda.get_device_name(0))
free, total = torch.cuda.mem_get_info()
print(f"mem free {free/2**30:.1f} GiB / total {total/2**30:.1f} GiB")
n = 8192
a = torch.randn(n, n, device=d, dtype=torch.bfloat16)
b = torch.randn(n, n, device=d, dtype=torch.bfloat16)
for _ in range(5): c = a @ b
torch.cuda.synchronize()
t0 = time.time()
iters = 50
for _ in range(iters): c = a @ b
torch.cuda.synchronize()
dt = time.time() - t0
tflops = 2 * n**3 * iters / dt / 1e12
print(f"bf16 matmul {n}^3: {dt/iters*1000:.2f} ms/iter -> {tflops:.1f} TFLOP/s")
