from pathlib import Path

p=Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s=p.read_text(encoding='utf-8')
s=s.replace('public static final String VERSION = "1.4.2";', 'public static final String VERSION = "1.4.3";', 1)
s=s.replace('SFIToolkit.displayln("HxWorkbench 1.4.2");', 'SFIToolkit.displayln("HxWorkbench 1.4.3");', 1)

old='''         JPanel center = new JPanel(new BorderLayout());
         center.setBackground(APP_BG);
         center.add(this.stageCards, BorderLayout.CENTER);
         center.add(this.buildStatusBar(), BorderLayout.SOUTH);

         JPanel shell = new JPanel(new BorderLayout());
         shell.setBackground(APP_BG);
         shell.add(this.buildSidebar(), BorderLayout.WEST);
         shell.add(center, BorderLayout.CENTER);
         this.add(shell, BorderLayout.CENTER);
'''
new='''         JPanel center = new JPanel(new BorderLayout());
         center.setBackground(APP_BG);
         center.add(this.buildSidebarToggleBar(), BorderLayout.NORTH);
         center.add(this.stageCards, BorderLayout.CENTER);
         center.add(this.buildStatusBar(), BorderLayout.SOUTH);

         JPanel shell = new JPanel(new BorderLayout());
         shell.setBackground(APP_BG);
         shell.add(this.buildSidebar(), BorderLayout.WEST);
         shell.add(center, BorderLayout.CENTER);
         this.add(shell, BorderLayout.CENTER);
'''
assert old in s
s=s.replace(old,new,1)

