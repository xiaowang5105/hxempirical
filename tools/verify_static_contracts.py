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
preview = read("hxpreview.ado")
resolve = read("hxresolve.ado")

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
if 'JButton var8 = new JButton("Excel / CSV 转换为 DTA")' not in java:
    fail("empty-data conversion action is missing")
if 'var8.addActionListener(var1x -> this.openCommandPage("hxconvert"));' not in java:
    fail("empty-data conversion action must route to the safe hxconvert workflow")
if 'var8.addActionListener(var1x -> this.openCommandPage("import"));' in java:
    fail("empty-data conversion action still routes to generic import instead of hxconvert")
for graph_cmd in ("graph_bar", "graph_dot", "graph_pie"):
    special_open = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "did_trends", "twoway").contains(var1)'
    if special_open not in java:
        fail("common graph commands are not routed to the special graph page")
if 'String nativeCommand = "graph_bar".equals(this.currentCommand) ? "graph bar" : "graph dot";' not in java:
    fail("bar/dot special graph preview builder missing")
if 'var1 = "graph pie" + (measure.isBlank() ? "" : " " + measure);' not in java:
    fail("pie special graph preview builder missing")
if '请选择饼图的分类变量 over()' not in java:
    fail("pie special graph validation missing")
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
data_cmds = set(local_words(registry, "data_cmds"))
core_data_management = {"describe", "codebook", "isid", "egen", "recode", "rename", "order", "label", "format", "compress", "sort", "gsort", "joinby"}
missing_core_data = sorted(core_data_management - data_cmds)
if missing_core_data:
    fail("core data-management commands missing: " + ", ".join(missing_core_data))
for needle in (
    'isid firm year',
    'egen firm_id = group(firm)',
    'recode age (0/17=1) (18/64=2) (65/max=3), gen(agegrp)',
    'rename oldname newname',
    'order firm year, first',
    'compress — 无损缩小数据存储',
    'gsort firm -sales',
    'joinby industry year using policy.dta',
):
    if needle not in semantics:
        fail(f"core data-management semantic contract missing: {needle}")

stats_cmds = set(local_words(registry, "stats_cmds"))
stats_methods = local_words(registry, "stats_methods")
if "样本选择模型" in stats_methods:
    fail("duplicate sample-selection method leaked into public Statistics navigation")
if "选择模型" not in stats_methods:
    fail("public Selection models method missing")
if 'local view "stset stcox streg stintreg"' not in registry:
    fail("survival navigation must start with the common declaration/estimation workflow")
if 'local view "var varsoc vargranger varlmar varnorm varstable irf"' not in registry:
    fail("multivariate time-series navigation must start with the routine VAR workflow")
if 'if c(stata_version) >= 17 local view "didregress xtdidregress"' not in registry:
    fail("Stata 17+ causal navigation must surface DID estimators first")
if '"更改方案/大小", "graph_scheme") local view "set"' not in registry:
    fail("Graphics scheme/size navigation must route to the real Stata set command")
if 'local title "set — 设置默认图形方案"' not in semantics:
    fail("set must have dedicated graphics-scheme semantics")
if 'local title "graph — 管理、保存与输出图形"' not in semantics:
    fail("graph management must have dedicated semantics")
if 'local view "use import export save"' not in registry:
    fail("Data import/convert navigation must surface native Stata I/O commands")
if 'local data_cmds "hxconvert ' in registry:
    fail("HX converter must not occupy the public native Data command catalog")
if 'local workflow_cmds "hxconvert oneclick oneclick_robustness"' not in registry:
    fail("HX converter must remain available in the Workflow catalog")
for native_io in ("use", "import", "export", "save"):
    if f'local title "{native_io} —' not in semantics:
        fail(f"native Data I/O semantics missing: {native_io}")
data_validation_reorg = {"assert", "count", "compare", "clonevar", "split", "expand", "cross", "contract", "fillin", "stack", "xpose", "frame", "frames", "frlink", "frget"}
missing_data_validation_reorg = sorted(data_validation_reorg - data_cmds)
if missing_data_validation_reorg:
    fail("data validation/reorganization commands missing: " + ", ".join(missing_data_validation_reorg))
for data_cmd in sorted(data_validation_reorg):
    if f'local title "{data_cmd} —' not in semantics:
        fail(f"data validation/reorganization semantics missing: {data_cmd}")
graph_cmds = set(local_words(registry, "graph_cmds"))
multivariate_graph_core = {"screeplot", "scoreplot", "loadingplot", "biplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay"}
missing_multivariate_graphs = sorted(multivariate_graph_core - graph_cmds)
if missing_multivariate_graphs:
    fail("multivariate graphics commands missing: " + ", ".join(missing_multivariate_graphs))
if 'local view "screeplot scoreplot loadingplot biplot cluster_dendrogram cabiplot caprojection mdsconfig mdsshepard procoverlay"' not in registry:
    fail("multivariate Graphics navigation must contain true graph commands")
if 'local view "pca factor cluster"' in registry:
    fail("multivariate Graphics navigation must not route to estimation commands")
