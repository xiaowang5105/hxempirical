from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "src/main/java/com/hexie/stata/HxWorkbench.java"
text = JAVA.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    text = text.replace(old, new, 1)


def insert_before(anchor: str, addition: str, label: str) -> None:
    replace_once(anchor, addition + anchor, label)


# 1. Route the Graphics back-half pages through the structured graph workspace.
old_open = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "graph_matrix", "twoway_contour", "tsline", "xtline", "sts_graph", "roctab", "roccomp", "rocgold", "did_trends", "twoway").contains(var1)'
new_open = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "graph_matrix", "twoway_contour", "tsline", "xtline", "sts_graph", "roctab", "roccomp", "rocgold", "screeplot", "scoreplot", "loadingplot", "biplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay", "symplot", "quantile", "qnorm", "pnorm", "qchi", "pchi", "qqplot", "gladder", "qladder", "dotplot", "spikeplot", "sunflower", "serrbar", "graph_combine", "graph", "did_trends", "twoway").contains(var1)'
replace_once(old_open, new_open, "openCommandPage special graph routing")

old_update = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "graph_matrix", "twoway_contour", "tsline", "xtline", "sts_graph", "roctab", "roccomp", "rocgold", "did_trends", "twoway").contains(this.currentCommand)'
new_update = 'Arrays.asList("histogram", "kdensity", "scatter", "lfit", "graph_bar", "graph_dot", "graph_pie", "graph_box", "graph_matrix", "twoway_contour", "tsline", "xtline", "sts_graph", "roctab", "roccomp", "rocgold", "screeplot", "scoreplot", "loadingplot", "biplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay", "symplot", "quantile", "qnorm", "pnorm", "qchi", "pchi", "qqplot", "gladder", "qladder", "dotplot", "spikeplot", "sunflower", "serrbar", "graph_combine", "graph", "did_trends", "twoway").contains(this.currentCommand)'
replace_once(old_update, new_update, "updatePreview special graph routing")

# 2. Postestimation/management pages should not offer an if field they cannot meaningfully use.
replace_once(
    'boolean includeIf = !"twoway".equals(var1);',
    'boolean includeIf = !"twoway".equals(var1)\n            && !Arrays.asList("screeplot", "scoreplot", "loadingplot", "cluster_dendrogram", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay", "graph_combine", "graph").contains(var1);',
    "special graph if eligibility",
)

# 3. Graph-management action selector.
old_model = '''         } else if ("sts_graph".equals(command)) {
            this.model.addItem("生存函数（默认）");
            this.model.addItem("失败函数（failure）");
            this.model.addItem("累计风险（cumhaz）");
            this.model.addItem("风险函数（hazard）");
            this.model.setSelectedIndex(0);
         } else {
            this.model.addItem("");
         }'''
new_model = '''         } else if ("sts_graph".equals(command)) {
            this.model.addItem("生存函数（默认）");
            this.model.addItem("失败函数（failure）");
            this.model.addItem("累计风险（cumhaz）");
            this.model.addItem("风险函数（hazard）");
            this.model.setSelectedIndex(0);
         } else if ("graph".equals(command)) {
            this.model.addItem("列出内存图形（dir）");
            this.model.addItem("显示图形（display）");
            this.model.addItem("保存 .gph（save）");
            this.model.addItem("导出文件（export）");
            this.model.addItem("重命名图形（rename）");
            this.model.addItem("关闭图形（close）");
            this.model.setSelectedIndex(0);
         } else {
            this.model.addItem("");
         }'''
replace_once(old_model, new_model, "graph management model selector")

