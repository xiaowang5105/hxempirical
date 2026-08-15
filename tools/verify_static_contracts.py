from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"HX_STATIC_VERIFY_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


entry = read("hxempirical.ado")
dependency = read("hxdependency.ado")
registry = read("hxregistry.ado")
readme = read("README.md")

# doctor: the declared total must match the ado list plus the JAR and classic dlg.
core_match = re.search(r'local core\s+"([^"]+)"', entry)
total_match = re.search(r"local core_total\s+(\d+)", entry)
if not core_match or not total_match:
    fail("doctor core declaration not found")
core_components = core_match.group(1).split()
expected_total = len(core_components) + 2
if int(total_match.group(1)) != expected_total:
    fail(f"doctor total mismatch: declared={total_match.group(1)} expected={expected_total}")

# oneclick: tuples is a required dependency and must be installed before oneclick.
if 'if `"`target\'"\' == "oneclick" local packages "tuples oneclick"' not in dependency:
    fail("oneclick dependency chain must include tuples before oneclick")
if "which tuples" not in dependency:
    fail("oneclick installation must verify tuples after installation")

# Legacy HX DID helpers stay callable for compatibility, but must not be public search entries.
public_loop = re.search(r"foreach cmd in ([^\n]+) \{", registry)
if not public_loop:
    fail("public command catalog loop not found")
if "did_cmds" in public_loop.group(1):
    fail("legacy did_cmds leaked into the public command catalog")
for official in ("didregress", "xtdidregress"):
    if official not in registry:
        fail(f"official DID command missing: {official}")

# Documentation must distinguish the verified SSC OneClick package from the manual robustness extension.
for needle in (
    "`oneclick`：SSC",
    "`oneclick_robustness`：作者扩展，需按作者说明手动安装",
):
    if needle not in readme:
        fail(f"README dependency/source note missing: {needle}")

print(
    "HX_STATIC_VERIFY_OK "
    f"doctor={expected_total}/{expected_total} "
    "oneclick=tuples+oneclick "
    "legacy_did_hidden=1 docs_source_split=1"
)
