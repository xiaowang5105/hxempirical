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

function Get-PosixChecksum {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    # POSIX.1 cksum / Stata checksum: CRC-32 polynomial 0x04C11DB7,
    # followed by the file length encoded least-significant byte first.
    [uint64]$mask = 4294967295
    [uint64]$polynomial = 79764919
    $table = [uint64[]]::new(256)
    for ($index = 0; $index -lt 256; $index++) {
        [uint64]$value = ([uint64]$index -shl 24) -band $mask
        for ($bit = 0; $bit -lt 8; $bit++) {
            if (($value -band 2147483648) -ne 0) {
                $value = ((($value -shl 1) -band $mask) -bxor $polynomial) -band $mask
            }
            else {
                $value = ($value -shl 1) -band $mask
            }
        }
        $table[$index] = $value
    }

    [uint64]$crc = 0
    $bytes = [System.IO.File]::ReadAllBytes($LiteralPath)
    foreach ($byte in $bytes) {
        $tableIndex = [int]((($crc -shr 24) -bxor [uint64]$byte) -band 255)
        $crc = ((($crc -shl 8) -band $mask) -bxor $table[$tableIndex]) -band $mask
    }

    [uint64]$remainingLength = $bytes.LongLength
    while ($remainingLength -ne 0) {
        $lengthByte = $remainingLength -band 255
        $tableIndex = [int]((($crc -shr 24) -bxor $lengthByte) -band 255)
        $crc = ((($crc -shl 8) -band $mask) -bxor $table[$tableIndex]) -band $mask
        $remainingLength = $remainingLength -shr 8
    }

    return ((-bnot $crc) -band $mask)
}

function Copy-FlatReleaseFiles {
    param(
        [Parameter(Mandatory = $true)][string]$SourceRoot,
        [Parameter(Mandatory = $true)][string]$DestinationRoot,
        [Parameter(Mandatory = $true)][string[]]$RelativePaths
    )
    foreach ($relativePath in $RelativePaths) {
        $sourcePath = Join-Path $SourceRoot $relativePath
        $destinationPath = Join-Path $DestinationRoot $relativePath
        $destinationDirectory = Split-Path -Parent $destinationPath
        if (-not (Test-Path -LiteralPath $destinationDirectory -PathType Container)) {
            [System.IO.Directory]::CreateDirectory($destinationDirectory) | Out-Null
        }
        [System.IO.File]::Copy($sourcePath, $destinationPath, $true)
    }
}

function New-PortableZipFromDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$SourceDirectory,
        [Parameter(Mandatory = $true)][string]$ArchivePath
    )
    $source = [System.IO.Path]::GetFullPath($SourceDirectory).TrimEnd('\', '/')
    $archive = [System.IO.Compression.ZipFile]::Open(
        $ArchivePath,
        [System.IO.Compression.ZipArchiveMode]::Create
    )
    try {
        foreach ($file in Get-ChildItem -LiteralPath $source -File -Recurse | Sort-Object FullName) {
            $relativePath = $file.FullName.Substring($source.Length + 1).Replace('\', '/')
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                $archive,
                $file.FullName,
                $relativePath,
                [System.IO.Compression.CompressionLevel]::Optimal
            ) | Out-Null
        }
    }
    finally {
        $archive.Dispose()
    }
}

