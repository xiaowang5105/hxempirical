from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/main/java/com/hexie/stata/HxWorkbench.java"
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    text = text.replace(old, new, 1)


# Make the step strip use the actual task names shown by the page.
start = text.index("      private JComponent genericStepStripV151(boolean hasMethodSettings) {")
end = text.index("      private static boolean isCoreModelCommand", start)
new_strip = r'''      private JComponent genericStepStripV152(boolean hasMethodSettings, String coreStepTitle, String methodStepTitle) {
         JPanel strip = cardPanel();
         strip.setBackground(SURFACE);
         strip.setBorder(BorderFactory.createCompoundBorder(
            new HxWorkbench.WorkbenchFrame.RoundedBorder(new Color(218, 225, 236), 11),
            new EmptyBorder(9, 10, 9, 10)
         ));
         String[][] steps = hasMethodSettings
            ? new String[][]{
               {"1", coreStepTitle, "先完成当前任务最关键的变量、文件或表达式"},
               {"2", methodStepTitle, "再设置当前命令真正支持的方法、固定效应或推断选项"},
               {"3", "检查运行", "最后检查样本范围、低频设置和真实 Stata 命令"}
            }
            : new String[][]{
               {"1", coreStepTitle, "先完成当前任务最关键的变量、文件或表达式"},
               {"2", "检查运行", "最后检查样本范围、低频设置和真实 Stata 命令"}
            };
         strip.setLayout(new GridLayout(1, steps.length, 8, 0));
         for (int i = 0; i < steps.length; i++) {
            JPanel p = new JPanel(new BorderLayout(6, 0));
            p.setOpaque(false);
            p.setMinimumSize(new Dimension(0, 0));
            JComponent n = this.xtregCircleBadge(steps[i][0], i == 0, 24);
            p.add(n, BorderLayout.WEST);
            JLabel label = new JLabel("<html><b>" + html(steps[i][1]) + "</b></html>");
            label.setForeground(TEXT);
            label.setFont(label.getFont().deriveFont(10.5F));
            label.setToolTipText(steps[i][2]);
            label.setMinimumSize(new Dimension(0, 0));
            p.add(label, BorderLayout.CENTER);
            strip.add(p);
         }
         strip.setPreferredSize(new Dimension(0, 52));
         strip.setMinimumSize(new Dimension(0, 52));
         strip.setMaximumSize(new Dimension(Integer.MAX_VALUE, 52));
         return strip;
      }

      private static String genericCoreTitle(String command) {
         if ("generate".equals(command)) return "生成规则";
         if ("replace".equals(command)) return "修改规则";
         if (Arrays.asList("keep", "drop").contains(command)) return "处理对象";
         if ("merge".equals(command)) return "合并设置";
         if ("append".equals(command)) return "追加设置";
         if ("reshape".equals(command)) return "转换设置";
         if ("collapse".equals(command)) return "汇总设置";
         if (Arrays.asList("xtset", "tsset").contains(command)) return "数据结构";
         if (Arrays.asList("encode", "decode", "destring", "tostring").contains(command)) return "转换设置";
         if ("winsor2".equals(command)) return "缩尾设置";
         if (Arrays.asList("duplicates", "misstable").contains(command)) return "检查范围";
         if (Arrays.asList("summarize", "tabstat", "correlate", "pwcorr", "tabulate").contains(command)) return "分析变量";
         if ("ttest".equals(command)) return "检验设置";
         if (Arrays.asList("ivregress", "ivreghdfe").contains(command)) return "方程设定";
         if (Arrays.asList("didregress", "xtdidregress").contains(command)) return "DID 设定";
         if (Arrays.asList("test", "lincom", "margins").contains(command)) return "后估计设置";
         if ("predict".equals(command)) return "生成设置";
         if (Arrays.asList("histogram", "kdensity").contains(command)) return "分布设置";
         if (Arrays.asList("scatter", "lfit").contains(command)) return "坐标变量";
         if (Arrays.asList("event_plot", "marginsplot", "coefplot").contains(command)) return "图形设置";
         if (isGenericPanelEstimator(command)) return "变量与面板";
         if (Arrays.asList(
            "areg", "reghdfe", "qreg", "rreg", "cnsreg", "vwls", "eivreg", "newey", "prais",
            "logit", "probit", "poisson", "nbreg", "ppmlhdfe"
         ).contains(command)) return "变量设定";
         return "核心设置";
      }

      private static String genericCoreSubtitle(String command) {
         if ("generate".equals(command)) return "填写新变量名和计算公式；需要限定样本时在最后一步补充 if。";
         if ("replace".equals(command)) return "选择已有变量并填写新值或公式；样本条件默认直接展开。";
         if (Arrays.asList("keep", "drop").contains(command)) return "先选择处理变量还是处理样本，再填写对应范围；样本条件默认直接展开。";
         if ("merge".equals(command)) return "先选择合并关系，再指定关联变量和副表文件；运行前检查键的唯一性。";
         if ("append".equals(command)) return "选择要追加的 using 数据文件；当前内存数据作为第一张表保留在上方。";
         if ("reshape".equals(command)) return "先选择宽转长或长转宽，再填写 stub、i() 和 j()。";
         if ("collapse".equals(command)) return "先选择统计量，再选择汇总变量和 by() 分组变量。";
         if (Arrays.asList("xtset", "tsset").contains(command)) return "指定个体与时间维度，让后续面板或时间序列命令使用明确的数据结构。";
         if (Arrays.asList("encode", "decode", "destring", "tostring").contains(command)) return "选择原变量、输出方式与目标变量；低频格式选项集中在最后一步。";
         if ("winsor2".equals(command)) return "先选择覆盖原变量或创建新变量，再设置变量和缩尾分位点。";
         if (Arrays.asList("duplicates", "misstable").contains(command)) return "选择需要检查的变量；留空时按 Stata 当前命令的默认范围执行。";
         if (Arrays.asList("summarize", "tabstat", "correlate", "pwcorr", "tabulate").contains(command)) return "选择要分析的变量；统计细节和显示选项集中在最后一步。";
         if ("ttest".equals(command)) return "先选择单样本、分组比较或配对比较，再填写变量与比较对象。";
         if (Arrays.asList("ivregress", "ivreghdfe").contains(command)) return "先区分因变量、正常解释变量、内生变量和工具变量，再设置估计方法。";
         if (Arrays.asList("didregress", "xtdidregress").contains(command)) return "填写结果变量、协变量、处理变量、group() 和 time()，再设置推断方式。";
         if (Arrays.asList("test", "lincom", "margins").contains(command)) return "基于上一项估计结果填写检验、线性组合或边际效应表达式。";
         if ("predict".equals(command)) return "先选择生成预测值、残差或标准化残差，再填写新变量名。";
         if (Arrays.asList("histogram", "kdensity").contains(command)) return "选择要查看分布的变量；样本筛选、权重和图形 options 放在最后一步。";
         if (Arrays.asList("scatter", "lfit").contains(command)) return "指定纵轴 Y 和横轴 X；图形细节与样本筛选放在最后一步。";
         if (Arrays.asList("event_plot", "marginsplot", "coefplot").contains(command)) return "指定结果对象或命令主体，再在最后一步补充图形 options。";
         if (isGenericPanelEstimator(command)) return "先选择因变量、解释变量以及面板结构，再设置模型和推断选项。";
         return "先完成当前任务最关键的变量、文件或表达式；变量可从右侧变量窗口或数据表表头直接拖入。";
      }

'''
text = text[:start] + new_strip + text[end:]