# 4. Command-specific explanations for the back-half pages.
header_anchor = '         } else if ("graph_box".equals(var1)) {'
header_addition = r'''         } else if ("biplot".equals(var1)) {
            this.commandTitle.setText("biplot · 多元双标图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> biplot x1 x2 x3 x4</html>");
            this.insightArea.setText("主要意图：直接对当前数据中的多个变量做 biplot analysis，同时显示观测位置与变量方向。\n\n至少选择 2 个数值变量；变量方向与观测位置共同用于理解低维结构。\n\ndim()、rowlabel()、rowover()、generate() 和样式设置放在更多图形设置中。");
            this.syntaxArea.setText("biplot varlist [if] [, dim() rowlabel() rowover() options]");
            coreTitle = "双标图变量";
            coreSubtitle = "选择至少两个参与 biplot analysis 的数值变量；无需手写整段命令。";
         } else if (Arrays.asList("screeplot", "scoreplot", "loadingplot", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay").contains(var1)) {
            String postName;
            String postNeed;
            if ("screeplot".equals(var1)) { postName = "碎石图"; postNeed = "factor / pca 等兼容多元分析"; }
            else if ("scoreplot".equals(var1)) { postName = "因子 / 主成分得分图"; postNeed = "factor / factormat / pca / pcamat"; }
            else if ("loadingplot".equals(var1)) { postName = "因子 / 主成分载荷图"; postNeed = "factor / factormat / pca / pcamat"; }
            else if ("cabiplot".equals(var1)) { postName = "对应分析双标图"; postNeed = "ca / camat"; }
            else if ("caprojection".equals(var1)) { postName = "对应分析投影图"; postNeed = "ca / camat"; }
            else if ("mdsconfig".equals(var1)) { postName = "MDS 配置图"; postNeed = "mds / mdslong / mdsmat"; }
            else if ("mdsshepard".equals(var1)) { postName = "MDS Shepard 图"; postNeed = "mds / mdslong / mdsmat"; }
            else { postName = "Procrustes 叠加图"; postNeed = "procrustes"; }
            this.commandTitle.setText(var1 + " · " + postName);
            this.exampleLabel.setText("<html><b>最简单例子：</b> " + var1 + "</html>");
            this.insightArea.setText("这是后估计图。先运行兼容的 " + postNeed + "，本页直接沿用最近一次模型结果。\n\n页面只暴露真正属于绘图阶段的 Stata options；默认留空即可运行基础图。\n\n维度、标签、坐标轴和样式按当前命令的官方 options 继续调整。");
            this.syntaxArea.setText(var1 + " [, options]");
            coreTitle = "沿用上一模型结果";
            coreSubtitle = "无需重新选择原始变量；确认已有兼容的多元分析结果，再按需设置绘图 options。";
         } else if ("cluster_dendrogram".equals(var1)) {
            this.commandTitle.setText("cluster dendrogram · 层次聚类树状图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> cluster dendrogram</html>");
            this.insightArea.setText("主要意图：在层次聚类结果后查看对象逐步合并成簇的树状结构。\n\n聚类分析名可以留空以使用当前兼容结果，也可以显式填写之前保存的 hierarchical cluster 名。\n\nhorizontal、cutnumber()、labels 等继续放在更多图形设置中。");
            this.syntaxArea.setText("cluster dendrogram [clname] [, options]");
            coreTitle = "聚类结果";
            coreSubtitle = "通常直接沿用当前层次聚类结果；有多个聚类结果时再填写分析名。";
         } else if (Arrays.asList("symplot", "quantile", "qnorm", "pnorm", "gladder", "qladder", "spikeplot").contains(var1)) {
            this.commandTitle.setText(var1 + " · 分布诊断图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> " + var1 + " y</html>");
            this.insightArea.setText("主要意图：检查单个数值变量的分布、对称性、尾部或变换特征。\n\n本页只需要选择一个真实变量；样本条件与低频图形 options 放到下一步。\n\n图形用于描述与诊断，具体解释取决于所选分布诊断命令。");
            this.syntaxArea.setText(var1 + " varname [if] [, options]");
            coreTitle = "诊断变量";
            coreSubtitle = "选择一个要检查分布形态的数值变量。";
         } else if (Arrays.asList("qchi", "pchi").contains(var1)) {
            this.commandTitle.setText(var1 + " · 卡方分布诊断图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> " + var1 + " distance, df(2)</html>");
            this.insightArea.setText("主要意图：把一个非负统计量与指定自由度的卡方分布进行图形比较。\n\n选择待诊断变量，并显式填写 df() 自由度；工作台会自动生成 df()。\n\n其他绘图样式与样本条件继续放在更多图形设置中。");
            this.syntaxArea.setText(var1 + " varname [if], df(#) [options]");
            coreTitle = "变量与自由度";
            coreSubtitle = "选择诊断变量，并填写正的自由度 df；无需手写 df()。";
         } else if (Arrays.asList("qqplot", "sunflower").contains(var1)) {
            boolean qq = "qqplot".equals(var1);
            this.commandTitle.setText(qq ? "qqplot · 两变量 Q–Q 图" : "sunflower · 高密度散点图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> " + (qq ? "qqplot x1 x2" : "sunflower y x") + "</html>");
            this.insightArea.setText(qq
               ? "主要意图：比较两个变量的经验分布分位数。\n\n两个变量分别选择，工作台固定保持 qqplot var1 var2 的顺序，并阻止重复角色。"
               : "主要意图：用 sunflower 标记缓解大量重复/密集散点的遮挡。\n\n明确选择纵轴 Y 和横轴 X；两个角色必须使用不同变量。");
            this.syntaxArea.setText(qq ? "qqplot var1 var2 [if] [, options]" : "sunflower y x [if] [, options]");
            coreTitle = qq ? "两个分布变量" : "Y / X 坐标";
            coreSubtitle = qq ? "分别指定两个要比较经验分布的变量。" : "分别指定纵轴 Y 和横轴 X。";
         } else if ("dotplot".equals(var1)) {
            this.commandTitle.setText("dotplot · 分布型点图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> dotplot y</html>");
            this.insightArea.setText("主要意图：用堆叠点展示一个或多个变量的经验分布。\n\n这里的 dotplot 与 graph dot 汇总点图属于不同命令；本页直接选择要展示的变量列表。\n\n分组、中心和样式等按 Stata 原生 options 调整。");
            this.syntaxArea.setText("dotplot varlist [if] [, options]");
            coreTitle = "分布变量";
            coreSubtitle = "选择至少一个变量；可多选，无需手写 varlist。";
         } else if ("serrbar".equals(var1)) {
            this.commandTitle.setText("serrbar · 均值与标准误条形图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> serrbar mean se group</html>");
            this.insightArea.setText("主要意图：对已经汇总好的均值和标准误/标准差绘制误差条。\n\n命令固定需要三个角色：均值变量、误差变量和横轴/组序变量；本页分别选择并保持原生顺序。\n\n如果数据还是明细观测，请先 collapse 或其他汇总步骤生成所需统计量。");
            this.syntaxArea.setText("serrbar meanvar sevar xvar [if] [, options]");
            coreTitle = "均值 / 误差 / 横轴";
            coreSubtitle = "分别选择三个角色；工作台会阻止角色重复。";
         } else if ("graph_combine".equals(var1)) {
            this.commandTitle.setText("graph combine · 组合已生成图形");
            this.exampleLabel.setText("<html><b>最简单例子：</b> graph combine g1 g2, cols(2)</html>");
            this.insightArea.setText("主要意图：把已经命名或保存的多个 Stata 图形组合成一个版面。\n\n这里填写图形名或 .gph 文件名，空格分隔；数据变量窗口不会被误当成图形对象来源。\n\ncols()/rows()/xcommon/ycommon、标题和边距放在更多图形设置中。");
            this.syntaxArea.setText("graph combine graphlist [, options]");
            coreTitle = "待组合图形";
            coreSubtitle = "填写至少两个已命名图形或 .gph 文件；例如 g1 g2。";
         } else if ("graph".equals(var1)) {
            this.commandTitle.setText("graph · 图形对象管理");
            this.exampleLabel.setText("<html><b>最简单例子：</b> graph dir</html>");
            this.insightArea.setText("主要意图：管理已经生成的 Stata 图形对象。\n\n先选择操作，再填写对应的图形名/文件参数；列出图形 dir 不需要参数。\n\n保存和导出面向 .gph 或 PNG/SVG/PDF 等文件，页面不会要求选择数据变量。");
            this.syntaxArea.setText("graph dir | display | save | export | rename | close ...");
            coreTitle = "图形管理操作";
            coreSubtitle = "先选择 dir/display/save/export/rename/close，再填写该操作真正需要的对象或文件参数。";
'''
insert_before(header_anchor, header_addition, "back-half graph headers")

