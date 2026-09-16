# walk_v1 — 第一个行走策略

| 项 | 值 |
|---|---|
| 日期 | 2026-09-08 |
| 任务 | `Mjlab-Velocity-Flat-MicroDuck` |
| 代码 | 上游 `pollen-robotics/microduck_rl@2b581c6`，无本地改动（见 `git_snapshot.txt`） |
| 硬件 | 1 × NVIDIA RTX PRO 4000 Blackwell（24 GB） |
| 规模 | 4096 环境 × 24 步/轮 × 5000 轮 ≈ 4.9 亿步 |
| 用时 | 1 小时 52 分 04 秒 |
| 吞吐 | 6.7 万–7.4 万 步/秒（采集 1.36 s + 学习 0.084 s / 轮） |

## 复现

```bash
git checkout 2b581c6
CUDA_VISIBLE_DEVICES=<gpu> uv run train Mjlab-Velocity-Flat-MicroDuck \
    --env.scene.num-envs 4096 \
    --agent.max-iterations 5000 \
    --agent.logger tensorboard \
    --agent.run-name walk_v1
```

训练之前先跑过冒烟测试（`--env.scene.num-envs 64 --agent.max-iterations 5`）。完整配置在 `params/agent.yaml` 和 `params/env.yaml`。

主要超参：actor/critic 都是 MLP 512-256-128 + ELU，观测归一化；PPO clip 0.2，γ 0.99，λ 0.95，5 epoch × 4 minibatch，初始学习率 1e-3，按 KL 自适应（目标 0.01），熵系数 0.01。

## 结果（第 5000 轮）

| 指标 | 值 |
|---|---|
| 平均回合得分 | 119.6 |
| 平均回合长度 | 966 / 1000 步 |
| 回合结束方式 | 活满时长 3.25 : 摔倒 0.25（约 93% 活满） |
| 动作标准差 σ | 1.0 → 0.177 |
| NaN 终止 | 0（全程） |
| 直行速度误差 | 0.435 m/s |
| 转向速度误差 | 1.042 rad/s |

各奖励项的最终得分（每秒）：

| 给分 | | 扣分 | |
|---|---|---|---|
| upright | +1.788 | action_rate_l2 | −0.948 |
| head_pose_tracking | +1.745 | head_pose_bias | −0.243 |
| track_linear_velocity | +1.317 | body_ang_vel | −0.025 |
| air_time | +1.045 | foot_clearance | −0.005 |
| track_angular_velocity | +0.829 | dof_pos_limits | −0.005 |
| pose | +0.574 | 其余 | 绝对值 < 0.003 |

导出的 ONNX 通过了三项检查：输入输出形状 `[1,61] → [1,14]`、无 NaN/Inf、输出不是常量。

## 观察

- 学会"不摔倒"非常快：第 110 轮（开训后约 2.5 分钟）平均回合长度就到了 800 步。
- 第 750–2000 轮得分出现平台和小幅回落，时间上和课程加码重合（抖动惩罚从 −0.1 升到 −1.0、头部指令范围放到最大、站立环境占比升到 25%）。不是训练发散。
- 转向是短板：转向误差是直行误差的两倍多，而且波动大。这是后续实验的切入点。

## 文件

| 文件 | 说明 |
|---|---|
| `policy.onnx` | 导出的策略，观测归一化已经内嵌在计算图里 |
| `gait.mp4` | 用 `model_4999.pt` 回放的 10 秒视频（960×720，50 fps） |
| `metrics.json` | 37 条训练曲线的降采样数据（`lab/tools/extract_tb.py` 生成） |
| `params/` | 训练时的完整 agent 和 env 配置 |
| `git_snapshot.txt` | rsl_rl 在训练开始时记下的 commit 和工作区状态 |

不在 git 里的：21 个 checkpoint（约 100 MB）、原始 tensorboard 事件文件（14 MB）和训练日志。它们还在训练机的 `logs/rsl_rl/velocity/2026-09-08_15-13-23_walk_v1/` 下。
