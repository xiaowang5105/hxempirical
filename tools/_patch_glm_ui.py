from pathlib import Path
import sys

JAVA = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
STATIC = Path('tools/verify_static_contracts.py')


def one(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f'HX_GLM_PATCH_FAIL {label}: {n}', file=sys.stderr)
        raise SystemExit(1)
    return text.replace(old, new)


java = JAVA.read_text(encoding='utf-8')
static = STATIC.read_text(encoding='utf-8')

# Dedicated GLM controls.
java = one(java,
'''      private final JCheckBox fractionalNoConstant = new JCheckBox("均值方程不含常数 noconstant", false);
      private final JCheckBox fractionalScaleNoConstant = new JCheckBox("scale() 不含常数 noconstant", false);
''',
'''      private final JCheckBox fractionalNoConstant = new JCheckBox("均值方程不含常数 noconstant", false);
      private final JCheckBox fractionalScaleNoConstant = new JCheckBox("scale() 不含常数 noconstant", false);
      private final JComboBox<String> glmRateMode = new JComboBox<>(new String[]{"无", "offset()", "exposure()"});
      private final JComboBox<String> glmEstimationMode = new JComboBox<>(new String[]{"ML（默认）", "IRLS"});
      private final JCheckBox glmNoConstant = new JCheckBox("不估计常数项 noconstant", false);
      private final JCheckBox glmEform = new JCheckBox("报告指数化系数 eform", false);
''', 'glm fields')

# Style dedicated combos consistently.
java = one(java,
'''         for (JComboBox var10 : Arrays.asList(this.depvar, this.model, this.panel, this.time, this.vce, this.cluster, this.genericWeightType, this.genericWeightVar)) {
            styleCombo(var10);
         }
''',
'''         for (JComboBox var10 : Arrays.asList(this.depvar, this.model, this.panel, this.time, this.vce, this.cluster, this.genericWeightType, this.genericWeightVar, this.glmRateMode, this.glmEstimationMode)) {
            styleCombo(var10);
         }
''', 'glm combo styling')

# Live preview / family-link dependency.
java = one(java,
'''         this.fractionalNoConstant.addActionListener(var1x -> this.schedulePreview());
         this.fractionalScaleNoConstant.addActionListener(var1x -> this.schedulePreview());
''',
'''         this.fractionalNoConstant.addActionListener(var1x -> this.schedulePreview());
         this.fractionalScaleNoConstant.addActionListener(var1x -> this.schedulePreview());
         this.glmNoConstant.addActionListener(var1x -> this.schedulePreview());
         this.glmEform.addActionListener(var1x -> this.schedulePreview());
         this.glmRateMode.addActionListener(var1x -> this.schedulePreview());
         this.glmEstimationMode.addActionListener(var1x -> this.schedulePreview());
         this.model.addActionListener(var1x -> {
            if (!this.rebuilding && "glm".equals(this.currentCommand)) {
               boolean oldRebuilding = this.rebuilding;
               this.rebuilding = true;
               this.updateStructuredGlmLinkChoices();
               this.rebuilding = oldRebuilding;
               this.schedulePreview();
            }
         });
''', 'glm listeners')

# Classifier.
java = one(java,
'''      private static boolean isStructuredFractionalOutcomeCommand(String command) {
         return Arrays.asList("fracreg", "betareg").contains(command);
      }
''',
'''      private static boolean isStructuredGlmCommand(String command) {
         return "glm".equals(command);
      }

      private static boolean isStructuredFractionalOutcomeCommand(String command) {
         return Arrays.asList("fracreg", "betareg").contains(command);
      }
''', 'glm classifier')

# Variable inspector roles.
java = one(java,
'''         if (isStructuredFractionalOutcomeCommand(this.currentCommand)) {
            String cmd = this.currentCommand;
''',
'''         if (isStructuredGlmCommand(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "GLM 结果变量 Y";
            if (this.variables.getSelectedValuesList().contains(variable)) return "GLM 解释变量 X";
            if (this.glmRateMode.getSelectedIndex() == 1 && variable.equals(selected(this.panel))) return "offset()";
            if (this.glmRateMode.getSelectedIndex() == 2 && variable.equals(selected(this.panel))) return "exposure()";
            if (variable.equals(selected(this.genericWeightVar))) return "权重变量";
            if ("cluster".equals(selected(this.vce)) && variable.equals(selected(this.cluster))) return "聚类变量";
         }
         if (isStructuredFractionalOutcomeCommand(this.currentCommand)) {
            String cmd = this.currentCommand;
''', 'glm inspector roles')