# 5. Command-specific input roles in the core card.
core_anchor = '         } else if ("graph_box".equals(var1)) {\n            JPanel boxVars = new JPanel(new GridLayout(1, 2, 12, 0));'
core_addition = r'''         } else if ("biplot".equals(var1)) {
            this.addGenericBodyField(coreBody, "参与分析的变量（至少 2 个，可多选）", this.listPane(this.variables));
            JLabel biplotHint = new JLabel("biplot 会直接对所选变量执行多元双标图分析；这里选择原始分析变量，而不是上一模型的 components。");
            biplotHint.setForeground(MUTED);
            biplotHint.setFont(biplotHint.getFont().deriveFont(9.8F));
            biplotHint.setAlignmentX(0.0F);
            coreBody.add(biplotHint);
         } else if (Arrays.asList("screeplot", "scoreplot", "loadingplot", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay").contains(var1)) {
            JLabel postHint = new JLabel("<html>本页沿用最近一次兼容模型结果。需要改变 dimensions / labels / axes 时，在下一步展开 Stata 原生图形 options。</html>");
            postHint.setForeground(MUTED);
            postHint.setFont(postHint.getFont().deriveFont(10.0F));
            postHint.setAlignmentX(0.0F);
            coreBody.add(postHint);
         } else if ("cluster_dendrogram".equals(var1)) {
            this.addGenericBodyField(coreBody, "聚类分析名（可选）", this.expression);
            JLabel clusterHint = new JLabel("留空时使用当前兼容的层次聚类结果；只有同时保存了多个 cluster result 时才需要显式填写分析名。");
            clusterHint.setForeground(MUTED);
            clusterHint.setFont(clusterHint.getFont().deriveFont(9.8F));
            clusterHint.setAlignmentX(0.0F);
            coreBody.add(clusterHint);
         } else if (Arrays.asList("symplot", "quantile", "qnorm", "pnorm", "gladder", "qladder", "spikeplot").contains(var1)) {
            this.addGenericBodyField(coreBody, "要诊断的变量", this.depvar);
         } else if (Arrays.asList("qchi", "pchi").contains(var1)) {
            JPanel chiVars = new JPanel(new GridLayout(1, 2, 12, 0));
            chiVars.setOpaque(false);
            chiVars.add(this.fieldBlock("诊断变量", this.depvar));
            chiVars.add(this.fieldBlock("自由度 df（只填数字）", this.expression));
            this.addGenericBodyField(coreBody, "变量与自由度", chiVars);
         } else if (Arrays.asList("qqplot", "sunflower").contains(var1)) {
            JPanel pairVars = new JPanel(new GridLayout(1, 2, 12, 0));
            pairVars.setOpaque(false);
            pairVars.add(this.fieldBlock("qqplot".equals(var1) ? "变量 1" : "纵轴 Y", this.depvar));
            pairVars.add(this.fieldBlock("qqplot".equals(var1) ? "变量 2" : "横轴 X", this.panel));
            this.addGenericBodyField(coreBody, "两个变量角色", pairVars);
         } else if ("dotplot".equals(var1)) {
            this.addGenericBodyField(coreBody, "分布变量（至少 1 个，可多选）", this.listPane(this.variables));
         } else if ("serrbar".equals(var1)) {
            JPanel seVars = new JPanel(new GridLayout(1, 3, 10, 0));
            seVars.setOpaque(false);
            seVars.add(this.fieldBlock("均值变量", this.depvar));
            seVars.add(this.fieldBlock("标准误 / 标准差", this.panel));
            seVars.add(this.fieldBlock("横轴 / 组序变量", this.time));
            this.addGenericBodyField(coreBody, "三个变量角色", seVars);
         } else if ("graph_combine".equals(var1)) {
            this.addGenericBodyField(coreBody, "图形名 / .gph 文件（空格分隔）", this.expression);
         } else if ("graph".equals(var1)) {
            this.addGenericBodyField(coreBody, "操作", this.model);
            this.addGenericBodyField(coreBody, "图形名 / 文件参数", this.expression);
            JLabel manageHint = new JLabel("dir 无需参数；display 可留空显示当前图；save/export 需要文件名；rename 填 old new；close 可填图形名或 _all。");
            manageHint.setForeground(MUTED);
            manageHint.setFont(manageHint.getFont().deriveFont(9.8F));
            manageHint.setAlignmentX(0.0F);
            coreBody.add(manageHint);
'''
insert_before(core_anchor, core_addition, "back-half graph core fields")

