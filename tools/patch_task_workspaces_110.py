from pathlib import Path


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"missing pattern: {label}")
    return text.replace(old, new, 1)


# -----------------------------------------------------------------------------
# Java workbench
# -----------------------------------------------------------------------------
p = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
s = p.read_text(encoding="utf-8")
s = replace_once(s, 'public static final String VERSION = "1.0.3";', 'public static final String VERSION = "1.1.0";', 'java version')

s = replace_once(
    s,
    '      private final JPanel homeAllFunctionsPanel = new JPanel();\n      private final JToggleButton homeAllFunctionsToggle = new JToggleButton("展开全部功能  +");',
    '      private final JPanel homeAllFunctionsPanel = new JPanel();',
    'remove home expand toggle field',
)

s = replace_once(
    s,
    '      private JPanel regressClusterFieldBlock;\n      private JPanel regressWeightVarFieldBlock;\n      private boolean regressWorkspaceActive;',
    '''      private JPanel regressClusterFieldBlock;\n      private JPanel regressWeightVarFieldBlock;\n      private boolean regressWorkspaceActive;\n      private final JComboBox<String> baselineEstimator = new JComboBox<>(new String[]{"xtreg", "reghdfe", "areg", "regress"});\n      private final JComboBox<String> baselineXtModel = new JComboBox<>(new String[]{"固定效应（FE）", "随机效应（RE）", "组间效应（BE）"});\n      private final JLabel baselineEstimatorSource = new JLabel("Stata 官方");\n      private JPanel baselineEstimatorHeader;\n      private JPanel baselineXtModelFieldBlock;\n      private JPanel baselineAbsorbFieldBlock;\n      private boolean baselineTaskActive;''',
    'baseline fields',
)

# Method code mappings: fixes stale/incorrect chooser contents for focused linear methods.
s = replace_once(
    s,
    '            case "线性模型":\n               return "linear";',
    '''            case "普通线性回归":\n               return "linear_ols";\n            case "固定效应线性回归":\n               return "linear_fe";\n            case "稳健与特殊线性回归":\n               return "linear_special";\n            case "分位数回归":\n               return "linear_quantile";\n            case "时间序列线性回归":\n               return "linear_ts";\n            case "线性模型":\n               return "linear";''',
    'focused linear method codes',
)

# Style the compact estimator controls.
s = replace_once(
    s,
    '         this.vce.setRenderer(new HxWorkbench.WorkbenchFrame.VceRenderer());',
    '''         styleCombo(this.baselineEstimator);\n         styleCombo(this.baselineXtModel);\n         this.vce.setRenderer(new HxWorkbench.WorkbenchFrame.VceRenderer());''',
    'baseline combo styling',
)

# Compact estimator selector in the command-page header.
s = replace_once(
    s,
    '''         JPanel var5 = new JPanel(new FlowLayout(2, 7, 0));\n         var5.setOpaque(false);\n         var5.add(this.changeMethodButton);\n         var5.add(this.homeButton);\n         var5.add(var4);''',
    '''         JPanel var5 = new JPanel(new FlowLayout(2, 7, 0));\n         var5.setOpaque(false);\n         this.baselineEstimatorHeader = new JPanel(new FlowLayout(0, 5, 0));\n         this.baselineEstimatorHeader.setOpaque(false);\n         JLabel baselineEstimatorLabel = new JLabel("估计方法");\n         baselineEstimatorLabel.setForeground(MUTED);\n         baselineEstimatorLabel.setFont(baselineEstimatorLabel.getFont().deriveFont(10.5F));\n         this.baselineEstimator.setPreferredSize(new Dimension(118, 29));\n         this.baselineEstimatorSource.setForeground(ACCENT);\n         this.baselineEstimatorSource.setFont(this.baselineEstimatorSource.getFont().deriveFont(Font.BOLD, 10.0F));\n         this.baselineEstimatorHeader.add(baselineEstimatorLabel);\n         this.baselineEstimatorHeader.add(this.baselineEstimator);\n         this.baselineEstimatorHeader.add(this.baselineEstimatorSource);\n         this.baselineEstimatorHeader.setVisible(false);\n         var5.add(this.baselineEstimatorHeader);\n         var5.add(this.changeMethodButton);\n         var5.add(this.homeButton);\n         var5.add(var4);''',
    'baseline estimator header',
)

