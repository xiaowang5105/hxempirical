from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
registry_path = root / 'hxregistry.ado'
sem_path = root / 'hxsemantics.ado'
java_path = root / 'src/main/java/com/hexie/stata/HxWorkbench.java'
registry = registry_path.read_text(encoding='utf-8')
sem = sem_path.read_text(encoding='utf-8')
java = java_path.read_text(encoding='utf-8')


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, got {n}')
    return text.replace(old, new, 1)


# 1) The BMA suite's estimation command is bmaregress; keep the catalog executable.
registry = replace_once(registry, ' bayesgraph bma predict ', ' bayesgraph bmaregress predict ', 'registry bma command')
if 'local key_bmaregress ' not in registry:
    marker = '        local key_predict "predict 预测值 残差"\n'
    registry = replace_once(
        registry,
        marker,
        '        local key_bmaregress "bmaregress bma bayesian model averaging 贝叶斯模型平均 模型不确定性 变量选择"\n' + marker,
        'bmaregress search key',
    )

# 2) Survival-time Cox page: outcome/time are already declared by stset, so show covariates only.
family_marker = '    /* Complex prefixes, workflow commands, and multi-equation grammars are safer\n'
stcox_block = r'''    /* stcox models the failure/time declared by stset; variables entered here are covariates. */
    if "`cmd'" == "stcox" {
        local template "generic"
        local title "stcox — Cox 比例风险模型"
        local purpose1 "在已经 stset 的生存数据上估计 Cox 比例风险模型。"
        local purpose2 "失败事件和分析时间来自 stset；本页只选择协变量，稳健标准误等放在最后设置。"
        local has_depvar 0
        local has_varlist 1
        local vars_label "协变量（失败事件 / 分析时间已由 stset 定义）"
        local example1 "stcox age i.dose"
        local explain1 "age 和 dose 是协变量；失败事件与分析时间沿用当前 stset。"
        local example2 "stcox age i.dose, vce(robust)"
        local explain2 "在相同 Cox 模型上使用稳健标准误。"
    }

    /* bmaregress is the executable estimation command in Stata's BMA suite. */
    if "`cmd'" == "bmaregress" {
        local template "generic"
        local title "bmaregress — 贝叶斯模型平均线性回归"
        local purpose1 "在多个候选线性模型之间进行贝叶斯模型平均，反映模型选择不确定性。"
        local purpose2 "先选择结果变量和候选预测变量；always/group、模型先验和 g-prior 等设置放在最后核对。"
        local has_depvar 1
        local has_varlist 1
        local dep_label "结果变量 Y"
        local vars_label "候选预测变量"
        local example1 "bmaregress y x1-x10"
        local explain1 "对 y 的候选预测变量 x1 到 x10 进行 BMA 线性回归。"
        local example2 "bmaregress y (x1-x3, always) x4-x10"
        local explain2 "把 x1 到 x3 设为所有候选模型都保留的变量。"
    }

'''
if stcox_block.strip() not in sem:
    idx = sem.index(family_marker)
    sem = sem[:idx] + stcox_block + sem[idx:]

# 3) Add more commands whose core grammar cannot be represented safely by a plain Y/X page.
old_complex = 'if strpos(" sem gsem mi meta fmm irt svy bootstrap jackknife permute simulate statsby bayes bayesmh bayespredict bayesstats bayesgraph power teffects sts irf graph discrim cluster table prtest sdtest oneway anova ranksum median signrank signtest bitesti tabi cc cs ir sureg mvreg canon cca manova heckman heckprobit heckoprobit heckpoisson eregress eprobit eoprobit epoisson eintreg mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm lasso elasticnet npregress stset ", " `cmd\' ") {'
new_complex = 'if strpos(" sem gsem mi meta fmm irt svy bootstrap jackknife permute simulate statsby bayes bayesmh bayespredict bayesstats bayesgraph power teffects sts irf graph discrim cluster table prtest sdtest oneway anova ranksum median signrank signtest bitesti tabi cc cs ir sureg mvreg canon cca manova heckman heckprobit heckoprobit heckpoisson eregress eprobit eoprobit epoisson eintreg mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm lasso elasticnet npregress stset streg stcrreg dsregress poivregress xporegress xpoivregress etregress etpoisson fracreg zip zinb tpoisson tnbreg glm hetprobit asclogit asmprobit ", " `cmd\' ") {'
sem = replace_once(sem, old_complex, new_complex, 'extend raw grammar commands')