# 6. Build real Stata commands from those structured roles.
preview_anchor = '         } else if ("graph_box".equals(this.currentCommand)) {'
preview_addition = r'''         } else if ("biplot".equals(this.currentCommand)) {
            List<String> biplotVars = this.variables.getSelectedValuesList();
            var1 = "biplot" + (biplotVars.isEmpty() ? "" : " " + String.join(" ", biplotVars));
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if (Arrays.asList("screeplot", "scoreplot", "loadingplot", "cabiplot", "caprojection", "mdsconfig", "mdsshepard", "procoverlay").contains(this.currentCommand)) {
            var1 = this.currentCommand;
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if ("cluster_dendrogram".equals(this.currentCommand)) {
            String clusterName = this.expression.getText().trim();
            var1 = "cluster dendrogram" + (clusterName.isBlank() ? "" : " " + clusterName);
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if (Arrays.asList("symplot", "quantile", "qnorm", "pnorm", "gladder", "qladder", "spikeplot").contains(this.currentCommand)) {
            var1 = this.currentCommand + " " + selected(this.depvar);
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if (Arrays.asList("qchi", "pchi").contains(this.currentCommand)) {
            var1 = this.currentCommand + " " + selected(this.depvar);
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            ArrayList<String> chiOpts = new ArrayList<>();
            if (!this.expression.getText().trim().isBlank()) chiOpts.add("df(" + this.expression.getText().trim() + ")");
            if (!this.options.getText().trim().isBlank()) chiOpts.add(this.options.getText().trim());
            if (!chiOpts.isEmpty()) var1 += ", " + String.join(" ", chiOpts);
         } else if (Arrays.asList("qqplot", "sunflower").contains(this.currentCommand)) {
            var1 = this.currentCommand + " " + selected(this.depvar) + " " + selected(this.panel);
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if ("dotplot".equals(this.currentCommand)) {
            List<String> dotVars = this.variables.getSelectedValuesList();
            var1 = "dotplot" + (dotVars.isEmpty() ? "" : " " + String.join(" ", dotVars));
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if ("serrbar".equals(this.currentCommand)) {
            var1 = "serrbar " + selected(this.depvar) + " " + selected(this.panel) + " " + selected(this.time);
            if (!this.ifCondition.getText().trim().isBlank()) var1 += " if " + this.ifCondition.getText().trim();
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if ("graph_combine".equals(this.currentCommand)) {
            var1 = "graph combine " + this.expression.getText().trim();
            if (!this.options.getText().trim().isBlank()) var1 += ", " + this.options.getText().trim();
         } else if ("graph".equals(this.currentCommand)) {
            String action = selected(this.model);
            String args = this.expression.getText().trim();
            if (action.startsWith("列出")) var1 = "graph dir";
            else if (action.startsWith("显示")) var1 = "graph display" + (args.isBlank() ? "" : " " + args);
            else if (action.startsWith("保存")) var1 = "graph save" + (args.isBlank() ? "" : " " + args);
            else if (action.startsWith("导出")) var1 = "graph export" + (args.isBlank() ? "" : " " + args);
            else if (action.startsWith("重命名")) var1 = "graph rename" + (args.isBlank() ? "" : " " + args);
            else var1 = "graph close" + (args.isBlank() ? "" : " " + args);
            if (!this.options.getText().trim().isBlank() && (action.startsWith("显示") || action.startsWith("保存") || action.startsWith("导出"))) {
               var1 += ", " + this.options.getText().trim();
            }
'''
insert_before(preview_anchor, preview_addition, "back-half graph command generation")

