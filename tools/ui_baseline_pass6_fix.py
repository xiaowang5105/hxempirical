from pathlib import Path
p=Path(__file__).resolve().parents[1]/'src/main/java/com/hexie/stata/HxWorkbench.java'
s=p.read_text(encoding='utf-8')
old='''         this.insightArea.setText("基准回归工作区用于在同一研究设定下比较常用线性估计器。默认使用 xtreg（固定效应），也可以切换 reghdfe、areg 或 regress。\n\n切换估计器时保留 Y、核心 X、Controls、样本条件和标准误等公共设置，只替换模型或固定效应等估计器特有参数。\n\n底部始终生成当前估计器的真实 Stata 命令。");'''
# The first patch writes literal newlines inside the Java string; normalize the whole statement.
start=s.index('         this.insightArea.setText("基准回归工作区用于在同一研究设定下比较常用线性估计器。')
end=s.index('");', start)+3
new='         this.insightArea.setText("基准回归工作区用于在同一研究设定下比较常用线性估计器。默认使用 xtreg（固定效应），也可以切换 reghdfe、areg 或 regress。切换估计器时保留 Y、核心 X、Controls、样本条件和标准误等公共设置，只替换模型或固定效应等估计器特有参数。底部始终生成当前估计器的真实 Stata 命令。");'
s=s[:start]+new+s[end:]
p.write_text(s,encoding='utf-8')
print('HX_UI_BASELINE_PASS6_FIX_OK')
