from pathlib import Path
import sys

JAVA = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
STATIC = Path('tools/verify_static_contracts.py')


def one(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f'HX_CATEGORICAL_PATCH_FAIL {label}: {n}', file=sys.stderr)
        raise SystemExit(1)
    return text.replace(old, new)


java = JAVA.read_text(encoding='utf-8')
static = STATIC.read_text(encoding='utf-8')

# Classifier.
java = one(java,
'''      private static boolean isStructuredOrdinalOutcomeCommand(String command) {
         return Arrays.asList("hetoprobit", "zioprobit", "ziologit").contains(command);
      }
''',
'''      private static boolean isStructuredCategoricalOutcomeCommand(String command) {
         return Arrays.asList("clogit", "slogit", "cmset", "cmsummarize", "cmchoiceset", "cmtab", "cmsample", "cmclogit").contains(command);
      }

      private static boolean isStructuredOrdinalOutcomeCommand(String command) {
         return Arrays.asList("hetoprobit", "zioprobit", "ziologit").contains(command);
      }
''', 'classifier')

# Inspector roles.
java = one(java,
'''         if (isStructuredOrdinalOutcomeCommand(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "序数结果 Y";
''',
'''         if (isStructuredCategoricalOutcomeCommand(this.currentCommand)) {
            String cmd = this.currentCommand;
            if ("clogit".equals(cmd)) {
               if (variable.equals(selected(this.depvar))) return "二元结果 Y";
               if (this.variables.getSelectedValuesList().contains(variable)) return "解释变量 X";
               if (variable.equals(selected(this.panel))) return "匹配组 group()";
               if (variable.equals(this.expression.getText().trim())) return "offset()";
            } else if ("slogit".equals(cmd)) {
               if (variable.equals(selected(this.depvar))) return "多类别结果 Y";
               if (this.variables.getSelectedValuesList().contains(variable)) return "解释变量 X";
            } else if ("cmset".equals(cmd)) {
               if (variable.equals(selected(this.depvar))) return this.model.getSelectedIndex() >= 3 && this.model.getSelectedIndex() <= 4 ? "面板 ID" : "Case ID";
               if (variable.equals(selected(this.time))) return "时间变量";
               if (variable.equals(selected(this.panel))) return "备选项变量";
            } else if ("cmsummarize".equals(cmd)) {
               if (variable.equals(selected(this.depvar))) return "选择指示 choice()";
               if (this.variables.getSelectedValuesList().contains(variable)) return "汇总变量";
            } else if ("cmchoiceset".equals(cmd)) {
               if (variable.equals(selected(this.depvar))) return "比较变量";
            } else if ("cmtab".equals(cmd)) {
               if (variable.equals(selected(this.depvar))) return "选择指示 choice()";
               if (variable.equals(selected(this.panel))) return "列联比较变量";
            } else if ("cmsample".equals(cmd)) {
               if (variable.equals(selected(this.depvar))) return this.model.getSelectedIndex() == 1 ? "排名 choice()" : "选择指示 choice()";
               if (this.variables.getSelectedValuesList().contains(variable)) return "备选项特定变量";
               if (this.absorb.getSelectedValuesList().contains(variable)) return "Case-specific 变量";
            } else if ("cmclogit".equals(cmd)) {
               if (variable.equals(selected(this.depvar))) return "选择指示 Y";
               if (this.variables.getSelectedValuesList().contains(variable)) return "备选项特定变量";
               if (this.absorb.getSelectedValuesList().contains(variable)) return "Case-specific 变量";
               if (variable.equals(this.expression.getText().trim())) return "offset()";
            }
         }
         if (isStructuredOrdinalOutcomeCommand(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "序数结果 Y";
''', 'inspector roles')

# Rebuild route.
java = one(java,
'''         if (isStructuredOrdinalOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredOrdinalOutcomeForm();
            return;
         }
''',
'''         if (isStructuredCategoricalOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredCategoricalOutcomeForm();
            return;
         }

         if (isStructuredOrdinalOutcomeCommand(this.currentCommand)) {
            this.rebuildStructuredOrdinalOutcomeForm();
            return;
         }
''', 'rebuild route')

