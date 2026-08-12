# Rebuilding `hxworkbench.jar`

The workbench targets Java 11 (`class` major version 55), matching the JAR shipped with hxempirical 0.9.7.

A normal production build must compile `HxWorkbench.java` against Stata's Java SFI classes (`com.stata.sfi.*`) from the installed Stata environment, then package `com/hexie/stata/*.class` into `hxworkbench.jar`.

The temporary GitHub Actions workflows used during source recovery are intentionally not kept in the release branch. They used compile-only SFI stubs solely to verify Java syntax, target version, class structure and offline render modes; they do not replace Stata's real SFI runtime.

Before replacing the production JAR:

1. Compile for Java 11.
2. Confirm the HX class set is complete.
3. Run the built-in offline preview modes.
4. Run a real Stata smoke test for launch, native command execution and Workflow integrations.
