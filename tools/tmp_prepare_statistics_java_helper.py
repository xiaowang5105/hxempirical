from pathlib import Path

p = Path("tools/tmp_patch_statistics_java_parity.py")
s = p.read_text(encoding="utf-8")
old = '''key_pat = re.compile(r'(case "项目反应理论\\(IRT\\)":\\s*\\n\\s*return "irt";)')
if 'case "DSGE模型"' not in j:
    j, n = key_pat.subn(r'\\1\\n            case "DSGE模型":\\n               return "dsge";', j, count=1)
    if n != 1:
        raise SystemExit(f"DSGE method-key insertion failed: {n}")
'''
new = '''key_pat = re.compile(r'(case "项目反应理论\\(IRT\\)":\\s*\\n\\s*return "irt";)')
if not re.search(r'case "DSGE模型":\\s*\\n\\s*return "dsge";', j):
    j, n = key_pat.subn(r'\\1\\n            case "DSGE模型":\\n               return "dsge";', j, count=1)
    if n != 1:
        raise SystemExit(f"DSGE method-key insertion failed: {n}")
'''
if s.count(old) != 1:
    raise SystemExit(f"DSGE helper condition expected once, got {s.count(old)}")
s = s.replace(old, new, 1)
old_contract = '''    'case "DSGE模型": return "dsge · dsgenl";',
):'''
new_contract = '''    'case "DSGE模型": return "dsge · dsgenl";',
    'case "DSGE模型":',
    'return "dsge";',
):'''
if s.count(old_contract) != 1:
    raise SystemExit(f"DSGE contract anchor expected once, got {s.count(old_contract)}")
s = s.replace(old_contract, new_contract, 1)
p.write_text(s, encoding="utf-8", newline="\n")
print("HX_STATISTICS_JAVA_HELPER_PREPARED")
