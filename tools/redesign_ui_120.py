from pathlib import Path

p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')


def method_span(src: str, signature: str):
    start = src.find(signature)
    if start < 0:
        raise SystemExit(f'missing method signature: {signature}')
    brace = src.find('{', start)
    if brace < 0:
        raise SystemExit(f'missing opening brace: {signature}')
    depth = 0
    i = brace
    state = 'code'
    while i < len(src):
        ch = src[i]
        nx = src[i + 1] if i + 1 < len(src) else ''
        if state == 'code':
            if ch == '"':
                state = 'string'
            elif ch == "'":
                state = 'char'
            elif ch == '/' and nx == '/':
                state = 'line'
                i += 1
            elif ch == '/' and nx == '*':
                state = 'block'
                i += 1
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return start, i + 1
        elif state == 'string':
            if ch == '\\':
                i += 1
            elif ch == '"':
                state = 'code'
        elif state == 'char':
            if ch == '\\':
                i += 1
            elif ch == "'":
                state = 'code'
        elif state == 'line':
            if ch == '\n':
                state = 'code'
        elif state == 'block':
            if ch == '*' and nx == '/':
                state = 'code'
                i += 1
        i += 1
    raise SystemExit(f'unclosed method: {signature}')


def replace_method(src: str, signature: str, replacement: str):
    a, b = method_span(src, signature)
    return src[:a] + replacement.rstrip() + src[b:]


# Public version strings.
s = s.replace('public static final String VERSION = "1.1.0";', 'public static final String VERSION = "1.2.0";', 1)
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.0.3");', 'SFIToolkit.displayln("HxWorkbench 1.2.0");', 1)

# Sidebar state fields.
anchor = '      private final JPanel homeAllFunctionsPanel = new JPanel();\n'
insert = anchor + '      private final Map<String, JButton> sidebarButtons = new LinkedHashMap<>();\n      private String activeSidebarKey = "home";\n'
if 'sidebarButtons = new LinkedHashMap<>()' not in s:
    if anchor not in s:
        raise SystemExit('missing sidebar field anchor')
    s = s.replace(anchor, insert, 1)

constructor = r'''      WorkbenchFrame(boolean var1) {
         super("我的实证工具箱");
         this.previewMode = var1;
         this.setDefaultCloseOperation(1);
         this.setMinimumSize(new Dimension(980, 620));
         this.setSize(new Dimension(1360, 820));
         this.setLocationRelativeTo(null);
         this.setLayout(new BorderLayout());
         this.getContentPane().setBackground(APP_BG);
         this.previewTimer = new Timer(260, var1x -> this.updatePreview());
         this.previewTimer.setRepeats(false);
         this.previewFlashTimer.setRepeats(false);
         this.buildNavigation();
         this.buildCommandPanel();
         this.buildDataPanel();
         this.oneClickP.setSelectedIndex(1);
         this.wireEvents();

         this.commandDataSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, this.buildCommandContainer(), this.buildDataContainer());
         this.commandDataSplit.setResizeWeight(0.68);
         this.commandDataSplit.setContinuousLayout(true);
         this.commandDataSplit.setBorder(null);
         this.commandDataSplit.setDividerSize(8);
         this.commandDataSplit.setBackground(APP_BG);

         this.stageCards.setBackground(APP_BG);
         this.stageCards.add(this.buildHomeContainer(), "home");
         this.stageCards.add(this.buildChooserContainer(), "chooser");
         this.stageCards.add(this.commandDataSplit, "workspace");

         JPanel center = new JPanel(new BorderLayout());
         center.setBackground(APP_BG);
         center.add(this.stageCards, BorderLayout.CENTER);
         center.add(this.buildStatusBar(), BorderLayout.SOUTH);

         JPanel shell = new JPanel(new BorderLayout());
         shell.setBackground(APP_BG);
         shell.add(this.buildSidebar(), BorderLayout.WEST);
         shell.add(center, BorderLayout.CENTER);
         this.add(shell, BorderLayout.CENTER);

         stylePrimaryButton(this.runButton);
         SwingUtilities.invokeLater(this::applyDividerRatios);
         if (var1) {
            this.populatePreviewState();
         } else {
            this.populateCategories();
            HxWorkbench.StataBridge.execute("quietly hxrefresh", false);
            this.refreshDataset(false);
            this.showHomePage();
         }
      }'''
s = replace_method(s, '      WorkbenchFrame(boolean var1)', constructor)

apply_dividers = r'''      void applyDividerRatios() {
         SwingUtilities.invokeLater(() -> {
            int var1 = (int)Math.round(this.commandDataSplit.getWidth() * 0.68);
            this.commandDataSplit.setDividerLocation(Math.max(540, var1));
            if (this.dataSummarySplit != null) {
               int var2 = (int)Math.round(this.dataSummarySplit.getHeight() * 0.70);
               this.dataSummarySplit.setDividerLocation(Math.max(170, var2));
            }
         });
      }'''
s = replace_method(s, '      void applyDividerRatios()', apply_dividers)