# Homepage: baseline task opens directly, full catalog is always visible, no reserved blank height.
s = replace_once(
    s,
    '         var13.add(this.homeLauncherButton("基准回归", "普通 OLS · regress", () -> this.openRegressWorkspace(), true));',
    '         var13.add(this.homeLauncherButton("基准回归", "xtreg · 可切换估计方法", () -> this.openBaselineRegressionWorkspace(), true));',
    'home baseline launcher',
)

s = replace_once(
    s,
    '''         var9.setPreferredSize(new Dimension(800, 390));\n         var9.setMinimumSize(new Dimension(0, 390));\n         var9.setMaximumSize(new Dimension(Integer.MAX_VALUE, 390));\n         var2.add(var9);\n         var2.add(Box.createVerticalStrut(18));\n         JPanel var22 = new JPanel(new BorderLayout());\n         var22.setOpaque(false);\n         JLabel var23 = sectionTitle("更多功能");\n         var22.add(var23, "West");\n         styleSecondaryButton(this.homeAllFunctionsToggle);\n         this.homeAllFunctionsToggle.setFocusPainted(false);\n         this.homeAllFunctionsToggle.addActionListener(var2x -> {\n            boolean var3x = this.homeAllFunctionsToggle.isSelected();\n            this.homeAllFunctionsPanel.setVisible(var3x);\n            this.homeAllFunctionsToggle.setText(var3x ? "收起全部功能  −" : "展开全部功能  +");\n            var2.revalidate();\n            var2.repaint();\n         });\n         this.homeAllFunctionsToggle.setPreferredSize(new Dimension(150, 34));\n         var22.add(this.homeAllFunctionsToggle, "East");\n         var22.setAlignmentX(0.0F);\n         var22.setMaximumSize(new Dimension(Integer.MAX_VALUE, 42));\n         var2.add(var22);''',
    '''         var2.add(var9);\n         var2.add(Box.createVerticalStrut(18));\n         JPanel var22 = new JPanel(new BorderLayout());\n         var22.setOpaque(false);\n         JLabel var23 = sectionTitle("全部功能");\n         var22.add(var23, "West");\n         var22.setAlignmentX(0.0F);\n         var22.setMaximumSize(new Dimension(Integer.MAX_VALUE, 34));\n         var2.add(var22);''',
    'remove homepage expand mechanism',
)
s = replace_once(s, '         this.homeAllFunctionsPanel.setVisible(false);', '         this.homeAllFunctionsPanel.setVisible(true);', 'always show all functions')

# Search for baseline regression should open the task workspace rather than a command chooser.
s = s.replace('this.openRegressWorkspace();\n               this.statusLabel.setText("已按“" + var1 + "”打开普通线性回归。");', 'this.openBaselineRegressionWorkspace();\n               this.statusLabel.setText("已按“" + var1 + "”打开基准回归工作区。");')

# Clear stale selection before every method reload.
s = replace_once(
    s,
    '         this.rebuilding = true;\n         this.commandModel.clear();\n         if (this.previewMode) {',
    '         this.rebuilding = true;\n         this.commandList.clearSelection();\n         this.commandModel.clear();\n         if (this.previewMode) {',
    'clear stale method command selection',
)

