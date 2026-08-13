from pathlib import Path

root = Path('.')
java = root / 'src/main/java/com/hexie/stata/HxWorkbench.java'
s = java.read_text(encoding='utf-8')

# Version bump.
s = s.replace('public static final String VERSION = "1.2.9";', 'public static final String VERSION = "1.3.0";')
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.2.9");', 'SFIToolkit.displayln("HxWorkbench 1.3.0");')

# ---- Home page v1.3.0 ----
legacy_sig = '      private JComponent buildHomeContainer() {'
if 'private JComponent buildHomeContainerV130Marker()' not in s:
    if legacy_sig not in s:
        raise SystemExit('buildHomeContainer signature not found')
    s = s.replace(legacy_sig, '      private JComponent buildHomeContainerLegacy() {', 1)

    home_block = r'''
      private JComponent buildHomeContainerV130Marker() {
         return null;
      }

      private JPanel homeCardV130() {
         JPanel card = cardPanel();
         card.setBackground(SURFACE);
         card.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(219, 226, 237), 12),
            new EmptyBorder(14, 16, 14, 16)
         ));
         return card;
      }

      private JButton homeQuickTileV130(String title, String detail, String glyph, Runnable action) {
         JButton b = new JButton(
            "<html><div style='text-align:center'><span style='font-size:22px;color:#2f6fe4'>" + html(glyph) + "</span><br>"
               + "<b>" + html(title) + "</b><br><span style='font-size:9px;color:#718096'>" + html(detail) + "</span></div></html>"
         );
         b.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(247, 250, 255), new Color(240, 246, 255), TEXT, SURFACE));
         b.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220, 227, 238), 10));
         b.setFocusPainted(false);
         b.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         b.setPreferredSize(new Dimension(122, 104));
         b.addActionListener(e -> action.run());
         return b;
      }

      private JButton homeListRowV130(String title, String detail, String glyph, Runnable action) {
         JButton row = new JButton(
            "<html><table width='360' cellpadding='0' cellspacing='0'><tr>"
               + "<td width='42'><span style='font-size:17px;color:#2f6fe4'>" + html(glyph) + "</span></td>"
               + "<td><b>" + html(title) + "</b><br><span style='font-size:9px;color:#718096'>" + html(detail) + "</span></td>"
               + "<td width='18' align='right'><span style='color:#607089'>›</span></td>"
               + "</tr></table></html>"
         );
         row.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 251, 255), new Color(241, 246, 253), TEXT, SURFACE));
         row.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createMatteBorder(1, 0, 0, 0, new Color(234, 238, 244)),
            new EmptyBorder(5, 8, 5, 8)
         ));
         row.setHorizontalAlignment(SwingConstants.LEFT);
         row.setFocusPainted(false);
         row.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         row.setMaximumSize(new Dimension(Integer.MAX_VALUE, 54));
         row.setPreferredSize(new Dimension(360, 54));
         row.addActionListener(e -> action.run());
         return row;
      }

      private JPanel homeListSectionV130(String title, Object[][] rows) {
         JPanel card = this.homeCardV130();
         card.setLayout(new BorderLayout(0, 10));
         JLabel head = new JLabel(title);
         head.setForeground(TEXT);
         head.setFont(head.getFont().deriveFont(Font.BOLD, 14.0F));
         card.add(head, BorderLayout.NORTH);
         JPanel list = new JPanel();
         list.setBackground(SURFACE);
         list.setLayout(new BoxLayout(list, BoxLayout.Y_AXIS));
         boolean first = true;
         for (Object[] spec : rows) {
            JButton row = this.homeListRowV130((String)spec[0], (String)spec[1], (String)spec[2], (Runnable)spec[3]);
            if (first) {
               row.setBorder(new EmptyBorder(5, 8, 5, 8));
               first = false;
            }
            list.add(row);
         }
         card.add(list, BorderLayout.CENTER);
         return card;
      }

      private JComponent buildHomeContainer() {
         JPanel root = new JPanel(new BorderLayout());
         root.setBackground(APP_BG);

         JPanel body = new JPanel();
         body.setBackground(APP_BG);
         body.setLayout(new BoxLayout(body, BoxLayout.Y_AXIS));
         body.setBorder(new EmptyBorder(20, 24, 16, 24));

         JPanel header = new JPanel(new BorderLayout());
         header.setOpaque(false);
         JPanel heading = new JPanel();
         heading.setOpaque(false);
         heading.setLayout(new BoxLayout(heading, BoxLayout.Y_AXIS));
         JLabel title = new JLabel("实证工作台");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD, 28.0F));
         JLabel sub = new JLabel("选择任务或直接搜索 Stata 命令");
         sub.setForeground(MUTED);
         sub.setFont(sub.getFont().deriveFont(10.5F));
         heading.add(title);
         heading.add(Box.createVerticalStrut(4));
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
         header.setMaximumSize(new Dimension(Integer.MAX_VALUE, 66));
         body.add(header);
         body.add(Box.createVerticalStrut(14));

         JPanel searchWrap = this.homeCardV130();
         searchWrap.setLayout(new BorderLayout(10, 0));
         searchWrap.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(213, 222, 236), 11),
            new EmptyBorder(6, 12, 6, 12)
         ));
         JLabel searchIcon = new JLabel("⌕");
         searchIcon.setForeground(new Color(72, 92, 125));
         searchIcon.setFont(searchIcon.getFont().deriveFont(Font.BOLD, 18.0F));
         searchWrap.add(searchIcon, BorderLayout.WEST);
         this.searchField.setText("");
         this.searchField.setToolTipText("搜索功能或直接输入 Stata 命令，例如 reg y x1 x2");
         this.searchField.setBorder(null);
         this.searchField.setBackground(SURFACE);
         this.searchField.setFont(this.searchField.getFont().deriveFont(12.0F));
         this.searchField.addActionListener(e -> this.smartHomeSearch());
         searchWrap.add(this.searchField, BorderLayout.CENTER);
         JLabel shortcut = new JLabel("Ctrl + K");
         shortcut.setForeground(MUTED);
         shortcut.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220, 227, 238), 7), new EmptyBorder(3, 8, 3, 8)));
         searchWrap.add(shortcut, BorderLayout.EAST);
         searchWrap.setMaximumSize(new Dimension(Integer.MAX_VALUE, 50));
         body.add(searchWrap);
         body.add(Box.createVerticalStrut(14));

         JPanel top = new JPanel(new GridBagLayout());
         top.setOpaque(false);
         GridBagConstraints tc = new GridBagConstraints();
         tc.gridy = 0; tc.fill = GridBagConstraints.BOTH; tc.weighty = 1.0;

         JPanel quick = this.homeCardV130();
         quick.setLayout(new BorderLayout(0, 12));
         JLabel quickTitle = new JLabel("快捷操作");
         quickTitle.setForeground(TEXT);
         quickTitle.setFont(quickTitle.getFont().deriveFont(Font.BOLD, 14.0F));
         quick.add(quickTitle, BorderLayout.NORTH);
         JPanel quickGrid = new JPanel(new GridLayout(1, 6, 10, 0));
         quickGrid.setOpaque(false);
         quickGrid.add(this.homeQuickTileV130("导入数据", "Excel / CSV / DTA", "▣", () -> this.navigateTo("data", "导入与转换", "hxconvert")));
         quickGrid.add(this.homeQuickTileV130("描述统计", "summarize / tabstat", "▥", () -> this.openCommandPage("summarize")));
         quickGrid.add(this.homeQuickTileV130("基准回归", "xtreg / reghdfe", "↗", () -> this.openBaselineRegressionWorkspace()));
         quickGrid.add(this.homeQuickTileV130("固定效应", "areg / reghdfe", "▦", () -> this.openCommandPage("reghdfe")));
         quickGrid.add(this.homeQuickTileV130("双重差分", "didregress", "⌘", () -> this.openCommandPage("didregress")));
         quickGrid.add(this.homeQuickTileV130("OneClick", "控制变量组合", "✦", () -> this.openCommandPage("oneclick")));
         quick.add(quickGrid, BorderLayout.CENTER);
         tc.gridx = 0; tc.weightx = 0.70; tc.insets = new Insets(0, 0, 0, 12);
         top.add(quick, tc);

         JPanel data = this.homeCardV130();
         data.setLayout(new BorderLayout(0, 12));
         JLabel dataTitle = new JLabel("当前数据");
         dataTitle.setForeground(TEXT);
         dataTitle.setFont(dataTitle.getFont().deriveFont(Font.BOLD, 14.0F));
         data.add(dataTitle, BorderLayout.NORTH);
         JPanel dataCenter = new JPanel();
         dataCenter.setOpaque(false);
         dataCenter.setLayout(new BoxLayout(dataCenter, BoxLayout.Y_AXIS));
         this.homeDatasetStatus.setHorizontalAlignment(SwingConstants.CENTER);
         this.homeDatasetStatus.setAlignmentX(0.5F);
         this.homeDatasetStatus.setForeground(TEXT);
         this.homeDatasetStatus.setFont(this.homeDatasetStatus.getFont().deriveFont(Font.BOLD, 14.0F));
         this.homeDatasetDetail.setHorizontalAlignment(SwingConstants.CENTER);
         this.homeDatasetDetail.setAlignmentX(0.5F);
         this.homeDatasetDetail.setForeground(MUTED);
         this.homeDatasetDetail.setFont(this.homeDatasetDetail.getFont().deriveFont(9.5F));
         dataCenter.add(Box.createVerticalGlue());
         dataCenter.add(this.homeDatasetStatus);
         dataCenter.add(Box.createVerticalStrut(6));
         dataCenter.add(this.homeDatasetDetail);
         dataCenter.add(Box.createVerticalGlue());
         data.add(dataCenter, BorderLayout.CENTER);
         JPanel dataButtons = new JPanel(new GridLayout(1, 3, 8, 0));
         dataButtons.setOpaque(false);
         JButton dta = this.refButton("打开 DTA", true);
         dta.addActionListener(e -> this.chooseAndLoadDta());
         JButton excel = this.refButton("导入 Excel/CSV", false);
         excel.addActionListener(e -> this.navigateTo("data", "导入与转换", "hxconvert"));
         JButton auto = this.refButton("auto 示例", false);
         auto.addActionListener(e -> this.runUtility("sysuse auto, clear", true));
         dataButtons.add(dta); dataButtons.add(excel); dataButtons.add(auto);
         data.add(dataButtons, BorderLayout.SOUTH);
         tc.gridx = 1; tc.weightx = 0.30; tc.insets = new Insets(0, 0, 0, 0);
         top.add(data, tc);
         top.setMaximumSize(new Dimension(Integer.MAX_VALUE, 220));
         body.add(top);
         body.add(Box.createVerticalStrut(14));

         Object[][] commonRows = new Object[][]{
            {"导入数据", "Excel / CSV / DTA", "▣", (Runnable)() -> this.navigateTo("data", "导入与转换", "hxconvert")},
            {"描述统计", "summarize / tabstat", "▥", (Runnable)() -> this.openCommandPage("summarize")},
            {"基准回归", "xtreg / reghdfe / regress", "↗", (Runnable)() -> this.openBaselineRegressionWorkspace()},
            {"固定效应", "areg / reghdfe / xtreg", "▦", (Runnable)() -> this.openCommandPage("reghdfe")},
            {"双重差分", "didregress / xtdidregress", "⌘", (Runnable)() -> this.openCommandPage("didregress")},
            {"OneClick", "控制变量组合", "✦", (Runnable)() -> this.openCommandPage("oneclick")}
         };
         JPanel common = this.homeListSectionV130("常用任务", commonRows);

         JPanel recent = this.homeCardV130();
         recent.setLayout(new BorderLayout(0, 10));
         JLabel recentTitle = new JLabel("最近任务");
         recentTitle.setForeground(TEXT);
         recentTitle.setFont(recentTitle.getFont().deriveFont(Font.BOLD, 14.0F));
         recent.add(recentTitle, BorderLayout.NORTH);
         this.homeRecentPanel.setOpaque(false);
         recent.add(this.homeRecentPanel, BorderLayout.CENTER);
         JButton history = this.refButton("查看全部历史 →", false);
         history.addActionListener(e -> this.browseCategoryOverview("recent"));
         recent.add(history, BorderLayout.SOUTH);

         Object[][] moreRows = new Object[][]{
            {"导入与转换", "Excel / CSV / DTA", "⇄", (Runnable)() -> this.navigateTo("data", "导入与转换", "hxconvert")},
            {"数据检查", "缺失 / 重复 / 唯一键", "◎", (Runnable)() -> this.browseMethod("data", "数据检查")},
            {"变量处理", "generate / replace", "✣", (Runnable)() -> this.browseMethod("data", "变量处理")},
            {"样本处理", "keep / drop", "⌑", (Runnable)() -> this.browseMethod("data", "样本处理")},
            {"合并与追加", "merge / append", "⇆", (Runnable)() -> this.browseMethod("data", "合并与追加")},
            {"数据结构", "reshape / xtset / tsset", "▤", (Runnable)() -> this.browseMethod("data", "数据结构")},
            {"相关分析", "correlate / pwcorr", "⌁", (Runnable)() -> this.openCommandPage("pwcorr")},
            {"均值检验", "ttest", "⌗", (Runnable)() -> this.openCommandPage("ttest")},
            {"频数列联", "tabulate", "▦", (Runnable)() -> this.openCommandPage("tabulate")}
         };
         JPanel more = this.homeListSectionV130("更多功能", moreRows);

         JPanel lower = new JPanel(new GridLayout(1, 3, 12, 0));
         lower.setOpaque(false);
         lower.add(common);
         lower.add(recent);
         lower.add(more);
         lower.setMaximumSize(new Dimension(Integer.MAX_VALUE, 382));
         body.add(lower);
         body.add(Box.createVerticalGlue());

         JScrollPane scroll = new JScrollPane(body);
         scroll.setBorder(null);
         scroll.getVerticalScrollBar().setUnitIncrement(18);
         scroll.setBackground(APP_BG);
         root.add(scroll, BorderLayout.CENTER);
         return root;
      }

'''
    marker = '      private JComponent buildHomeContainerLegacy() {'
    s = s.replace(marker, home_block + marker, 1)

