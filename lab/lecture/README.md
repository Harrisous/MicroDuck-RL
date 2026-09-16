# 讲义：一只鸭子如何学会走路

以 [`runs/2026-09-08_walk_v1`](../runs/2026-09-08_walk_v1/) 这次真实训练为标本，分 12 章讲 PPO、奖励设计、课程学习和 sim-to-real。单个 HTML 文件，离线可开，交互图表的数据全部内嵌。

| 文件 | 说明 |
|---|---|
| `duck-rl.html` | 已发布的版本，浏览器直接打开 |
| `src/part1–7.html` | 源码分片：1 样式，2–6 正文，7 交互脚本 |
| `build.sh` | 把分片和曲线数据拼成 `dist/duck-rl.html` |
| `assets/` | `tools/render_duck.py` 渲染出的站立姿态图和传感器像素坐标 |

## 构建

```bash
lab/lecture/build.sh                       # 默认用 walk_v1 的曲线
lab/lecture/build.sh path/to/metrics.json  # 换一次训练的数据
```

曲线数据由 `lab/tools/extract_tb.py` 从 tensorboard 事件文件生成。

## 进行中

第 2 章"61 维观测"图的升级做了一半：点某一段观测时，在渲染图上高亮它来自身体的哪个部位（关节段切换到透视图并标出编号）。

- 已完成：`src/part1.html` 里的样式、`src/part2.html` 里的页面结构、`assets/` 里的渲染图和坐标
- 未完成：`src/part7.html` 里的交互逻辑，以及把 `assets/` 的图片内嵌进页面

所以现在用 `build.sh` 构建出来的页面，第 2 章会有一块空白图位。已发布的 `duck-rl.html` 不含这项改动，内容完整。
