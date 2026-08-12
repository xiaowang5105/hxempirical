# HX Workbench Java source

`HxWorkbench.java` is the source baseline corresponding to the current `hxworkbench.jar` generation.

The source was recovered from the shipping JAR, mechanically repaired so that it compiles with Java 11, and validated against the original UI before product changes were applied.

Validation performed before the first UI refactor:

- Java target: class-file major version 55 (Java 11), matching the original JAR.
- HX class set: 44 `com.hexie.stata` class files, matching the original JAR.
- `render-regress-preview`: pixel-identical to the original 0.9.7 JAR before changes.
- All built-in offline preview modes rendered successfully.

Current UI rule for ordinary commands:

- common parameters first;
- low-frequency parameters under `更多设置`;
- validation remains in the background and only surfaces exceptions;
- the final real Stata command remains visible;
- ordinary estimation/data operations continue to call Stata official or mature third-party commands.

HX-specific multi-step logic belongs in Workflow/专区 features.
