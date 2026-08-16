from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


def exact(text: str, old: str, new: str, count: int, label: str) -> str:
    n = text.count(old)
    if n != count:
        raise SystemExit(f"{label}: expected {count} matches, got {n}")
    return text.replace(old, new)

# ---- Registry: complete the current official ROC suite ----
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.33  16aug2026", "*! hxregistry 3.1.34  16aug2026", "registry version")
r = once(
    r,
    ' roctab rocfit roccomp rocgold rocreg sts_graph ',
    ' roctab rocfit roccomp rocgold rocreg rocregplot sts_graph ',
    "graph catalog ROC suite",
)
r = once(
    r,
    'else if inlist(`"`method\'"\', "ROC分析", "roc_graph") local view "roctab rocfit roccomp rocgold rocreg"',
    'else if inlist(`"`method\'"\', "ROC分析", "roc_graph") local view "roctab rocfit roccomp rocgold rocreg rocregplot"',
    "ROC method view",
)
rp.write_text(r, encoding="utf-8", newline="\n")

# ---- Semantics: distinguish estimation from plotting and add rocregplot ----
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.30  16aug2026", "*! hxsemantics 1.4.31  16aug2026", "semantics version")
old_family = '''    else if strpos(" roctab rocfit roccomp rocgold rocreg ", " `cmd' ") {
        local title "`cmd' — ROC 分析"
        local purpose1 "用于评估、比较或回归建模二元结局预测的 ROC 曲线与区分能力。"
        local purpose2 "先明确真实二元结局和预测评分/模型；比较、协变量调整和图形设置按命令语法填写。"
    }
'''
new_family = '''    else if strpos(" roctab rocfit roccomp rocgold rocreg rocregplot ", " `cmd' ") {
        local title "`cmd' — ROC 分析"
        if "`cmd'" == "rocfit" {
            local purpose1 "拟合单一 classifier 的参数化 binormal ROC 模型；本命令首先产生估计结果，而不是直接绘图。"
            local purpose2 "需要拟合后的 ROC 图时使用 rocfit 的后估计绘图工具；不要把 rocfit 本身当成纯绘图命令。"
        }
        else if "`cmd'" == "rocreg" {
            local purpose1 "用协变量调整敏感度/特异度并进行 ROC regression；这是 ROC suite 中更一般的估计模型。"
            local purpose2 "roccov()/ctrlcov() 等结构属于模型本身；拟合后的协变量特定 ROC 曲线交给 rocregplot。"
        }
        else if "`cmd'" == "rocregplot" {
            local purpose1 "在 rocreg 估计之后绘制模型隐含的 ROC 曲线，可按 classifier 或协变量取值比较。"
            local purpose2 "这是 rocreg 的后估计绘图命令；先成功运行 rocreg，再设置 at#()、图例、标题和其他 graph options。"
        }
        else {
            local purpose1 "用于非参数 ROC 估计、ROC 面积比较或与 gold-standard ROC 曲线比较。"
            local purpose2 "先明确真实二元结局和预测评分；比较与图形设置按当前命令语法填写。"
        }
    }
'''
s = once(s, old_family, new_family, "ROC semantic family")

# Native command-body page for post-rocreg graphing. Keep all at#()/graph options intact.
anchor = '''    /* Family-level copy for catalog commands that rely on the generic syntax parser.
'''
block = '''    if "`cmd'" == "rocregplot" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_if 0
        local has_in 0
        local has_weight 0
        local has_using 0
        local has_newvar 0
        local has_expression 1
        local show_advanced 0
        local title "rocregplot — 绘制 ROC regression 结果"
        local expr_label "rocregplot 后面的完整主体（可留空，或填写 at1()/at2()/legend() 等）"
        local example1 "rocregplot"
        local explain1 "绘制最近一次 rocreg 模型对应的 ROC 曲线。"
        local example2 "rocregplot, at1(currage=40) at2(currage=50)"
        local explain2 "在两个协变量取值下比较模型隐含的 ROC 曲线。"
    }

'''
s = once(s, anchor, block + anchor, "rocregplot command body")
sp.write_text(s, encoding="utf-8", newline="\n")

# ---- Java: dedicated rocgold page, complete menu, correct result roles ----
jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")

