from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"missing pattern for {label} in {path}")
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")


def require(path: Path, needle: str, label: str) -> None:
    if needle not in path.read_text(encoding="utf-8"):
        raise SystemExit(f"required marker missing: {label}")


root = Path('.')

# ---------------------------------------------------------------------------
# README: cumulative change log, preserving all previous records.
# ---------------------------------------------------------------------------
readme = root / 'README.md'
replace_once(
    readme,
    '上次修改时间：**2026-08-12 14:28（UTC+8）**',
    '上次修改时间：**2026-08-12 15:08（UTC+8）**',
    'README last modified time',
)
marker = '> 维护规则：以后每次修改仓库，都在本节顶部新增一条记录，保留以前的记录，不覆盖历史。每条记录必须同时写明“修改时间”和“修改内容”。\n\n'
entry = '''### 2026-08-12 15:08（UTC+8）

**修改时间**：2026-08-12 15:08（UTC+8）

**修改内容**：

- 完成当前普通命令目录的逐项收尾审查；普通命令继续只生成并执行真实 Stata 官方命令或成熟第三方命令，HX 自定义逻辑继续集中在界面、解析、检查、调度、结果读取与 Workflow。
- 数据处理页补齐 `duplicates` / `misstable` 的明确语义；修正 `collapse` 的多变量 `by()` 设置，并为 `reshape`、`xtset`、`tsset` 提供与真实语法一致的字段名称。
- 统计检验页补齐 `ttest` 的角色说明与运行前检查，避免单样本、分组和配对三种模式混淆。
- 线性与特殊估计命令进一步结构化：`qreg` 的 `quantile()`、`cnsreg` 的 `constraints()`、`vwls` 的 `sd()`、`eivreg` 的 `reliab()`、`newey` 的 `lag()` 均提供直接字段，不再要求用户把最关键参数全部手写在高级 options 中。
- 修正 `margins` 代码生成位置，使 `dydx()` / `at()` 等内容按 Stata option 语法进入逗号后；`coefplot` 与 `event_plot` 增加命令主体输入入口，保留原作者命令语法。
- 特殊图形页统一为“核心变量直接显示，if 与低频图形 options 收入更多设置”；普通图形导航不再把 HX 的 `did_trends` 当作普通图形方法展示。
- 补齐 `tsset`、`rreg`、`cnsreg`、`vwls`、`eivreg`、`newey`、`prais` 等命令的面包屑归类和帮助映射；普通命令运行前增加必要字段与明显角色冲突检查。
- 通用命令页切换时清理上一条命令残留的字段状态，并应用语义默认值；`areg` 固定效应选择限制为单变量，其他 HDFE 命令继续支持多选。
- Java 工作台与 `hxworkbench.jar` 同步重建；完整离线 UI preview 集合、Java 11 / class major 55、命令目录覆盖和关键代码生成规则均纳入最终 smoke test。

'''
replace_once(readme, marker, marker + entry, 'README final log entry')

# ---------------------------------------------------------------------------
# Registry: finish command/workflow navigation boundary.
# ---------------------------------------------------------------------------
registry = root / 'hxregistry.ado'
replace_once(registry, '*! hxregistry 2.8.1  12aug2026', '*! hxregistry 2.9.0  12aug2026', 'registry version')
replace_once(
    registry,
    'local graph_methods "数据分布 变量关系 分组趋势 回归结果"',
    'local graph_methods "数据分布 变量关系 回归结果"',
    'remove workflow helper from ordinary graph methods',
)

