from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------- registry ----------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.17  16aug2026", "*! hxregistry 3.1.18  16aug2026", "registry version")
old_catalog = "stset sts stcox streg stintreg stintcox stcrreg cc"
new_catalog = "ctset cttost ltable snapspan stset stdescribe stsum stci stcurve stbase stfill stgen stsplit stvary sttocc sttoct sts stcox streg stintreg stintcox stcrreg stir strate stptime stmh stmc cc"
r = once(r, old_catalog, new_catalog, "survival workflow catalog")
old_route = '''    else if inlist(`"`method'"', "生存分析", "survival") {
        local view "stset sts stcox streg stintreg"
        if c(stata_version) >= 17 local view "`view' stintcox"
        local view "`view' stcrreg"
    }
'''
new_route = '''    else if inlist(`"`method'"', "生存分析", "survival") {
        local view "ctset cttost ltable snapspan stset stdescribe stsum stci stcurve stbase stfill stgen stsplit stvary sttocc sttoct"
        local view "`view' sts stcox streg stintreg"
        if c(stata_version) >= 17 local view "`view' stintcox"
        local view "`view' stcrreg stir strate stptime stmh stmc"
    }
'''
r = once(r, old_route, new_route, "survival method route")
keyword_anchor = '        local key_tsset "tsset time series 时间序列 时间变量 声明"\n'
keyword_add = '''        local key_ctset "ctset count-time survival 生存 计数时间 声明"
        local key_cttost "cttost count-time to survival 转换 生存数据"
        local key_ltable "ltable life table actuarial 生存表 寿命表"
        local key_stdescribe "stdescribe survival describe 生存数据 描述 结构"
        local key_stsum "stsum survival summary Kaplan Meier 生存时间 汇总"
        local key_stci "stci survival confidence interval mean median 生存 置信区间"
        local key_stcurve "stcurve survival failure hazard cumulative hazard 生存曲线 风险"
        local key_stsplit "stsplit split time records 生存 时间段 拆分"
        local key_stgen "stgen survival history variable 生存 历史 生成变量"
        local key_stfill "stfill carry forward covariates 生存 协变量 前向填充"
        local key_stvary "stvary time-varying covariates 生存 时变变量"
        local key_sttocc "sttocc nested case control 生存 嵌套 病例对照"
        local key_sttoct "sttoct survival count-time 转换 生存 计数时间"
        local key_stir "stir incidence rate ratio 生存 发病率 比率"
        local key_strate "strate failure rates SMR 生存 率 标准化死亡比"
        local key_stptime "stptime person-time incidence rate 生存 人时 发病率"
        local key_stmh "stmh Mantel Haenszel rate ratio 生存 分层 率比"
        local key_stmc "stmc Mantel Cox rate ratio 生存 分层 率比"
'''
r = once(r, keyword_anchor, keyword_anchor + keyword_add, "survival search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------- semantics ----------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.16  16aug2026", "*! hxsemantics 1.4.17  16aug2026", "semantics version")
old_body = " npregress stset streg stintreg stintcox stcrreg arima "
new_body = " npregress ctset cttost ltable snapspan stset stdescribe stsum stci stcurve stbase stfill stgen stsplit stvary sttocc sttoct streg stintreg stintcox stcrreg stir strate stptime stmh stmc arima "
s = once(s, old_body, new_body, "survival command-body catalog")

marker = '''        else if "`cmd'" == "stintreg" {
'''
if s.count(marker) != 1:
    raise SystemExit(f"survival semantic insertion marker count={s.count(marker)}")
