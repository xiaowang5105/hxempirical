# HX Empirical repository instructions

## Installation and release invariants

These rules apply to every AI agent and maintainer working in this repository.

1. `hxinstall.do` is the sole supported user-facing entrypoint for installation,
   updating, and repair.

2. Keep `net install` labeled compatibility-test-only. Do not recommend it for
   routine installation, updating, repair, troubleshooting, or release verification.

3. Preserve the managed target order:
   - writable `PERSONAL/h`;
   - otherwise writable `PLUS/h`.

4. An installation succeeds only when:
   - all staged files pass integrity checks;
   - `findfile hxempirical.ado` resolves to the intended target;
   - the effective ado version equals the release version;
   - no higher-priority stale copy shadows the installed version.

5. Preserve quoted-path parsing:
   `_hxinstaller_effective` must use `TARGET(string)`.
   Do not change it to `TARGET(string asis)`.

6. `hxempirical doctor` must inspect both `PERSONAL/h` and `PLUS/h` and report
   version conflicts and the currently effective path.

7. Installation, update, repair, and uninstall must remain transactional.
   Any failure must restore the complete previous installation.

8. Never delete an unverified user file. Stale copies may be removed only after
   manifest, version, path, and ownership validation.

9. Any installer or release change must run all release verification scripts and:
   - installer shadowing smoke test;
   - installer lifecycle smoke test;
   - installer integrity smoke test.

10. A release is complete only when all of the following agree:
    - source files on `main`;
    - `hxempirical.pkg`;
    - release ZIP;
    - release index;
    - all Base64 segments;
    - reconstructed ZIP checksum;
    - displayed package version.

11. Keep README.md, INSTALL.md, help files, and installer messages synchronized.

12. The empty/current-data Excel/CSV entry is a direct import workflow. It must:
    - accept `.xlsx`, `.xls`, and `.csv`;
    - derive a sibling `.dta` output automatically;
    - reuse the managed conversion engine instead of duplicating import logic;
    - keep overwrite protection and leading-zero protection;
    - load the generated DTA and refresh the workbench after success.
