<#
.SYNOPSIS
使用 ffmpeg 批量转换音频格式。默认：目录内 *.m4a -> *.mp3，输出到输入目录。

.PARAMETER InputDir
    输入目录（必填或默认当前目录）
.PARAMETER SourceExt
    源音频扩展名，默认 m4a
.PARAMETER TargetExt
    目标扩展名，默认 mp3
.PARAMETER OutputDir
    输出目录，默认 = 输入目录
.PARAMETER Bitrate
    目标码率（kbps），仅 mp3/ogg/opus 等有损格式生效，默认 320
.PARAMETER Ffmpeg
    ffmpeg 可执行文件路径，默认 PATH 中的 ffmpeg
.PARAMETER Force
    覆盖已存在的目标文件，默认跳过

.EXAMPLE
    ./convert_audio.ps1 "D:\Music\260916"
    ./convert_audio.ps1 -InputDir "D:\Music\260916" -SourceExt m4a -TargetExt mp3
    ./convert_audio.ps1 "D:\Music" wav flac -OutDir "D:\Music\flac"
#>
param(
    [string]$InputDir = (Get-Location).Path,
    [string]$SourceExt = "m4a",
    [string]$TargetExt = "mp3",
    [string]$OutputDir = "",
    [int]$Bitrate = 320,
    [string]$Ffmpeg = "ffmpeg",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Get-TargetCodec([string]$ext) {
    switch ($ext.ToLower()) {
        "mp3"  { return "libmp3lame" }
        "ogg"  { return "libvorbis" }
        "opus" { return "libopus" }
        "flac" { return "flac" }
        "wav"  { return "pcm_s16le" }
        default { return "" }  # 交给 ffmpeg 自动选择
    }
}

if (-not $OutputDir) { $OutputDir = $InputDir }
$InputDir  = [IO.Path]::GetFullPath($InputDir)
$OutputDir = [IO.Path]::GetFullPath($OutputDir)
if (-not (Test-Path $InputDir))  { Write-Error "输入目录不存在: $InputDir"; exit 1 }
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }

$pattern = "*." + $SourceExt.TrimStart('.')
$files = Get-ChildItem -Path $InputDir -Filter $pattern -File
if ($files.Count -eq 0) { Write-Host "未找到 $pattern 文件（目录: $InputDir）"; exit 0 }

$codec = Get-TargetCodec $TargetExt
$ok = 0; $skip = 0; $fail = 0
foreach ($f in $files) {
    $out = Join-Path $OutputDir (($f.BaseName) + "." + $TargetExt.TrimStart('.'))
    if ((Test-Path $out) -and -not $Force) {
        Write-Host "[跳过] 已存在: $($f.Name)"
        $skip++
        continue
    }
    Write-Host "[转换] $($f.Name) -> $(Split-Path $out -Leaf)"
    if ($codec) {
        if ($codec -eq "libmp3lame" -or $codec -eq "libvorbis" -or $codec -eq "libopus") {
            & $Ffmpeg -y -hide_banner -loglevel error -i $f.FullName -codec:a $codec -b:a "${Bitrate}k" -map_metadata 0 "$out"
        } else {
            & $Ffmpeg -y -hide_banner -loglevel error -i $f.FullName -codec:a $codec -map_metadata 0 "$out"
        }
    } else {
        & $Ffmpeg -y -hide_banner -loglevel error -i $f.FullName -map_metadata 0 "$out"
    }
    if ($LASTEXITCODE -ne 0) { Write-Host "[失败] $($f.Name)"; $fail++ } else { $ok++ }
}
Write-Host ""
Write-Host "完成: 转换 $ok / 跳过 $skip / 失败 $fail"
if ($fail -gt 0) { exit 1 } else { exit 0 }
