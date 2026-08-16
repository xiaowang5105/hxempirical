from pathlib import Path

jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")

func_start = j.find("      private static String commandMethod(String var0)")
func_end = j.find("      private static String commandPath(String var0)", func_start)
if func_start < 0 or func_end < 0:
    raise SystemExit("commandMethod scope not found")
sc = j[func_start:func_end]

start_marker = '         } else if (Arrays.asList("histogram", "kdensity", "graph_box").contains(var0)) {'
end_marker = '         } else if ("event_plot".equals(var0)) {'
a = sc.find(start_marker)
b = sc.find(end_marker, a)
if a < 0 or b < 0:
    raise SystemExit(f"Graphics commandMethod replacement range not found: start={a} end={b}")

graphs = '''         } else if (Arrays.asList("twoway", "scatter", "line", "connected", "lfit", "qfit").contains(var0)) {
            return "图形|二维图(散点图，折线图等)";
         } else if ("graph_bar".equals(var0)) {
            return "图形|条形图";
         } else if ("graph_dot".equals(var0)) {
            return "图形|点图";
         } else if ("graph_pie".equals(var0)) {
            return "图形|饼图";
         } else if ("histogram".equals(var0)) {
            return "图形|直方图";
         } else if ("graph_box".equals(var0)) {
            return "图形|箱线图";
         } else if ("twoway_contour".equals(var0)) {
            return "图形|等高线图";
         } else if ("graph_matrix".equals(var0)) {
            return "图形|散点图矩阵";
         } else if (Arrays.asList("kdensity", "lowess", "lpoly").contains(var0)) {
            return "图形|平滑和密度";
         } else if (Arrays.asList("rvfplot", "rvpplot", "avplot", "avplots", "lvr2plot", "cprplot", "acprplot").contains(var0)) {
            return "图形|回归诊断图";
         } else if ("tsline".equals(var0)) {
            return "图形|时间序列图";
         } else if ("xtline".equals(var0)) {
            return "图形|面板数据折线图";
         } else if ("sts_graph".equals(var0)) {
            return "图形|生存分析图";
         } else if (Arrays.asList("roctab", "rocfit", "roccomp", "rocgold", "rocreg").contains(var0)) {
            return "图形|ROC分析";
         } else if (Arrays.asList("screeplot", "scoreplot", "loadingplot", "biplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay").contains(var0)) {
            return "图形|多元分析图";
         } else if (Arrays.asList("cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar").contains(var0)) {
            return "图形|质量控制";
         } else if (Arrays.asList("symplot", "quantile", "qnorm", "pnorm", "qchi", "pchi", "qqplot", "gladder", "qladder", "dotplot", "spikeplot", "sunflower", "marginsplot", "coefplot").contains(var0)) {
            return "图形|更多统计图形";
         } else if ("graph_combine".equals(var0)) {
            return "图形|图形组合";
         } else if ("graph".equals(var0)) {
            return "图形|管理图形";
         } else if ("set".equals(var0)) {
            return "图形|更改方案/大小";
         } else if ("did_trends".equals(var0)) {
            return "DID 专区|平行趋势与动态图";
'''

sc = sc[:a] + graphs + sc[b:]
j = j[:func_start] + sc + j[func_end:]
jp.write_text(j, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''if 'return "后估计|系数检验";' in command_method_scope or 'return "后估计|预测边际";' in command_method_scope:
    fail("native postestimation commands still use legacy post commandPath labels")
'''
checks = '''graph_command_method_contracts = {
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
'''
if v.count(anchor) != 1:
    raise SystemExit(f"Graphics commandMethod contract anchor expected once, got {v.count(anchor)}")
v = v.replace(anchor, anchor + checks, 1)
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_GRAPH_COMMAND_METHOD_PATCH_OK")
