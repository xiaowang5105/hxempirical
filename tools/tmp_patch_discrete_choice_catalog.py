from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------------- registry ----------------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.11  16aug2026", "*! hxregistry 3.1.12  16aug2026", "registry version")
r = once(
    r,
    "logit logistic probit hetprobit scobit cloglog ologit oprobit mlogit mprobit asclogit asmprobit",
    "logit logistic binreg probit biprobit hetprobit scobit cloglog ologit oprobit hetoprobit ziologit zioprobit mlogit mprobit clogit slogit cmset cmsummarize cmchoiceset cmtab cmsample cmclogit cmmixlogit cmxtmixlogit cmmprobit cmroprobit cmrologit nlogit asclogit asmprobit",
    "discrete outcome catalog",
)
r = once(
    r,
    '''    if c(stata_version) < 17 {
        foreach cmd in didregress xtdidregress telasso {
            local stats_cmds : subinstr local stats_cmds " `cmd'" "", all
        }
    }
''',
    '''    if c(stata_version) < 17 {
        foreach cmd in didregress xtdidregress telasso ziologit {
            local stats_cmds : subinstr local stats_cmds " `cmd'" "", all
        }
    }
''',
    "Stata 17 gate",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "二元结果", "binary_outcomes") local view "logit logistic probit hetprobit scobit cloglog"\n',
    '    else if inlist(`"`method\'"\', "二元结果", "binary_outcomes") local view "logit logistic binreg probit biprobit hetprobit scobit cloglog"\n',
    "binary method",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "序数结果", "ordinal_outcomes") local view "ologit oprobit"\n',
    '''    else if inlist(`"`method'"', "序数结果", "ordinal_outcomes") {
        local view "ologit oprobit hetoprobit zioprobit"
        if c(stata_version) >= 17 local view "`view' ziologit"
    }
''',
    "ordinal method",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "分类结果", "categorical_outcomes") local view "mlogit mprobit asclogit asmprobit"\n',
    '    else if inlist(`"`method\'"\', "分类结果", "categorical_outcomes") local view "mlogit mprobit clogit slogit cmset cmsummarize cmchoiceset cmtab cmsample cmclogit cmmixlogit cmxtmixlogit cmmprobit cmroprobit cmrologit nlogit asclogit asmprobit"\n',
    "categorical method",
)
anchor = '        local key_logit "logit 二元 逻辑回归"\n'
add = '''        local key_binreg "binreg binomial glm risk ratio risk difference odds ratio 二项 风险比 风险差"
        local key_biprobit "biprobit bivariate probit two binary equations 二元 双变量 probit 联立 方程"
        local key_hetoprobit "hetoprobit heteroskedastic ordered probit 序数 异方差 有序 probit"
        local key_ziologit "ziologit zero inflated ordered logit 零膨胀 序数 有序 logit inflate"
        local key_zioprobit "zioprobit zero inflated ordered probit 零膨胀 序数 有序 probit inflate"
        local key_clogit "clogit conditional logistic matched case control fixed effects 条件 logistic 配对 病例对照"
        local key_slogit "slogit stereotype logistic categorical ordinal stereotype 分类 立体型 logit"
        local key_cmset "cmset choice model data declare case alternative panel choice 选择模型 数据声明 备选项"
        local key_cmsummarize "cmsummarize choice data summarize 选择模型 描述 备选项"
        local key_cmchoiceset "cmchoiceset choice sets tabulate diagnose 选择集 检查"
        local key_cmtab "cmtab chosen alternatives tabulate 选择模型 选择结果 频数"
        local key_cmsample "cmsample choice sample exclusion 选择模型 样本 排除 诊断"
        local key_cmclogit "cmclogit conditional logit McFadden choice 选择模型 条件 logit 备选项"
        local key_cmmixlogit "cmmixlogit mixed logit random coefficients choice 混合 logit 随机系数 选择"
        local key_cmxtmixlogit "cmxtmixlogit panel mixed logit repeated choice 面板 混合 logit 重复选择"
        local key_cmmprobit "cmmprobit multinomial probit choice 多项 probit 选择模型"
        local key_cmroprobit "cmroprobit rank ordered probit choice 排序 probit 选择模型"
        local key_cmrologit "cmrologit rank ordered logit choice 排序 logit 选择模型"
        local key_nlogit "nlogit nested logit choice tree 巢式 logit 选择模型 树"
'''
r = once(r, anchor, anchor + add, "discrete choice search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------------- semantics ----------------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.10  16aug2026", "*! hxsemantics 1.4.11  16aug2026", "semantics version")
s = once(
    s,
    " hetregress sqreg intreg tobit truncreg boxcox fp nl nlsur gmm sureg reg3 mvreg frontier canon",
    " hetregress sqreg intreg tobit truncreg boxcox fp nl nlsur gmm sureg reg3 mvreg frontier binreg biprobit hetoprobit ziologit zioprobit clogit slogit cmset cmsummarize cmchoiceset cmtab cmsample cmclogit cmmixlogit cmxtmixlogit cmmprobit cmroprobit cmrologit nlogit canon",
    "discrete command-body catalog",
)

