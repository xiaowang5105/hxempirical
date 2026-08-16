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
        print(f"HX_LINEAR_RELATED_PATCH_FAIL {label}: expected 1, found {count}", file=sys.stderr)
        raise SystemExit(1)
    return text.replace(old, new)


# Classify the linear-related commands whose core roles are stable enough for a guided page.
anchor = '''      private static boolean isStructuredPrSdTestCommand(String command) {
'''
insert = '''      private static boolean isStructuredLinearRelatedCommand(String command) {
         return Arrays.asList("hetregress", "intreg", "tobit", "truncreg", "sqreg").contains(command);
      }

      private static boolean isStructuredPrSdTestCommand(String command) {
'''
java = replace_once(java, anchor, insert, "linear-related classifier")

# Guided pages for heteroskedastic, censored/truncated, interval, and simultaneous-quantile regression.
anchor = '''      private void rebuildStructuredPrSdTestForm() {
'''
helper = r'''      private void rebuildStructuredLinearRelatedForm() {
         String command = this.currentCommand;
         boolean hetregress = "hetregress".equals(command);
         boolean intreg = "intreg".equals(command);
         boolean tobit = "tobit".equals(command);
         boolean truncreg = "truncreg".equals(command);
         boolean sqreg = "sqreg".equals(command);

         this.enableVariableDrop(this.depvar, intreg ? "区间下端点" : "结果变量 Y");
         this.enableVariableDrop(this.panel, "区间上端点");
         this.enableVariableDrop(this.expression, tobit || truncreg ? "下界" : (sqreg ? "分位点" : "模型特有设置"));
         this.enableVariableDrop(this.newvar, tobit || truncreg ? "上界" : "重复次数");

         this.model.removeAllItems();
         if (hetregress) {
            this.model.addItem("Maximum likelihood（默认）");
            this.model.addItem("Two-step GLS");
         }

         this.genericWeightType.removeAllItems();
         List<String> weightTypes = sqreg
            ? Collections.singletonList("无")
            : Arrays.asList("无", "fweight", "aweight", "pweight", "iweight");
         for (String type : weightTypes) this.genericWeightType.addItem(type);
         this.genericWeightType.setSelectedItem("无");
         this.genericWeightVar.setSelectedItem(null);
         this.genericWeightVar.setEnabled(false);

         String title;
         String example;
         String insight;
         String syntax;
         String coreTitle;
         String coreSubtitle;
         String methodTitle;
         String methodSubtitle;

         if (hetregress) {
            title = "hetregress · 异方差线性回归";
            example = "hetregress y x1 x2, het(z1 z2)";
            insight = "均值方程与方差方程分开设置。默认使用 maximum likelihood；Two-step GLS 时 Stata 要求同时指定 het() 方差方程，且该估计方式不接受权重。";
            syntax = "hetregress depvar [indepvars] [if] [in] [weight] [, mle_options]  |  hetregress depvar [indepvars] [if] [in], twostep het(varlist) [ts_options]";
            coreTitle = "均值方程";
            coreSubtitle = "选择连续结果变量和均值方程中的解释变量。";
            methodTitle = "方差方程与估计方法";
            methodSubtitle = "het() 中的变量用于解释残差方差；Two-step GLS 必须指定至少一个方差方程变量。";
         } else if (intreg) {
            title = "intreg · 区间回归";
            example = "intreg y_lower y_upper x1 x2";
            insight = "区间回归需要两个结果端点。左删失用下端点缺失、右删失用上端点缺失；点数据可让两个端点相等。可选 het() 用另一组变量建模条件方差。";
            syntax = "intreg depvar_lower depvar_upper [indepvars] [if] [in] [weight] [, options]";
            coreTitle = "区间结果与解释变量";
            coreSubtitle = "下端点和上端点都必须指定；它们可以是同一变量以表示精确观测。";
            methodTitle = "条件方差（可选）";
            methodSubtitle = "需要显式建模异方差时，在 het() 中选择方差方程变量；否则留空。";
         } else if (tobit) {
            title = "tobit · 删失回归";
            example = "tobit y x1 x2, ll(0)";
            insight = "删失意味着结果在界限之外仍有观测记录，但真实潜在值不可见。ll()/ul() 可填写常数或变量名；本页还支持输入 min / max 生成 Stata 的裸 ll / ul，使用样本最小值或最大值作为删失点。";
            syntax = "tobit depvar [indepvars] [if] [in] [weight] [, ll[(varname | #)] ul[(varname | #)] options]";
            coreTitle = "结果与解释变量";
            coreSubtitle = "先选择删失结果变量和解释变量。";
            methodTitle = "删失界限";
            methodSubtitle = "至少设置一个界限；数字或变量名会生成 ll()/ul()，min/max 分别生成裸 ll/ul。";
         } else if (truncreg) {
            title = "truncreg · 截断回归";
            example = "truncreg y x1 x2, ll(16)";
            insight = "截断与删失不同：界限之外的结果和协变量整条观测都不进入样本。ll()/ul() 可以是固定数值，也可以是逐观测变化的变量。";
            syntax = "truncreg depvar [indepvars] [if] [in] [weight] [, ll(varname | #) ul(varname | #) options]";
            coreTitle = "结果与解释变量";
            coreSubtitle = "选择截断样本中的结果变量和解释变量。";
            methodTitle = "截断界限";
            methodSubtitle = "至少设置一个截断点；可填数值或包含逐观测截断点的变量名。";
         } else {
            title = "sqreg · 同时分位数回归";
            example = "sqreg y x1 x2, quantiles(.25 .5 .75) reps(100)";
            insight = "一次估计多个条件分位数，并通过 bootstrap 得到包含跨分位协方差块的 VCE，适合直接比较不同分位上的系数。sqreg 不接受权重。";
            syntax = "sqreg depvar [indepvars] [if] [in] [, quantiles(# ...) reps(#) options]";
            coreTitle = "结果与解释变量";
            coreSubtitle = "Y 与 X 的角色和普通线性回归一致，但目标是多个条件分位数。";
            methodTitle = "分位点与 Bootstrap";
            methodSubtitle = "分位点可写 .25 .5 .75，也可写 25 50 75；reps() 为正整数。";
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
         this.formPanel.add(this.taskStepStripV153(coreTitle, methodTitle, "样本与选项"), c);

         JPanel coreCard = this.xtregWizardCardV130(1, coreTitle, coreSubtitle);
         JPanel coreBody = this.genericCardBody();
         if (intreg) {
            JPanel bounds = new JPanel(new GridLayout(1, 2, 10, 0));
            bounds.setOpaque(false);
            bounds.add(this.fieldBlock("下端点 depvar1", this.depvar));
            bounds.add(this.fieldBlock("上端点 depvar2", this.panel));
            this.addGenericBodyField(coreBody, "区间结果", bounds);
         } else {
            this.addGenericBodyField(coreBody, "结果变量 Y", this.depvar);
         }
         this.addGenericBodyField(coreBody, "解释变量 X（可多选）", this.listPane(this.variables));
         coreCard.add(coreBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(coreCard, c);

         JPanel methodCard = this.xtregWizardCardV130(2, methodTitle, methodSubtitle);
         JPanel methodBody = this.genericCardBody();
         if (hetregress) {
            this.addGenericBodyField(methodBody, "估计方法", this.model);
            this.addGenericBodyField(methodBody, "方差方程变量 het()（ML 可留空；Two-step 必填）", this.listPane(this.absorb));
         } else if (intreg) {
            this.addGenericBodyField(methodBody, "方差方程变量 het()（可选）", this.listPane(this.absorb));
         } else if (tobit || truncreg) {
            JPanel limits = new JPanel(new GridLayout(1, 2, 10, 0));
            limits.setOpaque(false);
            String lowerLabel = tobit ? "下删失点 ll()：数字 / 变量 / min" : "下截断点 ll()：数字 / 变量";
            String upperLabel = tobit ? "上删失点 ul()：数字 / 变量 / max" : "上截断点 ul()：数字 / 变量";
            limits.add(this.fieldBlock(lowerLabel, this.expression));
            limits.add(this.fieldBlock(upperLabel, this.newvar));
            this.addGenericBodyField(methodBody, "界限设置", limits);
         } else {
            JPanel quantiles = new JPanel(new GridLayout(1, 2, 10, 0));
            quantiles.setOpaque(false);
            quantiles.add(this.fieldBlock("quantiles()（默认 .5）", this.expression));
            quantiles.add(this.fieldBlock("reps()（默认 20）", this.newvar));
            this.addGenericBodyField(methodBody, "同时估计的分位点", quantiles);
         }
         methodCard.add(methodBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(methodCard, c);

         JPanel sampleCard = this.xtregWizardCardV130(3, "样本与选项", "样本范围与原生 options 放在最后；页面只自动生成已经明确拆出的核心结构。复杂 offset()/constraints()/VCE 等仍可直接写入 options。");
         JPanel sampleBody = this.genericCardBody();
         JPanel sampleRow = new JPanel(new GridLayout(1, 2, 10, 0));
         sampleRow.setOpaque(false);
         sampleRow.add(this.fieldBlock("样本条件 if（可选）", this.ifCondition));
         sampleRow.add(this.fieldBlock("观测范围 in（可选）", this.inCondition));
         this.addGenericBodyField(sampleBody, "样本范围", sampleRow);
         if (!sqreg) {
            JPanel weightRow = new JPanel(new GridLayout(1, 2, 10, 0));
            weightRow.setOpaque(false);
            weightRow.add(this.fieldBlock("权重类型", this.genericWeightType));
            weightRow.add(this.fieldBlock("权重变量", this.genericWeightVar));
            this.addGenericBodyField(sampleBody, "权重（可选）", weightRow);
         }
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
         this.updateStructuredLinearRelatedPreview();
         this.statusLabel.setText(command + "：核心模型角色已拆开；复杂低频设置继续保留 Stata 原生 options。 ");
      }

      private static String structuredLimitOption(String kind, String raw, boolean allowBareExtremum) {
         String value = raw == null ? "" : raw.trim();
         if (value.isBlank()) return "";
         if (allowBareExtremum && "ll".equals(kind) && "min".equalsIgnoreCase(value)) return "ll";
         if (allowBareExtremum && "ul".equals(kind) && "max".equalsIgnoreCase(value)) return "ul";
         if (value.equals(kind) || value.startsWith(kind + "(")) return value;
         return kind + "(" + value + ")";
      }

      private void updateStructuredLinearRelatedPreview() {
         String command = this.currentCommand;
         boolean hetregress = "hetregress".equals(command);
         boolean intreg = "intreg".equals(command);
         boolean tobit = "tobit".equals(command);
         boolean truncreg = "truncreg".equals(command);
         boolean sqreg = "sqreg".equals(command);

         StringBuilder preview = new StringBuilder(command);
         String y = selected(this.depvar);
         if (!y.isBlank()) preview.append(" ").append(y);
         if (intreg) {
            String upper = selected(this.panel);
            if (!upper.isBlank()) preview.append(" ").append(upper);
         }
         List<String> xs = this.variables.getSelectedValuesList();
         if (!xs.isEmpty()) preview.append(" ").append(String.join(" ", xs));

         String ifText = this.ifCondition.getText().trim();
         String inText = this.inCondition.getText().trim();
         if (!ifText.isBlank()) preview.append(" if ").append(ifText);
         if (!inText.isBlank()) preview.append(" in ").append(inText);

         String weightType = selected(this.genericWeightType);
         String weightVar = selected(this.genericWeightVar);
         if (!sqreg && !"无".equals(weightType) && !weightVar.isBlank()) {
            preview.append(" [").append(weightType).append("=").append(weightVar).append("]");
         }

         ArrayList<String> opts = new ArrayList<>();
         if (hetregress) {
            if (this.model.getSelectedIndex() == 1) opts.add("twostep");
            List<String> hetVars = this.absorb.getSelectedValuesList();
            if (!hetVars.isEmpty()) opts.add("het(" + String.join(" ", hetVars) + ")");
         } else if (intreg) {
            List<String> hetVars = this.absorb.getSelectedValuesList();
            if (!hetVars.isEmpty()) opts.add("het(" + String.join(" ", hetVars) + ")");
         } else if (tobit || truncreg) {
            String lower = structuredLimitOption("ll", this.expression.getText(), tobit);
            String upper = structuredLimitOption("ul", this.newvar.getText(), tobit);
            if (!lower.isBlank()) opts.add(lower);
            if (!upper.isBlank()) opts.add(upper);
         } else if (sqreg) {
            String qs = this.expression.getText().trim().replace(',', ' ');
            qs = qs.replaceAll("\\s+", " ").trim();
            String reps = this.newvar.getText().trim();
            if (!qs.isBlank()) opts.add("quantiles(" + qs + ")");
            if (!reps.isBlank()) opts.add("reps(" + reps + ")");
         }
         String nativeOptions = this.options.getText().trim();
         if (!nativeOptions.isBlank()) opts.add(nativeOptions);
         if (!opts.isEmpty()) preview.append(", ").append(String.join(" ", opts));

         this.rebuilding = true;
         this.previewArea.setText(preview.toString());
         this.previewArea.setCaretPosition(0);
         this.rebuilding = false;
         this.flashCommandPreview();
      }

      private boolean validateStructuredLinearRelatedBeforeRun() {
         String command = this.currentCommand;
         boolean hetregress = "hetregress".equals(command);
         boolean intreg = "intreg".equals(command);
         boolean tobit = "tobit".equals(command);
         boolean truncreg = "truncreg".equals(command);
         boolean sqreg = "sqreg".equals(command);

         if (selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, intreg ? "intreg 需要选择区间下端点 depvar1。" : command + " 需要选择结果变量 Y。", "模型变量尚未完整", 1);
            return false;
         }
         if (intreg && selected(this.panel).isBlank()) {
            JOptionPane.showMessageDialog(this, "intreg 需要选择区间上端点 depvar2。", "区间端点尚未完整", 1);
            return false;
         }
         if (hetregress && this.model.getSelectedIndex() == 1 && this.absorb.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "hetregress 的 Two-step GLS 必须选择至少 1 个 het() 方差方程变量。", "方差方程尚未完整", 1);
            return false;
         }
         if (hetregress && this.model.getSelectedIndex() == 1 && !"无".equals(selected(this.genericWeightType))) {
            JOptionPane.showMessageDialog(this, "hetregress 的 Two-step GLS 不接受权重；请把权重类型改为“无”，或改用 Maximum likelihood。", "Two-step GLS 不支持权重", 1);
            return false;
         }
         if ((tobit || truncreg) && this.expression.getText().trim().isBlank() && this.newvar.getText().trim().isBlank()) {
            JOptionPane.showMessageDialog(this, command + " 至少需要设置一个 ll()/ul() 界限；无删失/截断的普通连续结果请优先使用 regress。", "界限尚未设置", 1);
            return false;
         }
         if (sqreg) {
            String qtext = this.expression.getText().trim().replace(',', ' ');
            if (!qtext.isBlank()) {
               String[] parts = qtext.split("\\s+");
               for (String part : parts) {
                  try {
                     double q = Double.parseDouble(part);
                     boolean valid = (q > 0.0 && q < 1.0) || (q > 1.0 && q < 100.0);
                     if (!valid) throw new NumberFormatException();
                  } catch (NumberFormatException ex) {
                     JOptionPane.showMessageDialog(this, "sqreg 的 quantiles() 必须是 0–1 之间的小数，或 1–100 之间的百分数，例如 .25 .5 .75 或 25 50 75。", "分位点无效", 1);
                     return false;
                  }
               }
            }
            String reps = this.newvar.getText().trim();
            if (!reps.isBlank()) {
               try {
                  if (Integer.parseInt(reps) <= 0) throw new NumberFormatException();
               } catch (NumberFormatException ex) {
                  JOptionPane.showMessageDialog(this, "sqreg 的 reps() 必须是正整数，例如 100。", "Bootstrap 次数无效", 1);
                  return false;
               }
            }
         }
         if (!sqreg && !"无".equals(selected(this.genericWeightType)) && selected(this.genericWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后，请指定权重变量。", "权重变量缺失", 1);
            return false;
         }
         return true;
      }

      private void rebuildStructuredPrSdTestForm() {
'''
java = replace_once(java, anchor, helper, "linear-related helpers")

