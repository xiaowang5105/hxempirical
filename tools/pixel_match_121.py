from pathlib import Path

p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')


def method_span(src: str, signature: str):
    start = src.find(signature)
    if start < 0:
        raise SystemExit(f'missing method: {signature}')
    brace = src.find('{', start)
    depth = 0
    i = brace
    state = 'code'
    while i < len(src):
        ch = src[i]
        nx = src[i + 1] if i + 1 < len(src) else ''
        if state == 'code':
            if ch == '"': state = 'string'
            elif ch == "'": state = 'char'
            elif ch == '/' and nx == '/': state = 'line'; i += 1
            elif ch == '/' and nx == '*': state = 'block'; i += 1
            elif ch == '{': depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return start, i + 1
        elif state == 'string':
            if ch == '\\': i += 1
            elif ch == '"': state = 'code'
        elif state == 'char':
            if ch == '\\': i += 1
            elif ch == "'": state = 'code'
        elif state == 'line':
            if ch == '\n': state = 'code'
        elif state == 'block':
            if ch == '*' and nx == '/': state = 'code'; i += 1
        i += 1
    raise SystemExit(f'unclosed method: {signature}')


def replace_method(src: str, signature: str, replacement: str):
    a, b = method_span(src, signature)
    return src[:a] + replacement.rstrip() + src[b:]


# version and duplicate import cleanup
s = s.replace('import javax.swing.SwingConstants;\nimport javax.swing.SwingConstants;\n', 'import javax.swing.SwingConstants;\n')
s = s.replace('public static final String VERSION = "1.2.0";', 'public static final String VERSION = "1.2.1";', 1)
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.2.0");', 'SFIToolkit.displayln("HxWorkbench 1.2.1");', 1)
s = s.replace('this.setSize(new Dimension(1360, 820));', 'this.setSize(new Dimension(1672, 941));', 1)
s = s.replace('this.setMinimumSize(new Dimension(980, 620));', 'this.setMinimumSize(new Dimension(1280, 720));', 1)
# preview client area = reference screenshot minus Windows title bar
s = s.replace('var19x.setSize(1440, 860);', 'var19x.setSize(1672, 901);', 1)
s = s.replace('var20x.setSize(1440, 860);', 'var20x.setSize(1672, 901);', 1)

# exact OneClick page fields
anchor = '      private String activeSidebarKey = "home";\n'
insert = anchor + '''      private final JTextArea exactOneClickCommand = new JTextArea();\n      private final JLabel exactOneClickDataStatus = new JLabel("尚未载入数据", SwingConstants.CENTER);\n      private final JLabel exactOneClickDataDetail = new JLabel("选择一种方式开始，载入后这里会显示可滚动的只读数据表。", SwingConstants.CENTER);\n      private JPanel exactOneClickRoot;\n'''
if 'exactOneClickCommand' not in s:
    if anchor not in s: raise SystemExit('sidebar field anchor missing')
    s = s.replace(anchor, insert, 1)

# add dedicated OneClick stage
stage_anchor = '         this.stageCards.add(this.buildChooserContainer(), "chooser");\n         this.stageCards.add(this.commandDataSplit, "workspace");'
stage_insert = '         this.stageCards.add(this.buildChooserContainer(), "chooser");\n         this.stageCards.add(this.buildExactOneClickContainer(), "oneclick_exact");\n         this.stageCards.add(this.commandDataSplit, "workspace");'
if '"oneclick_exact"' not in s:
    if stage_anchor not in s: raise SystemExit('stage anchor missing')
    s = s.replace(stage_anchor, stage_insert, 1)

# colors closer to supplied reference
s = s.replace('private static final Color APP_BG = new Color(242, 245, 248);', 'private static final Color APP_BG = new Color(248, 250, 253);')
s = s.replace('private static final Color TEXT = new Color(24, 34, 48);', 'private static final Color TEXT = new Color(23, 35, 59);')
s = s.replace('private static final Color MUTED = new Color(99, 112, 131);', 'private static final Color MUTED = new Color(105, 120, 145);')
s = s.replace('private static final Color BORDER = new Color(216, 222, 231);', 'private static final Color BORDER = new Color(221, 228, 239);')
s = s.replace('private static final Color ACCENT = new Color(42, 102, 190);', 'private static final Color ACCENT = new Color(34, 109, 246);')
s = s.replace('private static final Color ACCENT_SOFT = new Color(232, 240, 252);', 'private static final Color ACCENT_SOFT = new Color(234, 243, 255);')

sidebar = r'''      private JComponent buildSidebar() {
         this.sidebarButtons.clear();
         JPanel sidebar = new JPanel(new BorderLayout());
         sidebar.setBackground(SURFACE);
         sidebar.setPreferredSize(new Dimension(205, 0));
         sidebar.setBorder(BorderFactory.createMatteBorder(0, 0, 0, 1, new Color(226, 232, 240)));

         JPanel nav = new JPanel();
         nav.setOpaque(false);
         nav.setBorder(new EmptyBorder(22, 11, 8, 11));
         nav.setLayout(new BoxLayout(nav, BoxLayout.Y_AXIS));
         nav.add(this.sidebarButton("home", "◆", "工作台", this::showHomePage));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("data", "▤", "数据", () -> this.browseCategoryOverview("data")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("reg", "↗", "回归", () -> this.browseMethod("reg", "线性模型")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("stats", "✓", "检验", () -> this.browseCategoryOverview("stats")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("oneclick", "◆", "OneClick", () -> this.browseMethodCategory("oneclick")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("history", "◷", "历史", () -> this.browseCommandCategory("recent", "最近任务")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("settings", "⚙", "设置", () -> this.openHomeTask("special", "performance")));
         sidebar.add(nav, BorderLayout.NORTH);

         JPanel bottom = new JPanel();
         bottom.setOpaque(false);
         bottom.setBorder(new EmptyBorder(8, 18, 20, 18));
         bottom.setLayout(new BoxLayout(bottom, BoxLayout.Y_AXIS));
         JButton guide = new JButton("<html><div style='text-align:left'><span style='font-size:22px;color:#2f76ed'>▣ ◕</span><br><b>新手指引</b><br><span style='font-size:9px;color:#718096'>5 分钟快速上手</span><br><span style='font-size:9px;color:#226df6'>立即查看  →</span></div></html>");
         guide.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(new Color(248, 251, 255), new Color(242, 247, 255), new Color(234, 242, 255), TEXT, new Color(210, 225, 248)));
         guide.setBorder(new EmptyBorder(12, 14, 12, 14));
         guide.setHorizontalAlignment(SwingConstants.LEFT);
         guide.setVerticalAlignment(SwingConstants.TOP);
         guide.setFocusPainted(false);
         guide.setContentAreaFilled(false);
         guide.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         guide.setMaximumSize(new Dimension(Integer.MAX_VALUE, 176));
         guide.setPreferredSize(new Dimension(168, 176));
         guide.setAlignmentX(0.0F);
         guide.addActionListener(e -> {
            HxWorkbench.StataBridge.execute("help hxempirical", false);
            HxWorkbench.StataBridge.execute("window manage forward viewer", false);
         });
         bottom.add(guide);
         bottom.add(Box.createVerticalStrut(22));
         JLabel version = new JLabel("版本：1.2.1");
         version.setForeground(MUTED);
         version.setFont(version.getFont().deriveFont(10.0F));
         version.setAlignmentX(0.0F);
         bottom.add(version);
         bottom.add(Box.createVerticalStrut(5));
         JLabel policy = new JLabel("隐私政策   意见反馈");
         policy.setForeground(ACCENT);
         policy.setFont(policy.getFont().deriveFont(10.0F));
         policy.setAlignmentX(0.0F);
         bottom.add(policy);
         sidebar.add(bottom, BorderLayout.SOUTH);
         this.setSidebarActive("home");
         return sidebar;
      }'''
