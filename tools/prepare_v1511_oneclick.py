from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
OLD = "1.5.10"
NEW = "1.5.11"


def read(rel):
    return (root / rel).read_text(encoding="utf-8")


def write(rel, text):
    (root / rel).write_text(text, encoding="utf-8")


def must_replace(text, old, new, label, count=None):
    actual = text.count(old)
    if actual == 0:
        raise SystemExit(f"missing replacement target in {label}: {old!r}")
    if count is not None and actual != count:
        raise SystemExit(f"unexpected target count in {label}: {old!r} count={actual} expected={count}")
    return text.replace(old, new, count if count is not None else -1)

# Public/current version surfaces.
pkg = read("hxempirical.pkg")
pkg = must_replace(pkg, "d Version 1.5.10", "d Version 1.5.11", "hxempirical.pkg", 1)
write("hxempirical.pkg", pkg)

ado = read("hxempirical.ado")
ado = ado.replace("hxempirical 1.5.10", "hxempirical 1.5.11")
ado = ado.replace('"1.5.10"', '"1.5.11"')
write("hxempirical.ado", ado)

for rel, old, new in [
    ("hxempirical.sthlp", "version 1.5.10", "version 1.5.11"),
    ("hxinstall.do", "hxinstall 1.5.10", "hxinstall 1.5.11"),
    ("hxinstaller.ado", "hxinstaller 1.5.10", "hxinstaller 1.5.11"),
]:
    text = read(rel)
    text = must_replace(text, old, new, rel, 1)
    write(rel, text)

# hxtoolbox: prefer the JAR sitting beside the active ado. Generic findfile is only a fallback.
hxt = read("hxtoolbox.ado")
hxt = hxt.replace("*! hxtoolbox 4.7.0  14aug2026", "*! hxtoolbox 4.7.1  15aug2026", 1)
start = hxt.index('    local jarfile ""')
end_marker = '    if `"`jarfile\'"\' == "" {\n        display as error "未找到 Java 工作台组件 hxworkbench.jar，当前安装可能不完整。"'
end = hxt.index(end_marker, start)
jar_block = '''    local jarfile ""
    /* Prefer the JAR adjacent to the active hxtoolbox.ado. This prevents an older
       hxworkbench.jar elsewhere on adopath from shadowing the current package. */
    capture quietly findfile hxtoolbox.ado
    if !_rc {
        local entry `"`r(fn)'"'
        local entry : subinstr local entry "\\" "/", all
        local jarfile = substr(`"`entry'"', 1, strlen(`"`entry'"') - strlen("hxtoolbox.ado")) + "hxworkbench.jar"
        capture confirm file `"`jarfile'"'
        if _rc local jarfile ""
    }
    if `"`jarfile'"' == "" {
        capture quietly findfile hxworkbench.jar
        if !_rc local jarfile `"`r(fn)'"'
    }
'''
hxt = hxt[:start] + jar_block + hxt[end:]
write("hxtoolbox.ado", hxt)

# Java version and redesigned OneClick page.
java_rel = "src/main/java/com/hexie/stata/HxWorkbench.java"
java = read(java_rel)
java = must_replace(java, 'VERSION = "1.5.10"', 'VERSION = "1.5.11"', java_rel, 1)

