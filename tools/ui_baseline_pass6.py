from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/main/java/com/hexie/stata/HxWorkbench.java"
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    text = text.replace(old, new, 1)


def replace_method(signature: str, new_method: str) -> None:
    global text
    start = text.index(signature)
    brace = text.index("{", start)
    depth = 0
    end = None
    for i in range(brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise SystemExit(f"cannot find end for {signature}")
    text = text[:start] + new_method.rstrip() + text[end:]


replace_once(
'''         this.exampleLabel.setText("<html>先设定研究问题，再选择估计方法。默认使用 xtreg；切换估计器时公共变量设置保持不变。</html>");
         this.insightArea.setText("基准回归工作区把研究任务放在前面。默认使用 xtreg（固定效应），也可以在同一页切换 reghdfe、areg 或 regress。切换时保留 Y、核心 X、Controls、样本条件和标准误等公共设置，只替换估计器特有参数和最终 Stata 命令。");
''',
'''         this.exampleLabel.setText("<html>按“选择变量 → 模型与推断 → 检查运行”完成基准回归；右上角可随时切换 xtreg / reghdfe / areg / regress。</html>");
         this.insightArea.setText("基准回归工作区用于在同一研究设定下比较常用线性估计器。默认使用 xtreg（固定效应），也可以切换 reghdfe、areg 或 regress。\n\n切换估计器时保留 Y、核心 X、Controls、样本条件和标准误等公共设置，只替换模型或固定效应等估计器特有参数。\n\n底部始终生成当前估计器的真实 Stata 命令。");
''',
"baseline intro copy",
)
replace_once(
'''         this.statusLabel.setText("基准回归：默认 xtreg；可在右上角切换估计方法，公共变量设置不会清空。");
''',
'''         this.statusLabel.setText("基准回归：按变量 → 模型与推断 → 检查运行组织；切换估计器时公共变量设置保持不变。");
''',
"baseline status copy",
)

new_method = r'''      private void rebuildBaselineForm() {
         String estimator = selected(this.baselineEstimator);
         this.formPanel.removeAll();

         this.enableVariableDrop(this.depvar, "因变量 Y");
         this.enableVariableDrop(this.regressX, "核心解释变量 X");
         this.enableVariableDrop(this.regressControls, "控制变量");
         this.enableVariableDrop(this.absorb, "固定效应");
         this.enableVariableDrop(this.cluster, "聚类变量");
         this.enableVariableDrop(this.regressWeightVar, "权重变量");

         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.genericStepStripV152(true, "选择变量", "模型与推断"), c);

         JPanel variableCard = this.xtregWizardCardV130(1, "选择变量", "Y、核心 X 和控制变量在所有估计器之间共享；切换方法时不会清空。");
         JPanel variableBody = this.genericCardBody();
         JPanel mainVars = new JPanel(new GridLayout(1, 2, 12, 0));
         mainVars.setOpaque(false);
         mainVars.add(this.fieldBlock("因变量 Y", this.depvar));
         mainVars.add(this.fieldBlock("核心解释变量 X", this.regressX));
         this.addGenericBodyField(variableBody, "核心变量", mainVars);
         this.addGenericBodyField(variableBody, "控制变量 Controls（可多选）", this.listPane(this.regressControls));
         variableCard.add(variableBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(variableCard, c);

         String methodSubtitle;
         if ("xtreg".equals(estimator)) {
            methodSubtitle = "当前估计器为 xtreg；先选择 FE / RE / BE，再设置标准误。面板结构沿用当前 Stata xtset。";
         } else if ("reghdfe".equals(estimator)) {
            methodSubtitle = "当前估计器为 reghdfe；选择一个或多个 absorb() 固定效应，再设置标准误。";
         } else if ("areg".equals(estimator)) {
            methodSubtitle = "当前估计器为 areg；选择一个 absorb() 固定效应，再设置标准误。";
         } else {
            methodSubtitle = "当前估计器为 regress；无需模型或固定效应选项，直接设置标准误。";
         }
         JPanel methodCard = this.xtregWizardCardV130(2, "模型与推断 · " + estimator, methodSubtitle);
         JPanel methodBody = this.genericCardBody();
         this.baselineXtModelFieldBlock = null;
         this.baselineAbsorbFieldBlock = null;

         if ("xtreg".equals(estimator)) {
            this.baselineXtModelFieldBlock = (JPanel)this.fieldBlock("模型", this.baselineXtModel);
            this.baselineXtModelFieldBlock.setAlignmentX(0.0F);
            this.baselineXtModelFieldBlock.setMaximumSize(new Dimension(Integer.MAX_VALUE, Math.max(54, this.baselineXtModelFieldBlock.getPreferredSize().height)));
            methodBody.add(this.baselineXtModelFieldBlock);
            methodBody.add(Box.createVerticalStrut(10));
         } else if ("reghdfe".equals(estimator) || "areg".equals(estimator)) {
            this.absorb.setSelectionMode("areg".equals(estimator) ? 0 : 2);
            this.baselineAbsorbFieldBlock = (JPanel)this.fieldBlock(
               "areg".equals(estimator) ? "固定效应 absorb()（选择一个）" : "固定效应 absorb()（可多选）",
               this.listPane(this.absorb)
            );
            this.baselineAbsorbFieldBlock.setAlignmentX(0.0F);
            this.baselineAbsorbFieldBlock.setMaximumSize(new Dimension(Integer.MAX_VALUE, Math.max(54, this.baselineAbsorbFieldBlock.getPreferredSize().height)));
            methodBody.add(this.baselineAbsorbFieldBlock);
            methodBody.add(Box.createVerticalStrut(10));
         }

         this.addGenericBodyField(methodBody, "标准误", this.vce);
         this.regressClusterFieldBlock = (JPanel)this.fieldBlock("聚类变量（仅 Cluster 时需要）", this.cluster);
         this.regressClusterFieldBlock.setAlignmentX(0.0F);
         this.regressClusterFieldBlock.setMaximumSize(new Dimension(Integer.MAX_VALUE, Math.max(54, this.regressClusterFieldBlock.getPreferredSize().height)));
         methodBody.add(this.regressClusterFieldBlock);
         methodBody.add(Box.createVerticalStrut(10));
         methodCard.add(methodBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(methodCard, c);

         JPanel checkCard = this.xtregWizardCardV130(3, "检查运行与更多设置", "样本条件、分类/交互/滞后项、权重和高级 options 集中在这里；默认收起。");
         JPanel checkBody = this.genericCardBody();
         JPanel moreSettings = this.buildBaselineMoreSettings(estimator);
         JToggleButton moreToggle = new JToggleButton("展开样本与更多设置  +");
         styleSecondaryButton(moreToggle);
         moreSettings.setVisible(false);
         moreToggle.setAlignmentX(0.0F);
         moreSettings.setAlignmentX(0.0F);
         moreToggle.addActionListener(event -> {
            boolean expanded = moreToggle.isSelected();
            moreToggle.setText(expanded ? "收起样本与更多设置  −" : "展开样本与更多设置  +");
            moreSettings.setVisible(expanded);
            this.formPanel.revalidate();
            this.formPanel.repaint();
         });
         checkBody.add(moreToggle);
         checkBody.add(Box.createVerticalStrut(8));
         checkBody.add(moreSettings);
         checkCard.add(checkBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(checkCard, c);

         GridBagConstraints filler = this.constraints(0, c.gridy + 1);
         filler.gridwidth = 2;
         filler.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), filler);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.updateRegressConditionalFields();
      }'''
replace_method("      private void rebuildBaselineForm()", new_method)

path.write_text(text, encoding="utf-8")
print("HX_UI_BASELINE_PASS6_OK")