s = replace_method(s, '      private JComponent buildSidebar()', sidebar)

# visual helpers inserted once
helpers = r'''
      private JPanel refCard() {
         JPanel p = new JPanel();
         p.setBackground(SURFACE);
         p.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220, 228, 240), 10), new EmptyBorder(14, 16, 14, 16)));
         return p;
      }

      private JButton refButton(String text, boolean primary) {
         JButton b = new JButton(text);
         Color bg = primary ? new Color(34, 109, 246) : SURFACE;
         Color hover = primary ? new Color(28, 94, 222) : new Color(247, 250, 254);
         Color pressed = primary ? new Color(24, 82, 198) : new Color(239, 244, 250);
         Color fg = primary ? Color.WHITE : TEXT;
         Color border = primary ? new Color(34, 109, 246) : new Color(215, 224, 237);
         b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(bg, hover, pressed, fg, border));
         b.setBorder(new EmptyBorder(8, 15, 8, 15));
         b.setFocusPainted(false);
         b.setContentAreaFilled(false);
         b.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         return b;
      }

      private JButton refTask(String glyph, String title, String subtitle, Color accent, Runnable action) {
         JButton b = new JButton("<html><div style='text-align:left'><span style='font-size:21px;color:" + html(colorHex(accent)) + "'>" + html(glyph) + "</span>&nbsp;&nbsp;<b>" + html(title) + "</b><br><span style='font-size:9px;color:#6b7890'>" + html(subtitle) + "</span></div></html>");
         b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(249, 251, 254), new Color(240, 245, 252), TEXT, new Color(221, 228, 239)));
         b.setBorder(new EmptyBorder(11, 14, 11, 14));
         b.setHorizontalAlignment(SwingConstants.LEFT);
         b.setFocusPainted(false);
         b.setContentAreaFilled(false);
         b.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         b.addActionListener(e -> action.run());
         return b;
      }

      private JButton refQuick(String glyph, String title, Runnable action) {
         JButton b = new JButton("<html><div style='text-align:center'><span style='font-size:20px;color:#2f76ed'>" + html(glyph) + "</span><br><b>" + html(title) + "</b></div></html>");
         b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 251, 255), new Color(239, 245, 253), TEXT, new Color(221, 228, 239)));
         b.setBorder(new EmptyBorder(8, 6, 8, 6));
         b.setFocusPainted(false);
         b.setContentAreaFilled(false);
         b.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         b.addActionListener(e -> action.run());
         return b;
      }

      private static String colorHex(Color c) {
         return String.format(Locale.ROOT, "#%02x%02x%02x", c.getRed(), c.getGreen(), c.getBlue());
      }

      private JPanel refSectionTitle(String text) {
         JPanel row = new JPanel(new BorderLayout());
         row.setOpaque(false);
         JLabel label = new JLabel(text);
         label.setForeground(TEXT);
         label.setFont(label.getFont().deriveFont(Font.BOLD, 14.0F));
         row.add(label, BorderLayout.WEST);
         return row;
      }

      private JPanel buildChooserRecommendationPanel() {
         JPanel right = this.refCard();
         right.setLayout(new BoxLayout(right, BoxLayout.Y_AXIS));
         right.setPreferredSize(new Dimension(240, 0));
         JLabel t = new JLabel("▥  推荐路径");
         t.setForeground(TEXT);
         t.setFont(t.getFont().deriveFont(Font.BOLD, 15.0F));
         t.setAlignmentX(0.0F);
         right.add(t);
         right.add(Box.createVerticalStrut(24));
         String[][] steps = {
            {"1", "先用常用命令", "从常用命令入手，快速完成基础分析。"},
            {"2", "看示例与说明", "查看示例与说明，理解命令用法与适用场景。"},
            {"3", "再进入进阶命令", "根据需求选择进阶命令，满足更复杂的分析。"}
         };
         Color[] colors = {new Color(34,109,246), new Color(31,169,105), new Color(118,83,224)};
         for (int i=0; i<steps.length; i++) {
            JPanel row = new JPanel(new BorderLayout(10, 0));
            row.setOpaque(false);
            JLabel n = new JLabel(steps[i][0], SwingConstants.CENTER);
            n.setOpaque(true); n.setBackground(colors[i]); n.setForeground(Color.WHITE);
            n.setFont(n.getFont().deriveFont(Font.BOLD, 12.0F));
            n.setPreferredSize(new Dimension(30,30));
            JPanel txt = new JPanel(); txt.setOpaque(false); txt.setLayout(new BoxLayout(txt, BoxLayout.Y_AXIS));
            JLabel a = new JLabel(steps[i][1]); a.setForeground(TEXT); a.setFont(a.getFont().deriveFont(Font.BOLD, 12.0F));
            JLabel d = new JLabel("<html><div style='width:145px;color:#718096'>"+html(steps[i][2])+"</div></html>");
            txt.add(a); txt.add(Box.createVerticalStrut(6)); txt.add(d);
            row.add(n, BorderLayout.WEST); row.add(txt, BorderLayout.CENTER);
            row.setMaximumSize(new Dimension(Integer.MAX_VALUE, 120));
            right.add(row);
            if (i < 2) { right.add(Box.createVerticalStrut(18)); }
         }
         right.add(Box.createVerticalGlue());
         JPanel tip = new JPanel(new BorderLayout(8,8));
         tip.setBackground(new Color(255,250,241));
         tip.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(255,219,166), 9), new EmptyBorder(13,13,13,13)));
         JLabel tipText = new JLabel("<html><b><span style='color:#f59e0b'>☼ 小贴士</span></b><br><br><span style='color:#68758b'>命令太多时，优先从常用命令开始，逐步深入更高阶方法！</span></html>");
         tip.add(tipText, BorderLayout.CENTER);
         tip.setMaximumSize(new Dimension(Integer.MAX_VALUE, 145));
         right.add(tip);
         return right;
      }

      private JButton chooserCommandCard(String cmd, String title, String desc, String example, Color accent) {
         JButton b = new JButton("<html><div style='text-align:left'><span style='font-size:10px;color:"+colorHex(accent)+"'><b>"+html(cmd)+"</b></span><br><span style='font-size:13px'><b>"+html(title)+"</b></span><br><span style='font-size:9px;color:#6f7d94'>"+html(desc)+"</span><br><span style='font-size:8px;color:"+colorHex(accent)+"'>示例："+html(example)+"</span></div></html>");
         b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(249,251,254), new Color(240,245,252), TEXT, new Color(220,228,239)));
         b.setBorder(new EmptyBorder(12, 16, 12, 16));
         b.setHorizontalAlignment(SwingConstants.LEFT);
         b.setVerticalAlignment(SwingConstants.TOP);
         b.setFocusPainted(false); b.setContentAreaFilled(false);
         b.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         b.addActionListener(e -> this.openCommandPage(cmd));
         return b;
      }

      private JPanel chooserGroup(String title, String[][] rows, Color accent) {
         JPanel g = this.refCard();
         g.setLayout(new BoxLayout(g, BoxLayout.Y_AXIS));
         JLabel h = new JLabel(title); h.setForeground(TEXT); h.setFont(h.getFont().deriveFont(Font.BOLD, 12.0F)); h.setAlignmentX(0.0F);
         g.add(h); g.add(Box.createVerticalStrut(8));
         for (String[] row : rows) {
            JButton b = new JButton("<html><div style='text-align:left'><b>"+html(row[0])+"</b>&nbsp;&nbsp;<span style='color:#68758b'>"+html(row[1])+"</span><span style='float:right'> ›</span></div></html>");
            b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(249,251,254), new Color(242,246,251), TEXT, SURFACE));
            b.setBorder(new EmptyBorder(5, 2, 5, 2)); b.setHorizontalAlignment(SwingConstants.LEFT); b.setFocusPainted(false); b.setContentAreaFilled(false);
            String cmd = row[0]; b.addActionListener(e -> this.openCommandPage(cmd));
            g.add(b);
         }
         return g;
      }
'''
if 'private JPanel refCard()' not in s:
    marker = '      private JComponent buildHomeContainer() {'
    pos = s.find(marker)
    if pos < 0: raise SystemExit('home marker missing')
    s = s[:pos] + helpers + '\n' + s[pos:]