# Route structured pages before command_body fallback.
anchor = '''         if (isStructuredPrSdTestCommand(this.currentCommand)) {
            this.rebuildStructuredPrSdTestForm();
            return;
         }
'''
replacement = '''         if (isStructuredLinearRelatedCommand(this.currentCommand)) {
            this.rebuildStructuredLinearRelatedForm();
            return;
         }

         if (isStructuredPrSdTestCommand(this.currentCommand)) {
            this.rebuildStructuredPrSdTestForm();
            return;
         }
'''
java = replace_once(java, anchor, replacement, "linear-related rebuild route")

# Build the real Stata command locally for these structured pages.
anchor = '''            } else if (isStructuredPrSdTestCommand(this.currentCommand)) {
               this.updateStructuredPrSdTestPreview();
'''
replacement = '''            } else if (isStructuredLinearRelatedCommand(this.currentCommand)) {
               this.updateStructuredLinearRelatedPreview();
            } else if (isStructuredPrSdTestCommand(this.currentCommand)) {
               this.updateStructuredPrSdTestPreview();
'''
java = replace_once(java, anchor, replacement, "linear-related preview route")

# Inspector roles must describe the actual statistical role, not generic panel/FE labels.
anchor = '''         if (isStructuredPrSdTestCommand(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "prtest".equals(this.currentCommand) ? "比例变量 1" : "方差变量 1";
'''
replacement = '''         if (isStructuredLinearRelatedCommand(this.currentCommand)) {
            if ("intreg".equals(this.currentCommand)) {
               if (variable.equals(selected(this.depvar))) return "区间下端点";
               if (variable.equals(selected(this.panel))) return "区间上端点";
               if (this.variables.getSelectedValuesList().contains(variable)) return "解释变量 X";
               if (this.absorb.getSelectedValuesList().contains(variable)) return "方差方程 het()";
            } else {
               if (variable.equals(selected(this.depvar))) return "结果变量 Y";
               if (this.variables.getSelectedValuesList().contains(variable)) return "解释变量 X";
               if ("hetregress".equals(this.currentCommand) && this.absorb.getSelectedValuesList().contains(variable)) return "方差方程 het()";
               if (Arrays.asList("tobit", "truncreg").contains(this.currentCommand)) {
                  if (variable.equals(this.expression.getText().trim())) return "下界 ll()";
                  if (variable.equals(this.newvar.getText().trim())) return "上界 ul()";
               }
            }
         }
         if (isStructuredPrSdTestCommand(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "prtest".equals(this.currentCommand) ? "比例变量 1" : "方差变量 1";
'''
java = replace_once(java, anchor, replacement, "linear-related inspector roles")