helpers = r'''
      private JComponent buildSidebar() {
         JPanel sidebar = new JPanel(new BorderLayout());
         sidebar.setBackground(SURFACE);
         sidebar.setPreferredSize(new Dimension(184, 0));
         sidebar.setBorder(BorderFactory.createMatteBorder(0, 0, 0, 1, BORDER));

         JPanel nav = new JPanel();
         nav.setOpaque(false);
         nav.setBorder(new EmptyBorder(20, 12, 12, 12));
         nav.setLayout(new BoxLayout(nav, BoxLayout.Y_AXIS));
         nav.add(this.sidebarButton("home", "⌂", "工作台", this::showHomePage));
         nav.add(Box.createVerticalStrut(7));
         nav.add(this.sidebarButton("data", "▤", "数据", () -> this.browseCategoryOverview("data")));
         nav.add(Box.createVerticalStrut(7));
         nav.add(this.sidebarButton("reg", "↗", "回归", () -> this.browseCategoryOverview("reg")));
         nav.add(Box.createVerticalStrut(7));
         nav.add(this.sidebarButton("stats", "✓", "检验", () -> this.browseCategoryOverview("stats")));
         nav.add(Box.createVerticalStrut(7));
         nav.add(this.sidebarButton("oneclick", "◆", "OneClick", () -> this.browseMethodCategory("oneclick")));
         nav.add(Box.createVerticalStrut(7));
         nav.add(this.sidebarButton("history", "◷", "历史", () -> this.browseCommandCategory("recent", "最近任务")));
         nav.add(Box.createVerticalStrut(7));
         nav.add(this.sidebarButton("settings", "⚙", "设置", () -> this.openHomeTask("special", "performance")));
         sidebar.add(nav, BorderLayout.NORTH);

         JPanel bottom = new JPanel();
         bottom.setOpaque(false);
         bottom.setBorder(new EmptyBorder(10, 16, 18, 16));
         bottom.setLayout(new BoxLayout(bottom, BoxLayout.Y_AXIS));
         JButton guide = new JButton("<html><div style='text-align:left'><b>新手指引</b><br><span style='font-size:9px;color:#637083'>5 分钟快速上手</span></div></html>");
         guide.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(new Color(247, 250, 255), new Color(238, 246, 255), new Color(228, 239, 253), ACCENT, new Color(211, 224, 243)));
         guide.setBorder(new EmptyBorder(12, 12, 12, 12));
         guide.setHorizontalAlignment(SwingConstants.LEFT);
         guide.setFocusPainted(false);
         guide.setContentAreaFilled(false);
         guide.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         guide.setMaximumSize(new Dimension(Integer.MAX_VALUE, 64));
         guide.setAlignmentX(0.0F);
         guide.addActionListener(e -> {
            HxWorkbench.StataBridge.execute("help hxempirical", false);
            HxWorkbench.StataBridge.execute("window manage forward viewer", false);
         });
         bottom.add(guide);
         bottom.add(Box.createVerticalStrut(16));
         JLabel version = new JLabel("版本：1.2.0");
         version.setForeground(MUTED);
         version.setFont(version.getFont().deriveFont(10.0F));
         version.setAlignmentX(0.0F);
         bottom.add(version);
         bottom.add(Box.createVerticalStrut(5));
         JLabel policy = new JLabel("帮助文档  ·  意见反馈");
         policy.setForeground(ACCENT);
         policy.setFont(policy.getFont().deriveFont(10.0F));
         policy.setAlignmentX(0.0F);
         bottom.add(policy);
         sidebar.add(bottom, BorderLayout.SOUTH);
         this.setSidebarActive("home");
         return sidebar;
      }

      private JButton sidebarButton(String key, String glyph, String label, Runnable action) {
         JButton button = new JButton("<html><div style='text-align:left'><span style='font-size:15px'>" + html(glyph) + "</span>&nbsp;&nbsp;<b>" + html(label) + "</b></div></html>");
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
      }

      private void applySidebarStyle(JButton button, boolean active) {
         Color bg = active ? new Color(232, 241, 255) : SURFACE;
         Color hover = active ? new Color(224, 236, 253) : new Color(247, 249, 252);
         Color pressed = active ? new Color(213, 229, 251) : new Color(238, 243, 249);
         Color fg = active ? new Color(20, 96, 214) : new Color(43, 55, 73);
         button.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(bg, hover, pressed, fg, active ? new Color(210, 226, 249) : SURFACE));
      }

      private void setSidebarActive(String key) {
         this.activeSidebarKey = key == null || key.isBlank() ? "home" : key;
         for (Entry<String, JButton> entry : this.sidebarButtons.entrySet()) {
            this.applySidebarStyle(entry.getValue(), entry.getKey().equals(this.activeSidebarKey));
         }
      }

      private void syncSidebarFromContext() {
         String key = "home";
         if ("data".equals(this.activeCategoryCode)) key = "data";
         else if ("reg".equals(this.activeCategoryCode)) key = "reg";
         else if ("stats".equals(this.activeCategoryCode) || "post".equals(this.activeCategoryCode) || "graph".equals(this.activeCategoryCode)) key = "stats";
         else if ("oneclick".equals(this.activeCategoryCode)) key = "oneclick";
         else if ("recent".equals(this.activeCategoryCode)) key = "history";
         else if ("performance".equals(this.activeCategoryCode) || "test".equals(this.activeCategoryCode)) key = "settings";
         this.setSidebarActive(key);
      }

      private JButton homeQuickButton(String title, String glyph, Runnable action) {
         JButton button = new JButton("<html><div style='text-align:center'><span style='font-size:18px;color:#2563d9'>" + html(glyph) + "</span><br><b>" + html(title) + "</b></div></html>");
         button.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(247, 250, 255), new Color(236, 244, 255), TEXT, new Color(216, 225, 238)));
         button.setBorder(new EmptyBorder(10, 8, 10, 8));
         button.setFocusPainted(false);
         button.setContentAreaFilled(false);
         button.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         button.addActionListener(e -> action.run());
         return button;
      }

      private JButton homeFeatureButton(String title, String subtitle, String glyph, Runnable action) {
         JButton button = new JButton("<html><div style='text-align:center'><span style='font-size:16px;color:#2a66be'>" + html(glyph) + "</span><br><b>" + html(title) + "</b><br><span style='font-size:8px;color:#637083'>" + html(subtitle) + "</span></div></html>");
         button.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 250, 253), new Color(239, 244, 250), TEXT, new Color(222, 228, 237)));
         button.setBorder(new EmptyBorder(10, 8, 10, 8));
         button.setFocusPainted(false);
         button.setContentAreaFilled(false);
         button.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         button.addActionListener(e -> action.run());
         return button;
      }

      private static String taskGlyph(String title) {
         if (title.contains("导入")) return "▤";
         if (title.contains("描述")) return "▥";
         if (title.contains("基准")) return "↗";
         if (title.contains("固定")) return "◆";
         if (title.contains("双重")) return "DID";
         if (title.contains("OneClick")) return "⚡";
         return "→";
      }
'''
if 'private JComponent buildSidebar()' not in s:
    marker = '      private JComponent buildHomeContainer() {'
    pos = s.find(marker)
    if pos < 0:
        raise SystemExit('missing home method marker for helper insertion')
    s = s[:pos] + helpers + '\n' + s[pos:]

