from pathlib import Path

root = Path('.')
java = root / 'src/main/java/com/hexie/stata/HxWorkbench.java'
s = java.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str):
    global s
    if old not in s:
        raise SystemExit(f'missing marker: {label}')
    s = s.replace(old, new, 1)

s = s.replace('public static final String VERSION = "1.3.0";', 'public static final String VERSION = "1.3.1";', 1)
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.3.0");', 'SFIToolkit.displayln("HxWorkbench 1.3.1");', 1)

replace_once(
    'import java.awt.datatransfer.StringSelection;\n',
    'import java.awt.datatransfer.DataFlavor;\nimport java.awt.datatransfer.StringSelection;\nimport java.awt.datatransfer.Transferable;\n',
    'datatransfer imports'
)
replace_once(
    'import javax.swing.JToggleButton;\n',
    'import javax.swing.JToggleButton;\nimport javax.swing.TransferHandler;\n',
    'TransferHandler import'
)

replace_once(
    '      private final Map<String, JButton> sidebarButtons = new LinkedHashMap<>();\n',
    '      private final Map<String, JButton> sidebarButtons = new LinkedHashMap<>();\n'
    '      private JPanel sidebarPanel;\n'
    '      private JPanel sidebarBottomPanel;\n'
    '      private JButton sidebarToggleButton;\n'
    '      private boolean sidebarCollapsed = false;\n'
    '      private String draggedDataVariable = "";\n',
    'sidebar fields'
)

replace_once(
    '         this.sharedDataInspector = this.buildDataContainer();\n'
    '         this.commandDataSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, this.buildCommandContainer(), this.sharedDataInspector);\n'
    '         this.commandDataSplit.setResizeWeight(1.0);\n'
    '         this.commandDataSplit.setContinuousLayout(true);\n'
    '         this.commandDataSplit.setBorder(null);\n'
    '         this.commandDataSplit.setDividerSize(8);\n'
    '         this.commandDataSplit.setBackground(APP_BG);\n',
    '         this.sharedDataInspector = this.buildDataContainer();\n'
    '         this.sharedDataInspector.setMinimumSize(new Dimension(260, 0));\n'
    '         JComponent commandPane = this.buildCommandContainer();\n'
    '         commandPane.setMinimumSize(new Dimension(0, 0));\n'
    '         this.commandDataSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, commandPane, this.sharedDataInspector);\n'
    '         this.commandDataSplit.setResizeWeight(0.60);\n'
    '         this.commandDataSplit.setContinuousLayout(true);\n'
    '         this.commandDataSplit.setOneTouchExpandable(true);\n'
    '         this.commandDataSplit.setBorder(null);\n'
    '         this.commandDataSplit.setDividerSize(8);\n'
    '         this.commandDataSplit.setBackground(APP_BG);\n',
    'responsive split pane'
)

