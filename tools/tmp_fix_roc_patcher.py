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
route_replacement = '''if '\"rocfit\"' in route_scope or '\"rocreg\"' in route_scope:
    fail("rocfit/rocreg are still routed as direct graph-producing commands")
if '\"rocregplot\"' not in route_scope:
    fail("rocregplot must route to the graph result view")
'''
s = s[:start] + route_replacement + s[end:]

p.write_text(s, encoding="utf-8", newline="\n")
print("HX_ROC_PATCHER_LOCATOR_FIXED")