home_method = r'''      private JComponent buildHomeContainer() {
         JPanel root = new JPanel(new BorderLayout());
         root.setBackground(APP_BG);
         JPanel page = new JPanel();
         page.setBackground(APP_BG);
         page.setBorder(new EmptyBorder(24, 28, 28, 28));
         page.setLayout(new BoxLayout(page, BoxLayout.Y_AXIS));

         JPanel titleRow = new JPanel(new BorderLayout(12, 0));
         titleRow.setOpaque(false);
         titleRow.setAlignmentX(0.0F);
         JPanel titles = new JPanel();
         titles.setOpaque(false);
         titles.setLayout(new BoxLayout(titles, BoxLayout.Y_AXIS));
         JLabel title = new JLabel("实证工作台");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD, 25.0F));
         JLabel subtitle = new JLabel("从数据导入到结果分析，一站式完成您的实证研究。");
         subtitle.setForeground(MUTED);
         subtitle.setFont(subtitle.getFont().deriveFont(11.5F));
         titles.add(title);
         titles.add(Box.createVerticalStrut(5));
         titles.add(subtitle);
         titleRow.add(titles, BorderLayout.WEST);
         JPanel topActions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 0));
         topActions.setOpaque(false);
         JButton backToStata = this.secondary("返回 Stata");
         backToStata.addActionListener(e -> this.toBack());
         JButton help = this.secondary("帮助");
         help.addActionListener(e -> {
            HxWorkbench.StataBridge.execute("help hxempirical", false);
            HxWorkbench.StataBridge.execute("window manage forward viewer", false);
         });
         topActions.add(backToStata);
         topActions.add(help);
         titleRow.add(topActions, BorderLayout.EAST);
         page.add(titleRow);
         page.add(Box.createVerticalStrut(18));

         JPanel hero = cardPanel();
         hero.setBackground(new Color(245, 249, 255));
         hero.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(205, 220, 244), 12), new EmptyBorder(18, 20, 18, 20)));
         hero.setLayout(new GridBagLayout());
         hero.setAlignmentX(0.0F);
         GridBagConstraints left = new GridBagConstraints();
         left.gridx = 0; left.gridy = 0; left.weightx = 0.56; left.weighty = 1.0; left.fill = GridBagConstraints.BOTH; left.insets = new Insets(0, 0, 0, 20);
         GridBagConstraints right = new GridBagConstraints();
         right.gridx = 1; right.gridy = 0; right.weightx = 0.44; right.weighty = 1.0; right.fill = GridBagConstraints.BOTH;

         JPanel start = new JPanel();
         start.setOpaque(false);
         start.setLayout(new BoxLayout(start, BoxLayout.Y_AXIS));
         JLabel startTitle = new JLabel("开始分析");
         startTitle.setForeground(TEXT);
         startTitle.setFont(startTitle.getFont().deriveFont(Font.BOLD, 18.0F));
         startTitle.setAlignmentX(0.0F);
         start.add(startTitle);
         start.add(Box.createVerticalStrut(3));
         JLabel startHint = new JLabel("告诉我您想做什么");
         startHint.setForeground(MUTED);
         startHint.setAlignmentX(0.0F);
         start.add(startHint);
         start.add(Box.createVerticalStrut(10));
         JPanel search = new JPanel(new BorderLayout(8, 0));
         search.setOpaque(false);
         styleTextField(this.searchField);
         this.searchField.setFont(this.searchField.getFont().deriveFont(13.0F));
         this.searchField.setToolTipText("例如：基准回归、reghdfe、描述统计、缺失值");
         JButton startButton = new JButton("开始");
         stylePrimaryButton(startButton);
         startButton.setPreferredSize(new Dimension(76, 36));
         startButton.addActionListener(e -> this.smartHomeSearch());
         this.searchField.addActionListener(e -> this.smartHomeSearch());
         search.add(this.searchField, BorderLayout.CENTER);
         search.add(startButton, BorderLayout.EAST);
         search.setMaximumSize(new Dimension(Integer.MAX_VALUE, 38));
         search.setAlignmentX(0.0F);
         start.add(search);
         start.add(Box.createVerticalStrut(8));
         JLabel examples = new JLabel("试试：基准回归　固定效应　双重差分　描述统计　OneClick");
         examples.setForeground(MUTED);
         examples.setFont(examples.getFont().deriveFont(9.5F));
         examples.setAlignmentX(0.0F);
         start.add(examples);
         hero.add(start, left);

         JPanel quick = new JPanel(new BorderLayout(0, 8));
         quick.setOpaque(false);
         JLabel quickTitle = new JLabel("快速开始");
         quickTitle.setForeground(TEXT);
         quickTitle.setFont(quickTitle.getFont().deriveFont(Font.BOLD, 12.5F));
         quick.add(quickTitle, BorderLayout.NORTH);
         JPanel quickGrid = new JPanel(new GridLayout(1, 5, 8, 0));
         quickGrid.setOpaque(false);
         quickGrid.add(this.homeQuickButton("基准回归", "↗", this::openBaselineRegressionWorkspace));
         quickGrid.add(this.homeQuickButton("固定效应", "◆", () -> this.browseMethod("reg", "固定效应线性回归")));
         quickGrid.add(this.homeQuickButton("双重差分", "DID", () -> this.browseMethod("reg", "双重差分")));
         quickGrid.add(this.homeQuickButton("描述统计", "▥", () -> this.browseMethod("stats", "描述统计")));
         quickGrid.add(this.homeQuickButton("OneClick", "⚡", () -> this.browseMethodCategory("oneclick")));
         quick.add(quickGrid, BorderLayout.CENTER);
         hero.add(quick, right);
         page.add(hero);
         page.add(Box.createVerticalStrut(16));

         JPanel mainRow = new JPanel(new GridBagLayout());
         mainRow.setOpaque(false);
         mainRow.setAlignmentX(0.0F);
         GridBagConstraints commonC = new GridBagConstraints();
         commonC.gridx = 0; commonC.gridy = 0; commonC.weightx = 0.70; commonC.weighty = 1.0; commonC.fill = GridBagConstraints.BOTH; commonC.insets = new Insets(0, 0, 0, 14);
         GridBagConstraints sideC = new GridBagConstraints();
         sideC.gridx = 1; sideC.gridy = 0; sideC.weightx = 0.30; sideC.weighty = 1.0; sideC.fill = GridBagConstraints.BOTH;

         JPanel common = cardPanel();
         common.setLayout(new BorderLayout(0, 12));
         common.add(sectionTitle("常用任务"), BorderLayout.NORTH);
         JPanel commonGrid = new JPanel(new GridLayout(2, 3, 12, 12));
         commonGrid.setOpaque(false);
         commonGrid.add(this.homeLauncherButton("导入数据", "从 Excel / CSV / DTA 等文件导入", () -> this.navigateTo("data", "导入与转换", "hxconvert"), false));
         commonGrid.add(this.homeLauncherButton("描述统计", "汇总统计、分组统计、变量分布", () -> this.browseMethod("stats", "描述统计"), false));
         commonGrid.add(this.homeLauncherButton("基准回归（OLS）", "任务式回归工作区，可切换估计方法", this::openBaselineRegressionWorkspace, true));
         commonGrid.add(this.homeLauncherButton("固定效应", "个体 / 时间 / 多维固定效应回归", () -> this.browseMethod("reg", "固定效应线性回归"), true));
         commonGrid.add(this.homeLauncherButton("双重差分（DID）", "Stata 官方 didregress / xtdidregress", () -> this.browseMethod("reg", "双重差分"), true));
         commonGrid.add(this.homeLauncherButton("OneClick 分析", "控制变量组合与稳健性 Workflow", () -> this.browseMethodCategory("oneclick"), true));
         common.add(commonGrid, BorderLayout.CENTER);
         mainRow.add(common, commonC);

         JPanel side = new JPanel();
         side.setOpaque(false);
         side.setLayout(new BoxLayout(side, BoxLayout.Y_AXIS));
         JPanel dataCard = cardPanel();
         dataCard.setLayout(new BoxLayout(dataCard, BoxLayout.Y_AXIS));
         JLabel dataTitle = sectionTitle("当前数据");
         dataTitle.setAlignmentX(0.0F);
         dataCard.add(dataTitle);
         dataCard.add(Box.createVerticalStrut(10));
         this.homeDatasetStatus.setForeground(TEXT);
         this.homeDatasetStatus.setFont(this.homeDatasetStatus.getFont().deriveFont(Font.BOLD, 14.5F));
         this.homeDatasetStatus.setAlignmentX(0.0F);
         this.homeDatasetDetail.setForeground(MUTED);
         this.homeDatasetDetail.setFont(this.homeDatasetDetail.getFont().deriveFont(10.0F));
         this.homeDatasetDetail.setAlignmentX(0.0F);
         dataCard.add(this.homeDatasetStatus);
         dataCard.add(Box.createVerticalStrut(4));
         dataCard.add(this.homeDatasetDetail);
         dataCard.add(Box.createVerticalStrut(12));
         JPanel dataButtons = new JPanel(new GridLayout(0, 1, 0, 7));
         dataButtons.setOpaque(false);
         JButton openDta = this.secondary("打开 DTA 文件");
         JButton importExcel = this.secondary("导入 Excel / CSV");
         JButton loadAuto = this.secondary("载入 auto 示例");
         openDta.addActionListener(e -> this.chooseAndLoadDta());
         importExcel.addActionListener(e -> this.navigateTo("data", "导入与转换", "hxconvert"));
         loadAuto.addActionListener(e -> this.runUtility("sysuse auto, clear", true));
         dataButtons.add(openDta); dataButtons.add(importExcel); dataButtons.add(loadAuto);
         dataCard.add(dataButtons);
         dataCard.setAlignmentX(0.0F);
         side.add(dataCard);
         side.add(Box.createVerticalStrut(12));

         JPanel recentCard = cardPanel();
         recentCard.setLayout(new BorderLayout(0, 9));
         recentCard.add(sectionTitle("最近任务"), BorderLayout.NORTH);
         this.homeRecentPanel.setOpaque(false);
         this.homeRecentPanel.setLayout(new BoxLayout(this.homeRecentPanel, BoxLayout.Y_AXIS));
         recentCard.add(this.homeRecentPanel, BorderLayout.CENTER);
         recentCard.setAlignmentX(0.0F);
         side.add(recentCard);
         mainRow.add(side, sideC);
         page.add(mainRow);
         page.add(Box.createVerticalStrut(16));

         JPanel more = cardPanel();
         more.setLayout(new BorderLayout(0, 12));
         more.setAlignmentX(0.0F);
         more.add(sectionTitle("更多功能"), BorderLayout.NORTH);
         this.homeAllFunctionsPanel.removeAll();
         this.homeAllFunctionsPanel.setOpaque(false);
         this.homeAllFunctionsPanel.setLayout(new GridLayout(0, 5, 10, 10));
         this.homeAllFunctionsPanel.add(this.homeFeatureButton("导入与转换", "Excel / CSV / DTA", "↔", () -> this.navigateTo("data", "导入与转换", "hxconvert")));
         this.homeAllFunctionsPanel.add(this.homeFeatureButton("数据检查", "缺失值 / 重复值", "✓", () -> this.browseMethod("data", "数据检查")));
         this.homeAllFunctionsPanel.add(this.homeFeatureButton("变量处理", "生成 / 修改 / 类型", "ƒ", () -> this.browseMethod("data", "变量处理")));
         this.homeAllFunctionsPanel.add(this.homeFeatureButton("样本处理", "筛选 / 子样本", "⊙", () -> this.browseMethod("data", "样本处理")));
         this.homeAllFunctionsPanel.add(this.homeFeatureButton("合并与追加", "merge / append", "≡", () -> this.browseMethod("data", "合并与追加")));
         this.homeAllFunctionsPanel.add(this.homeFeatureButton("数据结构", "reshape / xtset / tsset", "▦", () -> this.browseMethod("data", "数据结构")));
         this.homeAllFunctionsPanel.add(this.homeFeatureButton("相关分析", "pwcorr / correlate", "⌕", () -> this.browseMethod("stats", "相关分析")));
         this.homeAllFunctionsPanel.add(this.homeFeatureButton("均值检验", "t 检验 / 方差分析", "△", () -> this.browseMethod("stats", "均值检验")));
         this.homeAllFunctionsPanel.add(this.homeFeatureButton("频数列联", "频数 / 交叉表", "▥", () -> this.browseMethod("stats", "频数列联")));
         this.homeAllFunctionsPanel.add(this.homeFeatureButton("回归模型", "面板 / IV / 计数", "↗", () -> this.browseCategoryOverview("reg")));
         more.add(this.homeAllFunctionsPanel, BorderLayout.CENTER);
         page.add(more);

         JScrollPane scroll = new JScrollPane(page);
         scroll.setBorder(null);
         scroll.getViewport().setBackground(APP_BG);
         scroll.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
         scroll.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
         scroll.getVerticalScrollBar().setPreferredSize(new Dimension(0, 0));
         scroll.getVerticalScrollBar().setUnitIncrement(18);
         root.add(scroll, BorderLayout.CENTER);
         SwingUtilities.invokeLater(this::refreshHomeContext);
         return root;
      }'''