# ---------------------------------------------------------------------------
# Semantics: complete explicit ordinary-command roles.
# ---------------------------------------------------------------------------
sem = root / 'hxsemantics.ado'
replace_once(sem, '*! hxsemantics 1.3.2  12aug2026', '*! hxsemantics 1.4.0  12aug2026', 'semantics version')
replace_once(
    sem,
    '    local using_label "副表 / using 文件"\n    local if_label "样本条件 if（可选）"',
    '    local using_label "副表 / using 文件"\n    local panel_label "个体 / 面板变量"\n    local time_label "时间变量"\n    local if_label "样本条件 if（可选）"',
    'default panel/time labels',
)
replace_once(
    sem,
    '''        local model_label "汇总统计量"
        local models "均值（mean） 总和（sum） 中位数（median） 样本数（count）"
        local vars_label "要汇总的数值变量"
        local dep_label "分组变量 by()"
        local has_depvar 0
        local has_varlist 1
        local needs_panel 1
''',
    '''        local model_label "汇总统计量"
        local models "均值（mean） 总和（sum） 中位数（median） 样本数（count）"
        local vars_label "要汇总的数值变量"
        local absorb_label "分组变量 by()（可多选；不分组可留空）"
        local has_depvar 0
        local has_varlist 1
        local has_absorb 1
        local needs_panel 0
''',
    'collapse multivariable by fields',
)
replace_once(
    sem,
    '''        local model_before 1
        local expr_label "变量前缀 stub（如 income）"
        local dep_label "个体标识 i()"
        local has_depvar 0
''',
    '''        local model_before 1
        local expr_label "变量前缀 stub（如 income）"
        local panel_label "个体标识 i()"
        local time_label "维度变量 j()"
        local has_depvar 0
''',
    'reshape labels',
)
replace_once(
    sem,
    '''            local example2 "xtset firm"
            local explain2 "只有个体变量，没有规则的时间变量。"
        }
        else {
''',
    '''            local example2 "xtset firm"
            local explain2 "只有个体变量，没有规则的时间变量。"
            local panel_label "面板变量（必填）"
            local time_label "时间变量（可选）"
        }
        else {
''',
    'xtset labels',
)
replace_once(
    sem,
    '''            local example2 "tsset firm year"
            local explain2 "firm 是面板变量，year 是时间变量。"
        }
        local has_depvar 0
''',
    '''            local example2 "tsset firm year"
            local explain2 "firm 是面板变量，year 是时间变量。"
            local panel_label "面板变量（可选；纯时间序列留空）"
            local time_label "时间变量（必填）"
        }
        local has_depvar 0
''',
    'tsset labels',
)

# Explicit semantics for the two official data-check commands.
insert_before_stats = '''    else if inlist("`cmd'", "summarize", "tabstat", "correlate", "pwcorr", "ttest", "tabulate") {'''
check_block = '''    else if inlist("`cmd'", "duplicates", "misstable") {
        local has_depvar 0
        local has_varlist 1
        local vars_label "检查变量（可选；留空按命令默认范围）"
        local show_advanced 1
        if "`cmd'" == "duplicates" {
            local title "duplicates report — 检查重复记录"
            local purpose1 "检查整行记录或指定变量组合是否重复。"
            local purpose2 "页面最终执行 Stata 官方 duplicates report；选变量时按这些变量判断重复。"
            local example1 "duplicates report firm year"
            local explain1 "检查 firm-year 键是否出现重复。"
            local example2 "duplicates report"
            local explain2 "检查整行完全重复的记录。"
        }
        else {
            local title "misstable summarize — 汇总缺失值"
            local purpose1 "使用 Stata 官方 misstable summarize 查看变量缺失情况。"
            local purpose2 "可选择变量；留空时按 Stata 默认范围汇总。"
            local example1 "misstable summarize y x c1"
            local explain1 "汇总 y、x、c1 的缺失情况。"
            local example2 "misstable summarize"
            local explain2 "按 Stata 默认范围汇总缺失情况。"
        }
    }
'''
replace_once(sem, insert_before_stats, check_block + insert_before_stats, 'duplicates/misstable semantics')
replace_once(
    sem,
    '            local expr_label "比较数值（如 0）"',
    '            local expr_label "比较值 / 分组变量 / 第二变量（随检验方式填写）"',
    'ttest expression role',
)

