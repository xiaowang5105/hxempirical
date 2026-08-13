from pathlib import Path

p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')

# Version.
s = s.replace('public static final String VERSION = "1.4.4";', 'public static final String VERSION = "1.4.5";', 1)
s = s.replace('SFIToolkit.displayln("HxWorkbench 1.4.4");', 'SFIToolkit.displayln("HxWorkbench 1.4.5");', 1)

# Fields needed for the middle inspector and bidirectional xtreg command editing.
old = '''      private JList<String> xtregIndepList;\n      private Runnable xtregPreviewUpdater;\n      private String activeSidebarKey = "home";'''
new = '''      private JList<String> xtregIndepList;\n      private Runnable xtregPreviewUpdater;\n      private JTextArea xtregCommandPreview;\n      private JRadioButton xtregFeButton;\n      private JRadioButton xtregReButton;\n      private JRadioButton xtregBeButton;\n      private JRadioButton xtregPaButton;\n      private JComboBox<String> xtregSeCombo;\n      private boolean xtregSyncingFromCommand;\n      private String activeSidebarKey = "home";'''
assert old in s
s = s.replace(old, new, 1)

old = '''      private final JLabel inspectorRoleLabel = new JLabel("当前模型角色：未使用");\n      private final JTabbedPane oneClickResultTabs = new JTabbedPane();'''
new = '''      private final JLabel inspectorRoleLabel = new JLabel("当前模型角色：未使用");\n      private final JTextArea inspectorPropertyArea = readonlyArea();\n      private final JLabel inspectorOverviewLabel = new JLabel("数据概览：尚未载入数据");\n      private final JTabbedPane oneClickResultTabs = new JTabbedPane();'''
assert old in s
s = s.replace(old, new, 1)

old = '''      private JSplitPane dataSummarySplit;\n      private JSplitPane inspectorLowerSplit;\n      private JTabbedPane variableTabs;'''
new = '''      private JSplitPane dataSummarySplit;\n      private JSplitPane inspectorLowerSplit;\n      private JSplitPane inspectorDataSplit;\n      private JTabbedPane variableTabs;'''
assert old in s
s = s.replace(old, new, 1)