marker = '''        else if "`cmd'" == "hetregress" {
'''
if s.count(marker) != 1:
    raise SystemExit(f"discrete insertion marker count={s.count(marker)}")
blocks = '''        else if "`cmd'" == "binreg" {
            local expr_label "二元结果 Y + X + rr/rd/or 或 link() 报告尺度"
            local example1 "binreg y x1 x2, rr"
            local explain1 "用 binomial GLM 估计风险比；rr 决定报告尺度。"
            local example2 "binreg y x1 x2, rd"
            local explain2 "改用风险差尺度；研究问题应先明确需要 RR、RD 还是 OR。"
        }
        else if "`cmd'" == "biprobit" {
            local expr_label "两个二元 Probit 方程（每个方程一组括号）"
            local example1 "biprobit (private years) (vote logptax loginc)"
            local explain1 "联合估计 private 与 vote 两个二元结果，并允许两方程潜在误差相关。"
            local example2 "help biprobit"
            local explain2 "递归设定、约束和边际效应应结合两方程的识别结构核对。"
        }
        else if "`cmd'" == "hetoprobit" {
            local expr_label "序数 Y + X + het() 异方差方程"
            local example1 "hetoprobit health age bmi i.exercise, het(age)"
            local explain1 "主方程解释有序健康状态，het(age) 让潜在误差尺度随年龄变化。"
            local example2 "help hetoprobit"
            local explain2 "异方差方程变量应有明确的尺度异质性依据。"
        }
        else if "`cmd'" == "ziologit" {
            local expr_label "序数 Y + X + inflate() 零膨胀/最低类别生成方程"
            local example1 "ziologit tobacco education income i.female, inflate(income education i.parent)"
            local explain1 "有序 logit 方程解释吸烟强度，inflate() 区分额外最低类别来源。"
            local example2 "help ziologit"
            local explain2 "该命令从 Stata 17 开始提供；两套预测变量可以不同。"
        }
        else if "`cmd'" == "zioprobit" {
            local expr_label "序数 Y + X + inflate() 零膨胀/最低类别生成方程"
            local example1 "zioprobit tobacco income i.female age, inflate(income i.female age i.parent i.religion)"
            local explain1 "有序 probit 方程和 inflation probit 方程共同解释最低类别的两个来源。"
            local example2 "help zioprobit"
            local explain2 "最低类别的数值不必等于 0；关键是存在额外生成机制。"
        }
        else if "`cmd'" == "clogit" {
            local expr_label "二元结果 Y + X + group() 条件组/匹配组"
            local example1 "clogit case exposure x1 x2, group(matchid)"
            local explain1 "在每个 matchid 内条件化，适合匹配病例对照或组固定效应二元模型。"
            local example2 "help clogit"
            local explain2 "同组内不变化的变量无法识别；组定义属于核心设计信息。"
        }
        else if "`cmd'" == "slogit" {
            local expr_label "多类别结果 Y + X + stereotype dimension / constraints"
            local example1 "slogit y x1 x2"
            local explain1 "拟合 stereotype logistic model，在多项 logit 与有序结构之间提供更紧凑参数化。"
            local example2 "help slogit"
            local explain2 "维度、约束和结果类别解释应结合具体分类结构设置。"
        }
        else if "`cmd'" == "cmset" {
            local expr_label "case ID + time（面板时）+ alternatives 变量"
            local example1 "cmset id travelmode"
            local explain1 "横截面选择数据：id 标识 choice case，travelmode 标识备选项。"
            local example2 "cmset id t alt"
            local explain2 "重复选择/面板数据：同时声明个体 id、时间 t 和备选项 alt。"
        }
        else if "`cmd'" == "cmsummarize" {
            local expr_label "要按 chosen alternatives 汇总的 choice-data 变量（可留空看默认）"
            local example1 "cmsummarize"
            local explain1 "在已 cmset 的数据上查看 choice-data 的总体结构与变量摘要。"
            local example2 "help cmsummarize"
            local explain2 "先 cmset，再用本页确认备选项变量与 case-specific 变量分布。"
        }
        else if "`cmd'" == "cmchoiceset" {
            local expr_label "choice-set 检查参数（已 cmset 后运行）"
            local example1 "cmchoiceset"
            local explain1 "检查 choice sets 的规模和可用备选项，发现不平衡或异常选择集。"
            local example2 "help cmchoiceset"
            local explain2 "适合正式估计前做 choice-set 结构诊断。"
        }
        else if "`cmd'" == "cmtab" {
            local expr_label "要按 chosen alternative 列联/汇总的变量"
            local example1 "cmtab"
            local explain1 "查看各备选项被选择的频数与选择结构。"
            local example2 "help cmtab"
            local explain2 "可进一步按 choice-data covariates 做列联检查。"
        }
        else if "`cmd'" == "cmsample" {
            local expr_label "估计命令后的 sample-exclusion 诊断参数（通常可留空）"
            local example1 "cmsample"
            local explain1 "报告 choice model 样本被排除的原因，适合估计后诊断。"
            local example2 "help cmsample"
            local explain2 "先成功运行兼容的 cm estimation command。"
        }
        else if "`cmd'" == "cmclogit" {
            local expr_label "chosen 指示 + alternative-specific X + casevars() 个体/案例变量"
            local example1 "cmclogit chosen time, casevars(income partysize)"
            local explain1 "time 随备选项变化；income、partysize 在同一 choice case 内不变，放入 casevars()。"
            local example2 "help cmclogit"
            local explain2 "运行前先 cmset；casevars() 与 alternative-specific variables 的角色必须分清。"
        }
        else if "`cmd'" == "cmmixlogit" {
            local expr_label "chosen + 固定系数变量 + random() 随机系数 + casevars()"
            local example1 "cmmixlogit choice mfee, random(price) casevars(traffic)"
            local explain1 "mfee 固定系数，price 随机系数，traffic 为 case-specific 变量。"
            local example2 "help cmmixlogit"
            local explain2 "随机系数分布和相关结构决定如何放松 IIA，属于核心模型设定。"
        }
        else if "`cmd'" == "cmxtmixlogit" {
            local expr_label "chosen + 固定系数变量 + random() + casevars()；先 cmset panel/time/alt"
            local example1 "cmxtmixlogit choice trcost, random(trtime) casevars(age income)"
            local explain1 "对重复选择数据拟合 panel mixed logit；运行前应先用 cmset id t alt。"
            local example2 "help cmxtmixlogit"
            local explain2 "面板相关由随机系数建模，choice-data 结构由 cmset 声明。"
        }
        else if "`cmd'" == "cmmprobit" {
            local expr_label "chosen + alternative-specific X + casevars()/scale()/correlation 设定"
            local example1 "help cmmprobit"
            local explain1 "multinomial probit 允许备选项误差相关；协方差结构和尺度约束属于模型核心。"
            local example2 "cmmprobit chosen time, casevars(income)"
            local explain2 "示意：time 是 alternative-specific，income 是 case-specific；运行前先 cmset。"
        }
        else if "`cmd'" == "cmroprobit" {
            local expr_label "排名结果 + alternative-specific X + casevars()/协方差设定"
            local example1 "help cmroprobit"
            local explain1 "用于完整或部分排名的 rank-ordered probit，保留原生主体以表达 ranking 与协方差结构。"
            local example2 "cmroprobit rank x1 x2"
            local explain2 "示意：rank 是备选项排名；正式运行前按数据的排名编码核对。"
        }
        else if "`cmd'" == "cmrologit" {
            local expr_label "排名结果 + alternative-specific X + casevars()/ties 设定"
            local example1 "help cmrologit"
            local explain1 "rank-ordered logit 可处理完整/不完整排名及 ties；先 cmset 并确认 ranking 编码。"
            local example2 "cmrologit rank x1 x2"
            local explain2 "示意：rank 为备选项顺序，x1、x2 为备选项特征。"
        }
        else if "`cmd'" == "nlogit" {
            local expr_label "chosen + X + || 多层 nest tree + case()/base() 等结构"
            local example1 "nlogit chosen cost distance rating || type: income kids, base(family) || restaurant:, noconst case(family_id)"
            local explain1 "nested logit 的树层级直接写在 || 结构中；tree 需要事先按研究中的嵌套逻辑定义。"
            local example2 "help nlogit"
            local explain2 "多层 nesting、inclusive-value constraints 和 base alternatives 都属于识别结构。"
        }
'''
s = s.replace(marker, blocks + marker, 1)