for graph_cmd in sorted(multivariate_graph_core):
    native_title = "cluster dendrogram" if graph_cmd == "cluster_dendrogram" else graph_cmd
    if f'local title "{native_title} —' not in semantics:
        fail(f"multivariate graphics semantics missing: {graph_cmd}")
if 'cluster_dendrogram" local probe_cmd "cluster"' not in resolve:
    fail("cluster dendrogram UI alias must probe the native cluster command")
if 'else if ("cluster_dendrogram".equals(var1)) var1 = "cluster dendrogram";' not in java:
    fail("Java command preview must emit native cluster dendrogram syntax")
if 'local view "sts_graph"' not in registry:
    fail("Survival Graphics navigation must route to sts graph alias")
if 'cluster_dendrogram" local preview "cluster dendrogram"' not in preview:
    fail("cluster dendrogram preview alias missing")
if 'sts_graph" local preview "sts graph"' not in preview:
    fail("sts graph preview alias missing")
if 'local title "sts graph — 生存函数图"' not in semantics:
    fail("sts graph dedicated semantics missing")
for fallback_contract in (
    'return Collections.singletonList("graph_bar");',
    'return Collections.singletonList("graph_dot");',
    'return Collections.singletonList("graph_pie");',
    'return Collections.singletonList("graph_matrix");',
    'return Collections.singletonList("sts_graph");',
    'return Collections.singletonList("graph_combine");',
    'return Collections.singletonList("set");',
    'return Arrays.asList("use", "import", "export", "save");',
):
    if fallback_contract not in java:
        fail(f"Java fallback parity contract missing: {fallback_contract}")
if '"样本选择模型", "sample_selection") local view "heckman heckprobit heckoprobit heckpoisson"' not in registry:
    fail("legacy sample-selection navigation alias must remain resolvable")

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
java_invalid_tokens = ("epoisson", "cca")
for invalid in java_invalid_tokens:
    if re.search(rf"(?<![A-Za-z0-9_]){re.escape(invalid)}(?![A-Za-z0-9_])", java):
        fail(f"stale/nonexistent Java command token remains: {invalid}")
if 'Collections.singletonList("bma")' in java:
    fail("Java BMA fallback still points to retired bma alias")
for java_stats_contract in (
    'return Arrays.asList("irt", "irtgraph", "diflogistic", "difmh");',
    'return Arrays.asList("svyset", "svydescribe", "svy");',
    'return Arrays.asList("exlogistic", "expoisson", "bitest", "bitesti", "ksmirnov", "symmetry", "tetrachoric", "tabi");',
    'return Arrays.asList("power", "ciwidth");',
    'return Arrays.asList("bmaregress", "bmacoefsample", "bmagraph", "bmastats", "bmapredict");',
    'return Arrays.asList("dsge", "dsgenl");',
    'case "DSGE模型": return "dsge · dsgenl";',
    'case "DSGE模型":',
    'return "dsge";',
):
    if java_stats_contract not in java:
        fail(f"Java Statistics parity contract missing: {java_stats_contract}")
if '"内生协变量", "样本选择模型"' in java:
    fail("duplicate sample-selection method remains in Java public Statistics navigation")
if 'navigateTo("data", "导入与转换", "hxconvert")' in java:
    fail("public Java Data shortcuts must not bypass native Data I/O for hxconvert")
for data_entry_contract in (
    'case "导入与转换": return "use · import · export · save";',
    'case "数据检查": return "describe · codebook · isid · assert · duplicates";',
    'case "变量处理": return "generate · egen · recode · rename · encode";',
    'openCommandPage("import")',
    'browseMethod("data", "导入与转换")',
):
    if data_entry_contract not in java:
        fail(f"native Data entrypoint/card parity missing: {data_entry_contract}")
if 'return "打开、导入、导出和保存 Stata 或外部数据";' not in java:
    fail("Data import/export method summary still reflects the old HX converter")
if 'return "HX Workflow|数据转换";' not in java:
    fail("hxconvert command path must be labeled as HX Workflow")
for data_method_contract in (
    'Arrays.asList("use", "import", "export", "save").contains(var0)',
    'Arrays.asList("缺失值分析", "describe", "codebook", "isid", "assert", "count", "compare", "duplicates", "misstable").contains(var0)',
    'Arrays.asList("generate", "egen", "replace", "recode", "clonevar", "split", "rename", "order", "label", "format", "compress", "encode", "decode", "destring", "tostring", "winsor2").contains(var0)',
    'Arrays.asList("keep", "drop", "expand").contains(var0)',
    'Arrays.asList("merge", "append", "joinby", "cross", "frlink", "frget").contains(var0)',
    'Arrays.asList("reshape", "collapse", "contract", "fillin", "stack", "xpose", "sort", "gsort", "xtset", "tsset", "frame", "frames").contains(var0)',
):
    if data_method_contract not in java:
        fail(f"Java Data commandMethod parity missing: {data_method_contract}")
for official in ("didregress", "xtdidregress"):
    if official not in stats_cmds:
        fail(f"official DID command missing from Statistics catalog: {official}")