# Divider behavior now matches the three-column layout: main | middle variable rail | data/results.
old = '''      private void clampInspectorDividers() {\n         if (this.dataSummarySplit != null) {\n            int height = this.dataSummarySplit.getHeight();\n            if (height > 0) {\n               int dividerSize = Math.max(0, this.dataSummarySplit.getDividerSize());\n               int minData = 90;\n               int minLower = 160;\n               int current = this.dataSummarySplit.getDividerLocation();\n               if (current <= 0 || current >= height - dividerSize) current = (int)Math.round(height * 0.28);\n               int max = Math.max(minData, height - minLower - dividerSize);\n               int target = Math.max(minData, Math.min(current, max));\n               if (target != this.dataSummarySplit.getDividerLocation()) this.dataSummarySplit.setDividerLocation(target);\n            }\n         }\n         if (this.inspectorLowerSplit != null) {\n            int height = this.inspectorLowerSplit.getHeight();\n            if (height > 0) {\n               int dividerSize = Math.max(0, this.inspectorLowerSplit.getDividerSize());\n               int minVariable = 75;\n               int minProperty = 75;\n               int current = this.inspectorLowerSplit.getDividerLocation();\n               if (current <= 0 || current >= height - dividerSize) current = (int)Math.round(height * 0.52);\n               int max = Math.max(minVariable, height - minProperty - dividerSize);\n               int target = Math.max(minVariable, Math.min(current, max));\n               if (target != this.inspectorLowerSplit.getDividerLocation()) this.inspectorLowerSplit.setDividerLocation(target);\n            }\n         }\n      }\n\n      void applyDividerRatios() {\n         SwingUtilities.invokeLater(() -> {\n            int total = this.commandDataSplit.getWidth();\n            if (total > 0) {\n               int minInspector = total < 980 ? 270 : 320;\n               int inspector = Math.max(minInspector, Math.min(520, (int)Math.round(total * 0.43)));\n               int minCommand = total < 980 ? 390 : 480;\n               int divider = Math.max(minCommand, total - inspector);\n               divider = Math.min(divider, Math.max(minCommand, total - 250));\n               this.commandDataSplit.setDividerLocation(Math.max(0, divider));\n            }\n            this.clampInspectorDividers();\n         });\n      }'''
new = '''      private void clampInspectorDividers() {\n         if (this.dataSummarySplit != null) {\n            int height = this.dataSummarySplit.getHeight();\n            if (height > 0) {\n               int dividerSize = Math.max(0, this.dataSummarySplit.getDividerSize());\n               int minData = 135;\n               int minSummary = 105;\n               int current = this.dataSummarySplit.getDividerLocation();\n               if (current <= 0 || current >= height - dividerSize) current = (int)Math.round(height * 0.68);\n               int max = Math.max(minData, height - minSummary - dividerSize);\n               int target = Math.max(minData, Math.min(current, max));\n               if (target != this.dataSummarySplit.getDividerLocation()) this.dataSummarySplit.setDividerLocation(target);\n            }\n         }\n         if (this.inspectorLowerSplit != null) {\n            int height = this.inspectorLowerSplit.getHeight();\n            if (height > 0) {\n               int dividerSize = Math.max(0, this.inspectorLowerSplit.getDividerSize());\n               int minVariable = 120;\n               int minProperty = 120;\n               int current = this.inspectorLowerSplit.getDividerLocation();\n               if (current <= 0 || current >= height - dividerSize) current = (int)Math.round(height * 0.54);\n               int max = Math.max(minVariable, height - minProperty - dividerSize);\n               int target = Math.max(minVariable, Math.min(current, max));\n               if (target != this.inspectorLowerSplit.getDividerLocation()) this.inspectorLowerSplit.setDividerLocation(target);\n            }\n         }\n         if (this.inspectorDataSplit != null) {\n            int width = this.inspectorDataSplit.getWidth();\n            if (width > 0) {\n               int dividerSize = Math.max(0, this.inspectorDataSplit.getDividerSize());\n               int minMiddle = 210;\n               int minData = 300;\n               int current = this.inspectorDataSplit.getDividerLocation();\n               if (current <= 0 || current >= width - dividerSize) current = Math.min(250, Math.max(minMiddle, width / 3));\n               int max = Math.max(minMiddle, width - minData - dividerSize);\n               int target = Math.max(minMiddle, Math.min(current, max));\n               if (target != this.inspectorDataSplit.getDividerLocation()) this.inspectorDataSplit.setDividerLocation(target);\n            }\n         }\n      }\n\n      void applyDividerRatios() {\n         SwingUtilities.invokeLater(() -> {\n            int total = this.commandDataSplit.getWidth();\n            if (total > 0) {\n               int minInspector = total < 1050 ? 535 : 610;\n               int inspector = Math.max(minInspector, Math.min(720, (int)Math.round(total * 0.48)));\n               int minCommand = total < 1050 ? 420 : 520;\n               int divider = Math.max(minCommand, total - inspector);\n               divider = Math.min(divider, Math.max(minCommand, total - 510));\n               this.commandDataSplit.setDividerLocation(Math.max(0, divider));\n            }\n            if (this.inspectorDataSplit != null && this.inspectorDataSplit.getWidth() > 0) {\n               this.inspectorDataSplit.setDividerLocation(Math.min(250, Math.max(210, this.inspectorDataSplit.getWidth() / 3)));\n            }\n            this.clampInspectorDividers();\n         });\n      }'''
assert old in s
s = s.replace(old, new, 1)

