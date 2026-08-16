from pathlib import Path
import sys

JAVA = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
STATIC = Path('tools/verify_static_contracts.py')


def one(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f'HX_ORDINAL_PATCH_FAIL {label}: {n}', file=sys.stderr)
        raise SystemExit(1)
    return text.replace(old, new)

java = JAVA.read_text(encoding='utf-8')
static = STATIC.read_text(encoding='utf-8')

# Classifier.
java = one(java,
'''      private static boolean isStructuredBinaryOutcomeCommand(String command) {
         return Arrays.asList("binreg", "biprobit", "hetprobit").contains(command);
      }
''',
'''      private static boolean isStructuredOrdinalOutcomeCommand(String command) {
         return Arrays.asList("hetoprobit", "zioprobit", "ziologit").contains(command);
      }

      private static boolean isStructuredBinaryOutcomeCommand(String command) {
         return Arrays.asList("binreg", "biprobit", "hetprobit").contains(command);
      }
''', 'classifier')

# Inspector roles.
java = one(java,
'''         if (isStructuredBinaryOutcomeCommand(this.currentCommand)) {
            if ("binreg".equals(this.currentCommand)) {
''',
'''         if (isStructuredOrdinalOutcomeCommand(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "序数结果 Y";
            if (this.variables.getSelectedValuesList().contains(variable)) return Arrays.asList("zioprobit", "ziologit").contains(this.currentCommand) ? "主 / 强度方程 X" : "均值方程 X";
            if (this.absorb.getSelectedValuesList().contains(variable)) return "hetoprobit".equals(this.currentCommand) ? "方差方程 het()" : "膨胀方程 inflate()";
            if (variable.equals(this.expression.getText().trim())) return "主方程 offset()";
            if (variable.equals(this.newvar.getText().trim())) return "hetoprobit".equals(this.currentCommand) ? "方差方程 offset()" : "inflate() offset()";
         }
         if (isStructuredBinaryOutcomeCommand(this.currentCommand)) {
            if ("binreg".equals(this.currentCommand)) {
''', 'inspector')

# Rebuild route.
java = one(java,
'''         if (isStructuredBinaryOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredBinaryOutcomeForm();
            return;
         }
''',
'''         if (isStructuredOrdinalOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredOrdinalOutcomeForm();
            return;
         }

         if (isStructuredBinaryOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredBinaryOutcomeForm();
            return;
         }
''', 'rebuild route')

# Preview route.
java = one(java,
'''            } else if (isStructuredBinaryOutcomeCommand(this.currentCommand)) {
               this.updateStructuredBinaryOutcomePreview();
''',
'''            } else if (isStructuredOrdinalOutcomeCommand(this.currentCommand)) {
               this.updateStructuredOrdinalOutcomePreview();
            } else if (isStructuredBinaryOutcomeCommand(this.currentCommand)) {
               this.updateStructuredBinaryOutcomePreview();
''', 'preview route')

# Validation route.
java = one(java,
'''         if (isStructuredBinaryOutcomeCommand(command) && !this.validateStructuredBinaryOutcomeBeforeRun()) return false;
''',
'''         if (isStructuredOrdinalOutcomeCommand(command) && !this.validateStructuredOrdinalOutcomeBeforeRun()) return false;
         if (isStructuredBinaryOutcomeCommand(command) && !this.validateStructuredBinaryOutcomeBeforeRun()) return false;
''', 'validation route')

# Correct ordinal weights as a family.
java = one(java,
'''         if (Arrays.asList("logit", "logistic", "binreg", "probit", "biprobit", "hetprobit", "scobit", "cloglog").contains(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "iweight", "pweight");
''',
'''         if (Arrays.asList("logit", "logistic", "binreg", "probit", "biprobit", "hetprobit", "scobit", "cloglog", "ologit", "oprobit", "hetoprobit", "zioprobit", "ziologit").contains(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "iweight", "pweight");
''', 'ordinal weights')

# Offline method preview must match the Stata 17+ registry catalog.
java = one(java,
'''         }          else if ("序数结果".equals(var0)) {
            return Arrays.asList("ologit", "oprobit", "hetoprobit", "zioprobit");
''',
'''         }          else if ("序数结果".equals(var0)) {
            return Arrays.asList("ologit", "oprobit", "hetoprobit", "zioprobit", "ziologit");
''', 'preview catalog')

