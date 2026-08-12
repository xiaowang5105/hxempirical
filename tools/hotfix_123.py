from pathlib import Path
import re

src = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = src.read_text(encoding='utf-8')

# Public Java version + sidebar version.
s = s.replace('public static final String VERSION = "1.2.2";', 'public static final String VERSION = "1.2.3";', 1)
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.2.2");', 'SFIToolkit.displayln("HxWorkbench 1.2.3");', 1)
s = s.replace('new JLabel("版本：1.2.2")', 'new JLabel("版本：1.2.3")', 1)

# Restore the recommendation panel only inside the linear-model directory.
lin_start = s.index('private JComponent buildExactLinearContainer()')
lin_end = s.index('private JComponent buildExactOneClickContainer()', lin_start)
lin = s[lin_start:lin_end]
if '推荐路径' not in lin:
    anchor = 'root.add(search);\n\n         JPanel choose='
    if anchor not in lin:
        raise SystemExit('linear insertion anchor not found')
    block = '''root.add(search);\n\n         JPanel recommend=this.refCard(); recommend.setLayout(new BoxLayout(recommend,BoxLayout.Y_AXIS)); recommend.setBounds(1165,146,240,640); JLabel rt=new JLabel("▥  推荐路径"); rt.setForeground(TEXT); rt.setFont(rt.getFont().deriveFont(Font.BOLD,14.0F)); rt.setAlignmentX(0.0F); recommend.add(rt); recommend.add(Box.createVerticalStrut(24)); recommend.add(this.exactLinearStep("1","先用常用命令","从常用命令入手，快速完成基础分析。",new Color(34,109,246))); recommend.add(Box.createVerticalStrut(28)); recommend.add(this.exactLinearStep("2","看示例与说明","查看示例与说明，理解命令用法与适用场景。",new Color(31,169,105))); recommend.add(Box.createVerticalStrut(28)); recommend.add(this.exactLinearStep("3","再进入进阶命令","根据需求选择进阶命令，满足更复杂的分析。",new Color(116,83,224))); recommend.add(Box.createVerticalGlue()); JPanel tip=new JPanel(new BorderLayout()); tip.setBackground(new Color(255,250,241)); tip.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(255,219,166),9),new EmptyBorder(13,13,13,13))); tip.add(new JLabel("<html><b><span style='color:#f59e0b'>☼ 小贴士</span></b><br><br><span style='color:#68758b'>命令太多时，优先从常用命令开始，逐步深入更高阶方法！</span></html>"),BorderLayout.CENTER); tip.setMaximumSize(new Dimension(Integer.MAX_VALUE,140)); recommend.add(tip); root.add(recommend);\n\n         JPanel choose='''
    lin = lin.replace(anchor, block, 1)
    s = s[:lin_start] + lin + s[lin_end:]

# Remove recommendation/tips only inside OneClick page; keep its workflow steps in main content.
one_start = s.index('private JComponent buildExactOneClickContainer()')
one_end = s.index('private void showOneClickPage', one_start)
one = s[one_start:one_end]
pat = re.compile(r'\n\s*JPanel recommend=this\.refCard\(\); recommend\.setLayout\(new BoxLayout\(recommend,BoxLayout\.Y_AXIS\)\); recommend\.setBounds\(1200,115,240,695\);.*?recommend\.add\(tip\); root\.add\(recommend\);', re.S)
one, n = pat.subn('', one, count=1)
if n != 1:
    raise SystemExit(f'OneClick recommend block removal count={n}')
if '推荐流程' in one:
    raise SystemExit('OneClick recommendation still present')
s = s[:one_start] + one + s[one_end:]

# Guard the intended right-column structure.
if 'data.setBounds(780,115,660,695)' not in s[one_start:one_start+14000]:
    raise SystemExit('OneClick full-width Current Data missing')
if 'monitorDetailsToggle' in s:
    raise SystemExit('expand/collapse monitor control returned')

src.write_text(s, encoding='utf-8')

# Version metadata.
for f in ['hxempirical.ado','hxempirical.sthlp','hxempirical.pkg']:
    p=Path(f); t=p.read_text(encoding='utf-8'); t=t.replace('1.2.2','1.2.3'); p.write_text(t,encoding='utf-8')

# README cumulative log.
p=Path('README.md'); r=p.read_text(encoding='utf-8')
r=r.replace('**当前发布版本：1.2.2**','**当前发布版本：1.2.3**',1)
r=re.sub(r'\*\*上次修改时间：[^\n]+\*\*','**上次修改时间：2026-08-12 22:19（UTC+8）**',r,count=1)
entry='''### 2026-08-12 22:19（UTC+8）\n\n**修改时间**：2026-08-12 22:19（UTC+8）\n\n**修改内容**：\n\n- 修正 1.2.2 自查发现的页面归属误改：恢复“回归 > 线性模型”原有的右侧“推荐路径”，避免把线性模型目录误当成 OneClick 的辅助栏处理。\n- OneClick 页真正移除独立“推荐流程 / 小贴士”第三栏；右侧完整宽度统一留给“当前数据”，流程说明继续保留在主工作区“快速理解 OneClick”中。\n- 继续保留 1.2.2 的固定右栏规则：普通工作区右侧始终为“当前数据”，内部使用“数据 / 结果 / 日志”，不再随 Tab 改标题。\n- 继续保留无展开式运行日志：不恢复“详细运行信息 + / 收起详细信息 −”，执行记录固定显示在日志页，避免页面高度和按钮位置变化。\n- Java 11 / class major 55 编译、JAR 重建，并对线性模型、OneClick、运行日志和基准回归四类页面重新渲染检查。\n\n'''
r=r.replace('## 修改记录\n\n','## 修改记录\n\n'+entry,1)
r=r.replace('### 1.2.2（当前版本）','### 1.2.2',1)
ventry='''### 1.2.3（当前版本）\n\n**发布时间**：2026-08-12 22:19（UTC+8）\n\n**修改内容**：\n\n- 修复 1.2.2 的页面归属误改，恢复线性模型“推荐路径”。\n- OneClick 独立推荐栏正式移除，完整右侧空间归“当前数据”。\n- 固定“数据 / 结果 / 日志”右栏与无展开运行日志规则继续保留。\n\n'''
r=r.replace('## 版本记录\n\n','## 版本记录\n\n'+ventry,1)
p.write_text(r,encoding='utf-8')
print('HX_123_HOTFIX_OK')
