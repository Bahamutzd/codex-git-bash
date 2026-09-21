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
D:\nodejs\node_global\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe
```

Do not replace the similarly named executable under a VS Code extension directory. An npm reinstall or upgrade can overwrite this custom binary.