# Data tab: keep Current Data on the far right, with summary/distribution below it.
old = '''         JComponent variableWindow = this.buildVariableInspectorPanel();\n         JComponent propertyWindow = this.buildPropertyInspectorPanel();\n         variableWindow.setMinimumSize(new Dimension(0, 75));\n         propertyWindow.setMinimumSize(new Dimension(0, 75));\n         this.inspectorLowerSplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT, variableWindow, propertyWindow);\n         this.inspectorLowerSplit.setResizeWeight(0.52);\n         this.inspectorLowerSplit.setContinuousLayout(true);\n         this.inspectorLowerSplit.setMinimumSize(new Dimension(0, 155));\n         this.inspectorLowerSplit.setBorder(null);\n         this.inspectorLowerSplit.setDividerSize(5);\n\n         this.dataSummarySplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT, this.currentDataCards, this.inspectorLowerSplit);\n         this.dataSummarySplit.setResizeWeight(0.28);\n         this.dataSummarySplit.setContinuousLayout(true);\n         this.dataSummarySplit.setMinimumSize(new Dimension(0, 0));\n         this.dataSummarySplit.setBorder(null);\n         this.dataSummarySplit.setDividerSize(5);\n         var2.add(this.dataSummarySplit, BorderLayout.CENTER);\n         this.dataTabs.addTab("数据", var2);\n         SwingUtilities.invokeLater(() -> {\n            if (this.dataSummarySplit != null) this.dataSummarySplit.setDividerLocation(0.28);\n            if (this.inspectorLowerSplit != null) this.inspectorLowerSplit.setDividerLocation(0.52);\n         });'''
new = '''         this.dataSummarySplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT, this.currentDataCards, this.variableTabs);\n         this.dataSummarySplit.setResizeWeight(0.68);\n         this.dataSummarySplit.setContinuousLayout(true);\n         this.dataSummarySplit.setMinimumSize(new Dimension(0, 0));\n         this.dataSummarySplit.setBorder(null);\n         this.dataSummarySplit.setDividerSize(5);\n         var2.add(this.dataSummarySplit, BorderLayout.CENTER);\n         this.dataTabs.addTab("数据", var2);\n         SwingUtilities.invokeLater(() -> {\n            if (this.dataSummarySplit != null) this.dataSummarySplit.setDividerLocation(0.68);\n         });'''
assert old in s
s = s.replace(old, new, 1)

# Middle property panel now has its own compact property text; the full summary/distribution stays on far right.
old = '''         header.add(title, BorderLayout.WEST);\n         header.add(this.inspectorRoleLabel, BorderLayout.SOUTH);\n         root.add(header, BorderLayout.NORTH);\n         root.add(this.variableTabs, BorderLayout.CENTER);\n         return root;\n      }'''
new = '''         header.add(title, BorderLayout.WEST);\n         header.add(this.inspectorRoleLabel, BorderLayout.SOUTH);\n         root.add(header, BorderLayout.NORTH);\n         this.inspectorPropertyArea.setRows(8);\n         this.inspectorPropertyArea.setBackground(SURFACE);\n         this.inspectorPropertyArea.setForeground(TEXT);\n         this.inspectorPropertyArea.setFont(this.inspectorPropertyArea.getFont().deriveFont(10.5F));\n         JPanel body = new JPanel(new BorderLayout(0, 7));\n         body.setOpaque(false);\n         body.add(softScroll(this.inspectorPropertyArea), BorderLayout.CENTER);\n         this.inspectorOverviewLabel.setForeground(MUTED);\n         this.inspectorOverviewLabel.setFont(this.inspectorOverviewLabel.getFont().deriveFont(9.5F));\n         body.add(this.inspectorOverviewLabel, BorderLayout.SOUTH);\n         root.add(body, BorderLayout.CENTER);\n         return root;\n      }'''
assert old in s
s = s.replace(old, new, 1)

# Property text follows the selected variable.
old = '''         if (var2 < 0) {\n            this.summaryArea.setText("当前没有变量。");\n            this.histogram.setValues(Collections.emptyList(), "");\n         } else {\n            HxWorkbench.VariableSummary var3 = HxWorkbench.VariableSummary.compute(var2 + 1);\n            this.summaryArea.setText(var3.text);\n            this.summaryArea.setCaretPosition(0);\n            this.histogram.setValues(var3.numericValues, var3.name);\n         }\n         this.refreshInspectorRole();'''
new = '''         if (var2 < 0) {\n            this.summaryArea.setText("当前没有变量。");\n            this.inspectorPropertyArea.setText("当前没有变量。");\n            this.histogram.setValues(Collections.emptyList(), "");\n         } else {\n            HxWorkbench.VariableSummary var3 = HxWorkbench.VariableSummary.compute(var2 + 1);\n            this.summaryArea.setText(var3.text);\n            this.summaryArea.setCaretPosition(0);\n            this.inspectorPropertyArea.setText(var3.text);\n            this.inspectorPropertyArea.setCaretPosition(0);\n            this.histogram.setValues(var3.numericValues, var3.name);\n         }\n         this.inspectorOverviewLabel.setText("数据概览：" + Data.getObsTotal() + " 行 × " + Data.getVarCount() + " 列");\n         this.refreshInspectorRole();'''
assert old in s
s = s.replace(old, new, 1)

