from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/main/java/com/hexie/stata/HxWorkbench.java"
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    text = text.replace(old, new, 1)


# 1) Commands whose model/mode choice is part of the core task, not a secondary estimator setting.
marker = '''      private static boolean isGenericPanelEstimator(String command) {
'''
helper = '''      private static boolean isCoreModelCommand(String command) {
         return Arrays.asList(
            "keep", "drop", "merge", "reshape", "collapse", "ttest", "predict", "winsor2"
         ).contains(command);
      }

'''
if helper.strip() not in text:
    i = text.index(marker)
    text = text[:i] + helper + text[i:]

# 2) Split core choices / grouping roles from true method settings.
replace_once(
'''         boolean hasMethodSettings = this.model.getItemCount() > 0
            || this.flag("has_absorb") || this.flag("has_vce") || this.flag("has_cluster");
''',
'''         boolean modelIsCore = this.model.getItemCount() > 0 && isCoreModelCommand(this.currentCommand);
         boolean absorbIsCore = this.flag("has_absorb")
            && Arrays.asList("collapse", "didregress", "xtdidregress").contains(this.currentCommand);
         boolean hasMethodSettings = (this.model.getItemCount() > 0 && !modelIsCore)
            || (this.flag("has_absorb") && !absorbIsCore) || this.flag("has_vce") || this.flag("has_cluster");
''',
"split core and method settings",
)

# 3) Give task-heavy pages specific card titles instead of generic econometrics wording.
replace_once(
'''         JPanel coreCard = this.xtregWizardCardV130(1, "核心设置", "先完成当前任务最关键的变量、文件或表达式；变量可从右侧变量窗口或数据表表头直接拖入。");
         JPanel coreBody = this.genericCardBody();
         boolean hasCore = false;
''',
'''         String coreTitle = "核心设置";
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
         JPanel coreCard = this.xtregWizardCardV130(1, coreTitle, coreSubtitle);
         JPanel coreBody = this.genericCardBody();
         boolean hasCore = false;

         if (modelIsCore) {
            this.addGenericBodyField(coreBody, this.sem("model_label"), this.model);
            hasCore = true;
         }
''',
"task-specific core titles",
)

# 4) Grouping is a core data-role for collapse and DID, not a method card item.
panel_block = '''         if (showPanelStructure) {
            JPanel panelGrid = new JPanel(new GridLayout(1, 2, 12, 0));
            panelGrid.setOpaque(false);
            panelGrid.add(this.fieldBlock(this.sem("panel_label"), this.panel));
            panelGrid.add(this.fieldBlock(this.sem("time_label"), this.time));
            String panelGroupTitle = Arrays.asList("didregress", "xtdidregress").contains(this.currentCommand)
               ? "处理与时间设定" : "数据结构";
            this.addGenericBodyField(coreBody, panelGroupTitle, panelGrid);
            if (isGenericPanelEstimator(this.currentCommand)) {
               JLabel setupHint = new JLabel("运行时会先按这里执行 xtset，再运行当前面板模型；时间变量可按数据结构留空。");
               setupHint.setForeground(MUTED);
               setupHint.setFont(setupHint.getFont().deriveFont(9.8F));
               setupHint.setAlignmentX(0.0F);
               coreBody.add(setupHint);
               coreBody.add(Box.createVerticalStrut(4));
            }
            hasCore = true;
         }
'''
replacement_panel = panel_block + '''
         if (absorbIsCore) {
            this.addGenericBodyField(coreBody, this.sem("absorb_label"), this.listPane(this.absorb));
            hasCore = true;
         }

         if (Arrays.asList("keep", "drop", "merge", "append", "reshape", "collapse", "replace").contains(this.currentCommand)) {
            JLabel mutationHint = new JLabel("<html>提示：该操作会改变当前内存中的数据。正式数据建议先保存，再执行并检查结果。</html>");
            mutationHint.setForeground(MUTED);
            mutationHint.setFont(mutationHint.getFont().deriveFont(9.8F));
            mutationHint.setAlignmentX(0.0F);
            coreBody.add(mutationHint);
            coreBody.add(Box.createVerticalStrut(4));
         }
'''
replace_once(panel_block, replacement_panel, "core grouping and mutation hint")

# 5) Do not duplicate core mode choices or core grouping roles in the method card.
replace_once(
'''            if (this.model.getItemCount() > 0) {
               this.addGenericBodyField(methodBody, this.sem("model_label"), this.model);
            }
            if (this.flag("has_absorb")) {
               this.addGenericBodyField(methodBody, this.sem("absorb_label"), this.listPane(this.absorb));
            }
''',
'''            if (this.model.getItemCount() > 0 && !modelIsCore) {
               this.addGenericBodyField(methodBody, this.sem("model_label"), this.model);
            }
            if (this.flag("has_absorb") && !absorbIsCore) {
               this.addGenericBodyField(methodBody, this.sem("absorb_label"), this.listPane(this.absorb));
            }
''',
"avoid duplicated core settings",
)

# 6) replace commonly uses if as a first-class operation, so expose the condition immediately too.
replace_once(
'''         boolean advancedExpandedByDefault = Arrays.asList("keep", "drop").contains(this.currentCommand);
''',
'''         boolean advancedExpandedByDefault = Arrays.asList("keep", "drop", "replace").contains(this.currentCommand);
''',
"expand replace condition",
)

# 7) Keep the status bar accurate after the new task-aware layout.
replace_once(
'''         this.statusLabel.setText(this.currentCommand + "：常用参数已按步骤整理；低频设置默认收起，可从右侧直接拖入变量。");
''',
'''         this.statusLabel.setText(this.currentCommand + "：核心操作已按任务顺序整理；低频设置集中在最后一步，可从右侧直接拖入变量。");
''',
"status copy",
)

path.write_text(text, encoding="utf-8")
print("HX_UI_PAGE_PASS2_OK")
