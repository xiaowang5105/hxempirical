from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)


# 1) Java: dynamic-panel commands that rely on lags need an explicit time variable.
java_path = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
java = java_path.read_text(encoding="utf-8")

old = '''      private static boolean isGenericPanelEstimator(String command) {
         return Arrays.asList(
            "xtlogit", "xtprobit", "xtpoisson", "xtnbreg", "xtgee", "xttobit", "xtcloglog",
            "xtintreg", "xtoprobit", "xtmlogit", "xtfrontier", "xtabond", "xtdpdsys"
         ).contains(command);
      }
'''
new = '''      private static boolean isGenericPanelEstimator(String command) {
         return Arrays.asList(
            "xtlogit", "xtprobit", "xtpoisson", "xtnbreg", "xtgee", "xttobit", "xtcloglog",
            "xtintreg", "xtoprobit", "xtmlogit", "xtfrontier", "xtabond", "xtdpdsys"
         ).contains(command);
      }

      private static boolean isGenericPanelTimeRequired(String command) {
         return Arrays.asList("xtabond", "xtdpdsys").contains(command);
      }
'''
java = replace_once(java, old, new, "add dynamic-panel time helper")

old = '''      private boolean ensureGenericPanelDeclarationBeforeRun() {
         if (!isGenericPanelEstimator(this.currentCommand)) return true;
         String panelVar = selected(this.panel);
         String timeVar = selected(this.time);
         if (panelVar.isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择个体 / 面板变量。", "面板结构尚未完整", JOptionPane.INFORMATION_MESSAGE);
            return false;
         }
         String setup = "xtset " + panelVar + (timeVar.isBlank() ? "" : " " + timeVar);
'''
new = '''      private boolean ensureGenericPanelDeclarationBeforeRun() {
         if (!isGenericPanelEstimator(this.currentCommand)) return true;
         String panelVar = selected(this.panel);
         String timeVar = selected(this.time);
         if (panelVar.isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择个体 / 面板变量。", "面板结构尚未完整", JOptionPane.INFORMATION_MESSAGE);
            return false;
         }
         if (isGenericPanelTimeRequired(this.currentCommand) && timeVar.isBlank()) {
            JOptionPane.showMessageDialog(this, "当前动态面板模型需要时间变量，用于识别滞后期。请同时选择面板变量和时间变量。", "时间变量尚未选择", JOptionPane.INFORMATION_MESSAGE);
            return false;
         }
         String setup = "xtset " + panelVar + (timeVar.isBlank() ? "" : " " + timeVar);
'''
java = replace_once(java, old, new, "enforce dynamic-panel time before xtset")

old = '''            if (isGenericPanelEstimator(this.currentCommand)) {
               JLabel setupHint = new JLabel("运行时会先按这里执行 xtset，再运行当前面板模型；时间变量可按数据结构留空。");
               setupHint.setForeground(MUTED);
'''
new = '''            if (isGenericPanelEstimator(this.currentCommand)) {
               String setupHintText = isGenericPanelTimeRequired(this.currentCommand)
                  ? "运行时会先执行 xtset；当前动态面板模型必须同时指定面板变量和时间变量。"
                  : "运行时会先按这里执行 xtset，再运行当前面板模型；时间变量可按数据结构留空。";
               JLabel setupHint = new JLabel(setupHintText);
               setupHint.setForeground(MUTED);
'''
java = replace_once(java, old, new, "make panel hint command-specific")

old = '''         if (isGenericPanelEstimator(this.currentCommand) && selected(this.panel).isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择个体 / 面板变量；时间变量可按数据结构决定是否填写。", "面板结构尚未完整", 1);
            return false;
         }

         if (Arrays.asList("didregress", "xtdidregress").contains(this.currentCommand)) {
'''
new = '''         if (isGenericPanelEstimator(this.currentCommand) && selected(this.panel).isBlank()) {
            JOptionPane.showMessageDialog(this, "请选择个体 / 面板变量。", "面板结构尚未完整", 1);
            return false;
         }
         if (isGenericPanelTimeRequired(this.currentCommand) && selected(this.time).isBlank()) {
            JOptionPane.showMessageDialog(this, "xtabond / xtdpdsys 需要时间变量来构造动态滞后结构。", "时间变量尚未选择", 1);
            return false;
         }

         if (Arrays.asList("didregress", "xtdidregress").contains(this.currentCommand)) {
'''
java = replace_once(java, old, new, "validate dynamic-panel time")
java_path.write_text(java, encoding="utf-8")