# 7. Give the built-in preview useful variable context where possible.
replace_once(
    '            } else if (Arrays.asList("histogram", "kdensity", "graph_box").contains(this.currentCommand)) {\n               this.graphPreview.loadDistribution(var1, this.currentCommand);',
    '            } else if (Arrays.asList("histogram", "kdensity", "graph_box", "symplot", "quantile", "qnorm", "pnorm", "qchi", "pchi", "gladder", "qladder", "spikeplot").contains(this.currentCommand)) {\n               this.graphPreview.loadDistribution(var1, this.currentCommand);\n            } else if (Arrays.asList("qqplot", "sunflower").contains(this.currentCommand)) {\n               this.graphPreview.loadXY(var1, selected(this.panel), false);',
    "back-half graph preview context",
)

# 8. Right-side variable role hints should match the new pages.
role_anchor = '         if ("sts_graph".equals(this.currentCommand) && variable.equals(selected(this.panel))) return "生存曲线分组";'
role_addition = r'''         if ("biplot".equals(this.currentCommand) && this.variables.getSelectedValuesList().contains(variable)) return "双标图分析变量";
         if (Arrays.asList("symplot", "quantile", "qnorm", "pnorm", "qchi", "pchi", "gladder", "qladder", "spikeplot").contains(this.currentCommand)
            && variable.equals(selected(this.depvar))) return "分布诊断变量";
         if ("dotplot".equals(this.currentCommand) && this.variables.getSelectedValuesList().contains(variable)) return "分布点图变量";
         if ("qqplot".equals(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "Q–Q 变量 1";
            if (variable.equals(selected(this.panel))) return "Q–Q 变量 2";
         }
         if ("sunflower".equals(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "纵轴 Y";
            if (variable.equals(selected(this.panel))) return "横轴 X";
         }
         if ("serrbar".equals(this.currentCommand)) {
            if (variable.equals(selected(this.depvar))) return "均值变量";
            if (variable.equals(selected(this.panel))) return "标准误 / 标准差";
            if (variable.equals(selected(this.time))) return "横轴 / 组序变量";
         }
'''
insert_before(role_anchor, role_addition, "back-half inspector roles")

