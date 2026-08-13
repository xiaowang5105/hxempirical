from pathlib import Path

java = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = java.read_text(encoding='utf-8')

# Version bump for the selfcheck fixes.
assert 'public static final String VERSION = "1.4.0";' in s
s = s.replace('public static final String VERSION = "1.4.0";', 'public static final String VERSION = "1.4.1";', 1)
assert 'SFIToolkit.displayln("HxWorkbench 1.4.0");' in s
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.4.0");', 'SFIToolkit.displayln("HxWorkbench 1.4.1");', 1)

# The card layout includes an empty-state panel whose default minimum size can force
# the Current Data area much taller than the intended 28%. Give the split child an
# explicit small minimum so the proportional divider is honored.
anchor = '         this.currentDataCards.setBackground(SURFACE);\n         this.currentDataCards.add(var1, "table");\n'
assert anchor in s
s = s.replace(anchor, '         this.currentDataCards.setBackground(SURFACE);\n         this.currentDataCards.setMinimumSize(new Dimension(0, 90));\n         this.currentDataCards.add(var1, "table");\n', 1)

# applyDividerRatios still contained the old 70% data/summary split from v1.3.x.
old = '''            if (this.dataSummarySplit != null) {
               int var2 = (int)Math.round(this.dataSummarySplit.getHeight() * 0.70);
               this.dataSummarySplit.setDividerLocation(Math.max(170, var2));
            }
'''
assert old in s
new = '''            if (this.dataSummarySplit != null) {
               int dataHeight = this.dataSummarySplit.getHeight();
               if (dataHeight > 0) {
                  int dataDivider = (int)Math.round(dataHeight * 0.28);
                  dataDivider = Math.max(100, Math.min(dataDivider, Math.max(100, dataHeight - 240)));
                  this.dataSummarySplit.setDividerLocation(dataDivider);
               }
            }
            if (this.inspectorLowerSplit != null) {
               int lowerHeight = this.inspectorLowerSplit.getHeight();
               if (lowerHeight > 0) {
                  int lowerDivider = (int)Math.round(lowerHeight * 0.52);
                  lowerDivider = Math.max(90, Math.min(lowerDivider, Math.max(90, lowerHeight - 110)));
                  this.inspectorLowerSplit.setDividerLocation(lowerDivider);
               }
            }
'''
s = s.replace(old, new, 1)

# Two-way linkage: clicking a column in Current Data must also select that variable
# in the Variable Window before Property Window is refreshed.
listener_old = '''         this.dataTable.getSelectionModel().addListSelectionListener(var1x -> this.updateSelectedColumnSummary());
         this.dataTable.getColumnModel().getSelectionModel().addListSelectionListener(var1x -> this.updateSelectedColumnSummary());
'''
assert listener_old in s
listener_new = '''         this.dataTable.getSelectionModel().addListSelectionListener(var1x -> {
            if (!var1x.getValueIsAdjusting()) this.syncVariableWindowFromDataTable();
         });
         this.dataTable.getColumnModel().getSelectionModel().addListSelectionListener(var1x -> {
            if (!var1x.getValueIsAdjusting()) this.syncVariableWindowFromDataTable();
         });
'''
s = s.replace(listener_old, listener_new, 1)

method_anchor = '      private void installInspectorVariableDragSupport() {'
assert method_anchor in s
method = '''      private void syncVariableWindowFromDataTable() {
         int viewColumn = this.dataTable.getSelectedColumn();
         if (viewColumn < 0) {
            this.updateSelectedColumnSummary();
            return;
         }
         String variable = this.dataTable.getColumnName(viewColumn);
         if (!variable.equals(this.selectedInspectorVariable())) {
            int matchedRow = -1;
            for (int row = 0; row < this.inspectorVariableModel.getRowCount(); row++) {
               if (variable.equals(Objects.toString(this.inspectorVariableModel.getValueAt(row, 0), ""))) {
                  matchedRow = row;
                  break;
               }
            }
            if (matchedRow >= 0) {
               this.inspectorVariableTable.setRowSelectionInterval(matchedRow, matchedRow);
               Rectangle cell = this.inspectorVariableTable.getCellRect(matchedRow, 0, true);
               this.inspectorVariableTable.scrollRectToVisible(cell);
            } else {
               this.inspectorVariableTable.clearSelection();
            }
         }
         this.updateSelectedColumnSummary();
      }

'''
s = s.replace(method_anchor, method + method_anchor, 1)
java.write_text(s, encoding='utf-8')

# Package-facing version metadata.
ado = Path('hxempirical.ado')
a = ado.read_text(encoding='utf-8')
a = a.replace('*! hxempirical 1.4.0  13aug2026', '*! hxempirical 1.4.1  13aug2026', 1)
a = a.replace('版本：" as result "1.4.0"', '版本：" as result "1.4.1"', 1)
a = a.replace('return local version "1.4.0"', 'return local version "1.4.1"', 1)
ado.write_text(a, encoding='utf-8')

pkg = Path('hxempirical.pkg')
p = pkg.read_text(encoding='utf-8').replace('d Version 1.4.0', 'd Version 1.4.1', 1)
pkg.write_text(p, encoding='utf-8')

helpf = Path('hxempirical.sthlp')
h = helpf.read_text(encoding='utf-8').replace('version 1.4.0  13aug2026', 'version 1.4.1  13aug2026', 1)
h = h.replace('The 1.4.0 interface', 'The 1.4.1 interface', 1)
helpf.write_text(h, encoding='utf-8')

readme = Path('README.md')
r = readme.read_text(encoding='utf-8').replace('**当前发布版本：1.4.0**', '**当前发布版本：1.4.1**', 1)
r = r.replace('**上次修改时间：2026-08-13 15:05（UTC+8）**', '**上次修改时间：2026-08-13 15:27（UTC+8）**', 1)
readme.write_text(r, encoding='utf-8')

print('FIX_V141_SELFCHECK_OK')
