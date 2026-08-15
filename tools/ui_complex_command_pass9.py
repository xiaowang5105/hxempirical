from pathlib import Path

p = Path(__file__).resolve().parents[1] / "hxsemantics.ado"
s = p.read_text(encoding="utf-8")

old = 'if strpos(" sem gsem mi meta fmm irt svy bootstrap jackknife permute simulate statsby bayes bayesmh bayespredict bayesstats bayesgraph power teffects sts irf graph discrim cluster ", " `cmd\' ") {'
new = 'if strpos(" sem gsem mi meta fmm irt svy bootstrap jackknife permute simulate statsby bayes bayesmh bayespredict bayesstats bayesgraph power teffects sts irf graph discrim cluster table prtest sdtest oneway anova ranksum median signrank signtest bitesti tabi cc cs ir sureg mvreg canon cca manova heckman heckprobit heckoprobit heckpoisson eregress eprobit eoprobit epoisson eintreg mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm lasso elasticnet npregress stset ", " `cmd\' ") {'
if old not in s:
    raise SystemExit('complex command list marker not found')
s = s.replace(old, new, 1)

marker = '''        else if "`cmd'" == "teffects" {
            local expr_label "估计器 + 结果方程 + 处理方程（如 psmatch (y) (treat x1 x2)）"
            local example1 "teffects psmatch (y) (treat x1 x2)"
            local explain1 "使用倾向得分匹配估计处理效应。"
            local example2 "teffects ipwra (y x1 x3) (treat x1 x2)"
            local explain2 "使用双重稳健 IPWRA。"
        }
'''
insert = marker + '''        else if strpos(" table prtest sdtest oneway anova ranksum median signrank signtest bitesti tabi ", " `cmd' ") {
            local expr_label "检验 / 表格主体（变量、分组、比较值或计数参数）"
            local example1 "help `cmd'"
            local explain1 "这些命令的变量角色和参数顺序差异较大，页面保留官方原生命令主体，避免把分组变量或比较值误标成解释变量。"
        }
        else if strpos(" cc cs ir ", " `cmd' ") {
            local expr_label "流行病学命令主体（病例 / 暴露 / 时间 / 分层参数）"
            local example1 "help `cmd'"
            local explain1 "病例对照、队列和发病率命令的变量角色不同，按当前 help 填写完整主体。"
        }
        else if strpos(" sureg mvreg canon cca manova ", " `cmd' ") {
            local expr_label "多方程 / 多变量模型主体（含括号、等号或变量组）"
            if "`cmd'" == "sureg" {
                local example1 "sureg (y1 x1 x2) (y2 x1 x3)"
                local explain1 "每组括号表示一个方程。"
            }
            else {
                local example1 "help `cmd'"
                local explain1 "该模型包含多个结果或变量组，直接保留原生语法比猜测单一 Y/X 角色更可靠。"
            }
        }
        else if strpos(" heckman heckprobit heckoprobit heckpoisson ", " `cmd' ") {
            local expr_label "结果方程 + 选择方程主体（含 select() 等命令特有结构）"
            local example1 "help `cmd'"
            local explain1 "样本选择模型至少包含结果方程和选择机制，完整主体可以明确两套变量角色。"
        }
        else if strpos(" eregress eprobit eoprobit epoisson eintreg ", " `cmd' ") {
            local expr_label "主结果方程 + 内生协变量 / 处理方程主体"
            local example1 "help `cmd'"
            local explain1 "扩展回归模型可能同时包含多个内生方程，页面使用完整原生主体避免丢失方程结构。"
        }
        else if strpos(" mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm ", " `cmd' ") {
            local expr_label "固定部分 + || 随机效应层级（如 y x1 x2 || school: x2 || class:）"
            if "`cmd'" == "mixed" {
                local example1 "mixed y x1 x2 || school: x2 || class:"
                local explain1 "固定效应写在前面，|| 后按层级写随机截距 / 随机斜率。"
            }
            else {
                local example1 "help `cmd'"
                local explain1 "多层模型的 || 随机效应结构属于核心模型主体，不能只用普通 Y/X 框代替。"
            }
        }
        else if inlist("`cmd'", "lasso", "elasticnet") {
            local expr_label "模型类型 + 因变量 + 候选变量（如 linear y x1-x100）"
            local example1 "`cmd' linear y x1-x100"
            local explain1 "lasso / elasticnet 在因变量前需要明确 linear、logit、probit、poisson 或 cox 等模型类型。"
        }
        else if "`cmd'" == "npregress" {
            local expr_label "非参数方法 + 因变量 + 协变量（如 kernel y x1 x2 或 series y x1 x2）"
            local example1 "npregress kernel y x1 x2"
            local explain1 "kernel / series 是 npregress 的核心方法词，必须放在因变量之前。"
            local example2 "npregress series y x1 x2"
            local explain2 "使用 series 非参数回归。"
        }
        else if "`cmd'" == "stset" {
            local expr_label "生存数据声明主体（分析时间、failure()、id()、enter()/exit() 等）"
            local example1 "help stset"
            local explain1 "stset 同时定义分析时间、失败事件和风险区间，完整主体比单一变量框更清楚。"
        }
'''
if marker not in s:
    raise SystemExit('teffects branch marker not found')
s = s.replace(marker, insert, 1)

p.write_text(s, encoding="utf-8")
print('HX_UI_COMPLEX_COMMAND_PASS9_OK')