function Write-Base64Parts {
    param(
        [Parameter(Mandatory = $true)][string]$ArchivePath,
        [Parameter(Mandatory = $true)][string]$OutputRoot,
        [Parameter(Mandatory = $true)][string]$RelativeDirectory,
        [Parameter(Mandatory = $true)][int]$ChunkSize,
        [Parameter(Mandatory = $true)][System.Text.Encoding]$Encoding
    )

    $outputDirectory = Join-Path $OutputRoot $RelativeDirectory
    [System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
    $base64 = [System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes($ArchivePath))
    $names = [System.Collections.Generic.List[string]]::new()
    $partNumber = 0
    for ($offset = 0; $offset -lt $base64.Length; $offset += $ChunkSize) {
        $partNumber++
        $length = [Math]::Min($ChunkSize, $base64.Length - $offset)
        $leafName = 'hxempirical-release.b64.{0:D3}' -f $partNumber
        $relativeName = ($RelativeDirectory.TrimEnd('\', '/') + '/' + $leafName).Replace('\', '/')
        $partPath = Join-Path $OutputRoot $relativeName
        $chunk = $base64.Substring($offset, $length)
        $chunkLines = [System.Collections.Generic.List[string]]::new()
        for ($lineOffset = 0; $lineOffset -lt $chunk.Length; $lineOffset += 76) {
            $lineLength = [Math]::Min(76, $chunk.Length - $lineOffset)
            $chunkLines.Add($chunk.Substring($lineOffset, $lineLength))
        }
        [System.IO.File]::WriteAllLines($partPath, $chunkLines, $Encoding)
        $names.Add($relativeName)
    }
    return $names.ToArray()
}

function Write-ReleaseIndex {
    param(
        [Parameter(Mandatory = $true)][string]$IndexPath,
        [Parameter(Mandatory = $true)][string]$ArchivePath,
        [Parameter(Mandatory = $true)][string]$ArchiveName,
        [Parameter(Mandatory = $true)][string]$PackagePath,
        [Parameter(Mandatory = $true)][string]$PackageName,
        [Parameter(Mandatory = $true)][string]$PackageVersion,
        [Parameter(Mandatory = $true)][string[]]$PartNames,
        [Parameter(Mandatory = $true)][System.Text.Encoding]$Encoding,
        [string[]]$ExtraMetadata = @()
    )

    $archiveSha256 = (Get-FileHash -LiteralPath $ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant()
    $packageSha256 = (Get-FileHash -LiteralPath $PackagePath -Algorithm SHA256).Hash.ToLowerInvariant()
    $archiveBytes = (Get-Item -LiteralPath $ArchivePath).Length
    $packageBytes = (Get-Item -LiteralPath $PackagePath).Length
    $archiveChecksum = Get-PosixChecksum -LiteralPath $ArchivePath
    $packageChecksum = Get-PosixChecksum -LiteralPath $PackagePath
    $indexLines = @(
        'v 1'
        "d archive $ArchiveName"
        "d package $PackageName"
        "d version $PackageVersion"
        "d pkg_bytes $packageBytes"
        "d pkg_checksum $packageChecksum"
        "d pkg_sha256 $packageSha256"
        "d bytes $archiveBytes"
        "d checksum $archiveChecksum"
        "d sha256 $archiveSha256"
        "d parts $($PartNames.Count)"
    ) + @($ExtraMetadata) + @($PartNames | ForEach-Object { "f $_" })
    [System.IO.File]::WriteAllLines($IndexPath, $indexLines, $Encoding)

    return [PSCustomObject]@{
        ArchiveBytes = $archiveBytes
        ArchiveChecksum = $archiveChecksum
        ArchiveSHA256 = $archiveSha256
        PackageBytes = $packageBytes
        PackageChecksum = $packageChecksum
        PackageSHA256 = $packageSha256
        Parts = $PartNames.Count
    }
}

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
if ($managedFiles.Count -eq 0) {
    throw "No managed files found in $manifestPath"
}
$duplicateManaged = @($managedFiles | Group-Object | Where-Object Count -gt 1)
if ($duplicateManaged.Count -gt 0) {
    throw "Duplicate managed file in manifest: $($duplicateManaged[0].Name)"
}
foreach ($managedFile in $managedFiles) {
    if ($managedFile -notmatch '^[A-Za-z0-9_][A-Za-z0-9_.-]*$' -or $managedFile.Contains('..')) {
        throw "Unsafe managed filename in manifest: $managedFile"
    }
}
$packageVersionLine = Get-Content -LiteralPath $manifestPath -Encoding UTF8 |
    Where-Object { $_ -match '^d\s+Version\s+(.+?)\s*$' } |
    Select-Object -First 1
if ($null -eq $packageVersionLine -or $packageVersionLine -notmatch '^d\s+Version\s+(.+?)\s*$') {
    throw "Package version is missing from $manifestPath"
}
$packageVersion = $Matches[1]
$packageName = Split-Path -Leaf $manifestPath
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
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$buildRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('hxempirical-release-build-' + [guid]::NewGuid().ToString('N'))
$outerStage = Join-Path $buildRoot 'outer'

try {
    [System.IO.Directory]::CreateDirectory($outerStage) | Out-Null
    Copy-FlatReleaseFiles -SourceRoot $repository -DestinationRoot $outerStage -RelativePaths $bundleFiles

    # The extracted browser ZIP installs directly from its managed files.  A
    # separate per-file index is generated before the ZIP and therefore avoids
    # any self-reference while still giving Stata exact byte/checksum bindings.
    $packageBytes = (Get-Item -LiteralPath $manifestPath).Length
    $packageChecksum = Get-PosixChecksum -LiteralPath $manifestPath
    $offlineIndexLines = [System.Collections.Generic.List[string]]::new()
    $offlineIndexLines.Add('v 1')
    $offlineIndexLines.Add("d package $packageName")
    $offlineIndexLines.Add("d version $packageVersion")
    $offlineIndexLines.Add("d pkg_bytes $packageBytes")
    $offlineIndexLines.Add("d pkg_checksum $packageChecksum")
    foreach ($managedFile in $managedFiles) {
        $managedPath = Join-Path $repository $managedFile
        $managedBytes = (Get-Item -LiteralPath $managedPath).Length
        $managedChecksum = Get-PosixChecksum -LiteralPath $managedPath
        $offlineIndexLines.Add("f $managedFile $managedBytes $managedChecksum")
    }
    $offlineIndexPath = Join-Path $outerStage 'hxempirical-offline.index'
    [System.IO.File]::WriteAllLines($offlineIndexPath, $offlineIndexLines, $utf8NoBom)

    New-PortableZipFromDirectory -SourceDirectory $outerStage -ArchivePath $archivePath

    $partNames = @(Write-Base64Parts -ArchivePath $archivePath -OutputRoot $repository -RelativeDirectory 'release' -ChunkSize $ChunkBytes -Encoding $utf8NoBom)
    $metadata = Write-ReleaseIndex -IndexPath $indexPath -ArchivePath $archivePath -ArchiveName 'hxempirical-release.zip' -PackagePath $manifestPath -PackageName $packageName -PackageVersion $packageVersion -PartNames $partNames -Encoding $utf8NoBom -ExtraMetadata @('d offline_index hxempirical-offline.index')

    [PSCustomObject]@{
        Archive = $archivePath
        ArchiveBytes = $metadata.ArchiveBytes
        Parts = $metadata.Parts
        OfflineManagedFiles = $managedFiles.Count
        ChunkBytes = $ChunkBytes
        Index = $indexPath
        SHA256 = $metadata.ArchiveSHA256
        Package = $packageName
        PackageVersion = $packageVersion
        PackageBytes = $metadata.PackageBytes
        PackagePOSIXChecksum = $metadata.PackageChecksum
        PackageSHA256 = $metadata.PackageSHA256
        POSIXChecksum = $metadata.ArchiveChecksum
    }
}
finally {
    if (Test-Path -LiteralPath $buildRoot -PathType Container) {
        Remove-Item -LiteralPath $buildRoot -Recurse -Force
    }
}
