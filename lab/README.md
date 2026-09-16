# lab

我用 [microduck_rl](https://github.com/pollen-robotics/microduck_rl) 学强化学习的实验记录。上游代码原样保留，我自己的东西都放在这个目录里。

## 目录

| 路径 | 内容 |
|---|---|
| [`runs/`](runs/) | 每次训练一个子目录：命令、配置、结果、导出的策略、视频 |
| [`lecture/`](lecture/) | 交互式讲义《一只鸭子如何学会走路》及其源码 |
| [`tools/`](tools/) | 分析和渲染脚本；`tools/env/` 是装机后的 GPU 和 Warp 自检 |

## 实验索引

| run | 任务 | 代码 | 关键结果 | 结论 |
|---|---|---|---|---|
| [2026-09-08_walk_v1](runs/2026-09-08_walk_v1/) | Velocity-Flat | 上游 `2b581c6` | 得分 119.6，约 93% 回合活满，转向误差 1.04 rad/s | 基线跑通；转向是短板 |

## 分支

| 分支 | 用途 |
|---|---|
| `develop` | 上游 `develop` 的纯镜像，不在上面提交 |
| `lab` | 上游 `develop` + `lab/` 目录，默认分支 |
| `exp/<名字>` | 需要改代码的实验，从 `lab` 分出；结论整理后写回 `lab` 的 `runs/` |

工作分支刻意不叫 `main`：上游也有一个 `main`（旧的发布点），同名分支在 GitHub 上点 "Sync fork" 会去合并它。

同步上游：

```bash
git fetch upstream
git push origin upstream/develop:develop   # 更新镜像
git switch lab && git merge upstream/develop
```

上游不会动 `lab/`，所以合并一般不会冲突。

## 约定

- run 目录命名为 `YYYY-MM-DD_<run-name>`，里面必须有 `README.md` 写清命令、代码版本和结论。
- 进 git 的产物：ONNX、短视频、降采样曲线（`tools/extract_tb.py`）、`params/`。
- 不进 git 的：checkpoint（`*.pt`）、原始 tensorboard 事件文件、完整训练日志。
- 长时间训练前先跑冒烟测试：`--env.scene.num-envs 64 --agent.max-iterations 5`。
