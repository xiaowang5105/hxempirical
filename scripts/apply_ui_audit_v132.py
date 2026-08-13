from pathlib import Path

root = Path('.')
java = root / 'src/main/java/com/hexie/stata/HxWorkbench.java'
s = java.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str):
    global s
    if old not in s:
        raise SystemExit(f'missing marker: {label}')
    s = s.replace(old, new, 1)


def replace_between(start_marker: str, end_marker: str, replacement: str, label: str):
    global s
    start = s.find(start_marker)
    if start < 0:
        raise SystemExit(f'missing start marker: {label}')
    end = s.find(end_marker, start)
    if end < 0:
        raise SystemExit(f'missing end marker: {label}')
    s = s[:start] + replacement + '\n\n' + s[end:]

# ---- version ----
s = s.replace('public static final String VERSION = "1.3.1";', 'public static final String VERSION = "1.3.2";', 1)
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.3.1");', 'SFIToolkit.displayln("HxWorkbench 1.3.2");', 1)

# ---- width-tracking form panel: eliminate horizontal clipping ----
replace_once('import java.awt.RenderingHints;\n', 'import java.awt.Rectangle;\nimport java.awt.RenderingHints;\n', 'Rectangle import')
replace_once('import javax.swing.JScrollPane;\n', 'import javax.swing.JScrollPane;\nimport javax.swing.Scrollable;\n', 'Scrollable import')
replace_once(
    '      private final JPanel formPanel = new JPanel(new GridBagLayout());\n',
    '      private final JPanel formPanel = new HxWorkbench.WorkbenchFrame.WidthTrackingPanel();\n',
    'form panel initializer'
)
replace_once(
    '      private static final class RoundedBorder extends AbstractBorder {\n',
    '''      private static final class WidthTrackingPanel extends JPanel implements Scrollable {
         private WidthTrackingPanel() {
            super(new GridBagLayout());
         }

         @Override
         public Dimension getPreferredScrollableViewportSize() {
            return this.getPreferredSize();
         }

         @Override
         public int getScrollableUnitIncrement(Rectangle visibleRect, int orientation, int direction) {
            return 18;
         }

         @Override
         public int getScrollableBlockIncrement(Rectangle visibleRect, int orientation, int direction) {
            return Math.max(18, visibleRect.height - 18);
         }

         @Override
         public boolean getScrollableTracksViewportWidth() {
            return true;
         }

         @Override
         public boolean getScrollableTracksViewportHeight() {
            return false;
         }
      }

      private static final class RoundedBorder extends AbstractBorder {
''',
    'WidthTrackingPanel class'
)
replace_once(
    '         this.formScroll.setBorder(null);\n         this.formScroll.getVerticalScrollBar().setUnitIncrement(16);\n',
    '         this.formScroll.setBorder(null);\n         this.formScroll.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);\n         this.formScroll.getVerticalScrollBar().setUnitIncrement(16);\n',
    'form scroll horizontal policy'
)

# ---- xtreg fields that survive dataset refresh ----
replace_once(
    '      private String draggedDataVariable = "";\n',
    '''      private String draggedDataVariable = "";
      private JComboBox<String> xtregPanelVar;
      private JComboBox<String> xtregTimeVar;
      private JComboBox<String> xtregDepVar;
      private JList<String> xtregIndepList;
      private Runnable xtregPreviewUpdater;
''',
    'xtreg field references'
)

# ---- cleaner collapsible sidebar ----
for old, new, label in [
    ('this.sidebarButton("home", "◆", "工作台"', 'this.sidebarButton("home", "⌂", "工作台"', 'home sidebar glyph'),
    ('this.sidebarButton("data", "", "数据"', 'this.sidebarButton("data", "▤", "数据"', 'data sidebar glyph'),
    ('this.sidebarButton("stats", "", "统计"', 'this.sidebarButton("stats", "▥", "统计"', 'stats sidebar glyph'),
    ('this.sidebarButton("graph", "", "图形"', 'this.sidebarButton("graph", "▧", "图形"', 'graph sidebar glyph'),
    ('this.sidebarButton("oneclick", "", "OneClick"', 'this.sidebarButton("oneclick", "◇", "OneClick"', 'oneclick sidebar glyph'),
]:
    replace_once(old, new, label)
