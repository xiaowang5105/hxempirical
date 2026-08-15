from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/main/java/com/hexie/stata/HxWorkbench.java"
text = path.read_text(encoding="utf-8")


def replace_method(signature_prefix: str, new_method: str) -> None:
    global text
    start = text.index(signature_prefix)
    brace = text.index("{", start)
    depth = 0
    end = None
    for i in range(brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise SystemExit(f"cannot find end for {signature_prefix}")
    text = text[:start] + new_method.rstrip() + text[end:]


# Preview entry points for the two remaining user-facing legacy builders.
old_allow = '''            && !"--render-oneclick-results-preview".equals(var0[0])
            && !"--render-regress-preview".equals(var0[0])) {
'''
new_allow = '''            && !"--render-oneclick-results-preview".equals(var0[0])
            && !"--render-regress-preview".equals(var0[0])
            && !"--render-regress-command-preview".equals(var0[0])
            && !"--render-special-graph-preview".equals(var0[0])
            && !"--render-did-trends-graph-preview".equals(var0[0])) {
'''
if old_allow not in text:
    raise SystemExit("preview allowlist marker not found")
text = text.replace(old_allow, new_allow, 1)

old_dispatch = '''               if (var18) {
                  var19x.openBaselineRegressionWorkspace();
               }

               var19x.setSize(1672, 901);
'''
new_dispatch = '''               if (var18) {
                  var19x.openBaselineRegressionWorkspace();
               }

               if ("--render-regress-command-preview".equals(var0[0])) {
                  var19x.showRegressPage();
               }

               if ("--render-special-graph-preview".equals(var0[0])) {
                  var19x.showSpecialGraphPage("scatter");
               }

               if ("--render-did-trends-graph-preview".equals(var0[0])) {
                  var19x.showSpecialGraphPage("did_trends");
               }

               var19x.setSize(1672, 901);
'''
if old_dispatch not in text:
    raise SystemExit("preview dispatch marker not found")
text = text.replace(old_dispatch, new_dispatch, 1)

new_regress = r'''      private void showRegressPage() {
         this.baselineTaskActive = false;
         if (this.baselineEstimatorHeader != null) this.baselineEstimatorHeader.setVisible(false);
         this.regressWorkspaceActive = true;
         this.showWorkspacePage();
         this.selectDataView();
         this.currentCommand = "regress";
         this.activeCategoryCode = "reg";
         this.activeCategoryName = "回归模型";
         if (this.activeMethodName.isBlank()) {
            this.activeMethodName = "普通线性回归";
         }

         this.commandDock.setVisible(true);
         this.commandTabs.setVisible(true);
         this.commandTabs.setSelectedIndex(0);
         this.previewArea.setEditable(true);
         this.runButton.setText("运行回归");
         this.setWorkspaceBreadcrumb("回归模型  ›  普通线性回归  ›  regress");
         this.commandTitle.setText("regress · 普通线性回归");
         this.commandTitle.setToolTipText("Stata 官方普通最小二乘回归");
         this.exampleLabel.setText("<html><b>操作顺序：</b> 先选 Y、核心 X 和控制变量，再设置标准误；样本与低频模型项最后处理。</html>");
         this.insightArea.setText("适合连续因变量的普通最小二乘回归。\n\n页面按论文实证的常用顺序组织：变量设定 → 推断设置 → 样本与更多设置。\n\n底部始终显示真实 regress 命令，运行后进入 Stata History，便于复现。");
         this.syntaxArea.setText("regress depvar indepvars [if] [in] [weight] [, vce(...) beta level(#) noconstant ...]");
         this.refreshRegressVariables(false);

         this.rebuilding = true;
         this.vce.removeAllItems();
         this.vce.addItem("default");
         this.vce.addItem("robust");
         this.vce.addItem("cluster");
         if (selected(this.vce).isBlank()) this.vce.setSelectedItem("default");
         this.rebuilding = false;

         this.enableVariableDrop(this.depvar, "因变量 Y");
         this.enableVariableDrop(this.regressX, "核心解释变量 X");
         this.enableVariableDrop(this.regressControls, "控制变量");
         this.enableVariableDrop(this.cluster, "聚类变量");

         this.formPanel.removeAll();
         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.genericStepStripV152(true, "选择变量", "推断设置"), c);

         JPanel variableCard = this.xtregWizardCardV130(1, "选择变量", "先确定因变量、核心解释变量和控制变量；右侧变量可直接拖入。");
         JPanel variableBody = this.genericCardBody();
         JPanel mainVars = new JPanel(new GridLayout(1, 2, 12, 0));
         mainVars.setOpaque(false);
         mainVars.add(this.fieldBlock("因变量 Y", this.depvar));
         mainVars.add(this.fieldBlock("核心解释变量 X", this.regressX));
         this.addGenericBodyField(variableBody, "核心变量", mainVars);
         this.addGenericBodyField(variableBody, "控制变量 Controls（可多选）", this.listPane(this.regressControls));
         variableCard.add(variableBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(variableCard, c);

         JPanel inferenceCard = this.xtregWizardCardV130(2, "推断设置", "先选择标准误方式；只有选择 Cluster 时才需要聚类变量。");
         JPanel inferenceBody = this.genericCardBody();
         this.addGenericBodyField(inferenceBody, "标准误", this.vce);
         this.regressClusterFieldBlock = (JPanel)this.fieldBlock("聚类变量（仅 Cluster 时需要）", this.cluster);
         this.regressClusterFieldBlock.setAlignmentX(0.0F);
         this.regressClusterFieldBlock.setMaximumSize(new Dimension(Integer.MAX_VALUE, Math.max(54, this.regressClusterFieldBlock.getPreferredSize().height)));
         inferenceBody.add(this.regressClusterFieldBlock);
         inferenceBody.add(Box.createVerticalStrut(10));
         inferenceCard.add(inferenceBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(inferenceCard, c);

         JPanel moreCard = this.xtregWizardCardV130(3, "检查运行与更多设置", "样本条件、分类/交互/滞后项、权重和报告选项集中在这里；默认收起。");
         JPanel moreBody = this.genericCardBody();
         JPanel moreSettings = this.buildRegressMoreSettings();
         JToggleButton moreToggle = new JToggleButton("展开样本与更多设置  +");
         styleSecondaryButton(moreToggle);
         moreSettings.setVisible(false);
         moreToggle.setAlignmentX(0.0F);
         moreSettings.setAlignmentX(0.0F);
         moreToggle.addActionListener(event -> {
            boolean expanded = moreToggle.isSelected();
            moreToggle.setText(expanded ? "收起样本与更多设置  −" : "展开样本与更多设置  +");
            moreSettings.setVisible(expanded);
            this.formPanel.revalidate();
            this.formPanel.repaint();
         });
         moreBody.add(moreToggle);
         moreBody.add(Box.createVerticalStrut(8));
         moreBody.add(moreSettings);
         moreCard.add(moreBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(moreCard, c);

         GridBagConstraints filler = this.constraints(0, c.gridy + 1);
         filler.gridwidth = 2;
         filler.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), filler);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.updateRegressConditionalFields();
         this.updateRegressPreview();
         this.statusLabel.setText("普通线性回归：按变量 → 推断 → 检查运行组织；低频设置默认收起。");
      }'''
replace_method("      private void showRegressPage()", new_regress)

new_graph_more = r'''      private JPanel buildSpecialGraphMoreSettings(boolean includeIf, String optionLabel) {
         JPanel block = new JPanel();
         block.setOpaque(false);
         block.setLayout(new BoxLayout(block, BoxLayout.Y_AXIS));

         JPanel content = new JPanel();
         content.setOpaque(false);
         content.setLayout(new BoxLayout(content, BoxLayout.Y_AXIS));
         if (includeIf) {
            content.add(this.labeledInline("样本条件 if", this.ifCondition));
            content.add(Box.createVerticalStrut(8));
         }
         content.add(this.labeledInline(optionLabel, this.options));
         content.setVisible(false);

         JToggleButton toggle = new JToggleButton(includeIf ? "展开样本与图形设置  +" : "展开图形设置  +");
         styleSecondaryButton(toggle);
         toggle.setAlignmentX(0.0F);
         content.setAlignmentX(0.0F);
         toggle.addActionListener(event -> {
            boolean expanded = toggle.isSelected();
            if (includeIf) {
               toggle.setText(expanded ? "收起样本与图形设置  −" : "展开样本与图形设置  +");
            } else {
               toggle.setText(expanded ? "收起图形设置  −" : "展开图形设置  +");
            }
            content.setVisible(expanded);
            this.formPanel.revalidate();
            this.formPanel.repaint();
         });
         block.add(toggle);
         block.add(Box.createVerticalStrut(7));
         block.add(content);
         return block;
      }'''
replace_method("      private void addSpecialGraphAdvancedSettings(", new_graph_more)

new_graph = r'''      private void showSpecialGraphPage(String var1) {
         this.showWorkspacePage();
         this.selectResultView("graph", true);
         this.currentCommand = var1;
         this.commandDock.setVisible(true);
         this.commandTabs.setVisible(true);
         this.commandTabs.setSelectedIndex(0);
         this.previewArea.setEditable(true);
         this.runButton.setText("绘制图形");
         this.runButton.setEnabled(true);
         this.setWorkspaceBreadcrumb(commandPath(var1));
         this.depvar.setSelectedItem(null);
         this.panel.setSelectedItem(null);
         this.time.setSelectedItem(null);
         this.variables.clearSelection();
         this.ifCondition.setText("");
         this.options.setText("");
         this.expression.setText("twoway".equals(var1) ? "(scatter y x) (lfit y x)" : "");

         String coreTitle;
         String coreSubtitle;
         String optionLabel = "其他图形选项";
         boolean includeIf = !"twoway".equals(var1);
         if (Arrays.asList("histogram", "kdensity").contains(var1)) {
            this.commandTitle.setText(var1 + ("histogram".equals(var1) ? " · 直方图" : " · 核密度图"));
            this.exampleLabel.setText("<html><b>最简单例子：</b> " + var1 + " y</html>");
            this.insightArea.setText("主要意图：观察单个数值变量的分布形状、偏态和尾部。\n\n推荐数据：连续或有序数值变量。右侧预览用于快速检查分布，正式图形仍由 Stata 绘制。\n\n分箱或带宽会影响视觉结果，图形主要用于描述与诊断。");
            this.syntaxArea.setText(var1 + " varname [if] [, options]");
            coreTitle = "分布变量";
            coreSubtitle = "选择一个要观察的数值变量；样本筛选和图形细节放在下一步。";
         } else if (Arrays.asList("scatter", "lfit").contains(var1)) {
            this.commandTitle.setText(var1 + ("scatter".equals(var1) ? " · 散点图" : " · 线性拟合图"));
            this.exampleLabel.setText("<html><b>最简单例子：</b> twoway " + var1 + " y x</html>");
            this.insightArea.setText("主要意图：观察 Y 与 X 的原始关系" + ("lfit".equals(var1) ? "和线性拟合方向。" : "、离群点与可能的非线性。") + "\n\n至少需要两个数值变量。右侧预览会随 Y/X 选择更新。\n\n图中关系用于探索与诊断，因果解释仍取决于研究设计。");
            this.syntaxArea.setText("twoway " + var1 + " y x [if] [, options]");
            coreTitle = "坐标变量";
            coreSubtitle = "先指定纵轴 Y 和唯一的横轴 X；右侧同步显示关系预览。";
         } else if ("graph_box".equals(var1)) {
            this.commandTitle.setText("graph box · 分布与异常值箱线图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> graph box y, over(group)</html>");
            this.insightArea.setText("主要意图：观察变量分布、中位数、四分位距和潜在异常值。\n\n结果变量必填，分组变量可选。分组样本过少时箱线图可能不稳定。\n\n右侧先做分布预览，正式箱线图由 Stata Graph 窗口输出。");
            this.syntaxArea.setText("graph box y [, over(group) options]");
            coreTitle = "分布与分组";
            coreSubtitle = "选择结果变量；需要组间比较时再选择分组变量。";
         } else if ("did_trends".equals(var1)) {
            this.commandTitle.setText("处理组 / 对照组趋势图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> hxtrendplot y, group(treat) time(year)</html>");
            this.insightArea.setText("主要意图：比较处理组与对照组在政策前后的平均结果走势。\n\n需要结果变量、时间变量和处理组变量。右侧趋势预览用于检查分组和时间方向。\n\n趋势图属于 DID 诊断；正式识别仍需明确处理时点、基准期和识别假设。");
            this.syntaxArea.setText("hxtrendplot y [if], group(treat) time(year) [policy(#) options()]");
            coreTitle = "趋势变量";
            coreSubtitle = "一次填好结果 Y、处理组和时间变量；处理组通常使用 0/1 编码。";
            optionLabel = "政策时点或其他选项";
         } else {
            this.commandTitle.setText("twoway · 自定义叠加图");
            this.exampleLabel.setText("<html><b>最简单例子：</b> twoway (scatter y x) (lfit y x)</html>");
            this.insightArea.setText("主要意图：自由组合散点、拟合线、置信区间和其他二维图层。\n\n图层主体直接采用 Stata twoway 语法，适合已经明确所需图层的用户。\n\n页面保留真实表达式，便于复制到 do-file 继续精修。");
            this.syntaxArea.setText("twoway (plottype ...) (plottype ...) [, options]");
            if (this.expression.getText().isBlank()) this.expression.setText("(scatter y x) (lfit y x)");
            coreTitle = "图层表达式";
            coreSubtitle = "填写一个或多个 twoway 图层；可从默认散点 + 拟合线示例直接修改。";
         }

         this.enableVariableDrop(this.depvar, "Y / 分布变量");
         this.enableVariableDrop(this.variables, "横轴 X");
         this.enableVariableDrop(this.panel, "分组 / 处理组变量");
         this.enableVariableDrop(this.time, "时间变量");

         this.formPanel.removeAll();
         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.genericStepStripV152(false, coreTitle, ""), c);

         JPanel coreCard = this.xtregWizardCardV130(1, coreTitle, coreSubtitle);
         JPanel coreBody = this.genericCardBody();
         if (Arrays.asList("histogram", "kdensity").contains(var1)) {
            this.addGenericBodyField(coreBody, "要观察的变量", this.depvar);
         } else if (Arrays.asList("scatter", "lfit").contains(var1)) {
            JPanel xy = new JPanel(new GridLayout(1, 2, 12, 0));
            xy.setOpaque(false);
            xy.add(this.fieldBlock("纵轴变量 Y", this.depvar));
            xy.add(this.fieldBlock("横轴变量 X（选择一个）", this.listPane(this.variables)));
            this.addGenericBodyField(coreBody, "Y / X", xy);
         } else if ("graph_box".equals(var1)) {
            JPanel boxVars = new JPanel(new GridLayout(1, 2, 12, 0));
            boxVars.setOpaque(false);
            boxVars.add(this.fieldBlock("要观察的变量", this.depvar));
            boxVars.add(this.fieldBlock("分组变量（可选）", this.panel));
            this.addGenericBodyField(coreBody, "变量", boxVars);
         } else if ("did_trends".equals(var1)) {
            JPanel trendVars = new JPanel(new GridLayout(1, 3, 10, 0));
            trendVars.setOpaque(false);
            trendVars.add(this.fieldBlock("结果变量 Y", this.depvar));
            trendVars.add(this.fieldBlock("处理组变量（建议 0/1）", this.panel));
            trendVars.add(this.fieldBlock("时间变量", this.time));
            this.addGenericBodyField(coreBody, "趋势设定", trendVars);
            JLabel trendHint = new JLabel("处理组与时间变量决定右侧趋势预览的分组与横轴；正式图形由 hxtrendplot 执行。");
            trendHint.setForeground(MUTED);
            trendHint.setFont(trendHint.getFont().deriveFont(9.8F));
            trendHint.setAlignmentX(0.0F);
            coreBody.add(trendHint);
         } else {
            this.addGenericBodyField(coreBody, "图层表达式", this.expression);
         }
         coreCard.add(coreBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(coreCard, c);

         String checkTitle = includeIf ? "样本与图形设置" : "图形设置与检查";
         String checkSubtitle = includeIf
            ? "样本条件和 Stata 原生图形 options 默认收起；底部实时命令用于运行前核对。"
            : "Stata 原生图形 options 默认收起；底部实时命令用于运行前核对。";
         JPanel checkCard = this.xtregWizardCardV130(2, checkTitle, checkSubtitle);
         JPanel checkBody = this.genericCardBody();
         JPanel graphMore = this.buildSpecialGraphMoreSettings(includeIf, optionLabel);
         graphMore.setAlignmentX(0.0F);
         checkBody.add(graphMore);
         checkCard.add(checkBody, BorderLayout.CENTER);
         c.gridy++;
         this.formPanel.add(checkCard, c);

         GridBagConstraints filler = this.constraints(0, c.gridy + 1);
         filler.gridwidth = 2;
         filler.weighty = 1.0;
         this.formPanel.add(Box.createVerticalGlue(), filler);
         this.formPanel.revalidate();
         this.formPanel.repaint();
         this.formScroll.getVerticalScrollBar().setValue(0);
         this.updateSpecialGraphPreview();
         this.statusLabel.setText("图形页面按变量设定 → 检查运行组织；右侧图形预览会随变量选择更新。");
      }'''
replace_method("      private void showSpecialGraphPage(", new_graph)

# Add validation for the two special graph cases that previously had no explicit completeness check.
needle = '         if (Arrays.asList("scatter", "lfit").contains(command)) {'
pos = text.index(needle)
brace = text.index('{', pos)
depth = 0
end = None
for i in range(brace, len(text)):
    if text[i] == '{': depth += 1
    elif text[i] == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
if end is None:
    raise SystemExit("cannot find scatter validation block")
insert = r'''
         if ("did_trends".equals(command)) {
            if (selected(this.depvar).isBlank() || selected(this.panel).isBlank() || selected(this.time).isBlank()) {
               JOptionPane.showMessageDialog(this, "请选择结果变量、处理组变量和时间变量。", "趋势图设置尚未完整", JOptionPane.INFORMATION_MESSAGE);
               return false;
            }
         }
         if ("twoway".equals(command) && this.expression.getText().trim().isBlank()) {
            JOptionPane.showMessageDialog(this, "请填写至少一个 twoway 图层表达式。", "图层表达式为空", JOptionPane.INFORMATION_MESSAGE);
            return false;
         }
'''
if '"趋势图设置尚未完整"' not in text:
    text = text[:end] + insert + text[end:]

path.write_text(text, encoding="utf-8")
print("HX_UI_REGRESS_GRAPH_PASS5_OK")
