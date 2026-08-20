param(
    [string]$StataExe = 'D:\Stata\StataMP-64.exe',
    [string]$Repository = (Split-Path -Parent $PSScriptRoot),
    [ValidateRange(10, 3600)][int]$TimeoutSeconds = 180
)

$ErrorActionPreference = 'Stop'
if ($env:OS -ne 'Windows_NT') {
    throw 'run_stata_tests.ps1 is the Windows runner. On macOS, run each tests/*.do file from Stata batch mode.'
}
$repositoryPath = (Resolve-Path -LiteralPath $Repository).Path
$testsPath = Join-Path $repositoryPath 'tests'

if (-not (Test-Path -LiteralPath $StataExe -PathType Leaf)) {
    throw "Stata executable not found: $StataExe"
}
if (-not (Test-Path -LiteralPath $testsPath -PathType Container)) {
    throw "Tests directory not found: $testsPath"
}

function Convert-ToStataPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return $Path.Replace('\', '/')
}

$testFiles = @(Get-ChildItem -LiteralPath $testsPath -Filter '*.do' -File | Sort-Object Name)
if ($testFiles.Count -eq 0) {
    throw "No Stata smoke tests found in $testsPath"
}

$runDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ("hxempirical-stata-tests-" + [guid]::NewGuid().ToString('N'))
[System.IO.Directory]::CreateDirectory($runDirectory) | Out-Null
$failures = [System.Collections.Generic.List[string]]::new()
$completedCleanly = $false

try {
    foreach ($testFile in $testFiles) {
        $source = [System.IO.File]::ReadAllText($testFile.FullName)
        $markerMatch = [regex]::Match($source, 'display\s+as\s+result\s+"(?<marker>[A-Z0-9_]+_OK)"')
        if (-not $markerMatch.Success) {
            $failures.Add("$($testFile.Name): no explicit *_OK marker")
            continue
        }

        $marker = $markerMatch.Groups['marker'].Value
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($testFile.Name)
        $wrapperPath = Join-Path $runDirectory ("wrapper-$stem.do")
        # Stata /e automatically creates a log beside the wrapper do-file.
        # Inspect that outer log because an individual smoke test may close all
        # user logs while verifying its own Results output.
        $logPath = Join-Path $runDirectory ("wrapper-$stem.log")
        $testStata = Convert-ToStataPath $testFile.FullName
        $repositoryStata = Convert-ToStataPath $repositoryPath

        $wrapper = @(
            'version 17.0'
            'clear all'
            'set more off'
            "capture noisily do `"$testStata`" `"$repositoryStata`""
            'local test_rc = _rc'
            "display as text `"HX_TEST_RUNNER_RC=``test_rc'`""
            "exit ``test_rc'"
        )
        [System.IO.File]::WriteAllLines($wrapperPath, $wrapper, [System.Text.UTF8Encoding]::new($false))

        $wrapperStata = Convert-ToStataPath $wrapperPath
        $argumentLine = "/e do `"$wrapperStata`""
        try {
            $process = Start-Process -FilePath $StataExe -ArgumentList $argumentLine -WorkingDirectory $runDirectory -WindowStyle Hidden -PassThru
            if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                $failures.Add("$($testFile.Name): timed out after $TimeoutSeconds seconds; artifacts=$runDirectory")
                continue
            }
        }
        catch {
            $failures.Add("$($testFile.Name): runner exception: $($_.Exception.Message); artifacts=$runDirectory")
            continue
        }

        if (-not (Test-Path -LiteralPath $logPath -PathType Leaf)) {
            $failures.Add("$($testFile.Name): Stata produced no log (process exit $($process.ExitCode))")
            continue
        }

        $logText = [System.IO.File]::ReadAllText($logPath)
        $hasMarker = $logText.Contains($marker)
        $hasZeroRc = $logText.Contains('HX_TEST_RUNNER_RC=0')
        if (-not $hasMarker -or -not $hasZeroRc) {
            $failures.Add("$($testFile.Name): marker=$hasMarker rc0=$hasZeroRc process=$($process.ExitCode); log=$logPath")
            continue
        }

        Write-Host "PASS $($testFile.Name) [$marker]"
    }

    if ($failures.Count -gt 0) {
        $failures | ForEach-Object { Write-Host "FAIL $_" -ForegroundColor Red }
        throw "$($failures.Count) Stata smoke test(s) failed."
    }

    Write-Host "All $($testFiles.Count) Stata smoke tests passed with explicit log markers."
    $completedCleanly = $true
}
finally {
    if ($completedCleanly -and (Test-Path -LiteralPath $runDirectory)) {
        Remove-Item -LiteralPath $runDirectory -Recurse -Force
    }
    elseif (Test-Path -LiteralPath $runDirectory) {
        Write-Host "Failed-test logs retained at: $runDirectory"
    }
}
