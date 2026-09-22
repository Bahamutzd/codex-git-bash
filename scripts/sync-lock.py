"""保留官方第三方依赖，仅允许 Cargo 同步本地工作区锁文件。"""
from pathlib import Path
import subprocess
import tomllib


def external_packages(text):
    return {
        (p["name"], p["version"], p["source"], p.get("checksum"))
        for p in tomllib.loads(text)["package"]
        if "source" in p
    }


def main():
    root = Path("upstream-codex/codex-rs")
    original = subprocess.check_output(
        ["git", "show", "HEAD:codex-rs/Cargo.lock"], cwd=root
    ).decode("utf-8")
    toolchain = tomllib.loads((root / "rust-toolchain.toml").read_text())["toolchain"]["channel"]
    subprocess.run(
        ["cargo", f"+{toolchain}", "metadata", "--format-version", "1"],
        cwd=root, stdout=subprocess.DEVNULL, check=True,
    )
    expected = external_packages(original)
    actual = external_packages((root / "Cargo.lock").read_text(encoding="utf-8"))
    if expected != actual:
        for package in sorted(expected - actual):
            print("Removed:", package)
        for package in sorted(actual - expected):
            print("Added:", package)
        raise SystemExit("Third-party lockfile drift detected; refusing to build")
    print(f"Verified {len(expected)} upstream third-party package locks")


if __name__ == "__main__":
    main()
