from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------- registry ----------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.23  16aug2026", "*! hxregistry 3.1.24  16aug2026", "registry version")
old_graph = '    local graph_cmds "graph twoway scatter line connected lfit qfit histogram kdensity dotplot graph_box lowess lpoly rvfplot rvpplot avplot avplots lvr2plot cprplot acprplot tsline xtline roctab rocfit roccomp rocgold rocreg marginsplot coefplot event_plot"\n'
new_graph = '    local graph_cmds "graph twoway scatter line connected lfit qfit histogram kdensity graph_bar graph_dot graph_pie graph_box twoway_contour graph_matrix graph_combine lowess lpoly rvfplot rvpplot avplot avplots lvr2plot cprplot acprplot tsline xtline roctab rocfit roccomp rocgold rocreg cchart pchart rchart xchart shewhart serrbar symplot quantile qnorm pnorm qchi pchi qqplot gladder qladder dotplot spikeplot sunflower marginsplot coefplot event_plot"\n'
r = once(r, old_graph, new_graph, "graph command catalog")
route_repls = {
    '    else if inlist(`"`method\'"\', "条形图", "bar_graph") local view "twoway"\n': '    else if inlist(`"`method\'"\', "条形图", "bar_graph") local view "graph_bar"\n',
    '    else if inlist(`"`method\'"\', "点图", "dot_graph") local view "dotplot"\n': '    else if inlist(`"`method\'"\', "点图", "dot_graph") local view "graph_dot"\n',
    '    else if inlist(`"`method\'"\', "饼图", "pie_graph") local view "graph"\n': '    else if inlist(`"`method\'"\', "饼图", "pie_graph") local view "graph_pie"\n',
    '    else if inlist(`"`method\'"\', "等高线图", "contour_graph") local view "twoway"\n': '    else if inlist(`"`method\'"\', "等高线图", "contour_graph") local view "twoway_contour"\n',
    '    else if inlist(`"`method\'"\', "散点图矩阵", "matrix_graph") local view "graph"\n': '    else if inlist(`"`method\'"\', "散点图矩阵", "matrix_graph") local view "graph_matrix"\n',
    '    else if inlist(`"`method\'"\', "质量控制", "quality_graph") local view "graph"\n': '    else if inlist(`"`method\'"\', "质量控制", "quality_graph") local view "cchart pchart rchart xchart shewhart serrbar"\n',
    '    else if inlist(`"`method\'"\', "更多统计图形", "more_stat_graph") local view "marginsplot coefplot event_plot"\n': '    else if inlist(`"`method\'"\', "更多统计图形", "more_stat_graph") local view "symplot quantile qnorm pnorm qchi pchi qqplot gladder qladder dotplot spikeplot sunflower marginsplot coefplot event_plot"\n',
    '    else if inlist(`"`method\'"\', "图形组合", "graph_combine") local view "graph"\n': '    else if inlist(`"`method\'"\', "图形组合", "graph_combine") local view "graph_combine"\n',
}
for old, new in route_repls.items():
    r = once(r, old, new, f"graphics route {old[:45]}")
