from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.28  16aug2026", "*! hxregistry 3.1.29  16aug2026", "registry version")
r = once(
    r,
    'local graph_cmds "graph twoway scatter line connected lfit qfit histogram kdensity graph_bar graph_dot graph_pie graph_box twoway_contour graph_matrix graph_combine lowess lpoly rvfplot rvpplot avplot avplots lvr2plot cprplot acprplot tsline xtline roctab rocfit roccomp rocgold rocreg cchart pchart rchart xchart shewhart serrbar symplot quantile qnorm pnorm qchi pchi qqplot gladder qladder dotplot spikeplot sunflower marginsplot coefplot event_plot"',
    'local graph_cmds "graph set twoway scatter line connected lfit qfit histogram kdensity graph_bar graph_dot graph_pie graph_box twoway_contour graph_matrix graph_combine lowess lpoly rvfplot rvpplot avplot avplots lvr2plot cprplot acprplot tsline xtline roctab rocfit roccomp rocgold rocreg cchart pchart rchart xchart shewhart serrbar symplot quantile qnorm pnorm qchi pchi qqplot gladder qladder dotplot spikeplot sunflower marginsplot coefplot event_plot"',
    "graph command catalog",
)
r = once(
    r,
    'else if inlist(`"`method\'"\', "更改方案/大小", "graph_scheme") local view "graph"',
    'else if inlist(`"`method\'"\', "更改方案/大小", "graph_scheme") local view "set"',
    "graph scheme route",
)
# Add a search hint beside existing graph-related key definitions when present.
anchor = '        local key_tsset "tsset time series 时间序列 时间变量 声明"\n'
if anchor in r:
    r = once(r, anchor, anchor + '        local key_set "set scheme graphics graph default style 方案 图形 默认 样式"\n', "set search keyword")
rp.write_text(r, encoding="utf-8", newline="\n")

sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.24  16aug2026", "*! hxsemantics 1.4.25  16aug2026", "semantics version")
s = once(
    s,
    ' teffects eteffects stteffects mediate hdidregress xthdidregress sts irf graph discrim cluster table ',
    ' teffects eteffects stteffects mediate hdidregress xthdidregress sts irf graph set discrim cluster table ',
    "complex command-body set inclusion",
)
old_graph = '''        else if "`cmd'" == "graph" {
            local expr_label "graph 子命令与参数（如 combine / save / export / display）"
        }
'''
new_graph = '''        else if "`cmd'" == "graph" {
            local title "graph — 管理、保存与输出图形"
            local purpose1 "管理已经生成的 Stata 图形，包括显示、保存、导出、重命名、关闭和查询图形对象。"
            local purpose2 "这里填写 graph 后面的原生子命令；绘图本身请从对应图形类型入口进入。"
            local expr_label "graph 子命令与参数（如 display / save / export / dir / close）"
            local example1 "graph dir"
            local explain1 "列出当前内存中的已命名图形。"
            local example2 "graph export result.png, replace"
            local explain2 "把当前图形导出为 PNG 文件。"
        }
        else if "`cmd'" == "set" {
            local title "set — 设置默认图形方案"
            local purpose1 "用 Stata 官方 set scheme 命令修改后续新图形默认使用的 scheme。"
            local purpose2 "单张图的宽高和整体缩放属于绘图命令 options：在具体图形页使用 xsize()/ysize()/scale()；本页只负责默认 scheme。"
            local expr_label "set 后面的图形设置（通常填写 scheme 方案名 [, permanently]）"
            local example1 "set scheme stcolor"
            local explain1 "把当前会话后续新图形的默认 scheme 设为 Stata 18 默认的 stcolor。"
            local example2 "set scheme s2color, permanently"
            local explain2 "把 s2color 保存为以后启动 Stata 时继续使用的默认 scheme。"
        }
'''
s = once(s, old_graph, new_graph, "graph/set semantics")
sp.write_text(s, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor2 = 'if \'if c(stata_version) >= 17 local view "didregress xtdidregress"\' not in registry:\n    fail("Stata 17+ causal navigation must surface DID estimators first")\n'
checks = '''if 'inlist(`"`method\'"\', "更改方案/大小", "graph_scheme") local view "set"' not in registry:
    fail("Graphics scheme/size navigation must route to the real Stata set command")
if 'local title "set — 设置默认图形方案"' not in semantics:
    fail("set must have dedicated graphics-scheme semantics")
if 'local title "graph — 管理、保存与输出图形"' not in semantics:
    fail("graph management must have dedicated semantics")
'''
v = once(v, anchor2, anchor2 + checks, "graphics settings static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_GRAPH_SETTINGS_PATCH_OK")