# Replace large tutorial cards with compact command choices.
start = s.index('      private void renderCommandChooser(String var1, String var2, List<String> var3) {')
end = s.index('      private void handleChooserBack()', start)
new_chooser = r'''      private void renderCommandChooser(String var1, String var2, List<String> var3) {
         this.setChooserBreadcrumb(var2.isBlank() ? var1 : var1 + "  >  " + var2);
         this.chooserTitle.setText(var2.isBlank() ? var1 : var2);
         this.chooserHint.setText("选择一个命令进入参数设置；详细说明放在命令页面中。");
         this.chooserContent.removeAll();
         if (var3.isEmpty()) {
            JLabel var4 = new JLabel("当前没有找到可用命令。", 0);
            var4.setForeground(MUTED);
            var4.setAlignmentX(0.5F);
            this.chooserContent.add(Box.createVerticalStrut(48));
            this.chooserContent.add(var4);
         } else {
            int cols = var3.size() <= 2 ? 1 : 2;
            JPanel grid = new JPanel(new GridLayout(0, cols, 10, 10));
            grid.setOpaque(false);
            grid.setAlignmentX(0.0F);
            int rows = Math.max(1, (var3.size() + cols - 1) / cols);
            grid.setPreferredSize(new Dimension(800, rows * 78));
            grid.setMaximumSize(new Dimension(Integer.MAX_VALUE, rows * 78));
            for (String command : var3) {
               grid.add(this.commandChoiceButton(command, cols));
            }
            if (cols == 2 && var3.size() % 2 != 0) {
               JPanel filler = new JPanel();
               filler.setOpaque(false);
               grid.add(filler);
            }
            this.chooserContent.add(grid);
         }

         this.chooserReady = true;
         this.chooserAtCategoryLevel = false;
         this.configureChooserBack();
         this.chooserContent.revalidate();
         this.chooserContent.repaint();
         this.homeButton.setVisible(true);
         this.homeButton.setEnabled(true);
         this.inspectorToggle.setVisible(false);
         this.stageLayout.show(this.stageCards, "chooser");
      }

      private JButton commandChoiceButton(String command, int cols) {
         HxWorkbench.WorkbenchFrame.CommandGuide guide = commandGuide(command);
         String width = cols == 1 ? "760px" : "410px";
         String source = commandSource(command);
         JButton button = new JButton(
            "<html><div style='width:" + width + ";text-align:left'>"
               + "<span style='font-family:monospace;font-size:13px'><b>" + html(command) + "</b></span>"
               + "&nbsp;&nbsp;<span style='font-size:11px'><b>" + html(guide.title) + "</b></span>"
               + "&nbsp;&nbsp;<span style='font-size:9px;color:#2a66be'>[" + html(source) + "]</span>"
               + "<br><span style='font-size:10px;color:#637083'>" + html(guide.purpose) + "</span>"
               + "</div></html>"
         );
         button.setUI(new HxWorkbench.WorkbenchFrame.FlatButtonUI(SURFACE, new Color(248, 250, 253), new Color(238, 243, 249), TEXT, BORDER));
         button.setBorder(new EmptyBorder(9, 14, 9, 14));
         button.setHorizontalAlignment(2);
         button.setVerticalAlignment(0);
         button.setPreferredSize(new Dimension(320, 68));
         button.setToolTipText("进入 " + command + " 参数设置");
         button.setCursor(Cursor.getPredefinedCursor(12));
         button.setFocusPainted(false);
         button.setContentAreaFilled(false);
         button.addActionListener(event -> this.openCommandPage(command));
         return button;
      }

      private static String commandSource(String command) {
         if (command == null) return "";
         if (command.startsWith("oneclick") || "hxconvert".equals(command) || "缺失值分析".equals(command)) {
            return "HX Workflow";
         }
         if (Arrays.asList("reghdfe", "winsor2", "ivreghdfe", "ppmlhdfe", "coefplot", "event_plot").contains(command)) {
            return "第三方";
         }
         return "Stata 官方";
      }

'''
s = s[:start] + new_chooser + s[end:]

# Baseline events and common-field preservation.
s = replace_once(
    s,
    '''         this.regressWeightType.addActionListener(var1x -> this.updateRegressConditionalFields());\n         this.depvar.addActionListener(var1x -> {\n            if (this.regressWorkspaceActive) {''',
    '''         this.regressWeightType.addActionListener(var1x -> this.updateRegressConditionalFields());\n         this.baselineEstimator.addActionListener(var1x -> {\n            if (!this.rebuilding && this.baselineTaskActive) {\n               this.switchBaselineEstimator();\n            }\n         });\n         this.baselineXtModel.addActionListener(var1x -> {\n            if (!this.rebuilding && this.baselineTaskActive) {\n               this.updateBaselinePreview();\n            }\n         });\n         this.depvar.addActionListener(var1x -> {\n            if (this.regressWorkspaceActive || this.baselineTaskActive) {''',
    'baseline estimator events',
)
s = replace_once(s, '            if (this.regressWorkspaceActive) {\n               this.sanitizeRegressControls();', '            if (this.regressWorkspaceActive || this.baselineTaskActive) {\n               this.sanitizeRegressControls();', 'baseline x listener')
s = replace_once(s, '            if (this.regressWorkspaceActive) {\n               this.updateRegressConditionalFields();', '            if (this.regressWorkspaceActive || this.baselineTaskActive) {\n               this.updateRegressConditionalFields();', 'baseline vce condition')
s = replace_once(s, '         if (this.regressWorkspaceActive && !this.rebuilding) {', '         if ((this.regressWorkspaceActive || this.baselineTaskActive) && !this.rebuilding) {', 'sanitize baseline controls')

# Special terms should refresh whichever task workspace is active.
s = replace_once(
    s,
    '            this.regressSpecialTermsModel.addElement(var1);\n            this.updateRegressPreview();',
    '            this.regressSpecialTermsModel.addElement(var1);\n            if (this.baselineTaskActive) this.updateBaselinePreview();\n            else this.updateRegressPreview();',
    'special terms baseline preview',
)

