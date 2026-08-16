from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")

old_special = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_box", "did_trends", "twoway")'
new_special = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "did_trends", "twoway")'
if j.count(old_special) != 2:
    raise SystemExit(f"special graph route/list expected 2 matches, got {j.count(old_special)}")
j = j.replace(old_special, new_special)

box_branch = '''         } else if ("graph_box".equals(var1)) {
            this.commandTitle.setText("graph box · 分布与异常值箱线图");
'''
new_branches = '''         } else if (Arrays.asList("graph_bar", "graph_dot").contains(var1)) {
            boolean bar = "graph_bar".equals(var1);
            this.commandTitle.setText((bar ? "graph bar · 条形图" : "graph dot · 点图"));
            this.exampleLabel.setText("<html><b>最简单例子：</b> " + (bar ? "graph bar price, over(foreign)" : "graph dot price, over(foreign)") + "</html>");
            this.insightArea.setText("主要意图：汇总一个或多个数值变量，并按可选分类变量比较组间水平。\\n\\n数值变量至少选择 1 个；分组变量可选。默认统计量及 (mean)/(count) 等汇总方式继续使用 Stata 原生图形语法。\\n\\n复杂的第二层 over()、stack、percentages、标签和样式放在更多图形设置中。");
            this.syntaxArea.setText((bar ? "graph bar" : "graph dot") + " [stat] varlist [if] [, over(group) options]");
            coreTitle = "数值变量与分组";
            coreSubtitle = "选择一个或多个数值变量；需要组间比较时再选择分组变量。";
         } else if ("graph_pie".equals(var1)) {
            this.commandTitle.setText("graph pie · 饼图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> graph pie, over(foreign)</html>");
            this.insightArea.setText("主要意图：显示分类变量各类别占比，或用一个可选数值变量控制扇区大小。\\n\\n分类变量必填；最常用写法是 graph pie, over(category)。如果选择数值变量，则生成 graph pie measure, over(category)。\\n\\n标签、百分比显示、legend 和 by() 等继续放在更多图形设置中。");
            this.syntaxArea.setText("graph pie [varname] [if], over(category) [options]");
            coreTitle = "分类与扇区大小";
            coreSubtitle = "先选分类变量；只有需要用数值决定扇区大小时才选择数值变量。";
         } else if ("graph_box".equals(var1)) {
            this.commandTitle.setText("graph box · 分布与异常值箱线图");
'''
j = once(j, box_branch, new_branches, "special bar/dot/pie semantic branches")

box_form = '''         } else if ("graph_box".equals(var1)) {
            JPanel boxVars = new JPanel(new GridLayout(1, 2, 12, 0));
'''
new_forms = '''         } else if (Arrays.asList("graph_bar", "graph_dot").contains(var1)) {
            JPanel graphVars = new JPanel(new GridLayout(1, 2, 12, 0));
            graphVars.setOpaque(false);
            graphVars.add(this.fieldBlock("数值变量（可多选）", this.listPane(this.variables)));
            graphVars.add(this.fieldBlock("分组变量 over()（可选）", this.panel));
            this.addGenericBodyField(coreBody, "变量", graphVars);
            JLabel graphHint = new JLabel("需要 (mean)/(count) 等统计量或第二层 over() 时，在下一步“更多图形设置”中按 Stata 原生语法补充。");
            graphHint.setForeground(MUTED);
            graphHint.setFont(graphHint.getFont().deriveFont(9.8F));
            graphHint.setAlignmentX(0.0F);
            coreBody.add(graphHint);
         } else if ("graph_pie".equals(var1)) {
            JPanel pieVars = new JPanel(new GridLayout(1, 2, 12, 0));
            pieVars.setOpaque(false);
            pieVars.add(this.fieldBlock("分类变量 over()（必填）", this.panel));
            pieVars.add(this.fieldBlock("数值变量（可选）", this.depvar));
            this.addGenericBodyField(coreBody, "饼图变量", pieVars);
            JLabel pieHint = new JLabel("只想显示各类别频数/占比时，数值变量留空即可；例如 graph pie, over(foreign)。");
            pieHint.setForeground(MUTED);
            pieHint.setFont(pieHint.getFont().deriveFont(9.8F));
            pieHint.setAlignmentX(0.0F);
            coreBody.add(pieHint);
         } else if ("graph_box".equals(var1)) {
            JPanel boxVars = new JPanel(new GridLayout(1, 2, 12, 0));
'''
j = once(j, box_form, new_forms, "special bar/dot/pie form blocks")