home = r'''      private JComponent buildHomeContainer() {
         JPanel root = new JPanel(null);
         root.setBackground(APP_BG);
         root.setPreferredSize(new Dimension(1467, 840));

         JLabel title = new JLabel("实证工作台");
         title.setForeground(TEXT); title.setFont(title.getFont().deriveFont(Font.BOLD, 26.0F));
         title.setBounds(38, 25, 300, 38); root.add(title);
         JLabel subtitle = new JLabel("从数据导入到结果分析，一站式完成您的实证研究。");
         subtitle.setForeground(MUTED); subtitle.setFont(subtitle.getFont().deriveFont(11.5F));
         subtitle.setBounds(38, 63, 520, 24); root.add(subtitle);

         JButton openStata = this.refButton("▣  打开 Stata", false);
         openStata.setBounds(1240, 28, 120, 38); openStata.addActionListener(e -> this.setState(JFrame.ICONIFIED)); root.add(openStata);
         JButton help = this.refButton("?", false); help.setBounds(1375, 28, 44, 38); help.addActionListener(e -> this.openHelp()); root.add(help);

         JPanel hero = this.refCard(); hero.setLayout(null); hero.setBackground(new Color(246,250,255)); hero.setBounds(25, 105, 975, 210);
         JLabel rocket = new JLabel("◆"); rocket.setForeground(new Color(53,116,239)); rocket.setFont(rocket.getFont().deriveFont(Font.BOLD, 31.0F)); rocket.setBounds(24, 20, 42, 42); hero.add(rocket);
         JLabel start = new JLabel("开始分析"); start.setForeground(TEXT); start.setFont(start.getFont().deriveFont(Font.BOLD, 22.0F)); start.setBounds(72, 18, 190, 34); hero.add(start);
         JLabel startHint = new JLabel("告诉我你想做什么"); startHint.setForeground(MUTED); startHint.setBounds(72, 50, 180, 22); hero.add(startHint);
         styleTextField(this.searchField); this.searchField.setFont(this.searchField.getFont().deriveFont(12.0F)); this.searchField.setToolTipText("搜索功能或输入分析目的..."); this.searchField.setBounds(25, 86, 405, 42); hero.add(this.searchField);
         JButton startBtn = this.refButton("开始", true); startBtn.setBounds(430, 86, 82, 42); startBtn.addActionListener(e -> this.smartHomeSearch()); hero.add(startBtn);
         this.searchField.addActionListener(e -> this.smartHomeSearch());
         JLabel tryIt = new JLabel("试试： 基准回归、固定效应、双重差分、相关分析、描述统计"); tryIt.setForeground(MUTED); tryIt.setFont(tryIt.getFont().deriveFont(10.0F)); tryIt.setBounds(25, 138, 490, 24); hero.add(tryIt);
         JSeparatorLike divider = new JSeparatorLike(); divider.setBounds(545, 32, 1, 142); hero.add(divider);
         JLabel quick = new JLabel("快速开始"); quick.setForeground(TEXT); quick.setFont(quick.getFont().deriveFont(Font.BOLD, 14.0F)); quick.setBounds(575, 20, 120, 26); hero.add(quick);
         JPanel quickGrid = new JPanel(new GridLayout(1,5,10,0)); quickGrid.setOpaque(false); quickGrid.setBounds(575, 55, 375, 92);
         quickGrid.add(this.refQuick("↗", "基准回归", this::openBaselineRegressionWorkspace));
         quickGrid.add(this.refQuick("▱", "固定效应", () -> this.browseMethod("reg", "固定效应线性回归")));
         quickGrid.add(this.refQuick("↗", "双重差分", () -> this.browseMethod("reg", "双重差分")));
         quickGrid.add(this.refQuick("◕", "描述统计", () -> this.browseMethod("stats", "描述统计")));
         quickGrid.add(this.refQuick("✦", "OneClick", () -> this.browseMethodCategory("oneclick")));
         hero.add(quickGrid); root.add(hero);

         JPanel data = this.refCard(); data.setLayout(null); data.setBounds(1015, 105, 425, 235);
         JLabel dataTitle = new JLabel("当前数据"); dataTitle.setForeground(TEXT); dataTitle.setFont(dataTitle.getFont().deriveFont(Font.BOLD, 14.0F)); dataTitle.setBounds(20, 16, 120, 26); data.add(dataTitle);
         JLabel folder = new JLabel("▰", SwingConstants.CENTER); folder.setForeground(new Color(128,171,241)); folder.setFont(folder.getFont().deriveFont(Font.BOLD, 48.0F)); folder.setBounds(135, 42, 150, 60); data.add(folder);
         this.homeDatasetStatus.setHorizontalAlignment(SwingConstants.CENTER); this.homeDatasetStatus.setForeground(TEXT); this.homeDatasetStatus.setFont(this.homeDatasetStatus.getFont().deriveFont(Font.BOLD, 14.0F)); this.homeDatasetStatus.setBounds(50, 105, 325, 28); data.add(this.homeDatasetStatus);
         this.homeDatasetDetail.setHorizontalAlignment(SwingConstants.CENTER); this.homeDatasetDetail.setForeground(MUTED); this.homeDatasetDetail.setFont(this.homeDatasetDetail.getFont().deriveFont(10.0F)); this.homeDatasetDetail.setBounds(35, 132, 355, 23); data.add(this.homeDatasetDetail);
         JButton dta = this.refButton("打开 DTA 文件", true); dta.setBounds(20, 170, 118, 38); dta.addActionListener(e -> this.chooseAndLoadDta()); data.add(dta);
         JButton excel = this.refButton("导入 Excel / CSV", false); excel.setBounds(145,170,138,38); excel.addActionListener(e -> this.navigateTo("data", "导入与转换", "hxconvert")); data.add(excel);
         JButton auto = this.refButton("载入 auto 示例", false); auto.setBounds(290,170,115,38); auto.addActionListener(e -> this.runUtility("sysuse auto, clear", true)); data.add(auto); root.add(data);

         JPanel common = this.refCard(); common.setLayout(null); common.setBounds(25, 335, 975, 300);
         JLabel commonTitle = new JLabel("常用任务"); commonTitle.setForeground(TEXT); commonTitle.setFont(commonTitle.getFont().deriveFont(Font.BOLD, 14.0F)); commonTitle.setBounds(16, 12, 120, 26); common.add(commonTitle);
         JPanel taskGrid = new JPanel(new GridLayout(2,3,16,16)); taskGrid.setOpaque(false); taskGrid.setBounds(16, 48, 943, 225);
         taskGrid.add(this.refTask("▤", "导入数据", "从 Excel / CSV / DTA 等文件导入数据", new Color(33,176,93), () -> this.navigateTo("data", "导入与转换", "hxconvert")));
         taskGrid.add(this.refTask("▥", "描述统计", "汇总统计、分组统计、变量分布等", new Color(57,125,242), () -> this.browseMethod("stats", "描述统计")));
         taskGrid.add(this.refTask("◎", "基准回归（OLS）", "线性回归分析，快速估计模型", new Color(142,91,230), this::openBaselineRegressionWorkspace));
         taskGrid.add(this.refTask("◉", "固定效应", "个体 / 时间 / 双向固定效应回归", new Color(245,138,45), () -> this.browseMethod("reg", "固定效应线性回归")));
         taskGrid.add(this.refTask("DID", "双重差分（DID）", "政策评估的经典方法，简单易用", new Color(31,180,151), () -> this.browseMethod("reg", "双重差分")));
         taskGrid.add(this.refTask("ϟ", "OneClick 分析", "一键完成常见分析流程，自动生成结果报告", new Color(57,120,244), () -> this.browseMethodCategory("oneclick")));
         common.add(taskGrid); root.add(common);

         JPanel recent = this.refCard(); recent.setLayout(new BorderLayout(0,8)); recent.setBounds(1015, 355, 425, 280);
         JPanel recentHead = new JPanel(new BorderLayout()); recentHead.setOpaque(false); JLabel recentTitle = new JLabel("最近任务"); recentTitle.setForeground(TEXT); recentTitle.setFont(recentTitle.getFont().deriveFont(Font.BOLD,14.0F)); recentHead.add(recentTitle, BorderLayout.WEST); JLabel all = new JLabel("查看全部"); all.setForeground(ACCENT); all.setFont(all.getFont().deriveFont(10.0F)); recentHead.add(all, BorderLayout.EAST); recent.add(recentHead, BorderLayout.NORTH);
         this.homeRecentPanel.setOpaque(false); this.homeRecentPanel.setLayout(new BoxLayout(this.homeRecentPanel, BoxLayout.Y_AXIS)); recent.add(this.homeRecentPanel, BorderLayout.CENTER);
         JButton resume = this.refButton("◴  继续上次工作                       ›", false); resume.addActionListener(e -> { List<WorkSnapshot> snaps=this.loadRecentSnapshots(); if(!snaps.isEmpty()) this.restoreWorkSnapshot(snaps.get(0)); }); recent.add(resume, BorderLayout.SOUTH); root.add(recent);

         JPanel more = this.refCard(); more.setLayout(null); more.setBounds(25, 655, 1415, 176);
         JLabel moreTitle = new JLabel("更多功能"); moreTitle.setForeground(TEXT); moreTitle.setFont(moreTitle.getFont().deriveFont(Font.BOLD,14.0F)); moreTitle.setBounds(16,10,120,25); more.add(moreTitle);
         JPanel moreGrid = new JPanel(new GridLayout(1,9,10,0)); moreGrid.setOpaque(false); moreGrid.setBounds(16,43,1383,108);
         moreGrid.add(this.refTask("↔", "导入与转换", "Excel / CSV / DTA 格式转换", new Color(87,140,245), () -> this.navigateTo("data", "导入与转换", "hxconvert")));
         moreGrid.add(this.refTask("◔", "数据检查", "缺失值、重复值、异常值", new Color(37,180,144), () -> this.browseMethod("data", "数据检查")));
         moreGrid.add(this.refTask("▣", "变量处理", "生成变量、编码、标签管理", new Color(229,170,52), () -> this.browseMethod("data", "变量处理")));
         moreGrid.add(this.refTask("♙", "样本处理", "筛选、子样本、随机抽样", new Color(159,91,225), () -> this.browseMethod("data", "样本处理")));
         moreGrid.add(this.refTask("▱", "合并与追加", "合并数据集、追加数据", new Color(73,125,242), () -> this.browseMethod("data", "合并与追加")));
         moreGrid.add(this.refTask("▣", "数据结构", "reshape 长宽转换、面板设定", new Color(31,169,105), () -> this.browseMethod("data", "数据结构")));
         moreGrid.add(this.refTask("⌕", "相关分析", "相关系数、协方差、相关矩阵", new Color(38,171,219), () -> this.browseMethod("stats", "相关分析")));
         moreGrid.add(this.refTask("◒", "均值检验", "t 检验、方差分析、秩和检验", new Color(229,164,30), () -> this.browseMethod("stats", "均值检验")));
         moreGrid.add(this.refTask("▦", "频数列联", "频数统计、交叉表、卡方检验", new Color(139,86,223), () -> this.browseMethod("stats", "频数列联")));
         more.add(moreGrid); root.add(more);
         SwingUtilities.invokeLater(this::refreshHomeContext);
         return root;
      }'''
