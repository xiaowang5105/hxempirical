from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

# Registry
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.31  16aug2026", "*! hxregistry 3.1.32  16aug2026", "registry version")
r = once(
    r,
    'local graph_cmds "graph set twoway scatter line connected lfit qfit histogram kdensity graph_bar graph_dot graph_pie graph_box twoway_contour graph_matrix graph_combine lowess lpoly rvfplot rvpplot avplot avplots lvr2plot cprplot acprplot tsline xtline roctab rocfit roccomp rocgold rocreg cchart pchart rchart xchart shewhart serrbar symplot quantile qnorm pnorm qchi pchi qqplot gladder qladder dotplot spikeplot sunflower marginsplot coefplot event_plot"',
    'local graph_cmds "graph set twoway scatter line connected lfit qfit histogram kdensity graph_bar graph_dot graph_pie graph_box twoway_contour graph_matrix graph_combine lowess lpoly rvfplot rvpplot avplot avplots lvr2plot cprplot acprplot tsline xtline roctab rocfit roccomp rocgold rocreg screeplot scoreplot loadingplot biplot cluster_dendrogram cabiplot caprojection mdsconfig mdsshepard procoverlay cchart pchart rchart xchart shewhart serrbar symplot quantile qnorm pnorm qchi pchi qqplot gladder qladder dotplot spikeplot sunflower marginsplot coefplot event_plot"',
    "multivariate graph catalog",
)
r = once(
    r,
    'else if inlist(`"`method\'"\', "多元分析图", "multivariate_graph") local view "pca factor cluster"',
    'else if inlist(`"`method\'"\', "多元分析图", "multivariate_graph") local view "screeplot scoreplot loadingplot biplot cluster_dendrogram cabiplot caprojection mdsconfig mdsshepard procoverlay"',
    "multivariate graph route",
)
anchor = '        local key_marginsplot "marginsplot 边际效应图 调节效应图"\n'
keywords = '''        local key_screeplot "screeplot factor pca eigenvalue scree plot 碎石图 主成分 因子 特征值"
        local key_scoreplot "scoreplot factor pca scores components 因子 得分图 主成分"
        local key_loadingplot "loadingplot factor pca loadings 因子 载荷图 主成分"
        local key_biplot "biplot multivariate rows columns 双标图 多元分析"
        local key_cluster_dendrogram "cluster dendrogram hierarchical clustering tree 聚类 树状图 层次聚类"
        local key_cabiplot "cabiplot correspondence analysis biplot 对应分析 双标图"
        local key_caprojection "caprojection correspondence analysis projection 对应分析 投影图"
        local key_mdsconfig "mdsconfig multidimensional scaling configuration MDS 多维尺度 配置图"
        local key_mdsshepard "mdsshepard Shepard multidimensional scaling MDS 多维尺度 Shepard 图"
        local key_procoverlay "procoverlay procrustes overlay 普鲁克拉斯 叠加图"
'''
r = once(r, anchor, keywords + anchor, "multivariate graph search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")

# Resolver alias for cluster dendrogram
xp = Path("hxresolve.ado")
x = xp.read_text(encoding="utf-8")
x = once(x, "*! hxresolve 3.1.4  16aug2026", "*! hxresolve 3.1.5  16aug2026", "resolver version")
x = once(
    x,
    '    if strpos(" graph_bar graph_dot graph_pie graph_matrix graph_combine ", " `cmd\' ") local probe_cmd "graph"\n    else if "`cmd\'" == "twoway_contour" local probe_cmd "twoway"',
    '    if strpos(" graph_bar graph_dot graph_pie graph_matrix graph_combine ", " `cmd\' ") local probe_cmd "graph"\n    else if "`cmd\'" == "twoway_contour" local probe_cmd "twoway"\n    else if "`cmd\'" == "cluster_dendrogram" local probe_cmd "cluster"',
    "resolver cluster dendrogram alias",
)
xp.write_text(x, encoding="utf-8", newline="\n")

