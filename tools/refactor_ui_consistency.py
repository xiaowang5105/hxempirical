from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "src/main/java/com/hexie/stata/HxWorkbench.java"


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    a = text.find(start)
    if a < 0:
        raise SystemExit(f"start marker not found: {start}")
    b = text.find(end, a)
    if b < 0:
        raise SystemExit(f"end marker not found: {end}")
    return text[:a] + replacement.rstrip() + "\n\n" + text[b:]


def insert_before(text: str, marker: str, block: str) -> str:
    if block.strip() in text:
        return text
    i = text.find(marker)
    if i < 0:
        raise SystemExit(f"insert marker not found: {marker}")
    return text[:i] + block.rstrip() + "\n\n" + text[i:]


text = JAVA.read_text(encoding="utf-8")

helpers = r'''      private JComponent genericStepStripV150() {
         JPanel strip = cardPanel();
         strip.setBackground(SURFACE);
         strip.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 11),
            new EmptyBorder(9, 10, 9, 10)
         ));
         strip.setLayout(new GridLayout(1, 3, 8, 0));
         String[][] steps = new String[][]{
            {"1", "变量与数据", "先完成数据角色与核心变量"},
            {"2", "模型设定", "再设置模型、固定效应与标准误"},
            {"3", "检查运行", "最后检查低频设置和真实 Stata 命令"}
         };
         for (int i = 0; i < steps.length; i++) {
            JPanel p = new JPanel(new BorderLayout(6, 0));
            p.setOpaque(false);
            p.setMinimumSize(new Dimension(0, 0));
            JComponent n = this.xtregCircleBadge(steps[i][0], i == 0, 24);
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

      private static boolean isGenericPanelEstimator(String command) {
         return Arrays.asList(
            "xtlogit", "xtprobit", "xtpoisson", "xtnbreg", "xtgee", "xttobit", "xtcloglog",
            "xtintreg", "xtoprobit", "xtmlogit", "xtfrontier", "xtabond", "xtdpdsys"
         ).contains(command);
      }

      private JPanel genericCardBody() {
         JPanel body = new JPanel();
         body.setOpaque(false);
         body.setLayout(new BoxLayout(body, BoxLayout.Y_AXIS));
         body.setMinimumSize(new Dimension(0, 0));
         return body;
      }

      private void addGenericBodyField(JPanel body, String label, JComponent component) {
         JComponent block = this.fieldBlock(label, component);
         block.setAlignmentX(0.0F);
         block.setMaximumSize(new Dimension(Integer.MAX_VALUE, Math.max(54, block.getPreferredSize().height)));
         body.add(block);
         body.add(Box.createVerticalStrut(10));
      }

      private boolean ensureGenericPanelDeclarationBeforeRun() {
         if (!isGenericPanelEstimator(this.currentCommand)) return true;
         String panelVar = selected(this.panel);
         String timeVar = selected(this.time);
         if (panelVar.isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择个体 / 面板变量。", "面板结构尚未完整", JOptionPane.INFORMATION_MESSAGE);
            return false;
         }
         String setup = "xtset " + panelVar + (timeVar.isBlank() ? "" : " " + timeVar);
         int rc = HxWorkbench.StataBridge.execute(setup, false);
         if (rc != 0) {
            this.statusLabel.setText("xtset 失败，返回码：" + rc);
            JOptionPane.showMessageDialog(this, "面板结构声明失败：\n" + setup + "\n\n请检查面板键、重复时间或变量类型。", "xtset 失败", JOptionPane.WARNING_MESSAGE);
            return false;
         }
         return true;
      }'''
text = insert_before(text, "      private void rebuildForm() {", helpers)