# Home and ordinary command pages must hide the baseline selector.
s = replace_once(
    s,
    '      private void showHomePage() {\n         this.currentCommand = "";\n         this.regressWorkspaceActive = false;',
    '''      private void showHomePage() {\n         this.currentCommand = "";\n         this.regressWorkspaceActive = false;\n         this.baselineTaskActive = false;\n         if (this.baselineEstimatorHeader != null) this.baselineEstimatorHeader.setVisible(false);''',
    'hide baseline on home',
)
s = replace_once(
    s,
    '      private void openCommandPage(String var1) {\n         this.showWorkspacePage();',
    '''      private void openCommandPage(String var1) {\n         this.baselineTaskActive = false;\n         if (this.baselineEstimatorHeader != null) this.baselineEstimatorHeader.setVisible(false);\n         this.showWorkspacePage();''',
    'hide baseline on ordinary command',
)
s = replace_once(
    s,
    '      private void showRegressPage() {\n         this.regressWorkspaceActive = true;',
    '''      private void showRegressPage() {\n         this.baselineTaskActive = false;\n         if (this.baselineEstimatorHeader != null) this.baselineEstimatorHeader.setVisible(false);\n         this.regressWorkspaceActive = true;''',
    'direct regress page baseline off',
)

# Insert task workspace implementation before the existing direct regress page.
anchor = '      private void showRegressPage() {'
idx = s.index(anchor)
baseline_methods = r'''      private void openBaselineRegressionWorkspace() {
         this.activeCategoryCode = "reg";
         this.activeCategoryName = "回归模型";
         this.activeMethodName = "基准回归";
         this.chooserReady = false;
         this.showBaselineRegressionPage(true);
      }

      private void showBaselineRegressionPage(boolean resetEstimator) {
         this.regressWorkspaceActive = false;
         this.baselineTaskActive = true;
         this.showWorkspacePage();
         this.selectDataView();
         this.commandDock.setVisible(true);
         this.commandTabs.setVisible(true);
         this.commandTabs.setSelectedIndex(0);
         this.previewArea.setEditable(true);
         this.runButton.setText("运行基准回归");
         this.commandTitle.setText("基准回归");
         this.commandTitle.setToolTipText("在同一个任务页面切换 xtreg / reghdfe / areg / regress");
         this.setWorkspaceBreadcrumb("回归模型  ›  基准回归");
         this.exampleLabel.setText("<html>先设置 Y、核心 X 和 Controls；右上角只用一个小下拉框切换估计方法，变量设置会保留。</html>");
         this.insightArea.setText("基准回归工作区把研究任务放在前面。默认使用 xtreg（固定效应），也可以在同一页切换 reghdfe、areg 或 regress。切换时保留 Y、核心 X、Controls、样本条件和标准误等公共设置，只替换估计器特有参数和最终 Stata 命令。");
         this.syntaxArea.setText("任务工作区：xtreg / reghdfe / areg / regress；最终仍执行所选估计器的真实 Stata 命令。");
         if (this.baselineEstimatorHeader != null) this.baselineEstimatorHeader.setVisible(true);
         this.refreshVariableControls();
         this.refreshRegressVariables(true);
         if (resetEstimator) {
            this.rebuilding = true;
            this.baselineEstimator.setSelectedItem("xtreg");
            this.baselineXtModel.setSelectedItem("固定效应（FE）");
            this.rebuilding = false;
         }
         this.switchBaselineEstimator();
         this.statusLabel.setText("基准回归：默认 xtreg；可在右上角切换估计方法，公共变量设置不会清空。");
      }

      private void switchBaselineEstimator() {
         if (!this.baselineTaskActive) return;
         String estimator = selected(this.baselineEstimator);
         if (estimator.isBlank()) return;
         this.currentCommand = estimator;
         this.baselineEstimatorSource.setText(commandSource(estimator));
         this.baselineEstimatorSource.setForeground("第三方".equals(commandSource(estimator)) ? new Color(143, 91, 24) : ACCENT);
         if (!this.previewMode) {
            HxWorkbench.StataBridge.execute("quietly hxresolve " + estimator, false);
            this.offerOptionalDependency(estimator);
         }
         this.rebuilding = true;
         String previousWeight = selected(this.regressWeightType);
         this.regressWeightType.removeAllItems();
         this.regressWeightType.addItem("无");
         this.regressWeightType.addItem("fweight");
         this.regressWeightType.addItem("aweight");
         this.regressWeightType.addItem("pweight");
         if (!"reghdfe".equals(estimator) && !"areg".equals(estimator)) this.regressWeightType.addItem("iweight");
         this.setComboValue(this.regressWeightType, previousWeight);
         if (selected(this.regressWeightType).isBlank()) this.regressWeightType.setSelectedItem("无");
         this.rebuilding = false;
         this.rebuildBaselineForm();
         this.updateBaselinePreview();
      }

      private void rebuildBaselineForm() {
         String estimator = selected(this.baselineEstimator);
         this.formPanel.removeAll();
         int row = 0;
         this.addField(row++, "因变量 Y", this.depvar);
         this.addField(row++, "核心解释变量 X", this.regressX);
         this.addField(row++, "控制变量 Controls（可多选）", this.listPane(this.regressControls));
         this.baselineXtModelFieldBlock = null;
         this.baselineAbsorbFieldBlock = null;
         if ("xtreg".equals(estimator)) {
            this.baselineXtModelFieldBlock = this.addField(row++, "模型", this.baselineXtModel);
         } else if ("reghdfe".equals(estimator) || "areg".equals(estimator)) {
            this.absorb.setSelectionMode("areg".equals(estimator) ? 0 : 2);
            this.baselineAbsorbFieldBlock = this.addField(row++, "固定效应 absorb()", this.listPane(this.absorb));
         }
         this.addField(row++, "标准误", this.vce);
         this.regressClusterFieldBlock = this.addField(row++, "聚类变量", this.cluster);

         JPanel moreSettings = this.buildBaselineMoreSettings(estimator);
         JToggleButton moreToggle = new JToggleButton("展开更多设置  +");
         styleSecondaryButton(moreToggle);
         moreSettings.setVisible(false);
         moreToggle.addActionListener(event -> {
            boolean expanded = moreToggle.isSelected();
            moreToggle.setText(expanded ? "收起更多设置  −" : "展开更多设置  +");
            moreSettings.setVisible(expanded);
            this.formPanel.revalidate();
            this.formPanel.repaint();
         });
         JPanel moreBlock = new JPanel();
         moreBlock.setOpaque(false);
         moreBlock.setLayout(new BoxLayout(moreBlock, BoxLayout.Y_AXIS));
         moreToggle.setAlignmentX(0.0F);
         moreSettings.setAlignmentX(0.0F);
         moreBlock.add(moreToggle);
         moreBlock.add(Box.createVerticalStrut(7));
         moreBlock.add(moreSettings);
         this.addField(row++, "更多设置", moreBlock);
         GridBagConstraints filler = this.constraints(0, row);
         filler.gridwidth = 2;
         filler.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), filler);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.updateRegressConditionalFields();
      }

      private JPanel buildBaselineMoreSettings(String estimator) {
         JPanel panel = new JPanel();
         panel.setOpaque(false);
         panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
         JPanel sampleRow = new JPanel(new GridLayout(1, 2, 8, 0));
         sampleRow.setOpaque(false);
         sampleRow.add(this.miniLabeled("样本条件 if", this.ifCondition));
         sampleRow.add(this.miniLabeled("观测范围 in", this.inCondition));
         panel.add(sampleRow);
         panel.add(Box.createVerticalStrut(12));
         JLabel termsTitle = new JLabel("分类变量、交互项与滞后项");
         termsTitle.setForeground(MUTED);
         termsTitle.setFont(termsTitle.getFont().deriveFont(Font.BOLD));
         termsTitle.setAlignmentX(0.0F);
         panel.add(termsTitle);
         panel.add(Box.createVerticalStrut(7));
         panel.add(this.buildRegressTermBuilder());
         panel.add(Box.createVerticalStrut(12));
         JPanel weightRow = new JPanel(new GridLayout(1, 2, 8, 0));
         weightRow.setOpaque(false);
         weightRow.add(this.miniLabeled("权重类型", this.regressWeightType));
         weightRow.add(this.miniLabeled("权重变量", this.regressWeightVar));
         this.regressWeightVarFieldBlock = weightRow;
         panel.add(weightRow);
         if ("regress".equals(estimator)) {
            panel.add(Box.createVerticalStrut(10));
            JPanel reportRow = new JPanel(new GridLayout(1, 3, 8, 0));
            reportRow.setOpaque(false);
            reportRow.add(this.regressNoConstant);
            reportRow.add(this.regressBeta);
            reportRow.add(this.miniLabeled("置信水平", this.regressLevel));
            panel.add(reportRow);
         }
         panel.add(Box.createVerticalStrut(10));
         panel.add(this.labeledInline("其他 Stata options（高级）", this.regressAdvancedOptions));
         return panel;
      }

      private void updateBaselinePreview() {
         if (!this.baselineTaskActive || this.rebuilding) return;
         String estimator = selected(this.baselineEstimator);
         String y = selected(this.depvar);
         String x = selected(this.regressX);
         LinkedHashSet<String> rhs = new LinkedHashSet<>();
         if (!x.isBlank()) rhs.add(x);
         for (String control : this.regressControls.getSelectedValuesList()) {
            if (!control.equals(y) && !control.equals(x)) rhs.add(control);
         }
         for (int i = 0; i < this.regressSpecialTermsModel.size(); i++) rhs.add(this.regressSpecialTermsModel.get(i));
         StringBuilder command = new StringBuilder(estimator);
         if (!y.isBlank()) command.append(" ").append(y);
         if (!rhs.isEmpty()) command.append(" ").append(String.join(" ", rhs));
         String weight = selected(this.regressWeightType);
         String weightVar = selected(this.regressWeightVar);
         if (!"无".equals(weight) && !weightVar.isBlank()) command.append(" [").append(weight).append("=").append(weightVar).append("]");
         if (!this.ifCondition.getText().trim().isBlank()) command.append(" if ").append(this.ifCondition.getText().trim());
         if (!this.inCondition.getText().trim().isBlank()) command.append(" in ").append(this.inCondition.getText().trim());
         ArrayList<String> opts = new ArrayList<>();
         if ("xtreg".equals(estimator)) {
            String modelText = selected(this.baselineXtModel);
            opts.add(modelText.startsWith("固定") ? "fe" : modelText.startsWith("随机") ? "re" : "be");
         } else if ("reghdfe".equals(estimator) && !this.absorb.getSelectedValuesList().isEmpty()) {
            opts.add("absorb(" + String.join(" ", this.absorb.getSelectedValuesList()) + ")");
         } else if ("areg".equals(estimator) && !this.absorb.getSelectedValuesList().isEmpty()) {
            opts.add("absorb(" + this.absorb.getSelectedValuesList().get(0) + ")");
         }
         if ("robust".equals(selected(this.vce))) opts.add("vce(robust)");
         else if ("cluster".equals(selected(this.vce)) && !selected(this.cluster).isBlank()) opts.add("vce(cluster " + selected(this.cluster) + ")");
         if ("regress".equals(estimator)) {
            if (this.regressNoConstant.isSelected()) opts.add("noconstant");
            if (this.regressBeta.isSelected()) opts.add("beta");
            int level = ((Number)this.regressLevel.getValue()).intValue();
            if (level != 95) opts.add("level(" + level + ")");
         }
         if (!this.regressAdvancedOptions.getText().trim().isBlank()) opts.add(this.regressAdvancedOptions.getText().trim());
         if (!opts.isEmpty()) command.append(", ").append(String.join(" ", opts));
         this.currentCommand = estimator;
         this.rebuilding = true;
         this.previewArea.setText(command.toString().trim());
         this.previewArea.setCaretPosition(0);
         this.rebuilding = false;
         this.flashCommandPreview();
      }

      private boolean validateBaselineBeforeRun() {
         String y = selected(this.depvar);
         String x = selected(this.regressX);
         if (y.isBlank() || x.isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择因变量 Y 和核心解释变量 X。", "基准回归设置尚未完整", 1);
            return false;
         }
         if (y.equals(x)) {
            JOptionPane.showMessageDialog(this, "Y 和核心 X 不能是同一个变量。", "变量角色重复", 2);
            return false;
         }
         if (this.regressControls.getSelectedValuesList().contains(y) || this.regressControls.getSelectedValuesList().contains(x)) {
            JOptionPane.showMessageDialog(this, "Controls 中重复选择了 Y 或核心 X。", "变量角色重复", 2);
            return false;
         }
         String estimator = selected(this.baselineEstimator);
         if ("reghdfe".equals(estimator) && this.absorb.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "reghdfe 至少需要选择 1 个固定效应 absorb()。", "固定效应缺失", 1);
            return false;
         }
         if ("areg".equals(estimator) && this.absorb.getSelectedValuesList().size() != 1) {
            JOptionPane.showMessageDialog(this, "areg 需要且只能选择 1 个固定效应 absorb()。", "固定效应设置尚未完整", 1);
            return false;
         }
         if ("cluster".equals(selected(this.vce)) && selected(this.cluster).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择 Cluster 后，请指定聚类变量。", "聚类变量缺失", 1);
            return false;
         }
         if (!"无".equals(selected(this.regressWeightType)) && selected(this.regressWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后，请指定权重变量。", "权重变量缺失", 1);
            return false;
         }
         return true;
      }

'''
s = s[:idx] + baseline_methods + s[idx:]

