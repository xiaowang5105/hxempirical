from pathlib import Path
import sys

JAVA = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
STATIC = Path('tools/verify_static_contracts.py')


def one(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f'HX_FRACTIONAL_PATCH_FAIL {label}: {n}', file=sys.stderr)
        raise SystemExit(1)
    return text.replace(old, new)


java = JAVA.read_text(encoding='utf-8')
static = STATIC.read_text(encoding='utf-8')

# Dedicated state for mean/scale constants.
java = one(java,
'''      private final JComboBox<String> genericWeightType = new JComboBox<>(new String[]{"无", "fweight", "aweight", "pweight", "iweight"});
      private final JComboBox<String> genericWeightVar = variableCombo();
''',
'''      private final JComboBox<String> genericWeightType = new JComboBox<>(new String[]{"无", "fweight", "aweight", "pweight", "iweight"});
      private final JComboBox<String> genericWeightVar = variableCombo();
      private final JCheckBox fractionalNoConstant = new JCheckBox("均值方程不含常数 noconstant", false);
      private final JCheckBox fractionalScaleNoConstant = new JCheckBox("scale() 不含常数 noconstant", false);
''', 'fractional fields')

# Ensure checkbox state participates in live preview.
java = one(java,
'''         this.regressNoConstant.addActionListener(var1x -> this.schedulePreview());
         this.regressBeta.addActionListener(var1x -> this.schedulePreview());
''',
'''         this.regressNoConstant.addActionListener(var1x -> this.schedulePreview());
         this.regressBeta.addActionListener(var1x -> this.schedulePreview());
         this.fractionalNoConstant.addActionListener(var1x -> this.schedulePreview());
         this.fractionalScaleNoConstant.addActionListener(var1x -> this.schedulePreview());
''', 'fractional listeners')

# Classifier.
java = one(java,
'''      private static boolean isStructuredCountOutcomeCommand(String command) {
         return Arrays.asList("gnbreg", "cpoisson", "zip", "zinb", "tpoisson", "tnbreg").contains(command);
      }
''',
'''      private static boolean isStructuredFractionalOutcomeCommand(String command) {
         return Arrays.asList("fracreg", "betareg").contains(command);
      }

      private static boolean isStructuredCountOutcomeCommand(String command) {
         return Arrays.asList("gnbreg", "cpoisson", "zip", "zinb", "tpoisson", "tnbreg").contains(command);
      }
''', 'fractional classifier')

# Inspector roles.
java = one(java,
'''         if (isStructuredCountOutcomeCommand(this.currentCommand)) {
            String cmd = this.currentCommand;
''',
'''         if (isStructuredFractionalOutcomeCommand(this.currentCommand)) {
            String cmd = this.currentCommand;
            if (variable.equals(selected(this.depvar))) return "分数结果 Y";
            if (this.variables.getSelectedValuesList().contains(variable)) return "均值方程 X";
            if ("fracreg".equals(cmd)) {
               if (variable.equals(selected(this.panel))) return "主方程 offset()";
               if (this.model.getSelectedIndex() == 2 && this.absorb.getSelectedValuesList().contains(variable)) return "方差方程 het()";
               if (this.model.getSelectedIndex() == 2 && variable.equals(this.newvar.getText().trim())) return "het() offset()";
            } else if (this.absorb.getSelectedValuesList().contains(variable)) {
               return "尺度方程 scale()";
            }
         }
         if (isStructuredCountOutcomeCommand(this.currentCommand)) {
            String cmd = this.currentCommand;
''', 'fractional inspector roles')

# Rebuild route before count outcomes.
java = one(java,
'''         if (isStructuredCountOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredCountOutcomeForm();
            return;
         }
''',
'''         if (isStructuredFractionalOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredFractionalOutcomeForm();
            return;
         }

         if (isStructuredCountOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredCountOutcomeForm();
            return;
         }
''', 'fractional rebuild route')