# Preview route.
java = one(java,
'''            } else if (isStructuredOrdinalOutcomeCommand(this.currentCommand)) {
               this.updateStructuredOrdinalOutcomePreview();
''',
'''            } else if (isStructuredCategoricalOutcomeCommand(this.currentCommand)) {
               this.updateStructuredCategoricalOutcomePreview();
            } else if (isStructuredOrdinalOutcomeCommand(this.currentCommand)) {
               this.updateStructuredOrdinalOutcomePreview();
''', 'preview route')

# Validation route.
java = one(java,
'''         if (isStructuredOrdinalOutcomeCommand(command) && !this.validateStructuredOrdinalOutcomeBeforeRun()) return false;
''',
'''         if (isStructuredCategoricalOutcomeCommand(command) && !this.validateStructuredCategoricalOutcomeBeforeRun()) return false;
         if (isStructuredOrdinalOutcomeCommand(command) && !this.validateStructuredOrdinalOutcomeBeforeRun()) return false;
''', 'validation route')

# Generic categorical weights and focused validation for mlogit/mprobit.
java = one(java,
'''         if (Arrays.asList("logit", "logistic", "binreg", "probit", "biprobit", "hetprobit", "scobit", "cloglog", "ologit", "oprobit", "hetoprobit", "zioprobit", "ziologit").contains(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "iweight", "pweight");
''',
'''         if (Arrays.asList("logit", "logistic", "binreg", "probit", "biprobit", "hetprobit", "scobit", "cloglog", "ologit", "oprobit", "hetoprobit", "zioprobit", "ziologit", "mlogit", "mprobit", "clogit", "slogit", "cmclogit", "cmsample").contains(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "iweight", "pweight");
         } else if ("cmsummarize".equals(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight");
         } else if ("cmtab".equals(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "iweight");
''', 'categorical weights')

java = one(java,
'''            "xtreg", "xtlogit", "xtprobit", "logit", "probit", "ologit", "oprobit", "poisson", "nbreg", "ppmlhdfe", "ivregress", "ivreghdfe",
''',
'''            "xtreg", "xtlogit", "xtprobit", "logit", "probit", "ologit", "oprobit", "mlogit", "mprobit", "poisson", "nbreg", "ppmlhdfe", "ivregress", "ivreghdfe",
''', 'focused validation')

java = one(java,
'''            "logit", "probit", "poisson", "nbreg", "ppmlhdfe"
''',
'''            "logit", "probit", "mlogit", "mprobit", "poisson", "nbreg", "ppmlhdfe"
''', 'generic core title')