old = '''            this.summaryArea.setText("变量：" + variable + "\\n\\n预览模式下仅展示变量结构；载入真实 Stata 数据后显示类型、标签、缺失值和描述统计。");\n            this.histogram.setValues(Collections.emptyList(), variable);'''
new = '''            this.summaryArea.setText("变量：" + variable + "\\n\\n预览模式下仅展示变量结构；载入真实 Stata 数据后显示类型、标签、缺失值和描述统计。");\n            this.inspectorPropertyArea.setText(this.summaryArea.getText());\n            this.histogram.setValues(Collections.emptyList(), variable);'''
assert old in s
s = s.replace(old, new, 1)

# Build shared inspector as middle variable rail + far-right data/results/logs.
old = '''      private JComponent buildDataContainer() {\n         JPanel root = new JPanel(new BorderLayout());\n         root.setBackground(APP_BG);\n         root.setBorder(new EmptyBorder(18, 8, 16, 18));\n         JPanel card = cardPanel();\n         card.setLayout(new BorderLayout());\n         card.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(216, 224, 235), 11), new EmptyBorder(0, 0, 0, 0)));\n         JPanel header = new JPanel(new BorderLayout(10, 4));\n         header.setOpaque(false);\n         header.setBorder(new EmptyBorder(14, 15, 9, 15));\n         this.rightPaneTitle.setForeground(TEXT);\n         this.rightPaneTitle.setFont(this.rightPaneTitle.getFont().deriveFont(Font.BOLD, 15.0F));\n         styleSecondaryButton(this.refreshButton);\n         header.add(this.rightPaneTitle, BorderLayout.WEST);\n         header.add(this.refreshButton, BorderLayout.EAST);\n         this.dataLabel.setForeground(MUTED);\n         this.dataLabel.setFont(this.dataLabel.getFont().deriveFont(10.0F));\n         header.add(this.dataLabel, BorderLayout.SOUTH);\n         card.add(header, BorderLayout.NORTH);\n         this.dataTabs.setBorder(new EmptyBorder(0, 6, 6, 6));\n         card.add(this.dataTabs, BorderLayout.CENTER);\n         root.add(card, BorderLayout.CENTER);\n         return root;\n      }'''
new = '''      private JComponent buildDataContainer() {\n         JPanel root = new JPanel(new BorderLayout());\n         root.setBackground(APP_BG);\n         root.setBorder(new EmptyBorder(18, 6, 16, 18));\n\n         JComponent variableWindow = this.buildVariableInspectorPanel();\n         JComponent propertyWindow = this.buildPropertyInspectorPanel();\n         variableWindow.setMinimumSize(new Dimension(0, 120));\n         propertyWindow.setMinimumSize(new Dimension(0, 120));\n         this.inspectorLowerSplit = new JSplitPane(JSplitPane.VERTICAL_SPLIT, variableWindow, propertyWindow);\n         this.inspectorLowerSplit.setResizeWeight(0.54);\n         this.inspectorLowerSplit.setContinuousLayout(true);\n         this.inspectorLowerSplit.setBorder(null);\n         this.inspectorLowerSplit.setDividerSize(5);\n         JPanel middle = new JPanel(new BorderLayout());\n         middle.setBackground(APP_BG);\n         middle.setBorder(new EmptyBorder(0, 0, 0, 6));\n         middle.setPreferredSize(new Dimension(250, 0));\n         middle.setMinimumSize(new Dimension(210, 0));\n         middle.add(this.inspectorLowerSplit, BorderLayout.CENTER);\n\n         JPanel card = cardPanel();\n         card.setLayout(new BorderLayout());\n         card.setMinimumSize(new Dimension(300, 0));\n         card.setBorder(BorderFactory.createCompoundBorder(new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(216, 224, 235), 11), new EmptyBorder(0, 0, 0, 0)));\n         JPanel header = new JPanel(new BorderLayout(10, 4));\n         header.setOpaque(false);\n         header.setBorder(new EmptyBorder(14, 15, 9, 15));\n         this.rightPaneTitle.setForeground(TEXT);\n         this.rightPaneTitle.setFont(this.rightPaneTitle.getFont().deriveFont(Font.BOLD, 15.0F));\n         styleSecondaryButton(this.refreshButton);\n         header.add(this.rightPaneTitle, BorderLayout.WEST);\n         header.add(this.refreshButton, BorderLayout.EAST);\n         this.dataLabel.setForeground(MUTED);\n         this.dataLabel.setFont(this.dataLabel.getFont().deriveFont(10.0F));\n         header.add(this.dataLabel, BorderLayout.SOUTH);\n         card.add(header, BorderLayout.NORTH);\n         this.dataTabs.setBorder(new EmptyBorder(0, 6, 6, 6));\n         card.add(this.dataTabs, BorderLayout.CENTER);\n\n         this.inspectorDataSplit = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, middle, card);\n         this.inspectorDataSplit.setResizeWeight(0.0);\n         this.inspectorDataSplit.setContinuousLayout(true);\n         this.inspectorDataSplit.setOneTouchExpandable(false);\n         this.inspectorDataSplit.setDividerSize(6);\n         this.inspectorDataSplit.setBorder(null);\n         root.add(this.inspectorDataSplit, BorderLayout.CENTER);\n         SwingUtilities.invokeLater(() -> this.inspectorDataSplit.setDividerLocation(250));\n         return root;\n      }'''
assert old in s
s = s.replace(old, new, 1)