# Rebuild route.
java = one(java,
'''         if (isStructuredFractionalOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredFractionalOutcomeForm();
            return;
         }
''',
'''         if (isStructuredGlmCommand(this.currentCommand)) {
            this.rebuildStructuredGlmForm();
            return;
         }

         if (isStructuredFractionalOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredFractionalOutcomeForm();
            return;
         }
''', 'glm rebuild route')

# Preview route.
java = one(java,
'''            } else if (isStructuredFractionalOutcomeCommand(this.currentCommand)) {
               this.updateStructuredFractionalOutcomePreview();
''',
'''            } else if (isStructuredGlmCommand(this.currentCommand)) {
               this.updateStructuredGlmPreview();
            } else if (isStructuredFractionalOutcomeCommand(this.currentCommand)) {
               this.updateStructuredFractionalOutcomePreview();
''', 'glm preview route')

# Validation route.
java = one(java,
'''         if (isStructuredFractionalOutcomeCommand(command) && !this.validateStructuredFractionalOutcomeBeforeRun()) return false;
''',
'''         if (isStructuredGlmCommand(command) && !this.validateStructuredGlmBeforeRun()) return false;
         if (isStructuredFractionalOutcomeCommand(command) && !this.validateStructuredFractionalOutcomeBeforeRun()) return false;
''', 'glm validation route')