# Structured fields for high-value estimator-specific native options.
replace_once(
    sem,
    '''        else if "`cmd'" == "qreg" {
            local title "qreg — 分位数回归"
            local purpose1 "估计解释变量对因变量某个分位点的影响，而不仅是均值影响。"
            local purpose2 "默认估计中位数；其他分位点在更多设置中填写 quantile()。"
''',
    '''        else if "`cmd'" == "qreg" {
            local template "qreg"
            local has_expression 1
            local expr_label "分位点 quantile()（可选；默认 0.5）"
            local title "qreg — 分位数回归"
            local purpose1 "估计解释变量对因变量某个分位点的影响，而不仅是均值影响。"
            local purpose2 "默认估计中位数；需要其他分位点时直接填写 0 到 1 之间的数值。"
''',
    'qreg structured quantile',
)
replace_once(
    sem,
    '''        else if "`cmd'" == "cnsreg" {
            local title "cnsreg — 约束线性回归"
            local purpose1 "在预先定义的线性参数约束下估计线性回归。"
            local purpose2 "先用 constraint 定义限制，再在更多设置中填写 constraints(#)。"
''',
    '''        else if "`cmd'" == "cnsreg" {
            local template "cnsreg"
            local has_expression 1
            local expr_label "约束编号 constraints()（如 1 2）"
            local title "cnsreg — 约束线性回归"
            local purpose1 "在预先定义的线性参数约束下估计线性回归。"
            local purpose2 "先用 constraint 定义限制，再在本页填写要使用的约束编号。"
''',
    'cnsreg structured constraints',
)
replace_once(
    sem,
    '''        else if "`cmd'" == "vwls" {
            local title "vwls — 方差加权最小二乘"
            local purpose1 "使用已知或预先估计的条件标准差进行方差加权线性回归。"
            local purpose2 "常见设定是在更多设置填写 sd(sdvar)；只有方差信息有依据时才使用。"
''',
    '''        else if "`cmd'" == "vwls" {
            local template "vwls"
            local has_expression 1
            local expr_label "条件标准差变量 sd()（可选）"
            local title "vwls — 方差加权最小二乘"
            local purpose1 "使用已知或预先估计的条件标准差进行方差加权线性回归。"
            local purpose2 "有条件标准差信息时直接填写对应变量；只有方差信息有依据时才使用。"
''',
    'vwls structured sd',
)
replace_once(
    sem,
    '''        else if "`cmd'" == "eivreg" {
            local title "eivreg — 测量误差回归"
            local purpose1 "在已知解释变量测量可靠度时修正经典测量误差偏误。"
            local purpose2 "在更多设置填写 reliab(x .85) 等可靠度信息。"
''',
    '''        else if "`cmd'" == "eivreg" {
            local template "eivreg"
            local has_expression 1
            local expr_label "可靠度 reliab()（如 x .85）"
            local title "eivreg — 测量误差回归"
            local purpose1 "在已知解释变量测量可靠度时修正经典测量误差偏误。"
            local purpose2 "直接填写变量及其可靠度，例如 x .85；最终仍执行 Stata 官方 eivreg。"
''',
    'eivreg structured reliability',
)
replace_once(
    sem,
    '''        else if "`cmd'" == "newey" {
            local title "newey — Newey–West 线性回归"
            local purpose1 "用 HAC / Newey–West 标准误处理时间序列中的异方差与自相关。"
            local purpose2 "运行前应先声明时间变量，并在更多设置填写 lag(#)。"
''',
    '''        else if "`cmd'" == "newey" {
            local template "newey"
            local has_expression 1
            local expr_label "Newey–West 滞后阶数 lag()（非负整数）"
            local title "newey — Newey–West 线性回归"
            local purpose1 "用 HAC / Newey–West 标准误处理时间序列中的异方差与自相关。"
            local purpose2 "运行前应先用 tsset 声明时间变量，并在本页填写 lag 阶数。"
''',
    'newey structured lag',
)

# margins: expression is an option, not a positional argument.
replace_once(
    sem,
    '            local expr_label "要计算的内容"',
    '            local expr_label "margins 选项（如 dydx(x) 或 at(x=(0 1 2))）"',
    'margins option label',
)

# event_plot gets a real-command body field; coefplot gets an optional model/body field.
plot_marker = '    else if inlist("`cmd'", "marginsplot", "coefplot") {'
event_block = '''    else if "`cmd'" == "event_plot" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local has_if 0
        local has_in 0
        local has_weight 0
        local expr_label "event_plot 命令主体（按作者 help 填写）"
        local show_advanced 1
        local title "event_plot — 事件研究结果图"
        local purpose1 "调用已安装的第三方 event_plot 命令绘制事件研究动态系数。"
        local purpose2 "不同估计器的结果对象写法可能不同；本页保留原作者命令主体和 options，不用 HX 算法替代。"
        local example1 "help event_plot"
        local explain1 "先核对当前安装版本支持的结果对象语法。"
        local example2 "event_plot ..."
        local explain2 "在命令主体中填写作者 help 要求的结果对象，再补充图形 options。"
    }
'''
replace_once(sem, plot_marker, event_block + plot_marker, 'event_plot body semantics')
replace_once(
    sem,
    '''        else {
            local title "coefplot — 回归系数图"
            local purpose1 "把一个或多个已保存模型的系数和置信区间画在同一张图中。"
''',
    '''        else {
            local template "command_body"
            local has_expression 1
            local expr_label "模型 / 结果对象（可选，如 m1 m2）"
            local title "coefplot — 回归系数图"
            local purpose1 "把一个或多个已保存模型的系数和置信区间画在同一张图中。"
''',
    'coefplot body field',
)

# Export the new semantic labels to the Java workbench.
replace_once(
    sem,
    '''        expr_label model_label absorb_label endog_label inst_label ///
        using_label if_label example1 explain1 example2 explain2 ///''',
    '''        expr_label model_label absorb_label endog_label inst_label ///
        using_label panel_label time_label if_label example1 explain1 example2 explain2 ///''',
    'semantic panel/time char export',
)