s = replace_method(s, '      private JComponent buildHomeContainer()', home_method)

launcher_method = r'''      private JButton homeLauncherButton(String var1, String var2, Runnable var3, boolean var4) {
         String glyph = taskGlyph(var1);
         JButton var5 = new JButton(
            "<html><div style='text-align:left'><span style='font-size:16px;color:" + (var4 ? "#2563d9" : "#2f855a") + "'>" + html(glyph) + "</span>&nbsp;&nbsp;<b>" + html(var1) + "</b><br><span style='font-size:9px;color:#637083'>" + html(var2) + "</span><span style='float:right;color:#7b8798'>&nbsp;&nbsp;›</span></div></html>"
         );
         Color var6 = SURFACE;
         Color var7 = var4 ? new Color(244, 248, 255) : new Color(249, 251, 253);
         Color var8 = var4 ? new Color(233, 241, 253) : new Color(241, 246, 249);
         var5.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(var6, var7, var8, TEXT, new Color(220, 227, 237)));
         var5.setBorder(new EmptyBorder(13, 14, 13, 14));
         var5.setHorizontalAlignment(SwingConstants.LEFT);
         var5.setVerticalAlignment(SwingConstants.TOP);
         var5.setPreferredSize(new Dimension(200, 78));
         var5.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         var5.setFocusPainted(false);
         var5.setContentAreaFilled(false);
         var5.addActionListener(var1x -> var3.run());
         return var5;
      }'''