s = replace_method(s, '      private JComponent buildHomeContainer()', home)

# tiny custom separator class usage; insert nested helper class before FlatButtonUI
sep_class = r'''
      private static final class JSeparatorLike extends JComponent {
         JSeparatorLike() { setOpaque(false); }
         @Override protected void paintComponent(Graphics g) { super.paintComponent(g); g.setColor(new Color(225,231,239)); g.fillRect(0,0,Math.max(1,getWidth()),getHeight()); }
      }
'''
if 'class JSeparatorLike' not in s:
    marker = '      private static final class FlatButtonUI'
    pos = s.find(marker)
    if pos < 0: raise SystemExit('FlatButtonUI marker missing')
    s = s[:pos] + sep_class + '\n' + s[pos:]

chooser_container = r'''      private JComponent buildChooserContainer() {
         JPanel root = new JPanel(new BorderLayout(18, 0));
         root.setBackground(APP_BG);
         root.setBorder(new EmptyBorder(18, 22, 14, 22));

         JPanel center = new JPanel(new BorderLayout(0, 12)); center.setOpaque(false);
         JPanel header = new JPanel(); header.setOpaque(false); header.setLayout(new BoxLayout(header, BoxLayout.Y_AXIS));
         this.chooserBreadcrumbBar.setOpaque(false); this.chooserBreadcrumbBar.setAlignmentX(0.0F); header.add(this.chooserBreadcrumbBar); header.add(Box.createVerticalStrut(8));
         JPanel titleRow = new JPanel(new BorderLayout()); titleRow.setOpaque(false);
         JPanel titles = new JPanel(); titles.setOpaque(false); titles.setLayout(new BoxLayout(titles, BoxLayout.Y_AXIS));
         this.chooserTitle.setForeground(TEXT); this.chooserTitle.setFont(this.chooserTitle.getFont().deriveFont(Font.BOLD, 26.0F)); titles.add(this.chooserTitle); titles.add(Box.createVerticalStrut(5));
         this.chooserHint.setForeground(MUTED); this.chooserHint.setFont(this.chooserHint.getFont().deriveFont(11.0F)); titles.add(this.chooserHint); titleRow.add(titles, BorderLayout.WEST);
         JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT,8,0)); actions.setOpaque(false);
         JButton back = this.refButton("←  返回上一级", false); back.addActionListener(e -> this.showHomePage());
         JButton home = this.refButton("⌂  首页", false); home.addActionListener(e -> this.showHomePage());
         JButton help = this.refButton("?  帮助", false); help.addActionListener(e -> this.openHelp()); actions.add(back); actions.add(home); actions.add(help); titleRow.add(actions, BorderLayout.EAST);
         header.add(titleRow); center.add(header, BorderLayout.NORTH);

         this.chooserContent.setOpaque(false); this.chooserContent.setLayout(new BoxLayout(this.chooserContent, BoxLayout.Y_AXIS));
         JScrollPane scroll = new JScrollPane(this.chooserContent); scroll.setBorder(null); scroll.setOpaque(false); scroll.getViewport().setOpaque(false); scroll.getVerticalScrollBar().setUnitIncrement(18); center.add(scroll, BorderLayout.CENTER);
         root.add(center, BorderLayout.CENTER);
         root.add(this.buildChooserRecommendationPanel(), BorderLayout.EAST);
         return root;
      }'''