# ---------------------------------------------------------------------------
# Preview generator: keep all output native and fix command-specific syntax.
# ---------------------------------------------------------------------------
preview = root / 'hxpreview.ado'
replace_once(preview, '*! hxpreview 1.2.1  12aug2026', '*! hxpreview 1.3.0  12aug2026', 'preview version')
replace_once(
    preview,
    '''    if `"`template'"' == "expression_body" & `"`expression'"' != "" {
        local preview `"`preview' `expression'"'
    }
    if `"`template'"' == "reshape" & `"`expression'"' != "" {
''',
    '''    if inlist(`"`template'"', "expression_body", "command_body") & `"`expression'"' != "" {
        local preview `"`preview' `expression'"'
    }
    if `"`template'"' == "reshape" & `"`expression'"' != "" {
''',
    'command body preview',
)
replace_once(
    preview,
    '''    if `"`template'"' == "margins" & `"`expression'"' != "" {
        local preview `"`preview' `expression'"'
    }
''',
    '''    if `"`template'"' == "margins" & `"`expression'"' != "" {
        local opt `"`opt' `expression'"'
    }
    if `"`template'"' == "qreg" & `"`expression'"' != "" {
        local opt `"`opt' quantile(`expression')"'
    }
    if `"`template'"' == "cnsreg" & `"`expression'"' != "" {
        local opt `"`opt' constraints(`expression')"'
    }
    if `"`template'"' == "vwls" & `"`expression'"' != "" {
        local opt `"`opt' sd(`expression')"'
    }
    if `"`template'"' == "eivreg" & `"`expression'"' != "" {
        local opt `"`opt' reliab(`expression')"'
    }
    if `"`template'"' == "newey" & `"`expression'"' != "" {
        local opt `"`opt' lag(`expression')"'
    }
''',
    'structured estimation and margins options',
)
replace_once(
    preview,
    '''    if `"`template'"' == "collapse" & `"`panel'"' != "" {
        local opt `"`opt' by(`panel')"'
    }
''',
    '''    if `"`template'"' == "collapse" & `"`absorb'"' != "" {
        local opt `"`opt' by(`absorb')"'
    }
''',
    'collapse by list',
)
replace_once(
    preview,
    '''    if "`has_absorb'" == "1" & `"`absorb'"' != "" {
        local opt `"`opt' absorb(`absorb')"'
    }
''',
    '''    if "`has_absorb'" == "1" & `"`absorb'"' != "" & `"`template'"' != "collapse" {
        local opt `"`opt' absorb(`absorb')"'
    }
''',
    'avoid collapse absorb option',
)

# ---------------------------------------------------------------------------
# Java workbench: final ordinary-page UX, validation, paths, and help mapping.
# ---------------------------------------------------------------------------
java = root / 'src/main/java/com/hexie/stata/HxWorkbench.java'

# Generic command pages must not inherit stale fields from the previous command.
replace_once(
    java,
    '''      private void rebuildForm() {
         this.rebuilding = true;
         this.formPanel.removeAll();
         this.options.setText("");
         this.refreshVariableControls();
         this.model.removeAllItems();
''',
    '''      private void rebuildForm() {
         this.rebuilding = true;
         this.formPanel.removeAll();
         this.depvar.setSelectedItem(null);
         this.panel.setSelectedItem(null);
         this.time.setSelectedItem(null);
         this.cluster.setSelectedItem(null);
         this.genericWeightType.setSelectedItem("无");
         this.genericWeightVar.setSelectedItem(null);
         this.variables.clearSelection();
         this.absorb.clearSelection();
         this.endog.clearSelection();
         this.instruments.clearSelection();
         this.newvar.setText("");
         this.expression.setText("");
         this.usingFile.setText("");
         this.ifCondition.setText("");
         this.inCondition.setText("");
         this.options.setText("");
         this.refreshVariableControls();
         this.absorb.setSelectionMode("areg".equals(this.currentCommand) ? 0 : 2);
         String defaultExpression = visibleText(HxWorkbench.StataBridge.characteristic("hxtoolbox_sem_default_expression"));
         if (!defaultExpression.isBlank()) {
            this.expression.setText(defaultExpression);
         }
         this.model.removeAllItems();
''',
    'generic form reset and defaults',
)
replace_once(
    java,
    '''         if (this.flag("needs_panel")) {
            this.addField(var4++, "个体 / 面板变量", this.panel);
            this.addField(var4++, "时间变量", this.time);
         }
''',
    '''         if (this.flag("needs_panel")) {
            this.addField(var4++, this.sem("panel_label"), this.panel);
            this.addField(var4++, this.sem("time_label"), this.time);
         }
''',
    'semantic panel/time labels in UI',
)

