from pathlib import Path
import re

p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')


def rep(old, new, count=None):
    global s
    n = s.count(old)
    if count is not None and n != count:
        raise SystemExit(f'expected {count} occurrences, found {n}: {old[:120]!r}')
    if n == 0:
        raise SystemExit(f'pattern not found: {old[:120]!r}')
    s = s.replace(old, new)

rep('public static final String VERSION = "1.2.1";', 'public static final String VERSION = "1.2.2";', 1)
rep('SFIToolkit.displayln("HxWorkbench 1.2.1");', 'SFIToolkit.displayln("HxWorkbench 1.2.2");', 1)
rep('private final JLabel rightPaneTitle = new JLabel("数据与结果");', 'private final JLabel rightPaneTitle = new JLabel("当前数据");', 1)
rep('this.dataTabs.addTab("运行", this.buildRunMonitorPanel());', 'this.dataTabs.addTab("日志", this.buildRunMonitorPanel());', 1)

rep('''      private void selectDataView() {
         this.dataTabs.setSelectedIndex(0);
         this.rightPaneTitle.setText("当前数据");
      }

      private void selectResultView(String var1, boolean var2) {
         this.resultLayout.show(this.resultCards, var1);
         this.rightPaneTitle.setText("任务结果");
         if (var2) {
            this.dataTabs.setSelectedIndex(1);
         }
      }

      private void selectRunView() {
         this.dataTabs.setSelectedIndex(2);
         this.rightPaneTitle.setText("运行状态");
      }
''','''      private void selectDataView() {
         this.dataTabs.setSelectedIndex(0);
         this.rightPaneTitle.setText("当前数据");
      }

      private void selectResultView(String var1, boolean var2) {
         this.resultLayout.show(this.resultCards, var1);
         this.rightPaneTitle.setText("当前数据");
         if (var2) {
            this.dataTabs.setSelectedIndex(1);
         }
      }

      private void selectRunView() {
         this.dataTabs.setSelectedIndex(2);
         this.rightPaneTitle.setText("当前数据");
      }
''',1)

listener = re.compile(r'''\s*this\.dataTabs\.addChangeListener\(var1x -> \{\n\s*int var2x = this\.dataTabs\.getSelectedIndex\(\);\n\s*if \(var2x == 0\) \{\n\s*this\.rightPaneTitle\.setText\("当前数据"\);\n\s*\} else if \(var2x == 1\) \{\n\s*this\.rightPaneTitle\.setText\("任务结果"\);\n\s*\} else if \(var2x == 2\) \{\n\s*this\.rightPaneTitle\.setText\("运行状态"\);\n\s*\}\n\s*\}\);''')
s, n = listener.subn('''
         this.dataTabs.addChangeListener(var1x -> this.rightPaneTitle.setText("当前数据"));''', s, count=1)
if n != 1:
    raise SystemExit(f'failed to replace dataTabs title listener: {n}')

# Remove the layout-changing monitor details toggle listener entirely.
toggle_listener = re.compile(r'''\s*this\.monitorDetailsToggle\.addActionListener\(var1x -> \{\n\s*boolean var2x = this\.monitorDetailsToggle\.isSelected\(\);\n\s*this\.monitorDetailsToggle\.setText\(var2x \? "收起详细信息  −" : "详细运行信息  \+"\);\n\s*this\.monitorDetails\.setVisible\(var2x\);\n\s*this\.monitorDetails\.getParent\(\)\.revalidate\(\);\n\s*this\.monitorDetails\.getParent\(\)\.repaint\(\);\n\s*\}\);''')
s, n = toggle_listener.subn('', s, count=1)
if n != 1:
    raise SystemExit(f'failed to remove monitor toggle listener: {n}')

