from pathlib import Path
import re

src = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = src.read_text(encoding='utf-8')

# Version.
s = s.replace('public static final String VERSION = "1.2.3";', 'public static final String VERSION = "1.2.4";', 1)
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.2.3");', 'SFIToolkit.displayln("HxWorkbench 1.2.4");', 1)
s = s.replace('new JLabel("版本：1.2.3")', 'new JLabel("版本：1.2.4")', 1)

# One shared inspector component for ordinary workspaces and OneClick.
field_anchor = '      private JPanel exactOneClickRoot;\n'
field_block = '''      private JPanel exactOneClickRoot;\n      private final JPanel exactOneClickInspectorHost = new JPanel(new BorderLayout());\n      private JComponent sharedDataInspector;\n'''
if field_anchor not in s:
    raise SystemExit('field anchor not found')
s = s.replace(field_anchor, field_block, 1)

ctor_old = '         this.commandDataSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, this.buildCommandContainer(), this.buildDataContainer());\n'
ctor_new = '''         this.sharedDataInspector = this.buildDataContainer();\n         this.commandDataSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, this.buildCommandContainer(), this.sharedDataInspector);\n'''
if ctor_old not in s:
    raise SystemExit('constructor inspector anchor not found')
s = s.replace(ctor_old, ctor_new, 1)

# Replace the OneClick-only fake Data / Results / Logs artwork with a host for the real shared inspector.
one_start = s.index('      private JComponent buildExactOneClickContainer()')
one_end = s.index('      private void showOneClickPage', one_start)
one = s[one_start:one_end]
pat = re.compile(r'\n\s*JPanel data = this\.refCard\(\); data\.setLayout\(null\); data\.setBounds\(780,115,660,695\);.*?root\.add\(data\);', re.S)
replacement = '''\n         this.exactOneClickInspectorHost.removeAll();\n         this.exactOneClickInspectorHost.setOpaque(false);\n         this.exactOneClickInspectorHost.setBounds(780,115,660,695);\n         root.add(this.exactOneClickInspectorHost);'''
one, n = pat.subn(replacement, one, count=1)
if n != 1:
    raise SystemExit(f'OneClick fake inspector replacement count={n}')
if 'JLabel tabs=new JLabel("数据      |      结果      |      日志")' in one or 'JLabel tabs = new JLabel("数据      |      结果      |      日志")' in one:
    raise SystemExit('fake OneClick tabs still present')
s = s[:one_start] + one + s[one_end:]

# Shared inspector attachment helpers.
helper_anchor = '      private void selectDataView() {\n'
helpers = '''      private void attachSharedInspectorToOneClick() {\n         if (this.sharedDataInspector == null) {\n            return;\n         }\n         Container parent = this.sharedDataInspector.getParent();\n         if (parent != null) {\n            parent.remove(this.sharedDataInspector);\n         }\n         this.exactOneClickInspectorHost.removeAll();\n         this.exactOneClickInspectorHost.add(this.sharedDataInspector, BorderLayout.CENTER);\n         this.sharedDataInspector.setVisible(true);\n         this.exactOneClickInspectorHost.revalidate();\n         this.exactOneClickInspectorHost.repaint();\n      }\n\n      private void attachSharedInspectorToWorkspace() {\n         if (this.sharedDataInspector == null || this.commandDataSplit == null) {\n            return;\n         }\n         if (this.commandDataSplit.getRightComponent() != this.sharedDataInspector) {\n            Container parent = this.sharedDataInspector.getParent();\n            if (parent != null) {\n               parent.remove(this.sharedDataInspector);\n            }\n            this.commandDataSplit.setRightComponent(this.sharedDataInspector);\n         }\n         this.sharedDataInspector.setVisible(true);\n         this.commandDataSplit.setDividerSize(8);\n         this.commandDataSplit.revalidate();\n         this.commandDataSplit.repaint();\n         SwingUtilities.invokeLater(this::applyDividerRatios);\n      }\n\n      private void selectDataView() {\n'''
if helper_anchor not in s:
    raise SystemExit('shared inspector helper anchor not found')
s = s.replace(helper_anchor, helpers, 1)

