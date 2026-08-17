from pathlib import Path
import sys

JAVA = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
STATIC = Path('tools/verify_static_contracts.py')


def one(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f'HX_COUNT_PATCH_FAIL {label}: {n}', file=sys.stderr)
        raise SystemExit(1)
    return text.replace(old, new)


java = JAVA.read_text(encoding='utf-8')
static = STATIC.read_text(encoding='utf-8')

# Classifier.
java = one(java,
'''      private static boolean isStructuredCategoricalOutcomeCommand(String command) {
         return Arrays.asList("clogit", "slogit", "cmset", "cmsummarize", "cmchoiceset", "cmtab", "cmsample", "cmclogit").contains(command);
      }
''',
'''      private static boolean isStructuredCountOutcomeCommand(String command) {
         return Arrays.asList("gnbreg", "cpoisson", "zip", "zinb", "tpoisson", "tnbreg").contains(command);
      }

      private static boolean isStructuredCategoricalOutcomeCommand(String command) {
         return Arrays.asList("clogit", "slogit", "cmset", "cmsummarize", "cmchoiceset", "cmtab", "cmsample", "cmclogit").contains(command);
      }
''', 'classifier')

# Inspector roles.
java = one(java,
'''         if (isStructuredCategoricalOutcomeCommand(this.currentCommand)) {
            String cmd = this.currentCommand;
            if ("clogit".equals(cmd)) {
''',
'''         if (isStructuredCountOutcomeCommand(this.currentCommand)) {
            String cmd = this.currentCommand;
            if (variable.equals(selected(this.depvar))) return "计数结果 Y";
            if (this.variables.getSelectedValuesList().contains(variable)) return "均值方程 X";
            if ("gnbreg".equals(cmd) && this.absorb.getSelectedValuesList().contains(variable)) return "离散参数方程 lnalpha()";
            if (Arrays.asList("zip", "zinb").contains(cmd) && this.absorb.getSelectedValuesList().contains(variable)) return "零膨胀方程 inflate()";
            if (variable.equals(selected(this.panel))) {
               if (this.time.getSelectedIndex() == 1) return "主方程 offset()";
               if (this.time.getSelectedIndex() == 2) return "主方程 exposure()";
            }
            if (Arrays.asList("cpoisson", "tpoisson", "tnbreg").contains(cmd) && variable.equals(this.expression.getText().trim())) return "下界 ll()";
            if (Arrays.asList("cpoisson", "tpoisson").contains(cmd) && variable.equals(this.newvar.getText().trim())) return "上界 ul()";
            if (Arrays.asList("zip", "zinb").contains(cmd) && variable.equals(this.newvar.getText().trim())) return "inflate() offset()";
         }
         if (isStructuredCategoricalOutcomeCommand(this.currentCommand)) {
            String cmd = this.currentCommand;
            if ("clogit".equals(cmd)) {
''', 'inspector roles')

# Rebuild route.
java = one(java,
'''         if (isStructuredCategoricalOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredCategoricalOutcomeForm();
            return;
         }
''',
'''         if (isStructuredCountOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredCountOutcomeForm();
            return;
         }

         if (isStructuredCategoricalOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredCategoricalOutcomeForm();
            return;
         }
''', 'rebuild route')

# Preview route.
java = one(java,
'''            } else if (isStructuredCategoricalOutcomeCommand(this.currentCommand)) {
               this.updateStructuredCategoricalOutcomePreview();
''',
'''            } else if (isStructuredCountOutcomeCommand(this.currentCommand)) {
               this.updateStructuredCountOutcomePreview();
            } else if (isStructuredCategoricalOutcomeCommand(this.currentCommand)) {
               this.updateStructuredCategoricalOutcomePreview();
''', 'preview route')

# Validation route.
java = one(java,
'''         if (isStructuredCategoricalOutcomeCommand(command) && !this.validateStructuredCategoricalOutcomeBeforeRun()) return false;
''',
'''         if (isStructuredCountOutcomeCommand(command) && !this.validateStructuredCountOutcomeBeforeRun()) return false;
         if (isStructuredCategoricalOutcomeCommand(command) && !this.validateStructuredCategoricalOutcomeBeforeRun()) return false;
''', 'validation route')