method_pattern = re.compile(
    r"      private JComponent buildExactOneClickContainer\(\) \{.*?\n      \}\n\n      private void showOneClickPage",
    re.S,
)
new_method = r'''      private JComponent buildExactOneClickContainer() {
         JPanel root = new JPanel(new BorderLayout(14, 0));
         root.setBackground(APP_BG);
         root.setBorder(new EmptyBorder(16, 20, 16, 18));
         this.exactOneClickRoot = root;

         JPanel left = new JPanel(new BorderLayout(0, 12));
         left.setOpaque(false);

         JPanel header = new JPanel(new BorderLayout());
         header.setOpaque(false);
         JPanel heading = new JPanel();
         heading.setOpaque(false);
         heading.setLayout(new BoxLayout(heading, BoxLayout.Y_AXIS));
         JLabel crumb = new JLabel("首页 / OneClick / 控制变量筛选");
         crumb.setForeground(new Color(91, 111, 144));
         crumb.setFont(crumb.getFont().deriveFont(10.5F));
         JLabel title = new JLabel("OneClick 控制变量筛选");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD, 22.0F));
         JLabel subtitle = new JLabel("按步骤选择变量和筛选规则，底部始终显示将要执行的真实 Stata 命令。");
         subtitle.setForeground(MUTED);
         subtitle.setFont(subtitle.getFont().deriveFont(10.5F));
         heading.add(crumb);
         heading.add(Box.createVerticalStrut(5));
         heading.add(title);
         heading.add(Box.createVerticalStrut(4));
         heading.add(subtitle);
         header.add(heading, BorderLayout.WEST);

         JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 7, 0));
         actions.setOpaque(false);
         JButton back = this.refButton("← 上一级", false);
         back.addActionListener(e -> this.showHomePage());
         JButton home = this.refButton("首页", false);
         home.addActionListener(e -> this.showHomePage());
         JButton help = this.refButton("帮助", false);
         help.addActionListener(e -> this.openHelp());
         actions.add(back);
         actions.add(home);
         actions.add(help);
         header.add(actions, BorderLayout.EAST);
         left.add(header, BorderLayout.NORTH);

         JPanel form = new JPanel();
         form.setOpaque(false);
         form.setLayout(new BoxLayout(form, BoxLayout.Y_AXIS));

         JPanel guide = this.refCard();
         guide.setLayout(new BorderLayout(0, 7));
         JLabel guideTitle = new JLabel("怎么用");
         guideTitle.setForeground(TEXT);
         guideTitle.setFont(guideTitle.getFont().deriveFont(Font.BOLD, 12.5F));
         JLabel guideText = new JLabel("<html>1. 选择 Y 和核心 X　　2. 选择候选控制变量　　3. 按需设置固定变量和筛选规则　　4. 检查命令后运行</html>");
         guideText.setForeground(MUTED);
         guideText.setFont(guideText.getFont().deriveFont(10.5F));
         this.oneClickScale.setFont(this.oneClickScale.getFont().deriveFont(Font.BOLD, 10.5F));
         guide.add(guideTitle, BorderLayout.NORTH);
         guide.add(guideText, BorderLayout.CENTER);
         guide.add(this.oneClickScale, BorderLayout.SOUTH);
         guide.setAlignmentX(0.0F);
         guide.setMaximumSize(new Dimension(Integer.MAX_VALUE, 94));
         form.add(guide);
         form.add(Box.createVerticalStrut(12));

         styleCombo(this.oneClickY);
         styleCombo(this.oneClickX);
         styleCombo(this.oneClickP);
         styleCombo(this.oneClickEstimator);
         styleTextField(this.exactOneClickModelOptions);
         styleTextField(this.exactOneClickOtherOptions);
         styleTextField(this.exactOneClickCandidatesDisplay);
         styleTextField(this.exactOneClickRequiredDisplay);
         this.exactOneClickCandidatesDisplay.setEditable(false);
         this.exactOneClickRequiredDisplay.setEditable(false);
         this.exactOneClickCandidatesDisplay.setToolTipText("点击右侧按钮选择需要尝试组合的控制变量");
         this.exactOneClickRequiredDisplay.setToolTipText("这些变量会固定进入每一个模型");

         JPanel basic = this.refCard();
         basic.setLayout(new BoxLayout(basic, BoxLayout.Y_AXIS));
         JLabel basicTitle = new JLabel("1　基础变量");
         basicTitle.setForeground(TEXT);
         basicTitle.setFont(basicTitle.getFont().deriveFont(Font.BOLD, 13.0F));
         basicTitle.setAlignmentX(0.0F);
         basic.add(basicTitle);
         basic.add(Box.createVerticalStrut(4));
         JLabel basicHint = new JLabel("先确定结果变量和最关心的解释变量。");
         basicHint.setForeground(MUTED);
         basicHint.setFont(basicHint.getFont().deriveFont(10.0F));
         basicHint.setAlignmentX(0.0F);
         basic.add(basicHint);
         basic.add(Box.createVerticalStrut(10));

         JPanel yx = new JPanel(new GridLayout(1, 2, 14, 0));
         yx.setOpaque(false);
         JPanel yBlock = new JPanel(new BorderLayout(0, 5));
         yBlock.setOpaque(false);
         JLabel yLabel = new JLabel("因变量（Y）");
         yLabel.setForeground(TEXT);
         yBlock.add(yLabel, BorderLayout.NORTH);
         yBlock.add(this.oneClickY, BorderLayout.CENTER);
         JPanel xBlock = new JPanel(new BorderLayout(0, 5));
         xBlock.setOpaque(false);
         JLabel xLabel = new JLabel("核心解释变量（X）");
         xLabel.setForeground(TEXT);
         xBlock.add(xLabel, BorderLayout.NORTH);
         xBlock.add(this.oneClickX, BorderLayout.CENTER);
         yx.add(yBlock);
         yx.add(xBlock);
         yx.setMaximumSize(new Dimension(Integer.MAX_VALUE, 56));
         basic.add(yx);
         basic.setAlignmentX(0.0F);
         basic.setMaximumSize(new Dimension(Integer.MAX_VALUE, 130));
         form.add(basic);
         form.add(Box.createVerticalStrut(12));

         JPanel controls = this.refCard();
         controls.setLayout(new BoxLayout(controls, BoxLayout.Y_AXIS));
         JLabel controlsTitle = new JLabel("2　控制变量");
         controlsTitle.setForeground(TEXT);
         controlsTitle.setFont(controlsTitle.getFont().deriveFont(Font.BOLD, 13.0F));
         controlsTitle.setAlignmentX(0.0F);
         controls.add(controlsTitle);
         controls.add(Box.createVerticalStrut(4));
         JLabel controlsHint = new JLabel("候选变量用于组合筛选；固定变量会进入每一个模型。");
         controlsHint.setForeground(MUTED);
         controlsHint.setFont(controlsHint.getFont().deriveFont(10.0F));
         controlsHint.setAlignmentX(0.0F);
         controls.add(controlsHint);
         controls.add(Box.createVerticalStrut(10));

         JPanel candidates = new JPanel(new BorderLayout(10, 0));
         candidates.setOpaque(false);
         JPanel candidateLabel = new JPanel();
         candidateLabel.setOpaque(false);
         candidateLabel.setLayout(new BoxLayout(candidateLabel, BoxLayout.Y_AXIS));
         JLabel lc = new JLabel("候选控制变量");
         lc.setForeground(TEXT);
         JLabel lcRaw = new JLabel("Candidates");
         lcRaw.setForeground(MUTED);
         lcRaw.setFont(lcRaw.getFont().deriveFont(9.5F));
         candidateLabel.add(lc);
         candidateLabel.add(lcRaw);
         candidateLabel.setPreferredSize(new Dimension(128, 38));
         candidates.add(candidateLabel, BorderLayout.WEST);
         candidates.add(this.exactOneClickCandidatesDisplay, BorderLayout.CENTER);
         JButton cp = this.refButton("选择变量", false);
         cp.addActionListener(e -> this.chooseExactOneClickValues(this.oneClickCandidates, this.exactOneClickCandidatesDisplay, "选择候选控制变量"));
         candidates.add(cp, BorderLayout.EAST);
         candidates.setMaximumSize(new Dimension(Integer.MAX_VALUE, 42));
         controls.add(candidates);
         controls.add(Box.createVerticalStrut(10));

         JPanel required = new JPanel(new BorderLayout(10, 0));
         required.setOpaque(false);
         JPanel requiredLabel = new JPanel();
         requiredLabel.setOpaque(false);
         requiredLabel.setLayout(new BoxLayout(requiredLabel, BoxLayout.Y_AXIS));
         JLabel lr = new JLabel("固定控制变量");
         lr.setForeground(TEXT);
         JLabel lrRaw = new JLabel("fix() · 可选");
         lrRaw.setForeground(MUTED);
         lrRaw.setFont(lrRaw.getFont().deriveFont(9.5F));
         requiredLabel.add(lr);
         requiredLabel.add(lrRaw);
         requiredLabel.setPreferredSize(new Dimension(128, 38));
         required.add(requiredLabel, BorderLayout.WEST);
         required.add(this.exactOneClickRequiredDisplay, BorderLayout.CENTER);
         JButton rp = this.refButton("选择变量", false);
         rp.addActionListener(e -> this.chooseExactOneClickValues(this.oneClickRequired, this.exactOneClickRequiredDisplay, "选择固定控制变量"));
         required.add(rp, BorderLayout.EAST);
         required.setMaximumSize(new Dimension(Integer.MAX_VALUE, 42));
         controls.add(required);
         controls.setAlignmentX(0.0F);
         controls.setMaximumSize(new Dimension(Integer.MAX_VALUE, 190));
         form.add(controls);
         form.add(Box.createVerticalStrut(12));

         JPanel rules = this.refCard();
         rules.setLayout(new BoxLayout(rules, BoxLayout.Y_AXIS));
         JLabel rulesTitle = new JLabel("3　筛选与估计");
         rulesTitle.setForeground(TEXT);
         rulesTitle.setFont(rulesTitle.getFont().deriveFont(Font.BOLD, 13.0F));
         rulesTitle.setAlignmentX(0.0F);
         rules.add(rulesTitle);
         rules.add(Box.createVerticalStrut(10));

         JPanel pm = new JPanel(new GridLayout(1, 2, 14, 0));
         pm.setOpaque(false);
         JPanel pBlock = new JPanel(new BorderLayout(0, 5));
         pBlock.setOpaque(false);
         JLabel pLabel = new JLabel("显著性阈值（p()）");
         pLabel.setForeground(TEXT);
         pBlock.add(pLabel, BorderLayout.NORTH);
         pBlock.add(this.oneClickP, BorderLayout.CENTER);
         JPanel mBlock = new JPanel(new BorderLayout(0, 5));
         mBlock.setOpaque(false);
         JLabel mLabel = new JLabel("回归方法（method）");
         mLabel.setForeground(TEXT);
         mBlock.add(mLabel, BorderLayout.NORTH);
         mBlock.add(this.oneClickEstimator, BorderLayout.CENTER);
         pm.add(pBlock);
         pm.add(mBlock);
         pm.setMaximumSize(new Dimension(Integer.MAX_VALUE, 56));
         rules.add(pm);
         rules.add(Box.createVerticalStrut(10));

         JPanel opts = new JPanel(new GridLayout(1, 2, 14, 0));
         opts.setOpaque(false);
         JPanel oBlock = new JPanel(new BorderLayout(0, 5));
         oBlock.setOpaque(false);
         JLabel oLabel = new JLabel("模型附加选项（o()，可选）");
         oLabel.setForeground(TEXT);
         oBlock.add(oLabel, BorderLayout.NORTH);
         oBlock.add(this.exactOneClickModelOptions, BorderLayout.CENTER);
         JPanel zBlock = new JPanel(new BorderLayout(0, 5));
         zBlock.setOpaque(false);
         JLabel zLabel = new JLabel("其他原生选项（z，可选）");
         zLabel.setForeground(TEXT);
         zBlock.add(zLabel, BorderLayout.NORTH);
         zBlock.add(this.exactOneClickOtherOptions, BorderLayout.CENTER);
         opts.add(oBlock);
         opts.add(zBlock);
         opts.setMaximumSize(new Dimension(Integer.MAX_VALUE, 56));
         rules.add(opts);
         rules.setAlignmentX(0.0F);
         rules.setMaximumSize(new Dimension(Integer.MAX_VALUE, 175));
         form.add(rules);
         form.add(Box.createVerticalStrut(12));

         JPanel command = this.refCard();
         command.setLayout(new BorderLayout(10, 8));
         JPanel commandHeading = new JPanel();
         commandHeading.setOpaque(false);
         commandHeading.setLayout(new BoxLayout(commandHeading, BoxLayout.Y_AXIS));
         JLabel ctitle = new JLabel("4　确认 Stata 命令");
         ctitle.setForeground(TEXT);
         ctitle.setFont(ctitle.getFont().deriveFont(Font.BOLD, 12.5F));
         JLabel csub = new JLabel("运行前先检查；HX 调用的是你已经安装的真实 OneClick 外部命令。");
         csub.setForeground(MUTED);
         csub.setFont(csub.getFont().deriveFont(9.8F));
         commandHeading.add(ctitle);
         commandHeading.add(Box.createVerticalStrut(3));
         commandHeading.add(csub);
         command.add(commandHeading, BorderLayout.NORTH);
         this.exactOneClickCommand.setEditable(false);
         this.exactOneClickCommand.setLineWrap(true);
         this.exactOneClickCommand.setWrapStyleWord(true);
         this.exactOneClickCommand.setBackground(new Color(244, 248, 255));
         this.exactOneClickCommand.setForeground(TEXT);
         this.exactOneClickCommand.setFont(new Font("Monospaced", Font.PLAIN, 11));
         this.exactOneClickCommand.setBorder(new EmptyBorder(9, 10, 9, 10));
         JScrollPane cs = softScroll(this.exactOneClickCommand);
         cs.setPreferredSize(new Dimension(100, 64));
         command.add(cs, BorderLayout.CENTER);
         JPanel ca = new JPanel(new FlowLayout(FlowLayout.RIGHT, 7, 0));
         ca.setOpaque(false);
         JButton copy = this.refButton("复制命令", false);
         copy.addActionListener(e -> Toolkit.getDefaultToolkit().getSystemClipboard().setContents(new StringSelection(this.exactOneClickCommand.getText()), null));
         JButton run = this.refButton("运行 OneClick", true);
         run.addActionListener(e -> this.runOneClick());
         ca.add(copy);
         ca.add(run);
         command.add(ca, BorderLayout.SOUTH);
         command.setAlignmentX(0.0F);
         command.setMaximumSize(new Dimension(Integer.MAX_VALUE, 150));
         form.add(command);
         form.add(Box.createVerticalStrut(10));

         JLabel externalPolicy = new JLabel("外部命令由你自行安装；工作台只负责识别、设置参数和调用。", SwingConstants.LEFT);
         externalPolicy.setForeground(MUTED);
         externalPolicy.setFont(externalPolicy.getFont().deriveFont(9.8F));
         externalPolicy.setAlignmentX(0.0F);
         form.add(externalPolicy);

         HxWorkbench.SimpleDocumentListener exactListener = new HxWorkbench.SimpleDocumentListener(() -> this.updateOneClickPreview());
         this.exactOneClickModelOptions.getDocument().addDocumentListener(exactListener);
         this.exactOneClickOtherOptions.getDocument().addDocumentListener(exactListener);

         JScrollPane formScroll = softScroll(form);
         formScroll.setBorder(null);
         formScroll.getVerticalScrollBar().setUnitIncrement(18);
         left.add(formScroll, BorderLayout.CENTER);
         root.add(left, BorderLayout.CENTER);

         this.exactOneClickInspectorHost.removeAll();
         this.exactOneClickInspectorHost.setOpaque(false);
         this.exactOneClickInspectorHost.setPreferredSize(new Dimension(360, 0));
         root.add(this.exactOneClickInspectorHost, BorderLayout.EAST);
         return root;
      }

      private void showOneClickPage'''
