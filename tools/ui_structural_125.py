from pathlib import Path
import re

ROOT = Path('.')
JAVA = ROOT / 'src/main/java/com/hexie/stata/HxWorkbench.java'


def replace_method(src: str, signature: str, replacement: str) -> str:
    start = src.find(signature)
    if start < 0:
        raise RuntimeError(f'method not found: {signature}')
    brace = src.find('{', start)
    if brace < 0:
        raise RuntimeError(f'opening brace not found: {signature}')
    depth = 0
    i = brace
    in_str = False
    in_char = False
    esc = False
    line_comment = False
    block_comment = False
    while i < len(src):
        c = src[i]
        n = src[i+1] if i + 1 < len(src) else ''
        if line_comment:
            if c == '\n':
                line_comment = False
        elif block_comment:
            if c == '*' and n == '/':
                block_comment = False
                i += 1
        elif in_str:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                in_str = False
        elif in_char:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == "'":
                in_char = False
        else:
            if c == '/' and n == '/':
                line_comment = True
                i += 1
            elif c == '/' and n == '*':
                block_comment = True
                i += 1
            elif c == '"':
                in_str = True
            elif c == "'":
                in_char = True
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return src[:start] + replacement.rstrip() + src[i+1:]
        i += 1
    raise RuntimeError(f'closing brace not found: {signature}')


src = JAVA.read_text(encoding='utf-8')
src = src.replace('public static final String VERSION = "1.2.4";', 'public static final String VERSION = "1.2.5";')
src = src.replace('SFIToolkit.displayln("HxWorkbench 1.2.4");', 'SFIToolkit.displayln("HxWorkbench 1.2.5");')
src = src.replace('this.commandDataSplit.setResizeWeight(0.68);', 'this.commandDataSplit.setResizeWeight(1.0);')

# Stable fixed-width Current Data inspector on all ordinary work pages.
old_ratio = '''      void applyDividerRatios() {
         SwingUtilities.invokeLater(() -> {
            int var1 = (int)Math.round(this.commandDataSplit.getWidth() * 0.68);
            this.commandDataSplit.setDividerLocation(Math.max(540, var1));
            if (this.dataSummarySplit != null) {
               int var2 = (int)Math.round(this.dataSummarySplit.getHeight() * 0.70);
               this.dataSummarySplit.setDividerLocation(Math.max(170, var2));
            }
         });
      }'''
new_ratio = '''      void applyDividerRatios() {
         SwingUtilities.invokeLater(() -> {
            int total = this.commandDataSplit.getWidth();
            if (total > 0) {
               int inspector = Math.max(360, Math.min(410, total / 3));
               this.commandDataSplit.setDividerLocation(Math.max(560, total - inspector));
            }
            if (this.dataSummarySplit != null) {
               int var2 = (int)Math.round(this.dataSummarySplit.getHeight() * 0.70);
               this.dataSummarySplit.setDividerLocation(Math.max(170, var2));
            }
         });
      }'''
if old_ratio not in src:
    raise RuntimeError('applyDividerRatios block changed')
src = src.replace(old_ratio, new_ratio)

# Remove user-facing expand/collapse for ordinary command options. Advanced options remain visible in normal scroll flow.
src = src.replace('''         this.advancedContent.setVisible(false);
         styleSecondaryButton(this.advancedToggle);
         this.advancedToggle.setHorizontalAlignment(2);
         this.advancedToggle.addActionListener(var1x -> {
            boolean var2x = this.advancedToggle.isSelected();
            this.advancedToggle.setText(var2x ? "收起设置  −" : "更多设置  +");
            this.advancedContent.setVisible(var2x);
            this.formPanel.revalidate();
            this.formPanel.repaint();
         });''', '''         this.advancedContent.setVisible(true);
         this.advancedToggle.setVisible(false);''')

new_add_advanced = r'''      private void addAdvancedSettings(int var1, boolean var2, boolean var3, boolean var4) {
         this.rebuildGenericAdvancedContent(var2, var3, var4);
         this.advancedContent.setVisible(true);
         JPanel var5 = new JPanel();
         var5.setOpaque(false);
         var5.setLayout(new BoxLayout(var5, BoxLayout.Y_AXIS));
         JLabel title = sectionCaption("其他设置");
         title.setAlignmentX(0.0F);
         this.advancedContent.setAlignmentX(0.0F);
         var5.add(title);
         var5.add(Box.createVerticalStrut(7));
         var5.add(this.advancedContent);
         GridBagConstraints var6 = this.constraints(0, var1);
         var6.gridwidth = 2;
         var6.weightx = 1.0;
         var6.fill = GridBagConstraints.HORIZONTAL;
         this.formPanel.add(var5, var6);
      }'''
src = replace_method(src, '      private void addAdvancedSettings(int var1, boolean var2, boolean var3, boolean var4)', new_add_advanced)

