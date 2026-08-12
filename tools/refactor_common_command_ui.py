from pathlib import Path

path = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    text = text.replace(old, new, 1)


replace_once(
    '      private final JTextField options = new JTextField();\n      private final JComboBox<String> regressX = variableCombo();',
    '      private final JTextField options = new JTextField();\n      private final JComboBox<String> genericWeightType = new JComboBox<>(new String[]{"无", "fweight", "aweight", "pweight", "iweight"});\n      private final JComboBox<String> genericWeightVar = variableCombo();\n      private final JComboBox<String> regressX = variableCombo();',
    "generic weight fields",
)

replace_once(
    '      private final JToggleButton advancedToggle = new JToggleButton("更多设置  +");\n      private final JPanel advancedContent = new JPanel(new BorderLayout(0, 6));\n      private JPanel clusterFieldBlock;',
    '      private final JToggleButton advancedToggle = new JToggleButton("更多设置  +");\n      private final JPanel advancedContent = new JPanel();\n      private JPanel clusterFieldBlock;\n      private JPanel genericWeightVarFieldBlock;',
    "advanced panel declaration",
)

replace_once(
    '         this.addField(var4++, "解释变量（影响因变量）", this.listPane(this.variables));\n         this.addField(var4++, "标准误方式", this.vce);\n         this.clusterFieldBlock = this.addField(var4++, "聚类变量（仅 Cluster 时需要）", this.cluster);\n         this.clusterFieldBlock.setVisible(false);\n         this.addField(var4++, "筛选条件 if（可选）", this.ifCondition);\n         this.addAdvancedSettings(var4++);',
    '         this.addField(var4++, "解释变量（影响因变量）", this.listPane(this.variables));\n         this.addField(var4++, "标准误方式", this.vce);\n         this.clusterFieldBlock = this.addField(var4++, "聚类变量（仅 Cluster 时需要）", this.cluster);\n         this.clusterFieldBlock.setVisible(false);\n         this.addAdvancedSettings(var4++, true, true, true);',
    "offline preview layout",
)

replace_once(
    '         for (JComboBox var10 : Arrays.asList(this.depvar, this.model, this.panel, this.time, this.vce, this.cluster)) {\n            styleCombo(var10);\n         }',
    '         for (JComboBox var10 : Arrays.asList(this.depvar, this.model, this.panel, this.time, this.vce, this.cluster, this.genericWeightType, this.genericWeightVar)) {\n            styleCombo(var10);\n         }',
    "generic weight styling",
)

replace_once(
    '         this.advancedContent.setOpaque(false);\n         JLabel var14 = new JLabel("仍需手动输入的 Stata options（可留空）");\n         var14.setForeground(MUTED);\n         var14.setFont(var14.getFont().deriveFont(10.5F));\n         this.advancedContent.add(var14, "North");\n         this.advancedContent.add(this.options, "Center");\n         this.advancedContent.setVisible(false);',
    '         this.advancedContent.setOpaque(false);\n         this.advancedContent.setLayout(new BoxLayout(this.advancedContent, BoxLayout.Y_AXIS));\n         this.advancedContent.setVisible(false);',
    "advanced content initialization",
)

replace_once(
    '         this.vce.addActionListener(var1x -> {\n            this.updateConditionalFields();\n            if (this.regressWorkspaceActive) {\n               this.updateRegressConditionalFields();\n            }\n         });',
    '         this.vce.addActionListener(var1x -> {\n            this.updateConditionalFields();\n            if (this.regressWorkspaceActive) {\n               this.updateRegressConditionalFields();\n            }\n         });\n         this.genericWeightType.addActionListener(var1x -> {\n            this.updateGenericWeightConditionalFields();\n            this.schedulePreview();\n         });',
    "generic weight listener",
)

replace_once(
    '            this.cluster,\n            this.ifCondition,\n            this.inCondition,\n            this.options\n         );',
    '            this.cluster,\n            this.ifCondition,\n            this.inCondition,\n            this.genericWeightType,\n            this.genericWeightVar,\n            this.options\n         );',
    "generic preview listeners",
)

replace_once(
    '         replaceComboItems(this.time, var1);\n         replaceComboItems(this.cluster, var1);\n         replaceListItems(this.variables, var1);',
    '         replaceComboItems(this.time, var1);\n         replaceComboItems(this.cluster, var1);\n         replaceComboItems(this.genericWeightVar, var1);\n         replaceListItems(this.variables, var1);',
    "refresh generic weight variable",
)

