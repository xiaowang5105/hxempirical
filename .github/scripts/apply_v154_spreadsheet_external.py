from pathlib import Path


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"missing patch anchor: {label}")
    return text.replace(old, new, 1)

src = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
s = src.read_text(encoding="utf-8")

# Release version.
s = replace_once(s, 'public static final String VERSION = "1.5.3";', 'public static final String VERSION = "1.5.4";', 'java version')

# ---------------------------------------------------------------------------
# 1) Sidebar: replace Recent/History shortcut with installed external commands.
# ---------------------------------------------------------------------------
s = replace_once(
    s,
    '         nav.add(this.sidebarButton("history", "历", "历史", () -> this.browseCommandCategory("recent", "最近任务")));',
    '         nav.add(this.sidebarButton("external", "外", "已下载外部命令", this::browseInstalledExternalCommands));',
    'sidebar history -> external',
)
s = replace_once(
    s,
    '         else if ("recent".equals(this.activeCategoryCode)) key = "history";\n         else if ("performance".equals(this.activeCategoryCode) || "test".equals(this.activeCategoryCode)) key = "settings";',
    '         else if ("external".equals(this.activeCategoryCode)) key = "external";\n         else if ("recent".equals(this.activeCategoryCode)) key = "home";\n         else if ("performance".equals(this.activeCategoryCode) || "test".equals(this.activeCategoryCode)) key = "settings";',
    'sidebar active mapping',
)

# A separate ordered catalog is used for display. Keep OPTIONAL_DEPENDENCIES intact
# because it controls run-time installation behavior for normal command pages.
anchor = '''      private static final Set<String> OPTIONAL_DEPENDENCIES = new HashSet<>(
         Arrays.asList("reghdfe", "winsor2", "ivreghdfe", "ppmlhdfe", "coefplot", "event_plot")
      );'''
replacement = anchor + '''
      private static final List<String> EXTERNAL_COMMAND_CATALOG = Arrays.asList(
         "reghdfe", "winsor2", "ivreghdfe", "ppmlhdfe", "oneclick", "oneclick_robustness", "coefplot", "event_plot"
      );'''
s = replace_once(s, anchor, replacement, 'external catalog')

# Installed external-command browser reuses the existing command chooser/inspector.
method_anchor = '      private void browseCommandCategory(String var1, String var2) {'
external_method = '''      private void browseInstalledExternalCommands() {
         this.activeCategoryCode = "external";
         this.activeCategoryName = "已下载外部命令";
         this.activeMethodName = "已安装";
         this.rebuilding = true;
         this.commandModel.clear();
         ArrayList<String> installed = new ArrayList<>();
         if (this.previewMode) {
            installed.addAll(Arrays.asList("reghdfe", "winsor2", "ppmlhdfe", "oneclick", "coefplot"));
         } else {
            for (String command : EXTERNAL_COMMAND_CATALOG) {
               if (HxWorkbench.StataBridge.execute("quietly which " + command, false) == 0) installed.add(command);
            }
         }
         for (String command : installed) this.commandModel.addElement(command);
         this.rebuilding = false;
         this.renderCommandChooser("已下载外部命令", "", installed);
         this.chooserHint.setText(
            installed.isEmpty()
               ? "当前没有检测到工具箱已登记且 Stata 能找到的外部命令。"
               : "仅显示工具箱已登记且当前 Stata 能找到的外部命令，共 " + installed.size() + " 个。"
         );
         this.setSidebarActive("external");
         this.setBusy(false, installed.isEmpty() ? "没有检测到已安装的登记外部命令。" : "已读取当前可用的外部命令。");
      }

'''
s = replace_once(s, method_anchor, external_method + method_anchor, 'external browser method')