# Validate structured pages in the shared run gate.
anchor = '''      private boolean validateOrdinaryCommandBeforeRun() {
         String command = this.currentCommand;
         if (isStructuredPrSdTestCommand(command)) {
'''
replacement = '''      private boolean validateOrdinaryCommandBeforeRun() {
         String command = this.currentCommand;
         if (isStructuredLinearRelatedCommand(command) && !this.validateStructuredLinearRelatedBeforeRun()) return false;
         if (isStructuredPrSdTestCommand(command)) {
'''
java = replace_once(java, anchor, replacement, "linear-related validation route")

# Stata accepts percentile notation above 1 for qreg quantile(); do not reject 25/50/75.
old = '''               double q = Double.parseDouble(structured);
               if (!(q > 0.0 && q < 1.0)) {
                  throw new NumberFormatException();
               }
            } catch (NumberFormatException ex) {
               JOptionPane.showMessageDialog(this, "quantile() 请填写 0 到 1 之间的数值，例如 0.25。", "分位点无效", 1);
'''
new = '''               double q = Double.parseDouble(structured);
               boolean valid = (q > 0.0 && q < 1.0) || (q > 1.0 && q < 100.0);
               if (!valid) {
                  throw new NumberFormatException();
               }
            } catch (NumberFormatException ex) {
               JOptionPane.showMessageDialog(this, "quantile() 请填写 0–1 之间的小数，或 1–100 之间的百分数，例如 0.25 或 25。", "分位点无效", 1);
'''
java = replace_once(java, old, new, "qreg percentile validation")