replace_once(
    '         sidebar.setPreferredSize(new Dimension(205, 0));\n',
    '         sidebar.setPreferredSize(new Dimension(205, 0));\n'
    '         this.sidebarPanel = sidebar;\n',
    'sidebar host'
)
replace_once(
    '         sidebar.add(nav, BorderLayout.NORTH);\n',
    '         JPanel sidebarTop = new JPanel(new BorderLayout());\n'
    '         sidebarTop.setOpaque(false);\n'
    '         JPanel collapseLine = new JPanel(new FlowLayout(FlowLayout.RIGHT, 6, 6));\n'
    '         collapseLine.setOpaque(false);\n'
    '         this.sidebarToggleButton = new JButton("«");\n'
    '         this.sidebarToggleButton.setToolTipText("收起左侧导航");\n'
    '         this.sidebarToggleButton.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(247, 250, 254), new Color(239, 244, 250), TEXT, SURFACE));\n'
    '         this.sidebarToggleButton.setBorder(new EmptyBorder(5, 9, 5, 9));\n'
    '         this.sidebarToggleButton.setFocusPainted(false);\n'
    '         this.sidebarToggleButton.setContentAreaFilled(false);\n'
    '         this.sidebarToggleButton.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));\n'
    '         this.sidebarToggleButton.addActionListener(e -> this.toggleSidebarCollapsed());\n'
    '         collapseLine.add(this.sidebarToggleButton);\n'
    '         sidebarTop.add(collapseLine, BorderLayout.NORTH);\n'
    '         sidebarTop.add(nav, BorderLayout.CENTER);\n'
    '         sidebar.add(sidebarTop, BorderLayout.NORTH);\n',
    'sidebar collapse row'
)
replace_once(
    '         sidebar.add(bottom, BorderLayout.SOUTH);\n'
    '         this.setSidebarActive("home");\n'
    '         return sidebar;\n'
    '      }\n\n'
    '      private JButton sidebarButton(String key, String glyph, String label, Runnable action) {\n'
    '         JButton button = new JButton("<html><b>" + html(label) + "</b></html>");\n'
    '         button.putClientProperty("hx.sidebar.key", key);\n',
    '         this.sidebarBottomPanel = bottom;\n'
    '         sidebar.add(bottom, BorderLayout.SOUTH);\n'
    '         this.setSidebarActive("home");\n'
    '         this.applySidebarCollapsedState();\n'
    '         return sidebar;\n'
    '      }\n\n'
    '      private void toggleSidebarCollapsed() {\n'
    '         this.sidebarCollapsed = !this.sidebarCollapsed;\n'
    '         this.applySidebarCollapsedState();\n'
    '      }\n\n'
    '      private void applySidebarCollapsedState() {\n'
    '         if (this.sidebarPanel == null) return;\n'
    '         int width = this.sidebarCollapsed ? 58 : 205;\n'
    '         this.sidebarPanel.setPreferredSize(new Dimension(width, 0));\n'
    '         this.sidebarPanel.setMinimumSize(new Dimension(width, 0));\n'
    '         if (this.sidebarBottomPanel != null) this.sidebarBottomPanel.setVisible(!this.sidebarCollapsed);\n'
    '         if (this.sidebarToggleButton != null) {\n'
    '            this.sidebarToggleButton.setText(this.sidebarCollapsed ? "»" : "«");\n'
    '            this.sidebarToggleButton.setToolTipText(this.sidebarCollapsed ? "展开左侧导航" : "收起左侧导航");\n'
    '         }\n'
    '         for (JButton button : this.sidebarButtons.values()) {\n'
    '            String label = Objects.toString(button.getClientProperty("hx.sidebar.label"), "");\n'
    '            String glyph = Objects.toString(button.getClientProperty("hx.sidebar.glyph"), "");\n'
    '            String compact = glyph.isBlank() ? (label.isBlank() ? "•" : label.substring(0, 1)) : glyph;\n'
    '            button.setText(this.sidebarCollapsed ? "<html><b>" + html(compact) + "</b></html>" : "<html><b>" + html(label) + "</b></html>");\n'
    '            button.setHorizontalAlignment(this.sidebarCollapsed ? SwingConstants.CENTER : SwingConstants.LEFT);\n'
    '            button.setBorder(new EmptyBorder(11, this.sidebarCollapsed ? 6 : 14, 11, this.sidebarCollapsed ? 6 : 14));\n'
    '            button.setToolTipText(this.sidebarCollapsed ? label : null);\n'
    '         }\n'
    '         this.sidebarPanel.revalidate();\n'
    '         this.sidebarPanel.repaint();\n'
    '         Container parent = this.sidebarPanel.getParent();\n'
    '         if (parent != null) { parent.revalidate(); parent.repaint(); }\n'
    '         SwingUtilities.invokeLater(this::applyDividerRatios);\n'
    '      }\n\n'
    '      private JButton sidebarButton(String key, String glyph, String label, Runnable action) {\n'
    '         JButton button = new JButton("<html><b>" + html(label) + "</b></html>");\n'
    '         button.putClientProperty("hx.sidebar.key", key);\n'
    '         button.putClientProperty("hx.sidebar.label", label);\n'
    '         button.putClientProperty("hx.sidebar.glyph", glyph);\n',
    'sidebar collapse behavior'
)

s = s.replace('JLabel version = new JLabel("版本：1.2.7");', 'JLabel version = new JLabel("版本：" + VERSION);', 1)

s = s.replace('this.dataTable.getTableHeader().setReorderingAllowed(true);', 'this.dataTable.getTableHeader().setReorderingAllowed(false);', 1)
replace_once(
    '         this.dataTable.getTableHeader().setPreferredSize(new Dimension(0, 28));\n',
    '         this.dataTable.getTableHeader().setPreferredSize(new Dimension(0, 28));\n'
    '         this.installDataHeaderDragSupport();\n',
    'header drag hook'
)