# Preview route.
java = one(java,
'''            } else if (isStructuredCountOutcomeCommand(this.currentCommand)) {
               this.updateStructuredCountOutcomePreview();
''',
'''            } else if (isStructuredFractionalOutcomeCommand(this.currentCommand)) {
               this.updateStructuredFractionalOutcomePreview();
            } else if (isStructuredCountOutcomeCommand(this.currentCommand)) {
               this.updateStructuredCountOutcomePreview();
''', 'fractional preview route')

# Validation route.
java = one(java,
'''         if (isStructuredCountOutcomeCommand(command) && !this.validateStructuredCountOutcomeBeforeRun()) return false;
''',
'''         if (isStructuredFractionalOutcomeCommand(command) && !this.validateStructuredFractionalOutcomeBeforeRun()) return false;
         if (isStructuredCountOutcomeCommand(command) && !this.validateStructuredCountOutcomeBeforeRun()) return false;
''', 'fractional validation route')

# Official fractional weights: f/i/p only.
java = one(java,
'''         if (Arrays.asList("poisson", "nbreg", "gnbreg", "cpoisson", "zip", "zinb", "tpoisson", "tnbreg").contains(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "iweight", "pweight");
''',
'''         if (Arrays.asList("fracreg", "betareg").contains(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "iweight", "pweight");
         } else if (Arrays.asList("poisson", "nbreg", "gnbreg", "cpoisson", "zip", "zinb", "tpoisson", "tnbreg").contains(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "iweight", "pweight");
''', 'fractional weights')

