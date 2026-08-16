from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.6  16aug2026", "*! hxregistry 3.1.7  16aug2026", "registry version")
r = once(r, "factor pca canon cca manova discrim cluster svy lasso", "factor pca canon cca manova discrim cluster svyset svydescribe svy lasso", "survey catalog")
r = once(
    r,
    '    else if inlist(`"`method\'"\', "调查数据分析", "survey") local view "svy"\n',
    '    else if inlist(`"`method\'"\', "调查数据分析", "survey") local view "svyset svydescribe svy"\n',
    "survey method",
)
anchor = '        local key_sqrtlasso "sqrtlasso square root lasso 平方根 lasso 高维 变量选择"\n'
add = '''        local key_svyset "svyset survey design 调查数据 抽样设计 权重 分层 psu strata pweight"
        local key_svydescribe "svydescribe survey describe 调查数据 设计结构 分层 psu"
        local key_svy "svy survey prefix 调查数据 加权估计 复杂抽样"
'''
r = once(r, anchor, add + anchor, "survey search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")

sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.5  16aug2026", "*! hxsemantics 1.4.6  16aug2026", "semantics version")
s = once(s, " fmm irt svy bootstrap ", " fmm irt svyset svydescribe svy bootstrap ", "survey command-body catalog")
old = '''        else if "`cmd'" == "svy" {
            local expr_label "冒号后的估计命令（以 : 开头，如 : mean y）"
            local example1 "svy: mean y"
            local explain1 "在已 svyset 的调查设计下估计总体均值。"
            local example2 "svy: regress y x1 x2"
            local explain2 "在复杂抽样设计下运行线性回归。"
        }
'''
new = '''        else if "`cmd'" == "svyset" {
            local expr_label "PSU + sampling weight + strata()/fpc()/多阶段设计等声明"
            local example1 "svyset psu [pweight=finalwgt], strata(strata)"
            local explain1 "声明主抽样单元 psu、抽样权重 finalwgt 和分层变量 strata。"
            local example2 "svyset school_id, weight(wt_school) || _n, weight(wt_student)"
            local explain2 "多阶段调查可以逐层声明 sampling unit 和 stage-level weight。"
        }
        else if "`cmd'" == "svydescribe" {
            local expr_label "要检查的变量（可留空）+ 调查设计描述 options"
            local example1 "svydescribe"
            local explain1 "查看当前 svyset 设计中的 strata、PSU、权重与设计结构。"
            local example2 "svydescribe y"
            local explain2 "同时查看 y 在各 strata / stage 中的缺失与非缺失情况。"
        }
        else if "`cmd'" == "svy" {
            local expr_label "冒号后的估计命令（以 : 开头，如 : mean y）"
            local example1 "svy: mean weight"
            local explain1 "在已 svyset 的调查设计下估计总体均值并使用设计型标准误。"
            local example2 "svy: regress y x1 x2"
            local explain2 "在复杂抽样设计下运行线性回归。"
        }
'''
s = once(s, old, new, "survey semantics")
old_family = '''    else if "`cmd'" == "svy" {
        local title "svy — 调查数据估计"
        local purpose1 "用于复杂抽样设计下的加权估计和设计型标准误。"
        local purpose2 "应先用 svyset 正确声明抽样设计；本页执行的估计命令需与该设计保持一致。"
    }
'''
new_family = '''    else if "`cmd'" == "svyset" {
        local title "svyset — 声明调查抽样设计"
        local purpose1 "把抽样权重、PSU、strata、FPC 和多阶段 sampling units 写入数据的调查设计声明。"
        local purpose2 "这是 svy: 工作流的第一步；声明后用 svydescribe 检查，再运行 svy: 估计。"
    }
    else if "`cmd'" == "svydescribe" {
        local title "svydescribe — 检查调查设计结构"
        local purpose1 "检查当前 svyset 声明的分层、抽样单元、阶段和变量可用情况。"
        local purpose2 "适合在正式估计前确认 PSU/strata 结构和缺失情况。"
    }
    else if "`cmd'" == "svy" {
        local title "svy — 调查数据估计"
        local purpose1 "用于复杂抽样设计下的加权估计和设计型标准误。"
        local purpose2 "应先用 svyset 正确声明抽样设计；本页执行的估计命令需与该设计保持一致。"
    }
'''
s = once(s, old_family, new_family, "survey family copy")
sp.write_text(s, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'if "telasso" not in stats_cmds:\n    fail("official telasso treatment-effects command missing from Statistics catalog")\n'
extra = '''for survey_cmd in ("svyset", "svydescribe", "svy"):
    if survey_cmd not in stats_cmds:
        fail(f"survey workflow command missing: {survey_cmd}")
for needle in (
    'svyset psu [pweight=finalwgt], strata(strata)',
    'svydescribe',
    'svy: mean weight',
):
    if needle not in semantics:
        fail(f"survey workflow semantic contract missing: {needle}")
'''
v = once(v, anchor, anchor + extra, "survey static contracts")
v = v.replace(
    'causal_catalog=1 xthdid_panel=1 docs_source_split=1',
    'causal_catalog=1 xthdid_panel=1 survey_workflow=1 docs_source_split=1',
)
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_SURVEY_WORKFLOW_PATCH_OK")