statistics_command_method_contracts = {
    "summarize": "统计|汇总，表格和假设检验",
    "regress": "统计|线性模型及相关",
    "logit": "统计|二元结果",
    "ologit": "统计|序数结果",
    "mlogit": "统计|分类结果",
    "poisson": "统计|计数结果",
    "fracreg": "统计|分数结果",
    "glm": "统计|广义线性模型",
    "heckman": "统计|选择模型",
    "arima": "统计|时间序列",
    "var": "统计|多元时间序列",
    "spregress": "统计|空间自回归模型",
    "xtreg": "统计|纵向/面板数据",
    "mixed": "统计|多层混合效应模型",
    "stcox": "统计|生存分析",
    "cc": "统计|流行病学及相关",
    "eregress": "统计|内生协变量",
    "teffects": "统计|因果推断/处理效应",
    "sem": "统计|结构方程模型(SEM)",
    "irt": "统计|项目反应理论(IRT)",
    "dsge": "统计|DSGE模型",
    "pca": "统计|多元分析",
    "svy": "统计|调查数据分析",
    "lasso": "统计|Lasso回归",
    "meta": "统计|Meta分析",
    "mi": "统计|多重插补",
    "npregress": "统计|非参数分析",
    "exlogistic": "统计|精确统计",
    "bootstrap": "统计|重抽样",
    "power": "统计|效能，精度和样品含量",
    "bayes": "统计|贝叶斯分析",
    "bmaregress": "统计|贝叶斯模型平均",
    "ivregress": "统计|工具变量与内生性",
    "margins": "统计|估计后分析",
}
command_method_scope = java[java.find('private static String commandMethod(String var0)'):java.find('private static String commandPath(String var0)')]
for command, method_label in statistics_command_method_contracts.items():
    if command not in command_method_scope or f'return "{method_label}";' not in command_method_scope:
        fail(f"Statistics commandMethod canonical classification missing: {command} -> {method_label}")
if 'return "回归模型|工具变量";' in command_method_scope:
    fail("native IV commands still use the legacy regression commandPath classification")
if 'return "后估计|系数检验";' in command_method_scope or 'return "后估计|预测边际";' in command_method_scope:
    fail("native postestimation commands still use legacy post commandPath labels")
graph_command_method_contracts = {
    "scatter": "图形|二维图(散点图，折线图等)",
    "graph_bar": "图形|条形图",
    "graph_dot": "图形|点图",
    "graph_pie": "图形|饼图",
    "histogram": "图形|直方图",
    "graph_box": "图形|箱线图",
    "twoway_contour": "图形|等高线图",
    "graph_matrix": "图形|散点图矩阵",
    "kdensity": "图形|平滑和密度",
    "rvfplot": "图形|回归诊断图",
    "tsline": "图形|时间序列图",
    "xtline": "图形|面板数据折线图",
    "sts_graph": "图形|生存分析图",
    "roctab": "图形|ROC分析",
    "screeplot": "图形|多元分析图",
    "cluster_dendrogram": "图形|多元分析图",
    "cchart": "图形|质量控制",
    "qnorm": "图形|更多统计图形",
    "marginsplot": "图形|更多统计图形",
    "graph_combine": "图形|图形组合",
    "graph": "图形|管理图形",
    "set": "图形|更改方案/大小",
}
for command, method_label in graph_command_method_contracts.items():
    if command not in command_method_scope or f'return "{method_label}";' not in command_method_scope:
        fail(f"Graphics commandMethod canonical classification missing: {command} -> {method_label}")
if 'return "图形|分布图";' in command_method_scope:
    fail("stale broad distribution commandPath label remains after specific Graphics classification")
graph_method_preview_contracts = (
    'case "生存分析图": return "sts graph";',
    'case "ROC分析": return "roctab · rocfit · roccomp · rocgold · rocreg";',
    'case "多元分析图": return "screeplot · scoreplot · loadingplot · biplot · cluster dendrogram";',
    'case "质量控制": return "cchart · pchart · rchart · xchart · shewhart · serrbar";',
    'case "更多统计图形": return "symplot · qnorm · qqplot · dotplot · sunflower · marginsplot · coefplot";',
    'case "管理图形": return "graph dir · graph display · graph save · graph export";',
    'case "更改方案/大小": return "set scheme";',
)
for preview_contract in graph_method_preview_contracts:
    if preview_contract not in java:
        fail(f"Graphics method-card preview parity missing: {preview_contract}")
if 'case "更多统计图形": return "marginsplot · 更多统计图形";' in java:
    fail("placeholder Graphics method preview remains")
if 'case "更改方案/大小": return "set scheme · graph set";' in java:
    fail("Graphics settings card advertises a route not present in its current command list")
graph_result_route_required = ("graph_bar", "graph_box", "twoway_contour", "sts_graph", "roctab", "screeplot", "cchart", "graph_combine")
route_start = java.find('"graph_bar", "graph_dot", "graph_pie", "graph_box", "twoway_contour", "graph_matrix"')
route_end = java.find('this.selectResultView("graph", true);', route_start)
if route_start < 0 or route_end < 0:
    fail("expanded Graphics result-routing block missing")
