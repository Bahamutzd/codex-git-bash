param(
    [Parameter(Mandatory = $true)][string]$Toolchain,
    [int]$IntervalSeconds = 60
)

$ErrorActionPreference = 'Stop'
if ($IntervalSeconds -lt 1) { throw 'IntervalSeconds must be positive' }
$log = Join-Path $env:GITHUB_WORKSPACE 'build-cli.log'
$diagnostics = Join-Path $env:GITHUB_WORKSPACE 'build-diagnostics.log'

# 独立线程直接输出到控制台，不等待 Cargo 输出或结束。
$monitor = Start-ThreadJob -StreamingHost $Host -ArgumentList $diagnostics, $IntervalSeconds -ScriptBlock {
    param($path, $interval)
    while ($true) {
        try {
            $lines = @("=== diagnostics $(Get-Date -Format o) ===")
            foreach ($group in @(
                @{ Title = 'rustc processes'; Names = @('rustc') },
                @{ Title = 'cargo'; Names = @('cargo') },
                @{ Title = 'native build processes'; Names = @('link', 'lld-link', 'cl', 'clang', 'cmake', 'ninja', 'build-script-build') }
            )) {
                $lines += "=== $($group.Title) ==="
                $processes = @(Get-Process -Name $group.Names -ErrorAction SilentlyContinue)
                if ($processes.Count) {
                    $lines += ($processes | Select-Object ProcessName, Id,
                        @{n='CPU_seconds';e={[math]::Round($_.CPU, 1)}},
                        @{n='Memory_MiB';e={[math]::Round($_.WorkingSet64 / 1MB, 1)}},
                        StartTime | Format-Table -AutoSize | Out-String -Width 200).TrimEnd()
                } else { $lines += '(none)' }
            }
            $lines += '=== disk ==='
            foreach ($drive in Get-PSDrive -Name C,D -PSProvider FileSystem -ErrorAction SilentlyContinue) {
                $lines += ('{0}: free {1:N2} GiB' -f $drive.Name, ($drive.Free / 1GB))
            }
            $os = Get-CimInstance Win32_OperatingSystem
            $lines += ('=== system memory: free {0:N2} / total {1:N2} GiB ===' -f ($os.FreePhysicalMemory / 1MB), ($os.TotalVisibleMemorySize / 1MB))
            $text = $lines -join [Environment]::NewLine
            Add-Content -LiteralPath $path -Value $text
            Write-Host $text
        } catch {
            # 诊断失败不改变编译结果。
            Write-Host "Diagnostic warning: $_"
        }
        Start-Sleep -Seconds $interval
    }
}

$code = 1
try {
    & cargo "+$Toolchain" build --release --locked -p codex-cli --bin codex --verbose 2>&1 | Tee-Object -FilePath $log
    $code = $LASTEXITCODE
} finally {
    Stop-Job -Job $monitor
    Remove-Job -Job $monitor
}
exit $code