replace_once('         int width = this.sidebarCollapsed ? 58 : 205;\n', '         int width = this.sidebarCollapsed ? 56 : 205;\n', 'collapsed sidebar width')
replace_once(
    '         Container parent = this.sidebarPanel.getParent();\n         if (parent != null) { parent.revalidate(); parent.repaint(); }\n         SwingUtilities.invokeLater(this::applyDividerRatios);\n',
    '         Container parent = this.sidebarPanel.getParent();\n         if (parent != null) { parent.revalidate(); parent.repaint(); }\n',
    'preserve user split ratio when sidebar toggles'
)

# ---- breadcrumb parser: support slash separators and avoid 首页 › 首页 / ... ----
replace_once(
    '         for (String raw : path.split("\\\\s*[›>]\\\\s*")) {\n',
    '         for (String raw : path.split("\\\\s*[›>/]\\\\s*")) {\n',
    'breadcrumb separator parser'
)

# ---- xtreg card: badge belongs in the card header, not a full-height blue bar ----
replace_between(
    '      private JPanel xtregWizardCardV130(int step, String title, String subtitle) {\n',
    '      private JComponent xtregStepStripV130() {\n',
    '''      private JPanel xtregWizardCardV130(int step, String title, String subtitle) {
         JPanel card = cardPanel();
         card.setBackground(SURFACE);
         card.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 11),
            new EmptyBorder(12, 14, 12, 14)
         ));
         card.setLayout(new BorderLayout(0, 10));
         card.setMinimumSize(new Dimension(0, 0));

         JPanel header = new JPanel(new BorderLayout(10, 0));
         header.setOpaque(false);
         JLabel badge = new JLabel(Integer.toString(step), SwingConstants.CENTER);
         badge.setOpaque(true);
         badge.setBackground(new Color(47, 111, 228));
         badge.setForeground(Color.WHITE);
         badge.setFont(badge.getFont().deriveFont(Font.BOLD, 12.0F));
         badge.setPreferredSize(new Dimension(28, 28));
         badge.setMinimumSize(new Dimension(28, 28));
         badge.setMaximumSize(new Dimension(28, 28));
         badge.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(47, 111, 228), 14));
         header.add(badge, BorderLayout.WEST);

         JPanel head = new JPanel();
         head.setOpaque(false);
         head.setLayout(new BoxLayout(head, BoxLayout.Y_AXIS));
         JLabel t = new JLabel(title);
         t.setForeground(TEXT);
         t.setFont(t.getFont().deriveFont(Font.BOLD, 13.5F));
         JLabel st = new JLabel("<html>" + html(subtitle) + "</html>");
         st.setForeground(MUTED);
         st.setFont(st.getFont().deriveFont(9.5F));
         st.setMinimumSize(new Dimension(0, 0));
         head.add(t);
         head.add(Box.createVerticalStrut(3));
         head.add(st);
         header.add(head, BorderLayout.CENTER);
         card.add(header, BorderLayout.NORTH);
         return card;
      }''',
    'xtreg wizard card'
)