# 2) Registry: the public package supports Stata 17+, while BMA entered Stata in 18.
registry_path = Path("hxregistry.ado")
registry = registry_path.read_text(encoding="utf-8")

stats_line = next(line for line in registry.splitlines() if line.strip().startswith('local stats_cmds "'))
if " bmaregress " not in f" {stats_line} ":
    raise SystemExit("registry stats_cmds does not contain bmaregress")
registry = replace_once(
    registry,
    stats_line + "\n",
    stats_line + "\n    if c(stata_version) < 18 {\n        local stats_cmds : subinstr local stats_cmds \" bmaregress\" \"\", all\n    }\n",
    "gate bmaregress command catalog",
)

methods_line = next(line for line in registry.splitlines() if line.strip().startswith('local stats_methods "'))
if "贝叶斯模型平均" not in methods_line:
    raise SystemExit("registry stats_methods does not contain BMA method")
registry = replace_once(
    registry,
    methods_line + "\n",
    methods_line + "\n    if c(stata_version) < 18 {\n        local stats_methods : subinstr local stats_methods \" 贝叶斯模型平均\" \"\", all\n    }\n",
    "gate BMA method catalog",
)

old = '''    else if inlist(`"`method'"', "贝叶斯模型平均", "bma") local view "bmaregress"
'''
new = '''    else if inlist(`"`method'"', "贝叶斯模型平均", "bma") {
        if c(stata_version) >= 18 local view "bmaregress"
        else local view ""
    }
'''
registry = replace_once(registry, old, new, "gate BMA method navigation")
registry_path.write_text(registry, encoding="utf-8")


# 3) Semantics: clarify dynamic-panel time requirements and preserve precise stcox copy.
sem_path = Path("hxsemantics.ado")
sem = sem_path.read_text(encoding="utf-8")

old = '''        local purpose2 "先选择结果变量和候选预测变量；always/group、模型先验和 g-prior 等设置放在最后核对。"
'''
new = '''        local purpose2 "基础页面用于普通候选预测变量；需要 always/group 等内联变量组时，可直接在下方实时命令中按 Stata 原生语法补充；模型先验和 g-prior 等 options 运行前核对。"
'''
sem = replace_once(sem, old, new, "clarify bmaregress inline groups")

old = '''        local panel_label "个体 / 面板变量"
        local time_label "时间变量（可按数据结构留空）"
    }
    else if strpos(" mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm ", " `cmd' ") {
'''
new = '''        local panel_label "个体 / 面板变量"
        if inlist("`cmd'", "xtabond", "xtdpdsys") local time_label "时间变量（动态面板必填）"
        else local time_label "时间变量（可按数据结构留空）"
    }
    else if strpos(" mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm ", " `cmd' ") {
'''
sem = replace_once(sem, old, new, "label dynamic-panel time")

old = '''    else if strpos(" stset sts stcox streg stcrreg ", " `cmd' ") {
        local title "`cmd' — 生存与事件史分析"
        local purpose1 "用于声明生存数据、绘制生存函数或估计 Cox、参数生存与竞争风险模型。"
        local purpose2 "先确认失败事件、分析时间和删失定义；生存数据声明与模型 options 需在运行前核对。"
    }
'''
new = '''    else if strpos(" stset sts stcox streg stcrreg ", " `cmd' ") {
        if "`cmd'" != "stcox" {
            local title "`cmd' — 生存与事件史分析"
            local purpose1 "用于声明生存数据、绘制生存函数或估计参数生存与竞争风险模型。"
            local purpose2 "先确认失败事件、分析时间和删失定义；生存数据声明与模型 options 需在运行前核对。"
        }
    }
'''
sem = replace_once(sem, old, new, "preserve stcox-specific copy")
sem_path.write_text(sem, encoding="utf-8")


# Contract assertions for this self-audit pass.
java = java_path.read_text(encoding="utf-8")
registry = registry_path.read_text(encoding="utf-8")
sem = sem_path.read_text(encoding="utf-8")
assert 'private static boolean isGenericPanelTimeRequired' in java
assert 'Arrays.asList("xtabond", "xtdpdsys")' in java
assert '当前动态面板模型必须同时指定面板变量和时间变量' in java
assert 'if c(stata_version) < 18' in registry
assert 'local view "bmaregress"' in registry
assert '时间变量（动态面板必填）' in sem
assert 'local title "stcox — Cox 比例风险模型"' in sem
print("UI_SELF_AUDIT_PASS12_OK")
