from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

# 1) Java: every graph-producing command should switch the result pane to graph.
jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")
old_route = '''         } else if (Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_box", "did_trends", "twoway", "marginsplot", "coefplot", "event_plot")
            .contains(this.currentCommand)) {
            this.selectResultView("graph", true);
'''
new_route = '''         } else if (Arrays.asList(
               "twoway", "scatter", "line", "connected", "lfit", "qfit", "histogram", "kdensity",
               "graph_bar", "graph_dot", "graph_pie", "graph_box", "twoway_contour", "graph_matrix", "lowess", "lpoly",
               "rvfplot", "rvpplot", "avplot", "avplots", "lvr2plot", "cprplot", "acprplot", "tsline", "xtline", "sts_graph",
               "roctab", "rocfit", "roccomp", "rocgold", "rocreg",
               "screeplot", "scoreplot", "loadingplot", "biplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay",
               "cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar",
               "symplot", "quantile", "qnorm", "pnorm", "qchi", "pchi", "qqplot", "gladder", "qladder", "dotplot", "spikeplot", "sunflower",
               "marginsplot", "coefplot", "graph_combine", "did_trends", "event_plot"
            ).contains(this.currentCommand)) {
            this.selectResultView("graph", true);
'''
j = once(j, old_route, new_route, "Java graph result route")
jp.write_text(j, encoding="utf-8", newline="\n")

# 2) Resolver parity for graph_box alias.
rp = Path("hxresolve.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxresolve 3.1.6  16aug2026", "*! hxresolve 3.1.7  16aug2026", "hxresolve version")
r = once(
    r,
    'if strpos(" graph_bar graph_dot graph_pie graph_matrix graph_combine ", " `cmd\' ") local probe_cmd "graph"',
    'if strpos(" graph_bar graph_dot graph_pie graph_box graph_matrix graph_combine ", " `cmd\' ") local probe_cmd "graph"',
    "graph_box resolver probe",
)
rp.write_text(r, encoding="utf-8", newline="\n")

# 3) Native preview parity for graph_box alias.
pp = Path("hxpreview.ado")
p = pp.read_text(encoding="utf-8")
p = once(p, "*! hxpreview 1.3.3  16aug2026", "*! hxpreview 1.3.4  16aug2026", "hxpreview version")
p = once(
    p,
    '    if "`command\'" == "graph_pie" local preview "graph pie"\n',
    '    if "`command\'" == "graph_pie" local preview "graph pie"\n    if "`command\'" == "graph_box" local preview "graph box"\n',
    "graph_box preview mapping",
)
pp.write_text(p, encoding="utf-8", newline="\n")

# 4) Semantic parity for graph_box when resolved outside the Java special page.
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.29  16aug2026", "*! hxsemantics 1.4.30  16aug2026", "hxsemantics version")
s = once(
    s,
    'if strpos(" graph_bar graph_dot graph_pie graph_matrix twoway_contour graph_combine ", " `cmd\' ") {',
    'if strpos(" graph_bar graph_dot graph_pie graph_box graph_matrix twoway_contour graph_combine ", " `cmd\' ") {',
    "graph_box semantic alias group",
)
box_anchor = '''        else if "`cmd'" == "graph_matrix" {
'''
box_block = '''        else if "`cmd'" == "graph_box" {
            local title "graph box — 箱线图"
            local purpose1 "展示连续变量的中位数、四分位距、须线和潜在异常值，并可用 over() 比较组间分布。"
            local purpose2 "Java 专页会直接提供结果变量和可选分组变量；这里保留同一真实 Stata 语义，确保搜索/解析链一致。"
            local expr_label "数值变量 + over() 等（graph box 后面的内容）"
            local example1 "graph box y"
            local explain1 "查看 y 的整体箱线分布。"
            local example2 "graph box y, over(group)"
            local explain2 "按 group 比较 y 的中位数、四分位距和潜在异常值。"
        }
'''
s = once(s, box_anchor, box_block + box_anchor, "graph_box semantic block")
sp.write_text(s, encoding="utf-8", newline="\n")

# 5) Static contracts: alias parity + safe result-route scope checks.
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
v = once(
    v,
    'graph_aliases = {"graph_bar", "graph_dot", "graph_pie", "graph_matrix", "twoway_contour", "graph_combine"}',
    'graph_aliases = {"graph_bar", "graph_dot", "graph_pie", "graph_box", "graph_matrix", "twoway_contour", "graph_combine"}',
    "graph alias contract set",
)
v = once(
    v,
    '    "if \\\"`command\'\\\" == \\\"graph_pie\\\" local preview \\\"graph pie\\\"",\n',
    '    "if \\\"`command\'\\\" == \\\"graph_pie\\\" local preview \\\"graph pie\\\"",\n    "if \\\"`command\'\\\" == \\\"graph_box\\\" local preview \\\"graph box\\\"",\n',
    "graph_box preview contract",
)
v = once(
    v,
    '    "if strpos(\\\" graph_bar graph_dot graph_pie graph_matrix graph_combine \\\", \\\" `cmd\' \\\") local probe_cmd \\\"graph\\\"",\n',
    '    "if strpos(\\\" graph_bar graph_dot graph_pie graph_box graph_matrix graph_combine \\\", \\\" `cmd\' \\\") local probe_cmd \\\"graph\\\"",\n',
    "graph_box resolver contract",
)
v = once(
    v,
    '    ("graph_bar", "graph bar"), ("graph_dot", "graph dot"), ("graph_pie", "graph pie"),\n',
    '    ("graph_bar", "graph bar"), ("graph_dot", "graph dot"), ("graph_pie", "graph pie"), ("graph_box", "graph box"),\n',
    "graph_box Java help alias contract",
)
v = once(
    v,
    '    "graph pie pop, over(region)",\n',
    '    "graph pie pop, over(region)",\n    "graph box y, over(group)",\n',
    "graph_box semantic contract",
)
route_anchor = '''if 'case "更改方案/大小": return "set scheme · graph set";' in java:
    fail("Graphics settings card advertises a route not present in its current command list")
'''
route_checks = '''graph_result_route_required = ("graph_bar", "graph_box", "twoway_contour", "sts_graph", "roctab", "screeplot", "cchart", "graph_combine")
route_start = java.find('"graph_bar", "graph_dot", "graph_pie", "graph_box", "twoway_contour", "graph_matrix"')
route_end = java.find('this.selectResultView("graph", true);', route_start)
if route_start < 0 or route_end < 0:
    fail("expanded Graphics result-routing block missing")
route_scope = java[route_start:route_end]
for graph_cmd in graph_result_route_required:
    if f'"{graph_cmd}"' not in route_scope:
        fail(f"Graphics command does not route to graph result view: {graph_cmd}")
'''
v = once(v, route_anchor, route_anchor + route_checks, "graph result route contract anchor")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_GRAPH_ROUTING_PARITY_PATCH_OK")
