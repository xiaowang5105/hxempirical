from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
java_path = root / "src/main/java/com/hexie/stata/HxWorkbench.java"
static_path = root / "tools/verify_static_contracts.py"
java = java_path.read_text(encoding="utf-8")
static = static_path.read_text(encoding="utf-8")


def replace_exact(text, old, new, expected=1, label="anchor"):
    count = text.count(old)
    if count != expected:
        print(f"HX_ROCREGPLOT_PATCH_FAIL {label}: expected {expected}, found {count}", file=sys.stderr)
        raise SystemExit(1)
    return text.replace(old, new)

# rocregplot is a graph-producing postestimation command and belongs in the structured graph workspace.
java = replace_exact(
    java,
    '"roctab", "roccomp", "rocgold", "screeplot"',
    '"roctab", "roccomp", "rocgold", "rocregplot", "screeplot"',
    expected=2,
    label="special graph route lists",
)

# It consumes the current rocreg result; do not expose dataset if/in controls as if this were a raw-data graph.
java = replace_exact(
    java,
    '"cchart", "pchart", "marginsplot", "coefplot", "event_plot"',
    '"cchart", "pchart", "rocregplot", "marginsplot", "coefplot", "event_plot"',
    label="includeIf exclusion",
)

# Give rocregplot a result-based page instead of the generic command_body form.
page_anchor = '''         } else if ("biplot".equals(var1)) {
            this.commandTitle.setText("biplot · 多元双标图");'''
page_block = '''         } else if ("rocregplot".equals(var1)) {
            this.commandTitle.setText("rocregplot · ROC regression 结果图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> rocregplot, at1(currage=40) at2(currage=50)</html>");
            this.insightArea.setText("这是 rocreg 的后估计图。先成功运行 rocreg，本页直接使用当前 ROC regression 结果绘制 marginal 或 covariate-specific ROC curves。\\n\\nat1()/at2()/... 用于比较协变量取值下的 ROC 曲线；多个 classifier、置信区间、plot#opts()、legend、标题和尺寸继续使用 rocregplot 原生 options。\\n\\n这里不重新选择 refvar/classvar，也不把当前数据变量误当成新的 ROC 输入。");
            this.syntaxArea.setText("rocregplot [, options]");
            coreTitle = "上一条 rocreg 结果";
            coreSubtitle = "直接复用当前 rocreg estimation result；需要比较协变量情景时在图形设置中填写 at#() 等原生 options。";
         } else if ("biplot".equals(var1)) {
            this.commandTitle.setText("biplot · 多元双标图");'''
java = replace_exact(java, page_anchor, page_block, label="rocregplot page")

body_anchor = '''         } else if ("biplot".equals(var1)) {
            this.addGenericBodyField(coreBody, "参与分析的变量（至少 2 个，可多选）", this.listPane(this.variables));'''
body_block = '''         } else if ("rocregplot".equals(var1)) {
            JLabel rocRegPlotHint = new JLabel("<html>使用最近一次成功的 <b>rocreg</b> 结果。常见比较可在下一步直接写 <b>at1(currage=40) at2(currage=50)</b>；无需重新选择 ROC 原始变量。</html>");
            rocRegPlotHint.setForeground(MUTED);
            rocRegPlotHint.setFont(rocRegPlotHint.getFont().deriveFont(10.0F));
            rocRegPlotHint.setAlignmentX(0.0F);
            coreBody.add(rocRegPlotHint);
         } else if ("biplot".equals(var1)) {
            this.addGenericBodyField(coreBody, "参与分析的变量（至少 2 个，可多选）", this.listPane(this.variables));'''
java = replace_exact(java, body_anchor, body_block, label="rocregplot body")

# Build the native command directly from postestimation options.
preview_anchor = '''         } else if ("biplot".equals(this.currentCommand)) {
            List<String> biplotVars = this.variables.getSelectedValuesList();'''
preview_block = '''         } else if ("rocregplot".equals(this.currentCommand)) {
            var1 = "rocregplot";
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if ("biplot".equals(this.currentCommand)) {
            List<String> biplotVars = this.variables.getSelectedValuesList();'''
java = replace_exact(java, preview_anchor, preview_block, label="rocregplot preview builder")

