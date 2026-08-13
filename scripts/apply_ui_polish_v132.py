from pathlib import Path

p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')


def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'missing marker: {label}')
    s = s.replace(old, new, 1)

# Expanded sidebar: icon + label; collapsed: icon only.
rep(
'''            button.setText(this.sidebarCollapsed ? "<html><b>" + html(compact) + "</b></html>" : "<html><b>" + html(label) + "</b></html>");''',
'''            String expanded = glyph.isBlank() ? label : glyph + "   " + label;
            button.setText(this.sidebarCollapsed ? "<html><b>" + html(compact) + "</b></html>" : "<html><b>" + html(expanded) + "</b></html>");''',
'sidebar expanded icon label'
)

# Add a true circular painted badge. JLabel opaque backgrounds were still square.
marker = '      private JPanel xtregWizardCardV130(int step, String title, String subtitle) {\n'
if marker not in s:
    raise SystemExit('missing xtreg card marker')
badge = r'''      private JComponent xtregCircleBadge(String text, boolean active, int size) {
         JComponent badge = new JComponent() {
            @Override
            protected void paintComponent(Graphics g0) {
               Graphics2D g = (Graphics2D)g0.create();
               g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
               int d = Math.min(getWidth(), getHeight()) - 2;
               int x = (getWidth() - d) / 2;
               int y = (getHeight() - d) / 2;
               g.setColor(active ? new Color(47, 111, 228) : new Color(239, 243, 248));
               g.fillOval(x, y, d, d);
               if (!active) {
                  g.setColor(new Color(225, 231, 239));
                  g.drawOval(x, y, d - 1, d - 1);
               }
               g.setColor(active ? Color.WHITE : new Color(75, 88, 108));
               g.setFont(getFont().deriveFont(Font.BOLD, size >= 28 ? 12.0F : 10.5F));
               java.awt.FontMetrics fm = g.getFontMetrics();
               int tx = (getWidth() - fm.stringWidth(text)) / 2;
               int ty = (getHeight() - fm.getHeight()) / 2 + fm.getAscent();
               g.drawString(text, tx, ty);
               g.dispose();
            }
         };
         Dimension d = new Dimension(size, size);
         badge.setPreferredSize(d);
         badge.setMinimumSize(d);
         badge.setMaximumSize(d);
         return badge;
      }

'''
s = s.replace(marker, badge + marker, 1)

old_card_badge = '''         JLabel badge = new JLabel(Integer.toString(step), SwingConstants.CENTER);
         badge.setOpaque(true);
         badge.setBackground(new Color(47, 111, 228));
         badge.setForeground(Color.WHITE);
         badge.setFont(badge.getFont().deriveFont(Font.BOLD, 12.0F));
         badge.setPreferredSize(new Dimension(28, 28));
         badge.setMinimumSize(new Dimension(28, 28));
         badge.setMaximumSize(new Dimension(28, 28));
         badge.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(47, 111, 228), 14));
         header.add(badge, BorderLayout.WEST);'''
new_card_badge = '''         JComponent badge = this.xtregCircleBadge(Integer.toString(step), true, 28);
         header.add(badge, BorderLayout.WEST);'''
rep(old_card_badge, new_card_badge, 'card circular badge')

old_strip_badge = '''            JLabel n = new JLabel(steps[i][0], SwingConstants.CENTER);
            n.setOpaque(true);
            n.setBackground(i == 0 ? new Color(47, 111, 228) : new Color(239, 243, 248));
            n.setForeground(i == 0 ? Color.WHITE : new Color(75, 88, 108));
            n.setPreferredSize(new Dimension(24, 24));
            n.setMinimumSize(new Dimension(24, 24));
            n.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(i == 0 ? new Color(47, 111, 228) : new Color(225, 231, 239), 12));
            p.add(n, BorderLayout.WEST);'''
new_strip_badge = '''            JComponent n = this.xtregCircleBadge(steps[i][0], i == 0, 24);
            p.add(n, BorderLayout.WEST);'''
rep(old_strip_badge, new_strip_badge, 'strip circular badge')

# Dependent-variable combo should stay normal-height beside the multi-select X list.
old_p3 = '''         JPanel p3 = new JPanel(new BorderLayout(0, 5)); p3.setOpaque(false); p3.add(new JLabel("<html>因变量（Y） <span style='color:#2f6fe4'>· 可拖入</span></html>"), BorderLayout.NORTH); p3.add(dep, BorderLayout.CENTER);'''
new_p3 = '''         JPanel p3 = new JPanel(new BorderLayout(0, 5));
         p3.setOpaque(false);
         p3.add(new JLabel("<html>因变量（Y） <span style='color:#2f6fe4'>· 可拖入</span></html>"), BorderLayout.NORTH);
         dep.setPreferredSize(new Dimension(100, 32));
         dep.setMaximumSize(new Dimension(Integer.MAX_VALUE, 32));
         JPanel depWrap = new JPanel();
         depWrap.setOpaque(false);
         depWrap.setLayout(new BoxLayout(depWrap, BoxLayout.Y_AXIS));
         dep.setAlignmentX(0.0F);
         depWrap.add(dep);
         depWrap.add(Box.createVerticalGlue());
         p3.add(depWrap, BorderLayout.CENTER);'''
rep(old_p3, new_p3, 'dependent variable height')

p.write_text(s, encoding='utf-8')
print('final UI polish applied')
