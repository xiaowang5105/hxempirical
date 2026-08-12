from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: {label}: expected 1 match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# 1. Semantic defaults and estimator roles.
sem = Path("hxsemantics.ado")
replace_once(
    sem,
    "*! hxsemantics 1.3.1  12aug2026",
    "*! hxsemantics 1.3.2  12aug2026",
    "semantics version",
)
replace_once(
    sem,
    '    local model_label "方法 / 模型"\n    local absorb_label "固定效应 absorb()"',
    '    local model_label "方法 / 模型"\n    local default_model ""\n    local absorb_label "固定效应 absorb()"',
    "default model initializer",
)
replace_once(
    sem,
    '                local models "固定效应（FE） 随机效应（RE） 组间效应（Between）"\n                local example1 "xtset firm year"',
    '                local models "固定效应（FE） 随机效应（RE） 组间效应（Between）"\n                local default_model "随机效应（RE）"\n                local example1 "xtset firm year"',
    "xtreg default model",
)
replace_once(
    sem,
    '                local models "固定效应（FE） 随机效应（RE） 总体平均（PA）"\n                local example1 "xtset firm year"',
    '                local models "固定效应（FE） 随机效应（RE） 总体平均（PA）"\n                local default_model "随机效应（RE）"\n                local example1 "xtset firm year"',
    "xtlogit default model",
)
replace_once(
    sem,
    '                local models "随机效应（RE） 总体平均（PA）"\n                local example1 "xtset firm year"',
    '                local models "随机效应（RE） 总体平均（PA）"\n                local default_model "随机效应（RE）"\n                local example1 "xtset firm year"',
    "xtprobit default model",
)
replace_once(
    sem,
    '    local default_model : word 1 of `models\'\n    if `"`vces\'"\' == "" local vces "default"',
    '    if `"`default_model\'"\' == "" local default_model : word 1 of `models\'\n    if `"`vces\'"\' == "" local vces "default"',
    "default model fallback",
)

# 2. Minimum contracts for HDFE estimators when local third-party help is unavailable.
resolve = Path("hxresolve.ado")
replace_once(
    resolve,
    "*! hxresolve 3.1.1  12aug2026",
    "*! hxresolve 3.1.2  12aug2026",
    "resolver version",
)
replace_once(
    resolve,
    '''    if inlist("`cmd'", "reghdfe", "ppmlhdfe", "ivreghdfe") {
        local has_absorb 1
        local has_vce 1
        local has_cluster 1
        if `"`vces'"' == "" | `"`vces'"' == "default" {
            local vces "default robust cluster"
        }
    }''',
    '''    if inlist("`cmd'", "reghdfe", "ppmlhdfe", "ivreghdfe") {
        local has_depvar 1
        local has_varlist 1
        local has_if 1
        local has_in 1
        local has_weight 1
        local has_absorb 1
        local has_vce 1
        local has_cluster 1
        if `"`vces'"' == "" | `"`vces'"' == "default" {
            local vces "default robust cluster"
        }
    }''',
    "HDFE minimum contract",
)

