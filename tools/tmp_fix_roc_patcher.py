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
p.write_text(s, encoding="utf-8", newline="\n")
print("HX_ROC_PATCHER_LOCATOR_FIXED")
