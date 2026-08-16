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
help_text = read("hxempirical.sthlp")
install_doc = read("INSTALL.md")
launcher = read("hxinstall.do")
pkg = read("hxempirical.pkg")
java = read("src/main/java/com/hexie/stata/HxWorkbench.java")
semantics = read("hxsemantics.ado")

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

# The public launcher must load the downloaded installer core silently.
# Using `noisily do` echoes the entire ~580-line installer into Results.
if "capture noisily do" in launcher:
    fail("public hxinstall.do still echoes the installer core into Results")
if "capture quietly do" not in launcher:
    fail("public hxinstall.do does not load the installer core quietly")

# User-ado discovery must not execute one Stata `which` call per scanned file.
discovery_start = java.find("private List<String> discoverInstalledExternalCommands")
discovery_end = java.find("return new ArrayList<>(installed);", discovery_start)
if discovery_start < 0 or discovery_end < 0:
    fail("external discovery method not found")
discovery_block = java[discovery_start:discovery_end]
if discovery_block.count("quietly which") != 1:
    fail("external discovery must use which only for the curated fast-path, not once per discovered ado file")
if "for (String command : discovered)" not in discovery_block:
    fail("external discovery loop missing")

# Current user-facing docs must not advertise the removed auto-install behavior.
for stale in (
    "can be installed after user confirmation",
    "installation is offered only",
    "hxempirical install reghdfe",
    "can be installed from SSC on request",
):
    if stale in help_text:
        fail(f"help still advertises removed auto-install behavior: {stale}")
if "hxempirical 只检测和展示，不负责安装" not in install_doc:
    fail("INSTALL.md must state that external commands are user-installed")
version_match = re.search(r"^d Version ([0-9]+\.[0-9]+\.[0-9]+)$", pkg, re.MULTILINE)
if not version_match:
    fail("package version not found")
current_version = version_match.group(1)
if f"package version {current_version}." not in help_text:
    fail("help author/footer version is stale")

# net install and the transactional installer must share one standard h/ layout.
for system_file in (
    "hxtoolbox_v2.dlg",
    "hxworkbench.jar",
    "hx_nlswork.dta",
    "hx_grunfeld.dta",
    "hx_union.dta",
):
    if f"F {system_file}" not in pkg:
        fail(f"required system file is not marked with uppercase F: {system_file}")
if "local personal_h" not in read("hxinstaller.ado") or "local target `\"`personal_h'\"'" not in read("hxinstaller.ado"):
    fail("transactional installer does not target PERSONAL/h")
if "& !`legacy_present'" not in read("hxinstaller.ado"):
    fail("same-version fast path can skip legacy PERSONAL-root cleanup")
if "legacy_root'hxworkbench.jar" not in read("hxinstaller.ado"):
    fail("legacy JAR shadow is not detected")
for needle in (
    "legacy_root",
    "旧 PERSONAL 根目录文件仍在遮挡",
    "Pre-1.5.10 custom installs wrote managed files directly in PERSONAL",
):
    if needle not in read("hxinstaller.ado"):
        fail(f"legacy PERSONAL-root migration guard missing: {needle}")
if "x[0].lower() == \"f\"" not in read("tools/verify_release.py"):
    fail("release verifier does not include uppercase F package entries")

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

# Catalog correctness: Stata ERM has eregress/eintreg/eprobit/eoprobit; epoisson is not a public command.
if (
    "epoisson" in stats_cmds
    or re.search(r"(?<![A-Za-z0-9_])epoisson(?![A-Za-z0-9_])", registry)
    or re.search(r"(?<![A-Za-z0-9_])epoisson(?![A-Za-z0-9_])", semantics)
):
    fail("nonexistent epoisson leaked into Statistics catalog or semantics")
for official in ("eregress", "eintreg", "eprobit", "eoprobit"):
    if official not in stats_cmds:
        fail(f"official extended-regression command missing: {official}")

lasso_official = {
    "lasso", "elasticnet", "sqrtlasso",
    "poregress", "pologit", "popoisson", "poivregress",
    "dsregress", "dslogit", "dspoisson",
    "xporegress", "xpologit", "xpopoisson", "xpoivregress",
}
missing_lasso = sorted(lasso_official - stats_cmds)
if missing_lasso:
    fail("official Lasso commands missing from Statistics catalog: " + ", ".join(missing_lasso))
if "telasso" not in stats_cmds:
    fail("official telasso treatment-effects command missing from Statistics catalog")
for survey_cmd in ("svyset", "svydescribe", "svy"):
    if survey_cmd not in stats_cmds:
        fail(f"survey workflow command missing: {survey_cmd}")
exact_core = {"exlogistic", "expoisson", "bitest", "bitesti", "ksmirnov", "symmetry", "tetrachoric", "tabi"}
missing_exact = sorted(exact_core - stats_cmds)
if missing_exact:
    fail("exact-statistics commands missing: " + ", ".join(missing_exact))
for epi_cmd in ("cc", "cs", "ir", "mcc", "dstdize"):
    if epi_cmd not in stats_cmds:
        fail(f"epidemiology workflow command missing: {epi_cmd}")
for needle in (
    'exlogistic response treatment gender hypertension',
    'bitest outcome = .5',
    'mcc smoke1 smoke0',
    'dstdize deaths pop age_group, by(state)',
):
    if needle not in semantics:
        fail(f"exact/epidemiology semantic contract missing: {needle}")

