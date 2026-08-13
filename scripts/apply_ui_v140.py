from pathlib import Path
import re

p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')

# Version
assert 'public static final String VERSION = "1.3.9";' in s
s = s.replace('public static final String VERSION = "1.3.9";', 'public static final String VERSION = "1.4.0";', 1)
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.3.9");', 'SFIToolkit.displayln("HxWorkbench 1.4.0");', 1)

# Shared inspector fields
field_anchor = '      private final JLabel rightPaneTitle = new JLabel("当前数据");\n'
assert field_anchor in s
field_add = '''      private final JLabel rightPaneTitle = new JLabel("当前数据");
      private final DefaultTableModel inspectorVariableModel = new DefaultTableModel(new String[]{"名称", "标签"}, 0) {
         @Override
         public boolean isCellEditable(int row, int column) { return false; }
      };
      private final JTable inspectorVariableTable = new JTable(this.inspectorVariableModel);
      private final JTextField inspectorVariableFilter = new JTextField();
      private final JLabel inspectorRoleLabel = new JLabel("当前模型角色：未使用");
'''
s = s.replace(field_anchor, field_add, 1)

split_anchor = '      private JSplitPane dataSummarySplit;\n'
assert split_anchor in s
s = s.replace(split_anchor, split_anchor + '      private JSplitPane inspectorLowerSplit;\n', 1)

# Build data tab as Current Data + Variable Window + Property Window.
old_data_block = '''         JPanel var2 = new JPanel(new BorderLayout());
         var2.setBackground(SURFACE);
         this.variableTabs = new JTabbedPane();
         this.variableTabs.addTab("变量摘要", softScroll(this.summaryArea));
         this.variableTabs.addTab("分布图", this.histogram);
         this.variableTabs.setBackground(SURFACE);
         this.variableTabs.setMinimumSize(new Dimension(0, 0));
         var1.setMinimumSize(new Dimension(0, 0));
         this.dataSummarySplit = new JSplitPane(0, var1, this.variableTabs);
         this.dataSummarySplit.setResizeWeight(0.73);
         this.dataSummarySplit.setContinuousLayout(true);
         this.dataSummarySplit.setMinimumSize(new Dimension(0, 0));
         this.dataSummarySplit.setBorder(null);
         this.dataSummarySplit.setDividerSize(1);
         this.currentDataCards.setBackground(SURFACE);
         this.currentDataCards.add(this.dataSummarySplit, "table");
         this.currentDataCards.add(this.buildEmptyDataPanel(), "empty");
         var2.add(this.currentDataCards, "Center");
         this.dataTabs.addTab("数据", var2);
'''
assert old_data_block in s
new_data_block = '''         JPanel var2 = new JPanel(new BorderLayout());
         var2.setBackground(SURFACE);
         this.variableTabs = new JTabbedPane();
         this.variableTabs.addTab("变量摘要", softScroll(this.summaryArea));
         this.variableTabs.addTab("分布图", this.histogram);
         this.variableTabs.setBackground(SURFACE);
         this.variableTabs.setMinimumSize(new Dimension(0, 0));
         var1.setMinimumSize(new Dimension(0, 0));
         this.currentDataCards.setBackground(SURFACE);
         this.currentDataCards.add(var1, "table");
         this.currentDataCards.add(this.buildEmptyDataPanel(), "empty");

         JComponent variableWindow = this.buildVariableInspectorPanel();
         JComponent propertyWindow = this.buildPropertyInspectorPanel();
         this.inspectorLowerSplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT, variableWindow, propertyWindow);
         this.inspectorLowerSplit.setResizeWeight(0.52);
         this.inspectorLowerSplit.setContinuousLayout(true);
         this.inspectorLowerSplit.setMinimumSize(new Dimension(0, 0));
         this.inspectorLowerSplit.setBorder(null);
         this.inspectorLowerSplit.setDividerSize(5);

         this.dataSummarySplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT, this.currentDataCards, this.inspectorLowerSplit);
         this.dataSummarySplit.setResizeWeight(0.28);
         this.dataSummarySplit.setContinuousLayout(true);
         this.dataSummarySplit.setMinimumSize(new Dimension(0, 0));
         this.dataSummarySplit.setBorder(null);
         this.dataSummarySplit.setDividerSize(5);
         var2.add(this.dataSummarySplit, BorderLayout.CENTER);
         this.dataTabs.addTab("数据", var2);
         SwingUtilities.invokeLater(() -> {
            if (this.dataSummarySplit != null) this.dataSummarySplit.setDividerLocation(0.28);
            if (this.inspectorLowerSplit != null) this.inspectorLowerSplit.setDividerLocation(0.52);
         });
'''
s = s.replace(old_data_block, new_data_block, 1)

