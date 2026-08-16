from pathlib import Path

jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")
start = j.find("      private static String graphMethodPreview(String method)")
end = j.find("      private static String dataMethodPreview(String method)", start)
if start < 0 or end < 0:
    raise SystemExit("graphMethodPreview scope not found")
new = '''      private static String graphMethodPreview(String method) {
         switch (method) {
            case "二维图(散点图，折线图等)": return "twoway · scatter · line · connected · lfit · qfit";
            case "条形图": return "graph bar";
            case "点图": return "graph dot";
            case "饼图": return "graph pie";
            case "直方图": return "histogram";
            case "箱线图": return "graph box";
            case "等高线图": return "twoway contour";
            case "散点图矩阵": return "graph matrix";
            case "分布图": return "histogram · kdensity";
            case "平滑和密度": return "kdensity · lowess · lpoly";
            case "回归诊断图": return "rvfplot · rvpplot · avplot · lvr2plot · cprplot";
            case "时间序列图": return "tsline";
            case "面板数据折线图": return "xtline";
            case "生存分析图": return "sts graph";
            case "ROC分析": return "roctab · rocfit · roccomp · rocgold · rocreg";
            case "多元分析图": return "screeplot · scoreplot · loadingplot · biplot · cluster dendrogram";
            case "质量控制": return "cchart · pchart · rchart · xchart · shewhart · serrbar";
            case "更多统计图形": return "symplot · qnorm · qqplot · dotplot · sunflower · marginsplot · coefplot";
            case "图形组合": return "graph combine";
            case "管理图形": return "graph dir · graph display · graph save · graph export";
            case "更改方案/大小": return "set scheme";
            default: return "查看该分类下的 Stata 图形命令";
         }
      }

'''
j = j[:start] + new + j[end:]
jp.write_text(j, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''if 'return "图形|分布图";' in command_method_scope:
    fail("stale broad distribution commandPath label remains after specific Graphics classification")
'''
checks = '''graph_method_preview_contracts = (
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
'''
if v.count(anchor) != 1:
    raise SystemExit(f"Graphics method-preview contract anchor expected once, got {v.count(anchor)}")
v = v.replace(anchor, anchor + checks, 1)
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_GRAPH_METHOD_PREVIEW_PATCH_OK")
