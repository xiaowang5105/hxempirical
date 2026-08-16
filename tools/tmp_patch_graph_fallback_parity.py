from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

# Registry: route Survival analysis graph to the actual sts graph subcommand alias.
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.32  16aug2026", "*! hxregistry 3.1.33  16aug2026", "registry version")
r = once(r, ' roctab rocfit roccomp rocgold rocreg screeplot ', ' roctab rocfit roccomp rocgold rocreg sts_graph screeplot ', "sts graph catalog")
r = once(r, 'else if inlist(`"`method\'"\', "生存分析图", "survival_graph") local view "sts"', 'else if inlist(`"`method\'"\', "生存分析图", "survival_graph") local view "sts_graph"', "survival graph route")
rp.write_text(r, encoding="utf-8", newline="\n")

# Resolver: probe the native sts parent command for the stable UI alias.
xp = Path("hxresolve.ado")
x = xp.read_text(encoding="utf-8")
x = once(x, "*! hxresolve 3.1.5  16aug2026", "*! hxresolve 3.1.6  16aug2026", "resolver version")
x = once(x, '    else if "`cmd\'" == "cluster_dendrogram" local probe_cmd "cluster"', '    else if "`cmd\'" == "cluster_dendrogram" local probe_cmd "cluster"\n    else if "`cmd\'" == "sts_graph" local probe_cmd "sts"', "sts graph resolver alias")
xp.write_text(x, encoding="utf-8", newline="\n")

# Preview: multiword aliases must emit runnable Stata syntax.
pp = Path("hxpreview.ado")
p = pp.read_text(encoding="utf-8")
p = once(p, "*! hxpreview 1.3.2  16aug2026", "*! hxpreview 1.3.3  16aug2026", "preview version")
p = once(p, '    if "`command\'" == "graph_combine" local preview "graph combine"', '    if "`command\'" == "graph_combine" local preview "graph combine"\n    if "`command\'" == "cluster_dendrogram" local preview "cluster dendrogram"\n    if "`command\'" == "sts_graph" local preview "sts graph"', "native multiword preview aliases")
pp.write_text(p, encoding="utf-8", newline="\n")

# Semantics: survival graph gets a graph-specific task page rather than the broad sts workflow page.
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.28  16aug2026", "*! hxsemantics 1.4.29  16aug2026", "semantics version")
s = once(s, ' sts irf graph set screeplot ', ' sts sts_graph irf graph set screeplot ', "sts graph command-body inclusion")
marker = '''        else if "`cmd'" == "screeplot" {
'''
block = '''        else if "`cmd'" == "sts_graph" {
            local title "sts graph — 生存函数图"
            local purpose1 "在已经 stset 的生存数据上绘制 Kaplan–Meier 生存曲线、失败函数等非参数生存图。"
            local purpose2 "失败事件和分析时间沿用当前 stset；分组、failure、risktable 等设置写在 sts graph 的原生 options 中。"
            local expr_label "sts graph 后面的 options（可留空；例如 , by(treat)）"
            local example1 "sts graph"
            local explain1 "绘制当前 stset 数据的默认 Kaplan–Meier 生存曲线。"
            local example2 "sts graph, by(treat)"
            local explain2 "按 treat 分组绘制生存曲线。"
        }
        else if "`cmd'" == "screeplot" {
'''
s = once(s, marker, block, "sts graph semantics")
sp.write_text(s, encoding="utf-8", newline="\n")