# ROC menu summaries / preferred commands / path helpers.
j = once(j, 'case "ROC分析": return "roctab · rocfit · roccomp · rocgold · rocreg";', 'case "ROC分析": return "roctab · rocfit · roccomp · rocgold · rocreg · rocregplot";', "ROC category summary")
j = once(j, 'return Arrays.asList("roctab", "rocfit", "roccomp", "rocgold", "rocreg");', 'return Arrays.asList("roctab", "rocfit", "roccomp", "rocgold", "rocreg", "rocregplot");', "ROC preferred list")
j = once(j, 'Arrays.asList("roctab", "rocfit", "roccomp", "rocgold", "rocreg").contains(var0)', 'Arrays.asList("roctab", "rocfit", "roccomp", "rocgold", "rocreg", "rocregplot").contains(var0)', "ROC command path")

# rocgold joins the structured special graph pages. There are two copies: open route + updatePreview route.
old_special = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "graph_matrix", "twoway_contour", "tsline", "xtline", "sts_graph", "roctab", "roccomp", "did_trends", "twoway")'
new_special = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "graph_matrix", "twoway_contour", "tsline", "xtline", "sts_graph", "roctab", "roccomp", "rocgold", "did_trends", "twoway")'
j = exact(j, old_special, new_special, 2, "rocgold special routes")

# Add dedicated rocgold title/meaning before roctab/roccomp branch.
title_anchor = '''         } else if (Arrays.asList("roctab", "roccomp").contains(var1)) {
'''
title_block = '''         } else if ("rocgold".equals(var1)) {
            this.commandTitle.setText("rocgold · 与 Gold-standard ROC 比较");
            this.exampleLabel.setText("<html><b>最简单例子：</b> rocgold status goldscore model2 model3, graph</html>");
            this.insightArea.setText("主要意图：把多个 classifier 的 ROC 面积分别与一个明确的 gold-standard classifier 比较。\\n\\n真实二元结局、gold standard 和至少一个待比较评分分别选择，避免把 gold 混进普通 classifier 列表。\\n\\nSidak/Bonferroni 多重比较校正、summary 和图形样式继续放在更多设置中。");
            this.syntaxArea.setText("rocgold refvar goldclass compareclasses [if] [, sidak graph summary options]");
            coreTitle = "Gold standard 与待比较评分";
            coreSubtitle = "先选真实二元结局，再指定唯一 gold-standard classifier，最后选择一个或多个待比较评分。";
''' + title_anchor
j = once(j, title_anchor, title_block, "rocgold title branch")

# Fields: depvar=truth, panel=gold, variables=comparators.
body_anchor = '''         } else if (Arrays.asList("roctab", "roccomp").contains(var1)) {
            JPanel rocVars = new JPanel(new GridLayout(1, 2, 12, 0));
'''
body_block = '''         } else if ("rocgold".equals(var1)) {
            JPanel goldTop = new JPanel(new GridLayout(1, 2, 12, 0));
            goldTop.setOpaque(false);
            goldTop.add(this.fieldBlock("真实二元结局", this.depvar));
            goldTop.add(this.fieldBlock("Gold-standard classifier", this.panel));
            this.addGenericBodyField(coreBody, "基准角色", goldTop);
            this.addGenericBodyField(coreBody, "待比较 classifier（至少 1 个，可多选）", this.listPane(this.variables));
            JLabel goldHint = new JLabel("命令中 gold standard 固定排在第一个 classifier；本页会自动保持这个顺序。");
            goldHint.setForeground(MUTED);
            goldHint.setFont(goldHint.getFont().deriveFont(9.8F));
            goldHint.setAlignmentX(0.0F);
            coreBody.add(goldHint);
''' + body_anchor
j = once(j, body_anchor, body_block, "rocgold field branch")

# Native rocgold command always graphs in this Graphics entry.
preview_anchor = '''         } else if (Arrays.asList("roctab", "roccomp").contains(this.currentCommand)) {
'''
preview_block = '''         } else if ("rocgold".equals(this.currentCommand)) {
            List<String> compareScores = this.variables.getSelectedValuesList();
            var1 = "rocgold " + selected(this.depvar) + " " + selected(this.panel) + (compareScores.isEmpty() ? "" : " " + String.join(" ", compareScores));
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            ArrayList<String> goldOpts = new ArrayList<>();
            goldOpts.add("graph");
            if (!this.options.getText().trim().isBlank()) goldOpts.add(this.options.getText().trim());
            var1 += ", " + String.join(" ", goldOpts);
''' + preview_anchor
j = once(j, preview_anchor, preview_block, "rocgold preview builder")