# External browser has no category overview level; Back/Home breadcrumb must not
# route into an empty generic category.
old_back = '''      private void handleChooserBack() {
         if (!this.chooserAtCategoryLevel
            && !this.activeCategoryCode.isBlank()
            && !"search".equals(this.activeCategoryCode)
            && !"favorites".equals(this.activeCategoryCode)
            && !"recent".equals(this.activeCategoryCode)) {
            this.browseCategoryOverview(this.activeCategoryCode);
         } else {
            this.showHomePage();
         }
      }'''
new_back = '''      private void handleChooserBack() {
         if ("external".equals(this.activeCategoryCode)) {
            this.showHomePage();
         } else if (!this.chooserAtCategoryLevel
            && !this.activeCategoryCode.isBlank()
            && !"search".equals(this.activeCategoryCode)
            && !"favorites".equals(this.activeCategoryCode)
            && !"recent".equals(this.activeCategoryCode)) {
            this.browseCategoryOverview(this.activeCategoryCode);
         } else {
            this.showHomePage();
         }
      }'''
s = replace_once(s, old_back, new_back, 'chooser back external')

old_breadcrumb = '''         } else if ("favorites".equals(this.activeCategoryCode) || "recent".equals(this.activeCategoryCode)) {
            this.browseCommandCategory(this.activeCategoryCode, this.activeCategoryName);
         } else if ("test".equals(this.activeCategoryCode) || "performance".equals(this.activeCategoryCode)) {'''
new_breadcrumb = '''         } else if ("external".equals(this.activeCategoryCode)) {
            this.browseInstalledExternalCommands();
         } else if ("favorites".equals(this.activeCategoryCode) || "recent".equals(this.activeCategoryCode)) {
            this.browseCommandCategory(this.activeCategoryCode, this.activeCategoryName);
         } else if ("test".equals(this.activeCategoryCode) || "performance".equals(this.activeCategoryCode)) {'''
s = replace_once(s, old_breadcrumb, new_breadcrumb, 'breadcrumb external')

# ---------------------------------------------------------------------------
# 2) Spreadsheet-style current-data calculations.
# ---------------------------------------------------------------------------
# Callback keeps the data model generic while writes remain in WorkbenchFrame and
# always go through Stata (so Stata is still the single source of truth).
model_anchor = '   private static final class DataTableModel extends AbstractTableModel {'
model_prefix = '''   private interface DataCellCommitter {
      boolean commit(int row, int column, Object value);
   }

'''
s = replace_once(s, model_anchor, model_prefix + model_anchor, 'cell committer interface')

s = replace_once(
    s,
    '      private Object[][] previewValues;\n      private List<Long> visibleObservations;',
    '      private Object[][] previewValues;\n      private List<Long> visibleObservations;\n      private HxWorkbench.DataCellCommitter cellCommitter;',
    'data model committer field',
)

# Add model helpers before loadPreview.
old_model_helpers = '''      void clearRowFilter() {
         this.visibleObservations = null;
      }

      void loadPreview() {'''
new_model_helpers = '''      void clearRowFilter() {
         this.visibleObservations = null;
      }

      void setCellCommitter(HxWorkbench.DataCellCommitter var1) {
         this.cellCommitter = var1;
      }

      long observationAt(int row) {
         return this.visibleObservations == null ? row + 1L : this.visibleObservations.get(row);
      }

      void refreshCell(int row, int column) {
         this.fireTableCellUpdated(row, column);
      }

      void refreshAll() {
         this.fireTableDataChanged();
      }

      void loadPreview() {'''
s = replace_once(s, old_model_helpers, new_model_helpers, 'data model helpers')

s = replace_once(
    s,
    '''      @Override
      public boolean isCellEditable(int var1, int var2) {
         return false;
      }

      @Override
      public Object getValueAt(int var1, int var2) {''',
    '''      @Override
      public boolean isCellEditable(int var1, int var2) {
         return this.previewValues == null && this.cellCommitter != null;
      }

      @Override
      public void setValueAt(Object value, int row, int column) {
         if (this.isCellEditable(row, column) && this.cellCommitter.commit(row, column, value)) {
            this.fireTableCellUpdated(row, column);
         }
      }

      @Override
      public Object getValueAt(int var1, int var2) {''',
    'editable data model',
)

