from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"missing pattern: {label}")
    return text.replace(old, new, 1)


java_path = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
java = java_path.read_text(encoding="utf-8")

# Idempotent guard for the second workflow run after the generated commit.
if 'public static final String VERSION = "1.0.1";' not in java:
    java = replace_once(java, 'public static final String VERSION = "0.9.7";', 'public static final String VERSION = "1.0.1";', 'java version constant')
    java = replace_once(java, 'SFIToolkit.displayln("HxWorkbench 0.9.7");', 'SFIToolkit.displayln("HxWorkbench 1.0.1");', 'java version output')

    java = replace_once(
        java,
        'private final JLabel breadcrumbLabel = new JLabel("开始");',
        'private final JPanel breadcrumbBar = new JPanel(new FlowLayout(FlowLayout.LEFT, 0, 0));',
        'workspace breadcrumb field',
    )
    java = replace_once(java, 'private final JButton homeButton = new JButton("回到开始");', 'private final JButton homeButton = new JButton("首页");', 'workspace home label')
    java = replace_once(java, 'private final JButton changeMethodButton = new JButton("更换方法");', 'private final JButton changeMethodButton = new JButton("← 上一级");', 'workspace back label')
    java = replace_once(
        java,
        'private final JLabel chooserBreadcrumb = new JLabel("开始");',
        'private final JPanel chooserBreadcrumbBar = new JPanel(new FlowLayout(FlowLayout.LEFT, 0, 0));',
        'chooser breadcrumb field',
    )
    java = replace_once(
        java,
        'private final JButton chooserBackButton = new JButton("← 返回开始");',
        'private final JButton chooserBackButton = new JButton("← 上一级");\n      private final JButton chooserHomeButton = new JButton("首页");',
        'chooser navigation fields',
    )

    java = replace_once(
        java,
        '''         styleSecondaryButton(this.homeButton);\n         styleSecondaryButton(this.inspectorToggle);\n         this.homeButton.addActionListener(var1x -> this.showHomePage());\n         this.inspectorToggle.addActionListener(var1x -> this.toggleInspector());\n         JPanel var6 = new JPanel(new FlowLayout(2, 10, 0));\n         var6.setOpaque(false);\n         var6.add(var5);\n         var6.add(this.inspectorToggle);\n         var6.add(this.homeButton);''',
        '''         styleSecondaryButton(this.inspectorToggle);\n         this.inspectorToggle.addActionListener(var1x -> this.toggleInspector());\n         JPanel var6 = new JPanel(new FlowLayout(2, 10, 0));\n         var6.setOpaque(false);\n         var6.add(var5);\n         var6.add(this.inspectorToggle);''',
        'remove global home button from app header',
    )

    java = replace_once(
        java,
        '''         this.breadcrumbLabel.setForeground(ACCENT);\n         this.breadcrumbLabel.setFont(this.breadcrumbLabel.getFont().deriveFont(0, 10.5F));\n         this.breadcrumbLabel.setCursor(Cursor.getPredefinedCursor(12));''',
        '''         this.breadcrumbBar.setOpaque(false);\n         this.breadcrumbBar.setAlignmentX(0.0F);''',
        'workspace breadcrumb styling',
    )

    java = replace_once(
        java,
        '''         styleSecondaryButton(this.changeMethodButton);\n         this.changeMethodButton.addActionListener(var1x -> {''',
        '''         styleSecondaryButton(this.changeMethodButton);\n         styleSecondaryButton(this.homeButton);\n         this.homeButton.addActionListener(var1x -> this.showHomePage());\n         this.changeMethodButton.addActionListener(var1x -> {''',
        'workspace nav button wiring',
    )
    java = replace_once(
        java,
        '''         var5.setOpaque(false);\n         var5.add(this.changeMethodButton);\n         var5.add(var4);''',
        '''         var5.setOpaque(false);\n         var5.add(this.changeMethodButton);\n         var5.add(this.homeButton);\n         var5.add(var4);''',
        'workspace nav button placement',
    )
    java = replace_once(
        java,
        '''         this.breadcrumbLabel.setAlignmentX(0.0F);\n         this.breadcrumbLabel.setMaximumSize(new Dimension(Integer.MAX_VALUE, 22));\n         var3.setAlignmentX(0.0F);''',
        '''         this.breadcrumbBar.setAlignmentX(0.0F);\n         this.breadcrumbBar.setMaximumSize(new Dimension(Integer.MAX_VALUE, 22));\n         var3.setAlignmentX(0.0F);''',
        'workspace breadcrumb layout',
    )
    java = replace_once(java, 'var6.add(this.breadcrumbLabel);', 'var6.add(this.breadcrumbBar);', 'workspace breadcrumb component')

    java = replace_once(
        java,
        '''         styleSecondaryButton(this.chooserBackButton);\n         this.chooserBackButton.addActionListener(var1x -> this.handleChooserBack());\n         JPanel var3 = new JPanel(new FlowLayout(0, 0, 0));\n         var3.setOpaque(false);\n         var3.add(this.chooserBackButton);\n         var2.add(var3, "West");\n         this.chooserBreadcrumb.setForeground(ACCENT);\n         this.chooserBreadcrumb.setFont(this.chooserBreadcrumb.getFont().deriveFont(11.0F));''',
        '''         styleSecondaryButton(this.chooserBackButton);\n         styleSecondaryButton(this.chooserHomeButton);\n         this.chooserBackButton.addActionListener(var1x -> this.handleChooserBack());\n         this.chooserHomeButton.addActionListener(var1x -> this.showHomePage());\n         JPanel var3 = new JPanel(new FlowLayout(0, 7, 0));\n         var3.setOpaque(false);\n         var3.add(this.chooserBackButton);\n         var3.add(this.chooserHomeButton);\n         var2.add(var3, "West");\n         this.chooserBreadcrumbBar.setOpaque(false);''',
        'chooser nav controls',
    )
    java = replace_once(java, 'var4.add(this.chooserBreadcrumb);', 'var4.add(this.chooserBreadcrumbBar);', 'chooser breadcrumb component')

    java = java.replace('this.breadcrumbLabel.setText(', 'this.setWorkspaceBreadcrumb(')
    java = java.replace('this.chooserBreadcrumb.setText(', 'this.setChooserBreadcrumb(')

    java = replace_once(
        java,
        '''      private void configureChooserBack() {\n         boolean var1 = !this.chooserAtCategoryLevel\n            && !this.activeCategoryName.isBlank()\n            && !"search".equals(this.activeCategoryCode)\n            && !"favorites".equals(this.activeCategoryCode)\n            && !"recent".equals(this.activeCategoryCode);\n         this.chooserBackButton.setVisible(var1);\n         if (var1) {\n            this.chooserBackButton.setText("← 返回" + this.activeCategoryName);\n            this.chooserBackButton.setToolTipText("查看" + this.activeCategoryName + "中的其他方法");\n         }\n      }''',
        '''      private void configureChooserBack() {\n         this.chooserBackButton.setVisible(true);\n         this.chooserBackButton.setText("← 上一级");\n         this.chooserBackButton.setToolTipText(this.chooserAtCategoryLevel ? "返回首页" : "返回上一级选择");\n         this.chooserHomeButton.setVisible(true);\n         this.chooserHomeButton.setToolTipText("返回首页");\n      }''',
        'chooser back behavior',
    )

    old_workspace_back = '''      private void configureWorkspaceBack() {\n         String var1 = this.activeMethodName == null ? "" : this.activeMethodName.trim();\n         if (!var1.isBlank() && !var1.equals(this.activeCategoryName)) {\n            this.changeMethodButton.setText("← 返回" + var1);\n            this.changeMethodButton.setToolTipText("查看" + var1 + "中的其他命令");\n            this.breadcrumbLabel.setToolTipText("返回" + var1 + "命令选择页");\n         } else {\n            this.changeMethodButton.setText("← 返回上一层");\n            this.changeMethodButton.setToolTipText("返回刚才的选择页面");\n            this.breadcrumbLabel.setToolTipText("返回刚才的选择页面");\n         }\n      }'''
    new_workspace_back = '''      private void configureWorkspaceBack() {\n         this.changeMethodButton.setText("← 上一级");\n         String var1 = this.activeMethodName == null ? "" : this.activeMethodName.trim();\n         this.changeMethodButton.setToolTipText(!var1.isBlank() && !var1.equals(this.activeCategoryName) ? "返回当前方法的命令选择页" : "返回上一级选择");\n         this.homeButton.setText("首页");\n         this.homeButton.setToolTipText("返回首页");\n      }\n\n      private void setWorkspaceBreadcrumb(String path) {\n         this.renderBreadcrumb(this.breadcrumbBar, path);\n      }\n\n      private void setChooserBreadcrumb(String path) {\n         this.renderBreadcrumb(this.chooserBreadcrumbBar, path);\n      }\n\n      private void renderBreadcrumb(JPanel bar, String path) {\n         bar.removeAll();\n         ArrayList<String> parts = new ArrayList<>();\n         for (String raw : path.split("\\\\s*[›>]\\\\s*")) {\n            String part = raw.trim();\n            if (!part.isBlank() && !"开始".equals(part) && !"首页".equals(part)) {\n               parts.add(part);\n            }\n         }\n\n         this.addBreadcrumbItem(bar, "首页", this::showHomePage, parts.isEmpty());\n         for (int i = 0; i < parts.size(); i++) {\n            JLabel sep = new JLabel("  ›  ");\n            sep.setForeground(MUTED);\n            sep.setFont(sep.getFont().deriveFont(11.0F));\n            bar.add(sep);\n            Runnable action = null;\n            boolean current = i == parts.size() - 1;\n            if (!current && i == 0) {\n               action = this::openActiveCategoryFromBreadcrumb;\n            } else if (!current && i == 1 && this.activeMethodName != null && !this.activeMethodName.isBlank() && !this.activeMethodName.equals(this.activeCategoryName)) {\n               action = () -> this.browseMethod(this.activeCategoryCode, this.activeMethodName);\n            }\n            this.addBreadcrumbItem(bar, parts.get(i), action, current);\n         }\n         bar.revalidate();\n         bar.repaint();\n      }\n\n      private void openActiveCategoryFromBreadcrumb() {\n         if (this.activeCategoryCode == null || this.activeCategoryCode.isBlank() || "search".equals(this.activeCategoryCode)) {\n            this.showHomePage();\n         } else if ("favorites".equals(this.activeCategoryCode) || "recent".equals(this.activeCategoryCode)) {\n            this.browseCommandCategory(this.activeCategoryCode, this.activeCategoryName);\n         } else if ("test".equals(this.activeCategoryCode) || "performance".equals(this.activeCategoryCode)) {\n            this.showHomePage();\n         } else {\n            this.browseCategoryOverview(this.activeCategoryCode);\n         }\n      }\n\n      private void addBreadcrumbItem(JPanel bar, String text, Runnable action, boolean current) {\n         JLabel item = new JLabel(text);\n         item.setFont(item.getFont().deriveFont(current ? Font.BOLD : Font.PLAIN, 11.0F));\n         item.setForeground(current ? TEXT : ACCENT);\n         if (action != null && !current) {\n            item.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));\n            item.setToolTipText("打开“" + text + "”");\n            item.addMouseListener(new MouseAdapter() {\n               @Override\n               public void mouseClicked(MouseEvent event) {\n                  action.run();\n               }\n\n               @Override\n               public void mouseEntered(MouseEvent event) {\n                  item.setForeground(ACCENT.darker());\n               }\n\n               @Override\n               public void mouseExited(MouseEvent event) {\n                  item.setForeground(ACCENT);\n               }\n            });\n         }\n         bar.add(item);\n      }'''
    java = replace_once(java, old_workspace_back, new_workspace_back, 'workspace back and breadcrumb helpers')

    java = replace_once(
        java,
        '''      private void wireEvents() {\n         this.chooserBreadcrumb.setCursor(Cursor.getPredefinedCursor(12));\n         this.chooserBreadcrumb.setToolTipText("返回上一层");\n         this.chooserBreadcrumb.addMouseListener(new MouseAdapter() {\n            @Override\n            public void mouseClicked(MouseEvent var1) {\n               WorkbenchFrame.this.handleChooserBack();\n            }\n         });\n         this.breadcrumbLabel.addMouseListener(new MouseAdapter() {\n            @Override\n            public void mouseClicked(MouseEvent var1) {\n               if (WorkbenchFrame.this.chooserReady) {\n                  WorkbenchFrame.this.changeMethodButton.doClick();\n               }\n            }\n         });''',
        '''      private void wireEvents() {''',
        'remove whole-breadcrumb click handlers',
    )

    java = replace_once(
        java,
        '''         var24.setBorder(null);\n         var24.getViewport().setBackground(APP_BG);\n         var24.getVerticalScrollBar().setUnitIncrement(18);''',
        '''         var24.setBorder(null);\n         var24.getViewport().setBackground(APP_BG);\n         var24.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);\n         var24.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);\n         var24.getVerticalScrollBar().setPreferredSize(new Dimension(12, 0));\n         var24.getVerticalScrollBar().setUnitIncrement(18);''',
        'stable home scrollbar gutter',
    )
    java = replace_once(
        java,
        '''         var5.setBorder(null);\n         var5.getViewport().setBackground(APP_BG);\n         var5.getVerticalScrollBar().setUnitIncrement(18);''',
        '''         var5.setBorder(null);\n         var5.getViewport().setBackground(APP_BG);\n         var5.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);\n         var5.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);\n         var5.getVerticalScrollBar().setPreferredSize(new Dimension(12, 0));\n         var5.getVerticalScrollBar().setUnitIncrement(18);''',
        'stable chooser scrollbar gutter',
    )

    if 'breadcrumbLabel' in java or 'chooserBreadcrumb' in java:
        raise SystemExit('legacy breadcrumb component reference remains')

    java_path.write_text(java, encoding="utf-8")