# ---- xtreg wizard page ----
if 'private void showXtregWizardPageV130()' not in s:
    open_marker = '      private void openCommandPage(String var1) {\n         this.baselineTaskActive = false;'
    if open_marker not in s:
        raise SystemExit('openCommandPage marker not found')
    s = s.replace(open_marker, '      private void openCommandPage(String var1) {\n         this.baselineTaskActive = false;\n         if ("xtreg".equals(var1)) {\n            this.showXtregWizardPageV130();\n            return;\n         }', 1)

    xtreg_block = r'''
      private JPanel xtregWizardCardV130(int step, String title, String subtitle) {
         JPanel card = cardPanel();
         card.setBackground(SURFACE);
         card.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 11),
            new EmptyBorder(12, 14, 12, 14)
         ));
         card.setLayout(new BorderLayout(12, 10));
         JLabel badge = new JLabel(Integer.toString(step), SwingConstants.CENTER);
         badge.setOpaque(true);
         badge.setBackground(new Color(47, 111, 228));
         badge.setForeground(Color.WHITE);
         badge.setFont(badge.getFont().deriveFont(Font.BOLD, 12.0F));
         badge.setPreferredSize(new Dimension(26, 26));
         badge.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(47, 111, 228), 13));
         card.add(badge, BorderLayout.WEST);
         JPanel head = new JPanel();
         head.setOpaque(false);
         head.setLayout(new BoxLayout(head, BoxLayout.Y_AXIS));
         JLabel t = new JLabel(title);
         t.setForeground(TEXT);
         t.setFont(t.getFont().deriveFont(Font.BOLD, 13.5F));
         JLabel st = new JLabel(subtitle);
         st.setForeground(MUTED);
         st.setFont(st.getFont().deriveFont(9.5F));
         head.add(t);
         head.add(Box.createVerticalStrut(3));
         head.add(st);
         card.add(head, BorderLayout.NORTH);
         return card;
      }

      private JComponent xtregStepStripV130() {
         JPanel strip = cardPanel();
         strip.setBackground(SURFACE);
         strip.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 11),
            new EmptyBorder(10, 12, 10, 12)
         ));
         strip.setLayout(new GridLayout(1, 4, 12, 0));
         String[][] steps = new String[][]{
            {"1", "面板设定", "指定个体与时间维度"},
            {"2", "选择变量", "选择因变量与解释变量"},
            {"3", "估计选项", "模型与标准误设置"},
            {"4", "预览并运行", "预览命令并运行估计"}
         };
         for (int i = 0; i < steps.length; i++) {
            JPanel p = new JPanel(new BorderLayout(8, 0));
            p.setOpaque(false);
            JLabel n = new JLabel(steps[i][0], SwingConstants.CENTER);
            n.setOpaque(true);
            n.setBackground(i == 0 ? new Color(47, 111, 228) : new Color(239, 243, 248));
            n.setForeground(i == 0 ? Color.WHITE : new Color(75, 88, 108));
            n.setPreferredSize(new Dimension(28, 28));
            n.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(i == 0 ? new Color(47, 111, 228) : new Color(225, 231, 239), 14));
            p.add(n, BorderLayout.WEST);
            JLabel label = new JLabel("<html><b>" + html(steps[i][1]) + "</b><br><span style='font-size:9px;color:#738096'>" + html(steps[i][2]) + "</span></html>");
            p.add(label, BorderLayout.CENTER);
            strip.add(p);
         }
         strip.setMaximumSize(new Dimension(Integer.MAX_VALUE, 62));
         return strip;
      }

      private void showXtregWizardPageV130() {
         this.regressWorkspaceActive = false;
         this.baselineTaskActive = false;
         this.activeCategoryCode = "stats";
         this.activeCategoryName = "统计";
         this.activeMethodName = "纵向/面板数据";
         this.currentCommand = "xtreg";
         this.showWorkspacePage();
         this.syncSidebarFromContext();
         this.selectDataView();
         this.commandDock.setVisible(false);
         this.commandTabs.setVisible(true);
         this.commandTabs.setSelectedIndex(0);
         this.setWorkspaceBreadcrumb("首页  /  统计  /  纵向/面板数据  /  xtreg");
         this.commandTitle.setText("xtreg · 面板数据回归");
         this.commandTitle.setToolTipText("Stata 官方面板数据回归命令");
         this.exampleLabel.setText("使用 xtreg 进行面板数据回归分析，分四步完成模型设定与估计。");
         this.insightArea.setText("xtreg 用于面板数据模型。先指定面板 ID 与时间变量，再选择因变量、解释变量和 FE/RE 等估计方式。右侧可随时查看当前数据、结果与日志。");
         this.syntaxArea.setText("常用语法：xtset panelvar timevar；xtreg y x1 x2, fe vce(robust)；或 xtreg y x1 x2, re。\n建议：常规企业面板研究可先从固定效应（FE）开始，再按研究设计调整标准误与模型设定。");

         this.formPanel.removeAll();
         this.formPanel.setLayout(new GridBagLayout());
         this.formPanel.setBackground(APP_BG);
         this.formPanel.setBorder(new EmptyBorder(12, 12, 16, 12));

         List<String> vars = HxWorkbench.StataBridge.variableNames();
         String[] choices = new String[vars.size() + 1];
         choices[0] = "";
         for (int i = 0; i < vars.size(); i++) choices[i + 1] = vars.get(i);

         JComboBox<String> panelVar = new JComboBox<>(choices);
         JComboBox<String> timeVar = new JComboBox<>(choices);
         JComboBox<String> dep = new JComboBox<>(choices);
         DefaultListModel<String> indepModel = new DefaultListModel<>();
         for (String v : vars) indepModel.addElement(v);
         JList<String> indep = new JList<>(indepModel);
         indep.setSelectionMode(2);
         indep.setVisibleRowCount(4);
         JScrollPane indepScroll = new JScrollPane(indep);
         indepScroll.setPreferredSize(new Dimension(420, 82));
         indepScroll.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 8));

         JRadioButton fe = new JRadioButton("固定效应（FE）", true);
         JRadioButton re = new JRadioButton("随机效应（RE）");
         JRadioButton be = new JRadioButton("between");
         JRadioButton pa = new JRadioButton("population-averaged");
         for (JRadioButton b : Arrays.asList(fe, re, be, pa)) { b.setOpaque(false); b.setForeground(TEXT); }
         ButtonGroup modelGroup = new ButtonGroup();
         modelGroup.add(fe); modelGroup.add(re); modelGroup.add(be); modelGroup.add(pa);
         JComboBox<String> se = new JComboBox<>(new String[]{"稳健标准误", "默认标准误", "按面板聚类"});

         JTextArea commandPreview = readonlyArea();
         commandPreview.setRows(2);
         commandPreview.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 12));
         commandPreview.setBackground(new Color(247, 250, 255));
         JScrollPane commandPreviewScroll = softScroll(commandPreview);
         commandPreviewScroll.setPreferredSize(new Dimension(640, 62));

         Runnable update = () -> {
            String pv = Objects.toString(panelVar.getSelectedItem(), "").trim();
            String tv = Objects.toString(timeVar.getSelectedItem(), "").trim();
            String y = Objects.toString(dep.getSelectedItem(), "").trim();
            List<String> xs = indep.getSelectedValuesList();
            String model = fe.isSelected() ? "fe" : re.isSelected() ? "re" : be.isSelected() ? "be" : "pa";
            StringBuilder xt = new StringBuilder("xtreg");
            if (!y.isBlank()) xt.append(" ").append(y);
            for (String x : xs) xt.append(" ").append(x);
            xt.append(", ").append(model);
            String sem = Objects.toString(se.getSelectedItem(), "");
            if ("稳健标准误".equals(sem)) xt.append(" vce(robust)");
            if ("按面板聚类".equals(sem) && !pv.isBlank()) xt.append(" vce(cluster ").append(pv).append(")");
            String setup = pv.isBlank() ? "xtset panelvar timevar" : "xtset " + pv + (tv.isBlank() ? "" : " " + tv);
            String shown = setup + "\n" + xt;
            commandPreview.setText(shown);
            this.previewArea.setText(xt.toString());
         };
         panelVar.addActionListener(e -> update.run());
         timeVar.addActionListener(e -> update.run());
         dep.addActionListener(e -> update.run());
         indep.addListSelectionListener(e -> { if (!e.getValueIsAdjusting()) update.run(); });
         for (JRadioButton b : Arrays.asList(fe, re, be, pa)) b.addActionListener(e -> update.run());
         se.addActionListener(e -> update.run());
         update.run();

         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0; c.gridy = 0; c.weightx = 1.0; c.fill = GridBagConstraints.HORIZONTAL; c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.xtregStepStripV130(), c);

         JPanel step1 = this.xtregWizardCardV130(1, "面板设定（xtset）", "先设置面板结构：指定个体变量（面板 ID）和时间变量（时间维度）。");
         JPanel s1Fields = new JPanel(new GridLayout(1, 2, 12, 0)); s1Fields.setOpaque(false);
         JPanel p1 = new JPanel(new BorderLayout(0, 5)); p1.setOpaque(false); p1.add(new JLabel("个体变量（面板 ID）"), BorderLayout.NORTH); p1.add(panelVar, BorderLayout.CENTER);
         JPanel p2 = new JPanel(new BorderLayout(0, 5)); p2.setOpaque(false); p2.add(new JLabel("时间变量"), BorderLayout.NORTH); p2.add(timeVar, BorderLayout.CENTER);
         s1Fields.add(p1); s1Fields.add(p2);
         step1.add(s1Fields, BorderLayout.CENTER);
         JPanel advice1 = new JPanel(); advice1.setBackground(new Color(246, 250, 255)); advice1.setBorder(new EmptyBorder(8, 10, 8, 10));
         advice1.add(new JLabel("建议：企业面板常见设置为 firm + year。"));
         step1.add(advice1, BorderLayout.EAST);
         c.gridy++; this.formPanel.add(step1, c);

         JPanel step2 = this.xtregWizardCardV130(2, "选择变量", "选择因变量和一个或多个解释变量。");
         JPanel s2Fields = new JPanel(new GridLayout(1, 2, 12, 0)); s2Fields.setOpaque(false);
         JPanel p3 = new JPanel(new BorderLayout(0, 5)); p3.setOpaque(false); p3.add(new JLabel("因变量（Y）"), BorderLayout.NORTH); p3.add(dep, BorderLayout.CENTER);
         JPanel p4 = new JPanel(new BorderLayout(0, 5)); p4.setOpaque(false); p4.add(new JLabel("解释变量（X，可多选）"), BorderLayout.NORTH); p4.add(indepScroll, BorderLayout.CENTER);
         s2Fields.add(p3); s2Fields.add(p4);
         step2.add(s2Fields, BorderLayout.CENTER);
         JPanel tip2 = new JPanel(); tip2.setBackground(new Color(244, 252, 248)); tip2.setBorder(new EmptyBorder(8, 10, 8, 10));
         tip2.add(new JLabel("提示：按 Ctrl / Shift 可多选解释变量。"));
         step2.add(tip2, BorderLayout.EAST);
         c.gridy++; this.formPanel.add(step2, c);

         JPanel step3 = this.xtregWizardCardV130(3, "估计选项", "选择模型类型与标准误方式，并按需要继续调整高级选项。");
         JPanel s3 = new JPanel(); s3.setOpaque(false); s3.setLayout(new BoxLayout(s3, BoxLayout.Y_AXIS));
         JPanel models = new JPanel(new GridLayout(1, 4, 8, 0)); models.setOpaque(false);
         models.add(fe); models.add(re); models.add(be); models.add(pa);
         s3.add(models); s3.add(Box.createVerticalStrut(10));
         JPanel seLine = new JPanel(new BorderLayout(12, 0)); seLine.setOpaque(false); seLine.add(new JLabel("标准误方式"), BorderLayout.WEST); seLine.add(se, BorderLayout.CENTER);
         s3.add(seLine);
         step3.add(s3, BorderLayout.CENTER);
         JPanel tip3 = new JPanel(); tip3.setBackground(new Color(255, 249, 236)); tip3.setBorder(new EmptyBorder(8, 10, 8, 10));
         tip3.add(new JLabel("小贴士：不确定时可先用 FE + 稳健标准误。"));
         step3.add(tip3, BorderLayout.EAST);
         c.gridy++; this.formPanel.add(step3, c);

         JPanel step4 = this.xtregWizardCardV130(4, "预览并运行", "查看将要执行的命令，确认无误后运行模型。");
         JPanel previewWrap = new JPanel(new BorderLayout(10, 0)); previewWrap.setOpaque(false);
         JPanel previewLeft = new JPanel(new BorderLayout(0, 5)); previewLeft.setOpaque(false); previewLeft.add(new JLabel("命令预览"), BorderLayout.NORTH); previewLeft.add(commandPreviewScroll, BorderLayout.CENTER);
         JTextArea syntax = readonlyArea(); syntax.setRows(3); syntax.setText("语法说明\n• xtset：声明面板结构\n• fe / re：固定效应或随机效应\n• vce(robust)：稳健标准误");
         JScrollPane syntaxScroll = softScroll(syntax); syntaxScroll.setPreferredSize(new Dimension(310, 72));
         previewWrap.add(previewLeft, BorderLayout.CENTER); previewWrap.add(syntaxScroll, BorderLayout.EAST);
         step4.add(previewWrap, BorderLayout.CENTER);
         JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 0)); actions.setOpaque(false);
         JButton prev = this.refButton("上一步", false); prev.addActionListener(e -> this.formScroll.getVerticalScrollBar().setValue(0));
         JButton clear = this.refButton("清空设置", false); clear.addActionListener(e -> { panelVar.setSelectedIndex(0); timeVar.setSelectedIndex(0); dep.setSelectedIndex(0); indep.clearSelection(); fe.setSelected(true); se.setSelectedIndex(0); update.run(); });
         JButton run = this.refButton("运行 xtreg", true);
         run.addActionListener(e -> {
            String pv = Objects.toString(panelVar.getSelectedItem(), "").trim();
            String tv = Objects.toString(timeVar.getSelectedItem(), "").trim();
            String y = Objects.toString(dep.getSelectedItem(), "").trim();
            List<String> xs = indep.getSelectedValuesList();
            if (pv.isBlank() || y.isBlank() || xs.isEmpty()) {
               JOptionPane.showMessageDialog(this, "请至少完成面板 ID、因变量和解释变量的选择。", "设置尚未完成", JOptionPane.INFORMATION_MESSAGE);
               return;
            }
            String setup = "xtset " + pv + (tv.isBlank() ? "" : " " + tv);
            String cmd = this.previewArea.getText().trim();
            int rc = HxWorkbench.StataBridge.execute(setup, false);
            if (rc == 0) rc = HxWorkbench.StataBridge.execute(cmd, true);
            this.statusLabel.setText(rc == 0 ? "xtreg 已运行。右侧可查看结果与日志。" : "xtreg 运行失败，返回码：" + rc);
            this.refreshDataset(false);
         });
         actions.add(prev); actions.add(clear); actions.add(run);
         step4.add(actions, BorderLayout.SOUTH);
         c.gridy++; this.formPanel.add(step4, c);

         c.gridy++; c.weighty = 1.0; c.fill = GridBagConstraints.BOTH;
         this.formPanel.add(Box.createVerticalGlue(), c);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.statusLabel.setText("已进入 xtreg 分步向导：面板设定 → 选择变量 → 估计选项 → 预览并运行。");
      }

'''
    marker = '      private void openCommandPage(String var1) {'
    s = s.replace(marker, xtreg_block + marker, 1)

java.write_text(s, encoding='utf-8')

# Update package/public entry-point version strings.
for name in ['hxempirical.ado', 'hxempirical.pkg', 'hxworkbench.ado']:
    p = root / name
    if p.exists():
        text = p.read_text(encoding='utf-8')
        text = text.replace('1.2.9', '1.3.0')
        p.write_text(text, encoding='utf-8')

print('home + xtreg UI patch applied')
