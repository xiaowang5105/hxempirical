from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
java_path = root / "src/main/java/com/hexie/stata/HxWorkbench.java"
static_path = root / "tools/verify_static_contracts.py"
java = java_path.read_text(encoding="utf-8")
static = static_path.read_text(encoding="utf-8")


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        print(f"HX_PR_SD_PATCH_FAIL {label}: expected 1, found {count}", file=sys.stderr)
        raise SystemExit(1)
    return text.replace(old, new)

# prtest and sdtest share the same three stable official command shapes.
anchor = '''      private static boolean isStructuredSummaryTestCommand(String command) {
         return Arrays.asList("tabulate", "oneway", "ranksum", "median", "signrank", "signtest").contains(command);
      }
'''
replacement = anchor + '''
      private static boolean isStructuredPrSdTestCommand(String command) {
         return Arrays.asList("prtest", "sdtest").contains(command);
      }
'''
java = replace_once(java, anchor, replacement, "pr/sd classifier")

# Build a three-mode form: one-sample, by()-group comparison, or two-variable comparison.
anchor = '''      private void rebuildStructuredSummaryTestForm() {
'''
block = '''      private void rebuildStructuredPrSdTestForm() {
         String command = this.currentCommand;
         boolean proportion = "prtest".equals(command);

         this.model.removeAllItems();
         this.model.addItem("单样本：变量 == 数值");
         this.model.addItem("两组比较：by() 分组");
         this.model.addItem("双变量：变量1 == 变量2");
         this.model.setSelectedIndex(0);

         this.enableVariableDrop(this.depvar, proportion ? "比例变量 1" : "方差变量 1");
         this.enableVariableDrop(this.panel, "分组变量 / 比较变量 2");
         this.enableVariableDrop(this.expression, proportion ? "假设比例" : "假设标准差");

         String title = proportion ? "prtest · 比例检验" : "sdtest · 方差 / 标准差检验";
         String example = proportion ? "prtest foreign == 0.5" : "sdtest mpg == 5";
         String syntax = proportion
            ? "prtest var == #p  |  prtest var, by(group)  |  prtest var1 == var2"
            : "sdtest var == #  |  sdtest var, by(group)  |  sdtest var1 == var2";
         String insight = proportion
            ? "支持 Stata 官方三种比例检验形态：单样本比例与给定值比较、按 by() 比较两个独立组的比例、以及两个变量的比例比较。两组模式的分组变量必须实际只有两个组；cluster()/rho() 等仅在对应 prtest 形态支持时写入原生 options。"
            : "支持 Stata 官方三种标准差 / 方差比较形态：单样本标准差与给定值比较、按 by() 比较两个独立组、以及两个变量的方差比较。传统方差检验依赖正态性较强；若该假设不合适，可另外使用 Stata 官方 robvar 稳健方差检验。";

         this.commandTitle.setText(title);
         this.commandTitle.setToolTipText(title);
         this.exampleLabel.setText("<html><b>最简单例子：</b> " + html(example) + "</html>");
         this.insightArea.setText(insight);
         this.syntaxArea.setText(syntax);

         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.taskStepStripV153("选择检验方式", "填写变量与比较对象", "样本与检查"), c);

         JPanel modeCard = this.xtregWizardCardV130(1, "选择检验方式", "三种模式对应 Stata 官方三套语法；页面只使用当前模式需要的字段生成命令。");
         JPanel modeBody = this.genericCardBody();
         this.addGenericBodyField(modeBody, "检验方式", this.model);
         modeCard.add(modeBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(modeCard, c);

         JPanel coreCard = this.xtregWizardCardV130(2, "填写变量与比较对象", "变量 1 始终必选；单样本填写数值，两组 / 双变量模式再选择右侧变量。");
         JPanel coreBody = this.genericCardBody();
         this.addGenericBodyField(coreBody, proportion ? "比例变量 1（通常为 0/1）" : "方差 / 标准差变量 1", this.depvar);
         this.addGenericBodyField(coreBody, "分组变量 / 比较变量 2（两组或双变量模式）", this.panel);
         this.addGenericBodyField(coreBody, proportion ? "假设比例（单样本模式，0–1）" : "假设标准差（单样本模式，>0）", this.expression);
         JLabel modeHint = new JLabel("<html>两组模式自动生成 <b>by(group)</b>；双变量模式自动生成 <b>var1 == var2</b>。未被当前模式使用的字段不会进入命令。</html>");
         modeHint.setForeground(MUTED);
         modeHint.setFont(modeHint.getFont().deriveFont(9.8F));
         modeHint.setAlignmentX(0.0F);
         coreBody.add(modeHint);
         if (!proportion) {
            coreBody.add(Box.createVerticalStrut(5));
            JLabel robustHint = new JLabel("<html>数据明显偏离正态时，可考虑单独使用官方 <b>robvar var, by(group)</b>；本页不会自动把 sdtest 改成其他命令。</html>");
            robustHint.setForeground(MUTED);
            robustHint.setFont(robustHint.getFont().deriveFont(9.8F));
            robustHint.setAlignmentX(0.0F);
            coreBody.add(robustHint);
         }
         coreCard.add(coreBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(coreCard, c);

         JPanel checkCard = this.xtregWizardCardV130(3, "样本与检查", "if / in 与原生 options 集中在这里；运行前检查下方生成的真实 Stata 命令。");
         JPanel checkBody = this.genericCardBody();
         JPanel sampleRow = new JPanel(new GridLayout(1, 2, 10, 0));
         sampleRow.setOpaque(false);
         sampleRow.add(this.fieldBlock("样本条件 if（可选）", this.ifCondition));
         sampleRow.add(this.fieldBlock("观测范围 in（可选）", this.inCondition));
         this.addGenericBodyField(checkBody, "样本范围", sampleRow);
         this.addGenericBodyField(checkBody, "其他 Stata options（可选）", this.options);
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
         this.rebuilding = false;
         this.updateStructuredPrSdTestPreview();
         this.statusLabel.setText(command + "：已按单样本 / 两组 / 双变量三种官方形态拆分。");
      }

      private void updateStructuredPrSdTestPreview() {
         String command = this.currentCommand;
         int mode = this.model.getSelectedIndex();
         String first = selected(this.depvar);
         String second = selected(this.panel);
         String hypothesized = this.expression.getText().trim();
         StringBuilder preview = new StringBuilder(command);
         if (!first.isBlank()) preview.append(" ").append(first);
         if (mode == 0 && !hypothesized.isBlank()) preview.append(" == ").append(hypothesized);
         else if (mode == 2 && !second.isBlank()) preview.append(" == ").append(second);

         if (!this.ifCondition.getText().trim().isBlank()) preview.append(" if ").append(this.ifCondition.getText().trim());
         if (!this.inCondition.getText().trim().isBlank()) preview.append(" in ").append(this.inCondition.getText().trim());

         ArrayList<String> opts = new ArrayList<>();
         if (mode == 1 && !second.isBlank()) opts.add("by(" + second + ")");
         if (!this.options.getText().trim().isBlank()) opts.add(this.options.getText().trim());
         if (!opts.isEmpty()) preview.append(", ").append(String.join(" ", opts));

         this.rebuilding = true;
         this.previewArea.setText(preview.toString());
         this.previewArea.setCaretPosition(0);
         this.rebuilding = false;
         this.flashCommandPreview();
      }

      private void rebuildStructuredSummaryTestForm() {
'''
java = replace_once(java, anchor, block, "pr/sd form and preview")