# Formula-bar fields next to the current data table fields.
s = replace_once(
    s,
    '      private final HxWorkbench.DataTableModel dataModel = new HxWorkbench.DataTableModel();\n      private final JTable dataTable = new JTable(this.dataModel);\n      private final JLabel dataLabel = new JLabel();',
    '''      private final HxWorkbench.DataTableModel dataModel = new HxWorkbench.DataTableModel();
      private final JTable dataTable = new JTable(this.dataModel);
      private final JLabel dataCellRefLabel = new JLabel("未选择", SwingConstants.CENTER);
      private final JTextField dataFormulaField = new JTextField();
      private final JButton dataApplyCellButton = new JButton("写入单元格");
      private final JButton dataApplyColumnButton = new JButton("整列计算");
      private final JButton dataCreateColumnButton = new JButton("新建列");
      private boolean spreadsheetSyncing;
      private final JLabel dataLabel = new JLabel();''',
    'spreadsheet fields',
)

# Connect the model callback and use a wrapper containing formula bar + data table.
s = replace_once(
    s,
    '''      private void buildDataPanel() {
         this.dataTable.setAutoResizeMode(0);''',
    '''      private void buildDataPanel() {
         this.dataModel.setCellCommitter(this.previewMode ? null : this::commitSpreadsheetCellEdit);
         this.dataTable.putClientProperty("terminateEditOnFocusLost", Boolean.TRUE);
         this.dataTable.setAutoResizeMode(0);''',
    'build data callback',
)

old_scroll_wrap = '''         JScrollPane var1 = softScroll(this.dataTable);
         var1.getVerticalScrollBar().setUnitIncrement(20);
         var1.setColumnHeaderView(this.dataTable.getTableHeader());
         JPanel var2 = new JPanel(new BorderLayout());
         var2.setBackground(SURFACE);'''
new_scroll_wrap = '''         JScrollPane var1 = softScroll(this.dataTable);
         var1.getVerticalScrollBar().setUnitIncrement(20);
         var1.setColumnHeaderView(this.dataTable.getTableHeader());
         JPanel spreadsheet = new JPanel(new BorderLayout(0, 6));
         spreadsheet.setBackground(SURFACE);
         spreadsheet.add(this.buildSpreadsheetBar(), BorderLayout.NORTH);
         spreadsheet.add(var1, BorderLayout.CENTER);
         JPanel var2 = new JPanel(new BorderLayout());
         var2.setBackground(SURFACE);'''
s = replace_once(s, old_scroll_wrap, new_scroll_wrap, 'spreadsheet wrapper')
s = replace_once(
    s,
    '         this.currentDataCards.add(var1, "table");',
    '         this.currentDataCards.add(spreadsheet, "table");',
    'current data card spreadsheet wrapper',
)

