param(
    [string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot),
    [int]$ChunkBytes = 49152
)

$ErrorActionPreference = 'Stop'
$repository = [System.IO.Path]::GetFullPath($RepositoryRoot)
$manifestPath = Join-Path $repository 'hxempirical.pkg'
$releaseDir = Join-Path $repository 'release'
$archivePath = Join-Path $repository 'hxempirical-release.zip'
$indexPath = Join-Path $repository 'hxempirical-release.index'

if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Missing manifest: $manifestPath"
}
if ($ChunkBytes -lt 4096 -or ($ChunkBytes % 4) -ne 0) {
    throw 'ChunkBytes must be at least 4096 and divisible by 4.'
}

$managedFiles = @(
    Get-Content -LiteralPath $manifestPath -Encoding UTF8 |
        ForEach-Object {
            if ($_ -match '^[fF]\s+(.+?)\s*$') { $Matches[1] }
        }
)
$bundleFiles = @($managedFiles + 'hxempirical.pkg' + 'hxinstall.do' + 'hxinstall_offline.do' + 'INSTALL.md') |
    Select-Object -Unique

foreach ($relativePath in $bundleFiles) {
    $fullPath = Join-Path $repository $relativePath
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        throw "Bundle input is missing: $relativePath"
    }
}

if (-not (Test-Path -LiteralPath $releaseDir -PathType Container)) {
    New-Item -ItemType Directory -Path $releaseDir | Out-Null
}

$resolvedRelease = [System.IO.Path]::GetFullPath($releaseDir)
if (-not $resolvedRelease.StartsWith($repository, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Unsafe release directory: $resolvedRelease"
}
Get-ChildItem -LiteralPath $releaseDir -Filter 'hxempirical-release.b64.*' -File -ErrorAction SilentlyContinue |
    Remove-Item -Force
if (Test-Path -LiteralPath $archivePath) { Remove-Item -LiteralPath $archivePath -Force }
if (Test-Path -LiteralPath $indexPath) { Remove-Item -LiteralPath $indexPath -Force }

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::Open(
    $archivePath,
    [System.IO.Compression.ZipArchiveMode]::Create
)
try {
    foreach ($relativePath in $bundleFiles) {
        $fullPath = Join-Path $repository $relativePath
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $archive,
            $fullPath,
            $relativePath.Replace('\', '/'),
            [System.IO.Compression.CompressionLevel]::Optimal
        ) | Out-Null
    }
}
finally {
    $archive.Dispose()
}

$base64 = [System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes($archivePath))
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$partNames = [System.Collections.Generic.List[string]]::new()
$partNumber = 0
for ($offset = 0; $offset -lt $base64.Length; $offset += $ChunkBytes) {
    $partNumber++
    $length = [Math]::Min($ChunkBytes, $base64.Length - $offset)
    $partName = 'release/hxempirical-release.b64.{0:D3}' -f $partNumber
    $partPath = Join-Path $repository $partName
    $chunk = $base64.Substring($offset, $length)
    $chunkLines = [System.Collections.Generic.List[string]]::new()
    for ($lineOffset = 0; $lineOffset -lt $chunk.Length; $lineOffset += 76) {
        $lineLength = [Math]::Min(76, $chunk.Length - $lineOffset)
        $chunkLines.Add($chunk.Substring($lineOffset, $lineLength))
    }
    [System.IO.File]::WriteAllLines($partPath, $chunkLines, $utf8NoBom)
    $partNames.Add($partName)
}

$sha256 = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
$archiveBytes = (Get-Item -LiteralPath $archivePath).Length
$indexLines = @(
    'v 1'
    "d archive hxempirical-release.zip"
    "d bytes $archiveBytes"
    "d sha256 $sha256"
    "d parts $($partNames.Count)"
) + @($partNames | ForEach-Object { "f $_" })
[System.IO.File]::WriteAllLines($indexPath, $indexLines, $utf8NoBom)

[PSCustomObject]@{
    Archive = $archivePath
    ArchiveBytes = $archiveBytes
    Parts = $partNames.Count
    ChunkBytes = $ChunkBytes
    Index = $indexPath
    SHA256 = $sha256
}