s = replace_method(s, '      private JButton homeLauncherButton(String var1, String var2, Runnable var3, boolean var4)', launcher_method)

recent_method = r'''      private void rebuildHomeRecentPanel() {
         this.homeRecentPanel.removeAll();
         List<HxWorkbench.WorkbenchFrame.WorkSnapshot> var1 = this.loadRecentSnapshots();
         if (this.previewMode && var1.isEmpty()) {
            HxWorkbench.WorkbenchFrame.WorkSnapshot a = new HxWorkbench.WorkbenchFrame.WorkSnapshot();
            a.command = "reghdfe"; a.label = "固定效应回归分析"; a.depvar = "ROA"; a.x = "TPU"; a.method = "基准回归";
            HxWorkbench.WorkbenchFrame.WorkSnapshot b = new HxWorkbench.WorkbenchFrame.WorkSnapshot();
            b.command = "xtdidregress"; b.label = "双重差分分析"; b.depvar = "y"; b.x = "treat"; b.method = "双重差分";
            var1 = Arrays.asList(a, b);
         }
         if (var1.isEmpty()) {
            JLabel empty = new JLabel("<html><span style='color:#637083'>运行一次分析后，这里会保存最近 3 个设置。<br>点击即可恢复参数，不会自动运行。</span></html>");
            empty.setAlignmentX(0.0F);
            this.homeRecentPanel.add(empty);
         } else {
            for (HxWorkbench.WorkbenchFrame.WorkSnapshot item : var1) {
               String title = item.label.isBlank() ? item.command : item.label;
               String detail = item.depvar.isBlank() && item.x.isBlank() ? item.command : (item.depvar.isBlank() ? "" : "Y=" + item.depvar) + (item.x.isBlank() ? "" : " · X=" + item.x);
               JButton button = new JButton("<html><div style='text-align:left'><b>" + html(title) + "</b><br><span style='font-size:9px;color:#637083'>" + html(detail) + "</span></div></html>");
               button.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 250, 253), new Color(239, 244, 250), TEXT, new Color(229, 233, 239)));
               button.setBorder(new EmptyBorder(8, 10, 8, 10));
               button.setHorizontalAlignment(SwingConstants.LEFT);
               button.setMaximumSize(new Dimension(Integer.MAX_VALUE, 52));
               button.setAlignmentX(0.0F);
               button.setFocusPainted(false);
               button.setContentAreaFilled(false);
               button.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
               button.addActionListener(e -> this.restoreWorkSnapshot(item));
               this.homeRecentPanel.add(button);
               this.homeRecentPanel.add(Box.createVerticalStrut(5));
            }
         }
         this.homeRecentPanel.revalidate();
         this.homeRecentPanel.repaint();
      }'''