# Semantics
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.27  16aug2026", "*! hxsemantics 1.4.28  16aug2026", "semantics version")
# Put all multivariate graph commands through safe command-body handling.
needle = ' teffects eteffects stteffects mediate hdidregress xthdidregress sts irf graph set discrim cluster table '
s = once(s, needle, ' teffects eteffects stteffects mediate hdidregress xthdidregress sts irf graph set screeplot scoreplot loadingplot biplot cluster_dendrogram cabiplot caprojection mdsconfig mdsshepard procoverlay discrim cluster table ', "complex multivariate graph inclusion")
old = '''        else if "`cmd'" == "irf" {
            local expr_label "irf 子命令与参数（如 create / graph / table）"
        }
'''
new = '''        else if "`cmd'" == "irf" {
            local expr_label "irf 子命令与参数（如 create / graph / table）"
        }
        else if "`cmd'" == "screeplot" {
            local title "screeplot — 碎石图"
            local purpose1 "在 factor、pca 或兼容多元分析后绘制特征值/惯量随维度变化的 scree plot。"
            local purpose2 "先完成相应多元模型；本页只设置要展示的维度、置信区间和图形 options。"
            local expr_label "screeplot 选项（通常可留空直接绘图）"
            local example1 "screeplot"
            local explain1 "绘制最近一次 factor/PCA 等结果的碎石图。"
            local example2 "screeplot, yline(1)"
            local explain2 "增加 eigenvalue=1 的参考线。"
        }
        else if "`cmd'" == "scoreplot" {
            local title "scoreplot — 因子/主成分得分图"
            local purpose1 "在 factor 或 pca 后绘制因子/主成分 scores 的二维关系。"
            local purpose2 "需要先成功估计 factor/factormat 或 pca/pcamat。"
            local expr_label "维度与图形 options（如 factors(1 2)）"
            local example1 "scoreplot"
            local explain1 "绘制默认前两个因子或主成分的 score plot。"
            local example2 "help scoreplot"
            local explain2 "维度选择、标签和 marker 选项按当前 Stata Help 设置。"
        }
        else if "`cmd'" == "loadingplot" {
            local title "loadingplot — 因子/主成分载荷图"
            local purpose1 "在 factor 或 pca 后比较变量在两个因子/主成分上的 loadings。"
            local purpose2 "变量箭头/点的位置反映载荷结构，解释时结合旋转方式和保留维度。"
            local expr_label "维度与图形 options（通常可直接运行）"
            local example1 "loadingplot"
            local explain1 "绘制最近一次 factor/PCA 的默认 loading plot。"
            local example2 "help loadingplot"
            local explain2 "旋转结果、标签和坐标轴选项按当前 Stata Help 设置。"
        }
        else if "`cmd'" == "biplot" {
            local title "biplot — 多元双标图"
            local purpose1 "同时显示观测在低维空间中的位置与变量方向，用二维图概括多变量结构。"
            local purpose2 "biplot 可以直接对数据执行双标图分析；dim() 等选项决定显示维度。"
            local expr_label "变量列表 + dim()/rowlabel()/rowover() 等"
            local example1 "biplot x1 x2 x3 x4"
            local explain1 "对四个变量执行 biplot analysis 并绘制二维双标图。"
            local example2 "help biplot"
            local explain2 "分组、高亮、维度和坐标生成选项按当前 Stata Help 设置。"
        }
        else if "`cmd'" == "cluster_dendrogram" {
            local title "cluster dendrogram — 层次聚类树状图"
            local purpose1 "在层次聚类结果后绘制 dendrogram，查看对象如何逐步合并成簇。"
            local purpose2 "实时命令生成原生 cluster dendrogram；需要先存在兼容的 hierarchical cluster result。"
            local expr_label "cluster dendrogram 后面的分析名与 options（可留空使用当前聚类结果）"
            local example1 "cluster dendrogram"
            local explain1 "为当前层次聚类结果绘制完整树状图。"
            local example2 "cluster dendrogram, horizontal"
            local explain2 "改为水平树状图。"
        }
        else if "`cmd'" == "cabiplot" {
            local title "cabiplot — 对应分析双标图"
            local purpose1 "在 ca/camat 后同时显示行类别和列类别在主维度空间中的位置。"
            local purpose2 "先完成 correspondence analysis；本页只负责图形维度、标签和 marker options。"
            local expr_label "cabiplot 选项（如 dimensions()/origin/rowopts()/colopts()）"
            local example1 "cabiplot"
            local explain1 "绘制最近一次 correspondence analysis 的默认 biplot。"
            local example2 "cabiplot, origin"
            local explain2 "在图中显示原点。"
        }
        else if "`cmd'" == "caprojection" {
            local title "caprojection — 对应分析维度投影图"
            local purpose1 "在 ca/camat 后显示行、列类别在各 principal dimensions 上的投影顺序。"
            local purpose2 "适合直接比较类别沿主要对应分析维度的位置。"
            local expr_label "caprojection 图形 options"
            local example1 "caprojection"
            local explain1 "绘制最近一次 correspondence analysis 的维度投影图。"
            local example2 "help caprojection"
            local explain2 "维度、行列 marker labels 等设置按当前 Help 调整。"
        }
        else if "`cmd'" == "mdsconfig" {
            local title "mdsconfig — MDS 配置图"
            local purpose1 "在 mds/mdslong/mdsmat 后绘制低维 Euclidean configuration。"
            local purpose2 "点之间的图上距离用于近似原始 dissimilarities；应结合 stress 等拟合指标判断。"
            local expr_label "mdsconfig 维度、标签和 marker options"
            local example1 "mdsconfig"
            local explain1 "绘制最近一次 MDS 的前两个维度配置图。"
            local example2 "help mdsconfig"
            local explain2 "对象标签和维度选择按当前 Stata Help 设置。"
        }
        else if "`cmd'" == "mdsshepard" {
            local title "mdsshepard — MDS Shepard 图"
            local purpose1 "在 MDS 后比较原始 dissimilarities 与低维配置中的 fitted distances。"
            local purpose2 "点越接近拟合关系，低维表示越能保持原始距离结构；同时结合 stress 评价。"
            local expr_label "mdsshepard 图形 options"
            local example1 "mdsshepard"
            local explain1 "绘制最近一次 MDS 的 Shepard diagram。"
            local example2 "help mdsshepard"
            local explain2 "标记、拟合线和图形选项按当前 Help 设置。"
        }
        else if "`cmd'" == "procoverlay" {
            local title "procoverlay — Procrustes 叠加图"
            local purpose1 "在 procrustes 后把 target configuration 与由 source 拟合得到的位置叠加比较。"
            local purpose2 "用于直观看两个配置经过 Procrustean transformation 后的贴合程度。"
            local expr_label "procoverlay 图形 options"
            local example1 "procoverlay"
            local explain1 "绘制最近一次 Procrustes analysis 的 overlay plot。"
            local example2 "help procoverlay"
            local explain2 "标签、连接线和图形样式按当前 Help 调整。"
        }
'''
s = once(s, old, new, "multivariate graph semantics")
sp.write_text(s, encoding="utf-8", newline="\n")