# Count-weight restrictions go before the existing discrete-outcome branch so earlier contracts remain stable.
weight_anchor = '''         if (Arrays.asList("logit", "logistic", "binreg", "probit", "biprobit", "hetprobit", "scobit", "cloglog", "ologit", "oprobit", "hetoprobit", "zioprobit", "ziologit", "mlogit", "mprobit", "clogit", "slogit", "cmclogit", "cmsample").contains(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "iweight", "pweight");
'''
java = one(java, weight_anchor,
'''         if (Arrays.asList("poisson", "nbreg", "gnbreg", "cpoisson", "zip", "zinb", "tpoisson", "tnbreg").contains(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "iweight", "pweight");
         } else if ("ppmlhdfe".equals(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "pweight");
         } else if (Arrays.asList("logit", "logistic", "binreg", "probit", "biprobit", "hetprobit", "scobit", "cloglog", "ologit", "oprobit", "hetoprobit", "zioprobit", "ziologit", "mlogit", "mprobit", "clogit", "slogit", "cmclogit", "cmsample").contains(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "iweight", "pweight");
''', 'count weights')

# Structured count UI implementation. Insert immediately before categorical helpers.
anchor = '''      private static String structuredCategoricalOption(String name, String raw) {
'''
count_methods = r'''      private static String structuredCountWrappedOption(String name, String raw) {
         String value = raw == null ? "" : raw.trim();
         if (value.isBlank()) return "";
         if (value.startsWith(name + "(")) return value;
         return name + "(" + value + ")";
      }

      private static String structuredCountCensorOption(String name, String raw, boolean allowBare) {
         String value = raw == null ? "" : raw.trim();
         if (value.isBlank()) return "";
         if (value.startsWith(name + "(")) return value;
         if (allowBare && (("ll".equals(name) && "min".equalsIgnoreCase(value)) || ("ul".equals(name) && "max".equalsIgnoreCase(value)))) return name;
         return name + "(" + value + ")";
      }

      private static Double structuredCountNumeric(String raw) {
         String value = raw == null ? "" : raw.trim();
         if (value.isBlank()) return null;
         int open = value.indexOf('(');
         int close = value.endsWith(")") ? value.length() - 1 : -1;
         if (open >= 0 && close > open) value = value.substring(open + 1, close).trim();
         try {
            return Double.valueOf(value);
         } catch (NumberFormatException ex) {
            return null;
         }
      }

      private void setStructuredCountWeights() {
         this.genericWeightType.removeAllItems();
         this.genericWeightType.addItem("无");
         this.genericWeightType.addItem("fweight");
         this.genericWeightType.addItem("iweight");
         this.genericWeightType.addItem("pweight");
         this.genericWeightType.setSelectedItem("无");
         this.genericWeightVar.setSelectedItem(null);
         this.genericWeightVar.setEnabled(false);
      }

      private void addStructuredCountSampleCard(GridBagConstraints c) {
         JPanel sampleCard = this.xtregWizardCardV130(3, "样本与推断", "最后设置样本、权重和常用标准误；低频估计选项继续保留为 Stata 原生 options。");
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

         JPanel vceRow = new JPanel(new GridLayout(1, 2, 10, 0));
         vceRow.setOpaque(false);
         vceRow.add(this.fieldBlock("标准误", this.vce));
         vceRow.add(this.fieldBlock("聚类变量（仅 cluster）", this.cluster));
         this.addGenericBodyField(sampleBody, "推断", vceRow);
         this.addGenericBodyField(sampleBody, "其他 Stata options（可选）", this.options);
         sampleCard.add(sampleBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(sampleCard, c);
      }

      private void rebuildStructuredCountOutcomeForm() {
         String command = this.currentCommand;
         boolean generalized = "gnbreg".equals(command);
         boolean censored = "cpoisson".equals(command);
         boolean zeroInflated = Arrays.asList("zip", "zinb").contains(command);
         boolean truncatedPoisson = "tpoisson".equals(command);
         boolean truncatedNb = "tnbreg".equals(command);

         this.rebuilding = true;
         this.formPanel.removeAll();
         this.formPanel.setLayout(new GridBagLayout());
         this.depvar.setSelectedItem(null);
         this.variables.clearSelection();
         this.absorb.clearSelection();
         this.panel.setSelectedItem(null);
         this.expression.setText("");
         this.newvar.setText("");
         this.ifCondition.setText("");
         this.inCondition.setText("");
         this.options.setText("");
         this.cluster.setSelectedItem(null);

         this.time.removeAllItems();
         this.time.addItem("无率调整");
         this.time.addItem("offset()");
         this.time.addItem("exposure()");
         this.time.setSelectedIndex(0);

         this.model.removeAllItems();
         if (zeroInflated) {
            this.model.addItem("Logit：inflate() 协变量");
            this.model.addItem("Probit：inflate() 协变量");
            this.model.addItem("Logit：inflate(_cons)");
            this.model.addItem("Probit：inflate(_cons)");
         } else if (truncatedNb) {
            this.model.addItem("dispersion(mean)（默认）");
            this.model.addItem("dispersion(constant)");
         } else {
            this.model.addItem("默认设定");
         }
         this.model.setSelectedIndex(0);

         this.vce.removeAllItems();
         this.vce.addItem("default");
         this.vce.addItem("robust");
         this.vce.addItem("cluster");
         this.vce.setSelectedIndex(0);
         this.setStructuredCountWeights();

         this.enableVariableDrop(this.depvar, "计数结果 Y");
         this.enableVariableDrop(this.variables, "均值方程 X");
         this.enableVariableDrop(this.panel, "offset()/exposure() 变量");
         if (generalized) this.enableVariableDrop(this.absorb, "lnalpha() 方程变量");
         if (zeroInflated) {
            this.enableVariableDrop(this.absorb, "inflate() 方程变量");
            this.enableVariableDrop(this.newvar, "inflate() offset() 变量");
         }
         if (censored || truncatedPoisson || truncatedNb) this.enableVariableDrop(this.expression, "下界 ll()");
         if (censored || truncatedPoisson) this.enableVariableDrop(this.newvar, "上界 ul()");

         String title;
         String example;
         String insight;
         String syntax;
         String secondStep;
         if (generalized) {
            title = "gnbreg · 广义负二项回归";
            example = "gnbreg y x1 x2, lnalpha(z1 z2)";
            insight = "gnbreg 在负二项均值方程之外允许 ln(alpha) 随协变量变化。lnalpha() 可以留空；留空时形状参数为常数，结果退化为普通 nbreg 的对应设定。";
            syntax = "gnbreg depvar [indepvars] [if] [in] [weight] [, lnalpha(varlist) exposure(var) offset(var) vce(...) options]";
            secondStep = "离散参数方程";
         } else if (censored) {
            title = "cpoisson · 删失 Poisson 回归";
            example = "cpoisson y x1 x2, ul(4) ll(lower)";
            insight = "cpoisson 用于计数结果被左删失、右删失或双侧删失的情况。ll()/ul() 都可以留空；不指定时模型与普通 Poisson 对应。输入 min/max 可生成 Stata 的裸 ll/ul，分别使用因变量样本最小值/最大值。";
            syntax = "cpoisson depvar [indepvars] [if] [in] [weight] [, ll[(var|#)] ul[(var|#)] exposure(var) offset(var) vce(...) options]";
            secondStep = "删失界限";
         } else if (zeroInflated) {
            title = ("zip".equals(command) ? "zip · 零膨胀 Poisson 回归" : "zinb · 零膨胀负二项回归");
            example = command + " y x1 x2, inflate(z1 z2)";
            insight = "零膨胀模型同时估计计数过程和“额外零值”过程。inflate() 是官方必填方程；可用协变量，也可选择 inflate(_cons) 只估计截距。零膨胀方程默认 Logit，也可切换 Probit。";
            syntax = command + " depvar [indepvars] [if] [in] [weight], inflate(varlist [, offset(var)] | _cons) [probit exposure(var) offset(var) vce(...) options]";
            secondStep = "零膨胀方程";
         } else if (truncatedPoisson) {
            title = "tpoisson · 截断 Poisson 回归";
            example = "tpoisson y x1 x2, ll(0)";
            insight = "tpoisson 用于样本因截断机制而完全看不到某些计数值的情况。ll()/ul() 可使用非负整数或变量；两者都留空时 Stata 默认零截断 ll(0)。";
            syntax = "tpoisson depvar [indepvars] [if] [in] [weight] [, ll(#|var) ul(#|var) exposure(var) offset(var) vce(...) options]";
            secondStep = "截断界限";
         } else {
            title = "tnbreg · 截断负二项回归";
            example = "tnbreg y x1 x2, ll(0)";
            insight = "tnbreg 用于存在过度离散且样本经过下端截断的计数结果。ll() 可留空，Stata 默认 ll(0)；还可在 mean 与 constant 两种 dispersion 参数化之间切换。";
            syntax = "tnbreg depvar [indepvars] [if] [in] [weight] [, ll(#|var) dispersion(mean|constant) exposure(var) offset(var) vce(...) options]";
            secondStep = "截断与离散";
         }

         this.commandTitle.setText(title);
         this.commandTitle.setToolTipText("Stata Statistics > Count outcomes > " + command);
         this.setWorkspaceBreadcrumb("统计  ›  计数结果  ›  " + command);
         this.exampleLabel.setText("<html><b>最简单例子：</b> " + html(example) + "</html>");
         this.insightArea.setText(insight);
         this.syntaxArea.setText(syntax);
         this.runButton.setText("运行模型");
         this.commandDock.setVisible(true);

         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.taskStepStripV153("计数均值方程", secondStep, "样本与推断"), c);

         JPanel mainCard = this.xtregWizardCardV130(1, "计数均值方程", "先选择非负计数结果 Y 与主方程解释变量；需要按暴露量或已知率调整时，再选择 offset()/exposure()。 ");
         JPanel mainBody = this.genericCardBody();
         this.addGenericBodyField(mainBody, "计数结果 Y", this.depvar);
         this.addGenericBodyField(mainBody, "均值方程解释变量 X（可选）", this.listPane(this.variables));
         JPanel rateRow = new JPanel(new GridLayout(1, 2, 10, 0));
         rateRow.setOpaque(false);
         rateRow.add(this.fieldBlock("率调整方式", this.time));
         rateRow.add(this.fieldBlock("offset / exposure 变量", this.panel));
         this.addGenericBodyField(mainBody, "率 / 暴露量调整（可选）", rateRow);
         mainCard.add(mainBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(mainCard, c);

         JPanel secondCard = this.xtregWizardCardV130(2, secondStep, zeroInflated
            ? "inflate() 是模型的一部分，不是普通控制变量；主方程与额外零值过程要分开解释。"
            : (censored || truncatedPoisson || truncatedNb ? "删失/截断界限可以使用常数或变量；不要把观测筛选 if 与界限混为一谈。" : "lnalpha() 描述离散参数，不属于计数均值方程。"));
         JPanel secondBody = this.genericCardBody();
         if (generalized) {
            this.addGenericBodyField(secondBody, "lnalpha() 方程变量（可选）", this.listPane(this.absorb));
         } else if (censored) {
            this.addGenericBodyField(secondBody, "左删失 ll()（可选；min = 使用样本最小值）", this.expression);
            this.addGenericBodyField(secondBody, "右删失 ul()（可选；max = 使用样本最大值）", this.newvar);
         } else if (zeroInflated) {
            this.addGenericBodyField(secondBody, "额外零值过程", this.model);
            this.addGenericBodyField(secondBody, "inflate() 协变量（协变量模式必填）", this.listPane(this.absorb));
            this.addGenericBodyField(secondBody, "inflate() offset 变量（可选；仅协变量模式生效）", this.newvar);
         } else if (truncatedPoisson) {
            this.addGenericBodyField(secondBody, "下截断 ll()（可选；默认 0）", this.expression);
            this.addGenericBodyField(secondBody, "上截断 ul()（可选）", this.newvar);
         } else {
            this.addGenericBodyField(secondBody, "下截断 ll()（可选；默认 0）", this.expression);
            this.addGenericBodyField(secondBody, "离散参数化", this.model);
         }
         secondCard.add(secondBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(secondCard, c);
         this.addStructuredCountSampleCard(c);

         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.rebuilding = false;
         this.updateGenericWeightConditionalFields();
         this.updateStructuredCountOutcomePreview();
         this.statusLabel.setText(command + "：计数均值过程与离散 / 删失 / 零膨胀 / 截断结构已分开。 ");
      }

      private void appendStructuredCountSample(StringBuilder preview) {
         String ifText = this.ifCondition.getText().trim();
         String inText = this.inCondition.getText().trim();
         if (!ifText.isBlank()) preview.append(" if ").append(ifText);
         if (!inText.isBlank()) preview.append(" in ").append(inText);
         String type = selected(this.genericWeightType);
         String variable = selected(this.genericWeightVar);
         if (!"无".equals(type) && !variable.isBlank()) preview.append(" [").append(type).append("=").append(variable).append("]");
      }

      private void appendStructuredCountRateOption(List<String> opts) {
         int mode = this.time.getSelectedIndex();
         String variable = selected(this.panel);
         if (mode == 1 && !variable.isBlank()) opts.add("offset(" + variable + ")");
         if (mode == 2 && !variable.isBlank()) opts.add("exposure(" + variable + ")");
      }

      private void appendStructuredCountVce(List<String> opts) {
         String value = selected(this.vce);
         if ("robust".equals(value)) opts.add("vce(robust)");
         else if ("cluster".equals(value)) {
            String cl = selected(this.cluster);
            if (!cl.isBlank()) opts.add("vce(cluster " + cl + ")");
         }
      }

      private void updateStructuredCountOutcomePreview() {
         String command = this.currentCommand;
         StringBuilder preview = new StringBuilder(command);
         String y = selected(this.depvar);
         List<String> x = this.variables.getSelectedValuesList();
         if (!y.isBlank()) preview.append(" ").append(y);
         if (!x.isEmpty()) preview.append(" ").append(String.join(" ", x));
         this.appendStructuredCountSample(preview);

         ArrayList<String> opts = new ArrayList<>();
         if ("gnbreg".equals(command)) {
            List<String> alphaVars = this.absorb.getSelectedValuesList();
            if (!alphaVars.isEmpty()) opts.add("lnalpha(" + String.join(" ", alphaVars) + ")");
         } else if ("cpoisson".equals(command)) {
            String lower = structuredCountCensorOption("ll", this.expression.getText(), true);
            String upper = structuredCountCensorOption("ul", this.newvar.getText(), true);
            if (!lower.isBlank()) opts.add(lower);
            if (!upper.isBlank()) opts.add(upper);
         } else if (Arrays.asList("zip", "zinb").contains(command)) {
            int mode = this.model.getSelectedIndex();
            boolean constantOnly = mode >= 2;
            boolean probit = mode == 1 || mode == 3;
            if (constantOnly) {
               opts.add("inflate(_cons)");
            } else {
               List<String> inflateVars = this.absorb.getSelectedValuesList();
               if (!inflateVars.isEmpty()) {
                  StringBuilder inflate = new StringBuilder("inflate(").append(String.join(" ", inflateVars));
                  String inflateOffset = this.newvar.getText().trim();
                  if (!inflateOffset.isBlank()) inflate.append(", offset(").append(inflateOffset).append(")");
                  inflate.append(")");
                  opts.add(inflate.toString());
               }
            }
            if (probit) opts.add("probit");
         } else if ("tpoisson".equals(command)) {
            String lower = structuredCountWrappedOption("ll", this.expression.getText());
            String upper = structuredCountWrappedOption("ul", this.newvar.getText());
            if (!lower.isBlank()) opts.add(lower);
            if (!upper.isBlank()) opts.add(upper);
         } else if ("tnbreg".equals(command)) {
            String lower = structuredCountWrappedOption("ll", this.expression.getText());
            if (!lower.isBlank()) opts.add(lower);
            if (this.model.getSelectedIndex() == 1) opts.add("dispersion(constant)");
         }
         this.appendStructuredCountRateOption(opts);
         this.appendStructuredCountVce(opts);
         String extra = this.options.getText().trim();
         if (!extra.isBlank()) opts.add(extra);
         if (!opts.isEmpty()) preview.append(", ").append(String.join(" ", opts));

         this.previewArea.setText(preview.toString());
         this.previewArea.setCaretPosition(0);
         this.flashCommandPreview();
      }

      private boolean validateStructuredCountOutcomeBeforeRun() {
         String command = this.currentCommand;
         if (selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, command + " 需要选择计数结果变量 Y。", "结果变量缺失", 1);
            return false;
         }
         if (this.time.getSelectedIndex() > 0 && selected(this.panel).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择 offset()/exposure() 后必须指定对应变量。", "率调整变量缺失", 1);
            return false;
         }
         String weightType = selected(this.genericWeightType);
         if (!"无".equals(weightType) && selected(this.genericWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后必须指定权重变量。", "权重变量缺失", 1);
            return false;
         }
         if ("cluster".equals(selected(this.vce)) && selected(this.cluster).isBlank()) {
            JOptionPane.showMessageDialog(this, "vce(cluster) 需要选择聚类变量。", "聚类变量缺失", 1);
            return false;
         }
         if (Arrays.asList("zip", "zinb").contains(command) && this.model.getSelectedIndex() < 2 && this.absorb.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, command + " 的 inflate() 是官方必填项；当前协变量模式需要至少选择 1 个 inflate() 变量，或改用 inflate(_cons)。", "inflate() 缺失", 1);
            return false;
         }
         if (Arrays.asList("tpoisson", "tnbreg").contains(command)) {
            Double lower = structuredCountNumeric(this.expression.getText());
            if (lower != null && (lower < 0 || Math.rint(lower) != lower)) {
               JOptionPane.showMessageDialog(this, command + " 的 ll() 若填写常数，必须是非负整数；也可以填写变量名。", "截断下界无效", 1);
               return false;
            }
         }
         if ("tpoisson".equals(command)) {
            Double upper = structuredCountNumeric(this.newvar.getText());
            if (upper != null && (upper < 0 || Math.rint(upper) != upper)) {
               JOptionPane.showMessageDialog(this, "tpoisson 的 ul() 若填写常数，必须是非负整数；也可以填写变量名。", "截断上界无效", 1);
               return false;
            }
         }
         if (Arrays.asList("cpoisson", "tpoisson").contains(command)) {
            Double lower = structuredCountNumeric(this.expression.getText());
            Double upper = structuredCountNumeric(this.newvar.getText());
            if (lower != null && upper != null && lower > upper) {
               JOptionPane.showMessageDialog(this, "ll() 不能大于 ul()。", "界限顺序无效", 1);
               return false;
            }
         }
         return true;
      }

'''
java = one(java, anchor, count_methods + anchor, 'count methods')