# Replace collapsible details / nested tabs with one fixed execution log inside the outer 日志 tab.
run_details = re.compile(r'''\s*styleSecondaryButton\(this\.monitorDetailsToggle\);\n\s*this\.monitorDetailsToggle\.setAlignmentX\(0\.0F\);\n\s*var2\.add\(this\.monitorDetailsToggle\);\n\s*var2\.add\(Box\.createVerticalStrut\(7\)\);\n\s*this\.monitorLog\.setRows\(8\);\n\s*this\.monitorLog\.setBackground\(CODE_BG\);\n\s*this\.monitorLog\.setFont\(new Font\("Monospaced", 0, 11\)\);\n\s*this\.runQueueTable\.setRowHeight\(25\);\n\s*this\.runQueueTable\.setFillsViewportHeight\(true\);\n\s*this\.runQueueTable\.setAutoResizeMode\(3\);\n\s*JTabbedPane var8 = new JTabbedPane\(\);\n\s*var8\.addTab\("执行记录", softScroll\(this\.monitorLog\)\);\n\s*var8\.addTab\("运行队列", softScroll\(this\.runQueueTable\)\);\n\s*this\.monitorDetails\.setOpaque\(false\);\n\s*this\.monitorDetails\.add\(var8, "Center"\);\n\s*this\.monitorDetails\.setPreferredSize\(new Dimension\(100, 230\)\);\n\s*this\.monitorDetails\.setMaximumSize\(new Dimension\(Integer\.MAX_VALUE, 250\)\);\n\s*this\.monitorDetails\.setAlignmentX\(0\.0F\);\n\s*this\.monitorDetails\.setVisible\(false\);\n\s*var2\.add\(this\.monitorDetails\);''')
replacement = '''
         JLabel var8 = sectionCaption("执行记录");
         var8.setAlignmentX(0.0F);
         var2.add(var8);
         var2.add(Box.createVerticalStrut(7));
         this.monitorLog.setRows(10);
         this.monitorLog.setBackground(CODE_BG);
         this.monitorLog.setFont(new Font("Monospaced", 0, 11));
         JScrollPane var11 = softScroll(this.monitorLog);
         var11.setAlignmentX(0.0F);
         var11.setPreferredSize(new Dimension(100, 210));
         var11.setMaximumSize(new Dimension(Integer.MAX_VALUE, 230));
         var2.add(var11);'''
s, n = run_details.subn(replacement, s, count=1)
if n != 1:
    raise SystemExit(f'failed to replace monitor details UI: {n}')

# The old monitor-details preview now simply selects the fixed log tab.
preview = re.compile(r'''      private void populateMonitorDetailsPreviewState\(\) \{\n\s*this\.monitorDetailsToggle\.setSelected\(true\);\n\s*this\.monitorDetailsToggle\.setText\("收起详细运行信息  −"\);\n\s*this\.monitorDetails\.setVisible\(true\);\n\s*\}''')
s, n = preview.subn('''      private void populateMonitorDetailsPreviewState() {
         this.dataTabs.setSelectedIndex(2);
         this.rightPaneTitle.setText("当前数据");
      }''', s, count=1)
if n != 1:
    raise SystemExit(f'failed to replace monitor details preview: {n}')

# OneClick: give the entire right side to 当前数据, remove the separate 推荐流程 column.
for old, new in [
    ('data.setBounds(780,115,405,695);', 'data.setBounds(780,115,660,695);'),
    ('refresh.setBounds(315,9,70,32);', 'refresh.setBounds(570,9,70,32);'),
    ('tabs.setBounds(20,52,260,24);', 'tabs.setBounds(24,52,330,24);'),
    ('ill.setBounds(72,125,260,210);', 'ill.setBounds(200,125,260,210);'),
    ('this.exactOneClickDataStatus.setBounds(45,340,315,30);', 'this.exactOneClickDataStatus.setBounds(170,340,320,30);'),
    ('this.exactOneClickDataDetail.setBounds(30,372,345,25);', 'this.exactOneClickDataDetail.setBounds(145,372,370,25);'),
    ('au.setBounds(62,415,280,40);', 'au.setBounds(190,415,280,40);'),
    ('own.setBounds(62,465,280,40);', 'own.setBounds(190,465,280,40);'),
    ('cv.setBounds(62,515,280,40);', 'cv.setBounds(190,515,280,40);'),
    ('hint.setBounds(45,618,320,30);', 'hint.setBounds(160,618,350,30);'),
]:
    rep(old,new,1)