# Dedicated implementation before fractional helpers.
anchor = '''      private void setStructuredFractionalWeights() {
'''
methods = r'''      private void setStructuredGlmWeights() {
         this.genericWeightType.removeAllItems();
         this.genericWeightType.addItem("无");
         this.genericWeightType.addItem("fweight");
         this.genericWeightType.addItem("aweight");
         this.genericWeightType.addItem("iweight");
         this.genericWeightType.addItem("pweight");
         this.genericWeightType.setSelectedItem("无");
         this.genericWeightVar.setSelectedItem(null);
         this.genericWeightVar.setEnabled(false);
      }

      private String structuredGlmFamilyCode() {
         switch (this.model.getSelectedIndex()) {
            case 0: return "gaussian";
            case 1: return "igaussian";
            case 2: return "binomial";
            case 3: return "poisson";
            case 4: return "nbinomial";
            case 5: return "gamma";
            default: return "custom";
         }
      }

      private String structuredGlmCanonicalLink(String family) {
         if ("gaussian".equals(family)) return "identity";
         if ("igaussian".equals(family)) return "power -2";
         if ("binomial".equals(family)) return "logit";
         if ("poisson".equals(family)) return "log";
         if ("nbinomial".equals(family)) return "log";
         if ("gamma".equals(family)) return "power -1";
         return "由自定义 family 决定";
      }

      private void updateStructuredGlmLinkChoices() {
         String family = this.structuredGlmFamilyCode();
         String canonical = this.structuredGlmCanonicalLink(family);
         this.time.removeAllItems();
         this.time.addItem("默认（" + canonical + "）");
         if ("gaussian".equals(family) || "igaussian".equals(family) || "poisson".equals(family) || "gamma".equals(family)) {
            this.time.addItem("identity");
            this.time.addItem("log");
            this.time.addItem("power #");
         } else if ("binomial".equals(family)) {
            this.time.addItem("identity");
            this.time.addItem("log");
            this.time.addItem("logit");
            this.time.addItem("probit");
            this.time.addItem("cloglog");
            this.time.addItem("power #");
            this.time.addItem("opower #");
            this.time.addItem("loglog");
            this.time.addItem("logc");
         } else if ("nbinomial".equals(family)) {
            this.time.addItem("identity");
            this.time.addItem("log");
            this.time.addItem("power #");
            this.time.addItem("nbinomial");
         } else {
            this.time.addItem("identity");
            this.time.addItem("log");
            this.time.addItem("logit");
            this.time.addItem("probit");
            this.time.addItem("cloglog");
            this.time.addItem("power #");
            this.time.addItem("opower #");
            this.time.addItem("nbinomial");
            this.time.addItem("loglog");
            this.time.addItem("logc");
         }
         this.time.addItem("自定义 link()");
         this.time.setSelectedIndex(0);
         this.newvar.setText("");
      }

      private void rebuildStructuredGlmForm() {
         this.rebuilding = true;
         this.formPanel.removeAll();
         this.formPanel.setLayout(new GridBagLayout());
         this.depvar.setSelectedItem(null);
         this.variables.clearSelection();
         this.panel.setSelectedItem(null);
         this.expression.setText("");
         this.newvar.setText("");
         this.ifCondition.setText("");
         this.inCondition.setText("");
         this.options.setText("");
         this.cluster.setSelectedItem(null);
         this.glmRateMode.setSelectedIndex(0);
         this.glmEstimationMode.setSelectedIndex(0);
         this.glmNoConstant.setSelected(false);
         this.glmEform.setSelected(false);
         this.glmNoConstant.setOpaque(false);
         this.glmEform.setOpaque(false);

         this.model.removeAllItems();
         this.model.addItem("Gaussian / normal");
         this.model.addItem("Inverse Gaussian");
         this.model.addItem("Binomial / Bernoulli");
         this.model.addItem("Poisson");
         this.model.addItem("Negative binomial");
         this.model.addItem("Gamma");
         this.model.addItem("自定义 family()");
         this.model.setSelectedIndex(0);
         this.updateStructuredGlmLinkChoices();

         this.vce.removeAllItems();
         this.vce.addItem("default");
         this.vce.addItem("robust");
         this.vce.addItem("cluster");
         this.vce.setSelectedIndex(0);
         this.setStructuredGlmWeights();

         this.enableVariableDrop(this.depvar, "GLM 结果变量 Y");
         this.enableVariableDrop(this.variables, "GLM 解释变量 X");
         this.enableVariableDrop(this.panel, "offset()/exposure() 变量");
         this.enableVariableDrop(this.expression, "family() 参数 / 分母变量");
         this.enableVariableDrop(this.genericWeightVar, "权重变量");
         this.enableVariableDrop(this.cluster, "聚类变量");

         this.commandTitle.setText("glm · 广义线性模型");
         this.commandTitle.setToolTipText("Stata Statistics > Generalized linear models > Generalized linear models (GLM)");
         this.exampleLabel.setText("<html><b>最简单例子：</b> glm y x, family(poisson) link(log)</html>");
         this.insightArea.setText("GLM 的核心是结果分布 family() 与均值链接 link() 的组合。页面只提供 Stata 官方允许的内置 family-link 组合，并保留自定义 family/link 入口。Gaussian+identity、binomial+logit、Poisson+log 等常见组合都有对应的专用 Stata 命令；这里适合需要统一 GLM 框架、非默认链接、准似然或特殊方差设定的情况。");
         this.syntaxArea.setText("glm depvar [indepvars] [if] [in] [weight] [, family(...) link(...) noconstant exposure(var) offset(var) vce(...) ml|irls eform options]");
         this.setWorkspaceBreadcrumb("统计  ›  广义线性模型  ›  glm");
         this.runButton.setText("运行 GLM");
         this.commandDock.setVisible(true);

         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.taskStepStripV153("结果与解释变量", "分布与链接", "估计与推断"), c);

         JPanel varsCard = this.xtregWizardCardV130(1, "结果与解释变量", "先选择结果变量 Y 与解释变量 X；GLM 允许 X 留空以估计仅常数项模型。 ");
         JPanel varsBody = this.genericCardBody();
         this.addGenericBodyField(varsBody, "结果变量 Y", this.depvar);
         this.addGenericBodyField(varsBody, "解释变量 X（可多选）", this.listPane(this.variables));
         varsCard.add(varsBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(varsCard, c);

         JPanel familyCard = this.xtregWizardCardV130(2, "分布与链接", "先选 family()；link() 会自动收窄到该 family 在 Stata 手册中允许的组合，避免生成不合法模型。 ");
         JPanel familyBody = this.genericCardBody();
         JPanel familyRow = new JPanel(new GridLayout(1, 2, 10, 0));
         familyRow.setOpaque(false);
         familyRow.add(this.fieldBlock("结果分布 family()", this.model));
         familyRow.add(this.fieldBlock("链接函数 link()", this.time));
         this.addGenericBodyField(familyBody, "GLM 结构", familyRow);
         this.addGenericBodyField(familyBody, "family() 附加参数（binomial: 分母 #/变量；nbinomial: #/ml；自定义: family 名称）", this.expression);
         this.addGenericBodyField(familyBody, "link() 参数（power/opower: 指数 #；自定义: link 名称）", this.newvar);
         JPanel rateRow = new JPanel(new GridLayout(1, 2, 10, 0));
         rateRow.setOpaque(false);
         rateRow.add(this.fieldBlock("率 / 暴露量调整", this.glmRateMode));
         rateRow.add(this.fieldBlock("offset / exposure 变量", this.panel));
         this.addGenericBodyField(familyBody, "offset / exposure（可选）", rateRow);
         familyCard.add(familyBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(familyCard, c);

         JPanel inferenceCard = this.xtregWizardCardV130(3, "估计与推断", "默认使用 ML；需要迭代重加权最小二乘时选择 IRLS。低频的 eim/opg/HAC、scale()/disp()、constraints() 等继续保留在原生 options。 ");
         JPanel inferenceBody = this.genericCardBody();
         JPanel fitRow = new JPanel(new GridLayout(1, 2, 10, 0));
         fitRow.setOpaque(false);
         fitRow.add(this.fieldBlock("估计方法", this.glmEstimationMode));
         fitRow.add(this.fieldBlock("标准误 VCE", this.vce));
         this.addGenericBodyField(inferenceBody, "估计方法与标准误", fitRow);
         this.addGenericBodyField(inferenceBody, "聚类变量（仅 vce(cluster)）", this.cluster);
         JPanel weightRow = new JPanel(new GridLayout(1, 2, 10, 0));
         weightRow.setOpaque(false);
         weightRow.add(this.fieldBlock("权重类型", this.genericWeightType));
         weightRow.add(this.fieldBlock("权重变量", this.genericWeightVar));
         this.addGenericBodyField(inferenceBody, "权重（可选）", weightRow);
         JPanel flagsRow = new JPanel(new GridLayout(1, 2, 10, 0));
         flagsRow.setOpaque(false);
         flagsRow.add(this.glmNoConstant);
         flagsRow.add(this.glmEform);
         this.addGenericBodyField(inferenceBody, "报告与常数项", flagsRow);
         JPanel sampleRow = new JPanel(new GridLayout(1, 2, 10, 0));
         sampleRow.setOpaque(false);
         sampleRow.add(this.fieldBlock("样本条件 if（可选）", this.ifCondition));
         sampleRow.add(this.fieldBlock("观测范围 in（可选）", this.inCondition));
         this.addGenericBodyField(inferenceBody, "样本", sampleRow);
         this.addGenericBodyField(inferenceBody, "更多 Stata options（可选）", this.options);
         inferenceCard.add(inferenceBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(inferenceCard, c);

         c.gridy++;
         c.weighty = 1.0;
         c.fill = GridBagConstraints.BOTH;
         this.formPanel.add(Box.createVerticalGlue(), c);

         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.rebuilding = false;
         this.updateGenericWeightConditionalFields();
         this.updateStructuredGlmPreview();
         this.statusLabel.setText("glm：family()、link()、率调整和估计方法已分开。 ");
      }

      private String structuredGlmFamilyOption() {
         String family = this.structuredGlmFamilyCode();
         String parameter = this.expression.getText().trim();
         if ("custom".equals(family)) return parameter.isBlank() ? "" : "family(" + parameter + ")";
         if ("binomial".equals(family) || "nbinomial".equals(family)) {
            return "family(" + family + (parameter.isBlank() ? "" : " " + parameter) + ")";
         }
         return "family(" + family + ")";
      }

      private String structuredGlmLinkOption() {
         if (this.time.getSelectedIndex() <= 0) return "";
         String item = selected(this.time);
         String parameter = this.newvar.getText().trim();
         if ("power #".equals(item)) return parameter.isBlank() ? "" : "link(power " + parameter + ")";
         if ("opower #".equals(item)) return parameter.isBlank() ? "" : "link(opower " + parameter + ")";
         if ("自定义 link()".equals(item)) return parameter.isBlank() ? "" : "link(" + parameter + ")";
         return "link(" + item + ")";
      }

      private void appendStructuredGlmSample(StringBuilder preview) {
         String ifText = this.ifCondition.getText().trim();
         String inText = this.inCondition.getText().trim();
         if (!ifText.isBlank()) preview.append(" if ").append(ifText);
         if (!inText.isBlank()) preview.append(" in ").append(inText);
         String type = selected(this.genericWeightType);
         String weight = selected(this.genericWeightVar);
         if (!"无".equals(type) && !weight.isBlank()) preview.append(" [").append(type).append("=").append(weight).append("]");
      }

      private void updateStructuredGlmPreview() {
         StringBuilder preview = new StringBuilder("glm");
         String y = selected(this.depvar);
         List<String> x = this.variables.getSelectedValuesList();
         if (!y.isBlank()) preview.append(" ").append(y);
         if (!x.isEmpty()) preview.append(" ").append(String.join(" ", x));
         this.appendStructuredGlmSample(preview);

         ArrayList<String> opts = new ArrayList<>();
         String family = this.structuredGlmFamilyOption();
         if (!family.isBlank()) opts.add(family);
         String link = this.structuredGlmLinkOption();
         if (!link.isBlank()) opts.add(link);
         String rateVar = selected(this.panel);
         if (this.glmRateMode.getSelectedIndex() == 1 && !rateVar.isBlank()) opts.add("offset(" + rateVar + ")");
         if (this.glmRateMode.getSelectedIndex() == 2 && !rateVar.isBlank()) opts.add("exposure(" + rateVar + ")");
         if (this.glmNoConstant.isSelected()) opts.add("noconstant");
         if (this.glmEform.isSelected()) opts.add("eform");
         if (this.glmEstimationMode.getSelectedIndex() == 1) opts.add("irls");
         String vceValue = selected(this.vce);
         if ("robust".equals(vceValue)) opts.add("vce(robust)");
         else if ("cluster".equals(vceValue) && !selected(this.cluster).isBlank()) opts.add("vce(cluster " + selected(this.cluster) + ")");
         String extra = this.options.getText().trim();
         if (!extra.isBlank()) opts.add(extra);
         if (!opts.isEmpty()) preview.append(", ").append(String.join(" ", opts));

         this.previewArea.setText(preview.toString());
         this.previewArea.setCaretPosition(0);
         this.flashCommandPreview();
      }

      private static Double structuredGlmNumber(String raw) {
         try {
            return Double.valueOf(raw.trim());
         } catch (Exception ignored) {
            return null;
         }
      }

      private boolean validateStructuredGlmBeforeRun() {
         if (selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, "glm 需要选择结果变量 Y。", "结果变量缺失", 1);
            return false;
         }

         String family = this.structuredGlmFamilyCode();
         String familyParameter = this.expression.getText().trim();
         if ("custom".equals(family) && familyParameter.isBlank()) {
            JOptionPane.showMessageDialog(this, "选择自定义 family() 后需要填写 family 名称。", "family() 缺失", 1);
            return false;
         }
         if ("binomial".equals(family) && !familyParameter.isBlank()) {
            Double n = structuredGlmNumber(familyParameter);
            if (n != null && n <= 0) {
               JOptionPane.showMessageDialog(this, "binomial 分母 #N 必须大于 0；也可以填写包含试验次数的变量名。", "binomial 分母无效", 1);
               return false;
            }
         }
         if ("nbinomial".equals(family) && !familyParameter.isBlank() && !"ml".equalsIgnoreCase(familyParameter)) {
            Double k = structuredGlmNumber(familyParameter);
            if (k == null || k <= 0) {
               JOptionPane.showMessageDialog(this, "negative binomial 的 family() 参数只能留空、填写正数 #k，或填写 ml。", "nbinomial 参数无效", 1);
               return false;
            }
         }

         String linkItem = selected(this.time);
         String linkParameter = this.newvar.getText().trim();
         if (Arrays.asList("power #", "opower #").contains(linkItem)) {
            Double power = structuredGlmNumber(linkParameter);
            if (power == null) {
               JOptionPane.showMessageDialog(this, linkItem + " 需要填写数值指数 #。", "link() 参数缺失", 1);
               return false;
            }
         }
         if ("自定义 link()".equals(linkItem) && linkParameter.isBlank()) {
            JOptionPane.showMessageDialog(this, "选择自定义 link() 后需要填写 link 名称。", "link() 缺失", 1);
            return false;
         }
         if (this.glmRateMode.getSelectedIndex() > 0 && selected(this.panel).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择 offset() 或 exposure() 后必须指定对应变量。", "率调整变量缺失", 1);
            return false;
         }
         if (!"无".equals(selected(this.genericWeightType)) && selected(this.genericWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后必须指定权重变量。", "权重变量缺失", 1);
            return false;
         }
         if ("cluster".equals(selected(this.vce)) && selected(this.cluster).isBlank()) {
            JOptionPane.showMessageDialog(this, "vce(cluster) 需要选择聚类变量。", "聚类变量缺失", 1);
            return false;
         }

         String extra = this.options.getText().trim().toLowerCase(Locale.ROOT);
         boolean irls = this.glmEstimationMode.getSelectedIndex() == 1;
         if (irls && (extra.contains("constraints(") || Pattern.compile("(^|[\\s,])collinear($|[\\s,])").matcher(extra).find())) {
            JOptionPane.showMessageDialog(this, "glm, irls 不允许 constraints() 或 collinear；请删除该选项，或切回 ML。", "IRLS 选项冲突", 1);
            return false;
         }
         if (!irls && Pattern.compile("(^|[\\s,])disp\\(").matcher(extra).find()) {
            JOptionPane.showMessageDialog(this, "disp(#) 只允许与 irls 一起使用；请切换到 IRLS 或删除 disp().", "disp() 与估计方法冲突", 1);
            return false;
         }
         if (!irls && Pattern.compile("scale\\(\\s*dev\\s*\\)").matcher(extra).find()) {
            JOptionPane.showMessageDialog(this, "scale(dev) 只允许与 irls 一起使用；请切换到 IRLS 或改用其他 scale() 设置。", "scale(dev) 与估计方法冲突", 1);
            return false;
         }
         return true;
      }

'''
if java.count(anchor) != 1:
    print(f'HX_GLM_PATCH_FAIL method anchor: {java.count(anchor)}', file=sys.stderr)
    raise SystemExit(1)