# Official/third-party command pages should not show xtset-style panel/time fields unless they belong to the command itself.
src = src.replace('''         if (this.flag("needs_panel")) {
            this.addField(var4++, this.sem("panel_label"), this.panel);
            this.addField(var4++, this.sem("time_label"), this.time);
         }''', '''         if (this.flag("needs_panel") && !Arrays.asList(
            "reghdfe", "ppmlhdfe", "ivreghdfe", "xtreg", "xtlogit", "xtprobit", "xtpoisson"
         ).contains(this.currentCommand)) {
            this.addField(var4++, this.sem("panel_label"), this.panel);
            this.addField(var4++, this.sem("time_label"), this.time);
         }''')

# Remove unreliable Unicode pseudo-icons from common reusable buttons.
new_sidebar = r'''      private JButton sidebarButton(String key, String glyph, String label, Runnable action) {
         JButton button = new JButton("<html><b>" + html(label) + "</b></html>");
         button.putClientProperty("hx.sidebar.key", key);
         button.setHorizontalAlignment(SwingConstants.LEFT);
         button.setBorder(new EmptyBorder(11, 14, 11, 14));
         button.setMaximumSize(new Dimension(Integer.MAX_VALUE, 46));
         button.setAlignmentX(0.0F);
         button.setFocusPainted(false);
         button.setContentAreaFilled(false);
         button.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         this.sidebarButtons.put(key, button);
         button.addActionListener(e -> {
            this.setSidebarActive(key);
            action.run();
         });
         this.applySidebarStyle(button, key.equals(this.activeSidebarKey));
         return button;
      }'''
src = replace_method(src, '      private JButton sidebarButton(String key, String glyph, String label, Runnable action)', new_sidebar)

new_ref_quick = r'''      private JButton refQuick(String glyph, String title, Runnable action) {
         JButton b = new JButton("<html><div style='text-align:center'><b>" + html(title) + "</b></div></html>");
         b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 251, 255), new Color(239, 245, 253), TEXT, new Color(221, 228, 239)));
         b.setBorder(new EmptyBorder(8, 6, 8, 6));
         b.setFocusPainted(false);
         b.setContentAreaFilled(false);
         b.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         b.addActionListener(e -> action.run());
         return b;
      }'''
src = replace_method(src, '      private JButton refQuick(String glyph, String title, Runnable action)', new_ref_quick)

new_ref_task = r'''      private JButton refTask(String glyph, String title, String subtitle, Color accent, Runnable action) {
         JButton b = new JButton("<html><div style='text-align:left'><b>" + html(title) + "</b><br><span style='font-size:9px;color:#6b7890'>" + html(subtitle) + "</span></div></html>");
         b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(249, 251, 254), new Color(240, 245, 252), TEXT, new Color(221, 228, 239)));
         b.setBorder(new EmptyBorder(11, 14, 11, 14));
         b.setHorizontalAlignment(SwingConstants.LEFT);
         b.setFocusPainted(false);
         b.setContentAreaFilled(false);
         b.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         b.addActionListener(e -> action.run());
         return b;
      }'''
src = replace_method(src, '      private JButton refTask(String glyph, String title, String subtitle, Color accent, Runnable action)', new_ref_task)

new_linear_main = r'''      private JComponent exactLinearMainCard(String glyph, String command, String title, String desc, String example, Color accent) {
         JPanel card = new JPanel(new BorderLayout(12, 6));
         card.setBackground(SURFACE);
         card.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220,228,239),9),
            new EmptyBorder(14,16,14,16)
         ));
         JPanel text = new JPanel();
         text.setOpaque(false);
         text.setLayout(new BoxLayout(text, BoxLayout.Y_AXIS));
         JLabel cmd = new JLabel(command);
         cmd.setForeground(accent);
         cmd.setFont(new Font("Monospaced", Font.BOLD, 12));
         JLabel name = new JLabel(title);
         name.setForeground(TEXT);
         name.setFont(name.getFont().deriveFont(Font.BOLD, 13.0F));
         text.add(cmd);
         text.add(Box.createVerticalStrut(4));
         text.add(name);
         card.add(text, BorderLayout.CENTER);
         JButton enter = this.refButton("进入设置", true);
         enter.addActionListener(e -> this.openCommandPage(command));
         card.add(enter, BorderLayout.EAST);
         card.setPreferredSize(new Dimension(500, 82));
         return card;
      }'''
src = replace_method(src, '      private JComponent exactLinearMainCard(String glyph, String command, String title, String desc, String example, Color accent)', new_linear_main)

new_linear_group = r'''      private JComponent exactLinearGroup(String glyph, String title, String[][] entries, Color accent) {
         JPanel card = new JPanel(new BorderLayout(0, 8));
         card.setBackground(SURFACE);
         card.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(225,231,240),8),
            new EmptyBorder(12,12,12,12)
         ));
         JLabel h = new JLabel(title);
         h.setForeground(TEXT);
         h.setFont(h.getFont().deriveFont(Font.BOLD, 11.0F));
         card.add(h, BorderLayout.NORTH);
         JPanel list = new JPanel();
         list.setOpaque(false);
         list.setLayout(new BoxLayout(list, BoxLayout.Y_AXIS));
         for (String[] e : entries) {
            JButton b = new JButton("<html><b>" + html(e[0]) + "</b>&nbsp;&nbsp;<span style='color:#6e7b91'>" + html(e[1]) + "</span></html>");
            b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE,new Color(249,251,254),new Color(242,246,251),TEXT,SURFACE));
            b.setBorder(new EmptyBorder(4,4,4,4));
            b.setHorizontalAlignment(SwingConstants.LEFT);
            b.setFocusPainted(false);
            b.setContentAreaFilled(false);
            b.setMaximumSize(new Dimension(Integer.MAX_VALUE, 30));
            String cmd = e[0];
            b.addActionListener(ev -> this.openCommandPage(cmd));
            list.add(b);
         }
         card.add(list, BorderLayout.CENTER);
         return card;
      }'''