ordinal_methods = r'''      private static String structuredOrdinalOffset(String raw) {
         String value = raw == null ? "" : raw.trim();
         if (value.isBlank()) return "";
         return value.startsWith("offset(") ? value : "offset(" + value + ")";
      }

      private void rebuildStructuredOrdinalOutcomeForm() {
         String command = this.currentCommand;
         boolean heteroskedastic = "hetoprobit".equals(command);
         boolean zeroInflated = Arrays.asList("zioprobit", "ziologit").contains(command);

         this.model.removeAllItems();
         if (zeroInflated) {
            this.model.addItem("协变量 + 常数");
            this.model.addItem("协变量，不含常数 noconstant");
            this.model.addItem("仅常数 _cons");
            this.model.setSelectedIndex(0);
         }
         this.configureGenericWeightTypes();
         this.genericWeightType.setSelectedItem("无");
         this.genericWeightVar.setSelectedItem(null);

         this.enableVariableDrop(this.depvar, "序数结果 Y");
         this.enableVariableDrop(this.variables, zeroInflated ? "主 / 强度方程 X" : "均值方程 X");
         this.enableVariableDrop(this.absorb, heteroskedastic ? "方差方程 het()" : "膨胀方程 inflate()");
         this.enableVariableDrop(this.expression, "主方程 offset()");
         this.enableVariableDrop(this.newvar, heteroskedastic ? "方差方程 offset()" : "inflate() offset()");

         String title;
         String example;
         String insight;
         String syntax;
         if (heteroskedastic) {
            title = "hetoprobit · 异方差有序 Probit";
            example = "hetoprobit health age bmi i.exercise, het(age)";
            insight = "主方程解释有序结果水平，het() 单独解释潜在误差尺度。Stata 官方要求 het()；只有普通有序 Probit 时应使用 oprobit。";
            syntax = "hetoprobit depvar [indepvars] [if] [in] [weight], het(varlist [, offset(varname)]) [offset(varname) options]";
         } else if ("zioprobit".equals(command)) {
            title = "zioprobit · 零膨胀有序 Probit";
            example = "zioprobit tobacco education income age, inflate(education income i.parent)";
            insight = "最低类别可以来自两种潜在过程：inflate() 的二元 Probit 过程，以及主有序 Probit 过程。inflate() 为必填，两个过程可以使用不同协变量。";
            syntax = "zioprobit depvar [indepvars] [if] [in] [weight], inflate(varlist [, noconstant offset(varname)] | _cons) [offset(varname) options]";
         } else {
            title = "ziologit · 零膨胀有序 Logit";
            example = "ziologit tobacco education income age, inflate(education income i.parent)";
            insight = "最低类别可以来自 inflate() 的二元 Logit 过程或主有序 Logit 过程。inflate() 为必填；需要赔率比显示时可在原生 options 中加入 or。";
            syntax = "ziologit depvar [indepvars] [if] [in] [weight], inflate(varlist [, noconstant offset(varname)] | _cons) [offset(varname) options]";
         }

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
         this.formPanel.add(this.taskStepStripV153("主有序方程", heteroskedastic ? "方差方程" : "最低类别生成方程", "样本与检查"), c);

         JPanel mainCard = this.xtregWizardCardV130(1, "主有序方程", "先选择有序结果 Y 和主方程解释变量。结果变量的具体数字编码不要求等距，但类别顺序必须有实际含义。");
         JPanel mainBody = this.genericCardBody();
         this.addGenericBodyField(mainBody, "序数结果 Y", this.depvar);
         this.addGenericBodyField(mainBody, zeroInflated ? "主 / 强度方程解释变量 X（可选）" : "均值方程解释变量 X（可选）", this.listPane(this.variables));
         this.addGenericBodyField(mainBody, "主方程 offset() 变量（可选）", this.expression);
         mainCard.add(mainBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(mainCard, c);

         JPanel secondCard = this.xtregWizardCardV130(2, heteroskedastic ? "方差方程 het()" : "最低类别生成方程 inflate()", heteroskedastic
            ? "het() 是模型核心且必填；这里的变量解释潜在误差尺度，而不是再次解释结果均值。"
            : "inflate() 是模型核心且必填；可使用协变量建模额外最低类别，也可以选择仅常数 _cons。两套方程的协变量不必相同。");
         JPanel secondBody = this.genericCardBody();
         if (zeroInflated) this.addGenericBodyField(secondBody, "inflate() 形式", this.model);
         this.addGenericBodyField(secondBody, heteroskedastic ? "方差方程变量 het()（必填）" : "膨胀方程变量 inflate()（协变量模式必填）", this.listPane(this.absorb));
         this.addGenericBodyField(secondBody, heteroskedastic ? "het() 内 offset()（可选）" : "inflate() 内 offset()（仅协变量模式，可选）", this.newvar);
         if (zeroInflated) {
            JLabel hint = new JLabel("<html><b>仅常数 _cons</b> 模式会忽略已选 inflate() 变量，并且不允许 inflation offset；切回协变量模式时原选择仍会保留。</html>");
            hint.setForeground(MUTED);
            hint.setFont(hint.getFont().deriveFont(9.8F));
            hint.setAlignmentX(0.0F);
            secondBody.add(hint);
         }
         secondCard.add(secondBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(secondCard, c);

         JPanel sampleCard = this.xtregWizardCardV130(3, "样本与检查", "if / in、权重和低频 Stata options 集中到最后；运行前检查下方实时命令，尤其是两套方程的变量角色。");
         JPanel sampleBody = this.genericCardBody();
         JPanel sampleRow = new JPanel(new GridLayout(1, 2, 10, 0));
         sampleRow.setOpaque(false);
         sampleRow.add(this.fieldBlock("样本条件 if（可选）", this.ifCondition));
         sampleRow.add(this.fieldBlock("观测范围 in（可选）", this.inCondition));
         this.addGenericBodyField(sampleBody, "样本范围", sampleRow);
         JPanel weightRow = new JPanel(new GridLayout(1, 2, 10, 0));
         weightRow.setOpaque(false);
         weightRow.add(this.fieldBlock("权重类型", this.genericWeightType));
         weightRow.add(this.fieldBlock("权重变量", this.genericWeightVar));
         this.addGenericBodyField(sampleBody, "权重（可选）", weightRow);
         this.addGenericBodyField(sampleBody, "其他 Stata options（可选）", this.options);
         sampleCard.add(sampleBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(sampleCard, c);

         GridBagConstraints filler = this.constraints(0, c.gridy + 1);
         filler.gridwidth = 2;
         filler.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), filler);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.rebuilding = false;
         this.updateGenericWeightConditionalFields();
         this.updateStructuredOrdinalOutcomePreview();
         this.statusLabel.setText(command + "：主有序方程与第二过程已分开；复杂低频设置继续使用 Stata 原生 options。 ");
      }

      private void updateStructuredOrdinalOutcomePreview() {
         String command = this.currentCommand;
         boolean heteroskedastic = "hetoprobit".equals(command);
         boolean zeroInflated = Arrays.asList("zioprobit", "ziologit").contains(command);
         StringBuilder preview = new StringBuilder(command);
         String y = selected(this.depvar);
         if (!y.isBlank()) preview.append(" ").append(y);
         List<String> mainX = this.variables.getSelectedValuesList();
         if (!mainX.isEmpty()) preview.append(" ").append(String.join(" ", mainX));
         String ifText = this.ifCondition.getText().trim();
         String inText = this.inCondition.getText().trim();
         if (!ifText.isBlank()) preview.append(" if ").append(ifText);
         if (!inText.isBlank()) preview.append(" in ").append(inText);
         String weightType = selected(this.genericWeightType);
         String weightVar = selected(this.genericWeightVar);
         if (!"无".equals(weightType) && !weightVar.isBlank()) preview.append(" [").append(weightType).append("=").append(weightVar).append("]");

         ArrayList<String> opts = new ArrayList<>();
         List<String> secondX = this.absorb.getSelectedValuesList();
         String secondOffset = structuredOrdinalOffset(this.newvar.getText());
         if (heteroskedastic) {
            if (!secondX.isEmpty()) {
               StringBuilder het = new StringBuilder("het(").append(String.join(" ", secondX));
               if (!secondOffset.isBlank()) het.append(", ").append(secondOffset);
               het.append(")");
               opts.add(het.toString());
            }
         } else if (zeroInflated) {
            int mode = this.model.getSelectedIndex();
            if (mode == 2) {
               opts.add("inflate(_cons)");
            } else if (!secondX.isEmpty()) {
               ArrayList<String> subopts = new ArrayList<>();
               if (mode == 1) subopts.add("noconstant");
               if (!secondOffset.isBlank()) subopts.add(secondOffset);
               StringBuilder inflate = new StringBuilder("inflate(").append(String.join(" ", secondX));
               if (!subopts.isEmpty()) inflate.append(", ").append(String.join(" ", subopts));
               inflate.append(")");
               opts.add(inflate.toString());
            }
         }
         String mainOffset = structuredOrdinalOffset(this.expression.getText());
         if (!mainOffset.isBlank()) opts.add(mainOffset);
         String nativeOptions = this.options.getText().trim();
         if (!nativeOptions.isBlank()) opts.add(nativeOptions);
         if (!opts.isEmpty()) preview.append(", ").append(String.join(" ", opts));

         this.rebuilding = true;
         this.previewArea.setText(preview.toString());
         this.previewArea.setCaretPosition(0);
         this.rebuilding = false;
         this.flashCommandPreview();
      }

      private boolean validateStructuredOrdinalOutcomeBeforeRun() {
         String command = this.currentCommand;
         boolean heteroskedastic = "hetoprobit".equals(command);
         boolean zeroInflated = Arrays.asList("zioprobit", "ziologit").contains(command);
         if (selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, command + " 需要选择序数结果变量 Y。", "结果变量缺失", 1);
            return false;
         }
         if (heteroskedastic && this.absorb.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "hetoprobit 的 het() 方差方程是必填项；请至少选择 1 个尺度解释变量。", "方差方程缺失", 1);
            return false;
         }
         if (zeroInflated) {
            int mode = this.model.getSelectedIndex();
            if (mode != 2 && this.absorb.getSelectedValuesList().isEmpty()) {
               JOptionPane.showMessageDialog(this, command + " 的 inflate() 是必填项；协变量模式下请至少选择 1 个膨胀方程变量，或改为“仅常数 _cons”。", "膨胀方程缺失", 1);
               return false;
            }
            if (mode == 2 && !this.newvar.getText().trim().isBlank()) {
               JOptionPane.showMessageDialog(this, "仅常数 _cons 模式不能同时设置 inflate() 内 offset()；请清空该字段或切换到协变量模式。", "inflate() 形式冲突", 1);
               return false;
            }
         }
         if (!"无".equals(selected(this.genericWeightType)) && selected(this.genericWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后，请指定权重变量。", "权重变量缺失", 1);
            return false;
         }
         return true;
      }

'''
java = one(java,
'''      private void rebuildStructuredBinaryOutcomeForm() {
''', ordinal_methods + '''      private void rebuildStructuredBinaryOutcomeForm() {
''', 'ordinal methods')