start=s.index('      private JComponent buildSidebar() {')
end=s.index('      private JButton homeQuickButton(', start)
replacement='''      private JComponent buildSidebarToggleBar() {
         JPanel bar = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 8));
         bar.setOpaque(false);
         bar.setPreferredSize(new Dimension(0, 46));
         bar.setMinimumSize(new Dimension(0, 46));
         this.sidebarToggleButton = new JButton("☰");
         this.sidebarToggleButton.setToolTipText("隐藏左侧导航");
         this.sidebarToggleButton.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(247, 250, 254), new Color(239, 244, 250), TEXT, new Color(226, 232, 240)));
         this.sidebarToggleButton.setBorder(new EmptyBorder(7, 11, 7, 11));
         this.sidebarToggleButton.setFocusPainted(false);
         this.sidebarToggleButton.setContentAreaFilled(false);
         this.sidebarToggleButton.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         this.sidebarToggleButton.setPreferredSize(new Dimension(42, 32));
         this.sidebarToggleButton.addActionListener(e -> this.toggleSidebarCollapsed());
         bar.add(this.sidebarToggleButton);
         return bar;
      }

      private JComponent buildSidebar() {
         this.sidebarButtons.clear();
         JPanel sidebar = new JPanel(new BorderLayout());
         sidebar.setBackground(SURFACE);
         sidebar.setPreferredSize(new Dimension(205, 0));
         this.sidebarPanel = sidebar;
         sidebar.setBorder(BorderFactory.createMatteBorder(0, 0, 0, 1, new Color(226, 232, 240)));

         JPanel nav = new JPanel();
         nav.setOpaque(false);
         nav.setBorder(new EmptyBorder(22, 11, 8, 11));
         nav.setLayout(new BoxLayout(nav, BoxLayout.Y_AXIS));
         nav.add(this.sidebarButton("home", "⌂", "工作台", this::showHomePage));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("data", "▤", "数据", () -> this.browseCategoryOverview("data")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("stats", "▥", "统计", () -> this.browseCategoryOverview("stats")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("graph", "▧", "图形", () -> this.browseCategoryOverview("graph")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("oneclick", "◇", "OneClick", () -> this.browseMethodCategory("oneclick")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("history", "◷", "历史", () -> this.browseCommandCategory("recent", "最近任务")));
         nav.add(Box.createVerticalStrut(8));
         nav.add(this.sidebarButton("settings", "⚙", "设置", () -> this.openHomeTask("special", "performance")));
         sidebar.add(nav, BorderLayout.NORTH);

         JPanel bottom = new JPanel();
         bottom.setOpaque(false);
         bottom.setBorder(new EmptyBorder(8, 18, 20, 18));
         bottom.setLayout(new BoxLayout(bottom, BoxLayout.Y_AXIS));
         JButton guide = new JButton("<html><div style='text-align:left'><b>新手指引</b><br><span style='font-size:9px;color:#718096'>5 分钟快速上手</span><br><span style='font-size:9px;color:#226df6'>立即查看  →</span></div></html>");
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
         JLabel version = new JLabel("版本：" + VERSION);
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
         this.sidebarBottomPanel = bottom;
         sidebar.add(bottom, BorderLayout.SOUTH);
         this.setSidebarActive("home");
         this.applySidebarCollapsedState();
         return sidebar;
      }

      private void toggleSidebarCollapsed() {
         this.sidebarCollapsed = !this.sidebarCollapsed;
         this.applySidebarCollapsedState();
      }

      private void applySidebarCollapsedState() {
         if (this.sidebarPanel == null) return;
         this.sidebarPanel.setVisible(!this.sidebarCollapsed);
         int width = this.sidebarCollapsed ? 0 : 205;
         this.sidebarPanel.setPreferredSize(new Dimension(width, 0));
         this.sidebarPanel.setMinimumSize(new Dimension(width, 0));
         if (this.sidebarBottomPanel != null) this.sidebarBottomPanel.setVisible(!this.sidebarCollapsed);
         if (this.sidebarToggleButton != null) {
            this.sidebarToggleButton.setText("☰");
            this.sidebarToggleButton.setToolTipText(this.sidebarCollapsed ? "打开左侧导航" : "隐藏左侧导航");
         }
         for (JButton button : this.sidebarButtons.values()) {
            String label = Objects.toString(button.getClientProperty("hx.sidebar.label"), "");
            String glyph = Objects.toString(button.getClientProperty("hx.sidebar.glyph"), "");
            String expanded = glyph.isBlank() ? label : glyph + "   " + label;
            button.setText("<html><b>" + html(expanded) + "</b></html>");
            button.setHorizontalAlignment(SwingConstants.LEFT);
            button.setBorder(new EmptyBorder(11, 14, 11, 14));
            button.setToolTipText(null);
         }
         this.sidebarPanel.revalidate();
         this.sidebarPanel.repaint();
         Container parent = this.sidebarPanel.getParent();
         if (parent != null) { parent.revalidate(); parent.repaint(); }
      }

      private JButton sidebarButton(String key, String glyph, String label, Runnable action) {
         JButton button = new JButton("<html><b>" + html(label) + "</b></html>");
         button.putClientProperty("hx.sidebar.key", key);
         button.putClientProperty("hx.sidebar.label", label);
         button.putClientProperty("hx.sidebar.glyph", glyph);
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
         else if ("stats".equals(this.activeCategoryCode) || "reg".equals(this.activeCategoryCode) || "post".equals(this.activeCategoryCode)) key = "stats";
         else if ("graph".equals(this.activeCategoryCode)) key = "graph";
         else if ("oneclick".equals(this.activeCategoryCode) || "did".equals(this.activeCategoryCode)) key = "oneclick";
         else if ("recent".equals(this.activeCategoryCode)) key = "history";
         else if ("performance".equals(this.activeCategoryCode) || "test".equals(this.activeCategoryCode)) key = "settings";
         this.setSidebarActive(key);
      }

'''
s=s[:start]+replacement+s[end:]
p.write_text(s,encoding='utf-8')

ado=Path('hxempirical.ado'); a=ado.read_text(encoding='utf-8'); a=a.replace('*! hxempirical 1.4.2','*! hxempirical 1.4.3',1).replace('版本：" as result "1.4.2"','版本：" as result "1.4.3"',1).replace('return local version "1.4.2"','return local version "1.4.3"',1); ado.write_text(a,encoding='utf-8')
pkg=Path('hxempirical.pkg'); pkg.write_text(pkg.read_text(encoding='utf-8').replace('d Version 1.4.2','d Version 1.4.3',1),encoding='utf-8')
hlp=Path('hxempirical.sthlp'); h=hlp.read_text(encoding='utf-8').replace('version 1.4.2','version 1.4.3',1).replace('The 1.4.2 interface','The 1.4.3 interface',1); hlp.write_text(h,encoding='utf-8')
readme=Path('README.md'); r=readme.read_text(encoding='utf-8').replace('当前发布版本：1.4.2','当前发布版本：1.4.3',1).replace('上次修改时间：2026-08-13 15:34（UTC+8）','上次修改时间：2026-08-13 15:53（UTC+8）',1); readme.write_text(r,encoding='utf-8')
print('SIDEBAR_PATCH_OK')