# Family-level copy: refine titles for binary/ordinal/choice additions.
family_marker = '''    if strpos(" hetregress sqreg intreg tobit truncreg boxcox fp nl nlsur gmm reg3 frontier ", " `cmd' ") {
'''
family = '''    if strpos(" binreg biprobit ", " `cmd' ") {
        local title "`cmd' — 二元结果模型"
        local purpose1 "用于二项响应尺度估计或两个相关二元结果的联合 Probit 建模。"
        local purpose2 "报告尺度或多方程结构属于模型核心，页面直接保留原生语法。"
    }
    else if strpos(" hetoprobit ziologit zioprobit ", " `cmd' ") {
        local title "`cmd' — 序数结果扩展模型"
        local purpose1 "用于有序结果中的异方差或最低类别额外生成机制。"
        local purpose2 "het() 或 inflate() 是核心方程，运行前应分别解释主结果过程和尺度/膨胀过程。"
    }
    else if strpos(" clogit slogit cmset cmsummarize cmchoiceset cmtab cmsample cmclogit cmmixlogit cmxtmixlogit cmmprobit cmroprobit cmrologit nlogit ", " `cmd' ") {
        local title "`cmd' — 分类与选择模型"
        local purpose1 "用于条件/多类别结果，或 case × alternative 结构的 discrete-choice 数据。"
        local purpose2 "CM 工作流先 cmset，再检查 choice sets，最后估计；case-specific 与 alternative-specific 变量必须分开。"
    }
    else if strpos(" hetregress sqreg intreg tobit truncreg boxcox fp nl nlsur gmm reg3 frontier ", " `cmd' ") {
'''
s = once(s, family_marker, family, "discrete family copy")
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------------- static contracts ----------------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''linear_related_core = {
'''
checks = '''binary_core = {"logit", "logistic", "binreg", "probit", "biprobit", "hetprobit", "scobit", "cloglog"}
missing_binary = sorted(binary_core - stats_cmds)
if missing_binary:
    fail("binary outcome commands missing: " + ", ".join(missing_binary))
ordinal_core = {"ologit", "oprobit", "hetoprobit", "zioprobit", "ziologit"}
missing_ordinal = sorted(ordinal_core - stats_cmds)
if missing_ordinal:
    fail("ordinal outcome commands missing: " + ", ".join(missing_ordinal))
choice_core = {
    "mlogit", "mprobit", "clogit", "slogit", "cmset", "cmsummarize", "cmchoiceset", "cmtab", "cmsample",
    "cmclogit", "cmmixlogit", "cmxtmixlogit", "cmmprobit", "cmroprobit", "cmrologit", "nlogit",
}
missing_choice = sorted(choice_core - stats_cmds)
if missing_choice:
    fail("categorical/choice commands missing: " + ", ".join(missing_choice))
if 'foreach cmd in didregress xtdidregress telasso ziologit' not in registry:
    fail("Stata 17 ziologit version gate missing")
for needle in (
    'biprobit (private years) (vote logptax loginc)',
    'hetoprobit health age bmi i.exercise, het(age)',
    'ziologit tobacco education income i.female, inflate(income education i.parent)',
    'zioprobit tobacco income i.female age, inflate(income i.female age i.parent i.religion)',
    'cmset id travelmode',
    'cmclogit chosen time, casevars(income partysize)',
    'cmmixlogit choice mfee, random(price) casevars(traffic)',
    'cmxtmixlogit choice trcost, random(trtime) casevars(age income)',
    'nlogit chosen cost distance rating || type: income kids',
):
    if needle not in semantics:
        fail(f"binary/ordinal/choice semantic contract missing: {needle}")

'''
v = once(v, anchor, checks + anchor, "discrete choice static contracts")
v = v.replace(
    'linear_catalog=1 summary_catalog=1',
    'linear_catalog=1 discrete_choice_catalog=1 summary_catalog=1',
)
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_DISCRETE_CHOICE_CATALOG_PATCH_OK")