marker = '      private void showXtregWizardPageV130() {\n'
if marker not in s:
    raise SystemExit('missing marker: xtreg wizard')
helpers = r'''      private void installDataHeaderDragSupport() {
         final javax.swing.table.JTableHeader header = this.dataTable.getTableHeader();
         header.setReorderingAllowed(false);
         header.setCursor(Cursor.getPredefinedCursor(Cursor.HAND_CURSOR));
         header.setToolTipText("拖动变量名到左侧变量输入框，可直接完成选择");
         header.setTransferHandler(new TransferHandler() {
            @Override
            protected Transferable createTransferable(JComponent c) {
               return WorkbenchFrame.this.draggedDataVariable == null || WorkbenchFrame.this.draggedDataVariable.isBlank()
                  ? null : new StringSelection(WorkbenchFrame.this.draggedDataVariable);
            }

            @Override
            public int getSourceActions(JComponent c) {
               return COPY;
            }
         });

         MouseAdapter dragger = new MouseAdapter() {
            private boolean started;

            @Override
            public void mousePressed(MouseEvent e) {
               int viewColumn = header.columnAtPoint(e.getPoint());
               this.started = false;
               if (viewColumn >= 0) {
                  WorkbenchFrame.this.draggedDataVariable = WorkbenchFrame.this.dataTable.getColumnName(viewColumn);
                  WorkbenchFrame.this.dataTable.setColumnSelectionInterval(viewColumn, viewColumn);
               } else {
                  WorkbenchFrame.this.draggedDataVariable = "";
               }
            }

            @Override
            public void mouseDragged(MouseEvent e) {
               if (!this.started && WorkbenchFrame.this.draggedDataVariable != null && !WorkbenchFrame.this.draggedDataVariable.isBlank()) {
                  this.started = true;
                  header.getTransferHandler().exportAsDrag(header, e, TransferHandler.COPY);
               }
            }

            @Override
            public void mouseReleased(MouseEvent e) {
               this.started = false;
               WorkbenchFrame.this.draggedDataVariable = "";
            }
         };
         header.addMouseListener(dragger);
         header.addMouseMotionListener(dragger);
      }

      private void enableVariableDrop(JComboBox<String> target, String role) {
         target.setToolTipText("可从右侧数据表表头拖入变量：" + role);
         target.setTransferHandler(new TransferHandler() {
            @Override
            public boolean canImport(TransferSupport support) {
               return support.isDataFlavorSupported(DataFlavor.stringFlavor);
            }

            @Override
            public boolean importData(TransferSupport support) {
               if (!canImport(support)) return false;
               try {
                  String variable = ((String)support.getTransferable().getTransferData(DataFlavor.stringFlavor)).trim();
                  for (int i = 0; i < target.getItemCount(); i++) {
                     if (variable.equals(target.getItemAt(i))) {
                        target.setSelectedIndex(i);
                        WorkbenchFrame.this.statusLabel.setText("已将变量 " + variable + " 拖入“" + role + "”。");
                        return true;
                     }
                  }
               } catch (Exception ex) {
                  WorkbenchFrame.this.statusLabel.setText("拖入变量失败：" + ex.getMessage());
               }
               return false;
            }
         });
      }

      private void enableVariableDrop(JList<String> target, String role) {
         target.setToolTipText("可从右侧数据表表头拖入变量：" + role);
         target.setTransferHandler(new TransferHandler() {
            @Override
            public boolean canImport(TransferSupport support) {
               return support.isDataFlavorSupported(DataFlavor.stringFlavor);
            }

            @Override
            public boolean importData(TransferSupport support) {
               if (!canImport(support)) return false;
               try {
                  String variable = ((String)support.getTransferable().getTransferData(DataFlavor.stringFlavor)).trim();
                  ListModel<String> model = target.getModel();
                  for (int i = 0; i < model.getSize(); i++) {
                     if (variable.equals(model.getElementAt(i))) {
                        target.addSelectionInterval(i, i);
                        target.ensureIndexIsVisible(i);
                        WorkbenchFrame.this.statusLabel.setText("已将变量 " + variable + " 拖入“" + role + "”。");
                        return true;
                     }
                  }
               } catch (Exception ex) {
                  WorkbenchFrame.this.statusLabel.setText("拖入变量失败：" + ex.getMessage());
               }
               return false;
            }
         });
      }

'''
s = s.replace(marker, helpers + marker, 1)