# OneClick attaches the real inspector and starts on the real Data tab.
show_anchor = '         this.stageLayout.show(this.stageCards, "oneclick_exact");\n         this.updateOneClickConditionalFields();\n'
show_repl = '''         this.stageLayout.show(this.stageCards, "oneclick_exact");\n         this.attachSharedInspectorToOneClick();\n         this.selectDataView();\n         this.updateOneClickConditionalFields();\n'''
if show_anchor not in s:
    raise SystemExit('showOneClickPage anchor not found')
s = s.replace(show_anchor, show_repl, 1)

# Every ordinary workspace gets the same inspector back.
workspace_anchor = '      private void showWorkspacePage() {\n'
if workspace_anchor not in s:
    raise SystemExit('showWorkspacePage anchor not found')
s = s.replace(workspace_anchor, workspace_anchor + '         this.attachSharedInspectorToWorkspace();\n', 1)

# Restore a fixed, always-visible run queue inside Logs (no expand/collapse control).
queue_anchor = '         var2.add(var11);\n         this.monitorCommand.setText("尚未执行命令");\n'
queue_block = '''         var2.add(var11);\n         var2.add(Box.createVerticalStrut(12));\n         JLabel queueTitle = sectionCaption("运行队列");\n         queueTitle.setAlignmentX(0.0F);\n         var2.add(queueTitle);\n         var2.add(Box.createVerticalStrut(7));\n         this.styleResultTable(this.runQueueTable);\n         this.runQueueTable.setFillsViewportHeight(true);\n         JScrollPane queueScroll = softScroll(this.runQueueTable);\n         queueScroll.setAlignmentX(0.0F);\n         queueScroll.setPreferredSize(new Dimension(100, 150));\n         queueScroll.setMaximumSize(new Dimension(Integer.MAX_VALUE, 170));\n         var2.add(queueScroll);\n         this.monitorCommand.setText("尚未执行命令");\n'''
if queue_anchor not in s:
    raise SystemExit('run queue anchor not found')
s = s.replace(queue_anchor, queue_block, 1)

# UI terminology: the stable third tab is Logs, not Run.
s = s.replace("请查看右侧‘运行’和 Stata Results 中的原始错误信息。", "请查看右侧‘日志’和 Stata Results 中的原始错误信息。")

# Guardrails.
for bad in ['monitorDetailsToggle', 'JLabel tabs=new JLabel("数据      |      结果      |      日志")', 'JLabel tabs = new JLabel("数据      |      结果      |      日志")']:
    if bad in s:
        raise SystemExit(f'forbidden legacy UI remains: {bad}')
for required in ['attachSharedInspectorToOneClick()', 'attachSharedInspectorToWorkspace()', 'this.exactOneClickInspectorHost.add(this.sharedDataInspector, BorderLayout.CENTER)', 'sectionCaption("运行队列")']:
    if required not in s:
        raise SystemExit(f'missing required 1.2.4 structure: {required}')

src.write_text(s, encoding='utf-8')

# Package/version metadata.
for f in ['hxempirical.ado', 'hxempirical.sthlp', 'hxempirical.pkg']:
    p = Path(f)
    t = p.read_text(encoding='utf-8').replace('1.2.3', '1.2.4')
    p.write_text(t, encoding='utf-8')

# Rewrite outdated hxempirical help claims instead of only bumping the header.
p = Path('hxempirical.sthlp')
t = p.read_text(encoding='utf-8')
t = t.replace(
'''The 1.2.4 interface follows the supplied 1672x941 reference layouts directly.\nThe start page uses a fixed left navigation rail, a Start Analysis card, five\nquick actions, current-data status, a 2-by-3 common-task area, recent work, and a\nsingle row of additional functions. The linear-model directory and OneClick\nworkspace use the same fixed card proportions and right-side guidance structure.''',
'''The 1.2.4 interface uses a stable desktop-workbench layout: a fixed left\nnavigation rail, a task-focused main workspace, and one shared right-side\nCurrent Data inspector. OneClick and ordinary command pages reuse that same\ninspector instead of maintaining separate look-alike data/result panels.''')
t = t.replace('The right side has three stable tabs: {bf:数据}, {bf:结果}, and {bf:运行}.', 'The right side has three stable tabs: {bf:数据}, {bf:结果}, and {bf:日志}.')
t = t.replace('The complete catalog is available through {bf:展开全部功能}. ', '')
t = t.replace('The detailed section contains a timestamped log and\nrun queue. Ordinary Stata estimation commands use an indeterminate progress\nstate because their internal percentage is unavailable.', 'The {bf:日志} tab keeps the timestamped execution log and run queue visible in\none fixed scrollable view; there is no expand/collapse details control. Ordinary\nStata estimation commands use an indeterminate progress state because their\ninternal percentage is unavailable.')
t = re.sub(r'HX empirical workbench, package version [0-9.]+\.', 'HX empirical workbench, package version 1.2.4.', t)
p.write_text(t, encoding='utf-8')

