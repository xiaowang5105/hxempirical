from pathlib import Path

p = Path("tools/tmp_patch_postestimation_catalog.py")
s = p.read_text(encoding="utf-8")
start = s.find("test_anchor = '''")
end = s.find("# Remaining postestimation commands use their native command bodies.", start)
if start < 0 or end < 0:
    raise SystemExit("postestimation brittle semantic patch section not found")
replacement = '''test_extra = r'''        else if "`cmd'" == "testparm" {
            local template "expression_body"
            local title "testparm — 联合检验一组模型项"
            local purpose1 "对一组系数、因子变量 levels 或交互项执行联合 Wald 检验。"
            local purpose2 "特别适合检验 i.group、交互项或一组滞后项是否整体显著。"
            local example1 "testparm i.group"
            local explain1 "联合检验 group 的所有非基准类别系数是否同时为 0。"
            local example2 "testparm c.x#i.group"
            local explain2 "联合检验 x 与 group 的全部交互项。"
        }
        else if "`cmd'" == "testnl" {
            local template "expression_body"
            local title "testnl — 非线性 Wald 假设检验"
            local purpose1 "检验由回归系数组成的非线性约束，并用 delta method 计算 Wald statistic。"
            local purpose2 "表达式直接引用 _b[var] 或 equation-specific coefficient names。"
            local example1 "testnl (_b[x])^2 = 1"
            local explain1 "检验 x 系数平方是否等于 1。"
            local example2 "testnl _b[x1]/_b[x2] = 1"
            local explain2 "检验两个系数之比是否等于 1。"
        }
'''
test_marker = '        else if "`cmd\'" == "lincom" {\\n'
if s.count(test_marker) != 1:
    raise SystemExit(f"post test insertion marker count={s.count(test_marker)}")
s = s.replace(test_marker, test_extra + test_marker, 1)

nlcom_block = r'''        else if "`cmd'" == "nlcom" {
            local template "expression_body"
            local title "nlcom — 非线性系数组合"
            local purpose1 "计算系数的比率、乘积、转折点等非线性函数，并用 delta method 给出标准误和区间。"
            local purpose2 "表达式通常直接引用 _b[var]；多方程模型应使用 equation-specific coefficient names。"
            local example1 "nlcom (_b[x])^2"
            local explain1 "报告 x 系数平方及其 delta-method 标准误。"
            local example2 "nlcom -_b[x]/(2*_b[c.x#c.x])"
            local explain2 "计算二次项模型的 turning point。"
        }
'''
nlcom_marker = '        else if "`cmd\'" == "predict" {\\n'
if s.count(nlcom_marker) != 1:
    raise SystemExit(f"nlcom insertion marker count={s.count(nlcom_marker)}")
s = s.replace(nlcom_marker, nlcom_block + nlcom_marker, 1)

'''
s = s[:start] + replacement + s[end:]
p.write_text(s, encoding="utf-8", newline="\n")
print("HX_POSTESTIMATION_PATCH_PREPARE_OK")
