# Codex Git Bash Build

This repository does not vendor the Codex source tree. The workflow downloads an official stable `rust-v*` tag, applies `patches/git-bash-default.patch`, builds the Windows x64 CLI, verifies the default shell, and uploads an artifact.

## GitHub setup

1. Create a GitHub repository and push this directory.
2. Run `Actions` -> `Build Latest Codex Git Bash` -> `Run workflow`.
3. Leave `ref` empty to build the newest stable `rust-v*` tag, or provide an exact tag.
4. Download the artifact only after the workflow succeeds.

The workflow fails instead of publishing when the upstream source no longer accepts the patch or the shell verification does not report `bash`.

## Local replacement

The artifact contains `codex.exe`, `artifact-metadata.txt`, and `SHA256SUMS.txt`. Verify the checksum and version before replacing:

```text
<npm root -g 的输出>\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe
```

在 Windows 上先运行 `npm.cmd root -g`，把输出替换到上面的占位符中。输出已经包含 `node_modules`，不要重复追加。用 `where.exe codex` 确认当前 CLI 入口属于同一套 npm 安装，并确认目标文件确实存在。该路径适用于上述嵌套平台包布局；若目录不存在，先检查实际安装结构，不要直接创建目录或覆盖其他文件。替换前退出正在运行的 CLI 并备份原文件。

Do not replace the similarly named executable under a VS Code extension directory. An npm reinstall or upgrade can overwrite this custom binary.
