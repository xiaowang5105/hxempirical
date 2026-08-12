from pathlib import Path

path = Path('tools/complete_command_layer.py')
text = path.read_text(encoding='utf-8')
old = '''plot_marker = '    else if inlist("`cmd'", "marginsplot", "coefplot") {' '''.rstrip()
new = '''plot_marker = """    else if inlist("`cmd'", "marginsplot", "coefplot") {"""'''
if old not in text:
    # The exact invalid line contains no trailing whitespace; use line-wise replacement.
    lines = text.splitlines()
    changed = False
    for i, line in enumerate(lines):
        if line.startswith("plot_marker = '") and 'marginsplot' in line and 'coefplot' in line:
            lines[i] = new
            changed = True
            break
    if not changed:
        raise SystemExit('plot_marker line not found')
    text = '\n'.join(lines) + ('\n' if text.endswith('\n') else '')
else:
    text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('HX_REPAIR_COMPLETE_SCRIPT_OK')