# Java fallback and native multiword alias generation.
jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")
j = once(j, '            case "多元分析图": return "pca · factor · cluster";', '            case "多元分析图": return "screeplot · scoreplot · loadingplot · biplot · dendrogram";', "Java graph preview")
j = once(j, '         }          else if ("多元分析图".equals(var0)) {\n            return Arrays.asList("pca", "factor", "cluster");', '         }          else if ("多元分析图".equals(var0)) {\n            return Arrays.asList("screeplot", "scoreplot", "loadingplot", "biplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay");', "Java multivariate fallback list")
j = once(j, '            else if ("graph_combine".equals(var1)) var1 = "graph combine";', '            else if ("graph_combine".equals(var1)) var1 = "graph combine";\n            else if ("cluster_dendrogram".equals(var1)) var1 = "cluster dendrogram";', "Java native alias")
jp.write_text(j, encoding="utf-8", newline="\n")

# Static contracts
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor2 = 'for data_cmd in sorted(data_validation_reorg):\n    if f\'local title "{data_cmd} —\' not in semantics:\n        fail(f"data validation/reorganization semantics missing: {data_cmd}")\n'
checks = '''multivariate_graph_core = {"screeplot", "scoreplot", "loadingplot", "biplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay"}
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
if 'else if "`cmd\'" == "cluster_dendrogram" local probe_cmd "cluster"' not in resolver:
    fail("cluster dendrogram UI alias must probe the native cluster command")
if 'else if ("cluster_dendrogram".equals(var1)) var1 = "cluster dendrogram";' not in java_source:
    fail("Java command preview must emit native cluster dendrogram syntax")
'''
v = once(v, anchor2, anchor2 + checks, "multivariate graphics static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_MULTIVARIATE_GRAPH_PATCH_OK")
