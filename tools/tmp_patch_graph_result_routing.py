from pathlib import Path

jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")
old = '''         } else if (Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_box", "did_trends", "twoway", "marginsplot", "coefplot", "event_plot")
            .contains(this.currentCommand)) {
            this.selectResultView("graph", true);
'''
new = '''         } else if (Arrays.asList(
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
if j.count(old) != 1:
    raise SystemExit(f"old graph result-routing block expected once, got {j.count(old)}")
j = j.replace(old, new, 1)
jp.write_text(j, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'if \'case "更改方案/大小": return "set scheme · graph set";\' in java:\n    fail("Graphics settings card advertises a route not present in its current command list")\n'
checks = '''graph_result_route_required = ("graph_bar", "sts_graph", "screeplot", "cluster_dendrogram", "roctab", "cchart", "graph_combine")
for graph_cmd in graph_result_route_required:
    if graph_cmd not in java:
        fail(f"graph result-route command missing from Java source: {graph_cmd}")
route_start = java.find('} else if (Arrays.asList(\n               "twoway", "scatter", "line", "connected"')
route_end = java.find(').contains(this.currentCommand)) {\n            this.selectResultView("graph", true);', route_start)
if route_start < 0 or route_end < 0:
    fail("expanded Graphics result-routing block missing")
route_scope = java[route_start:route_end]
for graph_cmd in graph_result_route_required:
    if f'"{graph_cmd}"' not in route_scope:
        fail(f"Graphics command does not route to graph result view: {graph_cmd}")
'''
if v.count(anchor) != 1:
    raise SystemExit(f"graph result-route contract anchor expected once, got {v.count(anchor)}")
v = v.replace(anchor, anchor + checks, 1)
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_GRAPH_RESULT_ROUTING_PATCH_OK")