src = replace_method(src, '      private JComponent exactLinearGroup(String glyph, String title, String[][] entries, Color accent)', new_linear_group)

# Responsive home page: no absolute full-page width and no clipping on the right edge.
new_home = r'''      private JComponent buildHomeContainer() {
         JPanel root = new JPanel(new BorderLayout(0, 14));
         root.setBackground(APP_BG);
         root.setBorder(new EmptyBorder(20, 24, 16, 24));

         JPanel header = new JPanel(new BorderLayout());
         header.setOpaque(false);
         JPanel heading = new JPanel();
         heading.setOpaque(false);
         heading.setLayout(new BoxLayout(heading, BoxLayout.Y_AXIS));
         JLabel title = new JLabel("实证工作台");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD, 27.0F));
         JLabel sub = new JLabel("选择任务或直接搜索 Stata 命令");
         sub.setForeground(MUTED);
         sub.setFont(sub.getFont().deriveFont(10.5F));
         heading.add(title);
         heading.add(Box.createVerticalStrut(3));
         heading.add(sub);
         header.add(heading, BorderLayout.WEST);
         JPanel topActions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 0));
         topActions.setOpaque(false);
         JButton openStata = this.refButton("打开 Stata", false);
         openStata.addActionListener(e -> this.setState(JFrame.ICONIFIED));
         JButton help = this.refButton("帮助", false);
         help.addActionListener(e -> this.openHelp());
         topActions.add(openStata);
         topActions.add(help);
         header.add(topActions, BorderLayout.EAST);
         root.add(header, BorderLayout.NORTH);

         JPanel body = new JPanel();
         body.setOpaque(false);
         body.setLayout(new BoxLayout(body, BoxLayout.Y_AXIS));

         JPanel topRow = new JPanel(new GridBagLayout());
         topRow.setOpaque(false);
         topRow.setAlignmentX(0.0F);
         topRow.setMaximumSize(new Dimension(Integer.MAX_VALUE, 235));
         GridBagConstraints gc = new GridBagConstraints();
         gc.gridy = 0;
         gc.fill = GridBagConstraints.BOTH;
         gc.weighty = 1.0;

         JPanel hero = this.refCard();
         hero.setLayout(new GridLayout(1, 2, 18, 0));
         hero.setBackground(new Color(246,250,255));
         JPanel search = new JPanel();
         search.setOpaque(false);
         search.setLayout(new BoxLayout(search, BoxLayout.Y_AXIS));
         JLabel start = new JLabel("开始分析");
         start.setForeground(TEXT);
         start.setFont(start.getFont().deriveFont(Font.BOLD, 20.0F));
         search.add(start);
         search.add(Box.createVerticalStrut(12));
         JPanel searchLine = new JPanel(new BorderLayout(8,0));
         searchLine.setOpaque(false);
         styleTextField(this.searchField);
         this.searchField.setToolTipText("搜索任务或命令");
         JButton startBtn = this.refButton("开始", true);
         startBtn.addActionListener(e -> this.smartHomeSearch());
         this.searchField.addActionListener(e -> this.smartHomeSearch());
         searchLine.add(this.searchField, BorderLayout.CENTER);
         searchLine.add(startBtn, BorderLayout.EAST);
         search.add(searchLine);
         hero.add(search);

         JPanel quick = new JPanel(new BorderLayout(0,10));
         quick.setOpaque(false);
         JLabel quickTitle = new JLabel("快速开始");
         quickTitle.setForeground(TEXT);
         quickTitle.setFont(quickTitle.getFont().deriveFont(Font.BOLD, 13.0F));
         quick.add(quickTitle, BorderLayout.NORTH);
         JPanel quickGrid = new JPanel(new GridLayout(1,5,8,0));
         quickGrid.setOpaque(false);
         quickGrid.add(this.refQuick("", "基准回归", this::openBaselineRegressionWorkspace));
         quickGrid.add(this.refQuick("", "固定效应", () -> this.browseMethod("reg", "固定效应线性回归")));
         quickGrid.add(this.refQuick("", "双重差分", () -> this.browseMethod("reg", "双重差分")));
         quickGrid.add(this.refQuick("", "描述统计", () -> this.browseMethod("stats", "描述统计")));
         quickGrid.add(this.refQuick("", "OneClick", () -> this.browseMethodCategory("oneclick")));
         quick.add(quickGrid, BorderLayout.CENTER);
         hero.add(quick);

         gc.gridx = 0;
         gc.weightx = 0.72;
         gc.insets = new Insets(0,0,0,12);
         topRow.add(hero, gc);

         JPanel data = this.refCard();
         data.setLayout(new BorderLayout(0, 10));
         JLabel dataTitle = new JLabel("当前数据");
         dataTitle.setForeground(TEXT);
         dataTitle.setFont(dataTitle.getFont().deriveFont(Font.BOLD, 14.0F));
         data.add(dataTitle, BorderLayout.NORTH);
         JPanel dataCenter = new JPanel();
         dataCenter.setOpaque(false);
         dataCenter.setLayout(new BoxLayout(dataCenter, BoxLayout.Y_AXIS));
         this.homeDatasetStatus.setHorizontalAlignment(SwingConstants.CENTER);
         this.homeDatasetStatus.setForeground(TEXT);
         this.homeDatasetStatus.setFont(this.homeDatasetStatus.getFont().deriveFont(Font.BOLD, 14.0F));
         this.homeDatasetStatus.setAlignmentX(0.5F);
         this.homeDatasetDetail.setHorizontalAlignment(SwingConstants.CENTER);
         this.homeDatasetDetail.setForeground(MUTED);
         this.homeDatasetDetail.setFont(this.homeDatasetDetail.getFont().deriveFont(9.5F));
         this.homeDatasetDetail.setAlignmentX(0.5F);
         dataCenter.add(Box.createVerticalGlue());
         dataCenter.add(this.homeDatasetStatus);
         dataCenter.add(Box.createVerticalStrut(5));
         dataCenter.add(this.homeDatasetDetail);
         dataCenter.add(Box.createVerticalGlue());
         data.add(dataCenter, BorderLayout.CENTER);
         JPanel dataButtons = new JPanel(new GridLayout(1,3,7,0));
         dataButtons.setOpaque(false);
         JButton dta = this.refButton("打开 DTA", true);
         dta.addActionListener(e -> this.chooseAndLoadDta());
         JButton excel = this.refButton("导入 Excel/CSV", false);
         excel.addActionListener(e -> this.navigateTo("data", "导入与转换", "hxconvert"));
         JButton auto = this.refButton("auto 示例", false);
         auto.addActionListener(e -> this.runUtility("sysuse auto, clear", true));
         dataButtons.add(dta); dataButtons.add(excel); dataButtons.add(auto);
         data.add(dataButtons, BorderLayout.SOUTH);
         gc.gridx = 1;
         gc.weightx = 0.28;
         gc.insets = new Insets(0,0,0,0);
         topRow.add(data, gc);
         body.add(topRow);
         body.add(Box.createVerticalStrut(14));

         JPanel middleRow = new JPanel(new GridBagLayout());
         middleRow.setOpaque(false);
         middleRow.setAlignmentX(0.0F);
         middleRow.setMaximumSize(new Dimension(Integer.MAX_VALUE, 305));
         GridBagConstraints gm = new GridBagConstraints();
         gm.gridy = 0; gm.fill = GridBagConstraints.BOTH; gm.weighty = 1.0;
         JPanel common = this.refCard();
         common.setLayout(new BorderLayout(0,10));
         JLabel commonTitle = new JLabel("常用任务");
         commonTitle.setForeground(TEXT);
         commonTitle.setFont(commonTitle.getFont().deriveFont(Font.BOLD, 14.0F));
         common.add(commonTitle, BorderLayout.NORTH);
         JPanel taskGrid = new JPanel(new GridLayout(2,3,12,12));
         taskGrid.setOpaque(false);
         taskGrid.add(this.refTask("", "导入数据", "Excel / CSV / DTA", new Color(33,176,93), () -> this.navigateTo("data", "导入与转换", "hxconvert")));
         taskGrid.add(this.refTask("", "描述统计", "summarize / tabstat", new Color(57,125,242), () -> this.browseMethod("stats", "描述统计")));
         taskGrid.add(this.refTask("", "基准回归", "xtreg / reghdfe / regress", new Color(142,91,230), this::openBaselineRegressionWorkspace));
         taskGrid.add(this.refTask("", "固定效应", "areg / reghdfe / xtreg", new Color(245,138,45), () -> this.browseMethod("reg", "固定效应线性回归")));
         taskGrid.add(this.refTask("", "双重差分", "didregress / xtdidregress", new Color(31,180,151), () -> this.browseMethod("reg", "双重差分")));
         taskGrid.add(this.refTask("", "OneClick", "控制变量组合", new Color(57,120,244), () -> this.browseMethodCategory("oneclick")));
         common.add(taskGrid, BorderLayout.CENTER);
         gm.gridx = 0; gm.weightx = 0.72; gm.insets = new Insets(0,0,0,12);
         middleRow.add(common, gm);

         JPanel recent = this.refCard();
         recent.setLayout(new BorderLayout(0,8));
         JLabel recentTitle = new JLabel("最近任务");
         recentTitle.setForeground(TEXT);
         recentTitle.setFont(recentTitle.getFont().deriveFont(Font.BOLD,14.0F));
         recent.add(recentTitle, BorderLayout.NORTH);
         this.homeRecentPanel.setOpaque(false);
         this.homeRecentPanel.setLayout(new BoxLayout(this.homeRecentPanel, BoxLayout.Y_AXIS));
         recent.add(this.homeRecentPanel, BorderLayout.CENTER);
         JButton resume = this.refButton("继续上次工作", false);
         resume.addActionListener(e -> { List<WorkSnapshot> snaps=this.loadRecentSnapshots(); if(!snaps.isEmpty()) this.restoreWorkSnapshot(snaps.get(0)); });
         recent.add(resume, BorderLayout.SOUTH);
         gm.gridx = 1; gm.weightx = 0.28; gm.insets = new Insets(0,0,0,0);
         middleRow.add(recent, gm);
         body.add(middleRow);
         body.add(Box.createVerticalStrut(14));

         JPanel more = this.refCard();
         more.setLayout(new BorderLayout(0,10));
         more.setAlignmentX(0.0F);
         more.setMaximumSize(new Dimension(Integer.MAX_VALUE, 250));
         JLabel moreTitle = new JLabel("更多功能");
         moreTitle.setForeground(TEXT);
         moreTitle.setFont(moreTitle.getFont().deriveFont(Font.BOLD,14.0F));
         more.add(moreTitle, BorderLayout.NORTH);
         JPanel moreGrid = new JPanel(new GridLayout(3,3,10,10));
         moreGrid.setOpaque(false);
         moreGrid.add(this.refTask("", "导入与转换", "Excel / CSV / DTA", new Color(87,140,245), () -> this.navigateTo("data", "导入与转换", "hxconvert")));
         moreGrid.add(this.refTask("", "数据检查", "缺失 / 重复 / 唯一键", new Color(37,180,144), () -> this.browseMethod("data", "数据检查")));
         moreGrid.add(this.refTask("", "变量处理", "generate / replace", new Color(229,170,52), () -> this.browseMethod("data", "变量处理")));
         moreGrid.add(this.refTask("", "样本处理", "keep / drop", new Color(159,91,225), () -> this.browseMethod("data", "样本处理")));
         moreGrid.add(this.refTask("", "合并与追加", "merge / append", new Color(87,140,245), () -> this.browseMethod("data", "合并与追加")));
         moreGrid.add(this.refTask("", "数据结构", "reshape / xtset / tsset", new Color(37,180,144), () -> this.browseMethod("data", "数据结构")));
         moreGrid.add(this.refTask("", "相关分析", "correlate / pwcorr", new Color(57,125,242), () -> this.browseMethod("stats", "相关分析")));
         moreGrid.add(this.refTask("", "均值检验", "ttest", new Color(245,138,45), () -> this.browseMethod("stats", "均值检验")));
         moreGrid.add(this.refTask("", "频数列联", "tabulate", new Color(142,91,230), () -> this.browseMethod("stats", "频数列联")));
         more.add(moreGrid, BorderLayout.CENTER);
         body.add(more);

         JScrollPane scroll = softScroll(body);
         scroll.setBorder(null);
         scroll.getVerticalScrollBar().setUnitIncrement(18);
         root.add(scroll, BorderLayout.CENTER);
         return root;
      }'''