# Search keywords for aliases and restored official graphics.
anchor = '        local key_margins "margins 边际效应 调节效应"\n'
add = '''        local key_graph_bar "graph bar bar chart 条形图 柱状图 over 分组 均值 频数"
        local key_graph_dot "graph dot dot chart 点图 over 分组 均值"
        local key_graph_pie "graph pie pie chart 饼图 over 分组 百分比"
        local key_graph_matrix "graph matrix scatterplot matrix 散点图矩阵 多变量"
        local key_twoway_contour "twoway contour contour plot 等高线 三变量 z y x"
        local key_graph_combine "graph combine combine graphs 图形组合 多图 拼图"
        local key_cchart "cchart quality control count chart 质量控制 c图 计数"
        local key_pchart "pchart quality control proportion chart 质量控制 p图 比例"
        local key_rchart "rchart quality control range chart 质量控制 R图 极差"
        local key_xchart "xchart quality control mean chart 质量控制 Xbar图 均值"
        local key_shewhart "shewhart quality control chart 质量控制 控制限"
        local key_serrbar "serrbar standard error bar chart 标准误 误差棒"
        local key_symplot "symplot symmetry plot distribution 对称图 分布诊断"
        local key_quantile "quantile quantile plot distribution 分位数图"
        local key_qnorm "qnorm quantile normal plot 正态 分位数图"
        local key_pnorm "pnorm normal probability plot 正态 概率图"
        local key_qchi "qchi quantile chi squared plot 卡方 分位数图"
        local key_pchi "pchi chi squared probability plot 卡方 概率图"
        local key_qqplot "qqplot quantile quantile two variables Q-Q 两变量 分位数"
        local key_gladder "gladder ladder of powers distribution transformation 变换 梯图"
        local key_qladder "qladder quantile normal ladder transformation 梯图 正态"
        local key_dotplot "dotplot distribution dot plot 分布 点图 堆叠"
        local key_spikeplot "spikeplot spike plot distribution 尖峰图 分布"
        local key_sunflower "sunflower density distribution bivariate scatter 密度 向日葵图"
'''
r = once(r, anchor, anchor + add, "graphics search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------- resolver: UI aliases probe real Stata commands ----------
resp = Path("hxresolve.ado")
res = resp.read_text(encoding="utf-8")
res = once(res, "*! hxresolve 3.1.3  12aug2026", "*! hxresolve 3.1.4  16aug2026", "resolver version")
validation = '''    if !regexm("`cmd'", "^[A-Za-z_][A-Za-z0-9_]*$") {
        display as error "请输入一个 Stata 命令名，例如 regress 或 winsor2。"
        exit 198
    }

'''
probe = '''    if !regexm("`cmd'", "^[A-Za-z_][A-Za-z0-9_]*$") {
        display as error "请输入一个 Stata 命令名，例如 regress 或 winsor2。"
        exit 198
    }

    /* Multiword Graphics commands use stable one-token UI aliases.
       Probe the real Stata parent command for installation/help/parser metadata,
       while keeping the alias for semantic roles and native preview generation. */
    local probe_cmd "`cmd'"
    if strpos(" graph_bar graph_dot graph_pie graph_matrix graph_combine ", " `cmd' ") local probe_cmd "graph"
    else if "`cmd'" == "twoway_contour" local probe_cmd "twoway"

'''
res = once(res, validation, probe, "resolver graph alias probe")
for old, new, label in [
    ("capture quietly which `cmd'", "capture quietly which `probe_cmd'", "resolver which probe"),
    ("capture quietly findfile `cmd'.ado", "capture quietly findfile `probe_cmd'.ado", "resolver ado probe"),
    ("capture quietly findfile `cmd'.sthlp", "capture quietly findfile `probe_cmd'.sthlp", "resolver sthlp probe"),
    ("capture quietly findfile `cmd'.hlp", "capture quietly findfile `probe_cmd'.hlp", "resolver hlp probe"),
    ("capture quietly findfile `cmd'.dlg", "capture quietly findfile `probe_cmd'.dlg", "resolver dlg probe"),
    ("quietly hxparser, command(`cmd') source(\"`source'\") ///", "quietly hxparser, command(`probe_cmd') source(\"`source'\") ///", "resolver parser probe"),
]:
    res = once(res, old, new, label)
resp.write_text(res, encoding="utf-8", newline="\n")


# ---------- preview: aliases always generate native multiword Stata ----------
pp = Path("hxpreview.ado")
pv = pp.read_text(encoding="utf-8")
pv = once(pv, "*! hxpreview 1.3.1  12aug2026", "*! hxpreview 1.3.2  16aug2026", "preview version")
preview_anchor = '''    local preview `"`command'"'
    if "`command'" == "lfit" local preview "twoway lfit"
'''
preview_new = '''    local preview `"`command'"'
    if "`command'" == "lfit" local preview "twoway lfit"
    if "`command'" == "graph_bar" local preview "graph bar"
    if "`command'" == "graph_dot" local preview "graph dot"
    if "`command'" == "graph_pie" local preview "graph pie"
    if "`command'" == "graph_matrix" local preview "graph matrix"
    if "`command'" == "twoway_contour" local preview "twoway contour"
    if "`command'" == "graph_combine" local preview "graph combine"
'''
pv = once(pv, preview_anchor, preview_new, "preview graph aliases")
pp.write_text(pv, encoding="utf-8", newline="\n")


# ---------- semantics ----------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.22  16aug2026", "*! hxsemantics 1.4.23  16aug2026", "semantics version")
family_marker = '''    /* Family-level copy for catalog commands that rely on the generic syntax parser.
'''
if s.count(family_marker) != 1:
    raise SystemExit(f"graphics semantic insertion marker count={s.count(family_marker)}")
graphics_sem = '''    /* Graphics aliases preserve native multiword Stata syntax while offering one navigable UI token. */
    if strpos(" graph_bar graph_dot graph_pie graph_matrix twoway_contour graph_combine ", " `cmd' ") {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_if 0
        local has_in 0
        local has_weight 0
        local has_using 0
        local has_newvar 0
        local has_expression 1
        local has_absorb 0
        local has_vce 0
        local has_cluster 0
        local has_iv 0
        local needs_panel 0
        local model_before 0
        local show_advanced 1
        if "`cmd'" == "graph_bar" {
            local title "graph bar — 条形图"
            local purpose1 "对一个或多个数值变量绘制统计量条形图，并可用 over() 按类别分组。"
            local purpose2 "页面主体只填写 graph bar 后面的原生内容；实时命令始终生成真正的 graph bar。"
            local expr_label "统计量 + 数值变量 + over()/asyvars 等（graph bar 后面的内容）"
            local example1 "graph bar le le_w le_b"
            local explain1 "绘制三个变量的默认均值条形图。"
            local example2 "graph bar heatdd cooldd, over(region) blabel(total)"
            local explain2 "按 region 分组并显示 bar labels。"
        }
        else if "`cmd'" == "graph_dot" {
            local title "graph dot — 汇总点图"
            local purpose1 "绘制均值、百分位等 summary statistics 的 dot chart；这与分布型 dotplot 是两类图。"
            local purpose2 "需要按类别比较时直接写 over()；实时命令生成 graph dot。"
            local expr_label "统计量 + 数值变量 + over() 等（graph dot 后面的内容）"
            local example1 "graph dot wage, over(occ)"
            local explain1 "按 occupation 显示 wage 的汇总点图。"
            local example2 "graph dot wage hours, over(occ) vertical"
            local explain2 "同时画 wage、hours，并改为 vertical dot chart。"
        }
        else if "`cmd'" == "graph_pie" {
            local title "graph pie — 饼图"
            local purpose1 "用数值变量的总量或 over() 分组构造 pie slices。"
            local purpose2 "类别频数型饼图通常直接使用 over(category)。"
            local expr_label "数值变量 + over()/plabel()/pie() 等（graph pie 后面的内容）"
            local example1 "graph pie pop, over(region)"
            local explain1 "按 region 划分 pop 的饼图。"
            local example2 "graph pie pop, over(region) plabel(_all name)"
            local explain2 "在每个 slice 上显示类别名称。"
        }
        else if "`cmd'" == "graph_matrix" {
            local title "graph matrix — 散点图矩阵"
            local purpose1 "一次查看多个变量两两关系，并在对角线显示变量标签。"
            local purpose2 "变量较多时矩阵会迅速变密；先放核心连续变量。"
            local expr_label "变量列表 + half/diagonal()/marker options（graph matrix 后面的内容）"
            local example1 "graph matrix mpg weight length"
            local explain1 "绘制 mpg、weight、length 的 scatterplot matrix。"
            local example2 "help graph matrix"
            local explain2 "需要半矩阵、标签或 marker 调整时按原生 graph matrix options 补充。"
        }
        else if "`cmd'" == "twoway_contour" {
            local title "twoway contour — 等高线图"
            local purpose1 "把 z 在 y–x 平面上的数值变化显示为填充等高区域。"
            local purpose2 "前三个变量顺序固定为 z y x；当前 Stata 16–18 兼容层不展示 Stata 19 heatmap。"
            local expr_label "z y x + levels()/ccuts()/color options（twoway contour 后面的内容）"
            local example1 "twoway contour z y x"
            local explain1 "以 x、y 为坐标，用 z 的大小形成填充等高线。"
            local example2 "help twoway contour"
            local explain2 "等高层数、cutpoints 和颜色等继续使用原生 contour options。"
        }
        else if "`cmd'" == "graph_combine" {
            local title "graph combine — 组合已有图形"
            local purpose1 "把多个已命名或已保存的 Stata graphs 排成一张组合图。"
            local purpose2 "先确保子图已经存在；cols()/rows()/xcommon/ycommon 控制布局与公共坐标。"
            local expr_label "图形名/文件 + cols()/rows()/xcommon/ycommon 等（graph combine 后面的内容）"
            local example1 "graph combine gr1 gr2, cols(2)"
            local explain1 "把 gr1、gr2 横向排成两列。"
            local example2 "graph combine gr1 gr2, ycommon"
            local explain2 "组合两图并强制使用共同 y-axis scale。"
        }
    }

    if strpos(" symplot quantile qnorm pnorm qchi pchi qqplot gladder qladder dotplot spikeplot sunflower ", " `cmd' ") {
        local title "`cmd' — 分布诊断图"
        local purpose1 "用于检查对称性、分位数/概率分布、变量变换或密集散点的分布结构。"
        local purpose2 "这组是 Stata 官方 distributional diagnostic graphics；graph dot 另用于 summary dot charts。"
        if "`cmd'" == "symplot" {
            local example1 "symplot price"
            local explain1 "检查 price 分布关于中位数的对称程度。"
        }
        else if "`cmd'" == "quantile" {
            local example1 "quantile price"
            local explain1 "绘制 price 的 quantile plot。"
        }
        else if "`cmd'" == "qnorm" {
            local example1 "qnorm price"
            local explain1 "用 quantile–normal plot 检查 price 与正态分布的偏离。"
        }
        else if "`cmd'" == "pnorm" {
            local example1 "pnorm price"
            local explain1 "绘制 normal probability plot。"
        }
        else if "`cmd'" == "qchi" {
            local example1 "qchi ch, df(2)"
            local explain1 "将 ch 的分位数与 2 自由度 chi-squared 分布比较。"
        }
        else if "`cmd'" == "pchi" {
            local example1 "pchi ch, df(2)"
            local explain1 "绘制相对于 chi-squared 分布的 probability plot。"
        }
        else if "`cmd'" == "qqplot" {
            local example1 "qqplot weightd weightf"
            local explain1 "直接比较两个变量的 empirical quantiles。"
        }
        else if "`cmd'" == "gladder" {
            local example1 "gladder mpg, fraction"
            local explain1 "用 ladder-of-powers 图探索使 mpg 更接近正态/对称的变换。"
        }
        else if "`cmd'" == "qladder" {
            local example1 "qladder heatdd"
            local explain1 "比较多种 power transformations 的 quantile-normal 表现。"
        }
        else if "`cmd'" == "dotplot" {
            local example1 "dotplot age"
            local explain1 "把原始 age 分布显示为堆叠 dots；用途不同于 graph dot 的 summary chart。"
        }
        else if "`cmd'" == "spikeplot" {
            local example1 "spikeplot age"
            local explain1 "用 spikes 显示一维分布。"
        }
        else if "`cmd'" == "sunflower" {
            local example1 "sunflower mpg displ"
            local explain1 "用 sunflower rays 表示重叠观测密度，适合密集 bivariate scatter。"
        }
        local example2 "help `cmd'"
        local explain2 "查看当前 Stata 版本的完整绘图 options。"
    }

    if strpos(" cchart pchart rchart xchart shewhart serrbar ", " `cmd' ") {
        local title "`cmd' — 质量控制图"
        local purpose1 "用于 statistical process control：count/proportion/range/mean/Shewhart control charts 或 standard-error bars。"
        local purpose2 "控制图的样本单位、控制限和 subgroup 结构必须与实际过程采样设计一致。"
        if "`cmd'" == "shewhart" {
            local example1 "shewhart m1-m5, connect(l)"
            local explain1 "对 m1–m5 的 subgroup measurements 绘制 Shewhart control chart。"
        }
        else if "`cmd'" == "serrbar" {
            local example1 "serrbar mean se x"
            local explain1 "在 x 轴上绘制 mean ± se 的 standard-error bars。"
        }
        else {
            local example1 "help `cmd'"
            local explain1 "先按当前命令 Help 确认 count/proportion/range/mean control-chart 的样本结构字段。"
        }
        local example2 "help `cmd'"
        local explain2 "查看控制限、nograph、generate() 和图形定制等命令特有选项。"
    }

'''
s = s.replace(family_marker, graphics_sem + family_marker, 1)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------- Java: Help must resolve aliases to native multiword commands ----------
jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")
start = j.find("private void openHelp()")
if start < 0:
    raise SystemExit("Java openHelp() missing")
end = j.find("private ", start + len("private void openHelp()"))
if end < 0:
    raise SystemExit("Java openHelp() end marker missing")
block = j[start:end]
if '"graph_bar".equals(var1)' not in block:
    marker = "            int var2 ="
    pos = block.find(marker)
    if pos < 0:
        raise SystemExit("Java openHelp var2 insertion marker missing")
    alias_help = '''            if ("graph_bar".equals(var1)) var1 = "graph bar";
            else if ("graph_dot".equals(var1)) var1 = "graph dot";
            else if ("graph_pie".equals(var1)) var1 = "graph pie";
            else if ("graph_matrix".equals(var1)) var1 = "graph matrix";
            else if ("twoway_contour".equals(var1)) var1 = "twoway contour";
            else if ("graph_combine".equals(var1)) var1 = "graph combine";
'''
    block = block[:pos] + alias_help + block[pos:]
    j = j[:start] + block + j[end:]
jp.write_text(j, encoding="utf-8", newline="\n")


# ---------- static contracts ----------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'postestimation_core = {\n'
checks = '''graph_aliases = {"graph_bar", "graph_dot", "graph_pie", "graph_matrix", "twoway_contour", "graph_combine"}
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
    'if "`command\'" == "graph_bar" local preview "graph bar"',
    'if "`command\'" == "graph_dot" local preview "graph dot"',
    'if "`command\'" == "graph_pie" local preview "graph pie"',
    'if "`command\'" == "graph_matrix" local preview "graph matrix"',
    'if "`command\'" == "twoway_contour" local preview "twoway contour"',
    'if "`command\'" == "graph_combine" local preview "graph combine"',
}
for needle in preview_contracts:
    if needle not in preview:
        fail(f"native Graphics preview mapping missing: {needle}")
for needle in (
    'if strpos(" graph_bar graph_dot graph_pie graph_matrix graph_combine ", " `cmd\' ") local probe_cmd "graph"',
    'else if "`cmd\'" == "twoway_contour" local probe_cmd "twoway"',
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
    "graph matrix mpg weight length",
    "twoway contour z y x",
    "graph combine gr1 gr2, cols(2)",
    "symplot price", "qnorm price", "qqplot weightd weightf", "spikeplot age", "sunflower mpg displ",
    "shewhart m1-m5, connect(l)", "serrbar mean se x",
):
    if needle not in semantics:
        fail(f"Graphics semantic contract missing: {needle}")

'''
v = once(v, anchor, checks + anchor, "Graphics alias static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_GRAPHICS_ALIAS_PATCH_OK")