# Update toolbox help to match the stable tabs/no-expander rule.
p = Path('hxtoolbox.sthlp')
t = p.read_text(encoding='utf-8')
t = t.replace(
'''命令设置区底部固定显示“即将执行的 Stata 命令”，运行时同步显示状态和\n真实耗时。右侧“运行监控”记录开始/结束时间、return code、History 写入\n状态、处理器、数据前后观测数和变量数，以及可读取的回归 N、R-squared。\n详细区包含时间线和运行队列。普通回归使用不确定进度动画；批量转换按\n已完成文件数显示真实百分比。''',
'''命令设置区底部固定显示“即将执行的 Stata 命令”，运行时同步显示状态和\n真实耗时。右侧固定为“当前数据”，内部使用“数据 / 结果 / 日志”三个页签。\n“日志”记录开始/结束时间、return code、History 写入状态、处理器、时间线\n和运行队列，不再使用“详细运行信息 + / 收起详细信息 −”改变页面高度。\n普通回归使用不确定进度动画；批量转换按已完成文件数显示真实百分比。''')
p.write_text(t, encoding='utf-8')

# README cumulative log + release version.
p = Path('README.md')
r = p.read_text(encoding='utf-8')
r = r.replace('**当前发布版本：1.2.3**', '**当前发布版本：1.2.4**', 1)
r = re.sub(r'\*\*上次修改时间：[^\n]+\*\*', '**上次修改时间：2026-08-13 08:50（UTC+8）**', r, count=1)
entry = '''### 2026-08-13 08:50（UTC+8）\n\n**修改时间**：2026-08-13 08:50（UTC+8）\n\n**修改内容**：\n\n- 修复 OneClick 右栏的结构性问题：删除只画出“数据 / 结果 / 日志”文字但不可切换的假页签，OneClick 与普通命令页改为复用同一个真实“当前数据”检查器。\n- OneClick 载入数据后直接显示真实只读数据表；外部 OneClick 完成后，“结果”页直接显示结果概览和作者命令生成的结果表；运行过程统一进入同一个“日志”页。\n- “日志”页固定恢复运行队列表格，与执行记录同时存在；不恢复任何“详细运行信息 + / 收起详细信息 −”展开控件。\n- 修正 Stata 内部 help 与当前界面不一致的旧描述：统一为“数据 / 结果 / 日志”，删除旧的展开式运行详情和旧版首页描述，并修正帮助页尾部旧版本号。\n- Java 11 / class major 55 编译、JAR 重建，并对 OneClick 数据页、OneClick 结果页、日志页和基准回归页执行 1672×901 离线渲染检查。\n\n'''
r = r.replace('## 修改记录\n\n', '## 修改记录\n\n' + entry, 1)
r = r.replace('### 1.2.3（当前版本）', '### 1.2.3', 1)
ventry = '''### 1.2.4（当前版本）\n\n**发布时间**：2026-08-13 08:50（UTC+8）\n\n**修改内容**：\n\n- OneClick 与普通工作区共用真实“当前数据 / 结果 / 日志”右栏。\n- OneClick 数据、结果与日志链路真正可见，不再使用假页签。\n- 日志页固定显示执行记录与运行队列，无展开/收起。\n- Stata help 与 README 同步到当前界面。\n\n'''
r = r.replace('## 版本记录\n\n', '## 版本记录\n\n' + ventry, 1)
p.write_text(r, encoding='utf-8')

print('HX_124_PATCH_OK')