# Static: catalog classification, including the Stata 17 conditional entry.
ordinal_classification = '''# Ordinal-outcome Statistics method must remain fully classified, including Stata 17+ ziologit.\nif 'local view "ologit oprobit hetoprobit zioprobit"' not in registry:\n    fail("ordinal-outcome Statistics base catalog not found")\nif 'if c(stata_version) >= 17 local view "`view\' ziologit"' not in registry:\n    fail("ordinal-outcome ziologit Stata 17 gate missing")\nordinal_structured = {"hetoprobit", "zioprobit", "ziologit"}\nordinal_guided_safe = {"ologit", "oprobit"}\n\n'''
static = one(static,
'''# oneclick package knowledge remains correct for compatibility checks.
''', ordinal_classification + '''# oneclick package knowledge remains correct for compatibility checks.
''', 'static classification')

ordinal_contracts = r'''for needle in (
    'private static boolean isStructuredOrdinalOutcomeCommand(String command)',
    '"hetoprobit", "zioprobit", "ziologit"',
    'private void rebuildStructuredOrdinalOutcomeForm()',
    'private void updateStructuredOrdinalOutcomePreview()',
    'private boolean validateStructuredOrdinalOutcomeBeforeRun()',
    'hetoprobit · 异方差有序 Probit',
    'zioprobit · 零膨胀有序 Probit',
    'ziologit · 零膨胀有序 Logit',
    '协变量，不含常数 noconstant',
    '仅常数 _cons',
    'hetoprobit 的 het() 方差方程是必填项',
    '的 inflate() 是必填项',
    'inflate(_cons)',
    'structuredOrdinalOffset(this.expression.getText())',
    'Arrays.asList("logit", "logistic", "binreg", "probit", "biprobit", "hetprobit", "scobit", "cloglog", "ologit", "oprobit", "hetoprobit", "zioprobit", "ziologit")',
    'return Arrays.asList("ologit", "oprobit", "hetoprobit", "zioprobit", "ziologit")',
):
    if needle not in java:
        fail(f"structured ordinal-outcome UI contract missing: {needle}")
for cmd in ordinal_structured:
    if f' {cmd} ' not in semantics:
        fail(f"ordinal structured command lost native-body safety fallback: {cmd}")

'''
static = one(static,
'''for needle in (
    'private static boolean isStructuredBinaryOutcomeCommand(String command)',
''', ordinal_contracts + '''for needle in (
    'private static boolean isStructuredBinaryOutcomeCommand(String command)',
''', 'static contracts')

JAVA.write_text(java, encoding='utf-8')
STATIC.write_text(static, encoding='utf-8')
print('HX_ORDINAL_PATCH_OK')