categorical_methods = r'''      private static String structuredCategoricalOption(String name, String raw) {
         String value = raw == null ? "" : raw.trim();
         if (value.isBlank()) return "";
         return value.startsWith(name + "(") ? value : name + "(" + value + ")";
      }

      private void setStructuredCategoricalWeights(String command) {
         this.genericWeightType.removeAllItems();
         this.genericWeightType.addItem("无");
         if ("cmsummarize".equals(command)) {
            this.genericWeightType.addItem("fweight");
         } else if ("cmtab".equals(command)) {
            this.genericWeightType.addItem("fweight");
            this.genericWeightType.addItem("iweight");
         } else if (!Arrays.asList("cmset", "cmchoiceset").contains(command)) {
            this.genericWeightType.addItem("fweight");
            this.genericWeightType.addItem("iweight");
            this.genericWeightType.addItem("pweight");
         }
         this.genericWeightType.setSelectedItem("无");
         this.genericWeightVar.setSelectedItem(null);
         this.genericWeightVar.setEnabled(false);
      }

      private void addStructuredCategoricalSampleCard(GridBagConstraints c, String subtitle, boolean showWeight) {
         JPanel sampleCard = this.xtregWizardCardV130(3, "样本与检查", subtitle);
         JPanel sampleBody = this.genericCardBody();
         JPanel sampleRow = new JPanel(new GridLayout(1, 2, 10, 0));
         sampleRow.setOpaque(false);
         sampleRow.add(this.fieldBlock("样本条件 if（可选）", this.ifCondition));
         sampleRow.add(this.fieldBlock("观测范围 in（可选）", this.inCondition));
         this.addGenericBodyField(sampleBody, "样本范围", sampleRow);
         if (showWeight) {
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
      }

      private void rebuildStructuredCategoricalOutcomeForm() {
         String command = this.currentCommand;
         boolean clogit = "clogit".equals(command);
         boolean slogit = "slogit".equals(command);
         boolean cmset = "cmset".equals(command);
         boolean cmsummarize = "cmsummarize".equals(command);
         boolean cmchoiceset = "cmchoiceset".equals(command);
         boolean cmtab = "cmtab".equals(command);
         boolean cmsample = "cmsample".equals(command);
         boolean cmclogit = "cmclogit".equals(command);

         this.model.removeAllItems();
         if (cmset) {
            this.model.addItem("查看当前 CM 设置");
            this.model.addItem("截面：Case ID + 备选项");
            this.model.addItem("截面：Case ID，无备选项变量");
            this.model.addItem("面板：Panel ID + Time + 备选项");
            this.model.addItem("面板：Panel ID + Time，无备选项变量");
            this.model.addItem("清除 CM 设置");
            this.model.setSelectedIndex(1);
         } else if (cmsample) {
            this.model.addItem("0/1 选择变量（默认）");
            this.model.addItem("排名 choice() + ranks");
            this.model.setSelectedIndex(0);
         }
         this.setStructuredCategoricalWeights(command);

         this.enableVariableDrop(this.depvar, cmset ? "Case / Panel ID" : (cmchoiceset ? "比较变量" : "结果 / choice()"));
         this.enableVariableDrop(this.variables, cmsummarize ? "汇总变量" : (cmsample || cmclogit ? "备选项特定变量" : "解释变量 X"));
         this.enableVariableDrop(this.panel, cmset ? "备选项变量" : (clogit ? "匹配组 group()" : (cmtab ? "列联比较变量" : "辅助变量")));
         this.enableVariableDrop(this.time, "时间变量");
         this.enableVariableDrop(this.absorb, "Case-specific 变量");
         if (clogit || cmclogit) this.enableVariableDrop(this.expression, "offset() 变量");

         String title;
         String example;
         String insight;
         String syntax;
         String step1;
         String step2;
         if (clogit) {
            title = "clogit · 条件 / 固定效应 Logit";
            example = "clogit y x1 x2, group(pairid)";
            insight = "clogit 用于匹配病例-对照或组内固定效应 Logit；group() 是官方必填项。它与 McFadden 选择模型 cmclogit 不是同一个命令。";
            syntax = "clogit depvar [indepvars] [if] [in] [weight], group(varname) [offset(varname) options]";
            step1 = "结果与解释变量";
            step2 = "匹配组";
         } else if (slogit) {
            title = "slogit · Stereotype Logit";
            example = "slogit y x1 x2, dimension(1) baseoutcome(3)";
            insight = "用于多类别结果、但类别顺序是否应被完整利用并不明确的情形。dimension() 是模型维数，默认 1；最大可用维数取决于结果类别数与解释变量数量。";
            syntax = "slogit depvar [indepvars] [if] [in] [weight] [, dimension(#) baseoutcome(#|lbl) options]";
            step1 = "多类别方程";
            step2 = "维数与基准类别";
         } else if (cmset) {
            title = "cmset · 声明 Choice Model 数据结构";
            example = "cmset consumerid car";
            insight = "所有 cm 命令之前都必须先 cmset。截面数据使用 Case ID；面板 choice 数据使用 Panel ID + Time；有明确备选项时再指定 alternatives 变量。";
            syntax = "cmset caseid alt | cmset caseid, noalternatives | cmset panel time alt | cmset panel time, noalternatives | cmset | cmset, clear";
            step1 = "选择数据结构";
            step2 = "指定标识变量";
         } else if (cmsummarize) {
            title = "cmsummarize · 按已选备选项汇总变量";
            example = "cmsummarize price mpg, choice(chosen)";
            insight = "先 cmset，再选择要汇总的变量以及 0/1 choice()。官方只允许 fweight；统计量、time、altwise 和表格布局继续放在原生 options。";
            syntax = "cmsummarize varlist [if] [in] [fweight=var], choice(choicevar) [options]";
            step1 = "汇总变量";
            step2 = "选择指示";
         } else if (cmchoiceset) {
            title = "cmchoiceset · 检查 Choice Sets";
            example = "cmchoiceset";
            insight = "用于检查 choice-set 模式、大小和不平衡情况。比较变量可以留空；size、observations、time、generate() 等可组合设置继续使用原生 options。";
            syntax = "cmchoiceset [varname] [if] [in] [, options]";
            step1 = "Choice-set 检查";
            step2 = "可选比较变量";
         } else if (cmtab) {
            title = "cmtab · 已选备选项列联表";
            example = "cmtab gender, choice(purchase) row chi2";
            insight = "choice() 是必填的 0/1 选择指示变量；第二个比较变量可留空得到单向表。面板数据可在 options 中加入 time。官方允许 fweight 和 iweight。";
            syntax = "cmtab [varname] [if] [in] [weight], choice(choicevar) [options]";
            step1 = "选择指示";
            step2 = "列联比较";
         } else if (cmsample) {
            title = "cmsample · Choice Model 样本诊断";
            example = "cmsample x1 x2, choice(chosen) casevars(income)";
            insight = "用于在估计前后诊断 choice 数据错误和样本排除原因。备选项特定变量、case-specific 变量和 choice() 分开填写；排名结果使用 ranks 模式。";
            syntax = "cmsample [alt-specific varlist] [if] [in] [weight] [, choice(var) casevars(varlist) ranks generate(newvar[, replace]) options]";
            step1 = "检查变量";
            step2 = "Choice 与 Case 变量";
         } else {
            title = "cmclogit · McFadden 条件选择 Logit";
            example = "cmclogit chosen time, casevars(income partysize)";
            insight = "必须先 cmset。主 varlist 是随备选项变化的 alternative-specific 变量；casevars() 是同一 case 内保持不变的变量，两类变量不能混在一起。";
            syntax = "cmclogit depvar [alt-specific indepvars] [if] [in] [weight] [, casevars(varlist) offset(varname) options]";
            step1 = "选择方程";
            step2 = "变量角色";
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
         this.formPanel.add(this.taskStepStripV153(step1, step2, "样本与检查"), c);

         JPanel coreCard = this.xtregWizardCardV130(1, step1, cmset
            ? "先选择截面 / 面板 / 查看 / 清除模式；页面只使用当前模式需要的变量。"
            : "先把当前命令最关键的结果、选择或分析变量放到正确角色。 ");
         JPanel coreBody = this.genericCardBody();
         if (cmset) {
            this.addGenericBodyField(coreBody, "CM 设置模式", this.model);
         } else if (cmsummarize) {
            this.addGenericBodyField(coreBody, "要汇总的变量（至少 1 个）", this.listPane(this.variables));
         } else if (cmchoiceset) {
            this.addGenericBodyField(coreBody, "比较变量 varname（可选；留空检查 choice sets 本身）", this.depvar);
         } else if (cmtab) {
            this.addGenericBodyField(coreBody, "0/1 选择指示 choice()（必填）", this.depvar);
         } else if (cmsample) {
            this.addGenericBodyField(coreBody, "备选项特定数值变量（可选）", this.listPane(this.variables));
         } else {
            this.addGenericBodyField(coreBody, clogit ? "二元结果 Y" : (slogit ? "多类别结果 Y" : "0/1 选择指示 Y"), this.depvar);
            this.addGenericBodyField(coreBody, cmclogit ? "备选项特定解释变量（可选）" : "解释变量 X（可选）", this.listPane(this.variables));
         }
         coreCard.add(coreBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(coreCard, c);

         JPanel roleCard = this.xtregWizardCardV130(2, step2, cmset
            ? "Case / Panel ID 与 alternatives 是不同角色；面板模式还必须指定 Time。"
            : "把模型结构变量单独填写；页面会按 Stata 官方 option 位置生成命令。 ");
         JPanel roleBody = this.genericCardBody();
         if (clogit) {
            this.addGenericBodyField(roleBody, "匹配组 / 固定效应组 group()（必填）", this.panel);
            this.addGenericBodyField(roleBody, "offset() 变量（可选）", this.expression);
         } else if (slogit) {
            this.addGenericBodyField(roleBody, "dimension() 模型维数（可选；默认 1）", this.expression);
            this.addGenericBodyField(roleBody, "baseoutcome() 基准类别（可选）", this.newvar);
         } else if (cmset) {
            this.addGenericBodyField(roleBody, "Case ID / Panel ID", this.depvar);
            this.addGenericBodyField(roleBody, "Time（仅面板模式）", this.time);
            this.addGenericBodyField(roleBody, "Alternatives 变量（有备选项模式）", this.panel);
            JLabel hint = new JLabel("<html><b>查看当前设置</b>与<b>清除设置</b>模式不会使用这些变量；force、monthly、delta()、format() 等写入最后的原生 options。</html>");
            hint.setForeground(MUTED);
            hint.setFont(hint.getFont().deriveFont(9.8F));
            hint.setAlignmentX(0.0F);
            roleBody.add(hint);
         } else if (cmsummarize) {
            this.addGenericBodyField(roleBody, "0/1 选择指示 choice()（必填）", this.depvar);
         } else if (cmchoiceset) {
            JLabel hint = new JLabel("<html>常用原生 options：<b>size</b> 查看 choice-set 大小，<b>observations</b> 按观测而非 case 制表，<b>time</b> 查看面板时间维度，<b>generate()</b> 生成 choice-set 模式分类。</html>");
            hint.setForeground(MUTED);
            hint.setFont(hint.getFont().deriveFont(9.8F));
            hint.setAlignmentX(0.0F);
            roleBody.add(hint);
         } else if (cmtab) {
            this.addGenericBodyField(roleBody, "列联比较变量 varname（可选）", this.panel);
         } else if (cmsample) {
            this.addGenericBodyField(roleBody, "choice() 类型", this.model);
            this.addGenericBodyField(roleBody, "选择 / 排名变量 choice()（可选）", this.depvar);
            this.addGenericBodyField(roleBody, "Case-specific 变量 casevars()（可选）", this.listPane(this.absorb));
            this.addGenericBodyField(roleBody, "generate() 新变量（可选；可写 problem, replace）", this.newvar);
         } else if (cmclogit) {
            this.addGenericBodyField(roleBody, "Case-specific 变量 casevars()（可选）", this.listPane(this.absorb));
            this.addGenericBodyField(roleBody, "offset() 变量（可选）", this.expression);
         }
         roleCard.add(roleBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(roleCard, c);

         boolean showWeight = !Arrays.asList("cmset", "cmchoiceset").contains(command);
         if (cmset) {
            JPanel sampleCard = this.xtregWizardCardV130(3, "检查运行", "cmset 不使用 if / in / weight；低频 force 或时间序列单位设置只在声明模式下写入原生 options。 ");
            JPanel sampleBody = this.genericCardBody();
            this.addGenericBodyField(sampleBody, "其他 Stata options（可选）", this.options);
            sampleCard.add(sampleBody, BorderLayout.CENTER);
            c.gridy++;
            this.formPanel.add(sampleCard, c);
         } else {
            this.addStructuredCategoricalSampleCard(c, "运行前核对实时 Stata 命令；所有 cm utility / estimator 都假定数据已经正确 cmset。", showWeight);
         }

         GridBagConstraints filler = this.constraints(0, c.gridy + 1);
         filler.gridwidth = 2;
         filler.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), filler);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.rebuilding = false;
         this.updateGenericWeightConditionalFields();
         this.updateStructuredCategoricalOutcomePreview();
         this.statusLabel.setText(command + "：已按 categorical / choice-model 官方变量角色拆分。 ");
      }

      private void appendStructuredCategoricalWeight(StringBuilder preview) {
         String type = selected(this.genericWeightType);
         String variable = selected(this.genericWeightVar);
         if (!"无".equals(type) && !variable.isBlank()) preview.append(" [").append(type).append("=").append(variable).append("]");
      }

      private void appendStructuredCategoricalSample(StringBuilder preview, boolean allowWeight) {
         String ifText = this.ifCondition.getText().trim();
         String inText = this.inCondition.getText().trim();
         if (!ifText.isBlank()) preview.append(" if ").append(ifText);
         if (!inText.isBlank()) preview.append(" in ").append(inText);
         if (allowWeight) this.appendStructuredCategoricalWeight(preview);
      }

      private void updateStructuredCategoricalOutcomePreview() {
         String command = this.currentCommand;
         StringBuilder preview = new StringBuilder(command);
         ArrayList<String> opts = new ArrayList<>();
         String y = selected(this.depvar);
         List<String> x = this.variables.getSelectedValuesList();
         String extraOptions = this.options.getText().trim();

         if ("cmset".equals(command)) {
            int mode = this.model.getSelectedIndex();
            String id = selected(this.depvar);
            String timeVar = selected(this.time);
            String alt = selected(this.panel);
            if (mode == 1 || mode == 2) {
               if (!id.isBlank()) preview.append(" ").append(id);
               if (mode == 1 && !alt.isBlank()) preview.append(" ").append(alt);
               if (mode == 2) opts.add("noalternatives");
            } else if (mode == 3 || mode == 4) {
               if (!id.isBlank()) preview.append(" ").append(id);
               if (!timeVar.isBlank()) preview.append(" ").append(timeVar);
               if (mode == 3 && !alt.isBlank()) preview.append(" ").append(alt);
               if (mode == 4) opts.add("noalternatives");
            } else if (mode == 5) {
               opts.add("clear");
            }
            if (mode >= 1 && mode <= 4 && !extraOptions.isBlank()) opts.add(extraOptions);
         } else if ("clogit".equals(command)) {
            if (!y.isBlank()) preview.append(" ").append(y);
            if (!x.isEmpty()) preview.append(" ").append(String.join(" ", x));
            this.appendStructuredCategoricalSample(preview, true);
            String group = selected(this.panel);
            if (!group.isBlank()) opts.add("group(" + group + ")");
            String offset = structuredCategoricalOption("offset", this.expression.getText());
            if (!offset.isBlank()) opts.add(offset);
            if (!extraOptions.isBlank()) opts.add(extraOptions);
         } else if ("slogit".equals(command)) {
            if (!y.isBlank()) preview.append(" ").append(y);
            if (!x.isEmpty()) preview.append(" ").append(String.join(" ", x));
            this.appendStructuredCategoricalSample(preview, true);
            String dimension = structuredCategoricalOption("dimension", this.expression.getText());
            String base = structuredCategoricalOption("baseoutcome", this.newvar.getText());
            if (!dimension.isBlank()) opts.add(dimension);
            if (!base.isBlank()) opts.add(base);
            if (!extraOptions.isBlank()) opts.add(extraOptions);
         } else if ("cmsummarize".equals(command)) {
            if (!x.isEmpty()) preview.append(" ").append(String.join(" ", x));
            this.appendStructuredCategoricalSample(preview, true);
            if (!y.isBlank()) opts.add("choice(" + y + ")");
            if (!extraOptions.isBlank()) opts.add(extraOptions);
         } else if ("cmchoiceset".equals(command)) {
            if (!y.isBlank()) preview.append(" ").append(y);
            this.appendStructuredCategoricalSample(preview, false);
            if (!extraOptions.isBlank()) opts.add(extraOptions);
         } else if ("cmtab".equals(command)) {
            String compare = selected(this.panel);
            if (!compare.isBlank()) preview.append(" ").append(compare);
            this.appendStructuredCategoricalSample(preview, true);
            if (!y.isBlank()) opts.add("choice(" + y + ")");
            if (!extraOptions.isBlank()) opts.add(extraOptions);
         } else if ("cmsample".equals(command)) {
            if (!x.isEmpty()) preview.append(" ").append(String.join(" ", x));
            this.appendStructuredCategoricalSample(preview, true);
            if (!y.isBlank()) opts.add("choice(" + y + ")");
            List<String> caseVars = this.absorb.getSelectedValuesList();
            if (!caseVars.isEmpty()) opts.add("casevars(" + String.join(" ", caseVars) + ")");
            if (this.model.getSelectedIndex() == 1) opts.add("ranks");
            String generated = structuredCategoricalOption("generate", this.newvar.getText());
            if (!generated.isBlank()) opts.add(generated);
            if (!extraOptions.isBlank()) opts.add(extraOptions);
         } else if ("cmclogit".equals(command)) {
            if (!y.isBlank()) preview.append(" ").append(y);
            if (!x.isEmpty()) preview.append(" ").append(String.join(" ", x));
            this.appendStructuredCategoricalSample(preview, true);
            List<String> caseVars = this.absorb.getSelectedValuesList();
            if (!caseVars.isEmpty()) opts.add("casevars(" + String.join(" ", caseVars) + ")");
            String offset = structuredCategoricalOption("offset", this.expression.getText());
            if (!offset.isBlank()) opts.add(offset);
            if (!extraOptions.isBlank()) opts.add(extraOptions);
         }

         if (!opts.isEmpty()) preview.append(", ").append(String.join(" ", opts));
         this.rebuilding = true;
         this.previewArea.setText(preview.toString());
         this.previewArea.setCaretPosition(0);
         this.rebuilding = false;
         this.flashCommandPreview();
      }

      private boolean validateStructuredCategoricalOutcomeBeforeRun() {
         String command = this.currentCommand;
         if ("cmset".equals(command)) {
            int mode = this.model.getSelectedIndex();
            if (mode == 0 || mode == 5) return true;
            if (selected(this.depvar).isBlank()) {
               JOptionPane.showMessageDialog(this, mode >= 3 ? "面板 CM 设置需要 Panel ID。" : "截面 CM 设置需要 Case ID。", "CM 标识变量缺失", 1);
               return false;
            }
            if ((mode == 3 || mode == 4) && selected(this.time).isBlank()) {
               JOptionPane.showMessageDialog(this, "面板 CM 设置需要 Time 变量。", "CM 时间变量缺失", 1);
               return false;
            }
            if ((mode == 1 || mode == 3) && selected(this.panel).isBlank()) {
               JOptionPane.showMessageDialog(this, "当前 CM 模式需要 Alternatives 变量；若数据没有显式备选项，请改选 noalternatives 模式。", "备选项变量缺失", 1);
               return false;
            }
            return true;
         }

         if ("clogit".equals(command)) {
            if (selected(this.depvar).isBlank()) {
               JOptionPane.showMessageDialog(this, "clogit 需要选择二元结果变量 Y。", "结果变量缺失", 1);
               return false;
            }
            if (selected(this.panel).isBlank()) {
               JOptionPane.showMessageDialog(this, "clogit 的 group() 是官方必填项，请选择匹配组 / 固定效应组变量。", "group() 缺失", 1);
               return false;
            }
         } else if ("slogit".equals(command)) {
            if (selected(this.depvar).isBlank()) {
               JOptionPane.showMessageDialog(this, "slogit 需要选择多类别结果变量 Y。", "结果变量缺失", 1);
               return false;
            }
            String dimension = this.expression.getText().trim();
            if (!dimension.isBlank()) {
               try {
                  if (Integer.parseInt(dimension) <= 0) throw new NumberFormatException();
               } catch (NumberFormatException ex) {
                  JOptionPane.showMessageDialog(this, "slogit 的 dimension() 必须是正整数；实际最大维数还取决于结果类别数与解释变量数量。", "dimension() 无效", 1);
                  return false;
               }
            }
         } else if ("cmsummarize".equals(command)) {
            if (this.variables.getSelectedValuesList().isEmpty()) {
               JOptionPane.showMessageDialog(this, "cmsummarize 至少需要选择 1 个要汇总的变量。", "汇总变量缺失", 1);
               return false;
            }
            if (selected(this.depvar).isBlank()) {
               JOptionPane.showMessageDialog(this, "cmsummarize 的 choice() 是必填项，请选择 0/1 选择指示变量。", "choice() 缺失", 1);
               return false;
            }
         } else if ("cmtab".equals(command)) {
            if (selected(this.depvar).isBlank()) {
               JOptionPane.showMessageDialog(this, "cmtab 的 choice() 是必填项，请选择 0/1 选择指示变量。", "choice() 缺失", 1);
               return false;
            }
         } else if ("cmsample".equals(command)) {
            if (this.model.getSelectedIndex() == 1 && selected(this.depvar).isBlank()) {
               JOptionPane.showMessageDialog(this, "选择 ranks 模式时需要指定排名 choice() 变量。", "排名变量缺失", 1);
               return false;
            }
         } else if ("cmclogit".equals(command)) {
            if (selected(this.depvar).isBlank()) {
               JOptionPane.showMessageDialog(this, "cmclogit 需要 0/1 选择指示结果变量；每个 case 只能有一个被选中的 alternative。", "选择结果缺失", 1);
               return false;
            }
         }

         if (!Arrays.asList("cmchoiceset").contains(command) && !"无".equals(selected(this.genericWeightType)) && selected(this.genericWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后，请指定权重变量。", "权重变量缺失", 1);
            return false;
         }
         return true;
      }

'''