java = java.replace(anchor, methods + anchor)

# Static contract gate immediately after fractional gate and before count gate.
marker = '''for needle in (
    'private static boolean isStructuredCountOutcomeCommand(String command)',
'''
block = r'''# Generalized-linear-model Statistics method is a single, fully structured glm page.
glm_method_match = re.search(r'"广义线性模型"[^\n]*local view "([^"]+)"', registry)
if not glm_method_match:
    fail("GLM Statistics method catalog not found")
glm_catalog = set(glm_method_match.group(1).split())
if glm_catalog != {"glm"}:
    fail(f"GLM catalog classification drift: {sorted(glm_catalog)}")
for needle in (
    'private static boolean isStructuredGlmCommand(String command)',
    'private void rebuildStructuredGlmForm()',
    'private void updateStructuredGlmPreview()',
    'private boolean validateStructuredGlmBeforeRun()',
    'glm · 广义线性模型',
    'Gaussian / normal',
    'Inverse Gaussian',
    'Binomial / Bernoulli',
    'Negative binomial',
    '自定义 family()',
    '默认（power -2）',
    '默认（power -1）',
    'this.time.addItem("opower #")',
    'this.time.addItem("nbinomial")',
    'this.time.addItem("loglog")',
    'this.time.addItem("logc")',
    'family(" + family + (parameter.isBlank() ? "" : " " + parameter) + ")',
    'link(power " + parameter + ")',
    'link(opower " + parameter + ")',
    'new String[]{"无", "offset()", "exposure()"}',
    'new String[]{"ML（默认）", "IRLS"}',
    'opts.add("irls")',
    'opts.add("noconstant")',
    'opts.add("eform")',
    'this.genericWeightType.addItem("aweight")',
    'disp(#) 只允许与 irls 一起使用',
    'scale(dev) 只允许与 irls 一起使用',
):
    if needle not in java:
        fail(f"structured GLM UI contract missing: {needle}")

'''
if static.count(marker) != 1:
    print(f'HX_GLM_PATCH_FAIL static marker: {static.count(marker)}', file=sys.stderr)
    raise SystemExit(1)
static = static.replace(marker, block + marker)

JAVA.write_text(java, encoding='utf-8')
STATIC.write_text(static, encoding='utf-8')
print('HX_GLM_PATCH_OK')