# Update context wording for the middle variable rail.
s = s.replace('右侧“变量窗口”拖入', '中间“变量窗口”拖入')
s = s.replace('右侧变量窗口是主要选变量入口', '中间变量窗口是主要选变量入口')
s = s.replace('可从变量窗口或表头拖入左侧变量框', '可从中间变量窗口或表头拖入左侧变量框')

# xtreg preview: editable and reverse-synchronised.
old = '''         JRadioButton fe = new JRadioButton("固定效应（FE）", true);\n         JRadioButton re = new JRadioButton("随机效应（RE）");\n         JRadioButton be = new JRadioButton("between");\n         JRadioButton pa = new JRadioButton("population-averaged");\n         for (JRadioButton b : Arrays.asList(fe, re, be, pa)) { b.setOpaque(false); b.setForeground(TEXT); }\n         ButtonGroup modelGroup = new ButtonGroup();\n         modelGroup.add(fe); modelGroup.add(re); modelGroup.add(be); modelGroup.add(pa);\n         JComboBox<String> se = new JComboBox<>(new String[]{"稳健标准误", "默认标准误", "按面板聚类"});\n\n         JTextArea commandPreview = readonlyArea();\n         commandPreview.setRows(2);\n         commandPreview.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 12));\n         commandPreview.setBackground(new Color(247, 250, 255));'''
new = '''         JRadioButton fe = new JRadioButton("固定效应（FE）", true);\n         JRadioButton re = new JRadioButton("随机效应（RE）");\n         JRadioButton be = new JRadioButton("between");\n         JRadioButton pa = new JRadioButton("population-averaged");\n         this.xtregFeButton = fe; this.xtregReButton = re; this.xtregBeButton = be; this.xtregPaButton = pa;\n         for (JRadioButton b : Arrays.asList(fe, re, be, pa)) { b.setOpaque(false); b.setForeground(TEXT); }\n         ButtonGroup modelGroup = new ButtonGroup();\n         modelGroup.add(fe); modelGroup.add(re); modelGroup.add(be); modelGroup.add(pa);\n         JComboBox<String> se = new JComboBox<>(new String[]{"稳健标准误", "默认标准误", "按面板聚类"});\n         this.xtregSeCombo = se;\n\n         JTextArea commandPreview = new JTextArea();\n         this.xtregCommandPreview = commandPreview;\n         commandPreview.setEditable(true);\n         commandPreview.setRows(2);\n         commandPreview.setLineWrap(false);\n         commandPreview.setToolTipText("可以直接修改 xtset / xtreg 命令；离开编辑框后，上方设置会自动同步");\n         commandPreview.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 12));\n         commandPreview.setBackground(new Color(247, 250, 255));'''
assert old in s
s = s.replace(old, new, 1)