# Add spreadsheet UI/logic immediately before empty-data panel.
empty_anchor = '      private JComponent buildEmptyDataPanel() {'
spreadsheet_methods = r'''      private JComponent buildSpreadsheetBar() {
         JPanel root = new JPanel(new BorderLayout(0, 6));
         root.setBackground(new Color(249, 251, 254));
         root.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createMatteBorder(0, 0, 1, 0, new Color(225, 231, 240)),
            new EmptyBorder(7, 8, 7, 8)
         ));

         JPanel formula = new JPanel(new BorderLayout(7, 0));
         formula.setOpaque(false);
         this.dataCellRefLabel.setForeground(new Color(55, 69, 89));
         this.dataCellRefLabel.setFont(this.dataCellRefLabel.getFont().deriveFont(Font.BOLD, 10.5F));
         this.dataCellRefLabel.setPreferredSize(new Dimension(96, 30));
         this.dataCellRefLabel.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(216, 224, 236), 6));
         JLabel fx = new JLabel("fx", SwingConstants.CENTER);
         fx.setForeground(ACCENT);
         fx.setFont(new Font("Serif", Font.BOLD | Font.ITALIC, 14));
         fx.setPreferredSize(new Dimension(24, 30));
         styleTextField(this.dataFormulaField);
         this.dataFormulaField.putClientProperty("JTextField.placeholderText", "输入值或公式，例如 =price/mpg、=ln(price)");
         this.dataFormulaField.setToolTipText("不以 = 开头时按普通单元格值处理；以 = 开头时按 Stata 表达式计算");
         this.dataFormulaField.addActionListener(e -> this.applySpreadsheetToSelectedCell());
         formula.add(this.dataCellRefLabel, BorderLayout.WEST);
         formula.add(fx, BorderLayout.CENTER);
         JPanel fieldWrap = new JPanel(new BorderLayout());
         fieldWrap.setOpaque(false);
         fieldWrap.add(this.dataFormulaField, BorderLayout.CENTER);
         formula.add(fieldWrap, BorderLayout.EAST);
         // BorderLayout.CENTER is occupied by fx; move formula field into a nested row
         JPanel formulaRow = new JPanel(new BorderLayout(7, 0));
         formulaRow.setOpaque(false);
         formulaRow.add(this.dataCellRefLabel, BorderLayout.WEST);
         formulaRow.add(fx, BorderLayout.CENTER);
         JPanel formulaFieldHost = new JPanel(new BorderLayout());
         formulaFieldHost.setOpaque(false);
         formulaFieldHost.add(this.dataFormulaField, BorderLayout.CENTER);
         formulaFieldHost.setPreferredSize(new Dimension(310, 30));
         formulaRow.add(formulaFieldHost, BorderLayout.EAST);
         root.add(formulaRow, BorderLayout.NORTH);

         JPanel actions = new JPanel(new BorderLayout(8, 0));
         actions.setOpaque(false);
         JLabel hint = new JLabel("双击单元格可直接改值；= 开头按 Stata 表达式计算");
         hint.setForeground(MUTED);
         hint.setFont(hint.getFont().deriveFont(9.5F));
         actions.add(hint, BorderLayout.CENTER);
         JPanel buttons = new JPanel(new GridLayout(1, 3, 6, 0));
         buttons.setOpaque(false);
         for (JButton button : Arrays.asList(this.dataApplyCellButton, this.dataApplyColumnButton, this.dataCreateColumnButton)) {
            styleSecondaryButton(button);
            button.setMargin(new Insets(3, 7, 3, 7));
         }
         this.dataApplyCellButton.addActionListener(e -> this.applySpreadsheetToSelectedCell());
         this.dataApplyColumnButton.addActionListener(e -> this.applySpreadsheetToColumn());
         this.dataCreateColumnButton.addActionListener(e -> this.createSpreadsheetColumn());
         boolean enabled = !this.previewMode;
         this.dataApplyCellButton.setEnabled(enabled);
         this.dataApplyColumnButton.setEnabled(enabled);
         this.dataCreateColumnButton.setEnabled(enabled);
         buttons.add(this.dataApplyCellButton);
         buttons.add(this.dataApplyColumnButton);
         buttons.add(this.dataCreateColumnButton);
         buttons.setPreferredSize(new Dimension(280, 30));
         actions.add(buttons, BorderLayout.EAST);
         root.add(actions, BorderLayout.SOUTH);
         return root;
      }

      private void syncSpreadsheetSelection() {
         if (this.spreadsheetSyncing) return;
         int row = this.dataTable.getSelectedRow();
         int viewColumn = this.dataTable.getSelectedColumn();
         if (row < 0 || viewColumn < 0 || this.dataModel.getColumnCount() == 0) {
            this.dataCellRefLabel.setText("未选择");
            return;
         }
         int column = this.dataTable.convertColumnIndexToModel(viewColumn);
         String variable = this.dataModel.getColumnName(column);
         long observation = this.dataModel.observationAt(this.dataTable.convertRowIndexToModel(row));
         this.dataCellRefLabel.setText(variable + "[" + observation + "]");
         Object value = this.dataModel.getValueAt(this.dataTable.convertRowIndexToModel(row), column);
         this.spreadsheetSyncing = true;
         this.dataFormulaField.setText(Objects.toString(value, ""));
         this.spreadsheetSyncing = false;
      }

      private String spreadsheetExpressionForInput(String input, int variableIndex) {
         String text = input == null ? "" : input.trim();
         if (text.startsWith("=")) {
            String expression = text.substring(1).trim();
            if (expression.isBlank()) {
               JOptionPane.showMessageDialog(this, "= 后面请输入 Stata 表达式，例如 =price/mpg。", "公式为空", JOptionPane.INFORMATION_MESSAGE);
               return null;
            }
            return expression;
         }
         if (variableIndex > 0 && Data.isVarTypeString(variableIndex)) return HxWorkbench.StataBridge.quote(text);
         String numeric = text.replace(",", "");
         if (numeric.matches("\\.[a-z]?|[+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)(?:[eE][+-]?\\d+)?")) return numeric;
         JOptionPane.showMessageDialog(
            this,
            "数值单元格直接编辑请输入数字；需要计算时以 = 开头，例如 =price/mpg 或 =ln(price)。",
            "请输入数值或公式",
            JOptionPane.INFORMATION_MESSAGE
         );
         return null;
      }

      private boolean runSpreadsheetCommand(String command, boolean structureChanged) {
         if (this.previewMode || command == null || command.isBlank()) return false;
         HxWorkbench.DatasetSnapshot snapshot = structureChanged ? HxWorkbench.DatasetSnapshot.capture() : null;
         int rc = HxWorkbench.StataBridge.execute(command, true);
         if (rc != 0) {
            JOptionPane.showMessageDialog(this, "Stata 未能完成数据运算，return code = " + rc + "。\n\n" + command, "数据运算失败", JOptionPane.ERROR_MESSAGE);
            this.statusLabel.setText("数据运算失败 | Return code " + rc);
            return false;
         }
         this.lastExecutedCommand = command;
         if (structureChanged) {
            this.beforeSnapshot = snapshot;
            this.refreshDataset(true);
         } else {
            this.dataModel.refreshAll();
            this.updateSelectedColumnSummary();
            this.refreshInspectorVariables();
            this.syncSpreadsheetSelection();
            this.dataTable.repaint();
            this.refreshHomeContext();
         }
         this.statusLabel.setText("数据已更新 | 命令已写入 Stata History：" + shortenCommand(command));
         return true;
      }

      private boolean commitSpreadsheetCellEdit(int row, int column, Object value) {
         if (row < 0 || column < 0 || column >= this.dataModel.getColumnCount()) return false;
         String variable = this.dataModel.getColumnName(column);
         int variableIndex = HxWorkbench.safe(() -> Data.getVarIndex(variable), -1);
         if (variableIndex <= 0) return false;
         String expression = this.spreadsheetExpressionForInput(Objects.toString(value, ""), variableIndex);
         if (expression == null) return false;
         long observation = this.dataModel.observationAt(row);
         String command = "replace " + variable + " = " + expression + " in " + observation;
         if (!this.runSpreadsheetCommand(command, false)) return false;
         this.changedCells.clear();
         this.changedCells.add(row + ":" + column);
         this.dataModel.refreshCell(row, column);
         this.dataTable.repaint();
         return true;
      }

      private void applySpreadsheetToSelectedCell() {
         if (this.previewMode) return;
         if (this.dataTable.isEditing() && !this.dataTable.getCellEditor().stopCellEditing()) return;
         int viewRow = this.dataTable.getSelectedRow();
         int viewColumn = this.dataTable.getSelectedColumn();
         if (viewRow < 0 || viewColumn < 0) {
            JOptionPane.showMessageDialog(this, "请先在数据表中选择一个单元格。", "未选择单元格", JOptionPane.INFORMATION_MESSAGE);
            return;
         }
         int row = this.dataTable.convertRowIndexToModel(viewRow);
         int column = this.dataTable.convertColumnIndexToModel(viewColumn);
         this.commitSpreadsheetCellEdit(row, column, this.dataFormulaField.getText());
      }

      private void applySpreadsheetToColumn() {
         if (this.previewMode) return;
         int viewColumn = this.dataTable.getSelectedColumn();
         if (viewColumn < 0) {
            JOptionPane.showMessageDialog(this, "请先选择要计算的变量列。", "未选择变量列", JOptionPane.INFORMATION_MESSAGE);
            return;
         }
         int column = this.dataTable.convertColumnIndexToModel(viewColumn);
         String variable = this.dataModel.getColumnName(column);
         int variableIndex = HxWorkbench.safe(() -> Data.getVarIndex(variable), -1);
         String expression = this.spreadsheetExpressionForInput(this.dataFormulaField.getText(), variableIndex);
         if (expression == null) return;
         String command = "replace " + variable + " = " + expression;
         int answer = JOptionPane.showConfirmDialog(
            this,
            "这会计算整列 “" + variable + "”。\n\n将执行：\n" + command + "\n\n完整命令会写入 Stata History。",
            "确认整列计算",
            JOptionPane.OK_CANCEL_OPTION,
            JOptionPane.WARNING_MESSAGE
         );
         if (answer != JOptionPane.OK_OPTION) return;
         HxWorkbench.DatasetSnapshot snapshot = HxWorkbench.DatasetSnapshot.capture();
         if (this.runSpreadsheetCommand(command, false)) {
            this.beforeSnapshot = snapshot;
            this.compareSnapshots(snapshot);
         }
      }

      private void createSpreadsheetColumn() {
         if (this.previewMode) return;
         String name = JOptionPane.showInputDialog(this, "新变量名（Stata 变量名）：", "新建计算列", JOptionPane.PLAIN_MESSAGE);
         if (name == null) return;
         name = name.trim();
         if (!name.matches("[A-Za-z_][A-Za-z0-9_]{0,31}")) {
            JOptionPane.showMessageDialog(this, "变量名请使用字母/数字/下划线，首字符为字母或下划线，最长 32 个字符。", "变量名无效", JOptionPane.INFORMATION_MESSAGE);
            return;
         }
         final String newName = name;
         if (HxWorkbench.safe(() -> Data.getVarIndex(newName), -1) > 0) {
            JOptionPane.showMessageDialog(this, "变量 “" + newName + "” 已存在。请选择该列后使用“整列计算”。", "变量已存在", JOptionPane.INFORMATION_MESSAGE);
            return;
         }
         String text = this.dataFormulaField.getText() == null ? "" : this.dataFormulaField.getText().trim();
         String expression = text.startsWith("=") ? text.substring(1).trim() : text;
         if (expression.isBlank()) {
            String entered = JOptionPane.showInputDialog(this, "输入 Stata 表达式，例如 price/mpg 或 ln(price)：", "新建计算列", JOptionPane.PLAIN_MESSAGE);
            if (entered == null || entered.trim().isBlank()) return;
            expression = entered.trim();
            if (expression.startsWith("=")) expression = expression.substring(1).trim();
         }
         String command = "generate " + newName + " = " + expression;
         int answer = JOptionPane.showConfirmDialog(
            this,
            "将新建变量 “" + newName + "”。\n\n将执行：\n" + command,
            "确认新建计算列",
            JOptionPane.OK_CANCEL_OPTION,
            JOptionPane.QUESTION_MESSAGE
         );
         if (answer == JOptionPane.OK_OPTION) this.runSpreadsheetCommand(command, true);
      }

'''
s = replace_once(s, empty_anchor, spreadsheet_methods + empty_anchor, 'spreadsheet methods')