route_scope = java[route_start:route_end]
for graph_cmd in graph_result_route_required:
    if f'"{graph_cmd}"' not in route_scope:
        fail(f"Graphics command does not route to graph result view: {graph_cmd}")
if '"graph_box".equals(this.currentCommand) ? "graph box"' not in java:
    fail("graph_box Java help/native alias mapping missing")


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
if "nptrend" not in stats_cmds:
    fail("nptrend missing from nonparametric Statistics coverage")
for needle in (
    "npregress kernel y x1 x2",
    "npregress series output taxlevel rainfall i.irrigate",
    "nptrend relief, group(dose) carmitage",
    "nptrend exposure, group(group) jterpstra notable exact",
    "nptrend a, by(y)",
):
    if needle not in semantics:
        fail(f"nonparametric semantic contract missing: {needle}")
if 'if c(stata_version) >= 17 {' not in semantics:
    fail("nptrend version-aware semantic branch missing")

graph_aliases = {"graph_bar", "graph_dot", "graph_pie", "graph_box", "graph_matrix", "twoway_contour", "graph_combine"}
missing_graph_aliases = sorted(graph_aliases - graph_cmds)
if missing_graph_aliases:
    fail("Graphics multiword aliases missing: " + ", ".join(missing_graph_aliases))
for route in (
    '"条形图", "bar_graph") local view "graph_bar"',
    '"点图", "dot_graph") local view "graph_dot"',
    '"饼图", "pie_graph") local view "graph_pie"',
    '"等高线图", "contour_graph") local view "twoway_contour"',
    '"散点图矩阵", "matrix_graph") local view "graph_matrix"',
    '"图形组合", "graph_combine") local view "graph_combine"',
):
    if route not in registry:
        fail(f"Graphics native route missing: {route}")
quality_graphs = {"cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar"}
if quality_graphs - graph_cmds:
    fail("quality-control Graphics commands missing: " + ", ".join(sorted(quality_graphs - graph_cmds)))
distribution_graphs = {"symplot", "quantile", "qnorm", "pnorm", "qchi", "pchi", "qqplot", "gladder", "qladder", "dotplot", "spikeplot", "sunflower"}
if distribution_graphs - graph_cmds:
    fail("distribution diagnostic Graphics commands missing: " + ", ".join(sorted(distribution_graphs - graph_cmds)))
if "heatmap" in graph_cmds or "twoway_heatmap" in graph_cmds:
    fail("Stata 19 heatmap must not leak into the Stata 16-18 Graphics catalog")
preview_contracts = {
    "if \"`command'\" == \"graph_bar\" local preview \"graph bar\"",
    "if \"`command'\" == \"graph_dot\" local preview \"graph dot\"",
    "if \"`command'\" == \"graph_pie\" local preview \"graph pie\"",
    "if \"`command'\" == \"graph_box\" local preview \"graph box\"",
    "if \"`command'\" == \"graph_matrix\" local preview \"graph matrix\"",
    "if \"`command'\" == \"twoway_contour\" local preview \"twoway contour\"",
    "if \"`command'\" == \"graph_combine\" local preview \"graph combine\"",
}
for needle in preview_contracts:
    if needle not in preview:
        fail(f"native Graphics preview mapping missing: {needle}")
for needle in (
    "if strpos(\" graph_bar graph_dot graph_pie graph_box graph_matrix graph_combine \", \" `cmd' \") local probe_cmd \"graph\"",
    "else if \"`cmd'\" == \"twoway_contour\" local probe_cmd \"twoway\"",
):
    if needle not in resolve:
        fail(f"Graphics alias resolver probe missing: {needle}")
for alias, native in (
    ("graph_bar", "graph bar"), ("graph_dot", "graph dot"), ("graph_pie", "graph pie"),
    ("graph_matrix", "graph matrix"), ("twoway_contour", "twoway contour"), ("graph_combine", "graph combine"),
):
    if f'"{alias}".equals(var1)' not in java or f'var1 = "{native}"' not in java:
        fail(f"Java Help alias mapping missing: {alias} -> {native}")
for needle in (
    "graph bar heatdd cooldd, over(region) blabel(total)",
    "graph dot wage, over(occ)",
    "graph pie pop, over(region)",
    "graph box y, over(group)",
    "graph matrix mpg weight length",
    "twoway contour z y x",
    "graph combine gr1 gr2, cols(2)",
    "symplot price", "qnorm price", "qqplot weightd weightf", "spikeplot age", "sunflower mpg displ",
    "shewhart m1-m5, connect(l)", "serrbar mean se x",
):
    if needle not in semantics:
        fail(f"Graphics semantic contract missing: {needle}")

postestimation_core = {
    "test", "testparm", "testnl", "lincom", "nlcom", "contrast", "pwcompare", "predict", "predictnl", "margins",
    "lrtest", "hausman", "suest", "linktest", "estimates", "estat",
}
missing_post = sorted(postestimation_core - stats_cmds)
if missing_post:
    fail("postestimation command coverage missing: " + ", ".join(missing_post))
