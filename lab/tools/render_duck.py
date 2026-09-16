"""离屏渲染 microduck 的站立姿态，并算出传感器/关节在画面上的像素坐标。

用法（无显示器的机器需要 EGL）：
    MUJOCO_GL=egl uv run python lab/tools/render_duck.py --out lab/lecture/assets [--debug]

输出：
    beauty.jpg   普通视角（隐藏碰撞几何体）
    xray.jpg     透视视角：外壳半透明 + 关节转轴箭头
    coords.json  imu / head_imu / 双脚 / 14 个关节在 1280x960 画面上的 [u, v]
    *_debug.png  （--debug）把 coords 标在图上，用来核对投影
"""
import argparse
import json
import math
import os

import mujoco
import numpy as np
from PIL import Image

W, H = 1280, 960
# 相机参数与 coords.json 的投影必须一致
AZIMUTH, ELEVATION, DISTANCE = 140.0, -13.0, 0.52
COLLISION_GROUP = 3  # scene_walk.xml 里碰撞网格所在的 geom group


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", default="src/mjlab_microduck/robot/microduck/scene_walk.xml")
    ap.add_argument("--keyframe", default="STAND")
    ap.add_argument("--out", default="lab/lecture/assets")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    model = mujoco.MjModel.from_xml_path(args.scene)
    model.vis.global_.offwidth, model.vis.global_.offheight = W, H
    model.vis.scale.jointlength *= 2.4
    model.vis.scale.jointwidth *= 1.6
    data = mujoco.MjData(model)
    mujoco.mj_resetDataKeyframe(model, data, mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, args.keyframe))
    mujoco.mj_forward(model, data)

    trunk = data.body("trunk_base").xpos
    lookat = np.array([trunk[0], trunk[1], trunk[2] + 0.015])

    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.azimuth, cam.elevation, cam.distance = AZIMUTH, ELEVATION, DISTANCE
    cam.lookat[:] = lookat

    # 兴趣点：IMU、脚底、14 个铰链关节（顺序即观测/动作里的关节顺序）
    points = {n: data.site(n).xpos.copy() for n in ("imu", "head_imu", "left_foot", "right_foot")}
    for j in range(model.njnt):
        if model.jnt_type[j] == mujoco.mjtJoint.mjJNT_HINGE:
            points[mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, j)] = data.xanchor[j].copy()

    # 针孔投影，和 MuJoCo 自由相机的约定一致
    az, el = math.radians(AZIMUTH), math.radians(ELEVATION)
    fwd = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    pos = lookat - DISTANCE * fwd
    right = np.cross(fwd, [0, 0, 1])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    f = (H / 2) / math.tan(math.radians(float(model.vis.global_.fovy)) / 2)
    coords = {}
    for name, p in points.items():
        q = p - pos
        coords[name] = [round(W / 2 + (q @ right) / (q @ fwd) * f, 1), round(H / 2 - (q @ up) / (q @ fwd) * f, 1)]
    with open(os.path.join(args.out, "coords.json"), "w") as fh:
        json.dump(coords, fh, indent=1)

    renderer = mujoco.Renderer(model, height=H, width=W)
    opt = mujoco.MjvOption()
    opt.geomgroup[COLLISION_GROUP] = 0
    views = {"beauty": {}, "xray": {mujoco.mjtVisFlag.mjVIS_JOINT: True, mujoco.mjtVisFlag.mjVIS_TRANSPARENT: True}}
    for name, flags in views.items():
        for flag, val in flags.items():
            opt.flags[flag] = val
        renderer.update_scene(data, camera=cam, scene_option=opt)
        Image.fromarray(renderer.render()).convert("RGB").save(os.path.join(args.out, f"{name}.jpg"), quality=86)

    if args.debug:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        for name in views:
            fig, ax = plt.subplots(figsize=(W / 100, H / 100), dpi=100)
            ax.imshow(Image.open(os.path.join(args.out, f"{name}.jpg")))
            ax.axis("off")
            for k, (u, v) in coords.items():
                ax.plot(u, v, "o", ms=7, mfc="none", mec="red", mew=2)
                ax.annotate(k, (u, v), xytext=(4, -4), textcoords="offset points", fontsize=7, color="red")
            fig.savefig(os.path.join(args.out, f"{name}_debug.png"), bbox_inches="tight", pad_inches=0)
            plt.close(fig)
    print(f"wrote beauty.jpg, xray.jpg, coords.json -> {args.out}")


if __name__ == "__main__":
    main()