# Inspector roles.
role_anchor = '''         if (Arrays.asList("roctab", "roccomp").contains(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "真实二元结局";
            if (this.variables.getSelectedValuesList().contains(variable)) return "预测评分 / 分类器";
         }
'''
role_block = '''         if ("rocgold".equals(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "真实二元结局";
            if (variable.equals(selected(this.panel))) return "Gold-standard classifier";
            if (this.variables.getSelectedValuesList().contains(variable)) return "待比较 classifier";
         }
'''
j = once(j, role_anchor, role_anchor + role_block, "rocgold inspector roles")

# Validation keeps all three roles distinct.
validation_anchor = '''         if ("roccomp".equals(command)) {
            if (selected(this.depvar).isBlank() || this.variables.getSelectedValuesList().size() < 2) {
               JOptionPane.showMessageDialog(this, "roccomp 需要 1 个真实二元结局和至少 2 个预测评分。", "ROC 设置尚未完整", 1);
               return false;
            }
            if (this.variables.getSelectedValuesList().contains(selected(this.depvar))) {
               JOptionPane.showMessageDialog(this, "真实结局不能同时作为待比较的预测评分。", "ROC 变量角色重复", 2);
               return false;
            }
         }
'''
validation_block = '''         if ("rocgold".equals(command)) {
            String truth = selected(this.depvar);
            String gold = selected(this.panel);
            List<String> comparisons = this.variables.getSelectedValuesList();
            if (truth.isBlank() || gold.isBlank() || comparisons.isEmpty()) {
               JOptionPane.showMessageDialog(this, "rocgold 需要真实二元结局、1 个 Gold-standard classifier 和至少 1 个待比较 classifier。", "ROC 设置尚未完整", 1);
               return false;
            }
            if (truth.equals(gold) || comparisons.contains(truth) || comparisons.contains(gold)) {
               JOptionPane.showMessageDialog(this, "真实结局、Gold standard 与待比较 classifier 必须使用不同变量。", "ROC 变量角色重复", 2);
               return false;
            }
         }
'''
j = once(j, validation_anchor, validation_anchor + validation_block, "rocgold validation")

# Correct output routing: estimators report in Results; graph-producing entries show Graph.
old_result = '               "roctab", "rocfit", "roccomp", "rocgold", "rocreg",\n'
new_result = '               "roctab", "roccomp", "rocgold", "rocregplot",\n'
j = once(j, old_result, new_result, "ROC result-view roles")

# Generic copy remains useful for estimator pages; add rocregplot where the group is used for headings.
j = exact(
    j,
    'Arrays.asList("roctab", "rocfit", "roccomp", "rocgold", "rocreg")',
    'Arrays.asList("roctab", "rocfit", "roccomp", "rocgold", "rocreg", "rocregplot")',
    2,
    "ROC generic headings",
)

jp.write_text(j, encoding="utf-8", newline="\n")

# ---- Static contracts ----
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''for needle in (
    'graph matrix · 散点图矩阵',
'''
checks = '''roc_suite = {"roctab", "rocfit", "roccomp", "rocgold", "rocreg", "rocregplot"}
if not roc_suite.issubset(set(local_words(registry, "graph_cmds"))):
    fail("Graphics ROC catalog is missing an official ROC-suite command")
if 'local view "roctab rocfit roccomp rocgold rocreg rocregplot"' not in registry:
    fail("ROC Graphics method must expose rocregplot")
for needle in (
    'rocgold · 与 Gold-standard ROC 比较',
    'Gold-standard classifier',
    'var1 = "rocgold "',
    'goldOpts.add("graph")',
    'rocgold 需要真实二元结局、1 个 Gold-standard classifier 和至少 1 个待比较 classifier',
    '"roctab", "roccomp", "rocgold", "rocregplot"',
    'case "ROC分析": return "roctab · rocfit · roccomp · rocgold · rocreg · rocregplot";',
):
    if needle not in java:
        fail(f"ROC role/page contract missing: {needle}")
if '"roctab", "rocfit", "roccomp", "rocgold", "rocreg",\n' in java:
    fail("rocfit/rocreg are still routed as direct graph-producing commands")
for needle in (
    'rocregplot — 绘制 ROC regression 结果',
    'rocregplot, at1(currage=40) at2(currage=50)',
    '拟合单一 classifier 的参数化 binormal ROC 模型',
    '拟合后的协变量特定 ROC 曲线交给 rocregplot',
):
    if needle not in semantics:
        fail(f"ROC semantic role contract missing: {needle}")
'''
v = once(v, anchor, checks + anchor, "ROC static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_ROC_ROLE_PATCH_OK")