# Special graph pages: core fields first, low-frequency if/options behind one toggle.
replace_once(
    java,
    '''            this.addField(var2++, "要观察的变量", this.depvar);
            this.addField(var2++, "筛选条件 if（可选）", this.ifCondition);
            this.addField(var2++, "其他图形选项（可选）", this.options);
''',
    '''            this.addField(var2++, "要观察的变量", this.depvar);
            this.addSpecialGraphAdvancedSettings(var2++, true, "其他图形选项");
''',
    'univariate graph advanced settings',
)
replace_once(
    java,
    '''            this.addField(var2++, "纵轴变量 Y", this.depvar);
            this.addField(var2++, "横轴变量 X（选择一个）", this.listPane(this.variables));
            this.addField(var2++, "筛选条件 if（可选）", this.ifCondition);
            this.addField(var2++, "其他图形选项（可选）", this.options);
''',
    '''            this.addField(var2++, "纵轴变量 Y", this.depvar);
            this.addField(var2++, "横轴变量 X（选择一个）", this.listPane(this.variables));
            this.addSpecialGraphAdvancedSettings(var2++, true, "其他图形选项");
''',
    'xy graph advanced settings',
)
replace_once(
    java,
    '''            this.addField(var2++, "要观察的变量", this.depvar);
            this.addField(var2++, "分组变量（可选）", this.panel);
            this.addField(var2++, "筛选条件 if（可选）", this.ifCondition);
            this.addField(var2++, "其他图形选项（可选）", this.options);
''',
    '''            this.addField(var2++, "要观察的变量", this.depvar);
            this.addField(var2++, "分组变量（可选）", this.panel);
            this.addSpecialGraphAdvancedSettings(var2++, true, "其他图形选项");
''',
    'box graph advanced settings',
)
replace_once(
    java,
    '''            this.addField(var2++, "结果变量 Y", this.depvar);
            this.addField(var2++, "处理组变量（建议 0/1）", this.panel);
            this.addField(var2++, "时间变量", this.time);
            this.addField(var2++, "筛选条件 if（可选）", this.ifCondition);
            this.addField(var2++, "政策时点或图形选项（可选）", this.options);
''',
    '''            this.addField(var2++, "结果变量 Y", this.depvar);
            this.addField(var2++, "处理组变量（建议 0/1）", this.panel);
            this.addField(var2++, "时间变量", this.time);
            this.addSpecialGraphAdvancedSettings(var2++, true, "政策时点或其他选项");
''',
    'did trend advanced settings',
)
replace_once(
    java,
    '''            this.addField(var2++, "图层表达式", this.expression);
            this.addField(var2++, "其他图形选项（可选）", this.options);
         }

         GridBagConstraints var3 = this.constraints(0, var2);
''',
    '''            this.addField(var2++, "图层表达式", this.expression);
            this.addSpecialGraphAdvancedSettings(var2++, false, "其他图形选项");
         }

         GridBagConstraints var3 = this.constraints(0, var2);
''',
    'twoway advanced settings',
)
insert_graph_helper = '''
      private void addSpecialGraphAdvancedSettings(int row, boolean includeIf, String optionLabel) {
         JPanel content = new JPanel();
         content.setOpaque(false);
         content.setLayout(new BoxLayout(content, BoxLayout.Y_AXIS));
         if (includeIf) {
            content.add(this.labeledInline("样本条件 if", this.ifCondition));
            content.add(Box.createVerticalStrut(8));
         }
         content.add(this.labeledInline(optionLabel, this.options));
         content.setVisible(false);
         JToggleButton toggle = new JToggleButton("展开更多设置  +");
         styleSecondaryButton(toggle);
         toggle.addActionListener(event -> {
            boolean expanded = toggle.isSelected();
            toggle.setText(expanded ? "收起更多设置  −" : "展开更多设置  +");
            content.setVisible(expanded);
            this.formPanel.revalidate();
            this.formPanel.repaint();
         });
         JPanel block = new JPanel();
         block.setOpaque(false);
         block.setLayout(new BoxLayout(block, BoxLayout.Y_AXIS));
         toggle.setAlignmentX(0.0F);
         content.setAlignmentX(0.0F);
         block.add(toggle);
         block.add(Box.createVerticalStrut(7));
         block.add(content);
         this.addField(row, "更多设置", block);
      }

'''
replace_once(java, '      private void showOneClickPage(String var1) {\n', insert_graph_helper + '      private void showOneClickPage(String var1) {\n', 'special graph helper insertion')

