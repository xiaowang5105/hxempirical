from pathlib import Path


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"missing follow-up anchor: {label}")
    return text.replace(old, new, 1)

p = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
s = p.read_text(encoding="utf-8")

old_formula = '''         JPanel formula = new JPanel(new BorderLayout(7, 0));
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
         root.add(formulaRow, BorderLayout.NORTH);'''
new_formula = '''         this.dataCellRefLabel.setForeground(new Color(55, 69, 89));
         this.dataCellRefLabel.setFont(this.dataCellRefLabel.getFont().deriveFont(Font.BOLD, 10.5F));
         this.dataCellRefLabel.setPreferredSize(new Dimension(96, 30));
         this.dataCellRefLabel.setBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(216, 224, 236), 6));
         JLabel fx = new JLabel("fx", SwingConstants.CENTER);
         fx.setForeground(ACCENT);
         fx.setFont(new Font("Serif", Font.BOLD | Font.ITALIC, 14));
         fx.setPreferredSize(new Dimension(26, 30));
         styleTextField(this.dataFormulaField);
         this.dataFormulaField.putClientProperty("JTextField.placeholderText", "输入值或公式，例如 =price/mpg、=ln(price)");
         this.dataFormulaField.setToolTipText("不以 = 开头时按普通单元格值处理；以 = 开头时按 Stata 表达式计算");
         this.dataFormulaField.addActionListener(e -> this.applySpreadsheetToSelectedCell());
         JPanel formulaRow = new JPanel(new BorderLayout(7, 0));
         formulaRow.setOpaque(false);
         formulaRow.add(this.dataCellRefLabel, BorderLayout.WEST);
         JPanel fxField = new JPanel(new BorderLayout(6, 0));
         fxField.setOpaque(false);
         fxField.add(fx, BorderLayout.WEST);
         fxField.add(this.dataFormulaField, BorderLayout.CENTER);
         formulaRow.add(fxField, BorderLayout.CENTER);
         root.add(formulaRow, BorderLayout.NORTH);'''
s = replace_once(s, old_formula, new_formula, 'formula layout')

s = replace_once(
    s,
    '''         } else {
            this.dataModel.refreshAll();
            this.updateSelectedColumnSummary();
            this.refreshInspectorVariables();
            this.syncSpreadsheetSelection();
            this.dataTable.repaint();
            this.refreshHomeContext();
         }
         this.statusLabel.setText("数据已更新 | 命令已写入 Stata History：" + shortenCommand(command));''',
    '''         } else {
            this.dataModel.refreshAll();
            this.updateSelectedColumnSummary();
            this.syncSpreadsheetSelection();
            this.dataTable.repaint();
            this.refreshHomeContext();
         }
         this.statusLabel.setText("数据已更新 | 命令已写入 Stata History：" + shortenCommand(command));''',
    'avoid selection jump on spreadsheet refresh',
)

old_commit = '''      private boolean commitSpreadsheetCellEdit(int row, int column, Object value) {
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
      }'''
new_commit = '''      private boolean commitSpreadsheetCellEdit(int row, int column, Object value) {
         if (this.previewMode || row < 0 || column < 0 || column >= this.dataModel.getColumnCount()) return false;
         String variable = this.dataModel.getColumnName(column);
         int variableIndex = HxWorkbench.safe(() -> Data.getVarIndex(variable), -1);
         if (variableIndex <= 0) return false;
         String expression = this.spreadsheetExpressionForInput(Objects.toString(value, ""), variableIndex);
         if (expression == null) return false;
         long observation = this.dataModel.observationAt(row);
         String command = "replace " + variable + " = " + expression + " in " + observation;
         int rc = HxWorkbench.StataBridge.execute(command, true);
         if (rc != 0) {
            JOptionPane.showMessageDialog(this, "Stata 未能写入该单元格，return code = " + rc + "。\\n\\n" + command, "单元格写入失败", JOptionPane.ERROR_MESSAGE);
            this.statusLabel.setText("单元格写入失败 | Return code " + rc);
            return false;
         }
         this.lastExecutedCommand = command;
         this.changedCells.clear();
         this.changedCells.add(row + ":" + column);
         this.dataModel.refreshCell(row, column);
         this.updateSelectedColumnSummary();
         this.syncSpreadsheetSelection();
         this.dataTable.repaint();
         this.refreshHomeContext();
         this.statusLabel.setText("单元格已更新 | 命令已写入 Stata History：" + shortenCommand(command));
         return true;
      }'''
s = replace_once(s, old_commit, new_commit, 'direct cell commit')

p.write_text(s, encoding="utf-8")
print("HX_V154_FOLLOWUP_OK")