new_rebuild = r'''      private void rebuildForm() {
         this.rebuilding = true;
         this.formPanel.removeAll();
         this.depvar.setSelectedItem(null);
         this.panel.setSelectedItem(null);
         this.time.setSelectedItem(null);
         this.cluster.setSelectedItem(null);
         this.genericWeightType.setSelectedItem("无");
         this.genericWeightVar.setSelectedItem(null);
         this.variables.clearSelection();
         this.absorb.clearSelection();
         this.endog.clearSelection();
         this.instruments.clearSelection();
         this.newvar.setText("");
         this.expression.setText("");
         this.usingFile.setText("");
         this.ifCondition.setText("");
         this.inCondition.setText("");
         this.options.setText("");
         this.refreshVariableControls();
         this.absorb.setSelectionMode("areg".equals(this.currentCommand) ? 0 : 2);

         String defaultExpression = visibleText(HxWorkbench.StataBridge.characteristic("hxtoolbox_sem_default_expression"));
         if (!defaultExpression.isBlank()) this.expression.setText(defaultExpression);

         this.model.removeAllItems();
         for (String value : HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_schema_models"))) {
            this.model.addItem(value);
         }
         String defaultModel = visibleText(HxWorkbench.StataBridge.characteristic("hxtoolbox_schema_default_model"));
         if (!defaultModel.isBlank() && comboContains(this.model, defaultModel)) this.model.setSelectedItem(defaultModel);

         this.vce.removeAllItems();
         this.vce.addItem("default");
         for (String value : HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_schema_vces"))) {
            if (!"default".equals(value)) this.vce.addItem(value);
         }
         if (this.flag("has_cluster") && !comboContains(this.vce, "cluster")) this.vce.addItem("cluster");

         this.enableVariableDrop(this.depvar, "因变量");
         this.enableVariableDrop(this.variables, "变量 / 解释变量");
         this.enableVariableDrop(this.panel, "个体 / 面板变量");
         this.enableVariableDrop(this.time, "时间变量");
         this.enableVariableDrop(this.absorb, "固定效应");
         this.enableVariableDrop(this.endog, "内生变量");
         this.enableVariableDrop(this.instruments, "工具变量");
         this.enableVariableDrop(this.cluster, "聚类变量");

         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.genericStepStripV150(), c);

         JPanel coreCard = this.xtregWizardCardV130(1, "变量与数据角色", "先完成本命令最核心的数据角色。右侧变量窗口和数据表表头都可以直接拖入。");
         JPanel coreBody = this.genericCardBody();
         boolean hasCore = false;

         if (this.flag("has_depvar")) {
            this.addGenericBodyField(coreBody, this.sem("dep_label"), this.depvar);
            hasCore = true;
         }
         if (this.flag("has_varlist")) {
            this.addGenericBodyField(coreBody, this.sem("vars_label"), this.listPane(this.variables));
            hasCore = true;
         }
         if (this.flag("has_newvar")) {
            this.addGenericBodyField(coreBody, this.sem("newvar_label"), this.newvar);
            hasCore = true;
         }
         if (this.flag("has_expression")) {
            this.addGenericBodyField(coreBody, this.sem("expr_label"), this.expression);
            hasCore = true;
         }
         if (this.flag("has_using")) {
            this.usingLabel.setText(this.sem("using_label"));
            this.addGenericBodyField(coreBody, this.usingLabel.getText(), this.usingChooser());
            hasCore = true;
         }
         if (this.flag("has_iv")) {
            JPanel ivGrid = new JPanel(new GridLayout(1, 2, 12, 0));
            ivGrid.setOpaque(false);
            ivGrid.add(this.fieldBlock(this.sem("endog_label"), this.listPane(this.endog)));
            ivGrid.add(this.fieldBlock(this.sem("inst_label"), this.listPane(this.instruments)));
            this.addGenericBodyField(coreBody, "工具变量设定", ivGrid);
            hasCore = true;
         }

         boolean showPanelStructure = this.flag("needs_panel")
            && !Arrays.asList("reghdfe", "ppmlhdfe", "ivreghdfe").contains(this.currentCommand);
         if (showPanelStructure) {
            JPanel panelGrid = new JPanel(new GridLayout(1, 2, 12, 0));
            panelGrid.setOpaque(false);
            panelGrid.add(this.fieldBlock(this.sem("panel_label"), this.panel));
            panelGrid.add(this.fieldBlock(this.sem("time_label"), this.time));
            this.addGenericBodyField(coreBody, "数据结构", panelGrid);
            hasCore = true;
         }

         if (!hasCore) {
            JLabel noCore = new JLabel("这个命令没有必填变量角色，可直接进入下一步设置参数。");
            noCore.setForeground(MUTED);
            coreBody.add(noCore);
         }
         coreCard.add(coreBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(coreCard, c);

         JPanel modelCard = this.xtregWizardCardV130(2, "模型与估计设置", "常用模型设定集中在这里；只显示当前命令实际支持的选项。");
         JPanel modelBody = this.genericCardBody();
         boolean hasModel = false;

         if (this.model.getItemCount() > 0) {
            this.addGenericBodyField(modelBody, this.sem("model_label"), this.model);
            hasModel = true;
         }
         if (this.flag("has_absorb")) {
            this.addGenericBodyField(modelBody, this.sem("absorb_label"), this.listPane(this.absorb));
            hasModel = true;
         }
         if (this.flag("has_vce")) {
            this.addGenericBodyField(modelBody, "标准误方式", this.vce);
            hasModel = true;
         }
         this.clusterFieldBlock = null;
         if (this.flag("has_cluster")) {
            this.clusterFieldBlock = (JPanel)this.fieldBlock("聚类变量（仅 Cluster 时需要）", this.cluster);
            this.clusterFieldBlock.setAlignmentX(0.0F);
            this.clusterFieldBlock.setMaximumSize(new Dimension(Integer.MAX_VALUE, Math.max(54, this.clusterFieldBlock.getPreferredSize().height)));
            modelBody.add(this.clusterFieldBlock);
            modelBody.add(Box.createVerticalStrut(10));
            hasModel = true;
         }
         if (!hasModel) {
            JLabel defaultModelNote = new JLabel("当前命令没有额外模型选项，将直接使用 Stata 默认设定。");
            defaultModelNote.setForeground(MUTED);
            modelBody.add(defaultModelNote);
         }
         modelCard.add(modelBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(modelCard, c);

         JPanel advancedCard = this.xtregWizardCardV130(3, "检查与更多设置", "样本条件、观测范围、权重和原生 options 放在这里，默认收起。运行前可在下方检查真实 Stata 命令。");
         JPanel advancedBody = this.genericCardBody();
         this.rebuildGenericAdvancedContent(this.flag("has_if"), this.flag("has_in"), this.flag("has_weight"));
         this.advancedContent.setVisible(false);
         JToggleButton advancedToggle = new JToggleButton("展开更多设置  +");
         styleSecondaryButton(advancedToggle);
         advancedToggle.setAlignmentX(0.0F);
         this.advancedContent.setAlignmentX(0.0F);
         advancedToggle.addActionListener(event -> {
            boolean expanded = advancedToggle.isSelected();
            advancedToggle.setText(expanded ? "收起更多设置  −" : "展开更多设置  +");
            this.advancedContent.setVisible(expanded);
            this.formPanel.revalidate();
            this.formPanel.repaint();
         });
         advancedBody.add(advancedToggle);
         advancedBody.add(Box.createVerticalStrut(8));
         advancedBody.add(this.advancedContent);
         advancedCard.add(advancedBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(advancedCard, c);

         GridBagConstraints filler = this.constraints(0, c.gridy + 1);
         filler.gridwidth = 2;
         filler.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), filler);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.rebuilding = false;
         this.updateConditionalFields();
         this.statusLabel.setText(this.currentCommand + "：常用参数已按步骤整理；低频设置默认收起，可从右侧直接拖入变量。");
      }'''
text = replace_between(text, "      private void rebuildForm() {", "      private void showSpecialPage(String var1) {", new_rebuild)

needle = '''               String var1 = this.previewArea.getText().trim();
               if (var1.isEmpty()) {'''
replacement = '''               if (!this.ensureGenericPanelDeclarationBeforeRun()) {
                  return;
               }
               String var1 = this.previewArea.getText().trim();
               if (var1.isEmpty()) {'''
if replacement not in text:
    if needle not in text:
        raise SystemExit("runCurrentCommand insertion point not found")
    text = text.replace(needle, replacement, 1)

needle2 = '''         if (this.flag("has_depvar") && selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择因变量。", "因变量缺失", 1);
            return false;
         }
'''
replacement2 = needle2 + '''
         if (isGenericPanelEstimator(this.currentCommand) && selected(this.panel).isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择个体 / 面板变量；时间变量可按数据结构决定是否填写。", "面板结构尚未完整", 1);
            return false;
         }
'''
if replacement2 not in text:
    if needle2 not in text:
        raise SystemExit("panel validation insertion point not found")
    text = text.replace(needle2, replacement2, 1)

JAVA.write_text(text, encoding="utf-8")
print("HX_UI_CONSISTENCY_REFACTOR_OK")
