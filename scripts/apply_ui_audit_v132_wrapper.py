from pathlib import Path

p = Path('scripts/apply_ui_audit_v132.py')
s = p.read_text(encoding='utf-8')
old = "    s = s[:start] + replacement + '\\n\\n' + s[end:]"
new = "    trimmed = replacement.rstrip()\n    end_trimmed = end_marker.rstrip()\n    if trimmed.endswith(end_trimmed):\n        trimmed = trimmed[:-len(end_trimmed)].rstrip()\n    s = s[:start] + trimmed + '\\n\\n' + s[end:]"
if old not in s:
    raise SystemExit('replace_between implementation marker not found')
s = s.replace(old, new, 1)
code = compile(s, str(p), 'exec')
exec(code, {'__name__': '__main__', '__file__': str(p)})