# ---- compact step strip: 4 steps remain visible at narrow command-pane widths ----
replace_between(
    '      private JComponent xtregStepStripV130() {\n',
    '      private void installDataHeaderDragSupport() {\n',
    '''      private JComponent xtregStepStripV130() {
         JPanel strip = cardPanel();
         strip.setBackground(SURFACE);
         strip.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 11),
            new EmptyBorder(9, 10, 9, 10)
         ));
         strip.setLayout(new GridLayout(1, 4, 8, 0));
         String[][] steps = new String[][]{
            {"1", "面板设定", "指定个体与时间维度"},
            {"2", "选择变量", "选择因变量与解释变量"},
            {"3", "估计选项", "模型与标准误设置"},
            {"4", "预览运行", "预览命令并运行估计"}
         };
         for (int i = 0; i < steps.length; i++) {
            JPanel p = new JPanel(new BorderLayout(6, 0));
            p.setOpaque(false);
            p.setMinimumSize(new Dimension(0, 0));
            JLabel n = new JLabel(steps[i][0], SwingConstants.CENTER);
            n.setOpaque(true);
            n.setBackground(i == 0 ? new Color(47, 111, 228) : new Color(239, 243, 248));
            n.setForeground(i == 0 ? Color.WHITE : new Color(75, 88, 108));
            n.setPreferredSize(new Dimension(24, 24));
            n.setMinimumSize(new Dimension(24, 24));
            n.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(i == 0 ? new Color(47, 111, 228) : new Color(225, 231, 239), 12));
            p.add(n, BorderLayout.WEST);
            JLabel label = new JLabel("<html><b>" + html(steps[i][1]) + "</b></html>");
            label.setForeground(TEXT);
            label.setFont(label.getFont().deriveFont(10.5F));
            label.setToolTipText(steps[i][2]);
            label.setMinimumSize(new Dimension(0, 0));
            p.add(label, BorderLayout.CENTER);
            strip.add(p);
         }
         strip.setPreferredSize(new Dimension(0, 52));
         strip.setMinimumSize(new Dimension(0, 52));
         strip.setMaximumSize(new Dimension(Integer.MAX_VALUE, 52));
         return strip;
      }

      private List<String> xtregAvailableVariables() {
         if (this.previewMode) {
            return Arrays.asList("make", "price", "mpg", "rep78", "headroom", "trunk", "weight", "length", "turn", "displacement", "gear_ratio", "foreign");
         }
         return HxWorkbench.StataBridge.variableNames();
      }

      private void refreshXtregVariableControls() {
         if (!"xtreg".equals(this.currentCommand)
            || this.xtregPanelVar == null || this.xtregTimeVar == null
            || this.xtregDepVar == null || this.xtregIndepList == null) return;

         List<String> vars = this.xtregAvailableVariables();
         boolean oldRebuilding = this.rebuilding;
         this.rebuilding = true;
         replaceComboItems(this.xtregPanelVar, vars);
         replaceComboItems(this.xtregTimeVar, vars);
         replaceComboItems(this.xtregDepVar, vars);
         replaceListItems(this.xtregIndepList, vars);
         this.rebuilding = oldRebuilding;
         if (!this.rebuilding && this.xtregPreviewUpdater != null) this.xtregPreviewUpdater.run();
      }

      private void installDataHeaderDragSupport() {''',
    'xtreg step strip and refresh helpers'
)

# ---- patch xtreg page itself ----
start = s.find('      private void showXtregWizardPageV130() {\n')
end = s.find('      private void openCommandPage(String var1) {\n', start)
if start < 0 or end < 0:
    raise SystemExit('missing xtreg wizard segment')