java = one(java,
'''      private void rebuildStructuredOrdinalOutcomeForm() {
''',
categorical_methods + '''      private void rebuildStructuredOrdinalOutcomeForm() {
''', 'categorical methods')

# Static method-level coverage gate and UI contracts.
static_anchor = '''# oneclick package knowledge remains correct for compatibility checks.\n'''
static_block = r'''# Categorical-outcome Statistics method must remain fully classified.
categorical_method_match = re.search(r'"分类结果"[^\n]*local view "([^"]+)"', registry)
if not categorical_method_match:
    fail("categorical-outcome Statistics method catalog not found")
categorical_catalog = set(categorical_method_match.group(1).split())
categorical_structured = {"clogit", "slogit", "cmset", "cmsummarize", "cmchoiceset", "cmtab", "cmsample", "cmclogit"}
categorical_guided_safe = {"mlogit", "mprobit"}
categorical_native_body = {"cmmixlogit", "cmxtmixlogit", "cmmprobit", "cmroprobit", "cmrologit", "nlogit", "asclogit", "asmprobit"}
if categorical_catalog != categorical_structured | categorical_guided_safe | categorical_native_body:
    fail(f"categorical-outcome catalog classification drift: {sorted(categorical_catalog - (categorical_structured | categorical_guided_safe | categorical_native_body))}")

'''
static = one(static, static_anchor, static_block + static_anchor, 'categorical coverage gate')