post_declared = set(local_words(registry, "post_cmds"))
missing_post_category = sorted(postestimation_core - post_declared)
if missing_post_category:
    fail("post command category missing: " + ", ".join(missing_post_category))
if "假设检验 组合与比较 预测与边际 模型管理与诊断" not in registry:
    fail("task-oriented postestimation method groups missing")
for needle in (
    "testparm i.group",
    "testnl (_b[x])^2 = 1",
    "nlcom (_b[x])^2",
    "contrast ar.agegroup, nowald effects",
    "pwcompare agegrp, effects mcompare(tukey)",
    "predictnl xb2 = predict(xb)^2, se(se_xb2)",
    "lrtest restricted unrestricted",
    "hausman fixed random",
    "suest model1 model2",
    "linktest",
    "estimates store model1",
    "estat ic",
):
    if needle not in semantics:
        fail(f"postestimation semantic contract missing: {needle}")
if "marginsplot" not in graph_cmds:
    fail("marginsplot must remain in Graphics while being reachable from postestimation")

bayesian_core = {"bayes", "bayesmh", "bayespredict", "bayesreps", "bayesstats", "bayesgraph", "bayestest"}
missing_bayes = sorted(bayesian_core - stats_cmds)
if missing_bayes:
    fail("Bayesian core command coverage missing: " + ", ".join(missing_bayes))
bayes17 = {"bayesvarstable", "bayesirf", "bayesfcast"}
missing_bayes17 = sorted(bayes17 - stats_cmds)
if missing_bayes17:
    fail("Stata 17 Bayesian VAR postestimation missing: " + ", ".join(missing_bayes17))
if "stintcox bayesvarstable bayesirf bayesfcast" not in registry:
    fail("Stata 17 Bayesian VAR commands missing from version gate")
bma18 = {"bmaregress", "bmacoefsample", "bmagraph", "bmastats", "bmapredict"}
missing_bma = sorted(bma18 - stats_cmds)
if missing_bma:
    fail("Stata 18 BMA workflow missing: " + ", ".join(missing_bma))
if "bmaregress bmacoefsample bmagraph bmastats bmapredict" not in registry:
    fail("Stata 18 BMA commands missing from version gate or method route")
if "bayesselect" in stats_cmds:
    fail("post-Stata-18 bayesselect must not leak into the Stata 16-18 catalog")
for needle in (
    "bayespredict pmean, mean",
    "bayesreps yrep*, nreps(10)",
    "bayesstats summary",
    "bayesgraph diagnostics {inflation:L1.ogap}",
    "bayestest model lag1 lag2 lag3",
    "bayesvarstable",
    "bayesirf create birf, set(birfex)",
    "bayesirf graph irf, impulse(fedfunds)",
    "bayesfcast compute f_, step(10)",
    "bayesfcast graph f_inflation f_ogap f_fedfunds",
    "bmacoefsample, rseed(18)",
    "bmagraph pmp",
    "bmastats pip",
    "bmapredict pmean, mean",
):
    if needle not in semantics:
        fail(f"Bayesian/BMA semantic contract missing: {needle}")

dsge_core = {"dsge", "dsgenl"}
missing_dsge = sorted(dsge_core - stats_cmds)
if missing_dsge:
    fail("DSGE command coverage missing: " + ", ".join(missing_dsge))
if "DSGE模型" not in registry:
    fail("DSGE method missing from Statistics navigation")
pk_core = {"pkexamine", "pksumm", "pkcross", "pkequiv", "pkcollapse", "pkshape"}
missing_pk = sorted(pk_core - stats_cmds)
if missing_pk:
    fail("pharmacokinetic command coverage missing: " + ", ".join(missing_pk))
if "pk" in stats_cmds:
    fail("umbrella help entry pk must not be exposed as an executable Statistics command")
for needle in (
    "dsge (p = {beta}*E(F.p) + {kappa}*y) (F.y = {rho}*y, state)",
    "observed(r p) unobserved(x) exostate(z u)",
    "pkexamine time concentration, graph",
    "pksumm id time conc",
    "pkcross y, param(3) id(idvar) sequence(seq) treatment(treat) period(period)",
    "pkequiv auc treat period sequence id, limit(0.1) notost noboot",
    "pkcollapse time conc1 conc2, id(id) stat(auc) keep(seq)",
    "pkshape id seq period1 period2, order(RT TR)",
):
    if needle not in semantics:
        fail(f"PK/DSGE semantic contract missing: {needle}")

irt_core = {"irt", "irtgraph", "diflogistic", "difmh"}
missing_irt = sorted(irt_core - stats_cmds)
if missing_irt:
    fail("IRT command coverage missing: " + ", ".join(missing_irt))
for needle in (
    "irt 2pl item1-item10",
    "irt grm item1-item10, group(urban)",
    "irtgraph icc",
    "irtgraph tif",
    "fmm 2, lcprob(z1 z2): poisson y x1 x2",
    "gsem (alcohol truant weapon theft vandalism <-), logit lclass(C 3)",
):
    if needle not in semantics:
        fail(f"latent/IRT semantic contract missing: {needle}")