# Final ordinary-command validation and estimator-specific guardrails.
old_validation = '''      private boolean validateFocusedEstimationBeforeRun() {
         if (!Arrays.asList("reghdfe", "ppmlhdfe", "ivregress", "ivreghdfe", "xtreg").contains(this.currentCommand)) {
            return true;
         }

         if (this.flag("has_depvar") && selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择因变量。", "因变量缺失", 1);
            return false;
         }

         if (this.flag("has_iv")) {
            List<String> var1 = this.endog.getSelectedValuesList();
            List<String> var2 = this.instruments.getSelectedValuesList();
            if (var1.isEmpty() || var2.isEmpty()) {
               JOptionPane.showMessageDialog(this, "工具变量回归需要同时选择内生变量和工具变量。", "IV 设置尚未完整", 1);
               return false;
            }

            LinkedHashSet<String> var3 = new LinkedHashSet<>(var1);
            var3.retainAll(var2);
            if (!var3.isEmpty()) {
               JOptionPane.showMessageDialog(this, "同一变量不能同时作为内生变量和工具变量：" + String.join("、", var3), "IV 变量角色重复", 2);
               return false;
            }

            String var4 = selected(this.depvar);
            if (var1.contains(var4) || var2.contains(var4)) {
               JOptionPane.showMessageDialog(this, "因变量不能同时作为内生解释变量或工具变量。", "IV 变量角色重复", 2);
               return false;
            }

            LinkedHashSet<String> var5 = new LinkedHashSet<>(this.variables.getSelectedValuesList());
            var5.retainAll(var1);
            if (!var5.isEmpty()) {
               JOptionPane.showMessageDialog(this, "正常解释变量 / 控制中重复选择了内生变量：" + String.join("、", var5), "IV 变量角色重复", 2);
               return false;
            }

            var5 = new LinkedHashSet<>(this.variables.getSelectedValuesList());
            var5.retainAll(var2);
            if (!var5.isEmpty()) {
               JOptionPane.showMessageDialog(this, "正常解释变量 / 控制中重复选择了工具变量：" + String.join("、", var5), "IV 变量角色重复", 2);
               return false;
            }
         }

         if ("cluster".equalsIgnoreCase(selected(this.vce)) && selected(this.cluster).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择 Cluster 后，请指定聚类变量。", "聚类变量缺失", 1);
            return false;
         }

         if (this.flag("has_weight")
            && !"无".equals(selected(this.genericWeightType))
            && selected(this.genericWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后，请指定权重变量。", "权重变量缺失", 1);
            return false;
         }

         return true;
      }
'''
new_validation = '''      private boolean validateFocusedEstimationBeforeRun() {
         List<String> estimators = Arrays.asList(
            "areg", "reghdfe", "qreg", "rreg", "cnsreg", "vwls", "eivreg", "newey", "prais",
            "xtreg", "xtlogit", "xtprobit", "logit", "probit", "poisson", "nbreg", "ppmlhdfe", "ivregress", "ivreghdfe"
         );
         if (!estimators.contains(this.currentCommand)) {
            return true;
         }

         if (this.flag("has_depvar") && selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择因变量。", "因变量缺失", 1);
            return false;
         }

         if ("areg".equals(this.currentCommand) && this.absorb.getSelectedValuesList().size() != 1) {
            JOptionPane.showMessageDialog(this, "areg 需要且只能选择 1 个 absorb() 固定效应变量。", "固定效应设置尚未完整", 1);
            return false;
         }

         String structured = this.expression.getText().trim();
         if ("cnsreg".equals(this.currentCommand) && structured.isBlank()) {
            JOptionPane.showMessageDialog(this, "cnsreg 需要填写已经定义好的 constraint 编号。", "约束设置尚未完整", 1);
            return false;
         }
         if ("eivreg".equals(this.currentCommand) && structured.isBlank()) {
            JOptionPane.showMessageDialog(this, "eivreg 需要填写 reliab() 中的变量及可靠度。", "可靠度设置尚未完整", 1);
            return false;
         }
         if ("newey".equals(this.currentCommand)) {
            if (structured.isBlank() || !structured.matches("\\\\d+")) {
               JOptionPane.showMessageDialog(this, "newey 需要填写非负整数 lag 阶数，例如 4。", "lag 设置尚未完整", 1);
               return false;
            }
         }
         if ("qreg".equals(this.currentCommand) && !structured.isBlank()) {
            try {
               double q = Double.parseDouble(structured);
               if (!(q > 0.0 && q < 1.0)) {
                  throw new NumberFormatException();
               }
            } catch (NumberFormatException ex) {
               JOptionPane.showMessageDialog(this, "quantile() 请填写 0 到 1 之间的数值，例如 0.25。", "分位点无效", 1);
               return false;
            }
         }

         if (this.flag("has_iv")) {
            List<String> var1 = this.endog.getSelectedValuesList();
            List<String> var2 = this.instruments.getSelectedValuesList();
            if (var1.isEmpty() || var2.isEmpty()) {
               JOptionPane.showMessageDialog(this, "工具变量回归需要同时选择内生变量和工具变量。", "IV 设置尚未完整", 1);
               return false;
            }

            LinkedHashSet<String> var3 = new LinkedHashSet<>(var1);
            var3.retainAll(var2);
            if (!var3.isEmpty()) {
               JOptionPane.showMessageDialog(this, "同一变量不能同时作为内生变量和工具变量：" + String.join("、", var3), "IV 变量角色重复", 2);
               return false;
            }

            String var4 = selected(this.depvar);
            if (var1.contains(var4) || var2.contains(var4)) {
               JOptionPane.showMessageDialog(this, "因变量不能同时作为内生解释变量或工具变量。", "IV 变量角色重复", 2);
               return false;
            }

            LinkedHashSet<String> var5 = new LinkedHashSet<>(this.variables.getSelectedValuesList());
            var5.retainAll(var1);
            if (!var5.isEmpty()) {
               JOptionPane.showMessageDialog(this, "正常解释变量 / 控制中重复选择了内生变量：" + String.join("、", var5), "IV 变量角色重复", 2);
               return false;
            }

            var5 = new LinkedHashSet<>(this.variables.getSelectedValuesList());
            var5.retainAll(var2);
            if (!var5.isEmpty()) {
               JOptionPane.showMessageDialog(this, "正常解释变量 / 控制中重复选择了工具变量：" + String.join("、", var5), "IV 变量角色重复", 2);
               return false;
            }
         }

         if ("cluster".equalsIgnoreCase(selected(this.vce)) && selected(this.cluster).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择 Cluster 后，请指定聚类变量。", "聚类变量缺失", 1);
            return false;
         }

         if (this.flag("has_weight")
            && !"无".equals(selected(this.genericWeightType))
            && selected(this.genericWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后，请指定权重变量。", "权重变量缺失", 1);
            return false;
         }

         return true;
      }

      private boolean validateOrdinaryCommandBeforeRun() {
         String command = this.currentCommand;
         if (Arrays.asList("histogram", "kdensity", "graph_box").contains(command) && selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择要绘制的变量。", "图形设置尚未完整", 1);
            return false;
         }
         if (Arrays.asList("scatter", "lfit").contains(command)) {
            if (selected(this.depvar).isBlank() || this.variables.getSelectedValuesList().size() != 1) {
               JOptionPane.showMessageDialog(this, "请选择纵轴 Y，并且只选择 1 个横轴 X。", "图形设置尚未完整", 1);
               return false;
            }
         }
         if ("twoway".equals(command) && this.expression.getText().trim().isBlank()) {
            JOptionPane.showMessageDialog(this, "请填写 twoway 图层表达式。", "图形设置尚未完整", 1);
            return false;
         }
         if ("did_trends".equals(command)
            && (selected(this.depvar).isBlank() || selected(this.panel).isBlank() || selected(this.time).isBlank())) {
            JOptionPane.showMessageDialog(this, "趋势图需要结果变量、处理组变量和时间变量。", "趋势图设置尚未完整", 1);
            return false;
         }
         if ("generate".equals(command) && (this.newvar.getText().trim().isBlank() || this.expression.getText().trim().isBlank())) {
            JOptionPane.showMessageDialog(this, "generate 需要新变量名和计算公式。", "变量生成设置尚未完整", 1);
            return false;
         }
         if ("replace".equals(command) && (selected(this.depvar).isBlank() || this.expression.getText().trim().isBlank())) {
            JOptionPane.showMessageDialog(this, "replace 需要选择原变量并填写新的计算表达式。", "变量修改设置尚未完整", 1);
            return false;
         }
         if (Arrays.asList("encode", "decode").contains(command)
            && (selected(this.depvar).isBlank() || this.newvar.getText().trim().isBlank())) {
            JOptionPane.showMessageDialog(this, command + " 需要原变量和新变量名。", "转换设置尚未完整", 1);
            return false;
         }
         if (Arrays.asList("destring", "tostring").contains(command)) {
            if (selected(this.depvar).isBlank()) {
               JOptionPane.showMessageDialog(this, "请选择要转换的原变量。", "转换设置尚未完整", 1);
               return false;
            }
            if (!"覆盖原变量".equals(selected(this.model)) && this.newvar.getText().trim().isBlank()) {
               JOptionPane.showMessageDialog(this, "选择生成新变量时，请填写新变量名。", "转换设置尚未完整", 1);
               return false;
            }
         }
         if ("winsor2".equals(command) && this.variables.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "请选择至少 1 个需要缩尾的变量。", "缩尾设置尚未完整", 1);
            return false;
         }
         if ("merge".equals(command)
            && (this.variables.getSelectedValuesList().isEmpty() || this.usingFile.getText().trim().isBlank() || selected(this.model).isBlank())) {
            JOptionPane.showMessageDialog(this, "merge 需要合并关系、关联变量和 using 文件。", "合并设置尚未完整", 1);
            return false;
         }
         if ("append".equals(command) && this.usingFile.getText().trim().isBlank()) {
            JOptionPane.showMessageDialog(this, "append 需要选择 using 文件。", "追加设置尚未完整", 1);
            return false;
         }
         if ("reshape".equals(command)
            && (this.expression.getText().trim().isBlank() || selected(this.panel).isBlank() || selected(this.time).isBlank())) {
            JOptionPane.showMessageDialog(this, "reshape 需要 stub、i() 个体标识和 j() 维度变量。", "reshape 设置尚未完整", 1);
            return false;
         }
         if ("collapse".equals(command) && this.variables.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "collapse 需要选择至少 1 个汇总变量。", "汇总设置尚未完整", 1);
            return false;
         }
         if ("xtset".equals(command) && selected(this.panel).isBlank()) {
            JOptionPane.showMessageDialog(this, "xtset 需要选择面板变量。", "面板设置尚未完整", 1);
            return false;
         }
         if ("tsset".equals(command) && selected(this.time).isBlank()) {
            JOptionPane.showMessageDialog(this, "tsset 需要选择时间变量；纯时间序列时面板变量可以留空。", "时间设置尚未完整", 1);
            return false;
         }
         if ("ttest".equals(command)) {
            if (this.variables.getSelectedValuesList().size() != 1 || this.expression.getText().trim().isBlank()) {
               JOptionPane.showMessageDialog(this, "ttest 需要选择 1 个被检验变量，并按检验方式填写比较值、分组变量或第二变量。", "t 检验设置尚未完整", 1);
               return false;
            }
         }
         if ("tabulate".equals(command)) {
            int nvars = this.variables.getSelectedValuesList().size();
            if (nvars < 1 || nvars > 2) {
               JOptionPane.showMessageDialog(this, "tabulate 请选择 1 个变量做频数表，或 2 个变量做列联表。", "频数列联设置尚未完整", 1);
               return false;
            }
         }
         if (Arrays.asList("test", "lincom").contains(command) && this.expression.getText().trim().isBlank()) {
            JOptionPane.showMessageDialog(this, command + " 需要填写要检验或计算的系数表达式。", "后估计设置尚未完整", 1);
            return false;
         }
         if ("predict".equals(command) && this.newvar.getText().trim().isBlank()) {
            JOptionPane.showMessageDialog(this, "predict 需要填写新变量名。", "预测设置尚未完整", 1);
            return false;
         }
         return true;
      }
'''
replace_once(java, old_validation, new_validation, 'complete ordinary validation')