java, n = method_pattern.subn(new_method, java, count=1)
if n != 1:
    raise SystemExit(f"OneClick method replacement failed: {n}")
write(java_rel, java)

# README current release note; preserve historical 1.5.10 notes.
readme = read("README.md")
readme = must_replace(readme, "**当前发布版本：1.5.10**", "**当前发布版本：1.5.11**", "README.md", 1)
readme = re.sub(r"\*\*上次修改时间：[^*]+\*\*", "**上次修改时间：2026-08-15 21:45（UTC+8）**", readme, count=1)
anchor = "### 1.5.10 安装布局统一"
note = '''### 1.5.11 OneClick 界面与 Java 加载路径修复

- OneClick 页面改为“基础变量 → 控制变量 → 筛选与估计 → 确认 Stata 命令”四步结构，中文术语作为主标签，原始 `Candidates` / `fix()` / `p()` / `method` / `o()` 作为语法提示保留。
- 候选控制变量和固定控制变量改为明确的“选择变量”操作，组合数量提示进入页面上方，减少大面积空白和纯技术参数感。
- OneClick 右侧数据检查区收窄，为主参数区保留更多宽度；底部继续展示并运行真实外部 OneClick 命令。
- Java 启动器优先加载与当前 `hxtoolbox.ado` 同目录的 `hxworkbench.jar`，只有缺失时才回退到全局 `findfile`，避免旧 JAR 影子文件导致 ADO 已更新但 GUI 仍显示旧版本。

'''
if anchor not in readme:
    raise SystemExit("README 1.5.10 anchor missing")