# Route before the existing six-command structured summary-test family.
anchor = '''         if (isStructuredSummaryTestCommand(this.currentCommand)) {
            this.rebuildStructuredSummaryTestForm();
            return;
         }
'''
replacement = '''         if (isStructuredPrSdTestCommand(this.currentCommand)) {
            this.rebuildStructuredPrSdTestForm();
            return;
         }

''' + anchor
java = replace_once(java, anchor, replacement, "form route")

anchor = '''            } else if (isStructuredSummaryTestCommand(this.currentCommand)) {
               this.updateStructuredSummaryTestPreview();
'''
replacement = '''            } else if (isStructuredPrSdTestCommand(this.currentCommand)) {
               this.updateStructuredPrSdTestPreview();
            } else if (isStructuredSummaryTestCommand(this.currentCommand)) {
               this.updateStructuredSummaryTestPreview();
'''
java = replace_once(java, anchor, replacement, "preview route")

# Inspector reflects the selected mode rather than calling every second field a generic X.
anchor = '''         if ("tabulate".equals(this.currentCommand)) {
'''
replacement = '''         if (isStructuredPrSdTestCommand(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "prtest".equals(this.currentCommand) ? "比例变量 1" : "方差变量 1";
            if (variable.equals(selected(this.panel))) return this.model.getSelectedIndex() == 1 ? "分组变量" : "比较变量 2";
         }
''' + anchor
java = replace_once(java, anchor, replacement, "inspector roles")

