from pathlib import Path

p = Path('scripts/apply_consistent_category_ui_v129.py')
s = p.read_text(encoding='utf-8')
start = s.index('pattern = re.compile(')
end = s.index("java.write_text(s, encoding='utf-8')", start)
replacement = '''start_marker = '         this.setChooserBreadcrumb("开始  >  " + this.activeCategoryName);'
start_pos = s.find(start_marker)
if start_pos < 0:
    raise SystemExit('generic category fallback start not found')
end_marker = '         this.stageLayout.show(this.stageCards, "chooser");'
end_pos = s.find(end_marker, start_pos)
if end_pos < 0:
    raise SystemExit('generic category fallback end not found')
end_pos += len(end_marker)
s = s[:start_pos] + '         this.renderCompactGroupedOverview(var1, this.activeCategoryName, var2);' + s[end_pos:]

'''
s = s[:start] + replacement + s[end:]
p.write_text(s, encoding='utf-8')
print('temporary runner fixed')