old = '''         this.xtregPreviewUpdater = update;\n         panelVar.addActionListener(e -> { if (!this.rebuilding) update.run(); });'''
new = '''         this.xtregPreviewUpdater = update;\n         commandPreview.addFocusListener(new java.awt.event.FocusAdapter() {\n            @Override public void focusLost(java.awt.event.FocusEvent e) { WorkbenchFrame.this.syncXtregControlsFromCommand(); }\n         });\n         panelVar.addActionListener(e -> { if (!this.rebuilding) update.run(); });'''
assert old in s
s = s.replace(old, new, 1)

# Editable hint in Step 4.
old = '''         JPanel previewLeft = new JPanel(new BorderLayout(0, 5)); previewLeft.setOpaque(false); previewLeft.add(new JLabel("命令预览"), BorderLayout.NORTH); previewLeft.add(commandPreviewScroll, BorderLayout.CENTER);'''
new = '''         JPanel previewLeft = new JPanel(new BorderLayout(0, 5)); previewLeft.setOpaque(false);\n         JLabel commandPreviewLabel = new JLabel("<html>命令预览 <span style='color:#2f6fe4'>· 可编辑，编辑完成后自动同步上方设置</span></html>");\n         previewLeft.add(commandPreviewLabel, BorderLayout.NORTH); previewLeft.add(commandPreviewScroll, BorderLayout.CENTER);'''
assert old in s
s = s.replace(old, new, 1)

# Run always consumes the latest edited command and synchronises controls first.
old = '''         JButton run = this.refButton("运行 xtreg", true);\n         run.addActionListener(e -> {\n            String pv = Objects.toString(panelVar.getSelectedItem(), "").trim();'''
new = '''         JButton run = this.refButton("运行 xtreg", true);\n         run.addActionListener(e -> {\n            this.syncXtregControlsFromCommand();\n            String pv = Objects.toString(panelVar.getSelectedItem(), "").trim();'''
assert old in s
s = s.replace(old, new, 1)