src = replace_method(src, '      private JComponent buildHomeContainer()', new_home)

# Directory page: no right recommendation column, no expand-more control, no overflow-prone fixed 1450px shell.
new_linear = r'''      private JComponent buildExactLinearContainer() {
         JPanel root = new JPanel(new BorderLayout(0, 12));
         root.setBackground(APP_BG);
         root.setBorder(new EmptyBorder(18, 24, 16, 24));

         JPanel header = new JPanel(new BorderLayout());
         header.setOpaque(false);
         JPanel heading = new JPanel();
         heading.setOpaque(false);
         heading.setLayout(new BoxLayout(heading, BoxLayout.Y_AXIS));
         JLabel crumb = new JLabel("首页 / 回归 / 线性模型");
         crumb.setForeground(new Color(84,107,144));
         crumb.setFont(crumb.getFont().deriveFont(10.5F));
         JLabel title = new JLabel("线性模型");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD,27.0F));
         heading.add(crumb);
         heading.add(Box.createVerticalStrut(5));
         heading.add(title);
         header.add(heading, BorderLayout.WEST);
         JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT,7,0));
         actions.setOpaque(false);
         JButton back=this.refButton("← 上一级",false); back.addActionListener(e->this.showHomePage());
         JButton home=this.refButton("首页",false); home.addActionListener(e->this.showHomePage());
         JButton help=this.refButton("帮助",false); help.addActionListener(e->this.openHelp());
         actions.add(back); actions.add(home); actions.add(help);
         header.add(actions, BorderLayout.EAST);
         root.add(header, BorderLayout.NORTH);

         JPanel body = new JPanel();
         body.setOpaque(false);
         body.setLayout(new BoxLayout(body, BoxLayout.Y_AXIS));

         JPanel search = this.refCard();
         search.setLayout(new BorderLayout(8,0));
         search.setAlignmentX(0.0F);
         JTextField find = new JTextField();
         styleTextField(find);
         find.setToolTipText("搜索命令");
         JButton searchButton = this.refButton("搜索", true);
         ActionListener doSearch = e -> {
            String q = find.getText().trim();
            if (!q.isBlank()) {
               this.searchField.setText(q);
               this.smartHomeSearch();
            }
         };
         find.addActionListener(doSearch);
         searchButton.addActionListener(doSearch);
         search.add(find, BorderLayout.CENTER);
         search.add(searchButton, BorderLayout.EAST);
         search.setMaximumSize(new Dimension(Integer.MAX_VALUE, 62));
         body.add(search);
         body.add(Box.createVerticalStrut(12));

         JPanel commonCard=this.refCard();
         commonCard.setLayout(new BorderLayout(0,10));
         commonCard.setAlignmentX(0.0F);
         JLabel ct=new JLabel("常用命令"); ct.setForeground(TEXT); ct.setFont(ct.getFont().deriveFont(Font.BOLD,14.0F));
         commonCard.add(ct, BorderLayout.NORTH);
         JPanel commonGrid = new JPanel(new GridLayout(2,2,12,12));
         commonGrid.setOpaque(false);
         commonGrid.add(this.exactLinearMainCard("","regress","普通线性回归","","",new Color(54,114,236)));
         commonGrid.add(this.exactLinearMainCard("","areg","单组固定效应","","",new Color(29,164,101)));
         commonGrid.add(this.exactLinearMainCard("","reghdfe","高维固定效应回归","","",new Color(245,125,30)));
         commonGrid.add(this.exactLinearMainCard("","qreg","分位数回归","","",new Color(134,84,225)));
         commonCard.add(commonGrid, BorderLayout.CENTER);
         commonCard.setMaximumSize(new Dimension(Integer.MAX_VALUE, 230));
         body.add(commonCard);
         body.add(Box.createVerticalStrut(12));

         JPanel more=this.refCard();
         more.setLayout(new BorderLayout(0,10));
         more.setAlignmentX(0.0F);
         JLabel mt=new JLabel("更多线性模型"); mt.setForeground(TEXT); mt.setFont(mt.getFont().deriveFont(Font.BOLD,14.0F));
         more.add(mt, BorderLayout.NORTH);
         JPanel groups = new JPanel(new GridLayout(2,2,12,12));
         groups.setOpaque(false);
         groups.add(this.exactLinearGroup("","稳健与异常值处理",new String[][]{{"rreg","稳健回归"},{"cnsreg","约束线性回归"},{"newey","Newey-West"}},new Color(47,104,213)));
         groups.add(this.exactLinearGroup("","加权与广义最小二乘",new String[][]{{"regressw","加权最小二乘"},{"vwls","可变权重"},{"gls","广义最小二乘"},{"prais","Prais-Winsten"}},new Color(37,172,92)));
         groups.add(this.exactLinearGroup("","工具变量与内生性",new String[][]{{"ivregress","工具变量"},{"ivreg","2SLS"},{"ivprobit","IV Probit"},{"control","控制函数"}},new Color(245,128,30)));
         groups.add(this.exactLinearGroup("","其他线性扩展",new String[][]{{"sureg","SUR"},{"seemingly","SUR"},{"seemingly2","SUR 扩展"},{"ml","最大似然"}},new Color(132,85,220)));
         more.add(groups, BorderLayout.CENTER);
         body.add(more);

         JScrollPane scroll = softScroll(body);
         scroll.setBorder(null);
         scroll.getVerticalScrollBar().setUnitIncrement(18);
         root.add(scroll, BorderLayout.CENTER);
         return root;
      }'''