# Validate only the fields relevant to the selected mode.
anchor = '''      private boolean validateOrdinaryCommandBeforeRun() {
         String command = this.currentCommand;
'''
replacement = anchor + '''         if (isStructuredPrSdTestCommand(command)) {
            String first = selected(this.depvar);
            String second = selected(this.panel);
            int mode = this.model.getSelectedIndex();
            if (first.isBlank()) {
               JOptionPane.showMessageDialog(this, command + " 需要选择第一个检验变量。", "检验设置尚未完整", 1);
               return false;
            }
            if (mode == 0) {
               String valueText = this.expression.getText().trim();
               try {
                  double value = Double.parseDouble(valueText);
                  if ("prtest".equals(command) && (value < 0.0 || value > 1.0)) throw new NumberFormatException();
                  if ("sdtest".equals(command) && !(value > 0.0)) throw new NumberFormatException();
               } catch (NumberFormatException ex) {
                  JOptionPane.showMessageDialog(this,
                     "prtest".equals(command) ? "单样本 prtest 的假设比例必须是 0 到 1 之间的数值。" : "单样本 sdtest 的假设标准差必须是正数。",
                     "假设值无效", 1);
                  return false;
               }
            } else {
               if (second.isBlank()) {
                  JOptionPane.showMessageDialog(this, mode == 1 ? "两组模式需要选择 by() 分组变量。" : "双变量模式需要选择第二个比较变量。", "检验设置尚未完整", 1);
                  return false;
               }
               if (first.equals(second)) {
                  JOptionPane.showMessageDialog(this, "第一个检验变量与分组 / 第二变量不能相同。", "检验变量角色重复", 2);
                  return false;
               }
            }
         }
'''
java = replace_once(java, anchor, replacement, "validation")

# Static contracts for all three official command shapes and robust-variance guidance.
anchor = '''for needle in (
    'private static boolean isStructuredSummaryTestCommand(String command)',
'''
block = '''for needle in (
    'private static boolean isStructuredPrSdTestCommand(String command)',
    'return Arrays.asList("prtest", "sdtest").contains(command);',
    'private void rebuildStructuredPrSdTestForm()',
    'private void updateStructuredPrSdTestPreview()',
    'prtest · 比例检验',
    'sdtest · 方差 / 标准差检验',
    '单样本：变量 == 数值',
    '两组比较：by() 分组',
    '双变量：变量1 == 变量2',
    'opts.add("by(" + second + ")")',
    'robvar var, by(group)',
    '单样本 prtest 的假设比例必须是 0 到 1 之间的数值',
    '单样本 sdtest 的假设标准差必须是正数',
    '两组模式需要选择 by() 分组变量',
    '双变量模式需要选择第二个比较变量',
):
    if needle not in java:
        fail(f"structured prtest/sdtest UI contract missing: {needle}")

''' + anchor
static = replace_once(static, anchor, block, "static contracts")

java_path.write_text(java, encoding="utf-8")
static_path.write_text(static, encoding="utf-8")
print("HX_PR_SD_PATCH_OK")
