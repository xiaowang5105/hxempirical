from pathlib import Path

p = Path("tools/tmp_patch_roc_roles.py")
s = p.read_text(encoding="utf-8")

old = '''title_anchor = ''' + "'''" + '''         } else if (Arrays.asList(\"roctab\", \"roccomp\").contains(var1)) {
''' + "'''" + '''
'''
new = '''title_anchor = ''' + "'''" + '''         } else if (Arrays.asList(\"roctab\", \"roccomp\").contains(var1)) {
            boolean compareRoc = \"roccomp\".equals(var1);
''' + "'''" + '''
'''
if s.count(old) != 1:
    raise SystemExit(f"ROC title locator patch expected 1 match, got {s.count(old)}")
s = s.replace(old, new, 1)

old_count = '''    2,
    "ROC generic headings",
'''
new_count = '''    1,
    "ROC generic headings",
'''
if s.count(old_count) != 1:
    raise SystemExit(f"ROC generic-heading count patch expected 1 match, got {s.count(old_count)}")
s = s.replace(old_count, new_count, 1)

route_start_marker = "if '\"roctab\", \"rocfit\", \"roccomp\", \"rocgold\", \"rocreg\","
start = s.find(route_start_marker)
end = s.find("for needle in (", start)
if start < 0 or end < 0:
    raise SystemExit("ROC broken route-contract block not found")
route_replacement = '''roc_route_start = java.find('\"graph_bar\", \"graph_dot\", \"graph_pie\", \"graph_box\", \"twoway_contour\", \"graph_matrix\"')
roc_route_end = java.find('this.selectResultView(\"graph\", true);', roc_route_start)
if roc_route_start < 0 or roc_route_end < 0:
    fail("ROC graph-result route block missing")
roc_route_scope = java[roc_route_start:roc_route_end]
if '\"rocfit\"' in roc_route_scope or '\"rocreg\"' in roc_route_scope:
    fail("rocfit/rocreg are still routed as direct graph-producing commands")
if '\"rocregplot\"' not in roc_route_scope:
    fail("rocregplot must route to the graph result view")
'''
s = s[:start] + route_replacement + s[end:]
p.write_text(s, encoding="utf-8", newline="\n")

# Synchronize existing Graphics contracts with the expanded ROC menu before the main patch adds new checks.
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
old_special = 'special_open = \'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "graph_matrix", "twoway_contour", "tsline", "xtline", "sts_graph", "roctab", "roccomp", "did_trends", "twoway").contains(var1)\''
new_special = 'special_open = \'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "graph_matrix", "twoway_contour", "tsline", "xtline", "sts_graph", "roctab", "roccomp", "rocgold", "did_trends", "twoway").contains(var1)\''
if v.count(old_special) != 1:
    raise SystemExit(f"structured Graphics special_open expected 1 old match, got {v.count(old_special)}")
v = v.replace(old_special, new_special, 1)

old_preview = 'case "ROC分析": return "roctab · rocfit · roccomp · rocgold · rocreg";'
new_preview = 'case "ROC分析": return "roctab · rocfit · roccomp · rocgold · rocreg · rocregplot";'
if v.count(old_preview) != 1:
    raise SystemExit(f"ROC method-card preview contract expected 1 old match, got {v.count(old_preview)}")
v = v.replace(old_preview, new_preview, 1)
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_ROC_PATCHER_LOCATOR_FIXED")