s = replace_method(s, '      private void rebuildHomeRecentPanel()', recent_method)

command_container = r'''      private JComponent buildCommandContainer() {
         JPanel root = new JPanel(new BorderLayout());
         root.setBackground(APP_BG);

         JPanel header = new JPanel(new BorderLayout(10, 8));
         header.setOpaque(false);
         header.setBorder(new EmptyBorder(18, 20, 10, 12));
         JPanel heading = new JPanel();
         heading.setOpaque(false);
         heading.setLayout(new BoxLayout(heading, BoxLayout.Y_AXIS));
         this.breadcrumbBar.setAlignmentX(0.0F);
         this.breadcrumbBar.setMaximumSize(new Dimension(Integer.MAX_VALUE, 22));
         heading.add(this.breadcrumbBar);
         heading.add(Box.createVerticalStrut(7));
         this.commandTitle.setFont(this.commandTitle.getFont().deriveFont(Font.BOLD, 22.0F));
         this.commandTitle.setAlignmentX(0.0F);
         heading.add(this.commandTitle);
         heading.add(Box.createVerticalStrut(5));
         this.exampleLabel.setForeground(MUTED);
         this.exampleLabel.setFont(this.exampleLabel.getFont().deriveFont(10.5F));
         this.exampleLabel.setAlignmentX(0.0F);
         heading.add(this.exampleLabel);
         header.add(heading, BorderLayout.CENTER);

         styleSecondaryButton(this.changeMethodButton);
         styleSecondaryButton(this.homeButton);
         this.homeButton.addActionListener(var1x -> this.showHomePage());
         this.changeMethodButton.addActionListener(var1x -> {
            if (this.chooserReady) {
               this.stageLayout.show(this.stageCards, "chooser");
               this.syncSidebarFromContext();
            } else {
               this.showHomePage();
            }
         });
         JButton help = new JButton("查看帮助");
         styleSecondaryButton(help);
         help.addActionListener(var1x -> this.openHelp());

         this.baselineEstimatorHeader = new JPanel(new FlowLayout(FlowLayout.LEFT, 6, 0));
         this.baselineEstimatorHeader.setOpaque(false);
         JLabel estimatorLabel = new JLabel("估计方法");
         estimatorLabel.setForeground(MUTED);
         estimatorLabel.setFont(estimatorLabel.getFont().deriveFont(Font.BOLD, 10.5F));
         this.baselineEstimator.setPreferredSize(new Dimension(120, 31));
         this.baselineEstimatorSource.setForeground(ACCENT);
         this.baselineEstimatorSource.setFont(this.baselineEstimatorSource.getFont().deriveFont(Font.BOLD, 10.0F));
         this.baselineEstimatorHeader.add(estimatorLabel);
         this.baselineEstimatorHeader.add(this.baselineEstimator);
         this.baselineEstimatorHeader.add(this.baselineEstimatorSource);
         this.baselineEstimatorHeader.setVisible(false);

         JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 7, 0));
         actions.setOpaque(false);
         actions.add(this.baselineEstimatorHeader);
         actions.add(this.changeMethodButton);
         actions.add(this.homeButton);
         actions.add(help);
         header.add(actions, BorderLayout.EAST);
         root.add(header, BorderLayout.NORTH);

         JPanel contentWrap = new JPanel(new BorderLayout());
         contentWrap.setOpaque(false);
         contentWrap.setBorder(new EmptyBorder(0, 18, 10, 8));
         JPanel contentCard = cardPanel();
         contentCard.setLayout(new BorderLayout());
         contentCard.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(216, 224, 235), 11), new EmptyBorder(2, 2, 2, 2)));
         contentCard.add(this.commandTabs, BorderLayout.CENTER);
         contentWrap.add(contentCard, BorderLayout.CENTER);
         root.add(contentWrap, BorderLayout.CENTER);

         this.commandDock = cardPanel();
         this.commandDock.setLayout(new BorderLayout(10, 7));
         this.commandDock.setBackground(SURFACE);
         this.commandDock.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(216, 224, 235), 11), new EmptyBorder(12, 14, 12, 14)));
         this.commandDockTitle.setForeground(TEXT);
         this.commandDockTitle.setFont(this.commandDockTitle.getFont().deriveFont(Font.BOLD, 12.5F));
         this.commandDockHint.setForeground(MUTED);
         this.commandDockHint.setFont(this.commandDockHint.getFont().deriveFont(9.5F));
         this.commandDockStatus.setForeground(MUTED);
         this.commandDockStatus.setFont(this.commandDockStatus.getFont().deriveFont(Font.BOLD, 10.0F));
         JPanel dockHeader = new JPanel(new BorderLayout());
         dockHeader.setOpaque(false);
         JPanel dockTitle = new JPanel();
         dockTitle.setOpaque(false);
         dockTitle.setLayout(new BoxLayout(dockTitle, BoxLayout.Y_AXIS));
         dockTitle.add(this.commandDockTitle);
         dockTitle.add(Box.createVerticalStrut(2));
         dockTitle.add(this.commandDockHint);
         dockHeader.add(dockTitle, BorderLayout.CENTER);
         dockHeader.add(this.commandDockStatus, BorderLayout.EAST);
         this.commandDock.add(dockHeader, BorderLayout.NORTH);
         JScrollPane preview = softScroll(this.previewArea);
         preview.setPreferredSize(new Dimension(100, 70));
         this.commandDock.add(preview, BorderLayout.CENTER);
         JPanel dockActions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 7, 0));
         dockActions.setOpaque(false);
         dockActions.add(this.copyCommandButton);
         dockActions.add(this.runButton);
         this.commandDockProgress.setVisible(false);
         this.commandDockProgress.setStringPainted(true);
         this.commandDockProgress.setPreferredSize(new Dimension(180, 16));
         JPanel dockSouth = new JPanel(new BorderLayout(10, 0));
         dockSouth.setOpaque(false);
         dockSouth.add(this.commandDockProgress, BorderLayout.CENTER);
         dockSouth.add(dockActions, BorderLayout.EAST);
         this.commandDock.add(dockSouth, BorderLayout.SOUTH);
         JPanel dockWrap = new JPanel(new BorderLayout());
         dockWrap.setOpaque(false);
         dockWrap.setBorder(new EmptyBorder(0, 18, 16, 8));
         dockWrap.add(this.commandDock, BorderLayout.CENTER);
         root.add(dockWrap, BorderLayout.SOUTH);
         return root;
      }'''
