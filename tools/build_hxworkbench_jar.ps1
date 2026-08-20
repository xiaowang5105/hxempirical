param(
    [string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$StataRoot = $env:STATA_HOME,
    [string]$SfiJar = $env:STATA_SFI_JAR,
    [string]$JavaHome = $env:JAVA_HOME,
    [switch]$SkipReleaseBundle
)

$ErrorActionPreference = 'Stop'
$repository = [System.IO.Path]::GetFullPath($RepositoryRoot)
$source = Join-Path $repository 'src/main/java/com/hexie/stata/HxWorkbench.java'
$marker = Join-Path $repository 'src/main/java/com/hexie/stata/HxWorkbench.jar-source'
$outputJar = Join-Path $repository 'hxworkbench.jar'
$buildRoot = Join-Path $repository '.build/hxworkbench'
$classes = Join-Path $buildRoot 'classes'

function Resolve-ExistingFile([string[]]$Candidates) {
    foreach ($candidate in $Candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            return [System.IO.Path]::GetFullPath($candidate)
        }
    }
    return $null
}

function Resolve-JavaTool([string]$Name, [string]$ConfiguredJavaHome, [string]$ConfiguredStataRoot) {
    $suffix = if ($IsWindows -or $env:OS -eq 'Windows_NT') { "$Name.exe" } else { $Name }
    $candidates = @()
    if ($ConfiguredJavaHome) {
        $candidates += (Join-Path $ConfiguredJavaHome "bin/$suffix")
    }
    $resolved = Resolve-ExistingFile $candidates
    if ($resolved) { return $resolved }

    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }

    if ($ConfiguredStataRoot -and (Test-Path -LiteralPath $ConfiguredStataRoot -PathType Container)) {
        $utilities = Join-Path $ConfiguredStataRoot 'utilities'
        if (Test-Path -LiteralPath $utilities -PathType Container) {
            $match = Get-ChildItem -LiteralPath $utilities -Filter $suffix -File -Recurse -ErrorAction SilentlyContinue |
                Select-Object -First 1
            if ($match) { return $match.FullName }
        }
    }
    return $null
}

if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
    throw "Missing Java source: $source"
}

if (-not $SfiJar) {
    $sfiCandidates = @()
    if ($StataRoot) {
        $sfiCandidates += (Join-Path $StataRoot 'utilities/jar/sfi-api.jar')
    }
    if ($env:ProgramFiles) {
        $sfiCandidates += @(
            Get-ChildItem -Path (Join-Path $env:ProgramFiles 'Stata*') -Directory -ErrorAction SilentlyContinue |
                Sort-Object Name -Descending |
                ForEach-Object { Join-Path $_.FullName 'utilities/jar/sfi-api.jar' }
        )
    }
    if (${env:ProgramFiles(x86)}) {
        $sfiCandidates += @(
            Get-ChildItem -Path (Join-Path ${env:ProgramFiles(x86)} 'Stata*') -Directory -ErrorAction SilentlyContinue |
                Sort-Object Name -Descending |
                ForEach-Object { Join-Path $_.FullName 'utilities/jar/sfi-api.jar' }
        )
    }
    $SfiJar = Resolve-ExistingFile $sfiCandidates
} else {
    $SfiJar = Resolve-ExistingFile @($SfiJar)
}

if (-not $SfiJar) {
    throw @"
Stata sfi-api.jar was not found.
Pass -StataRoot "C:\Program Files\Stata18" or -SfiJar "...\utilities\jar\sfi-api.jar".
The production JAR must be compiled against Stata's real SFI API; CI compile stubs are not accepted for this build.
"@
}

# If SFI was auto-detected, infer the Stata installation root so the bundled JDK can also be found.
if (-not $StataRoot) {
    $jarDirectory = Split-Path -Parent $SfiJar
    $utilitiesDirectory = Split-Path -Parent $jarDirectory
    $candidateStataRoot = Split-Path -Parent $utilitiesDirectory
    if (Test-Path -LiteralPath $candidateStataRoot -PathType Container) {
        $StataRoot = $candidateStataRoot
    }
}