box_preview = '''         } else if ("graph_box".equals(this.currentCommand)) {
            String var6 = selected(this.depvar);
'''
new_preview = '''         } else if (Arrays.asList("graph_bar", "graph_dot").contains(this.currentCommand)) {
            String nativeCommand = "graph_bar".equals(this.currentCommand) ? "graph bar" : "graph dot";
            List<String> measures = this.variables.getSelectedValuesList();
            var1 = nativeCommand + (measures.isEmpty() ? "" : " " + String.join(" ", measures));
            if (!this.ifCondition.getText().trim().isBlank()) {
               var1 = var1 + " if " + this.ifCondition.getText().trim();
            }
            ArrayList<String> graphOpts = new ArrayList<>();
            if (!selected(this.panel).isBlank()) graphOpts.add("over(" + selected(this.panel) + ")");
            if (!this.options.getText().trim().isBlank()) graphOpts.add(this.options.getText().trim());
            if (!graphOpts.isEmpty()) var1 = var1 + ", " + String.join(" ", graphOpts);
         } else if ("graph_pie".equals(this.currentCommand)) {
            String measure = selected(this.depvar);
            var1 = "graph pie" + (measure.isBlank() ? "" : " " + measure);
            if (!this.ifCondition.getText().trim().isBlank()) {
               var1 = var1 + " if " + this.ifCondition.getText().trim();
            }
            ArrayList<String> pieOpts = new ArrayList<>();
            if (!selected(this.panel).isBlank()) pieOpts.add("over(" + selected(this.panel) + ")");
            if (!this.options.getText().trim().isBlank()) pieOpts.add(this.options.getText().trim());
            if (!pieOpts.isEmpty()) var1 = var1 + ", " + String.join(" ", pieOpts);
         } else if ("graph_box".equals(this.currentCommand)) {
            String var6 = selected(this.depvar);
'''
j = once(j, box_preview, new_preview, "special bar/dot/pie preview branches")

validation_anchor = '''         if (Arrays.asList("histogram", "kdensity", "graph_box").contains(command) && selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择要绘制的变量。", "图形设置尚未完整", 1);
            return false;
         }
'''
validation_add = '''         if (Arrays.asList("graph_bar", "graph_dot").contains(command) && this.variables.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "请选择至少 1 个数值变量。", "图形设置尚未完整", 1);
            return false;
         }
         if ("graph_pie".equals(command) && selected(this.panel).isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择饼图的分类变量 over()。", "图形设置尚未完整", 1);
            return false;
         }
'''
j = once(j, validation_anchor, validation_anchor + validation_add, "special bar/dot/pie validation")

jp.write_text(j, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''if 'var8.addActionListener(var1x -> this.openCommandPage("import"));' in java:
    fail("empty-data conversion action still routes to generic import instead of hxconvert")
'''
checks = '''for graph_cmd in ("graph_bar", "graph_dot", "graph_pie"):
    special_open = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "did_trends", "twoway").contains(var1)'
    if special_open not in java:
        fail("common graph commands are not routed to the special graph page")
if 'String nativeCommand = "graph_bar".equals(this.currentCommand) ? "graph bar" : "graph dot";' not in java:
    fail("bar/dot special graph preview builder missing")
if 'var1 = "graph pie" + (measure.isBlank() ? "" : " " + measure);' not in java:
    fail("pie special graph preview builder missing")
if '请选择饼图的分类变量 over()' not in java:
    fail("pie special graph validation missing")
'''
v = once(v, anchor, anchor + checks, "common graph page contract anchor")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_COMMON_GRAPH_PAGES_PATCH_OK")