src = replace_method(src, '      private JComponent buildExactLinearContainer()', new_linear)

# OneClick work page: fixed shared inspector, compact method selector, no separate pseudo-tab strip.
new_oneclick = r'''      private JComponent buildExactOneClickContainer() {
         JPanel root = new JPanel(new BorderLayout(14,0));
         root.setBackground(APP_BG);
         root.setBorder(new EmptyBorder(16,20,16,18));
         this.exactOneClickRoot = root;

         JPanel left = new JPanel(new BorderLayout(0,12));
         left.setOpaque(false);
         JPanel header = new JPanel(new BorderLayout());
         header.setOpaque(false);
         JPanel heading = new JPanel();
         heading.setOpaque(false);
         heading.setLayout(new BoxLayout(heading, BoxLayout.Y_AXIS));
         JLabel crumb = new JLabel("首页 / OneClick / oneclick");
         crumb.setForeground(new Color(91,111,144));
         crumb.setFont(crumb.getFont().deriveFont(10.5F));
         JLabel title = new JLabel("OneClick");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD,22.0F));
         heading.add(crumb);
         heading.add(Box.createVerticalStrut(5));
         heading.add(title);
         header.add(heading, BorderLayout.WEST);
         JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT,7,0));
         actions.setOpaque(false);
         JButton back = this.refButton("← 上一级", false); back.addActionListener(e -> this.browseMethodCategory("oneclick"));
         JButton home = this.refButton("首页", false); home.addActionListener(e -> this.showHomePage());
         JButton help = this.refButton("帮助", false); help.addActionListener(e -> this.openHelp());
         actions.add(back); actions.add(home); actions.add(help);
         header.add(actions, BorderLayout.EAST);
         left.add(header, BorderLayout.NORTH);

         JPanel form = new JPanel();
         form.setOpaque(false);
         form.setLayout(new BoxLayout(form, BoxLayout.Y_AXIS));
         JPanel settings = this.refCard();
         settings.setLayout(new BoxLayout(settings, BoxLayout.Y_AXIS));
         JLabel st = new JLabel("参数设置");
         st.setForeground(TEXT);
         st.setFont(st.getFont().deriveFont(Font.BOLD,13.0F));
         st.setAlignmentX(0.0F);
         settings.add(st);
         settings.add(Box.createVerticalStrut(10));

         styleCombo(this.oneClickY); styleCombo(this.oneClickX); styleCombo(this.oneClickP); styleCombo(this.oneClickEstimator);
         styleTextField(this.exactOneClickModelOptions); styleTextField(this.exactOneClickOtherOptions);
         styleTextField(this.exactOneClickCandidatesDisplay); styleTextField(this.exactOneClickRequiredDisplay);
         this.exactOneClickCandidatesDisplay.setEditable(false); this.exactOneClickRequiredDisplay.setEditable(false);

         JPanel yx = new JPanel(new GridLayout(1,4,10,0)); yx.setOpaque(false);
         yx.add(new JLabel("Y")); yx.add(this.oneClickY); yx.add(new JLabel("X")); yx.add(this.oneClickX);
         yx.setMaximumSize(new Dimension(Integer.MAX_VALUE,34)); settings.add(yx); settings.add(Box.createVerticalStrut(10));

         JPanel candidates = new JPanel(new BorderLayout(10,0)); candidates.setOpaque(false);
         JLabel lc = new JLabel("Candidates"); lc.setPreferredSize(new Dimension(110,28)); candidates.add(lc,BorderLayout.WEST);
         candidates.add(this.exactOneClickCandidatesDisplay,BorderLayout.CENTER);
         JButton cp=this.refButton("选择",false); cp.addActionListener(e->this.chooseExactOneClickValues(this.oneClickCandidates,this.exactOneClickCandidatesDisplay,"选择候选控制变量")); candidates.add(cp,BorderLayout.EAST);
         candidates.setMaximumSize(new Dimension(Integer.MAX_VALUE,34)); settings.add(candidates); settings.add(Box.createVerticalStrut(10));

         JPanel required = new JPanel(new BorderLayout(10,0)); required.setOpaque(false);
         JLabel lr = new JLabel("fix()" ); lr.setPreferredSize(new Dimension(110,28)); required.add(lr,BorderLayout.WEST);
         required.add(this.exactOneClickRequiredDisplay,BorderLayout.CENTER);
         JButton rp=this.refButton("选择",false); rp.addActionListener(e->this.chooseExactOneClickValues(this.oneClickRequired,this.exactOneClickRequiredDisplay,"选择固定变量")); required.add(rp,BorderLayout.EAST);
         required.setMaximumSize(new Dimension(Integer.MAX_VALUE,34)); settings.add(required); settings.add(Box.createVerticalStrut(10));

         JPanel pm = new JPanel(new GridLayout(1,4,10,0)); pm.setOpaque(false);
         pm.add(new JLabel("p()")); pm.add(this.oneClickP); pm.add(new JLabel("method")); pm.add(this.oneClickEstimator);
         pm.setMaximumSize(new Dimension(Integer.MAX_VALUE,34)); settings.add(pm); settings.add(Box.createVerticalStrut(10));

         JPanel opts = new JPanel(new GridLayout(1,4,10,0)); opts.setOpaque(false);
         opts.add(new JLabel("o()")); opts.add(this.exactOneClickModelOptions); opts.add(new JLabel("z")); opts.add(this.exactOneClickOtherOptions);
         opts.setMaximumSize(new Dimension(Integer.MAX_VALUE,34)); settings.add(opts);
         settings.setAlignmentX(0.0F);
         settings.setMaximumSize(new Dimension(Integer.MAX_VALUE, 250));
         form.add(settings);
         form.add(Box.createVerticalStrut(12));

         JPanel command = this.refCard();
         command.setLayout(new BorderLayout(10,8));
         JLabel ctitle=new JLabel("Stata 命令"); ctitle.setForeground(TEXT); ctitle.setFont(ctitle.getFont().deriveFont(Font.BOLD,12.0F)); command.add(ctitle,BorderLayout.NORTH);
         this.exactOneClickCommand.setEditable(false); this.exactOneClickCommand.setLineWrap(true); this.exactOneClickCommand.setWrapStyleWord(true);
         this.exactOneClickCommand.setBackground(new Color(244,248,255)); this.exactOneClickCommand.setForeground(TEXT); this.exactOneClickCommand.setFont(new Font("Monospaced",Font.PLAIN,11)); this.exactOneClickCommand.setBorder(new EmptyBorder(9,10,9,10));
         JScrollPane cs=softScroll(this.exactOneClickCommand); cs.setPreferredSize(new Dimension(100,70)); command.add(cs,BorderLayout.CENTER);
         JPanel ca = new JPanel(new FlowLayout(FlowLayout.RIGHT,7,0)); ca.setOpaque(false);
         JButton copy=this.refButton("复制命令",false); copy.addActionListener(e->{ Toolkit.getDefaultToolkit().getSystemClipboard().setContents(new StringSelection(this.exactOneClickCommand.getText()),null); });
         JButton run=this.refButton("运行 OneClick",true); run.addActionListener(e->this.runOneClick()); ca.add(copy); ca.add(run); command.add(ca,BorderLayout.SOUTH);
         command.setAlignmentX(0.0F); command.setMaximumSize(new Dimension(Integer.MAX_VALUE,145)); form.add(command);

         HxWorkbench.SimpleDocumentListener exactListener = () -> this.updateOneClickPreview();
         this.exactOneClickModelOptions.getDocument().addDocumentListener(exactListener);
         this.exactOneClickOtherOptions.getDocument().addDocumentListener(exactListener);

         JScrollPane formScroll = softScroll(form); formScroll.setBorder(null); formScroll.getVerticalScrollBar().setUnitIncrement(18);
         left.add(formScroll, BorderLayout.CENTER);
         root.add(left, BorderLayout.CENTER);

         this.exactOneClickInspectorHost.removeAll();
         this.exactOneClickInspectorHost.setOpaque(false);
         this.exactOneClickInspectorHost.setPreferredSize(new Dimension(410,0));
         root.add(this.exactOneClickInspectorHost, BorderLayout.EAST);
         return root;
      }'''