$javac = Resolve-JavaTool 'javac' $JavaHome $StataRoot
$jarTool = Resolve-JavaTool 'jar' $JavaHome $StataRoot
if (-not $javac -or -not $jarTool) {
    throw "Java compiler tools were not found. Pass -JavaHome to a JDK with javac and jar, or expose them on PATH."
}

# Make sure the selected SFI archive looks like the Stata API archive before compiling.
$sfiListing = & $jarTool tf $SfiJar
if ($LASTEXITCODE -ne 0 -or -not ($sfiListing -contains 'com/stata/sfi/SFIToolkit.class')) {
    throw "The selected file is not a usable Stata sfi-api.jar: $SfiJar"
}

if (Test-Path -LiteralPath $buildRoot) {
    Remove-Item -LiteralPath $buildRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $classes -Force | Out-Null

Write-Host "Compiling HxWorkbench.java with real Stata SFI: $SfiJar"
& $javac --release 11 -Xmaxerrs 200 -classpath $SfiJar -d $classes $source
if ($LASTEXITCODE -ne 0) {
    throw "javac failed with exit code $LASTEXITCODE"
}

if (Test-Path -LiteralPath $outputJar) {
    Remove-Item -LiteralPath $outputJar -Force
}
& $jarTool --create --file $outputJar -C $classes com/hexie/stata
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $outputJar -PathType Leaf)) {
    throw "jar packaging failed with exit code $LASTEXITCODE"
}

# Record the canonical Git blob for the Java source.  Git normalizes this
# tracked text file to LF, so normalize the Windows working-tree copy before
# calculating the blob ID.  This makes the provenance marker identical on
# Windows, macOS, and Linux CI.
$sourceText = [System.IO.File]::ReadAllText($source, [System.Text.Encoding]::UTF8)
$sourceText = $sourceText.Replace("`r`n", "`n").Replace("`r", "`n")
$sourceBytes = [System.Text.Encoding]::UTF8.GetBytes($sourceText)
$prefixBytes = [System.Text.Encoding]::ASCII.GetBytes("blob $($sourceBytes.Length)`0")
$blobBytes = New-Object byte[] ($prefixBytes.Length + $sourceBytes.Length)
[System.Buffer]::BlockCopy($prefixBytes, 0, $blobBytes, 0, $prefixBytes.Length)
[System.Buffer]::BlockCopy($sourceBytes, 0, $blobBytes, $prefixBytes.Length, $sourceBytes.Length)
$sha1 = [System.Security.Cryptography.SHA1]::Create()
try {
    $sourceBlob = ([System.BitConverter]::ToString($sha1.ComputeHash($blobBytes))).Replace('-', '').ToLowerInvariant()
}
finally {
    $sha1.Dispose()
}
$markerText = @(
    '# Git blob SHA-1 of src/main/java/com/hexie/stata/HxWorkbench.java used to build the shipped hxworkbench.jar.'
    '# This file is updated only by tools/build_hxworkbench_jar.ps1 after a successful build against Stata''s real sfi-api.jar.'
    $sourceBlob
) -join [Environment]::NewLine
[System.IO.File]::WriteAllText($marker, $markerText + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $python) {
    throw 'Python 3 is required for the repository verification scripts.'
}

& $python.Source (Join-Path $repository 'tools/verify_hxworkbench_jar_sync.py')
if ($LASTEXITCODE -ne 0) { throw 'JAR/source verification failed.' }

if (-not $SkipReleaseBundle) {
    & (Join-Path $repository 'tools/build_release_bundle.ps1') -RepositoryRoot $repository
    if ($LASTEXITCODE -ne 0) { throw 'Managed release bundle rebuild failed.' }
    & $python.Source (Join-Path $repository 'tools/verify_release.py')
    if ($LASTEXITCODE -ne 0) { throw 'Managed release verification failed.' }
}

Write-Host "HX_WORKBENCH_PRODUCTION_BUILD_OK"
Write-Host "Stata root: $StataRoot"
Write-Host "JAR: $outputJar"
Write-Host "Source Git blob: $sourceBlob"
Write-Host "Next: run the real-Stata smoke test documented in src/main/java/com/hexie/stata/BUILD.md before committing the JAR and release bundle."