# SEM/LCA/FMM are intentionally represented by their real Stata entry points.
for fake in ("lca", "latentclass"):
    if fake in stats_cmds:
        fail(f"fake latent-class command leaked into catalog: {fake}")

survival_workflow_core = {
    "ctset", "cttost", "ltable", "snapspan", "stset", "stdescribe", "stsum", "stci", "stcurve", "stbase",
    "stfill", "stgen", "stsplit", "stvary", "sttocc", "sttoct", "sts", "stcox", "streg", "stintreg", "stintcox",
    "stcrreg", "stir", "strate", "stptime", "stmh", "stmc",
}
missing_survival_workflow = sorted(survival_workflow_core - stats_cmds)
if missing_survival_workflow:
    fail("survival workflow commands missing: " + ", ".join(missing_survival_workflow))
if "stmgintcox" in stats_cmds:
    fail("Stata 19 stmgintcox must not leak into the Stata 16-18 catalog")
for needle in (
    "ctset time failures lost entered, by(group)",
    "cttost, clear",
    "ltable studytime died, failure graph",
    "stdescribe",
    "stsum, by(group)",
    "stci, by(group)",
    "stcurve, survival",
    "stsplit ageband, at(20(5)80)",
    "stvary x1 x2",
    "sttocc, match(sex agegroup) number(4)",
    "stir exposed",
    "strate group, per(1000)",
    "stptime, by(group) per(1000)",
):
    if needle not in semantics:
        fail(f"survival workflow semantic contract missing: {needle}")

time_series_core = {
    "arima", "arfima", "newey", "prais", "arch", "ucm", "mswitch", "threshold", "dfgls", "dfuller", "pperron",
    "corrgram", "cumsp", "pergram", "wntestb", "wntestq", "psdensity", "rolling", "forecast", "tsappend", "tsfill",
    "tsfilter", "tsreport", "tssmooth",
}
missing_ts = sorted(time_series_core - stats_cmds)
if missing_ts:
    fail("univariate time-series commands missing: " + ", ".join(missing_ts))
multivariate_ts_core = {
    "var", "svar", "vec", "varbasic", "varsoc", "vargranger", "varlmar", "varnorm", "varstable", "varwle",
    "vecrank", "veclmar", "vecnorm", "vecstable", "irf", "mgarch", "dfactor", "sspace", "xcorr",
}
missing_mvts = sorted(multivariate_ts_core - stats_cmds)
if missing_mvts:
    fail("multivariate time-series commands missing: " + ", ".join(missing_mvts))
for stata18_ts in ("arimasoc", "arfimasoc", "lpirf"):
    if stata18_ts not in stats_cmds:
        fail(f"Stata 18 time-series command missing: {stata18_ts}")
if "arimasoc arfimasoc lpirf" not in registry:
    fail("Stata 18 time-series version gate missing arimasoc/arfimasoc/lpirf")
for needle in (
    'arfima y, ar(1) ma(1)',
    "ogap, maxar(4) maxma(3)",
    "mswitch dr fedfunds",
    "threshold pollution, threshvar(hour) regionvars(oldbus newbus car)",
    "dfgls y",
    "检验 y 是否可视为白噪声",
    "rolling _b, window(20) saving(roll, replace): regress y x",
    "forecast create model",
    "tsappend, add(12)",
    "tsfilter hp y_cycle = y, smooth(1600)",
    "tssmooth ma y_ma = y, window(2 1 2)",
    "vecrank y1 y2",
    "lpirf indpro inflation, lags(1/12) exog(L(0/12).money_shock)",
    "mgarch dcc (toyota honda =), arch(1) garch(1) distribution(t)",
    "dfactor (D.(ipman income hours unemp) =, noconstant) (f=, ar(1/2)), nolog",
    "xcorr y x",
):
    if needle not in semantics:
        fail(f"time-series semantic contract missing: {needle}")

panel_round2_core = {
    "xteregress", "xteprobit", "xteoprobit", "xteintreg", "xtheckman", "xthtaylor",
    "xtdpd", "xtgls", "xtunitroot", "xtcointtest", "xtdescribe", "xtsum", "xttab", "xtdata",
}
missing_panel_round2 = sorted(panel_round2_core - stats_cmds)
if missing_panel_round2:
    fail("panel-data round-2 commands missing: " + ", ".join(missing_panel_round2))
for needle in (
    'xteregress y x1, endogenous(x2 = x3 x4)',
    'xteprobit y x1, endogenous(x2 = x3 x4)',
    'xteoprobit y x1, endogenous(x2 = x3 x4)',
    'xteintreg ylower yupper x1, endogenous(x2 = x3 x4)',
    'xtheckman income c.age##c.age i.training#(c.exp##c.exp), select(working = age exp i.region i.training)',
    'xthtaylor y x1 x2 z1, endog(x2)',
    'xtdpd L(0/1).y x, div(x) dgmmiv(y)',
    'xtgls y x1 x2, panels(heteroskedastic) corr(ar1)',
    'xtunitroot ips hprice',
    'xtcointtest kao hprice aprice nprice',
    'xtdescribe',
    'xtsum hours',
    'xttab msp',
    'xtdata y x1 x2, fe clear',
):
    if needle not in semantics:
        fail(f"panel round-2 semantic contract missing: {needle}")