s = replace_method(s, '      private JComponent buildCommandContainer()', command_container)

data_container = r'''      private JComponent buildDataContainer() {
         JPanel root = new JPanel(new BorderLayout());
         root.setBackground(APP_BG);
         root.setBorder(new EmptyBorder(18, 8, 16, 18));
         JPanel card = cardPanel();
         card.setLayout(new BorderLayout());
         card.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(216, 224, 235), 11), new EmptyBorder(0, 0, 0, 0)));
         JPanel header = new JPanel(new BorderLayout(10, 4));
         header.setOpaque(false);
         header.setBorder(new EmptyBorder(14, 15, 9, 15));
         this.rightPaneTitle.setForeground(TEXT);
         this.rightPaneTitle.setFont(this.rightPaneTitle.getFont().deriveFont(Font.BOLD, 15.0F));
         styleSecondaryButton(this.refreshButton);
         header.add(this.rightPaneTitle, BorderLayout.WEST);
         header.add(this.refreshButton, BorderLayout.EAST);
         this.dataLabel.setForeground(MUTED);
         this.dataLabel.setFont(this.dataLabel.getFont().deriveFont(10.0F));
         header.add(this.dataLabel, BorderLayout.SOUTH);
         card.add(header, BorderLayout.NORTH);
         this.dataTabs.setBorder(new EmptyBorder(0, 6, 6, 6));
         card.add(this.dataTabs, BorderLayout.CENTER);
         root.add(card, BorderLayout.CENTER);
         return root;
      }'''
s = replace_method(s, '      private JComponent buildDataContainer()', data_container)

status_bar = r'''      private JComponent buildStatusBar() {
         JPanel var1 = new JPanel(new BorderLayout(10, 0));
         var1.setBorder(BorderFactory.createCompoundBorder(BorderFactory.createMatteBorder(1, 0, 0, 0, BORDER), new EmptyBorder(7, 18, 8, 18)));
         var1.setBackground(SURFACE);
         this.statusLabel.setForeground(MUTED);
         this.statusLabel.setFont(this.statusLabel.getFont().deriveFont(10.5F));
         var1.add(this.statusLabel, BorderLayout.CENTER);
         JLabel var2 = new JLabel("●  Stata 已连接   ·   数据只读，修改统一通过 Stata 命令");
         var2.setForeground(new Color(50, 126, 88));
         var2.setFont(var2.getFont().deriveFont(10.0F));
         var1.add(var2, BorderLayout.EAST);
         return var1;
      }'''
s = replace_method(s, '      private JComponent buildStatusBar()', status_bar)

