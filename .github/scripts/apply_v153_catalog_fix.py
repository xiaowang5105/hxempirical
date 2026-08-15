from pathlib import Path


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"missing patch anchor: {label}")
    return text.replace(old, new, 1)

src = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
s = src.read_text(encoding="utf-8")

# Version.
s = replace_once(s, 'public static final String VERSION = "1.5.2";', 'public static final String VERSION = "1.5.3";', 'java version')

# The category overview used an orphan panel (chooserContent) while the visible
# JScrollPane was bound to chooserResultsHost.  Unify both category and command
# views on the same visible host.
s = replace_once(
    s,
    '      private final JPanel chooserContent = new JPanel();\n',
    '      private JComponent chooserToolbar;\n',
    'chooserContent field',
)
s = s.replace('this.chooserContent', 'this.chooserResultsHost')
if 'chooserContent' in s:
    raise SystemExit('chooserContent still referenced after host unification')

# Keep a reference to the command-level toolbar so category pages can hide it.
s = replace_once(
    s,
    '         catalog.add(this.buildChooserToolbar(), BorderLayout.NORTH);',
    '         this.chooserToolbar = this.buildChooserToolbar();\n         catalog.add(this.chooserToolbar, BorderLayout.NORTH);',
    'chooser toolbar binding',
)

# Category overview state: hide command filters, clear stale command inspector,
# and render into the visible host.
s = replace_once(
    s,
    '      private void finishGroupedOverview() {\n         this.chooserResultsHost.add(Box.createVerticalGlue());',
    '      private void finishGroupedOverview() {\n         this.chooserResultsHost.add(Box.createVerticalGlue());\n         if (this.chooserToolbar != null) this.chooserToolbar.setVisible(false);\n         this.updateChooserInspector("");',
    'finish grouped overview',
)

# Stats had a duplicated finish block; give it the same toolbar/inspector state.
s = replace_once(
    s,
    '         this.chooserResultsHost.add(Box.createVerticalGlue());\n         this.chooserReady = true;\n         this.chooserAtCategoryLevel = true;\n         this.configureChooserBack();\n         this.homeButton.setVisible(true);\n         this.homeButton.setEnabled(true);\n         this.inspectorToggle.setVisible(false);\n         this.chooserResultsHost.revalidate();\n         this.chooserResultsHost.repaint();\n         this.stageLayout.show(this.stageCards, "chooser");\n      }\n\n      private void browseCategoryOverview',
    '         this.finishGroupedOverview();\n      }\n\n      private void browseCategoryOverview',
    'stats finish block',
)

# A method/command page uses the toolbar and is not category-level navigation.
s = replace_once(
    s,
    '         this.chooserHint.setText("快速定位命令，支持搜索、筛选和分类浏览。");\n         this.chooserReady = false;',
    '         this.chooserHint.setText("快速定位命令，支持搜索、筛选和分类浏览。");\n         this.chooserReady = false;\n         this.chooserAtCategoryLevel = false;\n         if (this.chooserToolbar != null) this.chooserToolbar.setVisible(true);',
    'render command chooser state',
)

# Category navigation is part of the Java UI and must never disappear because a
# Stata-side characteristic is unavailable.  Use the shipped local catalog as
# the baseline and append any live registry additions.
old_category = '''         ArrayList<String> var2 = new ArrayList<>();
         if (this.previewMode) {
            var2.addAll(previewMethodsForCategory(var1));
         } else {
            int var3 = HxWorkbench.StataBridge.execute("quietly hxregistry, category(" + var1 + ")", false);
            if (var3 == 0) {
               var2.addAll(HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_method_view")));
            }
         }
'''
new_category = '''         LinkedHashSet<String> methodSet = new LinkedHashSet<>(previewMethodsForCategory(var1));
         if (!this.previewMode) {
            int var3 = HxWorkbench.StataBridge.execute("quietly hxregistry, category(" + var1 + ")", false);
            if (var3 == 0) {
               methodSet.addAll(HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_method_view")));
            }
         }
         ArrayList<String> var2 = new ArrayList<>(methodSet);
'''
s = replace_once(s, old_category, new_category, 'category registry fallback')

# Same rule at method level: local command catalog is the baseline; live registry
# can add commands, but an empty/failed characteristic cannot blank the page.
old_method = '''         this.commandList.clearSelection();
         this.commandModel.clear();
         if (this.previewMode) {
            for (String var4 : previewCommandsForMethod(var2)) {
               this.commandModel.addElement(var4);
            }
         } else {
            int var6 = HxWorkbench.StataBridge.execute("quietly hxregistry, method(" + HxWorkbench.StataBridge.methodCode(var2) + ")", false);
            if (var6 == 0) {
               for (String var5 : HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_command_view"))) {
                  this.commandModel.addElement(var5);
               }
            }
         }
'''
new_method = '''         this.commandList.clearSelection();
         this.commandModel.clear();
         LinkedHashSet<String> commandSet = new LinkedHashSet<>(previewCommandsForMethod(var2));
         if (!this.previewMode) {
            int var6 = HxWorkbench.StataBridge.execute("quietly hxregistry, method(" + HxWorkbench.StataBridge.methodCode(var2) + ")", false);
            if (var6 == 0) {
               commandSet.addAll(HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_command_view")));
            }
         }
         for (String var5 : commandSet) {
            if (var5 != null && !var5.isBlank()) this.commandModel.addElement(var5);
         }
'''
s = replace_once(s, old_method, new_method, 'method registry fallback')

src.write_text(s, encoding="utf-8")

# Release-facing text/version files.
for name in ["hxempirical.ado", "hxempirical.sthlp", "hxinstaller.ado", "hxinstall.do", "README.md", "INSTALL.md"]:
    p = Path(name)
    t = p.read_text(encoding="utf-8")
    t = t.replace("1.5.2", "1.5.3")
    p.write_text(t, encoding="utf-8")

pkg = Path("hxempirical.pkg")
t = pkg.read_text(encoding="utf-8").replace("d Version 1.5.2", "d Version 1.5.3")
pkg.write_text(t, encoding="utf-8")

# Add an explicit release note near the top of the README without disturbing the
# rest of the existing documentation.
readme = Path("README.md")nt = readme.read_text(encoding="utf-8")
marker = "### 安装或更新\n"
note = """### 1.5.3 目录显示修复\n\n- 修复“数据 / 统计 / 图形”等一级目录进入后内容为空的问题：分类页与命令页现在统一渲染到实际可见的目录容器。\n- 分类导航以随 JAR 发布的本地目录为稳定基线，并合并 Stata 侧 `hxregistry` 的新增项；即使运行时 characteristic 暂时不可用，也不会把整个目录清空。\n- 分类页隐藏仅适用于命令列表的“全部 / 常用 / 官方 / 外部扩展 / 进阶”筛选，进入具体方法后再显示。\n\n"""
if marker not in nt:
    raise SystemExit('README installation marker missing')
nt = nt.replace(marker, note + marker, 1)
readme.write_text(nt, encoding="utf-8")

print("HX_V153_PATCH_OK")
