from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


# ---------- registry ----------
rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.18  16aug2026", "*! hxregistry 3.1.19  16aug2026", "registry version")
r = once(r, " sem gsem fmm irt alpha factor ", " sem gsem fmm irt irtgraph diflogistic difmh alpha factor ", "IRT catalog")
r = once(
    r,
    '    else if inlist(`"`method\'"\', "项目反应理论(IRT)", "irt") local view "irt"\n',
    '    else if inlist(`"`method\'"\', "项目反应理论(IRT)", "irt") local view "irt irtgraph diflogistic difmh"\n',
    "IRT method route",
)
keyword_anchor = '        local key_vecrank "vecrank Johansen cointegration rank 协整秩 检验"\n'
keyword_add = '''        local key_irtgraph "irtgraph ICC TCC IIF TIF item characteristic information 项目反应 图形 信息函数 特征曲线"
        local key_diflogistic "diflogistic IRT differential item functioning logistic DIF 差异项目功能 逻辑回归"
        local key_difmh "difmh IRT Mantel Haenszel DIF differential item functioning 差异项目功能"
'''
r = once(r, keyword_anchor, keyword_anchor + keyword_add, "IRT search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")


# ---------- semantics ----------
sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.17  16aug2026", "*! hxsemantics 1.4.18  16aug2026", "semantics version")
s = once(s, " sem gsem mi meta fmm irt svyset ", " sem gsem mi meta fmm irt irtgraph diflogistic difmh svyset ", "IRT command-body catalog")

old_irt = '''        else if "`cmd'" == "irt" {
            local expr_label "IRT 模型 + 题项变量（如 2pl item1-item10）"
            local example1 "irt 2pl item1-item10"
            local explain1 "拟合二参数 Logistic IRT 模型。"
            local example2 "irt grm item1-item10"
            local explain2 "拟合 graded response model。"
        }
'''
new_irt = '''        else if "`cmd'" == "irt" {
            local expr_label "IRT 模型类型 + 题项变量 + group()/constraints 等（1pl / 2pl / 3pl / grm / pcm / rsm / nrm / hybrid）"
            local example1 "irt 2pl item1-item10"
            local explain1 "二元题项拟合 2PL：每个 item 可有不同 difficulty 和 discrimination。"
            local example2 "irt grm item1-item10, group(urban)"
            local explain2 "有序题项拟合 graded-response model，并用 group() 做多组 IRT / DIF 分析。"
        }
        else if "`cmd'" == "irtgraph" {
            local expr_label "图形类型 icc/tcc/iif/tif + item()/at()/by() 等图形参数"
            local example1 "irtgraph icc"
            local explain1 "绘制上一项 IRT 模型的 item characteristic curves。"
            local example2 "irtgraph tif"
            local explain2 "绘制 test information function，查看量表在哪些 latent-trait 区间提供最多信息。"
        }
        else if "`cmd'" == "diflogistic" {
            local expr_label "题项变量 + group() + ability() 等 logistic-regression DIF 设定"
            local example1 "help diflogistic"
            local explain1 "使用 logistic regression 检验 uniform / nonuniform differential item functioning；先按当前 help 指定 group 与 ability 变量。"
            local example2 "irt 2pl item1-item10, group(urban)"
            local explain2 "DIF 结果应与多组 IRT 的 item 参数差异一起判断。"
        }
        else if "`cmd'" == "difmh" {
            local expr_label "题项变量 + group() + score() 等 Mantel–Haenszel DIF 设定"
            local example1 "help difmh"
            local explain1 "使用 Mantel–Haenszel 方法检查二元题项的 DIF；分组变量与匹配 score 必须按 help 明确指定。"
            local example2 "irtgraph icc"
            local explain2 "统计检验后可用 ICC 进一步查看题项在 latent trait 上的组间差异。"
        }
'''
s = once(s, old_irt, new_irt, "IRT specialized semantics")

old_fmm = '''        else if "`cmd'" == "fmm" {
            local expr_label "类别数 + 冒号后的估计命令（如 2: regress y x1 x2）"
            local example1 "fmm 2: regress y x1 x2"
            local explain1 "拟合两类有限混合线性回归。"
            local example2 "fmm 3: poisson y x1 x2"
            local explain2 "拟合三类有限混合 Poisson 模型。"
        }
'''
new_fmm = '''        else if "`cmd'" == "fmm" {
            local expr_label "类别数 + lcprob() class-membership 模型 + 冒号后的基础估计命令"
            local example1 "fmm 2: regress y x1 x2"
            local explain1 "拟合两类有限混合线性回归；类别数位于冒号前。"
            local example2 "fmm 2, lcprob(z1 z2): poisson y x1 x2"
            local explain2 "两类 Poisson mixture，并让 z1、z2 通过 multinomial-logit class model 解释潜在类别归属。"
        }
'''
s = once(s, old_fmm, new_fmm, "FMM class-membership semantics")

# Improve family-level IRT copy.
old_family = '''    else if "`cmd'" == "irt" {
        local title "irt — 项目反应理论"
'''
new_family = '''    else if strpos(" irt irtgraph diflogistic difmh ", " `cmd' ") {
        local title "`cmd' — 项目反应理论"
'''
s = once(s, old_family, new_family, "IRT family copy")
s = once(
    s,
    '        local purpose1 "用于估计题项难度、区分度和潜在能力 / 特质之间的关系。"\n',
    '        local purpose1 "用于估计 IRT 模型、绘制 item/test characteristic 与 information curves，并检查 differential item functioning。"\n',
    "IRT family purpose",
)
sp.write_text(s, encoding="utf-8", newline="\n")


# ---------- permanent static contracts ----------
vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'survival_workflow_core = {\n'
checks = '''irt_core = {"irt", "irtgraph", "diflogistic", "difmh"}
missing_irt = sorted(irt_core - stats_cmds)
if missing_irt:
    fail("IRT command coverage missing: " + ", ".join(missing_irt))
for needle in (
    "irt 2pl item1-item10",
    "irt grm item1-item10, group(urban)",
    "irtgraph icc",
    "irtgraph tif",
    "fmm 2, lcprob(z1 z2): poisson y x1 x2",
    "gsem (alcohol truant weapon theft vandalism <-), logit lclass(C 3)",
):
    if needle not in semantics:
        fail(f"latent/IRT semantic contract missing: {needle}")
# SEM/LCA/FMM are intentionally represented by their real Stata entry points.
for fake in ("lca", "latentclass"):
    if fake in stats_cmds:
        fail(f"fake latent-class command leaked into catalog: {fake}")

'''
v = once(v, anchor, checks + anchor, "IRT latent-model static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_IRT_SEM_QUALITY_PATCH_OK")