# 4) Add task-specific examples/labels for those newly raw commands.
insert_marker = '''        else if "`cmd'" == "stset" {
            local expr_label "生存数据声明主体（分析时间、failure()、id()、enter()/exit() 等）"
            local example1 "help stset"
            local explain1 "stset 同时定义分析时间、失败事件和风险区间，完整主体比单一变量框更清楚。"
        }
'''
extra = r'''        else if "`cmd'" == "streg" {
            local expr_label "协变量 + 参数分布等核心 options（如 age protect, distribution(weibull)）"
            local example1 "streg protect age, distribution(weibull)"
            local explain1 "失败事件与分析时间来自 stset；这里填写协变量和参数生存分布。"
            local example2 "streg age, distribution(exponential)"
            local explain2 "以指数分布拟合参数生存模型。"
        }
        else if "`cmd'" == "stcrreg" {
            local expr_label "协变量 + compete()（如 ifp tumsize, compete(failtype==2)）"
            local example1 "stcrreg ifp tumsize pelnode, compete(failtype==2)"
            local explain1 "失败事件来自 stset，compete() 指定竞争事件。"
        }
        else if "`cmd'" == "dsregress" {
            local expr_label "Y + 关注变量 + controls()（如 y d1, controls(x1-x100)）"
            local example1 "dsregress y d1, controls(x1-x100)"
            local explain1 "d1 是关注变量，controls() 中的高维候选控制由 lasso 选择。"
        }
        else if inlist("`cmd'", "poivregress", "xpoivregress") {
            local expr_label "Y + 关注变量 + (内生变量 = 工具变量) + controls()"
            local example1 "`cmd' y d1 (x = z1-z20), controls(c1-c100)"
            local explain1 "把关注变量、IV 方程和高维候选控制完整保留在一个主体中。"
        }
        else if "`cmd'" == "xporegress" {
            local expr_label "Y + 关注变量 + controls()（交叉拟合 partialing-out）"
            local example1 "xporegress y d1, controls(x1-x100)"
            local explain1 "d1 是需要推断的变量，controls() 交给 lasso 选择并交叉拟合。"
        }
        else if inlist("`cmd'", "etregress", "etpoisson") {
            local expr_label "结果方程 + treat() 处理方程"
            local example1 "etregress wage age grade, treat(union = south black tenure)"
            local explain1 "主结果方程写在前面，内生处理变量及其协变量写进 treat()。"
            local example2 "help `cmd'"
            local explain2 "etpoisson 与 etregress 的结果分布不同，处理方程结构仍需显式保留。"
        }
        else if "`cmd'" == "fracreg" {
            local expr_label "链接模型 + Y + X（如 probit prate mrate sole）"
            local example1 "fracreg probit prate mrate sole"
            local explain1 "fracreg 的 probit/logit 等模型词位于结果变量之前。"
            local example2 "fracreg logit prate mrate sole"
            local explain2 "使用 fractional logit 拟合比例结果。"
        }
        else if inlist("`cmd'", "zip", "zinb") {
            local expr_label "计数方程 + inflate() 零膨胀方程"
            local example1 "`cmd' y x1 x2, inflate(z1 z2)"
            local explain1 "主计数方程与产生额外零值的 inflate() 方程需要同时明确。"
        }
        else if inlist("`cmd'", "tpoisson", "tnbreg") {
            local expr_label "Y + X + 截断点 options（ll()/ul()）"
            local example1 "`cmd' y x1 x2, ll(0)"
            local explain1 "截断模型必须把样本截断边界作为模型核心设定核对。"
        }
        else if "`cmd'" == "glm" {
            local expr_label "Y + X + family()/link()（如 y x, family(poisson) link(log)）"
            local example1 "glm y x, family(poisson) link(log)"
            local explain1 "GLM 的分布族和链接函数决定模型形式，因此和变量一起放在核心主体。"
        }
        else if "`cmd'" == "hetprobit" {
            local expr_label "主 Probit 方程 + het() 异方差方程"
            local example1 "hetprobit y x1 x2, het(z1 z2)"
            local explain1 "het() 中的变量决定潜在误差方差，需要与主方程一起确认。"
        }
        else if inlist("`cmd'", "asclogit", "asmprobit") {
            local expr_label "选择指示 + 备选项变量 + case()/alternatives()/casevars()"
            local example1 "`cmd' choice price, case(id) alternatives(alt) casevars(income age)"
            local explain1 "备选项特征、选择场景 ID、备选项 ID 与个体特征都属于离散选择模型的核心结构。"
        }
'''
if extra.strip() not in sem:
    sem = replace_once(sem, insert_marker, insert_marker + extra, 'new raw command branches')

# 5) Rename the stale BMA semantic command to the executable bmaregress command.
sem = replace_once(
    sem,
    '''    else if "`cmd'" == "bma" {
        local title "bma — 贝叶斯模型平均"
        local purpose1 "用于在多个候选模型之间进行贝叶斯模型平均并反映模型不确定性。"
        local purpose2 "候选变量、先验和模型空间设定会直接影响结果，建议在运行前明确研究口径。"
    }
''',
    '''    else if "`cmd'" == "bmaregress" {
        local title "bmaregress — 贝叶斯模型平均线性回归"
        local purpose1 "用于在线性回归候选模型之间进行贝叶斯模型平均并反映模型不确定性。"
        local purpose2 "候选变量、always/group、模型先验和 g-prior 会影响结果，运行前应明确模型空间。"
    }
''',
    'bma semantic command',
)

# 6) First-screen task titles should follow the corrected BMA command.
java = java.replace('"bayes", "bayesmh", "bayespredict", "bayesstats", "bayesgraph", "bma"', '"bayes", "bayesmh", "bayespredict", "bayesstats", "bayesgraph", "bmaregress"')
java = java.replace('"bma".equals(command)', '"bmaregress".equals(command)')

registry_path.write_text(registry, encoding='utf-8')
sem_path.write_text(sem, encoding='utf-8')
java_path.write_text(java, encoding='utf-8')
print('HX_UI_COMMAND_CORRECTNESS_PASS10_OK')