s = replace_method(s, '      private JComponent buildChooserContainer()', chooser_container)

render_chooser = r'''      private void renderCommandChooser(String var1, String var2, List<String> var3) {
         this.setChooserBreadcrumb("首页  /  " + (this.activeCategoryName.isBlank() ? var1 : this.activeCategoryName) + (var2.isBlank() ? "" : "  /  " + var2));
         boolean linear = "reg".equals(this.activeCategoryCode) && ("线性模型".equals(var2) || "线性模型".equals(var1));
         this.chooserTitle.setText(linear ? "线性模型" : (var2.isBlank() ? var1 : var2));
         this.chooserHint.setText(linear ? "先选分析目的，再进入具体命令。常用命令优先展示，其余命令按类别收纳。" : "选择一个命令进入设置；常用项优先，进阶项继续向下浏览。");
         this.chooserContent.removeAll();

         JPanel search = this.refCard(); search.setLayout(new BorderLayout(12,0)); search.setMaximumSize(new Dimension(Integer.MAX_VALUE, 58)); search.setAlignmentX(0.0F);
         JTextField field = new JTextField(); styleTextField(field); field.setToolTipText("搜索命令或分析目的"); field.setPreferredSize(new Dimension(600,38)); search.add(field, BorderLayout.CENTER);
         JPanel filters = new JPanel(new FlowLayout(FlowLayout.RIGHT,6,0)); filters.setOpaque(false); filters.add(this.refButton("全部", true)); filters.add(this.refButton("常用", false)); filters.add(this.refButton("进阶", false)); filters.add(this.refButton("筛选排序", false)); search.add(filters, BorderLayout.EAST);
         this.chooserContent.add(search); this.chooserContent.add(Box.createVerticalStrut(10));

         if (linear) {
            JPanel choose = this.refCard(); choose.setLayout(new FlowLayout(FlowLayout.LEFT,10,2)); choose.setMaximumSize(new Dimension(Integer.MAX_VALUE, 60)); choose.setAlignmentX(0.0F);
            JLabel how = new JLabel("●  怎么选？"); how.setForeground(TEXT); how.setFont(how.getFont().deriveFont(Font.BOLD,14.0F)); choose.add(how);
            choose.add(this.refButton("普通 OLS → regress", false)); choose.add(this.refButton("单组固定效应 → areg", false)); choose.add(this.refButton("多维固定效应 → reghdfe", false)); choose.add(this.refButton("关注分布位置 → qreg", false));
            this.chooserContent.add(choose); this.chooserContent.add(Box.createVerticalStrut(10));

            JPanel common = this.refCard(); common.setLayout(new BorderLayout(0,10)); common.setAlignmentX(0.0F);
            JLabel ct = new JLabel("常用命令"); ct.setForeground(TEXT); ct.setFont(ct.getFont().deriveFont(Font.BOLD,14.0F)); common.add(ct, BorderLayout.NORTH);
            JPanel grid = new JPanel(new GridLayout(2,2,16,12)); grid.setOpaque(false);
            grid.add(this.chooserCommandCard("regress", "普通线性回归", "用 OLS 估计连续因变量与解释变量的线性关系。", "regress y x c1 c2, vce(robust)", new Color(54,114,236)));
            grid.add(this.chooserCommandCard("areg", "单组固定效应", "在回归中吸收一组大量类别固定效应。", "areg y x c, absorb(firm)", new Color(29,164,101)));
            grid.add(this.chooserCommandCard("reghdfe", "高维固定效应回归", "高效吸收多组固定效应并支持聚类标准误。", "reghdfe y x c, absorb(firm year) vce(cluster firm)", new Color(245,125,30)));
            grid.add(this.chooserCommandCard("qreg", "分位数回归", "估计解释变量对条件分布不同分位点的影响。", "qreg y x c, quantile(.5)", new Color(134,84,225)));
            common.add(grid, BorderLayout.CENTER); common.setMaximumSize(new Dimension(Integer.MAX_VALUE, 292)); this.chooserContent.add(common); this.chooserContent.add(Box.createVerticalStrut(10));

            JPanel more = this.refCard(); more.setLayout(new BorderLayout(0,10)); more.setAlignmentX(0.0F); JLabel mt = new JLabel("更多线性模型"); mt.setForeground(TEXT); mt.setFont(mt.getFont().deriveFont(Font.BOLD,14.0F)); more.add(mt, BorderLayout.NORTH);
            JPanel groups = new JPanel(new GridLayout(1,4,12,0)); groups.setOpaque(false);
            groups.add(this.chooserGroup("◈  稳健与异常值处理", new String[][]{{"rreg","稳健回归（M-估计）"},{"cnsreg","截面回归（修正样本选择）"},{"newey","Newey-West 标准误"}}, new Color(47,104,213)));
            groups.add(this.chooserGroup("⚖  加权与广义最小二乘", new String[][]{{"regressw","加权最小二乘"},{"vwls","可变加权最小二乘"},{"gls","广义最小二乘"},{"prais","可行广义最小二乘"}}, new Color(37,172,92)));
            groups.add(this.chooserGroup("⚑  工具变量与内生性", new String[][]{{"ivregress","工具变量回归"},{"ivreg","2SLS 回归"},{"ivprobit","工具变量 Probit"},{"control","控制函数法"}}, new Color(245,128,30)));
            groups.add(this.chooserGroup("▦  其他线性扩展", new String[][]{{"sureg","联立方程回归"},{"seemingly","似不相关回归"},{"seemingly2","似不相关回归（扩展）"},{"ml","最大似然回归"}}, new Color(132,85,220)));
            more.add(groups, BorderLayout.CENTER); more.setMaximumSize(new Dimension(Integer.MAX_VALUE, 205)); this.chooserContent.add(more);
         } else {
            JPanel common = this.refCard(); common.setLayout(new BorderLayout(0,10)); common.setAlignmentX(0.0F); JLabel ct = new JLabel("可用命令"); ct.setForeground(TEXT); ct.setFont(ct.getFont().deriveFont(Font.BOLD,14.0F)); common.add(ct, BorderLayout.NORTH);
            int cols = var3.size() > 1 ? 2 : 1; JPanel grid = new JPanel(new GridLayout(0,cols,12,12)); grid.setOpaque(false);
            for (String cmd : var3) {
               CommandGuide g = COMMAND_GUIDES.get(cmd); String title = g == null ? cmd : g.title; String desc = g == null ? "进入命令设置页查看参数。" : g.intent; String ex = g == null ? cmd : g.example;
               grid.add(this.chooserCommandCard(cmd,title,desc,ex,new Color(54,114,236)));
            }
            common.add(grid,BorderLayout.CENTER); this.chooserContent.add(common);
         }
         this.chooserContent.add(Box.createVerticalGlue());
         this.chooserContent.revalidate(); this.chooserContent.repaint(); this.chooserReady = true; this.inspectorToggle.setVisible(false); this.stageLayout.show(this.stageCards, "chooser"); this.syncSidebarFromContext();
      }'''