panel_extension_core = {"xtologit", "xtivreg", "xtpcse", "xtregar", "xtrc", "xtstreg"}
missing_panel_extensions = sorted(panel_extension_core - stats_cmds)
if missing_panel_extensions:
    fail("panel-data main commands missing: " + ", ".join(missing_panel_extensions))
mixed_extension_core = {"mecloglog", "meintreg", "menl"}
missing_mixed_extensions = sorted(mixed_extension_core - stats_cmds)
if missing_mixed_extensions:
    fail("mixed-effects main commands missing: " + ", ".join(missing_mixed_extensions))
for survival_cmd in ("stintreg", "stintcox"):
    if survival_cmd not in stats_cmds:
        fail(f"interval-censored survival command missing: {survival_cmd}")
if "foreach cmd in didregress xtdidregress telasso ziologit xtmlogit stintcox" not in registry:
    fail("Stata 17 version gate must include xtmlogit and stintcox")
for needle in (
    'xtivreg y x1 (x2 = z1 z2), fe',
    'xtpcse y x1 x2, correlation(ar1) pairwise',
    'xtregar y x1 x2, fe',
    'xtrc y x1 x2',
    'xtstreg age female, distribution(weibull)',
    'mecloglog y x1 x2 || school:',
    'meintreg ylower yupper x1 x2 x3 || id:',
    'menl weight = ({b1}+{U[id]})/(1+exp(-(time-{b2})/{b3}))',
    'stintreg i.stage, interval(ltime rtime) distribution(weibull)',
    'stintcox age_mean i.male i.needle i.inject i.jail, interval(ltime rtime)',
):
    if needle not in semantics:
        fail(f"panel/mixed/survival semantic contract missing: {needle}")
panel_method_start = java.find("private static boolean isGenericPanelEstimator")
panel_method_end = java.find("private static boolean isGenericPanelTimeRequired", panel_method_start)
if panel_method_start < 0 or panel_method_end < 0:
    fail("Java generic panel estimator method missing")
panel_method_block = java[panel_method_start:panel_method_end]
for panel_cmd in panel_extension_core | panel_round2_core:
    if f'"{panel_cmd}"' not in panel_method_block:
        fail(f"Java panel auto-xtset routing missing: {panel_cmd}")
for time_required in ("xtdpd", "xtunitroot", "xtcointtest"):
    if f'"{time_required}"' not in java[java.find("private static boolean isGenericPanelTimeRequired"):java.find("private JPanel genericCardBody", java.find("private static boolean isGenericPanelTimeRequired"))]:
        fail(f"Java panel time-required routing missing: {time_required}")

iv_core = {"ivregress", "ivprobit", "ivtobit", "ivpoisson"}
missing_iv = sorted(iv_core - stats_cmds)
if missing_iv:
    fail("instrumental-variable commands missing: " + ", ".join(missing_iv))
for stata18_iv in ("ivfprobit", "ivqregress"):
    if stata18_iv not in stats_cmds:
        fail(f"Stata 18 IV command missing: {stata18_iv}")
if "ivfprobit ivqregress" not in registry or "gsdesign ivfprobit ivqregress" not in registry:
    fail("Stata 18 IV version gate or routing missing")
for needle in (
    'betareg gini i.rural i.democracy i.colony, nolog',
    '0<Y<1',
    'ivprobit y x1 (x2 = z1 z2)',
    'ivtobit y x1 (x2 = z1 z2), ll(0)',
    'ivpoisson gmm accidents x1 x2 (horsepower = x3 x4)',
    'ivfprobit prate c.ltotemp##c.ltotemp i.sole (mrate = c.age##c.age)',
    'ivqregress iqr assets (i.p401k = i.e401k)',
):
    if needle not in semantics:
        fail(f"IV/fractional semantic contract missing: {needle}")

count_core = {"poisson", "nbreg", "gnbreg", "cpoisson", "zip", "zinb", "tpoisson", "tnbreg"}
missing_count = sorted(count_core - stats_cmds)
if missing_count:
    fail("count outcome commands missing: " + ", ".join(missing_count))
if "churdle" not in stats_cmds:
    fail("Cragg hurdle regression missing from Statistics catalog")
for needle in (
    'gnbreg y x1 x2, lnalpha(z1 z2)',
    'cpoisson accidents i.past i.parent i.ntickets, ul(3) irr',
    'churdle linear money dating teenager nkids, select(newborn hours distance weekends) ll(0)',
):
    if needle not in semantics:
        fail(f"count/hurdle semantic contract missing: {needle}")

binary_core = {"logit", "logistic", "binreg", "probit", "biprobit", "hetprobit", "scobit", "cloglog"}
missing_binary = sorted(binary_core - stats_cmds)
if missing_binary:
    fail("binary outcome commands missing: " + ", ".join(missing_binary))