static_contract_anchor = '''for cmd in ordinal_structured:\n    if f' {cmd} ' not in semantics:\n        fail(f"ordinal structured command lost native-body safety fallback: {cmd}")\n\n'''
static_contract = r'''for needle in (
    'private static boolean isStructuredCategoricalOutcomeCommand(String command)',
    '"clogit", "slogit", "cmset", "cmsummarize", "cmchoiceset", "cmtab", "cmsample", "cmclogit"',
    'private void rebuildStructuredCategoricalOutcomeForm()',
    'private void updateStructuredCategoricalOutcomePreview()',
    'private boolean validateStructuredCategoricalOutcomeBeforeRun()',
    'clogit · 条件 / 固定效应 Logit',
    'slogit · Stereotype Logit',
    'cmset · 声明 Choice Model 数据结构',
    'cmsummarize · 按已选备选项汇总变量',
    'cmchoiceset · 检查 Choice Sets',
    'cmtab · 已选备选项列联表',
    'cmsample · Choice Model 样本诊断',
    'cmclogit · McFadden 条件选择 Logit',
    'clogit 的 group() 是官方必填项',
    'cmsummarize 的 choice() 是必填项',
    'cmtab 的 choice() 是必填项',
    '截面：Case ID + 备选项',
    '面板：Panel ID + Time + 备选项',
    'opts.add("noalternatives")',
    'opts.add("clear")',
    'opts.add("casevars(" + String.join(" ", caseVars) + ")")',
    'opts.add("ranks")',
    'structuredCategoricalOption("dimension", this.expression.getText())',
    '"mlogit", "mprobit", "poisson"',
    '"cmsummarize".equals(this.currentCommand)',
    '"cmtab".equals(this.currentCommand)',
):
    if needle not in java:
        fail(f"structured categorical-outcome UI contract missing: {needle}")
for cmd in categorical_structured | categorical_native_body:
    if f' {cmd} ' not in semantics:
        fail(f"categorical complex/native-body safety command missing from semantics: {cmd}")
preview_categorical = 'return Arrays.asList("mlogit", "mprobit", "clogit", "slogit", "cmset", "cmsummarize", "cmchoiceset", "cmtab", "cmsample", "cmclogit", "cmmixlogit", "cmxtmixlogit", "cmmprobit", "cmroprobit", "cmrologit", "nlogit", "asclogit", "asmprobit");'
if preview_categorical not in java:
    fail("Java categorical method preview catalog is incomplete")

'''
static = one(static, static_contract_anchor, static_contract_anchor + static_contract, 'categorical static contracts')

JAVA.write_text(java, encoding='utf-8')
STATIC.write_text(static, encoding='utf-8')
print('HX_CATEGORICAL_PATCH_OK')