# destring/tostring's save mode is also a core task choice.
replace_once(
'''            "keep", "drop", "merge", "reshape", "collapse", "ttest", "predict", "winsor2"
''',
'''            "keep", "drop", "merge", "reshape", "collapse", "ttest", "predict", "winsor2", "destring", "tostring"
''',
"core model command list",
)

# Replace the inline title chain with the full command-family mapping, and make the step strip mirror it.
old = '''         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.genericStepStripV151(hasMethodSettings), c);

         String coreTitle = "核心设置";
         String coreSubtitle = "先完成当前任务最关键的变量、文件或表达式；变量可从右侧变量窗口或数据表表头直接拖入。";
         if (Arrays.asList("keep", "drop").contains(this.currentCommand)) {
            coreTitle = "处理对象";
            coreSubtitle = "先选择处理变量还是处理样本，再填写对应范围；样本条件默认直接展开。";
         } else if ("merge".equals(this.currentCommand)) {
            coreTitle = "合并设置";
            coreSubtitle = "先选择合并关系，再指定关联变量和副表文件；运行前检查键是否满足唯一性要求。";
         } else if ("reshape".equals(this.currentCommand)) {
            coreTitle = "转换设置";
            coreSubtitle = "先选择宽转长或长转宽，再填写 stub、i() 和 j()。";
         } else if ("collapse".equals(this.currentCommand)) {
            coreTitle = "汇总设置";
            coreSubtitle = "先选择统计量，再选择汇总变量和 by() 分组变量。";
         } else if ("ttest".equals(this.currentCommand)) {
            coreTitle = "检验设置";
            coreSubtitle = "先选择单样本、分组比较或配对比较，再填写变量与比较对象。";
         } else if ("predict".equals(this.currentCommand)) {
            coreTitle = "生成设置";
            coreSubtitle = "先选择生成预测值、残差或标准化残差，再填写新变量名。";
         } else if ("winsor2".equals(this.currentCommand)) {
            coreTitle = "缩尾设置";
            coreSubtitle = "先选择覆盖原变量或创建新变量，再设置变量和缩尾分位点。";
         }
'''
new = '''         String coreTitle = genericCoreTitle(this.currentCommand);
         String coreSubtitle = genericCoreSubtitle(this.currentCommand);
         String methodTitle;
         if (Arrays.asList("ivregress", "ivreghdfe").contains(this.currentCommand)) {
            methodTitle = "估计方法";
         } else if ((this.flag("has_absorb") && !absorbIsCore) && (this.flag("has_vce") || this.flag("has_cluster"))) {
            methodTitle = "固定效应与推断";
         } else if (this.flag("has_vce") || this.flag("has_cluster")) {
            methodTitle = (this.model.getItemCount() > 0 && !modelIsCore) ? "估计与推断" : "推断设置";
         } else {
            methodTitle = "方法与设置";
         }

         GridBagConstraints c = new GridBagConstraints();
         c.gridx = 0;
         c.gridy = 0;
         c.weightx = 1.0;
         c.fill = GridBagConstraints.HORIZONTAL;
         c.insets = new Insets(0, 0, 10, 0);
         this.formPanel.add(this.genericStepStripV152(hasMethodSettings, coreTitle, methodTitle), c);
'''
replace_once(old, new, "dynamic task titles")

# Make the method card title match what the step strip says.
replace_once(
'''            JPanel methodCard = this.xtregWizardCardV130(2, "方法与设置", "当前任务支持的方法、模型、固定效应与标准误集中在这里。只显示实际可用的项目。");
''',
'''            JPanel methodCard = this.xtregWizardCardV130(2, methodTitle, "当前任务支持的方法、模型、固定效应与标准误集中在这里；只显示实际可用的项目。");
''',
"dynamic method title",
)

# Use a more specific final-card title when sample selection is actually present.
replace_once(
'''         JPanel advancedCard = this.xtregWizardCardV130(advancedStep, "检查与更多设置", advancedSubtitle);
''',
'''         String advancedTitle = (this.flag("has_if") || this.flag("has_in") || this.flag("has_weight"))
            ? "样本与更多设置" : "检查与更多设置";
         JPanel advancedCard = this.xtregWizardCardV130(advancedStep, advancedTitle, advancedSubtitle);
''',
"advanced title",
)

path.write_text(text, encoding="utf-8")
print("HX_UI_PAGE_PASS3_OK")
