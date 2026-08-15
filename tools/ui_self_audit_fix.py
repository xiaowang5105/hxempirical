from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/main/java/com/hexie/stata/HxWorkbench.java"
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    text = text.replace(old, new, 1)


start = text.index("      private JComponent genericStepStripV150() {")
end = text.index("      private static boolean isGenericPanelEstimator", start)
new_strip = r'''      private JComponent genericStepStripV151(boolean hasMethodSettings) {
         JPanel strip = cardPanel();
         strip.setBackground(SURFACE);
         strip.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 11),
            new EmptyBorder(9, 10, 9, 10)
         ));
         String[][] steps = hasMethodSettings
            ? new String[][]{
               {"1", "核心设置", "先完成当前任务最关键的变量、文件或表达式"},
               {"2", "方法与设置", "再设置方法、模型、固定效应或标准误"},
               {"3", "检查运行", "最后检查低频设置和真实 Stata 命令"}
            }
            : new String[][]{
               {"1", "核心设置", "先完成当前任务最关键的变量、文件或表达式"},
               {"2", "检查运行", "最后检查低频设置和真实 Stata 命令"}
            };
         strip.setLayout(new GridLayout(1, steps.length, 8, 0));
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

'''
text = text[:start] + new_strip + text[end:]

replace_once(
    '         if (this.flag("has_cluster") && !comboContains(this.vce, "cluster")) this.vce.addItem("cluster");\n\n         this.enableVariableDrop',
    '         if (this.flag("has_cluster") && !comboContains(this.vce, "cluster")) this.vce.addItem("cluster");\n\n         boolean hasMethodSettings = this.model.getItemCount() > 0\n            || this.flag("has_absorb") || this.flag("has_vce") || this.flag("has_cluster");\n\n         this.enableVariableDrop',
    "insert method settings flag",
)

replace_once(
    "         this.formPanel.add(this.genericStepStripV150(), c);",
    "         this.formPanel.add(this.genericStepStripV151(hasMethodSettings), c);",
    "step strip call",
)

replace_once(
    '         JPanel coreCard = this.xtregWizardCardV130(1, "变量与数据角色", "先完成本命令最核心的数据角色。右侧变量窗口和数据表表头都可以直接拖入。");',
    '         JPanel coreCard = this.xtregWizardCardV130(1, "核心设置", "先完成当前任务最关键的变量、文件或表达式；变量可从右侧变量窗口或数据表表头直接拖入。");',
    "core card title",
)

replace_once(
    '         boolean showPanelStructure = this.flag("needs_panel")\n            && !Arrays.asList("reghdfe", "ppmlhdfe", "ivreghdfe").contains(this.currentCommand);',
    '         boolean showPanelStructure = (this.flag("needs_panel") || isGenericPanelEstimator(this.currentCommand))\n            && !Arrays.asList("reghdfe", "ppmlhdfe", "ivreghdfe").contains(this.currentCommand);',
    "panel visibility",
)

replace_once(
    '            this.addGenericBodyField(coreBody, "数据结构", panelGrid);\n            hasCore = true;',
    '            String panelGroupTitle = Arrays.asList("didregress", "xtdidregress").contains(this.currentCommand)\n               ? "处理与时间设定" : "数据结构";\n            this.addGenericBodyField(coreBody, panelGroupTitle, panelGrid);\n            if (isGenericPanelEstimator(this.currentCommand)) {\n               JLabel setupHint = new JLabel("运行时会先按这里执行 xtset，再运行当前面板模型；时间变量可按数据结构留空。");\n               setupHint.setForeground(MUTED);\n               setupHint.setFont(setupHint.getFont().deriveFont(9.8F));\n               setupHint.setAlignmentX(0.0F);\n               coreBody.add(setupHint);\n               coreBody.add(Box.createVerticalStrut(4));\n            }\n            hasCore = true;',
    "panel group hint",
)

model_start = text.index('         JPanel modelCard = this.xtregWizardCardV130(2, "模型与估计设置"')
model_end = text.index('         JPanel advancedCard = this.xtregWizardCardV130(3, "检查与更多设置"', model_start)
new_model = r'''         this.clusterFieldBlock = null;
         if (hasMethodSettings) {
            JPanel methodCard = this.xtregWizardCardV130(2, "方法与设置", "当前任务支持的方法、模型、固定效应与标准误集中在这里。只显示实际可用的项目。");
            JPanel methodBody = this.genericCardBody();

            if (this.model.getItemCount() > 0) {
               this.addGenericBodyField(methodBody, this.sem("model_label"), this.model);
            }
            if (this.flag("has_absorb")) {
               this.addGenericBodyField(methodBody, this.sem("absorb_label"), this.listPane(this.absorb));
            }
            if (this.flag("has_vce")) {
               this.addGenericBodyField(methodBody, "标准误方式", this.vce);
            }
            if (this.flag("has_cluster")) {
               this.clusterFieldBlock = (JPanel)this.fieldBlock("聚类变量（仅 Cluster 时需要）", this.cluster);
               this.clusterFieldBlock.setAlignmentX(0.0F);
               this.clusterFieldBlock.setMaximumSize(new Dimension(Integer.MAX_VALUE, Math.max(54, this.clusterFieldBlock.getPreferredSize().height)));
               methodBody.add(this.clusterFieldBlock);
               methodBody.add(Box.createVerticalStrut(10));
            }
            methodCard.add(methodBody, BorderLayout.CENTER);
            c.gridy++;
            this.formPanel.add(methodCard, c);
         }

'''
text = text[:model_start] + new_model + text[model_end:]

replace_once(
    '         JPanel advancedCard = this.xtregWizardCardV130(3, "检查与更多设置", "样本条件、观测范围、权重和原生 options 放在这里，默认收起。运行前可在下方检查真实 Stata 命令。");\n         JPanel advancedBody = this.genericCardBody();\n         this.rebuildGenericAdvancedContent(this.flag("has_if"), this.flag("has_in"), this.flag("has_weight"));\n         this.advancedContent.setVisible(false);\n         JToggleButton advancedToggle = new JToggleButton("展开更多设置  +");',
    '         int advancedStep = hasMethodSettings ? 3 : 2;\n         boolean advancedExpandedByDefault = Arrays.asList("keep", "drop").contains(this.currentCommand);\n         String advancedSubtitle = advancedExpandedByDefault\n            ? "当前任务的样本条件直接展开；其余低频参数也在这里。运行前可在下方检查真实 Stata 命令。"\n            : "样本条件、观测范围、权重和原生 options 放在这里，默认收起。运行前可在下方检查真实 Stata 命令。";\n         JPanel advancedCard = this.xtregWizardCardV130(advancedStep, "检查与更多设置", advancedSubtitle);\n         JPanel advancedBody = this.genericCardBody();\n         this.rebuildGenericAdvancedContent(this.flag("has_if"), this.flag("has_in"), this.flag("has_weight"));\n         this.advancedContent.setVisible(advancedExpandedByDefault);\n         JToggleButton advancedToggle = new JToggleButton(advancedExpandedByDefault ? "收起更多设置  −" : "展开更多设置  +", advancedExpandedByDefault);',
    "advanced dynamic behavior",
)

replace_once(
    '         if (!estimators.contains(this.currentCommand)) {\n            return true;\n         }',
    '         if (!estimators.contains(this.currentCommand) && !isGenericPanelEstimator(this.currentCommand)) {\n            return true;\n         }',
    "focused estimator coverage",
)

path.write_text(text, encoding="utf-8")
print("HX_UI_SELF_AUDIT_FIX_OK")