replace_once(
    '         JList<String> indep = new JList<>(indepModel);\n'
    '         indep.setSelectionMode(javax.swing.ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);\n'
    '         indep.setVisibleRowCount(4);\n'
    '         JScrollPane indepScroll = new JScrollPane(indep);\n'
    '         indepScroll.setPreferredSize(new Dimension(420, 82));\n'
    '         indepScroll.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 8));\n',
    '         JList<String> indep = new JList<>(indepModel);\n'
    '         indep.setSelectionMode(javax.swing.ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);\n'
    '         indep.setVisibleRowCount(4);\n'
    '         this.enableVariableDrop(panelVar, "个体变量（面板 ID）");\n'
    '         this.enableVariableDrop(timeVar, "时间变量");\n'
    '         this.enableVariableDrop(dep, "因变量（Y）");\n'
    '         this.enableVariableDrop(indep, "解释变量（X，可多选）");\n'
    '         JScrollPane indepScroll = new JScrollPane(indep);\n'
    '         indepScroll.setPreferredSize(new Dimension(220, 82));\n'
    '         indepScroll.setMinimumSize(new Dimension(0, 82));\n'
    '         indepScroll.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 8));\n',
    'xtreg drop targets'
)

s = s.replace('step1.add(advice1, BorderLayout.EAST);', 'step1.add(advice1, BorderLayout.SOUTH);', 1)
s = s.replace('step2.add(tip2, BorderLayout.EAST);', 'step2.add(tip2, BorderLayout.SOUTH);', 1)
s = s.replace('step3.add(tip3, BorderLayout.EAST);', 'step3.add(tip3, BorderLayout.SOUTH);', 1)
s = s.replace('JPanel models = new JPanel(new GridLayout(1, 4, 8, 0)); models.setOpaque(false);',
              'JPanel models = new JPanel(new GridLayout(2, 2, 8, 6)); models.setOpaque(false);', 1)

replace_once(
    '         JScrollPane syntaxScroll = softScroll(syntax); syntaxScroll.setPreferredSize(new Dimension(310, 72));\n'
    '         previewWrap.add(previewLeft, BorderLayout.CENTER); previewWrap.add(syntaxScroll, BorderLayout.EAST);\n',
    '         JScrollPane syntaxScroll = softScroll(syntax); syntaxScroll.setPreferredSize(new Dimension(0, 72));\n'
    '         previewWrap.add(previewLeft, BorderLayout.CENTER); previewWrap.add(syntaxScroll, BorderLayout.SOUTH);\n',
    'xtreg preview responsive'
)

replace_once(
    '         this.formPanel.revalidate(); this.formPanel.repaint(); this.formScroll.getVerticalScrollBar().setValue(0);\n'
    '         this.rebuilding = false;\n'
    '         update.run();\n',
    '         this.formPanel.setMinimumSize(new Dimension(0, 0));\n'
    '         this.formPanel.revalidate(); this.formPanel.repaint(); this.formScroll.getVerticalScrollBar().setValue(0);\n'
    '         this.rebuilding = false;\n'
    '         update.run();\n',
    'xtreg form shrink'
)

replace_once(
    '            if (total > 0) {\n'
    '               int inspector = Math.max(360, Math.min(410, total / 3));\n'
    '               this.commandDataSplit.setDividerLocation(Math.max(560, total - inspector));\n'
    '            }\n',
    '            if (total > 0) {\n'
    '               int minInspector = total < 980 ? 270 : 320;\n'
    '               int inspector = Math.max(minInspector, Math.min(520, (int)Math.round(total * 0.43)));\n'
    '               int minCommand = total < 980 ? 390 : 480;\n'
    '               int divider = Math.max(minCommand, total - inspector);\n'
    '               divider = Math.min(divider, Math.max(minCommand, total - 250));\n'
    '               this.commandDataSplit.setDividerLocation(Math.max(0, divider));\n'
    '            }\n',
    'responsive divider ratio'
)

java.write_text(s, encoding='utf-8')

for path in [root / 'hxempirical.ado', root / 'hxempirical.pkg']:
    text = path.read_text(encoding='utf-8')
    text = text.replace('1.3.0', '1.3.1')
    path.write_text(text, encoding='utf-8')

print('HX_INTERACTION_UI_PATCH_OK')