# Existing convenience alias now opens the task workspace.
s = replace_once(
    s,
    '''      private void openRegressWorkspace() {\n         this.activeCategoryCode = "reg";\n         this.activeCategoryName = "回归模型";\n         this.activeMethodName = "普通线性回归";\n         this.showCommand("regress");\n      }''',
    '''      private void openRegressWorkspace() {\n         this.openBaselineRegressionWorkspace();\n      }''',
    'baseline alias',
)

# Baseline preview routing and run validation.
s = replace_once(
    s,
    '         if (!this.rebuilding && !this.currentCommand.isBlank()) {\n            if ("regress".equals(this.currentCommand) && this.regressWorkspaceActive) {',
    '         if (!this.rebuilding && !this.currentCommand.isBlank()) {\n            if (this.baselineTaskActive) {\n               this.updateBaselinePreview();\n            } else if ("regress".equals(this.currentCommand) && this.regressWorkspaceActive) {',
    'baseline preview routing',
)
s = replace_once(
    s,
    '''            if (this.validateOrdinaryCommandBeforeRun()\n               && this.validateFocusedEstimationBeforeRun()\n               && (!"regress".equals(this.currentCommand) || !this.regressWorkspaceActive || this.validateRegressBeforeRun())) {''',
    '''            if (this.validateOrdinaryCommandBeforeRun()\n               && (!this.baselineTaskActive || this.validateBaselineBeforeRun())\n               && this.validateFocusedEstimationBeforeRun()\n               && (!"regress".equals(this.currentCommand) || !this.regressWorkspaceActive || this.validateRegressBeforeRun())) {''',
    'baseline run validation',
)

