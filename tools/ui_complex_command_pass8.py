from pathlib import Path

root = Path(__file__).resolve().parents[1]
sem_path = root / "hxsemantics.ado"
preview_path = root / "hxpreview.ado"
java_path = root / "src/main/java/com/hexie/stata/HxWorkbench.java"
sem = sem_path.read_text(encoding="utf-8")
preview = preview_path.read_text(encoding="utf-8")
java = java_path.read_text(encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# Complex Stata prefixes/workflow commands should not be forced into misleading depvar/varlist boxes.
complex_block = r'''
    /* Complex prefixes, workflow commands, and multi-equation grammars are safer
       as one guided native command body than as guessed depvar/varlist roles. */
    if strpos(" sem gsem mi meta fmm irt svy bootstrap jackknife permute simulate statsby bayes bayesmh bayespredict bayesstats bayesgraph power teffects sts irf graph discrim cluster ", " `cmd' ") {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_if 0
        local has_in 0
        local has_weight 0
        local has_using 0
        local has_newvar 0
        local has_expression 1
        local has_absorb 0
        local has_vce 0
        local has_cluster 0
        local has_iv 0
        local needs_panel 0
        local model_before 0
        local models ""
        local default_model ""
        local vces "default"
        local show_advanced 0
        local expr_label "命令主体（不重复命令名）"
        local example1 "help `cmd'"
        local explain1 "先查看当前 Stata 版本支持的子命令、前缀或方程语法。"
        local example2 "`cmd' ..."
        local explain2 "页面会把这里填写的主体原样接到命令名后，并在运行前显示完整 Stata 命令。"

        if inlist("`cmd'", "sem", "gsem") {
            local expr_label "模型方程（不重复命令名；如 (y <- x1 x2)）"
            local example1 "sem (y <- x1 x2)"
            local explain1 "直接用路径 / 方程语法描述结构模型。"
            local example2 "gsem (y <- x1 x2, family(bernoulli) link(logit))"
            local explain2 "gsem 的 family/link 可与方程写在同一主体中。"
        }
        else if "`cmd'" == "mi" {
            local expr_label "mi 子命令与完整参数（如 set / impute / estimate）"
            local example1 "mi set mlong"
            local explain1 "先声明多重插补数据格式。"
            local example2 "mi estimate: regress y x1 x2"
            local explain2 "估计阶段可把完整 mi estimate 前缀主体直接写在这里。"
        }
        else if "`cmd'" == "meta" {
            local expr_label "meta 子命令与完整参数（如 set / summarize / regress）"
            local example1 "meta summarize"
            local explain1 "对已经声明的 meta 数据进行汇总。"
            local example2 "meta regress x1 x2"
            local explain2 "执行 meta 回归；数据声明可使用 meta set / meta esize。"
        }
        else if "`cmd'" == "fmm" {
            local expr_label "类别数 + 冒号后的估计命令（如 2: regress y x1 x2）"
            local example1 "fmm 2: regress y x1 x2"
            local explain1 "拟合两类有限混合线性回归。"
            local example2 "fmm 3: poisson y x1 x2"
            local explain2 "拟合三类有限混合 Poisson 模型。"
        }
        else if "`cmd'" == "irt" {
            local expr_label "IRT 模型 + 题项变量（如 2pl item1-item10）"
            local example1 "irt 2pl item1-item10"
            local explain1 "拟合二参数 Logistic IRT 模型。"
            local example2 "irt grm item1-item10"
            local explain2 "拟合 graded response model。"
        }
        else if "`cmd'" == "svy" {
            local expr_label "冒号后的估计命令（以 : 开头，如 : mean y）"
            local example1 "svy: mean y"
            local explain1 "在已 svyset 的调查设计下估计总体均值。"
            local example2 "svy: regress y x1 x2"
            local explain2 "在复杂抽样设计下运行线性回归。"
        }
        else if strpos(" bootstrap jackknife permute simulate statsby ", " `cmd' ") {
            local expr_label "统计量 / 前缀参数 + 冒号后的命令（完整写出命令名后的部分）"
            if "`cmd'" == "bootstrap" {
                local example1 "bootstrap r(mean), reps(500): summarize y"
                local explain1 "对 summarize 返回的均值进行 bootstrap。"
            }
            else if "`cmd'" == "jackknife" {
                local example1 "jackknife r(mean): summarize y"
                local explain1 "对 summarize 返回的均值进行 jackknife。"
            }
            else {
                local example1 "help `cmd'"
                local explain1 "该命令包含前缀统计量、重复设置或冒号后的被执行命令，请按当前 help 填写完整主体。"
            }
        }
        else if "`cmd'" == "bayes" {
            local expr_label "Bayes 前缀主体（如 : regress y x；前缀 options 也写在这里）"
            local example1 "bayes: regress y x1 x2"
            local explain1 "用 bayes: 前缀估计标准回归模型。"
            local example2 "bayes, gibbs: regress y x1 x2"
            local explain2 "Bayes 前缀自身的 options 位于冒号前。"
        }
        else if "`cmd'" == "bayesmh" {
            local expr_label "Bayesian 模型主体（结果变量、解释变量、likelihood、prior 等）"
            local example1 "bayesmh y x, likelihood(normal({sigma2})) prior({y:x _cons}, normal(0,100))"
            local explain1 "bayesmh 的似然和先验均属于完整模型主体。"
        }
        else if strpos(" bayespredict bayesstats bayesgraph ", " `cmd' ") {
            local expr_label "Bayesian 后估计子命令 / 结果对象与参数"
            local example1 "help `cmd'"
            local explain1 "先确认上一项 Bayesian 估计结果，再按当前后估计命令的子命令语法填写。"
        }
        else if "`cmd'" == "power" {
            local expr_label "检验类型与设计参数（如 onemean 0 0.5, power(.8)）"
            local example1 "power onemean 0 0.5, power(.8)"
            local explain1 "一元均值检验的效能 / 样本量设计。"
            local example2 "power twomeans 0 0.5, power(.8)"
            local explain2 "两组均值比较的效能 / 样本量设计。"
        }
        else if "`cmd'" == "teffects" {
            local expr_label "估计器 + 结果方程 + 处理方程（如 psmatch (y) (treat x1 x2)）"
            local example1 "teffects psmatch (y) (treat x1 x2)"
            local explain1 "使用倾向得分匹配估计处理效应。"
            local example2 "teffects ipwra (y x1 x3) (treat x1 x2)"
            local explain2 "使用双重稳健 IPWRA。"
        }
        else if "`cmd'" == "sts" {
            local expr_label "sts 子命令与参数（如 graph / list / test group）"
        }
        else if "`cmd'" == "irf" {
            local expr_label "irf 子命令与参数（如 create / graph / table）"
        }
        else if "`cmd'" == "graph" {
            local expr_label "graph 子命令与参数（如 combine / save / export / display）"
        }
        else if inlist("`cmd'", "discrim", "cluster") {
            local expr_label "子命令 + 变量与参数（按当前 Stata help 填写）"
        }
    }
'''

family_marker = '    /* Family-level copy for catalog commands that rely on the generic syntax parser.\n'
if complex_block.strip() not in sem:
    idx = sem.index(family_marker)
    sem = sem[:idx] + complex_block + "\n" + sem[idx:]

# command_body can safely represent prefix syntax when the remainder starts with ':' or ','.
old_preview = '''    if inlist(`"`template'"', "expression_body", "command_body") & `"`expression'"' != "" {
        local preview `"`preview' `expression'"'
    }
'''
new_preview = '''    if inlist(`"`template'"', "expression_body", "command_body") & `"`expression'"' != "" {
        local body = trim(`"`expression'"')
        if `"`template'"' == "command_body" & inlist(substr(`"`body'"', 1, 1), ":", ",") {
            local preview `"`preview'`body'"'
        }
        else local preview `"`preview' `body'"'
    }
'''
preview = replace_once(preview, old_preview, new_preview, "command body preview")

# Text fields used for command bodies should accept variable drag/drop at the caret.
marker = '      private void updateConditionalFields() {'
textfield_drop = r'''      private void enableVariableDrop(JTextField target, String role) {
         target.setToolTipText("可从右侧数据表表头拖入变量：" + role);
         target.setTransferHandler(new TransferHandler() {
            @Override
            public boolean canImport(TransferSupport support) {
               return support.isDataFlavorSupported(DataFlavor.stringFlavor);
            }

            @Override
            public boolean importData(TransferSupport support) {
               if (!this.canImport(support)) return false;
               try {
                  String value = ((String)support.getTransferable().getTransferData(DataFlavor.stringFlavor)).trim();
                  if (value.isBlank()) return false;
                  String current = target.getText();
                  int pos = Math.max(0, Math.min(target.getCaretPosition(), current.length()));
                  String before = current.substring(0, pos);
                  String after = current.substring(pos);
                  String insert = value;
                  if (!before.isEmpty()) {
                     char prev = before.charAt(before.length() - 1);
                     if (!Character.isWhitespace(prev) && prev != '(' && prev != ':' && prev != ',') insert = " " + insert;
                  }
                  if (!after.isEmpty()) {
                     char next = after.charAt(0);
                     if (!Character.isWhitespace(next) && next != ')' && next != ',') insert = insert + " ";
                  }
                  target.setText(before + insert + after);
                  target.setCaretPosition(Math.min((before + insert).length(), target.getText().length()));
                  target.requestFocusInWindow();
                  return true;
               } catch (Exception ex) {
                  return false;
               }
            }
         });
      }

'''
if textfield_drop.strip() not in java:
    idx = java.index(marker)
    java = java[:idx] + textfield_drop + java[idx:]

# Mark raw command-body pages before method-step calculation.
old = '''         boolean modelIsCore = this.model.getItemCount() > 0 && isCoreModelCommand(this.currentCommand);
         boolean absorbIsCore = this.flag("has_absorb")
'''
new = '''         boolean rawCommandBody = "command_body".equals(this.sem("template"));
         boolean modelIsCore = this.model.getItemCount() > 0 && isCoreModelCommand(this.currentCommand);
         boolean absorbIsCore = this.flag("has_absorb")
'''
java = replace_once(java, old, new, "raw command body flag")

old = '''         this.enableVariableDrop(this.instruments, "工具变量");
         this.enableVariableDrop(this.cluster, "聚类变量");

         String coreTitle = genericCoreTitle(this.currentCommand);
         String coreSubtitle = genericCoreSubtitle(this.currentCommand);
'''
new = '''         this.enableVariableDrop(this.instruments, "工具变量");
         this.enableVariableDrop(this.cluster, "聚类变量");
         if (rawCommandBody) this.enableVariableDrop(this.expression, "命令主体");

         String coreTitle = genericCoreTitle(this.currentCommand);
         String coreSubtitle = rawCommandBody
            ? "这个命令包含子命令、前缀、冒号或多方程结构。第一步直接填写命令名后面的完整主体；右侧变量可拖到光标位置。"
            : genericCoreSubtitle(this.currentCommand);
'''
java = replace_once(java, old, new, "command body core copy")

# Replace the last card construction so raw-body pages do not show a misleading duplicate options form.
old = '''         int advancedStep = hasMethodSettings ? 3 : 2;
         boolean advancedExpandedByDefault = Arrays.asList("keep", "drop", "replace").contains(this.currentCommand);
         String advancedSubtitle = advancedExpandedByDefault
            ? "当前任务的样本条件直接展开；其余低频参数也在这里。运行前可在下方检查真实 Stata 命令。"
            : "样本条件、观测范围、权重和原生 options 放在这里，默认收起。运行前可在下方检查真实 Stata 命令。";
         String advancedTitle = (this.flag("has_if") || this.flag("has_in") || this.flag("has_weight"))
            ? "样本与更多设置" : "检查与更多设置";
         JPanel advancedCard = this.xtregWizardCardV130(advancedStep, advancedTitle, advancedSubtitle);
         JPanel advancedBody = this.genericCardBody();
         this.rebuildGenericAdvancedContent(this.flag("has_if"), this.flag("has_in"), this.flag("has_weight"));
         this.advancedContent.setVisible(advancedExpandedByDefault);
         JToggleButton advancedToggle = new JToggleButton(advancedExpandedByDefault ? "收起更多设置  −" : "展开更多设置  +", advancedExpandedByDefault);
         styleSecondaryButton(advancedToggle);
         advancedToggle.setAlignmentX(0.0F);
         this.advancedContent.setAlignmentX(0.0F);
         advancedToggle.addActionListener(event -> {
            boolean expanded = advancedToggle.isSelected();
            advancedToggle.setText(expanded ? "收起更多设置  −" : "展开更多设置  +");
            this.advancedContent.setVisible(expanded);
            this.formPanel.revalidate();
            this.formPanel.repaint();
         });
         advancedBody.add(advancedToggle);
         advancedBody.add(Box.createVerticalStrut(8));
         advancedBody.add(this.advancedContent);
         advancedCard.add(advancedBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(advancedCard, c);
'''
new = '''         int advancedStep = hasMethodSettings ? 3 : 2;
         boolean advancedExpandedByDefault = Arrays.asList("keep", "drop", "replace").contains(this.currentCommand);
         String advancedSubtitle = rawCommandBody
            ? "复杂语法已经完整写在第一步；这里仅核对下方实时 Stata 命令，确认子命令、冒号、括号和 options 的位置。"
            : (advancedExpandedByDefault
               ? "当前任务的样本条件直接展开；其余低频参数也在这里。运行前可在下方检查真实 Stata 命令。"
               : "样本条件、观测范围、权重和原生 options 放在这里，默认收起。运行前可在下方检查真实 Stata 命令。");
         String advancedTitle = rawCommandBody ? "检查运行"
            : ((this.flag("has_if") || this.flag("has_in") || this.flag("has_weight")) ? "样本与更多设置" : "检查与更多设置");
         JPanel advancedCard = this.xtregWizardCardV130(advancedStep, advancedTitle, advancedSubtitle);
         JPanel advancedBody = this.genericCardBody();
         if (rawCommandBody) {
            JLabel rawHint = new JLabel("<html>命令主体按原生 Stata 语法直接拼接。运行前请在下方确认完整命令；复杂前缀自身的 options 也应写在第一步主体中。</html>");
            rawHint.setForeground(MUTED);
            rawHint.setFont(rawHint.getFont().deriveFont(9.8F));
            rawHint.setAlignmentX(0.0F);
            advancedBody.add(rawHint);
         } else {
            this.rebuildGenericAdvancedContent(this.flag("has_if"), this.flag("has_in"), this.flag("has_weight"));
            this.advancedContent.setVisible(advancedExpandedByDefault);
            JToggleButton advancedToggle = new JToggleButton(advancedExpandedByDefault ? "收起更多设置  −" : "展开更多设置  +", advancedExpandedByDefault);
            styleSecondaryButton(advancedToggle);
            advancedToggle.setAlignmentX(0.0F);
            this.advancedContent.setAlignmentX(0.0F);
            advancedToggle.addActionListener(event -> {
               boolean expanded = advancedToggle.isSelected();
               advancedToggle.setText(expanded ? "收起更多设置  −" : "展开更多设置  +");
               this.advancedContent.setVisible(expanded);
               this.formPanel.revalidate();
               this.formPanel.repaint();
            });
            advancedBody.add(advancedToggle);
            advancedBody.add(Box.createVerticalStrut(8));
            advancedBody.add(this.advancedContent);
         }
         advancedCard.add(advancedBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(advancedCard, c);
'''
java = replace_once(java, old, new, "raw command body final card")

old = '''         this.statusLabel.setText(this.currentCommand + "：核心操作已按任务顺序整理；低频设置集中在最后一步，可从右侧直接拖入变量。");
'''
new = '''         this.statusLabel.setText(rawCommandBody
            ? this.currentCommand + "：复杂语法使用原生命令主体输入；运行前请核对下方完整 Stata 命令。"
            : this.currentCommand + "：核心操作已按任务顺序整理；低频设置集中在最后一步，可从右侧直接拖入变量。");
'''
java = replace_once(java, old, new, "raw command body status")

sem_path.write_text(sem, encoding="utf-8")
preview_path.write_text(preview, encoding="utf-8")
java_path.write_text(java, encoding="utf-8")
print("HX_UI_COMPLEX_COMMAND_PASS8_OK")