# Insert reverse parser before openCommandPage.
marker = '''      private void openCommandPage(String var1) {'''
assert marker in s
parser = r'''      private boolean setXtregComboValue(JComboBox<String> combo, String value) {
         if (combo == null || value == null || value.isBlank()) return false;
         for (int i = 0; i < combo.getItemCount(); i++) {
            if (value.equals(Objects.toString(combo.getItemAt(i), ""))) {
               combo.setSelectedIndex(i);
               return true;
            }
         }
         return false;
      }

      private void syncXtregControlsFromCommand() {
         if (this.xtregSyncingFromCommand || this.xtregCommandPreview == null
            || this.xtregPanelVar == null || this.xtregTimeVar == null || this.xtregDepVar == null
            || this.xtregIndepList == null || this.xtregFeButton == null || this.xtregSeCombo == null) return;
         String raw = this.xtregCommandPreview.getText() == null ? "" : this.xtregCommandPreview.getText().trim();
         if (raw.isBlank()) return;

         String xtsetLine = "";
         String xtregLine = "";
         for (String line : raw.split("\\R")) {
            String trimmed = line.trim();
            if (trimmed.toLowerCase(Locale.ROOT).startsWith("xtset ")) xtsetLine = trimmed;
            if (trimmed.toLowerCase(Locale.ROOT).startsWith("xtreg ")) xtregLine = trimmed;
         }
         if (xtregLine.isBlank() && raw.toLowerCase(Locale.ROOT).startsWith("xtreg ")) xtregLine = raw;
         if (xtregLine.isBlank()) {
            this.statusLabel.setText("命令编辑：未找到 xtreg 命令；上方设置未改变。");
            return;
         }

         boolean oldRebuilding = this.rebuilding;
         this.xtregSyncingFromCommand = true;
         this.rebuilding = true;
         int synced = 0;
         try {
            if (!xtsetLine.isBlank()) {
               String[] parts = xtsetLine.replaceFirst("(?i)^xtset\\s+", "").trim().split("\\s+");
               if (parts.length >= 1 && this.setXtregComboValue(this.xtregPanelVar, parts[0])) synced++;
               if (parts.length >= 2 && this.setXtregComboValue(this.xtregTimeVar, parts[1])) synced++;
            }

            int comma = xtregLine.indexOf(',');
            String lhs = comma >= 0 ? xtregLine.substring(0, comma).trim() : xtregLine.trim();
            String opts = comma >= 0 ? xtregLine.substring(comma + 1).trim() : "";
            String varsText = lhs.replaceFirst("(?i)^xtreg\\s+", "").trim();
            String[] terms = varsText.isBlank() ? new String[0] : varsText.split("\\s+");
            if (terms.length >= 1 && this.setXtregComboValue(this.xtregDepVar, terms[0])) synced++;

            this.xtregIndepList.clearSelection();
            ListModel<String> model = this.xtregIndepList.getModel();
            for (int t = 1; t < terms.length; t++) {
               String term = terms[t];
               for (int i = 0; i < model.getSize(); i++) {
                  if (term.equals(model.getElementAt(i))) {
                     this.xtregIndepList.addSelectionInterval(i, i);
                     synced++;
                     break;
                  }
               }
            }

            String padded = " " + opts.toLowerCase(Locale.ROOT).replaceAll("\\s+", " ") + " ";
            if (Pattern.compile("(^|\\s)fe(\\s|$)").matcher(padded).find()) this.xtregFeButton.setSelected(true);
            else if (Pattern.compile("(^|\\s)re(\\s|$)").matcher(padded).find()) this.xtregReButton.setSelected(true);
            else if (Pattern.compile("(^|\\s)(be|between)(\\s|$)").matcher(padded).find()) this.xtregBeButton.setSelected(true);
            else if (Pattern.compile("(^|\\s)(pa|population-averaged)(\\s|$)").matcher(padded).find()) this.xtregPaButton.setSelected(true);
            synced++;

            Matcher clusterMatcher = Pattern.compile("(?i)vce\\s*\\(\\s*cluster\\s+([^\\s\\)]+)\\s*\\)").matcher(opts);
            if (clusterMatcher.find()) this.xtregSeCombo.setSelectedItem("按面板聚类");
            else if (Pattern.compile("(?i)vce\\s*\\(\\s*robust\\s*\\)").matcher(opts).find()) this.xtregSeCombo.setSelectedItem("稳健标准误");
            else this.xtregSeCombo.setSelectedItem("默认标准误");
            synced++;

            this.previewArea.setText(xtregLine);
            this.previewArea.setCaretPosition(0);
            this.refreshInspectorRole();
         } finally {
            this.rebuilding = oldRebuilding;
            this.xtregSyncingFromCommand = false;
         }
         this.statusLabel.setText("已从编辑后的命令同步上方设置（" + synced + " 项）；未识别的高级语法继续保留在命令框中。");
      }

'''
s = s.replace(marker, parser + marker, 1)

# Release metadata.
ado = Path('hxempirical.ado')
a = ado.read_text(encoding='utf-8')
a = a.replace('*! hxempirical 1.4.4', '*! hxempirical 1.4.5', 1)
a = a.replace('版本：" as result "1.4.4"', '版本：" as result "1.4.5"', 1)
a = a.replace('return local version "1.4.4"', 'return local version "1.4.5"', 1)
ado.write_text(a, encoding='utf-8')

pkg = Path('hxempirical.pkg')
pkg.write_text(pkg.read_text(encoding='utf-8').replace('d Version 1.4.4', 'd Version 1.4.5', 1), encoding='utf-8')

hlp = Path('hxempirical.sthlp')
h = hlp.read_text(encoding='utf-8').replace('version 1.4.4', 'version 1.4.5', 1).replace('The 1.4.4 interface', 'The 1.4.5 interface', 1).replace('package version 1.4.4', 'package version 1.4.5', 1)
h = h.replace('navigation rail, a task-focused main workspace, and one shared right-side', 'navigation rail, a task-focused main workspace, a middle variable inspector, and a shared right-side')
hlp.write_text(h, encoding='utf-8')

readme = Path('README.md')
r = readme.read_text(encoding='utf-8').replace('当前发布版本：1.4.4', '当前发布版本：1.4.5', 1)
# update only the headline timestamp if present
import re
r = re.sub(r'(\*\*上次修改时间：)2026-08-13 [0-9]{2}:[0-9]{2}(（UTC\+8）\*\*)', r'\g<1>2026-08-13 16:12\g<2>', r, count=1)
readme.write_text(r, encoding='utf-8')

print('V145_PATCH_OK')