chooser_container = r'''      private JComponent buildChooserContainer() {
         JPanel root = new JPanel(new BorderLayout());
         root.setBackground(APP_BG);
         JPanel header = new JPanel(new BorderLayout(14, 0));
         header.setOpaque(false);
         header.setBorder(new EmptyBorder(18, 22, 10, 22));
         JPanel titleBlock = new JPanel();
         titleBlock.setOpaque(false);
         titleBlock.setLayout(new BoxLayout(titleBlock, BoxLayout.Y_AXIS));
         this.chooserBreadcrumbBar.setOpaque(false);
         this.chooserBreadcrumbBar.setAlignmentX(0.0F);
         titleBlock.add(this.chooserBreadcrumbBar);
         titleBlock.add(Box.createVerticalStrut(7));
         this.chooserTitle.setForeground(TEXT);
         this.chooserTitle.setFont(this.chooserTitle.getFont().deriveFont(Font.BOLD, 23.0F));
         this.chooserTitle.setAlignmentX(0.0F);
         titleBlock.add(this.chooserTitle);
         titleBlock.add(Box.createVerticalStrut(5));
         this.chooserHint.setForeground(MUTED);
         this.chooserHint.setFont(this.chooserHint.getFont().deriveFont(10.5F));
         this.chooserHint.setAlignmentX(0.0F);
         titleBlock.add(this.chooserHint);
         header.add(titleBlock, BorderLayout.CENTER);
         styleSecondaryButton(this.chooserBackButton);
         styleSecondaryButton(this.chooserHomeButton);
         this.chooserBackButton.addActionListener(var1x -> this.handleChooserBack());
         this.chooserHomeButton.addActionListener(var1x -> this.showHomePage());
         JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 7, 0));
         actions.setOpaque(false);
         actions.add(this.chooserBackButton);
         actions.add(this.chooserHomeButton);
         header.add(actions, BorderLayout.EAST);
         root.add(header, BorderLayout.NORTH);

         this.chooserContent.setOpaque(false);
         this.chooserContent.setBorder(new EmptyBorder(2, 2, 2, 2));
         this.chooserContent.setLayout(new BoxLayout(this.chooserContent, BoxLayout.Y_AXIS));
         JPanel card = cardPanel();
         card.setLayout(new BorderLayout());
         card.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(216, 224, 235), 11), new EmptyBorder(14, 14, 14, 14)));
         card.add(this.chooserContent, BorderLayout.NORTH);
         JPanel wrap = new JPanel(new BorderLayout());
         wrap.setOpaque(false);
         wrap.setBorder(new EmptyBorder(0, 22, 20, 22));
         wrap.add(card, BorderLayout.CENTER);
         JScrollPane scroll = new JScrollPane(wrap);
         scroll.setBorder(null);
         scroll.getViewport().setBackground(APP_BG);
         scroll.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
         scroll.getVerticalScrollBar().setUnitIncrement(18);
         root.add(scroll, BorderLayout.CENTER);
         return root;
      }'''
s = replace_method(s, '      private JComponent buildChooserContainer()', chooser_container)

show_home = r'''      private void showHomePage() {
         this.currentCommand = "";
         this.regressWorkspaceActive = false;
         this.baselineTaskActive = false;
         if (this.baselineEstimatorHeader != null) this.baselineEstimatorHeader.setVisible(false);
         this.searchResultsMode = false;
         this.runButton.setEnabled(false);
         this.homeButton.setEnabled(false);
         this.homeButton.setVisible(false);
         this.inspectorToggle.setVisible(false);
         this.setSidebarActive("home");
         this.stageLayout.show(this.stageCards, "home");
         this.refreshHomeContext();
         this.statusLabel.setText("从常用任务开始，或直接搜索研究任务 / Stata 命令。");
      }'''
s = replace_method(s, '      private void showHomePage()', show_home)

show_workspace = r'''      private void showWorkspacePage() {
         this.homeButton.setVisible(true);
         this.homeButton.setEnabled(true);
         this.inspectorToggle.setVisible(false);
         this.configureWorkspaceBack();
         this.syncSidebarFromContext();
         this.stageLayout.show(this.stageCards, "workspace");
      }'''
s = replace_method(s, '      private void showWorkspacePage()', show_workspace)

# Keep sidebar highlight aligned when method/category chooser pages are opened.
s = s.replace('''      private void browseCategoryOverview(String var1) {\n         this.activeCategoryCode = var1;\n         this.activeCategoryName = categoryLabel(var1);''', '''      private void browseCategoryOverview(String var1) {\n         this.activeCategoryCode = var1;\n         this.activeCategoryName = categoryLabel(var1);\n         this.syncSidebarFromContext();''', 1)
s = s.replace('''      private void browseMethod(String var1, String var2) {\n         this.activeCategoryCode = var1;\n         this.activeCategoryName = categoryLabel(var1);''', '''      private void browseMethod(String var1, String var2) {\n         this.activeCategoryCode = var1;\n         this.activeCategoryName = categoryLabel(var1);\n         this.syncSidebarFromContext();''', 1)

# Make baseline task title copy match the new polished task-workspace language.
s = s.replace('this.exampleLabel.setText("<html>先设置 Y、核心 X 和 Controls；右上角只用一个小下拉框切换估计方法，变量设置会保留。</html>");',
              'this.exampleLabel.setText("<html>先设定研究问题，再选择估计方法。默认使用 xtreg；切换估计器时公共变量设置保持不变。</html>");', 1)

p.write_text(s, encoding='utf-8')
print('HX_UI_120_PATCH_OK')