readme = readme.replace(anchor, note + anchor, 1)
write("README.md", readme)

install = read("INSTALL.md")
install = install.replace("当前版本：1.5.10", "当前版本：1.5.11")
install = install.replace("最新版本：1.5.10", "最新版本：1.5.11")
write("INSTALL.md", install)

# Static guard for the stale-JAR shadowing regression and OneClick information architecture.
verify_rel = "tools/verify_static_contracts.py"
verify = read(verify_rel)
append = r'''

# v1.5.11: Java launcher must prefer the JAR adjacent to the active hxtoolbox ado.
hxtoolbox_text = (root / "hxtoolbox.ado").read_text(encoding="utf-8")
adjacent_marker = "Prefer the JAR adjacent to the active hxtoolbox.ado"
if adjacent_marker not in hxtoolbox_text:
    fail("hxtoolbox must document/use adjacent JAR preference")
adjacent_pos = hxtoolbox_text.find("findfile hxtoolbox.ado")
generic_pos = hxtoolbox_text.find("findfile hxworkbench.jar")
if adjacent_pos < 0 or generic_pos < 0 or adjacent_pos > generic_pos:
    fail("hxtoolbox must resolve active ado directory before generic JAR findfile")

# v1.5.11: OneClick should remain task-first and keep raw syntax as secondary guidance.
java_text = (root / "src/main/java/com/hexie/stata/HxWorkbench.java").read_text(encoding="utf-8")
for needle in (
    "OneClick 控制变量筛选",
    "1　基础变量",
    "2　控制变量",
    "3　筛选与估计",
    "4　确认 Stata 命令",
    "候选控制变量",
    "固定控制变量",
    "外部命令由你自行安装",
):
    if needle not in java_text:
        fail("OneClick task-first UI contract missing: " + needle)
'''
if adjacent_marker not in verify:
    verify = verify.rstrip() + append + "\n"
write(verify_rel, verify)

print("HX_PREP_V1511_OK")