# Add inspector helper methods before buildDataContainer.
method_anchor = '      private JComponent buildDataContainer() {'
assert method_anchor in s
helpers = r'''      private JComponent buildVariableInspectorPanel() {
         JPanel root = new JPanel(new BorderLayout(0, 7));
         root.setBackground(SURFACE);
         root.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220, 227, 237), 9),
            new EmptyBorder(9, 10, 9, 10)
         ));

         JPanel header = new JPanel(new BorderLayout(8, 0));
         header.setOpaque(false);
         JLabel title = new JLabel("变量窗口");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD, 13.0F));
         JLabel hint = new JLabel("拖到左侧变量框");
         hint.setForeground(MUTED);
         hint.setFont(hint.getFont().deriveFont(9.5F));
         header.add(title, BorderLayout.WEST);
         header.add(hint, BorderLayout.EAST);

         this.inspectorVariableFilter.putClientProperty("JTextField.placeholderText", "过滤变量（名称 / 标签）");
         this.inspectorVariableFilter.setToolTipText("按变量名或变量标签过滤；可直接拖动变量到左侧参数框");
         this.inspectorVariableTable.setRowHeight(24);
         this.inspectorVariableTable.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
         this.inspectorVariableTable.setFillsViewportHeight(true);
         this.inspectorVariableTable.setShowVerticalLines(false);
         this.inspectorVariableTable.setGridColor(new Color(235, 239, 245));
         this.inspectorVariableTable.getTableHeader().setReorderingAllowed(false);
         this.inspectorVariableTable.getTableHeader().setBackground(new Color(248, 250, 253));
         this.inspectorVariableTable.getColumnModel().getColumn(0).setPreferredWidth(118);
         this.inspectorVariableTable.getColumnModel().getColumn(1).setPreferredWidth(210);
         this.installInspectorVariableDragSupport();

         this.inspectorVariableFilter.getDocument().addDocumentListener(new HxWorkbench.WorkbenchFrame.SimpleDocumentListener(this::refreshInspectorVariables));
         this.inspectorVariableTable.getSelectionModel().addListSelectionListener(e -> {
            if (!e.getValueIsAdjusting()) this.syncInspectorSelectionFromVariableWindow();
         });

         JPanel top = new JPanel(new BorderLayout(0, 6));
         top.setOpaque(false);
         top.add(header, BorderLayout.NORTH);
         top.add(this.inspectorVariableFilter, BorderLayout.SOUTH);
         root.add(top, BorderLayout.NORTH);
         root.add(softScroll(this.inspectorVariableTable), BorderLayout.CENTER);
         return root;
      }

      private JComponent buildPropertyInspectorPanel() {
         JPanel root = new JPanel(new BorderLayout(0, 7));
         root.setBackground(SURFACE);
         root.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(220, 227, 237), 9),
            new EmptyBorder(9, 10, 9, 10)
         ));
         JPanel header = new JPanel(new BorderLayout(8, 2));
         header.setOpaque(false);
         JLabel title = new JLabel("属性窗口");
         title.setForeground(TEXT);
         title.setFont(title.getFont().deriveFont(Font.BOLD, 13.0F));
         this.inspectorRoleLabel.setForeground(ACCENT);
         this.inspectorRoleLabel.setFont(this.inspectorRoleLabel.getFont().deriveFont(Font.BOLD, 10.0F));
         header.add(title, BorderLayout.WEST);
         header.add(this.inspectorRoleLabel, BorderLayout.SOUTH);
         root.add(header, BorderLayout.NORTH);
         root.add(this.variableTabs, BorderLayout.CENTER);
         return root;
      }

      private void refreshInspectorVariables() {
         if (this.inspectorVariableModel == null) return;
         String selectedName = this.selectedInspectorVariable();
         String q = this.inspectorVariableFilter.getText() == null ? "" : this.inspectorVariableFilter.getText().trim().toLowerCase(Locale.ROOT);
         this.inspectorVariableModel.setRowCount(0);
         List<String> names = new ArrayList<>();
         if (this.previewMode && this.dataModel.getColumnCount() > 0) {
            for (int i = 0; i < this.dataModel.getColumnCount(); i++) names.add(this.dataModel.getColumnName(i));
         } else {
            names.addAll(HxWorkbench.StataBridge.variableNames());
         }
         for (String name : names) {
            int index = this.previewMode ? -1 : HxWorkbench.safe(() -> Data.getVarIndex(name), -1);
            String label = index > 0 ? HxWorkbench.safe(() -> Data.getVarLabel(index), "") : "";
            String hay = (name + " " + label).toLowerCase(Locale.ROOT);
            if (q.isBlank() || hay.contains(q)) this.inspectorVariableModel.addRow(new Object[]{name, label});
         }
         if (!selectedName.isBlank()) {
            for (int r = 0; r < this.inspectorVariableModel.getRowCount(); r++) {
               if (selectedName.equals(Objects.toString(this.inspectorVariableModel.getValueAt(r, 0), ""))) {
                  this.inspectorVariableTable.setRowSelectionInterval(r, r);
                  break;
               }
            }
         } else if (this.inspectorVariableModel.getRowCount() > 0) {
            this.inspectorVariableTable.setRowSelectionInterval(0, 0);
         }
      }

      private String selectedInspectorVariable() {
         int row = this.inspectorVariableTable.getSelectedRow();
         if (row >= 0 && row < this.inspectorVariableModel.getRowCount()) {
            return Objects.toString(this.inspectorVariableModel.getValueAt(row, 0), "").trim();
         }
         int viewCol = this.dataTable.getSelectedColumn();
         if (viewCol >= 0) return this.dataTable.getColumnName(viewCol);
         return "";
      }

      private void syncInspectorSelectionFromVariableWindow() {
         String variable = this.selectedInspectorVariable();
         if (variable.isBlank()) {
            this.refreshInspectorRole();
            return;
         }
         for (int view = 0; view < this.dataTable.getColumnCount(); view++) {
            if (variable.equals(this.dataTable.getColumnName(view))) {
               this.dataTable.setColumnSelectionInterval(view, view);
               if (this.dataTable.getRowCount() > 0) this.dataTable.setRowSelectionInterval(0, 0);
               break;
            }
         }
         if (this.previewMode && HxWorkbench.safe(() -> Data.getVarIndex(variable), -1) <= 0) {
            this.summaryArea.setText("变量：" + variable + "\n\n预览模式下仅展示变量结构；载入真实 Stata 数据后显示类型、标签、缺失值和描述统计。");
            this.histogram.setValues(Collections.emptyList(), variable);
            this.refreshInspectorRole();
         } else {
            this.updateSelectedColumnSummary();
         }
      }

      private void installInspectorVariableDragSupport() {
         this.inspectorVariableTable.setTransferHandler(new TransferHandler() {
            @Override
            protected Transferable createTransferable(JComponent c) {
               String variable = WorkbenchFrame.this.selectedInspectorVariable();
               return variable.isBlank() ? null : new StringSelection(variable);
            }
            @Override public int getSourceActions(JComponent c) { return COPY; }
         });
         if (!GraphicsEnvironment.isHeadless()) this.inspectorVariableTable.setDragEnabled(true);
         this.inspectorVariableTable.setToolTipText("按住变量行拖到左侧 Y / X / 面板 ID / 时间变量框");
      }

      private String inspectorRoleFor(String variable) {
         if (variable == null || variable.isBlank()) return "未使用";
         if ("xtreg".equals(this.currentCommand)) {
            if (this.xtregPanelVar != null && variable.equals(Objects.toString(this.xtregPanelVar.getSelectedItem(), ""))) return "面板 ID";
            if (this.xtregTimeVar != null && variable.equals(Objects.toString(this.xtregTimeVar.getSelectedItem(), ""))) return "时间变量";
            if (this.xtregDepVar != null && variable.equals(Objects.toString(this.xtregDepVar.getSelectedItem(), ""))) return "因变量 Y";
            if (this.xtregIndepList != null && this.xtregIndepList.getSelectedValuesList().contains(variable)) return "解释变量 X";
         }
         if (variable.equals(selected(this.depvar))) return "因变量 Y";
         if (this.variables.getSelectedValuesList().contains(variable)) return "解释变量 X";
         if (this.absorb.getSelectedValuesList().contains(variable)) return "固定效应 FE";
         if (variable.equals(selected(this.cluster))) return "聚类变量";
         if (variable.equals(selected(this.panel))) return "面板 ID";
         if (variable.equals(selected(this.time))) return "时间变量";
         return "未使用";
      }

      private void refreshInspectorRole() {
         String variable = this.selectedInspectorVariable();
         this.inspectorRoleLabel.setText("当前模型角色：" + this.inspectorRoleFor(variable));
      }

'''
s = s.replace(method_anchor, helpers + method_anchor, 1)