multivariate_core = {
    "alpha", "factor", "pca", "canon", "ca", "candisc", "hotelling", "manova", "mvreg",
    "mca", "mds", "mdslong", "mdsmat", "mvtest", "procrustes", "discrim", "cluster",
}
missing_mv = sorted(multivariate_core - stats_cmds)
if missing_mv:
    fail("multivariate core commands missing: " + ", ".join(missing_mv))
if "cca" in stats_cmds or re.search(r"(?<![A-Za-z0-9_])cca(?![A-Za-z0-9_])", registry):
    fail("nonofficial cca token leaked into official multivariate catalog")
for needle in (
    'alpha item1-item10',
    'candisc x1 x2 x3, group(group)',
    'mvtest normality x1 x2 x3',
):
    if needle not in semantics:
        fail(f"multivariate semantic contract missing: {needle}")
for needle in (
    'svyset psu [pweight=finalwgt], strata(strata)',
    'svydescribe',
    'svy: mean weight',
):
    if needle not in semantics:
        fail(f"survey workflow semantic contract missing: {needle}")
causal_core = {"teffects", "eteffects", "etregress", "etpoisson", "stteffects"}
missing_causal = sorted(causal_core - stats_cmds)
if missing_causal:
    fail("official treatment-effects commands missing: " + ", ".join(missing_causal))
for stata18_cmd in ("mediate", "hdidregress", "xthdidregress"):
    if stata18_cmd not in stats_cmds:
        fail(f"Stata 18 causal command missing: {stata18_cmd}")
for needle in (
    'eteffects (wage tenure c.age##c.age) (college c.age##c.age i.pcollege)',
    'stteffects ra (age exercise diet education) (smoke)',
    'mediate (wellbeing, logit) (bonotonin, logit) (exercise)',
    'hdidregress aipw (bmi medu i.girl i.sports) (hhabit parksd), group(schools) time(year)',
    'xthdidregress ra (registered best) (movie), group(breed)',
):
    if needle not in semantics:
        fail(f"causal semantic contract missing: {needle}")
for needle in (
    '"xthdidregress"',
    'Arrays.asList("xtabond", "xtdpdsys", "xthdidregress")',
):
    if needle not in java:
        fail(f"xthdidregress low-barrier panel contract missing: {needle}")
for needle in (
    'sqrtlasso y x1-x1000',
    "Partialing-out Lasso",
    'telasso (y x1-x100) (treat w1-w100)',
    'gsem (alcohol truant weapon theft vandalism <-), logit lclass(C 3)',
):
    if needle not in semantics:
        fail(f"Lasso/LCA semantic contract missing: {needle}")
for needle in (
    'xtgee union age not_smsa, family(binomial) link(probit) corr(exchangeable)',
    'xtintreg ylower yupper x1 x2 x3',
    'xtfrontier y x1 x2, tvd',
    'xtabond y x1 x2, lags(1)',
    'xtdpdsys y x1 x2, lags(1)',
    'heckpoisson patents investment i.firmtype, select(applied = investment size i.firmtype)',
    'eprobit y x1, endogenous(x2 = x3 x4)',
):
    if needle not in semantics:
        fail(f"long-tail command semantic contract missing: {needle}")

print(
    "HX_STATIC_VERIFY_OK "
    f"doctor={expected_total}/{expected_total} "
    "oneclick=tuples+oneclick "
    "oneclick_robustness=manual-author-extension "
    "ui_external_manual_only=1 external_user_ado_scan=1 external_scan_fastpath=1 docs_manual_only=1 spreadsheet_editable=1 launcher_quiet=1 "
    "legacy_did_hidden=1 event_plot_graph=1 official_did_stats=1 epoisson_removed=1 longtail_semantics=1 lasso_catalog=1 lca_example=1 causal_catalog=1 xthdid_panel=1 survey_workflow=1 multivariate_catalog=1 exact_epi_catalog=1 docs_source_split=1"
)

# v1.5.11: Java launcher must prefer the JAR adjacent to the active hxtoolbox ado.
hxtoolbox_text = (root / "hxtoolbox.ado").read_text(encoding="utf-8")
adjacent_marker = "Prefer the JAR adjacent to the active hxtoolbox.ado"
if adjacent_marker not in hxtoolbox_text:
    fail("hxtoolbox must document/use adjacent JAR preference")
adjacent_pos = hxtoolbox_text.find("findfile hxtoolbox.ado")
generic_pos = hxtoolbox_text.find("findfile hxworkbench.jar")
if adjacent_pos < 0 or generic_pos < 0 or adjacent_pos > generic_pos:
    fail("hxtoolbox must resolve active ado directory before generic JAR findfile")

# v1.5.11: OneClick should remain task-first and keep raw syntax as secondary guidance.
java_text = (root / "src/main/java/com/hexie/stata/HxWorkbench.java").read_text(encoding="utf-8")
for needle in (
    "OneClick 控制变量筛选",
    "1　基础变量",
    "2　控制变量",
    "3　筛选与估计",
    "4　确认 Stata 命令",
    "候选控制变量",
    "固定控制变量",
    "外部命令由你自行安装",
):
    if needle not in java_text:
        fail("OneClick task-first UI contract missing: " + needle)