# Preview renderer: regress preview now shows the task workspace.
s = replace_once(s, '                  var19x.showRegressPage();', '                  var19x.openBaselineRegressionWorkspace();', 'baseline render preview')

p.write_text(s, encoding="utf-8")

# -----------------------------------------------------------------------------
# Public version metadata
# -----------------------------------------------------------------------------
p = Path("hxempirical.ado")
s = p.read_text(encoding="utf-8")
s = s.replace('*! hxempirical 1.0.3  12aug2026', '*! hxempirical 1.1.0  12aug2026', 1)
s = s.replace('display as text "版本：" as result "1.0.3"', 'display as text "版本：" as result "1.1.0"', 1)
s = s.replace('return local version "1.0.3"', 'return local version "1.1.0"', 1)
p.write_text(s, encoding="utf-8")

p = Path("hxempirical.pkg")
s = p.read_text(encoding="utf-8").replace('d Version 1.0.3', 'd Version 1.1.0', 1)
p.write_text(s, encoding="utf-8")

p = Path("hxempirical.sthlp")
s = p.read_text(encoding="utf-8")
s = s.replace('{* *! version 1.0.3  12aug2026}{...}', '{* *! version 1.1.0  12aug2026}{...}', 1)
old = '''The start page is a launcher rather than a full function wall. A large task\nsearch sits at the top, six common jobs stay visible, current-data status and up\nto three recent commands appear on the right, and the full function catalog is\ncollapsed until the user explicitly expands it. Selecting a method opens a\ncompact command-choice page. Selecting a command then enters a focused workspace\nand hides the broader navigation. Every command page shows its complete path and\nsimplest example above the settings. Advanced free-text options stay collapsed\nuntil requested; cluster variables appear only when the Cluster standard-error\nchoice is active.\n\n{pstd}\nEach command-choice row explains the Chinese name, purpose, suitable data,\nsimplest example, and the main difference from related commands. Methods with\none to four commands use a compact single-column list. Breadcrumbs and the\nleft-side back action return to the previous method level; the global\n{bf:回到开始} action remains available at the top right. Search covers Stata\nnames, Chinese purposes, suitable-data descriptions, examples, and workflows.'''
new = '''The start page keeps one stable layout. Search and six common research tasks stay\nat the top, current-data status and recent work appear on the right, and the full\nfunction catalog is shown directly below with natural scrolling. There is no\nexpand/collapse state and no reserved blank area.\n\n{pstd}\nResearch tasks can open a task workspace directly. The baseline-regression\nworkspace defaults to {cmd:xtreg} and uses a compact estimator selector to switch\nbetween {cmd:xtreg}, {cmd:reghdfe}, {cmd:areg}, and {cmd:regress} without leaving\nthe page. Y, the core X, controls, sample restrictions, and other common settings\nare preserved while estimator-specific fields and the real Stata command update.\n\n{pstd}\nWhen a method still needs a command chooser, the chooser is a compact directory:\nit shows only the command name, Chinese title, one-line purpose, and source tag.\nDetailed examples and limitations are kept in the command page. Breadcrumbs,\n{bf:上一级}, {bf:首页}, and command help use fixed positions.'''
if old not in s:
    raise SystemExit('missing help architecture block')