seg = s[start:end]
seg = seg.replace('         this.setWorkspaceBreadcrumb("首页  /  统计  /  纵向/面板数据  /  xtreg");', '         this.setWorkspaceBreadcrumb("统计  >  纵向/面板数据  >  xtreg");', 1)
seg = seg.replace('         List<String> vars = HxWorkbench.StataBridge.variableNames();', '         List<String> vars = this.xtregAvailableVariables();', 1)
seg = seg.replace(
    '''         JComboBox<String> panelVar = new JComboBox<>(choices);
         JComboBox<String> timeVar = new JComboBox<>(choices);
         JComboBox<String> dep = new JComboBox<>(choices);
         DefaultListModel<String> indepModel = new DefaultListModel<>();
         for (String v : vars) indepModel.addElement(v);
         JList<String> indep = new JList<>(indepModel);
''',
    '''         this.xtregPanelVar = new JComboBox<>(choices);
         this.xtregTimeVar = new JComboBox<>(choices);
         this.xtregDepVar = new JComboBox<>(choices);
         DefaultListModel<String> indepModel = new DefaultListModel<>();
         for (String v : vars) indepModel.addElement(v);
         this.xtregIndepList = new JList<>(indepModel);
         JComboBox<String> panelVar = this.xtregPanelVar;
         JComboBox<String> timeVar = this.xtregTimeVar;
         JComboBox<String> dep = this.xtregDepVar;
         JList<String> indep = this.xtregIndepList;
''',
    1
)
seg = seg.replace(
    '         indep.setVisibleRowCount(4);\n',
    '         indep.setVisibleRowCount(4);\n         panelVar.setMinimumSize(new Dimension(0, 30));\n         timeVar.setMinimumSize(new Dimension(0, 30));\n         dep.setMinimumSize(new Dimension(0, 30));\n',
    1
)
seg = seg.replace(
    '         commandPreviewScroll.setPreferredSize(new Dimension(640, 62));\n',
    '         commandPreviewScroll.setPreferredSize(new Dimension(100, 62));\n         commandPreviewScroll.setMinimumSize(new Dimension(0, 62));\n',
    1
)
seg = seg.replace(
    '         panelVar.addActionListener(e -> update.run());\n         timeVar.addActionListener(e -> update.run());\n         dep.addActionListener(e -> update.run());\n         indep.addListSelectionListener(e -> { if (!e.getValueIsAdjusting()) update.run(); });\n         for (JRadioButton b : Arrays.asList(fe, re, be, pa)) b.addActionListener(e -> update.run());\n         se.addActionListener(e -> update.run());\n',
    '         this.xtregPreviewUpdater = update;\n         panelVar.addActionListener(e -> { if (!this.rebuilding) update.run(); });\n         timeVar.addActionListener(e -> { if (!this.rebuilding) update.run(); });\n         dep.addActionListener(e -> { if (!this.rebuilding) update.run(); });\n         indep.addListSelectionListener(e -> { if (!this.rebuilding && !e.getValueIsAdjusting()) update.run(); });\n         for (JRadioButton b : Arrays.asList(fe, re, be, pa)) b.addActionListener(e -> { if (!this.rebuilding) update.run(); });\n         se.addActionListener(e -> { if (!this.rebuilding) update.run(); });\n',
    1
)
seg = seg.replace('new JLabel("个体变量（面板 ID）")', 'new JLabel("<html>个体变量（面板 ID） <span style=\'color:#2f6fe4\'>· 可拖入</span></html>")', 1)
seg = seg.replace('new JLabel("时间变量")', 'new JLabel("<html>时间变量 <span style=\'color:#2f6fe4\'>· 可拖入</span></html>")', 1)
seg = seg.replace('new JLabel("因变量（Y）")', 'new JLabel("<html>因变量（Y） <span style=\'color:#2f6fe4\'>· 可拖入</span></html>")', 1)
seg = seg.replace('new JLabel("解释变量（X，可多选）")', 'new JLabel("<html>解释变量（X，可多选） <span style=\'color:#2f6fe4\'>· 可拖入</span></html>")', 1)
seg = seg.replace('tip2.add(new JLabel("提示：按 Ctrl / Shift 可多选解释变量。"));', 'tip2.add(new JLabel("提示：可直接把右侧数据表表头拖入；列表仍支持 Ctrl / Shift 多选。"));', 1)
seg = seg.replace(
    '         this.formPanel.repaint();\n         this.formScroll.getVerticalScrollBar().setValue(0);\n         this.statusLabel.setText("已进入 xtreg 分步向导：面板设定 → 选择变量 → 估计选项 → 预览并运行。");\n',
    '         this.formPanel.repaint();\n         this.formScroll.getVerticalScrollBar().setValue(0);\n         if (!this.previewMode) {\n            long n = Data.getObsTotal();\n            int k = Data.getVarCount();\n            if (n > 0L && k > 0) this.dataLabel.setText(n + " 行 × " + k + " 列 | 拖动表头变量可直接填入左侧变量框");\n         }\n         this.statusLabel.setText("xtreg：可点击选择变量，也可直接从右侧表头拖入对应变量框。");\n',
    1
)
s = s[:start] + seg + s[end:]

# ---- refresh xtreg controls when dataset is loaded/refreshed while page stays open ----
replace_once(
    '         this.dataModel.reload();\n         this.refreshVariableControls();\n',
    '         this.dataModel.reload();\n         this.refreshVariableControls();\n         this.refreshXtregVariableControls();\n',
    'refresh xtreg controls with dataset'
)
replace_once(
    '         this.dataLabel.setText(var2 != 0L && var4 != 0 ? var2 + " 行 × " + var4 + " 列 | 表格只读，可横向和纵向滚动" : "尚未载入数据");\n',
    '         String dataHint = "xtreg".equals(this.currentCommand) ? " | 拖动表头变量可直接填入左侧变量框" : " | 表格只读，可横向和纵向滚动";\n         this.dataLabel.setText(var2 != 0L && var4 != 0 ? var2 + " 行 × " + var4 + " 列" + dataHint : "尚未载入数据");\n',
    'contextual data hint'
)

java.write_text(s, encoding='utf-8')

# ---- package versions ----
ado = root / 'hxempirical.ado'
a = ado.read_text(encoding='utf-8')
a = a.replace('*! hxempirical 1.3.1  13aug2026', '*! hxempirical 1.3.2  13aug2026', 1)
a = a.replace('display as text "版本：" as result "1.3.1"', 'display as text "版本：" as result "1.3.2"', 1)
a = a.replace('return local version "1.3.1"', 'return local version "1.3.2"', 1)
ado.write_text(a, encoding='utf-8')

pkg = root / 'hxempirical.pkg'
p = pkg.read_text(encoding='utf-8')
p = p.replace('d Version 1.3.1', 'd Version 1.3.2', 1)
pkg.write_text(p, encoding='utf-8')

print('UI audit patch v1.3.2 applied')
