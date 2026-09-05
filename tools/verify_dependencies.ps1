$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$dependencies = Join-Path $root "addon\globalPlugins\soundtub\dependencies"
$checksumFile = Join-Path $dependencies "checksums.sha256"

foreach ($line in Get-Content -LiteralPath $checksumFile -Encoding UTF8) {
    if (-not $line.Trim() -or $line.TrimStart().StartsWith("#")) { continue }
    if ($line -notmatch '^([0-9A-Fa-f]{64})\s{2}(.+)$') {
        throw "Linha inválida no arquivo de hashes: $line"
    }
    $expected = $Matches[1].ToUpperInvariant()
    $relative = $Matches[2].Replace('/', [IO.Path]::DirectorySeparatorChar)
    $file = Join-Path $dependencies $relative
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "Dependência ausente: $relative"
    }
    $actual = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash
    if ($actual -ne $expected) {
        throw "Hash inválido para $relative. Esperado: $expected; obtido: $actual"
    }
}

Write-Output "Dependências verificadas com SHA-256."
