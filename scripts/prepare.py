"""读取上游工具链，仅修正工作区本地包的锁文件版本。"""
import os
from pathlib import Path
import re
import tomllib

root = Path("upstream-codex/codex-rs")
workspace = tomllib.loads((root / "Cargo.toml").read_text(encoding="utf-8"))
version = workspace["workspace"]["package"]["version"]
packages = {}
for member in workspace["workspace"]["members"]:
    for manifest in root.glob(f"{member}/Cargo.toml"):
        package = tomllib.loads(manifest.read_text(encoding="utf-8")).get("package", {})
        if package.get("version") == {"workspace": True}:
            packages[package["name"]] = version
lock = root / "Cargo.lock"
text = lock.read_text(encoding="utf-8")
blocks = text.split("[[package]]")
for i, block in enumerate(blocks[1:], 1):
    data = tomllib.loads(block)
    if "source" not in data and data["name"] in packages:
        blocks[i] = re.sub(r'^version = "[^"]+"$', f'version = "{packages[data["name"]]}"', block, count=1, flags=re.M)
lock.write_text("[[package]]".join(blocks), encoding="utf-8")
toolchain = tomllib.loads((root / "rust-toolchain.toml").read_text(encoding="utf-8"))["toolchain"]["channel"]
with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
    print(f"toolchain={toolchain}", file=output)
