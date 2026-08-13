from pathlib import Path

java = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = java.read_text(encoding='utf-8')

s = s.replace('public static final String VERSION = "1.4.1";', 'public static final String VERSION = "1.4.2";', 1)
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.4.1");', 'SFIToolkit.displayln("HxWorkbench 1.4.2");', 1)

old_constructor = '''         shell.add(this.buildSidebar(), BorderLayout.WEST);
         shell.add(center, BorderLayout.CENTER);
         this.add(shell, BorderLayout.CENTER);

         stylePrimaryButton(this.runButton);
'''
new_constructor = '''         shell.add(this.buildSidebar(), BorderLayout.WEST);
         shell.add(center, BorderLayout.CENTER);
         this.add(shell, BorderLayout.CENTER);
         this.addComponentListener(new java.awt.event.ComponentAdapter() {
            @Override
            public void componentResized(java.awt.event.ComponentEvent e) {
               SwingUtilities.invokeLater(() -> WorkbenchFrame.this.clampInspectorDividers());
            }
         });

         stylePrimaryButton(this.runButton);
'''
assert old_constructor in s
s = s.replace(old_constructor, new_constructor, 1)

old_windows = '''         JComponent variableWindow = this.buildVariableInspectorPanel();
         JComponent propertyWindow = this.buildPropertyInspectorPanel();
         this.inspectorLowerSplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT, variableWindow, propertyWindow);
         this.inspectorLowerSplit.setResizeWeight(0.52);
         this.inspectorLowerSplit.setContinuousLayout(true);
         this.inspectorLowerSplit.setMinimumSize(new Dimension(0, 0));
'''
new_windows = '''         JComponent variableWindow = this.buildVariableInspectorPanel();
         JComponent propertyWindow = this.buildPropertyInspectorPanel();
         variableWindow.setMinimumSize(new Dimension(0, 75));
         propertyWindow.setMinimumSize(new Dimension(0, 75));
         this.inspectorLowerSplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT, variableWindow, propertyWindow);
         this.inspectorLowerSplit.setResizeWeight(0.52);
         this.inspectorLowerSplit.setContinuousLayout(true);
         this.inspectorLowerSplit.setMinimumSize(new Dimension(0, 155));
'''
assert old_windows in s
s = s.replace(old_windows, new_windows, 1)

start = s.index('      void applyDividerRatios() {')
end = s.index('      private JComponent buildAppHeader() {', start)
new_method = '''      private void clampInspectorDividers() {
         if (this.dataSummarySplit != null) {
            int height = this.dataSummarySplit.getHeight();
            if (height > 0) {
               int dividerSize = Math.max(0, this.dataSummarySplit.getDividerSize());
               int minData = 90;
               int minLower = 160;
               int current = this.dataSummarySplit.getDividerLocation();
               if (current <= 0 || current >= height - dividerSize) current = (int)Math.round(height * 0.28);
               int max = Math.max(minData, height - minLower - dividerSize);
               int target = Math.max(minData, Math.min(current, max));
               if (target != this.dataSummarySplit.getDividerLocation()) this.dataSummarySplit.setDividerLocation(target);
            }
         }
         if (this.inspectorLowerSplit != null) {
            int height = this.inspectorLowerSplit.getHeight();
            if (height > 0) {
               int dividerSize = Math.max(0, this.inspectorLowerSplit.getDividerSize());
               int minVariable = 75;
               int minProperty = 75;
               int current = this.inspectorLowerSplit.getDividerLocation();
               if (current <= 0 || current >= height - dividerSize) current = (int)Math.round(height * 0.52);
               int max = Math.max(minVariable, height - minProperty - dividerSize);
               int target = Math.max(minVariable, Math.min(current, max));
               if (target != this.inspectorLowerSplit.getDividerLocation()) this.inspectorLowerSplit.setDividerLocation(target);
            }
         }
      }

      void applyDividerRatios() {
         SwingUtilities.invokeLater(() -> {
            int total = this.commandDataSplit.getWidth();
            if (total > 0) {
               int minInspector = total < 980 ? 270 : 320;
               int inspector = Math.max(minInspector, Math.min(520, (int)Math.round(total * 0.43)));
               int minCommand = total < 980 ? 390 : 480;
               int divider = Math.max(minCommand, total - inspector);
               divider = Math.min(divider, Math.max(minCommand, total - 250));
               this.commandDataSplit.setDividerLocation(Math.max(0, divider));
            }
            this.clampInspectorDividers();
         });
      }

'''
s = s[:start] + new_method + s[end:]
java.write_text(s, encoding='utf-8')

ado = Path('hxempirical.ado')
a = ado.read_text(encoding='utf-8')
a = a.replace('*! hxempirical 1.4.1', '*! hxempirical 1.4.2', 1)
a = a.replace('版本：" as result "1.4.1"', '版本：" as result "1.4.2"', 1)
a = a.replace('return local version "1.4.1"', 'return local version "1.4.2"', 1)
ado.write_text(a, encoding='utf-8')

pkg = Path('hxempirical.pkg')
pkg.write_text(pkg.read_text(encoding='utf-8').replace('d Version 1.4.1', 'd Version 1.4.2', 1), encoding='utf-8')

hlp = Path('hxempirical.sthlp')
h = hlp.read_text(encoding='utf-8').replace('version 1.4.1', 'version 1.4.2', 1).replace('The 1.4.1 interface', 'The 1.4.2 interface', 1)
hlp.write_text(h, encoding='utf-8')

readme = Path('README.md')
r = readme.read_text(encoding='utf-8').replace('当前发布版本：1.4.1', '当前发布版本：1.4.2', 1).replace('上次修改时间：2026-08-13 15:27（UTC+8）', '上次修改时间：2026-08-13 15:34（UTC+8）', 1)
readme.write_text(r, encoding='utf-8')

print('FIX_V142_RESIZE_OK')