s = replace_method(s, '      private void renderCommandChooser(String var1, String var2, List<String> var3)', render_chooser)

# dedicated OneClick page helpers and page
oneclick_helpers = r'''
      private JComponent buildExactOneClickContainer() {
         JPanel root = new JPanel(null); root.setBackground(APP_BG); root.setPreferredSize(new Dimension(1467,840)); this.exactOneClickRoot = root;
         JLabel crumb = new JLabel("首页  /  OneClick 专区  /  控制变量组合筛选  /  oneclick"); crumb.setForeground(new Color(91,111,144)); crumb.setFont(crumb.getFont().deriveFont(10.5F)); crumb.setBounds(20,16,620,24); root.add(crumb);
         JLabel title = new JLabel("控制变量组合筛选 · 外部 OneClick"); title.setForeground(TEXT); title.setFont(title.getFont().deriveFont(Font.BOLD,22.0F)); title.setBounds(20,45,520,32); root.add(title);
         JLabel sub = new JLabel("本页用于调用外部 oneclick 命令。你只需选择 Y、核心 X、候选控制变量和模型方法，工具将自动为你组装命令。"); sub.setForeground(MUTED); sub.setFont(sub.getFont().deriveFont(10.0F)); sub.setBounds(20,78,720,24); root.add(sub);
         JButton back = this.refButton("←  返回上一级", false); back.setBounds(995,20,140,38); back.addActionListener(e -> this.browseMethodCategory("oneclick")); root.add(back);
         JButton home = this.refButton("⌂  首页", false); home.setBounds(1145,20,105,38); home.addActionListener(e -> this.showHomePage()); root.add(home);
         JButton help = this.refButton("?  查看帮助", false); help.setBounds(1260,20,120,38); help.addActionListener(e -> this.openHelp()); root.add(help);

         JPanel scenario = this.refCard(); scenario.setLayout(new FlowLayout(FlowLayout.LEFT,12,0)); scenario.setBounds(16,108,745,52); JLabel sc = new JLabel("?  适合什么场景？"); sc.setForeground(TEXT); sc.setFont(sc.getFont().deriveFont(Font.BOLD,13.0F)); scenario.add(sc); scenario.add(this.refButton("控制变量筛选", false)); scenario.add(this.refButton("稳健性比较", false)); scenario.add(this.refButton("外部命令调用", false)); root.add(scenario);

         JPanel quick = this.refCard(); quick.setLayout(null); quick.setBounds(16,170,745,130); JLabel qt = new JLabel("快速理解 OneClick"); qt.setForeground(TEXT); qt.setFont(qt.getFont().deriveFont(Font.BOLD,13.0F)); qt.setBounds(14,8,200,22); quick.add(qt);
         String[][] q = {{"01","选择核心变量：Y、核心 X","确定因变量与核心解释变量。"},{"02","添加候选控制变量","从当前数据中选择候选控制变量。"},{"03","选择模型方法并运行","工具组装命令并运行外部 oneclick。"}};
         for(int i=0;i<3;i++){ int x=14+i*238; JPanel step=new JPanel(new BorderLayout(8,0)); step.setBackground(SURFACE); step.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220,228,239),8),new EmptyBorder(10,10,10,10))); step.setBounds(x,38,220,70); JLabel n=new JLabel(q[i][0],SwingConstants.CENTER); n.setOpaque(true); n.setBackground(new Color(34,109,246)); n.setForeground(Color.WHITE); n.setFont(n.getFont().deriveFont(Font.BOLD,12.0F)); n.setPreferredSize(new Dimension(31,31)); JPanel txt=new JPanel(); txt.setOpaque(false); txt.setLayout(new BoxLayout(txt,BoxLayout.Y_AXIS)); JLabel a=new JLabel(q[i][1]); a.setForeground(TEXT); a.setFont(a.getFont().deriveFont(Font.BOLD,10.5F)); JLabel d=new JLabel("<html><span style='font-size:8px;color:#718096'>"+html(q[i][2])+"</span></html>"); txt.add(a); txt.add(Box.createVerticalStrut(4)); txt.add(d); step.add(n,BorderLayout.WEST); step.add(txt,BorderLayout.CENTER); quick.add(step); }
         JLabel history = new JLabel("ⓘ  运行后命令会写入 Stata History。"); history.setForeground(MUTED); history.setFont(history.getFont().deriveFont(9.0F)); history.setBounds(14,108,300,18); quick.add(history); root.add(quick);

         JPanel settings = this.refCard(); settings.setLayout(null); settings.setBounds(16,310,745,270); JLabel st = new JLabel("⚙  参数设置"); st.setForeground(TEXT); st.setFont(st.getFont().deriveFont(Font.BOLD,13.0F)); st.setBounds(14,8,150,22); settings.add(st);
         styleCombo(this.oneClickY); styleCombo(this.oneClickX); styleCombo(this.oneClickEstimator); styleCombo(this.oneClickP); styleTextField(this.oneClickModelOptions); styleTextField(this.options);
         JLabel ly=new JLabel("因变量  Y"); ly.setForeground(TEXT); ly.setBounds(14,42,100,22); settings.add(ly); this.oneClickY.setBounds(145,40,225,32); settings.add(this.oneClickY);
         JLabel lx=new JLabel("核心解释变量  X"); lx.setForeground(TEXT); lx.setBounds(385,42,120,22); settings.add(lx); this.oneClickX.setBounds(505,40,220,32); settings.add(this.oneClickX);
         JLabel lc=new JLabel("候选控制变量"); lc.setForeground(TEXT); lc.setBounds(14,82,110,22); settings.add(lc); JScrollPane cps=softScroll(this.oneClickCandidates); cps.setBounds(145,80,580,45); settings.add(cps);
         JLabel lr=new JLabel("固定变量 fix(x) required"); lr.setForeground(TEXT); lr.setBounds(14,134,130,22); settings.add(lr); JScrollPane rps=softScroll(this.oneClickRequired); rps.setBounds(145,132,580,38); settings.add(rps);
         JLabel lp=new JLabel("显著性水平 p(#)"); lp.setForeground(TEXT); lp.setBounds(14,180,120,22); settings.add(lp); this.oneClickP.setBounds(145,178,210,32); settings.add(this.oneClickP);
         JLabel lm=new JLabel("模型方法 m(method)"); lm.setForeground(TEXT); lm.setBounds(385,180,130,22); settings.add(lm); this.oneClickEstimator.setBounds(520,178,205,32); settings.add(this.oneClickEstimator);
         JLabel lo=new JLabel("可选模型附加项 [o]"); lo.setForeground(TEXT); lo.setBounds(14,222,130,22); settings.add(lo); this.oneClickModelOptions.setBounds(145,220,210,32); settings.add(this.oneClickModelOptions);
         JLabel lz=new JLabel("其他选项 [z]"); lz.setForeground(TEXT); lz.setBounds(385,222,110,22); settings.add(lz); this.options.setBounds(520,220,205,32); settings.add(this.options); root.add(settings);

         JPanel explain = this.refCard(); explain.setLayout(new BorderLayout(12,0)); explain.setBounds(16,590,745,96); JLabel ex = new JLabel("<html><b>◉  方法说明</b><br><br>• 本工具通过外部 oneclick 命令完成控制变量组合筛选。<br>• 运行后，工具会自动读取生成的 subset.dta，用于在右侧查看数据与结果。</html>"); ex.setForeground(TEXT); explain.add(ex,BorderLayout.CENTER); JTextArea syntax=new JTextArea("oneclick y candidates, fix(x required) p(#) m(method)\n[o(model_options)] [z]"); syntax.setEditable(false); syntax.setBackground(CODE_BG); syntax.setForeground(TEXT); syntax.setFont(new Font("Monospaced",Font.PLAIN,10)); syntax.setBorder(new EmptyBorder(8,10,8,10)); syntax.setPreferredSize(new Dimension(350,68)); explain.add(syntax,BorderLayout.EAST); root.add(explain);

         JPanel command = this.refCard(); command.setLayout(null); command.setBounds(16,696,745,106); JLabel ctitle=new JLabel("即将执行的 Stata 命令"); ctitle.setForeground(TEXT); ctitle.setFont(ctitle.getFont().deriveFont(Font.BOLD,12.0F)); ctitle.setBounds(14,6,190,22); command.add(ctitle); this.exactOneClickCommand.setEditable(false); this.exactOneClickCommand.setLineWrap(true); this.exactOneClickCommand.setWrapStyleWord(true); this.exactOneClickCommand.setBackground(new Color(244,248,255)); this.exactOneClickCommand.setForeground(TEXT); this.exactOneClickCommand.setFont(new Font("Monospaced",Font.PLAIN,10)); this.exactOneClickCommand.setBorder(new EmptyBorder(9,10,9,10)); JScrollPane cs=softScroll(this.exactOneClickCommand); cs.setBounds(14,32,420,55); command.add(cs); JButton copy=this.refButton("复制命令",false); copy.setBounds(450,39,110,38); copy.addActionListener(e->{ Toolkit.getDefaultToolkit().getSystemClipboard().setContents(new StringSelection(this.exactOneClickCommand.getText()),null); }); command.add(copy); JButton run=this.refButton("▶  运行外部 OneClick",true); run.setBounds(570,39,155,38); run.addActionListener(e->this.runOneClick()); command.add(run); root.add(command);

         JPanel data = this.refCard(); data.setLayout(null); data.setBounds(780,108,400,694); JLabel dt=new JLabel("▣  当前数据"); dt.setForeground(TEXT); dt.setFont(dt.getFont().deriveFont(Font.BOLD,13.0F)); dt.setBounds(16,10,160,25); data.add(dt); JButton refresh=this.refButton("↻ 刷新",false); refresh.setBounds(310,9,70,32); refresh.addActionListener(e->this.refreshDataset(false)); data.add(refresh); JLabel tabs=new JLabel("数据     |     结果     |     日志"); tabs.setForeground(new Color(54,108,220)); tabs.setBounds(20,52,260,24); data.add(tabs); JLabel ill=new JLabel("▰",SwingConstants.CENTER); ill.setForeground(new Color(126,172,240)); ill.setFont(ill.getFont().deriveFont(Font.BOLD,54.0F)); ill.setBounds(100,150,200,80); data.add(ill); this.exactOneClickDataStatus.setForeground(TEXT); this.exactOneClickDataStatus.setFont(this.exactOneClickDataStatus.getFont().deriveFont(Font.BOLD,14.0F)); this.exactOneClickDataStatus.setBounds(45,238,310,30); data.add(this.exactOneClickDataStatus); this.exactOneClickDataDetail.setForeground(MUTED); this.exactOneClickDataDetail.setFont(this.exactOneClickDataDetail.getFont().deriveFont(9.5F)); this.exactOneClickDataDetail.setBounds(30,270,340,25); data.add(this.exactOneClickDataDetail); JButton au=this.refButton("▣  载入 auto 示例数据",false); au.setBounds(62,320,275,40); au.addActionListener(e->this.runUtility("sysuse auto, clear",true)); data.add(au); JButton own=this.refButton("↥  载入自己的 DTA",false); own.setBounds(62,370,275,40); own.addActionListener(e->this.chooseAndLoadDta()); data.add(own); JButton cv=this.refButton("▤  Excel / CSV 转换为 DTA",false); cv.setBounds(62,420,275,40); cv.addActionListener(e->this.navigateTo("data","导入与转换","hxconvert")); data.add(cv); JLabel hint=new JLabel("☼  提示：左侧完成变量设置，右侧查看数据与结果。"); hint.setForeground(MUTED); hint.setBounds(45,610,320,30); data.add(hint); root.add(data);

         JPanel recommend=this.refCard(); recommend.setLayout(new BoxLayout(recommend,BoxLayout.Y_AXIS)); recommend.setBounds(1195,108,245,694); JLabel rt=new JLabel("▥  推荐流程"); rt.setForeground(TEXT); rt.setFont(rt.getFont().deriveFont(Font.BOLD,14.0F)); rt.setAlignmentX(0.0F); recommend.add(rt); recommend.add(Box.createVerticalStrut(22)); String[][] rs={{"1","先确定核心变量","明确因变量 Y 与核心解释变量 X。"},{"2","再放入候选控制变量","根据理论与数据特征，添加候选控制变量。"},{"3","最后选择模型并运行","选择模型方法与显著性水平，运行外部 OneClick。"}}; Color[] rc={new Color(34,109,246),new Color(31,169,105),new Color(116,83,224)}; for(int i=0;i<3;i++){ JPanel rr=new JPanel(new BorderLayout(10,0)); rr.setOpaque(false); JLabel n=new JLabel(rs[i][0],SwingConstants.CENTER); n.setOpaque(true); n.setBackground(rc[i]); n.setForeground(Color.WHITE); n.setPreferredSize(new Dimension(29,29)); JPanel tx=new JPanel(); tx.setOpaque(false); tx.setLayout(new BoxLayout(tx,BoxLayout.Y_AXIS)); JLabel a=new JLabel(rs[i][1]); a.setForeground(TEXT); a.setFont(a.getFont().deriveFont(Font.BOLD,11.0F)); JLabel d=new JLabel("<html><div style='width:155px;color:#718096'>"+html(rs[i][2])+"</div></html>"); tx.add(a); tx.add(Box.createVerticalStrut(6)); tx.add(d); rr.add(n,BorderLayout.WEST); rr.add(tx,BorderLayout.CENTER); rr.setMaximumSize(new Dimension(Integer.MAX_VALUE,120)); recommend.add(rr); recommend.add(Box.createVerticalStrut(14)); } recommend.add(Box.createVerticalGlue()); JPanel tip=new JPanel(new BorderLayout()); tip.setBackground(new Color(255,250,241)); tip.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(255,219,166),9),new EmptyBorder(13,13,13,13))); tip.add(new JLabel("<html><b><span style='color:#f59e0b'>☼ 小贴士</span></b><br><br><span style='color:#68758b'>OneClick 最适合比较不同控制变量组合的稳健性结果，而不是替代理论选择。</span></html>"),BorderLayout.CENTER); tip.setMaximumSize(new Dimension(Integer.MAX_VALUE,150)); recommend.add(tip); root.add(recommend);
         return root;
      }
'''
if 'private JComponent buildExactOneClickContainer()' not in s:
    marker = '      private void showOneClickPage(String var1) {'
    pos = s.find(marker)
    if pos < 0: raise SystemExit('oneclick marker missing')
    s = s[:pos] + oneclick_helpers + '\n' + s[pos:]

