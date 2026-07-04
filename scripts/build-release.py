#!/usr/bin/env python3
"""
B 站封面提取项目 - 打包脚本(跨平台,纯 Python)

打包产物:releases/<PROJECT_NAME>-v<VERSION>.zip

包含内容:
  - backend/(源码 + scripts/,不含 node_modules / data / *.log)
  - frontend/(源码 + scripts/ + dist/ 已构建产物)
  - deploy.sh / start.sh / stop.sh(部署 / 启动 / 停止)
  - VERSION / LICENSE / README.md

参数:
  --skip-build    跳过前端构建(默认会跑 npm run build)
  --bump          自动 bump 版本号 patch +1(只改 backend/package.json)
                  记得手动同步 frontend/package.json 和 VERSION
"""
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

PROJECT_NAME = "blibilicover"
ROOT = Path(__file__).resolve().parent.parent
RELEASES = ROOT / "releases"
STAGING = RELEASES / ".staging"


def get_version():
    pkg_path = ROOT / "backend" / "package.json"
    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    return pkg["version"]


def bump_version():
    """patch +1,只改 backend/package.json。提示用户同步 frontend + VERSION。"""
    pkg_path = ROOT / "backend" / "package.json"
    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    parts = pkg["version"].split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    pkg["version"] = ".".join(parts)
    pkg_path.write_text(
        json.dumps(pkg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"[bump] backend/package.json -> {pkg['version']}")
    print(f"[!] 记得手动同步 frontend/package.json 和 VERSION 改成 {pkg['version']}")
    return pkg["version"]


def build_frontend():
    """npm install(若需要)+ npm run build,产物到 frontend/dist/。"""
    print("[1/4] 构建前端...")
    fe = ROOT / "frontend"
    if not (fe / "node_modules" / ".package-lock.json").exists():
        print("    - 装前端依赖(可能耗时 1-2 分钟)")
        subprocess.run(["npm", "install"], cwd=fe, check=True, shell=True)
    subprocess.run(["npm", "run", "build"], cwd=fe, check=True, shell=True)
    if not (fe / "dist" / "index.html").exists():
        raise RuntimeError("前端构建失败,dist/index.html 不存在")
    print("    ✓ dist/ 已生成")


def stage(version):
    print(f"[2/4] 准备 staging(v{version})...")
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)

    # backend:源码 + scripts,排除 node_modules / data / 日志
    shutil.copytree(
        ROOT / "backend",
        STAGING / "backend",
        ignore=shutil.ignore_patterns(
            "node_modules", "data", "*.log", ".env*", "coverage", "*.log"
        ),
    )

    # frontend:src + 配置 + 已构建的 dist
    fe = STAGING / "frontend"
    fe.mkdir()
    for item in (
        "src",
        "index.html",
        "package.json",
        "package-lock.json",
        "vite.config.js",
        ".gitignore",
        "README.md",
        "scripts",
        "dist",
    ):
        src = ROOT / "frontend" / item
        if not src.exists():
            continue
        if src.is_dir():
            shutil.copytree(
                src, fe / item, ignore=shutil.ignore_patterns("node_modules")
            )
        else:
            shutil.copy2(src, fe / item)

    # 顶层脚本 + 文档
    for f in ("deploy.sh", "start.sh", "stop.sh", "VERSION", "LICENSE", "README.md"):
        src = ROOT / f
        if src.exists():
            shutil.copy2(src, STAGING / f)

    print("    ✓ staging 完成")


def zip_release(version):
    print(f"[3/4] 打包 -> releases/{PROJECT_NAME}-v{version}.zip")
    RELEASES.mkdir(exist_ok=True)
    zip_path = RELEASES / f"{PROJECT_NAME}-v{version}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(STAGING):
            for f in files:
                fp = Path(root) / f
                arcname = fp.relative_to(STAGING).as_posix()
                z.write(fp, arcname)
    size_mb = zip_path.stat().st_size / 1024 / 1024
    print(f"    ✓ {zip_path.name}  ({size_mb:.2f} MB)")


def cleanup_old(keep=3):
    print(f"[4/4] 清理旧产物(保留最近 {keep} 个)...")
    zips = sorted(
        RELEASES.glob(f"{PROJECT_NAME}-v*.zip"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for old in zips[keep:]:
        old.unlink()
        print(f"    - 删 {old.name}")
    if STAGING.exists():
        shutil.rmtree(STAGING)


def main():
    args = sys.argv[1:]
    skip_build = "--skip-build" in args
    bump = "--bump" in args

    if bump:
        version = bump_version()
    else:
        version = get_version()
        print(f"[info] 当前版本 v{version}(来自 backend/package.json)")

    if not skip_build:
        try:
            build_frontend()
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] 前端构建失败: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("[skip] 跳过前端构建(--skip-build)")
        if not (ROOT / "frontend" / "dist" / "index.html").exists():
            print("[ERROR] frontend/dist/index.html 不存在,无法跳过构建",
                  file=sys.stderr)
            sys.exit(1)

    try:
        stage(version)
        zip_release(version)
        cleanup_old()
    finally:
        # 兜底:即使中途出错,也清理 staging
        if STAGING.exists():
            shutil.rmtree(STAGING)

    print(f"\n[done] 产物:releases/{PROJECT_NAME}-v{version}.zip")
    print("[next] 上传到服务器,解压后跑 bash deploy.sh")


if __name__ == "__main__":
    main()