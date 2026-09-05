param([string]$Output = "dist\SoundTub-1.0.0.nvda-addon")
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$addon = Join-Path $root "addon"
$tools = Join-Path $addon "globalPlugins\soundtub\dependencies\win64"
& (Join-Path $PSScriptRoot "verify_dependencies.ps1")
foreach ($name in @(
    "yt-dlp.exe", "ffmpeg.exe", "ffprobe.exe", "qjs.exe", "bgutil-pot.exe",
    "avcodec-63.dll", "avdevice-63.dll", "avfilter-12.dll", "avformat-63.dll",
    "avutil-61.dll", "swresample-7.dll", "swscale-10.dll"
)) {
    if (-not (Test-Path -LiteralPath (Join-Path $tools $name) -PathType Leaf)) {
        throw "Dependência ausente: $name."
    }
}
$plugin = Join-Path $tools "plugins\bgutil-ytdlp-pot-provider-rs.zip"
if (-not (Test-Path -LiteralPath $plugin -PathType Leaf)) {
    throw "Dependência ausente: plugins\bgutil-ytdlp-pot-provider-rs.zip."
}
$target = Join-Path $root $Output
$targetDir = Split-Path -Parent $target
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target }
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$stream = [System.IO.File]::Open($target, [System.IO.FileMode]::CreateNew)
try {
    $archive = [System.IO.Compression.ZipArchive]::new(
        $stream, [System.IO.Compression.ZipArchiveMode]::Create, $false
    )
    try {
        Get-ChildItem -LiteralPath $addon -Recurse -File |
            Where-Object { $_.FullName -notmatch '[\\/]__pycache__[\\/]' -and $_.Extension -ne '.pyc' } |
            ForEach-Object {
                $relative = $_.FullName.Substring($addon.Length + 1).Replace('\', '/')
                [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                    $archive, $_.FullName, $relative,
                    [System.IO.Compression.CompressionLevel]::Optimal
                ) | Out-Null
            }
    } finally {
        $archive.Dispose()
    }
} finally {
    $stream.Dispose()
}
Write-Output $target