src = replace_method(src, '      private JComponent buildExactOneClickContainer()', new_oneclick)

JAVA.write_text(src, encoding='utf-8')

# Version and help metadata.
ado = ROOT / 'hxempirical.ado'
a = ado.read_text(encoding='utf-8').replace('*! hxempirical 1.2.4', '*! hxempirical 1.2.5')
ado.write_text(a, encoding='utf-8')

pkg = ROOT / 'hxempirical.pkg'
p = pkg.read_text(encoding='utf-8').replace('d Version 1.2.4', 'd Version 1.2.5').replace('d Distribution-Date: 20260812', 'd Distribution-Date: 20260813')
pkg.write_text(p, encoding='utf-8')

helpf = ROOT / 'hxempirical.sthlp'
h = helpf.read_text(encoding='utf-8').replace('version 1.2.4', 'version 1.2.5').replace('The 1.2.4 interface', 'The 1.2.5 interface')
h = h.replace('The right inspector can be hidden so the settings workspace can use the full width.', 'The right inspector keeps a stable width on work pages.')
h = h.replace('The command-settings page ends with a fixed command dock.', 'The command-settings page ends with a fixed command dock; low-frequency options remain in the normal scroll flow instead of an expand/collapse section.')
helpf.write_text(h, encoding='utf-8')