ordinal_core = {"ologit", "oprobit", "hetoprobit", "zioprobit", "ziologit"}
missing_ordinal = sorted(ordinal_core - stats_cmds)
if missing_ordinal:
    fail("ordinal outcome commands missing: " + ", ".join(missing_ordinal))
choice_core = {
    "mlogit", "mprobit", "clogit", "slogit", "cmset", "cmsummarize", "cmchoiceset", "cmtab", "cmsample",
    "cmclogit", "cmmixlogit", "cmxtmixlogit", "cmmprobit", "cmroprobit", "cmrologit", "nlogit",
}
missing_choice = sorted(choice_core - stats_cmds)
if missing_choice:
    fail("categorical/choice commands missing: " + ", ".join(missing_choice))
if 'foreach cmd in didregress xtdidregress telasso ziologit' not in registry:
    fail("Stata 17 ziologit version gate missing")
for needle in (
    'biprobit (private years) (vote logptax loginc)',
    'hetoprobit health age bmi i.exercise, het(age)',
    'ziologit tobacco education income i.female, inflate(income education i.parent)',
    'zioprobit tobacco income i.female age, inflate(income i.female age i.parent i.religion)',
    'cmset id travelmode',
    'cmclogit chosen time, casevars(income partysize)',
    'cmmixlogit choice mfee, random(price) casevars(traffic)',
    'cmxtmixlogit choice trcost, random(trtime) casevars(age income)',
    'nlogit chosen cost distance rating || type: income kids',
):
    if needle not in semantics:
        fail(f"binary/ordinal/choice semantic contract missing: {needle}")

linear_related_core = {
    "regress", "areg", "cnsreg", "rreg", "hetregress", "qreg", "iqreg", "bsqreg", "sqreg",
    "vwls", "eivreg", "intreg", "tobit", "truncreg", "boxcox", "fp", "nl", "nlsur", "gmm",
    "sureg", "reg3", "mvreg", "frontier", "correlate", "pwcorr",
}
missing_linear = sorted(linear_related_core - stats_cmds)
if missing_linear:
    fail("linear-related commands missing: " + ", ".join(missing_linear))
for needle in (
    'hetregress y x1 x2, het(z1 z2)',
    'sqreg y x1 x2, quantile(.25 .5 .75) reps(100)',
    'intreg ylower yupper x1 x2',
    'tobit y x1 x2, ll(0)',
    'truncreg y x1 x2, ll(0)',
    'fp <age>, scale: regress y x <age>',
    'nl (y = {b0=1}*(1-exp(-{b1=.1}*x)))',
    'nlsur (y1 = {a1}*x1 + {a2}*x2) (y2 = {b1}*x1 + {b2}*x2)',
    'gmm (y - {b0} - {b1}*x), instruments(z x)',
    'reg3 (y1 x1 x2) (y2 y1 z1), 3sls',
    'frontier lncost lnout lnp_l lnp_k, cost',
):
    if needle not in semantics:
        fail(f"linear-related semantic contract missing: {needle}")

summary_core = {"summarize", "ameans", "centile", "ci", "mean", "proportion", "ratio", "total", "tabstat", "tabulate", "table", "dtable"}
missing_summary = sorted(summary_core - stats_cmds)
if missing_summary:
    fail("summary/table commands missing: " + ", ".join(missing_summary))
power_core = {"power", "ciwidth", "gsbounds", "gsdesign"}
missing_power = sorted(power_core - stats_cmds)
if missing_power:
    fail("power/precision commands missing: " + ", ".join(missing_power))
for gated in ("dtable", "gsbounds", "gsdesign"):
    if gated not in stats_cmds:
        fail(f"Stata 18 summary/power command missing: {gated}")
if "dtable gsbounds gsdesign" not in registry:
    fail("Stata 18 summary/power version gate missing")
for needle in (
    'centile y, centile(25 50 75)',
    'ci means y',
    'ratio sales/cost',
    'dtable price weight mpg i.rep78',
    'ciwidth twomeans, width(6) sd(5) probwidth(.96)',
    'gsbounds, efficacy(obfleming) futility(obfleming) nlooks(5) power(.9) alpha(.05)',
    'gsdesign twomeans 5.5 6.5',
    'meta set es se',
    'permute treatment _b[treatment], reps(500): regress y treatment x1 x2',
    'statsby mean=r(mean) sd=r(sd), by(group): summarize y',
):
    if needle not in semantics:
        fail(f"summary/power/resampling semantic contract missing: {needle}")

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
    'Arrays.asList("xtabond", "xtdpdsys", "xtdpd", "xtunitroot", "xtcointtest", "xthdidregress")',
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
    "legacy_did_hidden=1 event_plot_graph=1 official_did_stats=1 epoisson_removed=1 longtail_semantics=1 lasso_catalog=1 lca_example=1 causal_catalog=1 xthdid_panel=1 survey_workflow=1 multivariate_catalog=1 exact_epi_catalog=1 linear_catalog=1 discrete_choice_catalog=1 count_catalog=1 hurdle_model=1 iv_catalog=1 fractional_semantics=1 summary_catalog=1 power_precision=1 resampling_examples=1 meta_workflow=1 docs_source_split=1"
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