# Treat it consistently with other result-based graph pages in hints/status.
java = replace_exact(
    java,
    'Arrays.asList("marginsplot", "coefplot", "event_plot").contains(var1)',
    'Arrays.asList("rocregplot", "marginsplot", "coefplot", "event_plot").contains(var1)',
    label="result graph status",
)
java = replace_exact(
    java,
    'Arrays.asList("event_plot", "marginsplot", "coefplot").contains(command)',
    'Arrays.asList("rocregplot", "event_plot", "marginsplot", "coefplot").contains(command)',
    label="result graph task hint",
)

# Keep static contracts synchronized with the new structured route.
static = replace_exact(
    static,
    '"roctab", "roccomp", "rocgold", "screeplot"',
    '"roctab", "roccomp", "rocgold", "rocregplot", "screeplot"',
    expected=1,
    label="static special_open",
)
static = replace_exact(
    static,
    '"sts_graph", "roctab", "roccomp", "rocgold", "screeplot"',
    '"sts_graph", "roctab", "roccomp", "rocgold", "rocregplot", "screeplot"',
    expected=1,
    label="structured route loop",
)

roc_contract_anchor = '''if '"rocregplot"' not in roc_route_scope:
    fail("rocregplot must route to the graph result view")
'''
roc_contract_block = '''if '"rocregplot"' not in roc_route_scope:
    fail("rocregplot must route to the graph result view")
for needle in (
    'rocregplot · ROC regression 结果图',
    'coreTitle = "上一条 rocreg 结果";',
    'var1 = "rocregplot";',
    '使用最近一次成功的 <b>rocreg</b> 结果',
    'Arrays.asList("rocregplot", "marginsplot", "coefplot", "event_plot").contains(var1)',
):
    if needle not in java:
        fail(f"rocregplot structured page contract missing: {needle}")
'''
static = replace_exact(static, roc_contract_anchor, roc_contract_block, label="rocregplot static contract")

# Strong catalog coverage gate: only setting/estimation commands are intentionally non-special in Graphics.
coverage_anchor = '''for graph_cmd in ("line", "connected", "qfit", "lowess", "lpoly", "rvfplot", "rvpplot", "avplot", "avplots", "lvr2plot", "cprplot", "acprplot", "graph_matrix", "twoway_contour", "tsline", "xtline", "sts_graph", "roctab", "roccomp", "rocgold", "screeplot", "scoreplot", "loadingplot", "biplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay", "symplot", "quantile", "qnorm", "pnorm", "qchi", "pchi", "qqplot", "gladder", "qladder", "dotplot", "spikeplot", "sunflower", "cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar", "marginsplot", "coefplot", "event_plot", "graph_combine", "graph"):
    if graph_cmd not in special_open:
        fail(f"structured Graphics route contract missing: {graph_cmd}")
'''
coverage_block = '''for graph_cmd in ("line", "connected", "qfit", "lowess", "lpoly", "rvfplot", "rvpplot", "avplot", "avplots", "lvr2plot", "cprplot", "acprplot", "graph_matrix", "twoway_contour", "tsline", "xtline", "sts_graph", "roctab", "roccomp", "rocgold", "rocregplot", "screeplot", "scoreplot", "loadingplot", "biplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay", "symplot", "quantile", "qnorm", "pnorm", "qchi", "pchi", "qqplot", "gladder", "qladder", "dotplot", "spikeplot", "sunflower", "cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar", "marginsplot", "coefplot", "event_plot", "graph_combine", "graph"):
    if graph_cmd not in special_open:
        fail(f"structured Graphics route contract missing: {graph_cmd}")
intentional_non_special_graphics = {"set", "rocfit", "rocreg"}
for graph_cmd in set(local_words(registry, "graph_cmds")) - intentional_non_special_graphics:
    if f'"{graph_cmd}"' not in special_open:
        fail(f"Graphics catalog command unexpectedly falls back to generic page: {graph_cmd}")
'''
static = replace_exact(static, coverage_anchor, coverage_block, label="catalog coverage gate")

java_path.write_text(java, encoding="utf-8")
static_path.write_text(static, encoding="utf-8")
print("HX_ROCREGPLOT_PATCH_OK")