# Java: keep fallback navigation aligned with registry and normalize multiword aliases for Help.
jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")
repls = [
    ('return Collections.singletonList("twoway");', 'return Collections.singletonList("graph_bar");', 'bar fallback'),
    ('}          else if ("点图".equals(var0)) {\n            return Collections.singletonList("dotplot");', '}          else if ("点图".equals(var0)) {\n            return Collections.singletonList("graph_dot");', 'dot fallback'),
    ('}          else if ("饼图".equals(var0)) {\n            return Collections.singletonList("graph");', '}          else if ("饼图".equals(var0)) {\n            return Collections.singletonList("graph_pie");', 'pie fallback'),
    ('}          else if ("等高线图".equals(var0)) {\n            return Collections.singletonList("twoway");', '}          else if ("等高线图".equals(var0)) {\n            return Collections.singletonList("twoway_contour");', 'contour fallback'),
    ('}          else if ("散点图矩阵".equals(var0)) {\n            return Collections.singletonList("graph");', '}          else if ("散点图矩阵".equals(var0)) {\n            return Collections.singletonList("graph_matrix");', 'matrix fallback'),
    ('}          else if ("生存分析图".equals(var0)) {\n            return Collections.singletonList("sts");', '}          else if ("生存分析图".equals(var0)) {\n            return Collections.singletonList("sts_graph");', 'survival fallback'),
    ('}          else if ("质量控制".equals(var0)) {\n            return Collections.singletonList("graph");', '}          else if ("质量控制".equals(var0)) {\n            return Arrays.asList("cchart", "pchart", "rchart", "xchart", "shewhart", "serrbar");', 'quality fallback'),
    ('}          else if ("图形组合".equals(var0)) {\n            return Collections.singletonList("graph");', '}          else if ("图形组合".equals(var0)) {\n            return Collections.singletonList("graph_combine");', 'combine fallback'),
    ('}          else if ("更改方案/大小".equals(var0)) {\n            return Collections.singletonList("graph");', '}          else if ("更改方案/大小".equals(var0)) {\n            return Collections.singletonList("set");', 'scheme fallback'),
    ('} else if ("导入与转换".equals(var0)) {\n            return Collections.singletonList("hxconvert");', '} else if ("导入与转换".equals(var0)) {\n            return Arrays.asList("use", "import", "export", "save");', 'data io fallback'),
    ('} else if ("数据检查".equals(var0)) {\n            return Arrays.asList("misstable", "duplicates");', '} else if ("数据检查".equals(var0)) {\n            return Arrays.asList("describe", "codebook", "isid", "assert", "count", "compare", "duplicates", "misstable");', 'data check fallback'),
    ('} else if ("变量处理".equals(var0)) {\n            return Arrays.asList("generate", "replace", "encode", "decode", "destring", "tostring", "winsor2");', '} else if ("变量处理".equals(var0)) {\n            return Arrays.asList("generate", "egen", "replace", "recode", "clonevar", "split", "rename", "order", "label", "format", "compress", "encode", "decode", "destring", "tostring", "winsor2");', 'variable fallback'),
]
for old, new, label in repls:
    j = once(j, old, new, label)
# The first generic twoway replacement above is deliberately anchored by uniqueness; verify it still belongs to 条形图.
if '}          else if ("条形图".equals(var0)) {\n            return Collections.singletonList("graph_bar");' not in j:
    raise SystemExit('bar fallback context mismatch')
j = once(j, '} else if ("样本处理".equals(var0)) {\n            return Arrays.asList("keep", "drop");', '} else if ("样本处理".equals(var0)) {\n            return Arrays.asList("keep", "drop", "expand");', 'sample fallback')
j = once(j, '} else if ("合并与追加".equals(var0)) {\n            return Arrays.asList("merge", "append");', '} else if ("合并与追加".equals(var0)) {\n            return Arrays.asList("merge", "append", "joinby", "cross", "frlink", "frget");', 'combine data fallback')
j = once(j, '} else if ("数据结构".equals(var0)) {\n            return Arrays.asList("reshape", "collapse", "xtset", "tsset");', '} else if ("数据结构".equals(var0)) {\n            return Arrays.asList("reshape", "collapse", "contract", "fillin", "stack", "xpose", "sort", "gsort", "xtset", "tsset", "frame", "frames");', 'data structure fallback')
j = once(j, '            else if ("cluster_dendrogram".equals(var1)) var1 = "cluster dendrogram";', '            else if ("cluster_dendrogram".equals(var1)) var1 = "cluster dendrogram";\n            else if ("sts_graph".equals(var1)) var1 = "sts graph";', 'Java sts graph alias')
j = once(j, '            case "质量控制": return "质量控制相关图形";', '            case "质量控制": return "cchart · pchart · rchart · xchart · shewhart · serrbar";', 'quality graph preview')
jp.write_text(j, encoding="utf-8", newline="\n")

# Static contracts.
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'if \'else if ("cluster_dendrogram".equals(var1)) var1 = "cluster dendrogram";\' not in java:\n    fail("Java command preview must emit native cluster dendrogram syntax")\n'
checks = '''if 'local view "sts_graph"' not in registry:
    fail("Survival Graphics navigation must route to sts graph alias")
if 'if "`command\'" == "cluster_dendrogram" local preview "cluster dendrogram"' not in preview:
    fail("cluster dendrogram preview alias missing")
if 'if "`command\'" == "sts_graph" local preview "sts graph"' not in preview:
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
'''
v = once(v, anchor, anchor + checks, "graph/data fallback parity contracts")
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_GRAPH_FALLBACK_PARITY_PATCH_OK")