blocks = '''        else if "`cmd'" == "ctset" {
            local expr_label "时间 + 失败数 + 失访数 + 进入数 + by()（count-time 数据声明）"
            local example1 "ctset time failures lost entered, by(group)"
            local explain1 "把聚合的 count-time 生存表声明为 Stata count-time 数据；进入、失败和失访人数需要在各组内平衡。"
            local example2 "help ctset"
            local explain2 "ctset 后通常用 cttost 转成 st 数据，再进入 sts/streg/stcox 等工作流。"
        }
        else if "`cmd'" == "cttost" {
            local expr_label "count-time → survival-time 转换 options"
            local example1 "cttost, clear"
            local explain1 "把已 ctset 的聚合 count-time 数据转换成 st 数据；clear 会重写当前内存数据。"
            local example2 "help cttost"
            local explain2 "转换前应保存原始数据，并检查 ctset 中进入、失败和失访人数是否一致。"
        }
        else if "`cmd'" == "ltable" {
            local expr_label "时间变量 + 失败状态变量 + interval()/by()/failure 等 life-table 设定"
            local example1 "ltable studytime died, failure graph"
            local explain1 "按 actuarial life-table 方法汇总 studytime 与 died，并绘制失败函数。"
            local example2 "help ltable"
            local explain2 "ltable 会按区间聚合；若需要精确 Kaplan–Meier 风险集，优先使用 sts list/graph。"
        }
        else if "`cmd'" == "snapspan" {
            local expr_label "subject ID + snapshot 时间 + 状态变量 + generate() 起点变量"
            local example1 "help snapspan"
            local explain1 "把 snapshot 记录转换为 time-span 记录；转换会重构每个 subject 的时间区间。"
            local example2 "stset endtime, id(id) time0(starttime) failure(event)"
            local explain2 "snapspan 后通常继续 stset；先核对生成的起止时间与状态变量。"
        }
        else if "`cmd'" == "stdescribe" {
            local expr_label "已 stset 数据的结构描述 options（通常直接运行）"
            local example1 "stdescribe"
            local explain1 "检查 subjects、records、entry/exit time、gaps、time at risk 和 failures。"
            local example2 "help stdescribe"
            local explain2 "适合放在 stset 后第一步，先确认数据结构再估计生存模型。"
        }
        else if "`cmd'" == "stsum" {
            local expr_label "by() 等生存时间汇总设定"
            local example1 "stsum, by(group)"
            local explain1 "按 group 汇总 time at risk、失败数和生存时间分布。"
            local example2 "help stsum"
            local explain2 "与普通 summarize 不同，stsum 使用 stset 后的 risk-time 定义。"
        }
        else if "`cmd'" == "stci" {
            local expr_label "by() + mean/p() 等生存时间置信区间设定"
            local example1 "stci, by(group)"
            local explain1 "按 group 报告平均/中位等生存时间及置信区间。"
            local example2 "help stci"
            local explain2 "估计对象来自当前 stset 的 survivor function，分组和权重限制运行前核对。"
        }
        else if "`cmd'" == "stcurve" {
            local expr_label "survival/failure/hazard/chazard + at() 等上一模型后曲线设定"
            local example1 "stcurve, survival"
            local explain1 "在兼容的 streg、stcox、stcrreg、stintreg 或 stintcox 估计后绘制调整后的生存函数。"
            local example2 "stcurve, cif"
            local explain2 "在 competing-risks 模型后可绘制 cumulative incidence function。"
        }
        else if "`cmd'" == "stbase" {
            local expr_label "从已 stset 数据构造 baseline dataset 的 at()/failure 等设定"
            local example1 "help stbase"
            local explain1 "把多记录 survival-time 数据压成 baseline 数据；属于数据重构操作，运行前先保存当前数据。"
            local example2 "stdescribe"
            local explain2 "重构后重新检查 subject、entry/exit 和 failure 定义。"
        }
        else if "`cmd'" == "stfill" {
            local expr_label "要在 subject 历史内 carry forward/backward 的协变量"
            local example1 "help stfill"
            local explain1 "在同一 subject 的多段记录之间填充协变量值；会修改当前数据中的变量。"
            local example2 "stvary"
            local explain2 "填充后用 stvary 检查哪些协变量仍随时间变化。"
        }
        else if "`cmd'" == "stgen" {
            local expr_label "新变量 = survival-history function()"
            local example1 "help stgen"
            local explain1 "按每个 subject 的完整生存历史生成累计、首次/末次事件时间等派生变量。"
            local example2 "describe"
            local explain2 "生成后检查变量含义和记录级/subject 级重复方式，再进入模型。"
        }
        else if "`cmd'" == "stsplit" {
            local expr_label "新时间段变量 + at()/after()/every() 等切分规则"
            local example1 "stsplit ageband, at(20(5)80)"
            local explain1 "把每个 subject 的风险时间按 5 年年龄段切成多条 time-span 记录。"
            local example2 "help stsplit"
            local explain2 "stsplit 会增加记录数并改变数据形态；切分后重新 stdescribe 检查 gaps 和 risk time。"
        }
        else if "`cmd'" == "stvary" {
            local expr_label "要检查是否随时间变化的协变量列表"
            local example1 "stvary x1 x2"
            local explain1 "检查 x1、x2 在同一 subject 的多段记录中是否发生变化。"
            local example2 "help stvary"
            local explain2 "适合在构造 time-varying covariates 或 stfill 后验证数据。"
        }
        else if "`cmd'" == "sttocc" {
            local expr_label "match() + number() 等 nested case-control 抽样设定"
            local example1 "sttocc, match(sex agegroup) number(4)"
            local explain1 "从 stset cohort 的每个 failure risk set 中抽取最多 4 个按 sex、agegroup 匹配的 controls。"
            local example2 "help sttocc"
            local explain2 "该命令会生成 nested case-control 数据；抽样前保存完整 cohort，并确认 risk-set 定义。"
        }
        else if "`cmd'" == "sttoct" {
            local expr_label "survival-time → count-time 聚合转换设定"
            local example1 "help sttoct"
            local explain1 "把 st 数据转换成 count-time 表；属于数据重构操作，运行前先保存原始 survival-time 数据。"
            local example2 "ctset"
            local explain2 "转换后用 ctset 检查 time、failure、lost/entered 与分组定义。"
        }
        else if "`cmd'" == "stir" {
            local expr_label "二元 exposure + by()/level() 等 incidence-rate ratio 设定"
            local example1 "stir exposed"
            local explain1 "比较 exposed=1 与 exposed=0 的 incidence rate 并报告 incidence-rate ratio。"
            local example2 "help stir"
            local explain2 "exposure 应是二元变量；多分类率比较更适合 strate/stptime。"
        }
        else if "`cmd'" == "strate" {
            local expr_label "一个或多个分组变量 + per()/smr() 等 failure-rate 设定"
            local example1 "strate group, per(1000)"
            local explain1 "按 group 报告每 1,000 person-time 的 failure rate。"
            local example2 "help strate"
            local explain2 "可进一步计算 SMR；分母来自当前 stset 的 person-time。"
        }
        else if "`cmd'" == "stptime" {
            local expr_label "by() + per()/smr() 等 person-time 率汇总设定"
            local example1 "stptime, by(group) per(1000)"
            local explain1 "按 group 汇总 person-time、failure 数和每 1,000 person-time 的 incidence rate。"
            local example2 "help stptime"
            local explain2 "适合直接查看风险人时与率；率比检验可进一步使用 stir/stmh/stmc。"
        }
        else if inlist("`cmd'", "stmh", "stmc") {
            local expr_label "二元 exposure + by() 分层变量（Mantel–Haenszel / Mantel–Cox rate ratio）"
            local example1 "help `cmd'"
            local explain1 "在分层 person-time 数据中计算调整后的 rate ratio；分层变量和 exposure 编码应先核对。"
            local example2 "strate"
            local explain2 "先用 strate/stptime 检查各层 person-time 和 failures，再进行分层率比汇总。"
        }
'''
s = s.replace(marker, blocks + marker, 1)

