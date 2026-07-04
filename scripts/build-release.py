#!/usr/bin/env python3
"""
B 站封面提取项目 - 打包脚本(跨平台,纯 Python)

打包产物:releases/<PROJECT_NAME>-v<VERSION>.zip
    完整包:含 backend + frontend + dist + 部署脚本(整体部署 / 后端改动时用)
    前端包:releases/<PROJECT_NAME>-frontend-v<VERSION>.zip
    只含 frontend/dist/ + VERSION(前端热更用,服务器端覆盖 dist/ 不重启)

包含内容(完整包):
  - backend/(源码 + scripts/,不含 node_modules / data / *.log)
  - frontend/(源码 + scripts/ + dist/ 已构建产物)
  - deploy.sh / start.sh / stop.sh(部署 / 启动 / 停止)
  - VERSION / LICENSE / README.md

参数:
  --skip-build      跳过前端构建(默认会跑 npm run build)
  --bump            自动 bump 版本号 patch +1
                    完整模式:backend / frontend / 根 package.json + VERSION 全改
                    frontend-only 模式:只改 frontend/package.json + VERSION
  --frontend-only   只打前端包(只含 dist/),不包含 backend,zip 名带 -frontend 后缀
                    配合 update-frontend.sh 实现"前端热更"(无需重启 Node)
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


def bump_version(target="all"):
    """patch +1。

    target='all'(完整包):
      backend / frontend / 根 package.json + VERSION 共四处一起 bump
    target='frontend'(只打前端包):
      只 bump frontend/package.json + VERSION,backend 不动
      —— 这样后端依赖不会因为前端小改动而触发 npm install
    """
    if target == "all":
        pkg_path = ROOT / "backend" / "package.json"
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
        parts = pkg["version"].split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        new_version = ".".join(parts)
        pkg["version"] = new_version
        pkg_path.write_text(
            json.dumps(pkg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"[bump] backend/package.json -> {new_version}")

        # 根 package.json 也跟着 backend
        root_pkg_path = ROOT / "package.json"
        root_pkg = json.loads(root_pkg_path.read_text(encoding="utf-8"))
        root_pkg["version"] = new_version
        root_pkg_path.write_text(
            json.dumps(root_pkg, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"[bump] package.json -> {new_version}")
    else:
        # frontend-only:从 frontend/package.json 读当前版本
        fe_pkg_path = ROOT / "frontend" / "package.json"
        fe_pkg = json.loads(fe_pkg_path.read_text(encoding="utf-8"))
        parts = fe_pkg["version"].split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        new_version = ".".join(parts)

    # frontend/package.json + VERSION —— 两种模式都要更新
    fe_pkg_path = ROOT / "frontend" / "package.json"
    fe_pkg = json.loads(fe_pkg_path.read_text(encoding="utf-8"))
    fe_pkg["version"] = new_version
    fe_pkg_path.write_text(
        json.dumps(fe_pkg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"[bump] frontend/package.json -> {new_version}")

    version_file = ROOT / "VERSION"
    version_file.write_text(new_version + "\n", encoding="utf-8")
    print(f"[bump] VERSION -> {new_version}")

    return new_version


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


def stage(version, mode="full"):
    """准备 staging 目录。

    mode='full'(默认):完整包,含 backend + frontend + 部署脚本
    mode='frontend':只装 frontend/dist/ + VERSION(前端热更包)
    """
    if mode == "frontend":
        print(f"[2/4] 准备 frontend-only staging(v{version})...")
    else:
        print(f"[2/4] 准备 staging(v{version})...")

    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)

    if mode == "frontend":
        # 只装 frontend/dist/,以及标记版本
        fe_dist = ROOT / "frontend" / "dist"
        if not (fe_dist / "index.html").exists():
            raise RuntimeError("frontend/dist/index.html 不存在,无法打包")
        shutil.copytree(fe_dist, STAGING / "frontend" / "dist")
        # 版本号(用来确认解压出来的是哪个版本)
        shutil.copy2(ROOT / "VERSION", STAGING / "VERSION")
        print("    ✓ frontend-only staging 完成(只含 dist/ + VERSION)")
        return

    # ---- 以下是完整包 ----

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

    # 顶层脚本 + 文档 + 宝塔入口
    for f in (
        "deploy.sh",
        "start.sh",
        "stop.sh",
        "server.js",
        "package.json",
        "package-lock.json",
        "VERSION",
        "LICENSE",
        "README.md",
    ):
        src = ROOT / f
        if src.exists():
            shutil.copy2(src, STAGING / f)

    print("    ✓ staging 完成")


def zip_release(version, mode="full"):
    if mode == "frontend":
        suffix = "-frontend"
    else:
        suffix = ""
    print(f"[3/4] 打包 -> releases/{PROJECT_NAME}{suffix}-v{version}.zip")
    RELEASES.mkdir(exist_ok=True)
    zip_path = RELEASES / f"{PROJECT_NAME}{suffix}-v{version}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(STAGING):
            for f in files:
                fp = Path(root) / f
                arcname = fp.relative_to(STAGING).as_posix()
                z.write(fp, arcname)
    size_kb = zip_path.stat().st_size / 1024
    print(f"    ✓ {zip_path.name}  ({size_kb:.1f} KB)")


def cleanup_old(keep=3, mode="full"):
    print(f"[4/4] 清理旧产物(保留最近 {keep} 个)...")
    pattern = (
        f"{PROJECT_NAME}-frontend-v*.zip"
        if mode == "frontend"
        else f"{PROJECT_NAME}-v*.zip"
    )
    zips = sorted(
        RELEASES.glob(pattern),
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
    frontend_only = "--frontend-only" in args
    mode = "frontend" if frontend_only else "full"

    if bump:
        version = bump_version(target="frontend" if frontend_only else "all")
    else:
        # frontend-only 模式从 frontend/package.json 读,完整模式从 backend 读
        pkg_rel = "frontend" if frontend_only else "backend"
        pkg_path = ROOT / pkg_rel / "package.json"
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
        version = pkg["version"]
        print(f"[info] 当前版本 v{version}(来自 {pkg_rel}/package.json, mode={mode})")

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
        stage(version, mode=mode)
        zip_release(version, mode=mode)
        cleanup_old(mode=mode)
    finally:
        # 兜底:即使中途出错,也清理 staging
        if STAGING.exists():
            shutil.rmtree(STAGING)

    suffix = "-frontend" if frontend_only else ""
    print(f"\n[done] 产物:releases/{PROJECT_NAME}{suffix}-v{version}.zip")
    if frontend_only:
        print("[next] 上传到服务器,跑 bash update-frontend.sh <zip>")
        print("       会覆盖 frontend/dist/,无需重启 Node,刷新浏览器即可")
    else:
        print("[next] 上传到服务器,解压后跑 bash deploy.sh")


if __name__ == "__main__":
    main()