# Static contracts: structured pages plus an explicit catalog classification gate for the whole method.
anchor = '''for needle in (
    'private static boolean isStructuredPrSdTestCommand(String command)',
'''
checks = '''linear_method_match = re.search(r'"线性模型及相关"[^\\n]*local view "([^"]+)"', registry)
if not linear_method_match:
    fail("linear-related Statistics method catalog not found")
linear_catalog = set(linear_method_match.group(1).split())
linear_structured = {"hetregress", "intreg", "tobit", "truncreg", "sqreg"}
linear_guided_safe = {"regress", "areg", "reghdfe", "cnsreg", "rreg", "qreg", "iqreg", "bsqreg", "vwls", "eivreg", "correlate", "pwcorr"}
linear_native_body = {"churdle", "boxcox", "fp", "nl", "nlsur", "gmm", "sureg", "reg3", "mvreg", "frontier"}
if linear_catalog != linear_structured | linear_guided_safe | linear_native_body:
    fail(f"linear-related catalog classification drift: {sorted(linear_catalog - (linear_structured | linear_guided_safe | linear_native_body))}")
for needle in (
    'private static boolean isStructuredLinearRelatedCommand(String command)',
    '"hetregress", "intreg", "tobit", "truncreg", "sqreg"',
    'private void rebuildStructuredLinearRelatedForm()',
    'private void updateStructuredLinearRelatedPreview()',
    'private boolean validateStructuredLinearRelatedBeforeRun()',
    'hetregress · 异方差线性回归',
    'intreg · 区间回归',
    'tobit · 删失回归',
    'truncreg · 截断回归',
    'sqreg · 同时分位数回归',
    'opts.add("twostep")',
    'opts.add("het(" + String.join(" ", hetVars) + ")")',
    'structuredLimitOption("ll", this.expression.getText(), tobit)',
    'opts.add("quantiles(" + qs + ")")',
    'Two-step GLS 必须选择至少 1 个 het() 方差方程变量',
    '至少需要设置一个 ll()/ul() 界限',
    'sqreg 的 quantiles() 必须是 0–1 之间的小数',
    'qreg percentile validation',
):
    if needle == 'qreg percentile validation':
        if '1–100 之间的百分数，例如 0.25 或 25' not in java:
            fail("qreg percentile notation validation was not widened to official syntax")
    elif needle not in java:
        fail(f"structured linear-related UI contract missing: {needle}")
for cmd in linear_native_body:
    if f' {cmd} ' not in semantics:
        fail(f"complex linear-related native-body command missing from semantics: {cmd}")

for needle in (
    'private static boolean isStructuredPrSdTestCommand(String command)',
'''
static = replace_once(static, anchor, checks, "linear-related static contracts")

java_path.write_text(java, encoding="utf-8")
static_path.write_text(static, encoding="utf-8")
print("HX_LINEAR_RELATED_PATCH_OK")