# Wire general validation into the run chain before command submission.
replace_once(
    java,
    '''            if (this.validateFocusedEstimationBeforeRun()
               && (!"regress".equals(this.currentCommand) || !this.regressWorkspaceActive || this.validateRegressBeforeRun())) {
''',
    '''            if (this.validateOrdinaryCommandBeforeRun()
               && this.validateFocusedEstimationBeforeRun()
               && (!"regress".equals(this.currentCommand) || !this.regressWorkspaceActive || this.validateRegressBeforeRun())) {
''',
    'wire ordinary validation',
)

# Help aliases for pseudo-navigation command names.
replace_once(
    java,
    '''                     : this.currentCommand
               );
            HxWorkbench.StataBridge.execute("help " + var1, true);
''',
    '''                     : ("graph_box".equals(this.currentCommand) ? "graph box" : ("did_trends".equals(this.currentCommand) ? "hxtrendplot" : this.currentCommand))
               );
            HxWorkbench.StataBridge.execute("help " + var1, true);
''',
    'help alias mapping',
)

# Complete breadcrumb/category mapping for every ordinary catalog command.
replace_once(
    java,
    '''         } else if (Arrays.asList("reshape", "collapse", "xtset").contains(var0)) {
            return "数据处理|数据结构";
''',
    '''         } else if (Arrays.asList("reshape", "collapse", "xtset", "tsset").contains(var0)) {
            return "数据处理|数据结构";
''',
    'tsset command path',
)
replace_once(
    java,
    '''         } else if (Arrays.asList("regress", "areg", "reghdfe", "qreg").contains(var0)) {
            return "回归模型|线性模型";
''',
    '''         } else if (Arrays.asList("regress", "areg", "reghdfe", "qreg", "rreg", "cnsreg", "vwls", "eivreg", "newey", "prais").contains(var0)) {
            return "回归模型|线性模型";
''',
    'all linear estimator paths',
)

# Sanity markers before CI build.
for p, needle, label in [
    (registry, 'local graph_methods "数据分布 变量关系 回归结果"', 'ordinary graph methods'),
    (sem, 'local template "newey"', 'newey structured semantics'),
    (sem, 'local absorb_label "分组变量 by()（可多选；不分组可留空）"', 'collapse by semantics'),
    (preview, 'local opt `"`opt\' by(`absorb\')"\'', 'collapse by preview'),
    (java, 'private boolean validateOrdinaryCommandBeforeRun()', 'ordinary validation method'),
    (java, 'this.sem("panel_label")', 'semantic panel label'),
]:
    require(p, needle, label)

print('HX_COMPLETE_COMMAND_LAYER_PATCH_OK')