# Keep variable window synchronized with dataset refresh.
refresh_anchor = '''         this.dataModel.reload();
         this.refreshVariableControls();
         this.refreshXtregVariableControls();
'''
assert refresh_anchor in s
s = s.replace(refresh_anchor, refresh_anchor + '         this.refreshInspectorVariables();\n', 1)

# Update property role whenever a data column summary changes.
summary_old = '''            this.summaryArea.setText(var3.text);
            this.summaryArea.setCaretPosition(0);
            this.histogram.setValues(var3.numericValues, var3.name);
         }
      }
'''
assert summary_old in s
summary_new = '''            this.summaryArea.setText(var3.text);
            this.summaryArea.setCaretPosition(0);
            this.histogram.setValues(var3.numericValues, var3.name);
         }
         this.refreshInspectorRole();
      }
'''
s = s.replace(summary_old, summary_new, 1)

# xtreg: selected-variable chip basket replaces the visible all-variable list.
old_indep = '''         JScrollPane indepScroll = new JScrollPane(indep);
         indepScroll.setPreferredSize(new Dimension(220, 82));
         indepScroll.setMinimumSize(new Dimension(0, 82));
         indepScroll.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 8));
'''
assert old_indep in s
new_indep = '''         JPanel chipZone = new JPanel(new BorderLayout());
         chipZone.setBackground(Color.WHITE);
         chipZone.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(190, 210, 238), 8));
         chipZone.setPreferredSize(new Dimension(220, 72));
         chipZone.setMinimumSize(new Dimension(0, 72));
         JPanel chips = new JPanel(new FlowLayout(FlowLayout.LEFT, 6, 6));
         chips.setOpaque(false);
         JLabel chipHint = new JLabel("将右侧变量拖到这里");
         chipHint.setForeground(MUTED);
         chipHint.setBorder(new EmptyBorder(9, 8, 8, 8));
         Runnable refreshChips = () -> {
            chips.removeAll();
            List<String> selectedVars = indep.getSelectedValuesList();
            if (selectedVars.isEmpty()) {
               chips.add(chipHint);
            } else {
               for (String variable : selectedVars) {
                  JButton chip = new JButton(variable + "  ×");
                  chip.setFocusPainted(false);
                  chip.setBorder(new EmptyBorder(4, 8, 4, 8));
                  chip.setBackground(ACCENT_SOFT);
                  chip.setForeground(TEXT);
                  chip.setToolTipText("点击移除 " + variable);
                  chip.addActionListener(e -> {
                     ListModel<String> model = indep.getModel();
                     for (int i = 0; i < model.getSize(); i++) {
                        if (variable.equals(model.getElementAt(i))) {
                           indep.removeSelectionInterval(i, i);
                           break;
                        }
                     }
                  });
                  chips.add(chip);
               }
            }
            chips.revalidate();
            chips.repaint();
         };
         TransferHandler xDrop = new TransferHandler() {
            @Override public boolean canImport(TransferSupport support) { return support.isDataFlavorSupported(DataFlavor.stringFlavor); }
            @Override public boolean importData(TransferSupport support) {
               if (!canImport(support)) return false;
               try {
                  String variable = ((String)support.getTransferable().getTransferData(DataFlavor.stringFlavor)).trim();
                  ListModel<String> model = indep.getModel();
                  for (int i = 0; i < model.getSize(); i++) {
                     if (variable.equals(model.getElementAt(i))) {
                        indep.addSelectionInterval(i, i);
                        WorkbenchFrame.this.statusLabel.setText("已将变量 " + variable + " 拖入“解释变量 X”。");
                        return true;
                     }
                  }
               } catch (Exception ex) {
                  WorkbenchFrame.this.statusLabel.setText("拖入变量失败：" + ex.getMessage());
               }
               return false;
            }
         };
         chipZone.setTransferHandler(xDrop);
         chips.setTransferHandler(xDrop);
         chipHint.setTransferHandler(xDrop);
         chipZone.add(chips, BorderLayout.CENTER);
         indep.addListSelectionListener(e -> { if (!e.getValueIsAdjusting()) refreshChips.run(); });
         refreshChips.run();
'''
s = s.replace(old_indep, new_indep, 1)

