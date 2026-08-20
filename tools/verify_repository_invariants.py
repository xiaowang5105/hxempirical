from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"HX_REPO_INVARIANTS_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        fail(f"missing required file: {path}")
    return target.read_text(encoding="utf-8")


readme = read("README.md")
agents = read("AGENTS.md")
installer = read("hxinstaller.ado")
ci = read(".github/workflows/ci.yml")
runner = read("tools/run_stata_tests.ps1")
pkg = read("hxempirical.pkg")
release_index = read("hxempirical-release.index")

entrypoint = 'do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"'
if readme.count(entrypoint) != 1:
    fail(f"README must contain exactly one executable hxinstall.do entrypoint; found {readme.count(entrypoint)}")
if "## 唯一受支持的安装、更新与修复入口" not in readme:
    fail("README primary installation section missing")
if re.search(r"(?mi)^\s*net\s+install\s+hxempirical\b", readme):
    fail("README contains a copy-pastable net install hxempirical command")
if "`net install` 仅作为兼容性测试接口保留" not in readme:
    fail("README must label net install compatibility-test-only")

required_agent_rules = (
    "`hxinstall.do` is the sole supported user-facing entrypoint",
    "Keep `net install` labeled compatibility-test-only",
    "`_hxinstaller_effective` must use `TARGET(string)`",
    "Do not change it to `TARGET(string asis)`",
    "installer shadowing smoke test",
    "installer lifecycle smoke test",
    "installer integrity smoke test",
)
for rule in required_agent_rules:
    if rule not in agents:
        fail(f"AGENTS.md invariant missing: {rule}")

helper_match = re.search(
    r"program define _hxinstaller_effective, rclass(?P<body>.*?)(?:\ncapture program drop|\Z)",
    installer,
    flags=re.S,
)
if not helper_match:
    fail("_hxinstaller_effective program missing")
helper = helper_match.group("body")
if "syntax , TARGET(string) PACKAGEVERSION(string)" not in helper:
    fail("_hxinstaller_effective must use TARGET(string)")
if "TARGET(string asis)" in helper:
    fail("_hxinstaller_effective must not use TARGET(string asis)")

if "python tools/verify_repository_invariants.py" not in ci:
    fail("CI does not run repository invariant verifier")

required_smokes = {
    "tests/installer_shadowing_smoke.do": "HX_INSTALLER_SHADOWING_OK",
    "tests/installer_lifecycle_smoke.do": "HX_INSTALLER_LIFECYCLE_OK",
    "tests/installer_integrity_smoke.do": "HX_INSTALLER_INTEGRITY_OK",
}
for path, marker in required_smokes.items():
    source = read(path)
    if marker not in source:
        fail(f"required installer smoke lacks explicit success marker: {path}")

# The Windows release runner auto-discovers every tests/*.do file, so the three
# required installer smokes cannot silently fall out of the real-Stata suite.
if "Get-ChildItem -LiteralPath $testsPath -Filter '*.do'" not in runner:
    fail("Stata test runner no longer auto-discovers tests/*.do")

pkg_match = re.search(r"^d Version ([0-9]+\.[0-9]+\.[0-9]+)$", pkg, re.M)
index_match = re.search(r"^d version ([0-9]+\.[0-9]+\.[0-9]+)$", release_index, re.M)
readme_match = re.search(r"\*\*当前发布版本：([0-9]+\.[0-9]+\.[0-9]+)\*\*", readme)
if not pkg_match or not index_match or not readme_match:
    fail("release version surface missing")
versions = {pkg_match.group(1), index_match.group(1), readme_match.group(1)}
if len(versions) != 1:
    fail(f"README/pkg/release-index version mismatch: {sorted(versions)}")

part_count_match = re.search(r"^d parts (\d+)$", release_index, re.M)
parts = re.findall(r"^f (release/hxempirical-release\.b64\.\d{3})$", release_index, re.M)
if not part_count_match:
    fail("release index part count missing")
if int(part_count_match.group(1)) != len(parts):
    fail("release index Base64 part count mismatch")
for part in parts:
    if not (ROOT / part).is_file():
        fail(f"release Base64 part missing: {part}")

print(
    "HX_REPO_INVARIANTS_OK "
    f"version={pkg_match.group(1)} hxinstall_entrypoints=1 "
    f"base64_parts={len(parts)} target_string=1 required_smokes=3"
)