# Version metadata and README release log.
def update_text_file(path: str, transforms):
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    for old, new, label in transforms:
        if old in text:
            text = text.replace(old, new, 1)
        elif new not in text:
            raise SystemExit(f"missing pattern: {label}")
    p.write_text(text, encoding="utf-8")

update_text_file('hxempirical.pkg', [('d Version 1.0.0', 'd Version 1.0.1', 'pkg version')])
update_text_file('hxempirical.ado', [
    ('*! hxempirical 1.0.0  12aug2026', '*! hxempirical 1.0.1  12aug2026', 'ado header'),
    ('display as text "版本：" as result "1.0.0"', 'display as text "版本：" as result "1.0.1"', 'about version'),
    ('return local version "1.0.0"', 'return local version "1.0.1"', 'return version'),
])
help_path = Path('hxempirical.sthlp')
help_text = help_path.read_text(encoding='utf-8')
if 'version 1.0.1' not in help_text:
    help_text = help_text.replace('{* *! version 1.0.0  12aug2026}{...}', '{* *! version 1.0.1  12aug2026}{...}', 1)
    help_text = help_text.replace('package version 1.0.0.', 'package version 1.0.1.', 1)
help_path.write_text(help_text, encoding='utf-8')

readme_path = Path('README.md')
readme = readme_path.read_text(encoding='utf-8')
if '### 1.0.1（当前版本）' not in readme:
    readme = replace_once(readme, '当前发布版本：**1.0.0**', '当前发布版本：**1.0.1**', 'README version')
    readme = replace_once(readme, '上次修改时间：**2026-08-12 15:46（UTC+8）**', '上次修改时间：**2026-08-12 16:07（UTC+8）**', 'README modification time')
    readme = replace_once(readme, '### 1.0.0（当前版本）', '### 1.0.0', 'previous version heading')
    marker = '## 版本记录\n\n'
    release = '''### 1.0.1（当前版本）\n\n**发布时间**：2026-08-12 16:07（UTC+8）\n\n**修改内容**：\n\n- 修复开始页“展开全部功能”前后因垂直滚动条出现/消失造成的页面宽度跳动；开始页与命令选择页固定预留滚动条区域，展开、收起时主内容不再左右位移。\n- 工作页面和命令选择页面统一使用两个固定导航键：`← 上一级` 与 `首页`；取消“返回 OneClick 专区”“返回某某方法”等随页面变化的长按钮文案，也不再把首页按钮单独放在顶栏右侧。\n- 面包屑路径改为真正的层级导航：`首页 › 分类 › 方法 › 当前命令`；首页、分类和方法等上级节点可直接点击，当前节点保持不可点击。\n- 导航层级和按钮职责统一：`上一级` 只回到父级，`首页` 始终直接回到开始页，避免同一页面出现两个含义相近但位置、文案不同的“返回”入口。\n- 同步修正 Java 工作台内部版本常量与版本输出，使 `HxWorkbench`、Stata 入口、package manifest、help 和 README 全部统一为 **1.0.1**；重新构建 `hxworkbench.jar` 并执行离线界面 smoke test。\n\n'''
    readme = replace_once(readme, marker, marker + release, 'README release insertion')
readme_path.write_text(readme, encoding='utf-8')

print('HX_UI_NAV_1_0_1_PATCH_OK')
