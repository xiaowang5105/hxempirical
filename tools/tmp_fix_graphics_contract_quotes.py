from pathlib import Path
import json

p = Path("tools/verify_static_contracts.py")
text = p.read_text(encoding="utf-8")
lines = text.splitlines()
out = []
changed = 0
for line in lines:
    stripped = line.strip()
    if ("local preview" in line or "probe_cmd" in line) and stripped.startswith("'") and stripped.endswith("',"):
        inner = stripped[1:-2]
        indent = line[: len(line) - len(line.lstrip())]
        line = indent + json.dumps(inner, ensure_ascii=False) + ","
        changed += 1
    out.append(line)
if changed != 8:
    raise SystemExit(f"expected 8 Graphics quote repairs, got {changed}")
text = "\n".join(out) + "\n"
load_anchor = 'semantics = read("hxsemantics.ado")\n'
if load_anchor not in text:
    raise SystemExit("static verifier semantics load anchor missing")
if 'preview = read("hxpreview.ado")' not in text:
    text = text.replace(
        load_anchor,
        load_anchor + 'preview = read("hxpreview.ado")\nresolve = read("hxresolve.ado")\n',
        1,
    )
p.write_text(text, encoding="utf-8", newline="\n")
print("HX_GRAPHICS_CONTRACT_QUOTES_AND_INPUTS_OK")