# Insert dedicated fractional UI before count helpers.
anchor = '''      private static String structuredCountWrappedOption(String name, String raw) {
'''
methods = r'''      private void setStructuredFractionalWeights() {
         this.genericWeightType.removeAllItems();
         this.genericWeightType.addItem("无");
         this.genericWeightType.addItem("fweight");
         this.genericWeightType.addItem("iweight");
         this.genericWeightType.addItem("pweight");
         this.genericWeightType.setSelectedItem("无");
         this.genericWeightVar.setSelectedItem(null);
         this.genericWeightVar.setEnabled(false);
      }

      private void rebuildStructuredFractionalOutcomeForm() {
         String command = this.currentCommand;
         boolean fracreg = "fracreg".equals(command);

         this.rebuilding = true;
         this.formPanel.removeAll();
         this.formPanel.setLayout(new GridBagLayout());
         this.depvar.setSelectedItem(null);
         this.variables.clearSelection();
         this.absorb.clearSelection();
         this.panel.setSelectedItem(null);
         this.newvar.setText("");
         this.ifCondition.setText("");
         this.inCondition.setText("");
         this.options.setText("");
         this.cluster.setSelectedItem(null);
         this.fractionalNoConstant.setSelected(false);
         this.fractionalScaleNoConstant.setSelected(false);
         this.fractionalNoConstant.setOpaque(false);
         this.fractionalScaleNoConstant.setOpaque(false);

         this.model.removeAllItems();
         if (fracreg) {
            this.model.addItem("Probit");
            this.model.addItem("Logit");
            this.model.addItem("异方差 Probit + het()");
         } else {
            this.model.addItem("logit（默认）");
            this.model.addItem("probit");
            this.model.addItem("cloglog");
            this.model.addItem("loglog");
         }
         this.model.setSelectedIndex(0);

         this.time.removeAllItems();
         if (fracreg) {
            this.time.addItem("不适用");
         } else {
            this.time.addItem("log（默认）");
            this.time.addItem("root");
            this.time.addItem("identity");
         }
         this.time.setSelectedIndex(0);

         this.vce.removeAllItems();
         this.vce.addItem("default");
         this.vce.addItem("robust");
         this.vce.addItem("cluster");
         this.vce.setSelectedIndex(0);
         this.setStructuredFractionalWeights();

         this.enableVariableDrop(this.depvar, fracreg ? "分数结果 Y（允许 0/1）" : "分数结果 Y（严格 0<Y<1）");
         this.enableVariableDrop(this.variables, "均值方程 X");
         this.enableVariableDrop(this.absorb, fracreg ? "异方差方程 het()" : "尺度方程 scale()");
         if (fracreg) {
            this.enableVariableDrop(this.panel, "主方程 offset()");
            this.enableVariableDrop(this.newvar, "het() offset()");
         }

         String title;
         String example;
         String insight;
         String syntax;
         String step2;
         if (fracreg) {
            title = "fracreg · 分数响应回归";
            example = "fracreg logit prate mrate age";
            insight = "fracreg 用于 0≤Y≤1 的比例、率或分数结果，允许结果恰好等于 0 或 1。官方主模型只有 fractional probit 和 fractional logit；选择异方差 Probit 时再用 het() 建模方差。fracreg 默认报告 robust 标准误。";
            syntax = "fracreg probit|logit depvar [indepvars] [if] [in] [weight] [, het(varlist [, offset(var)]) offset(var) vce(...) options]；het() 仅适用于 probit。";
            step2 = "链接与异方差";
         } else {
            title = "betareg · Beta 回归";
            example = "betareg prate x1 x2, scale(z1) link(logit) slink(log)";
            insight = "betareg 要求结果严格位于 0 与 1 之间；只要样本含 0 或 1，就应改用 fracreg 等允许端点的模型。均值方程可选 logit/probit/cloglog/loglog，尺度方程可用 scale() 协变量，并选择 log/root/identity 的 slink()。";
            syntax = "betareg depvar indepvars [if] [in] [weight] [, scale(varlist [, noconstant]) link(logit|probit|cloglog|loglog) slink(log|root|identity) vce(...) options]";
            step2 = "均值链接与尺度方程";
         }

         this.commandTitle.setText(title);
         this.commandTitle.setToolTipText(title);
         this.exampleLabel.setText("<html><b>最简单例子：</b> " + html(example) + "</html>");
         this.insightArea.setText(insight);
         this.syntaxArea.setText(syntax);
         this.setWorkspaceBreadcrumb("统计  ›  分数结果  ›  " + command);

         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.taskStepStripV153("结果与均值方程", step2, "样本与推断"), c);

         JPanel coreCard = this.xtregWizardCardV130(1, "结果与均值方程", fracreg
            ? "Y 可以落在 [0,1]，X 可留空以估计常数项模型。"
            : "Beta 分布要求 0<Y<1；Stata betareg 语法要求至少指定一项 indepvars。");
         JPanel coreBody = this.genericCardBody();
         this.addGenericBodyField(coreBody, fracreg ? "分数结果 Y（0≤Y≤1）" : "分数结果 Y（0<Y<1）", this.depvar);
         this.addGenericBodyField(coreBody, "均值方程解释变量 X", this.softList(this.variables, 7));
         coreCard.add(coreBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(coreCard, c);

         JPanel modelCard = this.xtregWizardCardV130(2, step2, fracreg
            ? "先选 Probit / Logit；只有“异方差 Probit”模式才读取 het() 变量和它自己的 offset。"
            : "均值链接和尺度链接分开选择；scale() 协变量可留空，此时尺度参数只有常数项。");
         JPanel modelBody = this.genericCardBody();
         if (fracreg) {
            this.addGenericBodyField(modelBody, "均值模型", this.model);
            this.addGenericBodyField(modelBody, "主方程 offset()（可选）", this.panel);
            this.addGenericBodyField(modelBody, "异方差方程 het()（仅异方差 Probit）", this.softList(this.absorb, 5));
            this.addGenericBodyField(modelBody, "het() 内 offset()（可选）", this.newvar);
            this.addGenericBodyField(modelBody, "常数项", this.fractionalNoConstant);
         } else {
            JPanel links = new JPanel(new GridLayout(1, 2, 10, 0));
            links.setOpaque(false);
            links.add(this.fieldBlock("均值链接 link()", this.model));
            links.add(this.fieldBlock("尺度链接 slink()", this.time));
            this.addGenericBodyField(modelBody, "链接函数", links);
            this.addGenericBodyField(modelBody, "尺度方程 scale() 协变量（可选）", this.softList(this.absorb, 5));
            JPanel constants = new JPanel(new GridLayout(1, 2, 10, 0));
            constants.setOpaque(false);
            constants.add(this.fractionalNoConstant);
            constants.add(this.fractionalScaleNoConstant);
            this.addGenericBodyField(modelBody, "常数项", constants);
         }
         modelCard.add(modelBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(modelCard, c);

         this.addStructuredCountSampleCard(c);
         c.gridy++;
         c.weighty = 1.0;
         c.fill = GridBagConstraints.BOTH;
         this.formPanel.add(Box.createVerticalGlue(), c);

         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.rebuilding = false;
         this.updateGenericWeightConditionalFields();
         this.updateStructuredFractionalOutcomePreview();
         this.statusLabel.setText(command + "：均值链接与方差 / 尺度结构已按官方语法分开。 ");
      }

      private void appendStructuredFractionalSample(StringBuilder preview) {
         String ifText = this.ifCondition.getText().trim();
         String inText = this.inCondition.getText().trim();
         if (!ifText.isBlank()) preview.append(" if ").append(ifText);
         if (!inText.isBlank()) preview.append(" in ").append(inText);
         String type = selected(this.genericWeightType);
         String weight = selected(this.genericWeightVar);
         if (!"无".equals(type) && !weight.isBlank()) preview.append(" [").append(type).append("=").append(weight).append("]");
      }

      private void appendStructuredFractionalVce(List<String> opts) {
         String selectedVce = selected(this.vce);
         if ("robust".equals(selectedVce)) opts.add("vce(robust)");
         else if ("cluster".equals(selectedVce) && !selected(this.cluster).isBlank()) opts.add("vce(cluster " + selected(this.cluster) + ")");
      }

      private void updateStructuredFractionalOutcomePreview() {
         String command = this.currentCommand;
         boolean fracreg = "fracreg".equals(command);
         StringBuilder preview = new StringBuilder(command);
         String y = selected(this.depvar);
         List<String> x = this.variables.getSelectedValuesList();
         ArrayList<String> opts = new ArrayList<>();

         if (fracreg) {
            String family = this.model.getSelectedIndex() == 1 ? "logit" : "probit";
            preview.append(" ").append(family);
         }
         if (!y.isBlank()) preview.append(" ").append(y);
         if (!x.isEmpty()) preview.append(" ").append(String.join(" ", x));
         this.appendStructuredFractionalSample(preview);

         if (this.fractionalNoConstant.isSelected()) opts.add("noconstant");
         if (fracreg) {
            String mainOffset = selected(this.panel);
            if (!mainOffset.isBlank()) opts.add("offset(" + mainOffset + ")");
            if (this.model.getSelectedIndex() == 2) {
               List<String> hetVars = this.absorb.getSelectedValuesList();
               if (!hetVars.isEmpty()) {
                  StringBuilder het = new StringBuilder("het(").append(String.join(" ", hetVars));
                  String hetOffset = this.newvar.getText().trim();
                  if (!hetOffset.isBlank()) het.append(", offset(").append(hetOffset).append(")");
                  het.append(")");
                  opts.add(het.toString());
               }
            }
         } else {
            List<String> scaleVars = this.absorb.getSelectedValuesList();
            if (!scaleVars.isEmpty()) {
               StringBuilder scale = new StringBuilder("scale(").append(String.join(" ", scaleVars));
               if (this.fractionalScaleNoConstant.isSelected()) scale.append(", noconstant");
               scale.append(")");
               opts.add(scale.toString());
            }
            String[] links = {"logit", "probit", "cloglog", "loglog"};
            int linkIndex = Math.max(0, Math.min(this.model.getSelectedIndex(), links.length - 1));
            if (linkIndex != 0) opts.add("link(" + links[linkIndex] + ")");
            String[] slinks = {"log", "root", "identity"};
            int slinkIndex = Math.max(0, Math.min(this.time.getSelectedIndex(), slinks.length - 1));
            if (slinkIndex != 0) opts.add("slink(" + slinks[slinkIndex] + ")");
         }

         this.appendStructuredFractionalVce(opts);
         String extra = this.options.getText().trim();
         if (!extra.isBlank()) opts.add(extra);
         if (!opts.isEmpty()) preview.append(", ").append(String.join(" ", opts));

         this.previewArea.setText(preview.toString());
         this.previewArea.setCaretPosition(0);
         this.flashCommandPreview();
      }

      private boolean validateStructuredFractionalOutcomeBeforeRun() {
         String command = this.currentCommand;
         boolean fracreg = "fracreg".equals(command);
         if (selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, command + " 需要选择分数结果变量 Y。", "结果变量缺失", 1);
            return false;
         }
         if (!fracreg && this.variables.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "betareg 官方语法要求指定 indepvars；请至少选择 1 个均值方程解释变量。", "解释变量缺失", 1);
            return false;
         }
         if (fracreg && this.model.getSelectedIndex() == 2 && this.absorb.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "异方差 fractional probit 需要至少选择 1 个 het() 方差方程变量。", "het() 缺失", 1);
            return false;
         }
         if (!fracreg && this.fractionalScaleNoConstant.isSelected() && this.absorb.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "scale() 没有协变量时不能单独设置 scale(..., noconstant)；请先选择尺度方程变量。", "scale() 设置无效", 1);
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
         if (fracreg && this.model.getSelectedIndex() != 1) {
            String extra = this.options.getText().trim().toLowerCase(Locale.ROOT);
            if (Pattern.compile("(^|[\\s,])or($|[\\s,])").matcher(extra).find()) {
               JOptionPane.showMessageDialog(this, "fracreg 的 or 仅适用于 fractional logit；请切换到 Logit 或删除 or。", "or 与模型不兼容", 1);
               return false;
            }
         }
         return true;
      }

'''
java = one(java, anchor, methods + anchor, 'fractional methods')