recommend = re.compile(r'''\n\s*JPanel recommend=this\.refCard\(\);.*?root\.add\(recommend\);''', re.S)
s, n = recommend.subn('', s, count=1)
if n != 1:
    raise SystemExit(f'failed to remove OneClick recommend column: {n}')

p.write_text(s, encoding='utf-8')

# Public version metadata.
for path in ['hxempirical.ado','hxempirical.sthlp','hxempirical.pkg']:
    q = Path(path)
    t = q.read_text(encoding='utf-8')
    t = t.replace('1.2.1','1.2.2')
    q.write_text(t, encoding='utf-8')

# README: cumulative modification log, preserving prior history.
rp = Path('README.md')
r = rp.read_text(encoding='utf-8')
r = r.replace('**当前发布版本：1.2.1**', '**当前发布版本：1.2.2**', 1)
r = re.sub(r'\*\*上次修改时间：[^\n]+\*\*', '**上次修改时间：2026-08-12 21:51（UTC+8）**', r, count=1)
entry = '''### 2026-08-12 21:51（UTC+8）

**修改时间**：2026-08-12 21:51（UTC+8）

**修改内容**：

- 统一右侧辅助栏职责：整列固定为“当前数据”，不再把“推荐流程”“小贴士”或额外说明拆成第三栏；OneClick 页原最右推荐流程栏已移除，当前数据栏扩展为完整右侧宽度。
- 普通工作区右侧固定使用“数据 / 结果 / 日志”三类视图，页头始终保持“当前数据”，切换结果或日志时不再把整栏标题改成“任务结果 / 运行状态”。
- 删除运行监控里的“详细运行信息 + / 收起详细信息 −”交互；执行记录直接固定显示在“日志”页中，不再通过展开 / 收起改变页面高度和控件位置。
- 运行页继续保留当前命令、Return code、耗时、History 状态、执行摘要和执行记录，但压回同一固定信息层级；不再显示嵌套的“执行记录 / 运行队列”折叠区域。
- OneClick 的流程说明继续留在主工作区“快速理解 OneClick”中；右侧只承担数据、结果与日志职责，形成“主任务在中间、当前数据在右侧”的稳定布局。
- Java 11 / class major 55 编译、JAR 重建及 OneClick / 运行监控 / 普通工作区离线渲染验证通过后发布。

'''
if '## 修改记录\n\n' not in r:
    raise SystemExit('README 修改记录 heading missing')
r = r.replace('## 修改记录\n\n', '## 修改记录\n\n'+entry, 1)
r = r.replace('### 1.2.1（当前版本）', '### 1.2.1', 1)
version_entry = '''### 1.2.2（当前版本）

**发布时间**：2026-08-12 21:51（UTC+8）

**修改内容**：

- 右侧整列统一保留给“当前数据”，内部固定为数据、结果、日志三个视图。
- OneClick 移除独立推荐流程第三栏，当前数据扩展为完整右侧信息栏；流程说明回归主工作区。
- 删除运行详情展开 / 收起机制，执行记录在日志页固定呈现，避免页面高度和按钮位置跳动。

'''
if '## 版本记录\n\n' not in r:
    raise SystemExit('README 版本记录 heading missing')
r = r.replace('## 版本记录\n\n', '## 版本记录\n\n'+version_entry, 1)
rp.write_text(r, encoding='utf-8')

print('HX_RIGHT_COLUMN_122_PATCH_OK')