s = s.replace(old, new, 1)
s = s.replace('package version 1.0.3', 'package version 1.1.0')
p.write_text(s, encoding="utf-8")

# -----------------------------------------------------------------------------
# README: current version, task-first architecture, cumulative changelog
# -----------------------------------------------------------------------------
p = Path("README.md")
s = p.read_text(encoding="utf-8")
s = s.replace('**当前发布版本：1.0.3**', '**当前发布版本：1.1.0**', 1)
s = s.replace('**上次修改时间：2026-08-12 17:18（UTC+8）**', '**上次修改时间：2026-08-12 19:14（UTC+8）**', 1)
s = s.replace(
    '- **任务式入口与命令搜索**：可以按基准回归、固定效应、工具变量、描述统计、数据处理等研究任务寻找命令，也可以直接搜索 Stata 命令名。',
    '- **任务式工作区与命令搜索**：基准回归等高频研究任务可直接进入工作区；具体估计器只占一个小型切换控件。同时也可以直接搜索 Stata 命令名。',
    1,
)
s = s.replace(
    '普通命令页遵循统一设计：**一个命令对应一个页面，常用参数放前面，低频参数放到“更多设置”中。**',
    '普通功能同时支持**任务入口**和**命令入口**：高频研究任务直接进入稳定工作区，在页内用紧凑下拉框切换真实估计命令；已知具体命令时仍可通过搜索直接打开。常用参数放前面，低频参数放到“更多设置”中。',
    1,
)
changelog = '''### 2026-08-12 19:14（UTC+8）\n\n**修改时间**：2026-08-12 19:14（UTC+8）\n\n**修改内容**：\n\n- 首页取消“展开全部功能 / 收起全部功能”机制，不再为了折叠状态固定上半区高度；完整功能目录直接展示并自然滚动，消除折叠时的大面积空白和展开前后的跳动。\n- “基准回归”升级为任务工作区：点击首页后直接进入，不再先浏览命令卡；默认估计器为 `xtreg`（FE），右上角用小型“估计方法”下拉框切换 `xtreg` / `reghdfe` / `areg` / `regress`。\n- 切换基准回归估计器时保留 Y、核心 X、Controls、样本条件、聚类、权重和已构造项等公共设置，仅替换 `xtreg` 模型、`absorb()` 等估计器特有字段以及最终真实 Stata 命令。\n- 命令选择页改为紧凑目录，不再为每个命令铺设“适合 / 示例 / 区别”大卡片；只保留命令名、中文名称、一句话用途和 `Stata 官方` / `第三方` / `HX Workflow` 来源标签。\n- 修复“普通线性回归 / 固定效应线性回归 / 特殊线性回归 / 分位数回归 / 时间序列线性回归”的 method-code 映射，并在每次读取方法时清除旧命令选择，防止标题已经切换但列表仍残留上一页命令。\n- Java 工作台、JAR、help、package manifest、README 和公开版本信息同步升级为 **1.1.0**。\n\n'''
marker = '## 修改记录\n\n'
if marker not in s:
    raise SystemExit('missing README changelog marker')
s = s.replace(marker, marker + changelog, 1)
version_block = '''### 1.1.0（当前版本）\n\n**发布时间**：2026-08-12 19:14（UTC+8）\n\n**修改内容**：\n\n- 首页改为单一稳定状态，完整功能目录始终显示。\n- 基准回归改为任务工作区，默认 `xtreg`，页内紧凑切换 `reghdfe` / `areg` / `regress` 并保留公共变量设置。\n- 命令选择页压缩为目录式布局，并修复方法切换后的命令列表残留问题。\n\n'''
s = s.replace('### 1.0.3（当前版本）', version_block + '### 1.0.3', 1)
p.write_text(s, encoding="utf-8")

print("HX_TASK_WORKSPACES_110_PATCH_OK")