# 3. Java common-first layout, command-specific weight types, and focused validation.
java = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
replace_once(
    java,
    '''         for (String var2 : HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_schema_models"))) {
            this.model.addItem(var2);
         }

         this.vce.removeAllItems();''',
    '''         for (String var2 : HxWorkbench.StataBridge.words(HxWorkbench.StataBridge.characteristic("hxtoolbox_schema_models"))) {
            this.model.addItem(var2);
         }

         String var3 = visibleText(HxWorkbench.StataBridge.characteristic("hxtoolbox_schema_default_model"));
         if (!var3.isBlank() && comboContains(this.model, var3)) {
            this.model.setSelectedItem(var3);
         }

         this.vce.removeAllItems();''',
    "apply semantic default model",
)
replace_once(
    java,
    '''         if (this.model.getItemCount() > 0) {
            this.addField(var4++, this.sem("model_label"), this.model);
         }

         if (this.flag("has_using")) {
            this.usingLabel.setText(this.sem("using_label"));
            this.addField(var4++, this.usingLabel.getText(), this.usingChooser());
         }

         if (this.flag("needs_panel")) {
            this.addField(var4++, "个体 / 面板变量", this.panel);
            this.addField(var4++, "时间变量", this.time);
         }

         if (this.flag("has_absorb")) {
            this.addField(var4++, this.sem("absorb_label"), this.listPane(this.absorb));
         }

         if (this.flag("has_iv")) {
            this.addField(var4++, this.sem("endog_label"), this.listPane(this.endog));
            this.addField(var4++, this.sem("inst_label"), this.listPane(this.instruments));
         }''',
    '''         if (this.flag("has_iv")) {
            this.addField(var4++, this.sem("endog_label"), this.listPane(this.endog));
            this.addField(var4++, this.sem("inst_label"), this.listPane(this.instruments));
         }

         if (this.model.getItemCount() > 0) {
            this.addField(var4++, this.sem("model_label"), this.model);
         }

         if (this.flag("has_using")) {
            this.usingLabel.setText(this.sem("using_label"));
            this.addField(var4++, this.usingLabel.getText(), this.usingChooser());
         }

         if (this.flag("needs_panel")) {
            this.addField(var4++, "个体 / 面板变量", this.panel);
            this.addField(var4++, "时间变量", this.time);
         }

         if (this.flag("has_absorb")) {
            this.addField(var4++, this.sem("absorb_label"), this.listPane(this.absorb));
         }''',
    "IV fields before model and absorb",
)
replace_once(
    java,
    '''      private void rebuildGenericAdvancedContent(boolean var1, boolean var2, boolean var3) {
         this.advancedContent.removeAll();
         this.genericWeightVarFieldBlock = null;
         if (var1) {''',
    '''      private void rebuildGenericAdvancedContent(boolean var1, boolean var2, boolean var3) {
         this.advancedContent.removeAll();
         this.genericWeightVarFieldBlock = null;
         if (var3) {
            this.configureGenericWeightTypes();
         }
         if (var1) {''',
    "configure command weight types",
)
replace_once(
    java,
    '''      private void updateGenericWeightConditionalFields() {
         boolean var1 = !"无".equals(selected(this.genericWeightType));
         this.genericWeightVar.setEnabled(var1);
         if (!var1) {
            this.genericWeightVar.setSelectedItem(null);
         }
      }''',
    '''      private void configureGenericWeightTypes() {
         String var1 = selected(this.genericWeightType);
         List<String> var2;
         if ("ppmlhdfe".equals(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "pweight");
         } else if ("reghdfe".equals(this.currentCommand)) {
            var2 = Arrays.asList("无", "fweight", "aweight", "pweight");
         } else {
            var2 = Arrays.asList("无", "fweight", "aweight", "pweight", "iweight");
         }

         this.genericWeightType.removeAllItems();
         for (String var4 : var2) {
            this.genericWeightType.addItem(var4);
         }

         this.genericWeightType.setSelectedItem(var2.contains(var1) ? var1 : "无");
      }

      private void updateGenericWeightConditionalFields() {
         boolean var1 = !"无".equals(selected(this.genericWeightType));
         this.genericWeightVar.setEnabled(var1);
         if (!var1) {
            this.genericWeightVar.setSelectedItem(null);
         }
      }''',
    "generic weight type helper",
)
replace_once(
    java,
    '''         } else if (!"did_builder".equals(this.currentCommand) || this.validateDidBeforeRun()) {
            if (!"regress".equals(this.currentCommand) || !this.regressWorkspaceActive || this.validateRegressBeforeRun()) {
               String var1 = this.previewArea.getText().trim();''',
    '''         } else if (!"did_builder".equals(this.currentCommand) || this.validateDidBeforeRun()) {
            if (this.validateFocusedEstimationBeforeRun()
               && (!"regress".equals(this.currentCommand) || !this.regressWorkspaceActive || this.validateRegressBeforeRun())) {
               String var1 = this.previewArea.getText().trim();''',
    "focused pre-run validation call",
)
replace_once(
    java,
    '''      private boolean validateDidBeforeRun() {
         String var1 = selected(this.didAction);''',
    '''      private boolean validateFocusedEstimationBeforeRun() {
         if (!Arrays.asList("reghdfe", "ppmlhdfe", "ivregress", "ivreghdfe", "xtreg").contains(this.currentCommand)) {
            return true;
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

         if (!"无".equals(selected(this.genericWeightType)) && selected(this.genericWeightVar).isBlank()) {
            JOptionPane.showMessageDialog(this, "选择权重类型后，请指定权重变量。", "权重变量缺失", 1);
            return false;
         }

         return true;
      }

      private boolean validateDidBeforeRun() {
         String var1 = selected(this.didAction);''',
    "focused estimator validator",
)

# 4. README cumulative record.
readme = Path("README.md")
replace_once(
    readme,
    "上次修改时间：**2026-08-12 14:20（UTC+8）**",
    "上次修改时间：**2026-08-12 14:28（UTC+8）**",
    "README modified time",
)
marker = "### 2026-08-12 14:20（UTC+8）\n"
text = readme.read_text(encoding="utf-8")
if text.count(marker) != 1:
    raise SystemExit(f"README changelog marker expected once, found {text.count(marker)}")
entry = '''### 2026-08-12 14:28（UTC+8）

**修改时间**：2026-08-12 14:28（UTC+8）

**修改内容**：

- 继续清理 `reghdfe`、`ppmlhdfe`、`ivregress`、`ivreghdfe`、`xtreg` 这组常用估计命令的普通命令页，统一“核心模型参数 → 标准误 → 更多设置”的层级。
- IV 页面把内生变量与工具变量提升到主要参数区；`ivregress` 的估计方法紧随核心变量设置，`ivreghdfe` 的固定效应与 VCE 继续保留在主页面。
- 面板命令开始使用显式语义默认值：`xtreg`、`xtlogit`、`xtprobit` 默认选择随机效应（RE），同时仍可在页面切换其他可用模型。
- 未安装 `reghdfe`、`ppmlhdfe`、`ivreghdfe` 时，最低命令契约仍保留因变量、解释变量、`if/in`、权重、`absorb()`、VCE 和 Cluster 等原生命令入口。
- 权重类型按命令收窄：`reghdfe` 提供 `fweight/aweight/pweight`，`ppmlhdfe` 提供 `fweight/pweight`，`ivreghdfe` 保留四类权重；避免界面生成命令本身不接受的权重类型。
- 对这组重点估计命令增加运行前结构检查：IV 角色重复或缺失、Cluster 变量缺失、权重变量缺失时先提示，不提交明显不完整的命令。
- `hxsemantics` 更新到 1.3.2，`hxresolve` 更新到 3.1.2；Java 工作台与 `hxworkbench.jar` 同步重建并通过编译和离线界面 smoke test。

'''
readme.write_text(text.replace(marker, entry + marker, 1), encoding="utf-8")

print("FOCUSED_ESTIMATOR_REFACTOR_OK")