show_one = r'''      private void showOneClickPage(String var1) {
         this.currentCommand = var1;
         this.activeCategoryCode = "oneclick";
         this.activeCategoryName = "OneClick 专区";
         this.activeMethodName = "oneclick_robustness".equals(var1) ? "控制变量组合稳健性" : "控制变量组合筛选";
         this.regressWorkspaceActive = false;
         this.baselineTaskActive = false;
         this.refreshVariableControls();
         this.syncSidebarFromContext();
         this.setSidebarActive("oneclick");
         if (!this.previewMode) {
            HxWorkbench.StataBridge.execute("quietly hxresolve " + var1, false);
            this.offerOptionalDependency(var1);
         }
         this.exactOneClickDataStatus.setText(Data.getObsTotal() > 0 ? Data.getObsTotal() + " 行 × " + Data.getVarCount() + " 变量" : "尚未载入数据");
         this.exactOneClickDataDetail.setText(Data.getObsTotal() > 0 ? "当前 Stata 内存数据已连接。" : "选择一种方式开始，载入后这里会显示可滚动的只读数据表。");
         this.stageLayout.show(this.stageCards, "oneclick_exact");
         this.updateOneClickConditionalFields();
         this.updateOneClickPreview();
         this.statusLabel.setText("OneClick 页面已就绪：只显示当前回归方法真正需要的设置。");
      }'''
s = replace_method(s, '      private void showOneClickPage(String var1)', show_one)

# Sync exact command box at the end of current OneClick preview method without reimplementing command syntax.
a,b = method_span(s, '      private void updateOneClickPreview()')
body = s[a:b]
if 'exactOneClickCommand.setText' not in body:
    idx = body.rfind('this.flashCommandPreview();')
    if idx < 0:
        idx = body.rfind('}')
        body = body[:idx] + '         this.exactOneClickCommand.setText(this.previewArea.getText());\n' + body[idx:]
    else:
        end = idx + len('this.flashCommandPreview();')
        body = body[:end] + '\n         this.exactOneClickCommand.setText(this.previewArea.getText());' + body[end:]
    s = s[:a] + body + s[b:]

# showHome also keeps sidebar state
if 'private void showHomePage()' in s:
    a,b = method_span(s, '      private void showHomePage()')
    body=s[a:b]
    if 'this.setSidebarActive("home")' not in body:
        brace=body.find('{')+1
        body=body[:brace]+'\n         this.setSidebarActive("home");'+body[brace:]
        s=s[:a]+body+s[b:]

p.write_text(s, encoding='utf-8')
print('HX_PIXEL_MATCH_121_PATCH_OK')