old_p4 = '         JPanel p4 = new JPanel(new BorderLayout(0, 5)); p4.setOpaque(false); p4.add(new JLabel("<html>解释变量（X，可多选） <span style=\'color:#2f6fe4\'>· 可拖入</span></html>"), BorderLayout.NORTH); p4.add(indepScroll, BorderLayout.CENTER);\n'
assert old_p4 in s
s = s.replace(old_p4, '         JPanel p4 = new JPanel(new BorderLayout(0, 5)); p4.setOpaque(false); p4.add(new JLabel("<html>解释变量（X，可多选） <span style=\'color:#2f6fe4\'>· 可拖入</span></html>"), BorderLayout.NORTH); p4.add(chipZone, BorderLayout.CENTER);\n', 1)

s = s.replace('提示：可直接把右侧数据表表头拖入；列表仍支持 Ctrl / Shift 多选。', '提示：优先从右侧“变量窗口”拖入；顶部数据表头也可直接拖入。', 1)
s = s.replace('xtreg：可点击选择变量，也可直接从右侧表头拖入对应变量框。', 'xtreg：右侧变量窗口是主要选变量入口；可把变量直接拖到 Y / X / 面板 ID / 时间变量。', 1)
s = s.replace('n + " 行 × " + k + " 列 | 拖动表头变量可直接填入左侧变量框"', 'n + " 行 × " + k + " 列 | 可从变量窗口或表头拖入左侧变量框"', 1)
s = s.replace('"xtreg".equals(this.currentCommand) ? " | 拖动表头变量可直接填入左侧变量框" : " | 表格只读，可横向和纵向滚动"', '"xtreg".equals(this.currentCommand) ? " | 可从变量窗口或表头拖入左侧变量框" : " | 表格只读，可横向和纵向滚动"')