toolhelp = ROOT / 'hxtoolbox.sthlp'
th = toolhelp.read_text(encoding='utf-8')
th = th.replace('较少使用的参数收在“更多设置”中。', '较少使用的参数按顺序放在主页面下方，不使用展开/收起改变页面高度。')
toolhelp.write_text(th, encoding='utf-8')

readme = ROOT / 'README.md'
r = readme.read_text(encoding='utf-8')
r = r.replace('**当前发布版本：1.2.4**', '**当前发布版本：1.2.5**')
r = re.sub(r'\*\*上次修改时间：[^\n]+\*\*', '**上次修改时间：2026-08-13 09:15（UTC+8）**', r, count=1)
r = r.replace('常用参数放前面，低频参数放到“更多设置”中。', '常用参数放前面，低频参数直接顺序排列在后面，不通过展开/收起改变页面结构。')
record = '''### 2026-08-13 09:15（UTC+8）\n\n**修改时间**：2026-08-13 09:15（UTC+8）\n\n**修改内容**：\n\n- 统一页面结构：目录页只保留左侧导航与主内容；工作页统一使用固定宽度的“当前数据 / 结果 / 日志”右栏。\n- 首页改为自适应布局，取消依赖固定绝对坐标的整页宽度，避免窗口尺寸和 DPI 变化时右侧内容被裁切。\n- 线性模型目录删除“推荐路径”和“展开更多命令类别”，常用与其他命令直接在正常滚动页面中展示。\n- 普通命令页取消“更多设置 / 收起设置”展开结构，低频参数直接放在常用参数之后。\n- `reghdfe`、`ppmlhdfe`、`ivreghdfe` 及常见 `xt*` 估计页面不再显示额外的面板变量 / 时间变量字段；面板结构由 `xtset` / `tsset` 单独声明。\n- OneClick 改为自适应工作页，模型方法使用紧凑下拉框；右侧继续复用统一“当前数据”组件。\n- 清理首页、侧栏和线性模型页依赖字体支持的 Unicode 伪图标，避免 Windows 字体环境出现方框乱码。\n\n'''
if '## 修改记录' in r:
    r = r.replace('## 修改记录\n\n', '## 修改记录\n\n' + record, 1)
else:
    r += '\n\n## 修改记录\n\n' + record
readme.write_text(r, encoding='utf-8')

print('UI_STRUCTURAL_125_PATCH_OK')
