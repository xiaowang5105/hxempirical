from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.20  16aug2026", "*! hxregistry 3.1.21  16aug2026", "registry version")
r = once(r, " meta mi npregress kdensity lowess lpoly exlogistic ", " meta mi npregress nptrend kdensity lowess lpoly exlogistic ", "nptrend statistics catalog")
r = once(
    r,
    '    else if inlist(`"`method\'"\', "非参数分析", "nonparametric") local view "ranksum median signrank signtest npregress kdensity lowess lpoly"\n',
    '    else if inlist(`"`method\'"\', "非参数分析", "nonparametric") local view "ranksum median signrank signtest npregress nptrend kdensity lowess lpoly"\n',
    "nonparametric route",
)
keyword_anchor = '        local key_pkshape "pkshape pharmacokinetic Latin square crossover reshape 药代动力学 拉丁方 交叉设计 重塑"\n'
keyword_add = '''        local key_nptrend "nptrend nonparametric trend Cochran Armitage Jonckheere Terpstra Cuzick 趋势检验 非参数 有序组 exact"
'''
r = once(r, keyword_anchor, keyword_anchor + keyword_add, "nptrend search keyword")
rp.write_text(r, encoding="utf-8", newline="\n")


sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.19  16aug2026", "*! hxsemantics 1.4.20  16aug2026", "semantics version")
s = once(s, " telasso npregress ctset ", " telasso npregress nptrend ctset ", "nptrend command-body catalog")

old_np = '''        else if "`cmd'" == "npregress" {
            local expr_label "非参数方法 + 因变量 + 协变量（如 kernel y x1 x2 或 series y x1 x2）"
            local example1 "npregress kernel y x1 x2"
            local explain1 "kernel / series 是 npregress 的核心方法词，必须放在因变量之前。"
            local example2 "npregress series y x1 x2"
            local explain2 "使用 series 非参数回归。"
        }
'''
new_np = '''        else if "`cmd'" == "npregress" {
            local expr_label "非参数方法 + Y + X：kernel 或 series；series 还可用 asis()/nointeract() 施加半参数结构"
            local example1 "npregress kernel y x1 x2"
            local explain1 "kernel regression 通过核与带宽平滑估计 E(y|x1,x2)，适合低维连续/离散协变量。"
            local example2 "npregress series output taxlevel rainfall i.irrigate"
            local explain2 "series regression 用 spline/polynomial series 逼近未知响应面；asis() 可保留线性项，nointeract() 可限制可加结构。"
        }
        else if "`cmd'" == "nptrend" {
            local expr_label "响应变量 + 有序组变量 + trend-test 类型；Stata 17+ 支持 carmitage/jterpstra/linear/cuzick 与 exact"
            if c(stata_version) >= 17 {
                local example1 "nptrend relief, group(dose) carmitage"
                local explain1 "对二元 relief 检验其阳性比例是否随有序 dose 呈 Cochran–Armitage 线性趋势。"
                local example2 "nptrend exposure, group(group) jterpstra notable exact"
                local explain2 "用 Jonckheere–Terpstra 检验任意单调趋势，并通过 permutation 计算 exact p-value。"
            }
            else {
                local example1 "nptrend a, by(y)"
                local explain1 "Stata 16 及更早语法使用 rank-based trend test；a 为响应排序变量，y 给出有序组。"
                local example2 "help nptrend"
                local explain2 "Stata 17 才增加 Cochran–Armitage、Jonckheere–Terpstra、linear-by-linear 与 exact 选项。"
            }
        }
'''
s = once(s, old_np, new_np, "nonparametric specialized semantics")
s = once(
    s,
    '    else if strpos(" npregress lowess lpoly ", " `cmd\' ") {\n',
    '    else if strpos(" npregress nptrend lowess lpoly ", " `cmd\' ") {\n',
    "nonparametric family copy",
)
s = once(
    s,
    '        local purpose1 "用于非参数回归或局部平滑，减少对函数形式的强假设。"\n',
    '        local purpose1 "用于 kernel/series 非参数回归、跨有序组趋势检验或局部平滑，减少对函数形式和分布的强假设。"\n',
    "nonparametric family purpose",
)
sp.write_text(s, encoding="utf-8", newline="\n")


vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'dsge_core = {"dsge", "dsgenl"}\n'
checks = '''if "nptrend" not in stats_cmds:
    fail("nptrend missing from nonparametric Statistics coverage")
for needle in (
    "npregress kernel y x1 x2",
    "npregress series output taxlevel rainfall i.irrigate",
    "nptrend relief, group(dose) carmitage",
    "nptrend exposure, group(group) jterpstra notable exact",
    "nptrend a, by(y)",
):
    if needle not in semantics:
        fail(f"nonparametric semantic contract missing: {needle}")
if 'if c(stata_version) >= 17 {' not in semantics:
    fail("nptrend version-aware semantic branch missing")

'''
v = once(v, anchor, checks + anchor, "nonparametric static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_NONPARAMETRIC_QUALITY_PATCH_OK")