# Keep role indicator live as xtreg selections change.
update_tail = '''            commandPreview.setText(shown);
            this.previewArea.setText(xt.toString());
         };
'''
assert update_tail in s
s = s.replace(update_tail, '''            commandPreview.setText(shown);
            this.previewArea.setText(xt.toString());
            this.refreshInspectorRole();
         };
''', 1)

# Responsive FE / RE / between / PA: 2x2 when wide, 1x4 when narrow.
old_models = '''         JPanel models = new JPanel(new GridLayout(4, 1, 0, 4)); models.setOpaque(false);
         models.add(fe); models.add(re); models.add(be); models.add(pa);
'''
assert old_models in s
new_models = '''         JPanel models = new JPanel(null) {
            private int columns() { return this.getWidth() >= 520 ? 2 : 1; }
            @Override public Dimension getPreferredSize() { return new Dimension(0, this.columns() == 2 ? 62 : 116); }
            @Override public Dimension getMinimumSize() { return new Dimension(0, 116); }
            @Override public void doLayout() {
               int cols = this.columns();
               int rows = cols == 2 ? 2 : 4;
               int gapX = 16, gapY = 3;
               int cellW = Math.max(0, (this.getWidth() - (cols - 1) * gapX) / cols);
               int cellH = Math.max(27, (this.getHeight() - (rows - 1) * gapY) / rows);
               Component[] items = this.getComponents();
               for (int i = 0; i < items.length; i++) {
                  int row = i / cols, col = i % cols;
                  items[i].setBounds(col * (cellW + gapX), row * (cellH + gapY), cellW, cellH);
               }
            }
         };
         models.setOpaque(false);
         models.add(fe); models.add(re); models.add(be); models.add(pa);
         models.addComponentListener(new java.awt.event.ComponentAdapter() {
            @Override public void componentResized(java.awt.event.ComponentEvent e) { models.revalidate(); }
         });
'''
s = s.replace(old_models, new_models, 1)

p.write_text(s, encoding='utf-8')

# Version files
p = Path('hxempirical.ado')
a = p.read_text(encoding='utf-8')
assert '1.3.9' in a
p.write_text(a.replace('1.3.9', '1.4.0'), encoding='utf-8')

p = Path('hxempirical.pkg')
a = p.read_text(encoding='utf-8')
assert 'd Version 1.3.9' in a
p.write_text(a.replace('d Version 1.3.9', 'd Version 1.4.0', 1), encoding='utf-8')

p = Path('hxempirical.sthlp')
a = p.read_text(encoding='utf-8')
p.write_text(a.replace('1.3.9', '1.4.0'), encoding='utf-8')

p = Path('README.md')
a = p.read_text(encoding='utf-8')
assert '**当前发布版本：1.3.9**' in a
a = a.replace('**当前发布版本：1.3.9**', '**当前发布版本：1.4.0**', 1)
a = a.replace('**上次修改时间：2026-08-13 14:42（UTC+8）**', '**上次修改时间：2026-08-13 15:05（UTC+8）**', 1)
p.write_text(a, encoding='utf-8')

print('APPLY_UI_V140_OK')