# Static classification and contract gate.
count_gate = '''if count_catalog != count_structured | count_guided_safe:
    fail(f"count-outcome catalog classification drift: {sorted(count_catalog - (count_structured | count_guided_safe))}")
'''
fractional_gate = '''if count_catalog != count_structured | count_guided_safe:
    fail(f"count-outcome catalog classification drift: {sorted(count_catalog - (count_structured | count_guided_safe))}")

# Fractional-outcome Statistics method must remain fully classified.
fractional_method_match = re.search(r'"分数结果"[^\\n]*local view "([^"]+)"', registry)
if not fractional_method_match:
    fail("fractional-outcome Statistics method catalog not found")
fractional_catalog = set(fractional_method_match.group(1).split())
fractional_structured = {"fracreg", "betareg"}
if fractional_catalog != fractional_structured:
    fail(f"fractional-outcome catalog classification drift: {sorted(fractional_catalog - fractional_structured)}")
for needle in (
    'private static boolean isStructuredFractionalOutcomeCommand(String command)',
    '"fracreg", "betareg"',
    'private void rebuildStructuredFractionalOutcomeForm()',
    'private void updateStructuredFractionalOutcomePreview()',
    'private boolean validateStructuredFractionalOutcomeBeforeRun()',
    'fracreg · 分数响应回归',
    'betareg · Beta 回归',
    '异方差 Probit + het()',
    '均值链接 link()',
    '尺度链接 slink()',
    '尺度方程 scale() 协变量（可选）',
    'scale.append(", noconstant")',
    'String[] links = {"logit", "probit", "cloglog", "loglog"}',
    'String[] slinks = {"log", "root", "identity"}',
    'fracreg 的 or 仅适用于 fractional logit',
    'Beta 分布要求 0<Y<1',
    'var2 = Arrays.asList("无", "fweight", "iweight", "pweight")',
):
    if needle not in java:
        fail(f"structured fractional-outcome UI contract missing: {needle}")
if 'this.model.addItem("cloglog")' in java and 'boolean fracreg = "fracreg".equals(command);' not in java:
    fail("fracreg must not expose betareg-only cloglog/loglog links")
'''
static = one(static, count_gate, fractional_gate, 'fractional static gate')

JAVA.write_text(java, encoding='utf-8')
STATIC.write_text(static, encoding='utf-8')
print('HX_FRACTIONAL_PATCH_OK')