old_family = '    else if strpos(" stset sts stcox streg stintreg stintcox stcrreg ", " `cmd\' ") {\n'
new_family = '    else if strpos(" ctset cttost ltable snapspan stset stdescribe stsum stci stcurve stbase stfill stgen stsplit stvary sttocc sttoct sts stcox streg stintreg stintcox stcrreg stir strate stptime stmh stmc ", " `cmd\' ") {\n'
s = once(s, old_family, new_family, "survival family copy")
s = once(
    s,
    '            local purpose1 "用于声明生存数据、绘制生存函数或估计参数生存与竞争风险模型。"\n',
    '            local purpose1 "用于声明/检查/转换 survival data、非参数生存分析、率与人时汇总，以及 Cox、参数、区间删失和竞争风险模型。"\n',
    "survival family purpose",
)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------- permanent static contracts ----------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'time_series_core = {\n'
checks = '''survival_workflow_core = {
    "ctset", "cttost", "ltable", "snapspan", "stset", "stdescribe", "stsum", "stci", "stcurve", "stbase",
    "stfill", "stgen", "stsplit", "stvary", "sttocc", "sttoct", "sts", "stcox", "streg", "stintreg", "stintcox",
    "stcrreg", "stir", "strate", "stptime", "stmh", "stmc",
}
missing_survival_workflow = sorted(survival_workflow_core - stats_cmds)
if missing_survival_workflow:
    fail("survival workflow commands missing: " + ", ".join(missing_survival_workflow))
if "stmgintcox" in stats_cmds:
    fail("Stata 19 stmgintcox must not leak into the Stata 16-18 catalog")
for needle in (
    "ctset time failures lost entered, by(group)",
    "cttost, clear",
    "ltable studytime died, failure graph",
    "stdescribe",
    "stsum, by(group)",
    "stci, by(group)",
    "stcurve, survival",
    "stsplit ageband, at(20(5)80)",
    "stvary x1 x2",
    "sttocc, match(sex agegroup) number(4)",
    "stir exposed",
    "strate group, per(1000)",
    "stptime, by(group) per(1000)",
):
    if needle not in semantics:
        fail(f"survival workflow semantic contract missing: {needle}")

'''
v = once(v, anchor, checks + anchor, "survival workflow static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_SURVIVAL_WORKFLOW_PATCH_OK")
