from pathlib import Path

root = Path(__file__).resolve().parents[1]
java_path = root / 'src/main/java/com/hexie/stata/HxWorkbench.java'
text = java_path.read_text(encoding='utf-8')

repls = {
'''         sidebar.setPreferredSize(new Dimension(210, 0));''': '''         sidebar.setPreferredSize(new Dimension(176, 0));''',
'''         nav.setBorder(new EmptyBorder(14, 11, 8, 11));''': '''         nav.setBorder(new EmptyBorder(12, 10, 8, 10));''',
'''         nav.add(this.sidebarButton("home", "首", "工作台", this::showHomePage));
         nav.add(Box.createVerticalStrut(4));
         nav.add(this.sidebarButton("data", "数", "数据", () -> this.browseCategoryOverview("data")));
         nav.add(Box.createVerticalStrut(4));
         nav.add(this.sidebarButton("stats", "统", "统计", () -> this.browseCategoryOverview("stats")));
         nav.add(Box.createVerticalStrut(4));
         nav.add(this.sidebarButton("graph", "图", "图形", () -> this.browseCategoryOverview("graph")));
         nav.add(Box.createVerticalStrut(4));
         nav.add(this.sidebarButton("oneclick", "O", "OneClick", () -> this.browseMethodCategory("oneclick")));
         nav.add(Box.createVerticalStrut(4));
         nav.add(this.sidebarButton("external", "外", "已下载外部命令", this::browseInstalledExternalCommands));
         nav.add(Box.createVerticalStrut(4));
         nav.add(this.sidebarButton("settings", "设", "设置", () -> this.openHomeTask("special", "performance")));''': '''         nav.add(this.sidebarButton("home", "", "工作台", this::showHomePage));
         nav.add(Box.createVerticalStrut(2));
         nav.add(this.sidebarButton("data", "", "数据", () -> this.browseCategoryOverview("data")));
         nav.add(Box.createVerticalStrut(2));
         nav.add(this.sidebarButton("stats", "", "统计", () -> this.browseCategoryOverview("stats")));
         nav.add(Box.createVerticalStrut(2));
         nav.add(this.sidebarButton("graph", "", "图形", () -> this.browseCategoryOverview("graph")));
         nav.add(Box.createVerticalStrut(2));
         nav.add(this.sidebarButton("oneclick", "", "OneClick", () -> this.browseMethodCategory("oneclick")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("external", "", "外部命令", this::browseInstalledExternalCommands));
         nav.add(Box.createVerticalStrut(2));
         nav.add(this.sidebarButton("settings", "", "设置", () -> this.openHomeTask("special", "performance")));''',
'''         int width = this.sidebarCollapsed ? 0 : 210;''': '''         int width = this.sidebarCollapsed ? 0 : 176;''',
'''            String glyph = Objects.toString(button.getClientProperty("hx.sidebar.glyph"), "");
            String expanded = glyph.isBlank() ? label : glyph + "   " + label;
            button.setText("<html><b>" + html(expanded) + "</b></html>");''': '''            button.setText(label);''',
'''         JButton button = new JButton("<html><b>" + html(label) + "</b></html>");''': '''         JButton button = new JButton(label);''',
'''         button.setBorder(new EmptyBorder(9, 12, 9, 12));
         button.setMaximumSize(new Dimension(Integer.MAX_VALUE, 40));''': '''         button.setBorder(new EmptyBorder(7, 12, 7, 12));
         button.setPreferredSize(new Dimension(156, 36));
         button.setMaximumSize(new Dimension(Integer.MAX_VALUE, 36));
         button.setFont(button.getFont().deriveFont(Font.BOLD, 13.0F));''',
'''         Color bg = active ? new Color(232, 241, 255) : SURFACE;
         Color hover = active ? new Color(224, 236, 253) : new Color(247, 249, 252);
         Color pressed = active ? new Color(213, 229, 251) : new Color(238, 243, 249);
         Color fg = active ? new Color(20, 96, 214) : new Color(43, 55, 73);
         button.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(bg, hover, pressed, fg, active ? new Color(210, 226, 249) : SURFACE));''': '''         Color bg = active ? new Color(235, 243, 255) : SURFACE;
         Color hover = active ? new Color(226, 238, 255) : new Color(247, 249, 252);
         Color pressed = active ? new Color(216, 232, 253) : new Color(238, 243, 249);
         Color fg = active ? new Color(18, 91, 196) : new Color(36, 48, 66);
         button.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(bg, hover, pressed, fg, active ? new Color(201, 221, 249) : SURFACE));'''
}