# Static coverage and UI contracts.
cat_gate = '''if categorical_catalog != categorical_structured | categorical_guided_safe | categorical_native_body:
    fail(f"categorical-outcome catalog classification drift: {sorted(categorical_catalog - (categorical_structured | categorical_guided_safe | categorical_native_body))}")
'''
count_gate = '''if categorical_catalog != categorical_structured | categorical_guided_safe | categorical_native_body:
    fail(f"categorical-outcome catalog classification drift: {sorted(categorical_catalog - (categorical_structured | categorical_guided_safe | categorical_native_body))}")

# Count-outcome Statistics method must remain fully classified.
count_method_match = re.search(r'"计数结果"[^\\n]*local view "([^"]+)"', registry)
if not count_method_match:
    fail("count-outcome Statistics method catalog not found")
count_catalog = set(count_method_match.group(1).split())
count_structured = {"gnbreg", "cpoisson", "zip", "zinb", "tpoisson", "tnbreg"}
count_guided_safe = {"poisson", "nbreg", "ppmlhdfe"}
if count_catalog != count_structured | count_guided_safe:
    fail(f"count-outcome catalog classification drift: {sorted(count_catalog - (count_structured | count_guided_safe))}")
for needle in (
    'private static boolean isStructuredCountOutcomeCommand(String command)',
    '"gnbreg", "cpoisson", "zip", "zinb", "tpoisson", "tnbreg"',
    'private void rebuildStructuredCountOutcomeForm()',
    'private void updateStructuredCountOutcomePreview()',
    'private boolean validateStructuredCountOutcomeBeforeRun()',
    'gnbreg · 广义负二项回归',
    'cpoisson · 删失 Poisson 回归',
    'zip · 零膨胀 Poisson 回归',
    'zinb · 零膨胀负二项回归',
    'tpoisson · 截断 Poisson 回归',
    'tnbreg · 截断负二项回归',
    'opts.add("lnalpha(" + String.join(" ", alphaVars) + ")")',
    'opts.add("inflate(_cons)")',
    'inflate() 是官方必填项',
    'dispersion(constant)',
    '非负整数；也可以填写变量名',
    'Arrays.asList("poisson", "nbreg", "gnbreg", "cpoisson", "zip", "zinb", "tpoisson", "tnbreg")',
    'var2 = Arrays.asList("无", "fweight", "pweight")',
):
    if needle not in java:
        fail(f"structured count-outcome UI contract missing: {needle}")
for cmd in count_structured:
    if f' {cmd} ' not in semantics:
        fail(f"count structured command lost native-body safety fallback: {cmd}")
'''
static = one(static, cat_gate, count_gate, 'count static gate')

JAVA.write_text(java, encoding='utf-8')
STATIC.write_text(static, encoding='utf-8')
print('HX_COUNT_PATCH_OK')