# Selection changes keep the Excel-like cell reference/formula bar synchronized.
s = replace_once(
    s,
    '''         this.dataTable.getSelectionModel().addListSelectionListener(var1x -> {
            if (!var1x.getValueIsAdjusting()) this.syncVariableWindowFromDataTable();
         });
         this.dataTable.getColumnModel().getSelectionModel().addListSelectionListener(var1x -> {
            if (!var1x.getValueIsAdjusting()) this.syncVariableWindowFromDataTable();
         });''',
    '''         this.dataTable.getSelectionModel().addListSelectionListener(var1x -> {
            if (!var1x.getValueIsAdjusting()) {
               this.syncVariableWindowFromDataTable();
               this.syncSpreadsheetSelection();
            }
         });
         this.dataTable.getColumnModel().getSelectionModel().addListSelectionListener(var1x -> {
            if (!var1x.getValueIsAdjusting()) {
               this.syncVariableWindowFromDataTable();
               this.syncSpreadsheetSelection();
            }
         });''',
    'spreadsheet selection listeners',
)

# The current-data panel is no longer read-only.
s = s.replace('74 行 × 12 列 | 表格只读，可横向和纵向滚动', '74 行 × 12 列 | 双击单元格可编辑；公式栏支持 = 表达式')
s = s.replace(' | 表格只读，可横向和纵向滚动', ' | 双击单元格可编辑；公式栏支持 = 表达式')
s = s.replace('选择一种方式开始，载入后这里会显示可滚动的只读数据表。', '选择一种方式开始，载入后这里会显示可滚动、可直接计算的数据表和公式栏。')

