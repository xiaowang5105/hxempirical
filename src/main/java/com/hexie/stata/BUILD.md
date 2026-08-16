# Rebuilding `hxworkbench.jar`

`hxworkbench.jar` is a production component. The repository targets Java 11 (`class` major version 55) and supports Stata 17+.

## Production rule

Compile `HxWorkbench.java` against the real Stata Function Interface archive from an installed Stata distribution:

```text
<Stata>/utilities/jar/sfi-api.jar
```

Do not ship a JAR compiled from the CI-only `com.stata.sfi` stubs. Those stubs exist only to catch Java syntax/type regressions in hosted CI; they do not replace Stata's runtime API.

Because the package supports Stata 17+, the safest release build is against the Stata 17 SFI API when that installation is available, followed by smoke testing on the supported Stata versions. Stata documents its Java API as forward-compatible rather than backward-compatible.

The repository tracks the exact Java source used to build the shipped JAR in:

```text
src/main/java/com/hexie/stata/HxWorkbench.jar-source
```

`tools/verify_hxworkbench_jar_sync.py` fails whenever `HxWorkbench.java` changes without a corresponding production JAR rebuild. This deliberately prevents a PR from passing release CI with a stale GUI binary.

## One-command Windows build

From the repository root, first try:

```powershell
pwsh -File tools/build_hxworkbench_jar.ps1
```

The script searches the normal `Program Files\Stata*` locations for `sfi-api.jar`, infers the Stata installation root, and then looks for `javac` / `jar` on `PATH`, in `JAVA_HOME`, or inside Stata's bundled Java directories.

If automatic discovery does not match the intended Stata installation, specify it explicitly:

```powershell
pwsh -File tools/build_hxworkbench_jar.ps1 -StataRoot "C:\Program Files\Stata18"
```

You can also pass the SFI archive directly:

```powershell
pwsh -File tools/build_hxworkbench_jar.ps1 -SfiJar "C:\Program Files\Stata18\utilities\jar\sfi-api.jar"
```

If `javac` / `jar` still cannot be found, pass a JDK explicitly:

```powershell
pwsh -File tools/build_hxworkbench_jar.ps1 `
  -StataRoot "C:\Program Files\Stata18" `
  -JavaHome "C:\path\to\jdk"
```

The build script performs all of the following:

1. Refuses to continue without an `sfi-api.jar` containing `com/stata/sfi/SFIToolkit.class`.
2. Compiles `HxWorkbench.java` with `javac --release 11`.
3. Replaces `hxworkbench.jar` with only the `com/hexie/stata` classes; Stata SFI classes are never bundled.
4. Updates `HxWorkbench.jar-source` to the Git blob SHA-1 of the exact source bytes used for the build.
5. Runs `tools/verify_hxworkbench_jar_sync.py`.
6. Rebuilds the managed ZIP/index/Base64 release bundle and runs `tools/verify_release.py` unless `-SkipReleaseBundle` is supplied.

## Real Stata smoke test

A successful compile is necessary but does not prove that the GUI works inside Stata. Before committing or publishing a rebuilt JAR, open the Stata version you intend to support and run the JAR directly from the repository path so an older installed copy cannot shadow it:

```stata
discard
local hxjar "C:/path/to/hxempirical/hxworkbench.jar"

javacall com.hexie.stata.HxWorkbench version, classpath("`hxjar'")
javacall com.hexie.stata.HxWorkbench selfTest, classpath("`hxjar'")
javacall com.hexie.stata.HxWorkbench launch, classpath("`hxjar'")
```

Then smoke-test at least these UI paths in the opened workbench:

- `xtreg` plus one generic panel estimator; for `xtabond` / `xtdpdsys`, confirm both panel and time variables are required and the generated model runs.
- `regress`, IV, `didregress` / `xtdidregress`, and one complex native-command-body page.
- `generate` plus one destructive data operation such as `keep/drop/merge` on disposable test data.
- one graph page, DTA conversion, missing-value analysis, DID builder, and the baseline-regression workspace.

Check the Stata Results/History after each run and confirm the displayed command is the command actually executed. Close the workbench and reopen it once to catch class-loading or stale-JAR issues.

## Commit gate

Only after the real Stata smoke test succeeds should the following generated files be committed together with the Java source:

```text
hxworkbench.jar
src/main/java/com/hexie/stata/HxWorkbench.jar-source
hxempirical-release.zip
hxempirical-release.index
release/hxempirical-release.b64.*
```

Finally run:

```powershell
python tools/verify_hxworkbench_jar_sync.py
python tools/verify_release.py
python tools/verify_static_contracts.py
```
