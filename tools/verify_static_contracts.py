from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"HX_STATIC_VERIFY_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def local_words(source: str, name: str) -> list[str]:
    match = re.search(rf'^\s*local\s+{re.escape(name)}\s+"([^"]*)"', source, re.MULTILINE)
    if not match:
        fail(f"local macro not found: {name}")
    return match.group(1).split()


entry = read("hxempirical.ado")
dependency = read("hxdependency.ado")
registry = read("hxregistry.ado")
readme = read("README.md")
java = read("src/main/java/com/hexie/stata/HxWorkbench.java")

# doctor: the declared total must match the ado list plus the JAR and classic dlg.
core_match = re.search(r'local core\s+"([^"]+)"', entry)
total_match = re.search(r"local core_total\s+(\d+)", entry)
if not core_match or not total_match:
    fail("doctor core declaration not found")
core_components = core_match.group(1).split()
expected_total = len(core_components) + 2
if int(total_match.group(1)) != expected_total:
    fail(f"doctor total mismatch: declared={total_match.group(1)} expected={expected_total}")

# oneclick package knowledge remains correct for compatibility checks.
oneclick_packages = re.search(r'if\s+.+target.+==\s+"oneclick"\s+local packages\s+"([^"]+)"', dependency)
if not oneclick_packages or oneclick_packages.group(1).split() != ["tuples", "oneclick"]:
    fail("oneclick dependency chain must be exactly: tuples oneclick")
if "which tuples" not in dependency:
    fail("oneclick installation must verify tuples after installation")
if "作者扩展；需按作者说明手动安装" not in dependency:
    fail("oneclick_robustness must be identified as a manually installed author extension")

# Historical source notes remain documented, while current UI policy is manual-only.
for needle in (
    "`oneclick` 通过 SSC 安装，且依赖 `tuples`",
    "`oneclick_robustness` 按作者扩展处理",
    "未配置经过验证的 SSC 自动安装源",
):
    if needle not in readme:
        fail(f"README dependency/source note missing: {needle}")

# UI must never install external commands on behalf of the user.
if "hxdependency install" in java:
    fail("Java UI still contains automatic external-command installation")
if "当前没有安装 oneclick。现在从 SSC 安装吗？" in java:
    fail("OneClick auto-install prompt still present")
for needle in (
    "已安装外部命令",
    "sysdir_plus",
    "sysdir_personal",
    "sysdir_oldplace",
    "Files.walk",
    "quietly which",
    "本页只扫描和统计，不负责安装",
    "工作台不会自动安装第三方命令",
    "commitSpreadsheetCellEdit",
    "spreadsheetExpressionForInput",
):
    if needle not in java:
        fail(f"Java manual-install/spreadsheet contract missing: {needle}")
if "工作台只检测是否已安装，不再自动安装" not in readme:
    fail("README current external-command policy is not manual-only")
if "hxempirical 不再自动安装第三方命令" not in entry:
    fail("public hxempirical install compatibility path must not install packages")

# Parse the registry structure rather than relying on the first foreach in the file.
stats_cmds = set(local_words(registry, "stats_cmds"))
graph_cmds = set(local_words(registry, "graph_cmds"))
did_cmds = set(local_words(registry, "did_cmds"))

catalog_loop = re.search(
    r'local\s+all_cmds\s+""\s*\n\s*foreach\s+cmd\s+in\s+([^\n]+?)\s*\{',
    registry,
    re.MULTILINE,
)
if not catalog_loop:
    fail("public all_cmds catalog loop not found")
catalog_groups = catalog_loop.group(1).split()
if "`did_cmds'" in catalog_groups or any("did_cmds" in token for token in catalog_groups):
    fail("legacy did_cmds leaked into the public command catalog")

# Compatibility paths remain present, but only event_plot is public through Graph.
for legacy in ("did_builder", "did_trends", "event_plot"):
    if legacy not in did_cmds:
        fail(f"legacy DID compatibility command missing: {legacy}")
for hidden in ("did_builder", "did_trends"):
    if hidden in stats_cmds or hidden in graph_cmds:
        fail(f"legacy DID helper leaked into a public command group: {hidden}")
if "event_plot" not in graph_cmds:
    fail("event_plot must remain public through the Graph catalog")
for official in ("didregress", "xtdidregress"):
    if official not in stats_cmds:
        fail(f"official DID command missing from Statistics catalog: {official}")

print(
    "HX_STATIC_VERIFY_OK "
    f"doctor={expected_total}/{expected_total} "
    "oneclick=tuples+oneclick "
    "oneclick_robustness=manual-author-extension "
    "ui_external_manual_only=1 external_user_ado_scan=1 spreadsheet_editable=1 "
    "legacy_did_hidden=1 event_plot_graph=1 official_did_stats=1 docs_source_split=1"
)
