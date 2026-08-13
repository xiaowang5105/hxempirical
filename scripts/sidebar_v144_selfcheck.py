from pathlib import Path

p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')
assert 'public static final String VERSION = "1.4.3";' in s
assert 'SFIToolkit.displayln("HxWorkbench 1.4.3");' in s

s = s.replace('public static final String VERSION = "1.4.3";', 'public static final String VERSION = "1.4.4";', 1)
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.4.3");', 'SFIToolkit.displayln("HxWorkbench 1.4.4");', 1)

old = '''         JPanel center = new JPanel(new BorderLayout());
         center.setBackground(APP_BG);
         center.add(this.buildSidebarToggleBar(), BorderLayout.NORTH);
         center.add(this.stageCards, BorderLayout.CENTER);
         center.add(this.buildStatusBar(), BorderLayout.SOUTH);

         JPanel shell = new JPanel(new BorderLayout());
         shell.setBackground(APP_BG);
         shell.add(this.buildSidebar(), BorderLayout.WEST);
         shell.add(center, BorderLayout.CENTER);
'''
new = '''         JPanel center = new JPanel(new BorderLayout());
         center.setBackground(APP_BG);
         center.add(this.stageCards, BorderLayout.CENTER);
         center.add(this.buildStatusBar(), BorderLayout.SOUTH);

         JPanel shell = new JPanel(new BorderLayout());
         shell.setBackground(APP_BG);
         shell.add(this.buildSidebarToggleBar(), BorderLayout.NORTH);
         shell.add(this.buildSidebar(), BorderLayout.WEST);
         shell.add(center, BorderLayout.CENTER);
'''
assert old in s, 'expected center/shell layout block not found'
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')

ado = Path('hxempirical.ado')
a = ado.read_text(encoding='utf-8')
a = a.replace('*! hxempirical 1.4.3', '*! hxempirical 1.4.4', 1)
a = a.replace('版本：" as result "1.4.3"', '版本：" as result "1.4.4"', 1)
a = a.replace('return local version "1.4.3"', 'return local version "1.4.4"', 1)
ado.write_text(a, encoding='utf-8')

pkg = Path('hxempirical.pkg')
pkg.write_text(pkg.read_text(encoding='utf-8').replace('d Version 1.4.3', 'd Version 1.4.4', 1), encoding='utf-8')

hlp = Path('hxempirical.sthlp')
h = hlp.read_text(encoding='utf-8')
h = h.replace('{* *! version 1.4.3', '{* *! version 1.4.4', 1)
h = h.replace('The 1.4.3 interface uses a stable desktop-workbench layout: a fixed left\nnavigation rail,', 'The 1.4.4 interface uses a stable desktop-workbench layout: a collapsible left\nnavigation sidebar,', 1)
hlp.write_text(h, encoding='utf-8')

readme = Path('README.md')
r = readme.read_text(encoding='utf-8')
r = r.replace('当前发布版本：1.4.3', '当前发布版本：1.4.4', 1)
r = r.replace('上次修改时间：2026-08-13 15:53（UTC+8）', '上次修改时间：2026-08-13 16:03（UTC+8）', 1)
readme.write_text(r, encoding='utf-8')

print('SIDEBAR_V144_PATCH_OK')