# 9. Run-time validation for the structured pages.
validation_anchor = '         if (Arrays.asList("scatter", "lfit").contains(command)) {'
validation_addition = r'''         if ("biplot".equals(command) && this.variables.getSelectedValuesList().size() < 2) {
            JOptionPane.showMessageDialog(this, "biplot 至少选择 2 个参与分析的变量。", "图形设置尚未完整", 1);
            return false;
         }
         if (Arrays.asList("symplot", "quantile", "qnorm", "pnorm", "gladder", "qladder", "spikeplot", "qchi", "pchi").contains(command)
            && selected(this.depvar).isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择要进行分布诊断的变量。", "图形设置尚未完整", 1);
            return false;
         }
         if (Arrays.asList("qchi", "pchi").contains(command)) {
            String df = this.expression.getText().trim();
            try {
               double value = Double.parseDouble(df);
               if (!(value > 0.0)) throw new NumberFormatException();
            } catch (NumberFormatException ex) {
               JOptionPane.showMessageDialog(this, command + " 需要填写正的自由度 df，例如 2。", "自由度设置无效", 1);
               return false;
            }
         }
         if (Arrays.asList("qqplot", "sunflower").contains(command)) {
            String first = selected(this.depvar), second = selected(this.panel);
            if (first.isBlank() || second.isBlank()) {
               JOptionPane.showMessageDialog(this, command + " 需要分别选择两个变量角色。", "图形设置尚未完整", 1);
               return false;
            }
            if (first.equals(second)) {
               JOptionPane.showMessageDialog(this, "两个图形角色必须使用不同变量。", "图形变量角色重复", 2);
               return false;
            }
         }
         if ("dotplot".equals(command) && this.variables.getSelectedValuesList().isEmpty()) {
            JOptionPane.showMessageDialog(this, "dotplot 至少选择 1 个分布变量。", "图形设置尚未完整", 1);
            return false;
         }
         if ("serrbar".equals(command)) {
            String mean = selected(this.depvar), error = selected(this.panel), axis = selected(this.time);
            if (mean.isBlank() || error.isBlank() || axis.isBlank()) {
               JOptionPane.showMessageDialog(this, "serrbar 需要均值变量、误差变量和横轴 / 组序变量。", "图形设置尚未完整", 1);
               return false;
            }
            if (new LinkedHashSet<>(Arrays.asList(mean, error, axis)).size() < 3) {
               JOptionPane.showMessageDialog(this, "serrbar 的三个变量角色必须使用不同变量。", "图形变量角色重复", 2);
               return false;
            }
         }
         if ("graph_combine".equals(command)) {
            String[] graphNames = this.expression.getText().trim().split("\\s+");
            if (this.expression.getText().trim().isBlank() || graphNames.length < 2) {
               JOptionPane.showMessageDialog(this, "graph combine 至少填写两个图形名或 .gph 文件名，例如 g1 g2。", "组合图形尚未完整", 1);
               return false;
            }
         }
         if ("graph".equals(command)) {
            String action = selected(this.model), args = this.expression.getText().trim();
            if ((action.startsWith("保存") || action.startsWith("导出") || action.startsWith("重命名")) && args.isBlank()) {
               JOptionPane.showMessageDialog(this, "当前 graph 操作需要填写图形名或文件参数。", "图形管理参数缺失", 1);
               return false;
            }
         }
'''
insert_before(validation_anchor, validation_addition, "back-half validation")

JAVA.write_text(text, encoding="utf-8")

# Lightweight source contracts. These run before compilation and make the one-shot patch fail closed.
required = [
    '"biplot".equals(var1)',
    '"cluster dendrogram" + (clusterName.isBlank()',
    'chiOpts.add("df(" + this.expression.getText().trim() + ")")',
    '"serrbar " + selected(this.depvar)',
    '"graph combine " + this.expression.getText().trim()',
    'this.model.addItem("列出内存图形（dir）")',
    'return "Q–Q 变量 1"',
]
final_text = JAVA.read_text(encoding="utf-8")
missing = [needle for needle in required if needle not in final_text]
if missing:
    raise SystemExit("Graphics back-half source contract missing: " + repr(missing))

print("HX_GRAPHICS_BACKHALF_PATCH_OK")