# ---------------------------------------------------------------------------
# 3) Release metadata/documentation.
# ---------------------------------------------------------------------------
for name in ["hxempirical.ado", "hxempirical.sthlp", "hxinstaller.ado", "hxinstall.do", "INSTALL.md", "README.md"]:
    p = Path(name)
    t = p.read_text(encoding="utf-8").replace("1.5.3", "1.5.4")
    p.write_text(t, encoding="utf-8")

pkg = Path("hxempirical.pkg")
t = pkg.read_text(encoding="utf-8").replace("d Version 1.5.3", "d Version 1.5.4")
t = t.replace(
    "d visual regress builders, postestimation diagnostics, live command preview, data view, DID and external OneClick.",
    "d visual regress builders, postestimation diagnostics, spreadsheet-style data calculations, DID and external commands."
)
pkg.write_text(t, encoding="utf-8")

readme = Path("README.md")
t = readme.read_text(encoding="utf-8")
marker = "### 1.5.3 目录显示修复\n"
note = """### 1.5.4 数据表运算与外部命令\n\n- 左侧“历史”入口改为“已下载外部命令”，动态显示工具箱已登记且当前 Stata 实际能够找到的第三方/外部命令；最近任务仍保留在首页。\n- “当前数据”加入类似 WPS/Excel 的公式栏：双击单元格可直接改值，以 `=` 开头可按 Stata 表达式计算；支持写入单元格、整列计算和新建计算列。\n- 所有数据写入仍由 Stata `replace` / `generate` 执行，并写入 Stata History，避免 Java 表格形成第二份数据状态。\n- 当前实现聚焦实证数据运算，不宣称完整复刻 Excel；排序、复杂多单元格粘贴和撤销栈可在后续版本继续扩展。\n\n"""
if marker not in t:
    raise SystemExit("README release marker missing")
t = t.replace(marker, note + marker, 1)
readme.write_text(t, encoding="utf-8")

src.write_text(s, encoding="utf-8")
print("HX_V154_PATCH_OK")