for old, new in repls.items():
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'expected exactly one match, got {count}: {old[:80]!r}')
    text = text.replace(old, new)

if text.count('public static final String VERSION = "1.5.5";') != 1:
    raise SystemExit('Java version marker mismatch')
text = text.replace('public static final String VERSION = "1.5.5";', 'public static final String VERSION = "1.5.6";', 1)
java_path.write_text(text, encoding='utf-8')

version_files = {
    'hxempirical.pkg': [('d Version 1.5.5', 'd Version 1.5.6')],
    'hxempirical.ado': [('*! hxempirical 1.5.5  15aug2026', '*! hxempirical 1.5.6  15aug2026'), ('"1.5.5"', '"1.5.6"')],
    'hxempirical.sthlp': [('{* *! version 1.5.5  15aug2026}{...}', '{* *! version 1.5.6  15aug2026}{...}'), ('The 1.5.5 interface', 'The 1.5.6 interface')],
    'hxinstall.do': [('1.5.5', '1.5.6')],
    'hxinstaller.ado': [('1.5.5', '1.5.6')],
    'INSTALL.md': [('当前版本：1.5.5', '当前版本：1.5.6'), ('最新版本：1.5.5', '最新版本：1.5.6')],
    'README.md': [('**当前发布版本：1.5.5**', '**当前发布版本：1.5.6**')],
}
for rel, pairs in version_files.items():
    p = root / rel
    s = p.read_text(encoding='utf-8')
    for old, new in pairs:
        if old not in s:
            raise SystemExit(f'missing version marker in {rel}: {old!r}')
        s = s.replace(old, new)
    p.write_text(s, encoding='utf-8')

readme = root / 'README.md'
s = readme.read_text(encoding='utf-8')
anchor = '### 1.5.5 OneClick 依赖与发布一致性\n'
insert = '''### 1.5.6 左侧导航重构\n\n- 左侧导航移除“首 / 数 / 统 / 图 / O / 外 / 设”等重复单字前缀，避免出现“数 数据”“O OneClick”这类视觉噪声。\n- 侧栏宽度由 210px 收紧到 176px，行高由 40px 收紧到 36px，导航间距同步压缩。\n- 菜单统一为“工作台 / 数据 / 统计 / 图形 / OneClick / 外部命令 / 设置”，保留浅蓝选中态并降低视觉重量。\n- 本次只调整导航信息层级与视觉密度，不改变命令功能和现有工作区逻辑。\n\n'''
if anchor not in s:
    raise SystemExit('README release anchor missing')
s = s.replace(anchor, insert + anchor, 1)
record_anchor = '## 版本记录\n\n'
record = '''### 1.5.6（当前版本）\n\n**发布时间**：2026-08-15（UTC+8）\n\n**修改内容**：\n\n- 重构左侧导航，去除重复单字前缀与 `O OneClick` 等视觉噪声。\n- 将侧栏宽度收紧至 176px、菜单行高收紧至 36px，并统一菜单文字和选中态。\n- 保持现有功能入口、命令逻辑和工作区行为不变。\n\n'''
if record_anchor not in s:
    raise SystemExit('README version record anchor missing')
s = s.replace(record_anchor, record_anchor + record, 1)
s = s.replace('### 1.5.5（当前版本）', '### 1.5.5', 1)
readme.write_text(s, encoding='utf-8')

print('HX_SIDEBAR_PATCH_OK')