replace_once(
    '               this.appendOption(var1, "cluster", selected(this.cluster));\n               this.appendOption(var1, "ifcond", this.ifCondition.getText());\n               this.appendOption(var1, "incond", this.inCondition.getText());\n               this.appendOption(var1, "options", this.options.getText());',
    '               this.appendOption(var1, "cluster", selected(this.cluster));\n               this.appendOption(var1, "ifcond", this.ifCondition.getText());\n               this.appendOption(var1, "incond", this.inCondition.getText());\n               String genericWeight = selected(this.genericWeightType);\n               if (!"无".equals(genericWeight)) {\n                  this.appendOption(var1, "weight", genericWeight);\n                  this.appendOption(var1, "weightvar", selected(this.genericWeightVar));\n               }\n               this.appendOption(var1, "options", this.options.getText());',
    "generic weight preview options",
)

replace_once(
    '         if (this.flag("has_if")) {\n            this.addField(var4++, this.sem("if_label"), this.ifCondition);\n         }\n\n         if (this.flag("has_in")) {\n            this.addField(var4++, "观测范围 in（可选）", this.inCondition);\n         }\n\n         this.addAdvancedSettings(var4++);',
    '         this.addAdvancedSettings(var4++, this.flag("has_if"), this.flag("has_in"), this.flag("has_weight"));',
    "move low-frequency fields into more settings",
)

start = text.index("      private void addAdvancedSettings(int var1) {")
end = text.index("\n\n      private void addTaskGroup", start)
new_method = '''      private void addAdvancedSettings(int var1, boolean var2, boolean var3, boolean var4) {
         this.rebuildGenericAdvancedContent(var2, var3, var4);
         this.advancedToggle.setSelected(false);
         this.advancedToggle.setText("更多设置  +");
         this.advancedContent.setVisible(false);
         JPanel var5 = new JPanel();
         var5.setOpaque(false);
         var5.setLayout(new BoxLayout(var5, BoxLayout.Y_AXIS));
         this.advancedToggle.setAlignmentX(0.0F);
         this.advancedContent.setAlignmentX(0.0F);
         var5.add(this.advancedToggle);
         var5.add(Box.createVerticalStrut(7));
         var5.add(this.advancedContent);
         GridBagConstraints var6 = this.constraints(0, var1);
         var6.gridwidth = 2;
         var6.weightx = 1.0;
         var6.fill = 2;
         var6.insets = new Insets(0, 0, 13, 0);
         this.formPanel.add(var5, var6);
      }

      private void rebuildGenericAdvancedContent(boolean var1, boolean var2, boolean var3) {
         this.advancedContent.removeAll();
         this.genericWeightVarFieldBlock = null;
         if (var1) {
            this.advancedContent.add(this.labeledInline("样本条件 if", this.ifCondition));
            this.advancedContent.add(Box.createVerticalStrut(8));
         }

         if (var2) {
            this.advancedContent.add(this.labeledInline("观测范围 in", this.inCondition));
            this.advancedContent.add(Box.createVerticalStrut(8));
         }

         if (var3) {
            JPanel var4 = new JPanel(new GridLayout(1, 2, 8, 0));
            var4.setOpaque(false);
            var4.add(this.miniLabeled("权重类型", this.genericWeightType));
            var4.add(this.miniLabeled("权重变量", this.genericWeightVar));
            this.genericWeightVarFieldBlock = this.labeledInline("权重", var4);
            this.advancedContent.add(this.genericWeightVarFieldBlock);
            this.advancedContent.add(Box.createVerticalStrut(8));
         }

         JLabel var5 = new JLabel("其他 Stata options（高级，可留空）");
         var5.setForeground(MUTED);
         var5.setFont(var5.getFont().deriveFont(10.5F));
         var5.setAlignmentX(0.0F);
         this.options.setMaximumSize(new Dimension(Integer.MAX_VALUE, 32));
         this.advancedContent.add(var5);
         this.advancedContent.add(Box.createVerticalStrut(4));
         this.advancedContent.add(this.options);
         this.updateGenericWeightConditionalFields();
         this.advancedContent.revalidate();
         this.advancedContent.repaint();
      }

      private void updateGenericWeightConditionalFields() {
         boolean var1 = !"无".equals(selected(this.genericWeightType));
         this.genericWeightVar.setEnabled(var1);
         if (!var1) {
            this.genericWeightVar.setSelectedItem(null);
         }
      }'''
text = text[:start] + new_method + text[end:]

replace_once(
    '      private void updateConditionalFields() {\n         if (this.clusterFieldBlock != null) {\n            boolean var1 = "cluster".equalsIgnoreCase(selected(this.vce));\n            this.clusterFieldBlock.setVisible(var1);\n            this.formPanel.revalidate();\n            this.formPanel.repaint();\n         }\n      }',
    '      private void updateConditionalFields() {\n         if (this.clusterFieldBlock != null) {\n            boolean var1 = "cluster".equalsIgnoreCase(selected(this.vce));\n            this.clusterFieldBlock.setVisible(var1);\n         }\n         this.updateGenericWeightConditionalFields();\n         this.formPanel.revalidate();\n         this.formPanel.repaint();\n      }',
    "conditional fields",
)

path.write_text(text, encoding="utf-8")
