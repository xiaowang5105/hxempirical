from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.7  16aug2026", "*! hxregistry 3.1.8  16aug2026", "registry version")
r = once(
    r,
    "sem gsem fmm irt factor pca canon cca manova discrim cluster svyset",
    "sem gsem fmm irt alpha factor pca canon ca candisc hotelling manova mca mds mdslong mdsmat mvtest procrustes discrim cluster svyset",
    "multivariate catalog",
)
r = once(
    r,
    '    else if inlist(`"`method\'"\', "多元分析", "multivariate") local view "factor pca canon cca manova mvreg discrim cluster"\n',
    '    else if inlist(`"`method\'"\', "多元分析", "multivariate") local view "alpha factor pca canon ca candisc hotelling manova mvreg mca mds mdslong mdsmat mvtest procrustes discrim cluster"\n',
    "multivariate method",
)
anchor = '        local key_svyset "svyset survey design 调查数据 抽样设计 权重 分层 psu strata pweight"\n'
add = '''        local key_alpha "alpha cronbach reliability 量表 信度 克隆巴赫"
        local key_ca "ca correspondence analysis 对应分析 列联表"
        local key_candisc "candisc canonical discriminant analysis 典型 判别分析"
        local key_hotelling "hotelling t squared multivariate means 多元 均值 检验"
        local key_mca "mca multiple joint correspondence analysis 多重 联合 对应分析"
        local key_mds "mds multidimensional scaling 多维尺度 距离"
        local key_mdslong "mdslong multidimensional scaling long 多维尺度 长表 距离"
        local key_mdsmat "mdsmat multidimensional scaling matrix 多维尺度 矩阵 距离"
        local key_mvtest "mvtest multivariate test means covariance correlation normality 多元检验"
        local key_procrustes "procrustes transformation shape configuration 普鲁克拉斯 变换"
'''
r = once(r, anchor, add + anchor, "multivariate search keywords")
if " cca " in f" {r} ":
    raise SystemExit("obsolete/nonofficial cca token remains in registry")
rp.write_text(r, encoding="utf-8", newline="\n")

sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.6  16aug2026", "*! hxsemantics 1.4.7  16aug2026", "semantics version")
s = once(
    s,
    " cc cs ir sureg mvreg canon cca manova heckman ",
    " cc cs ir sureg mvreg canon ca candisc hotelling manova mca mds mdslong mdsmat mvtest procrustes heckman ",
    "multivariate command-body catalog",
)
old_multi = '''        else if strpos(" sureg mvreg canon cca manova ", " `cmd' ") {
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
'''
new_multi = '''        else if strpos(" sureg mvreg canon manova ", " `cmd' ") {
            local expr_label "多方程 / 多变量模型主体（含括号、等号或变量组）"
            if "`cmd'" == "sureg" {
                local example1 "sureg (y1 x1 x2) (y2 x1 x3)"
                local explain1 "每组括号表示一个方程。"
            }
            else {
                local example1 "help `cmd'"
                local explain1 "该模型包含多个结果或变量组，直接保留原生语法避免误判单一 Y/X 角色。"
            }
        }
        else if "`cmd'" == "ca" {
            local expr_label "行类别变量 + 列类别变量（可含 crossed variables）"
            local example1 "ca rowcat colcat"
            local explain1 "对 rowcat × colcat 列联表执行简单对应分析。"
            local example2 "help ca"
            local explain2 "crossed variables、normalization 和图形设定按研究任务继续核对。"
        }
        else if "`cmd'" == "candisc" {
            local expr_label "判别变量 + group() 已知组别"
            local example1 "candisc x1 x2 x3, group(group)"
            local explain1 "用 x1–x3 构造典型判别函数来区分已知 group。"
            local example2 "help candisc"
            local explain2 "组别变量和判别变量都属于核心输入。"
        }
        else if "`cmd'" == "hotelling" {
            local expr_label "多元变量 + by() 或 mu() 比较设定"
            local example1 "hotelling x1 x2, by(group)"
            local explain1 "比较两个 group 在 x1、x2 联合均值向量上的差异。"
            local example2 "help hotelling"
            local explain2 "单样本、配对或两组设定按当前 help 选择。"
        }
        else if "`cmd'" == "mca" {
            local expr_label "多个分类变量 + dimensions()/method() 等 MCA/JCA 设定"
            local example1 "mca q1 q2 q3"
            local explain1 "对 q1–q3 执行多重对应分析。"
            local example2 "help mca"
            local explain2 "维数和 joint correspondence 等设定按数据结构核对。"
        }
        else if "`cmd'" == "mds" {
            local expr_label "变量列表 + method()/measure()/dimensions() 等 MDS 设定"
            local example1 "mds x1 x2 x3"
            local explain1 "根据观测之间的多变量距离构造低维配置。"
            local example2 "help mds"
            local explain2 "metric/nonmetric、距离度量和维数是核心模型设定。"
        }
        else if "`cmd'" == "mdslong" {
            local expr_label "距离变量 + id() / pair identifiers + MDS 设定"
            local example1 "help mdslong"
            local explain1 "输入是对象两两距离的长表；先核对对象 ID 和距离变量角色。"
            local example2 "mdslong ..."
            local explain2 "页面保留原生命令主体，避免把 long-format proximity 数据误当普通 X 变量。"
        }
        else if "`cmd'" == "mdsmat" {
            local expr_label "距离 / 相异度矩阵名 + MDS 设定"
            local example1 "help mdsmat"
            local explain1 "输入核心是 Stata matrix，而非当前数据中的普通变量列表。"
            local example2 "mdsmat D"
            local explain2 "示意：对事先准备的相异度矩阵 D 做 MDS。"
        }
        else if "`cmd'" == "mvtest" {
            local expr_label "子命令 + 变量与检验设定（means/correlations/covariances/normality）"
            local example1 "mvtest normality x1 x2 x3"
            local explain1 "检验 x1–x3 的多元正态性。"
            local example2 "help mvtest"
            local explain2 "不同子命令的假设与参数结构不同，第一步先明确检验目标。"
        }
        else if "`cmd'" == "procrustes" {
            local expr_label "目标配置 + 来源配置 + transformation options"
            local example1 "help procrustes"
            local explain1 "Procrustes 比较两组多维配置；变量需要成对对应。"
            local example2 "procrustes ..."
            local explain2 "旋转、平移和缩放限制按比较目标设置。"
        }
'''
s = once(s, old_multi, new_multi, "multivariate command-body semantics")
# Alpha is simple enough for direct variable selection.
family_anchor = '''    else if strpos(" factor pca canon ca candisc hotelling manova mca mds mdslong mdsmat mvtest procrustes discrim cluster ", " `cmd' ") {
'''
# This exact expanded family does not exist yet; replace the older family block header instead.
s = once(
    s,
    '    else if strpos(" factor pca canon cca manova discrim cluster ", " `cmd\' ") {\n',
    '    else if strpos(" factor pca canon ca candisc hotelling manova mca mds mdslong mdsmat mvtest procrustes discrim cluster ", " `cmd\' ") {\n',
    "multivariate family header",
)
insert_marker = '    else if strpos(" factor pca canon ca candisc hotelling manova mca mds mdslong mdsmat mvtest procrustes discrim cluster ", " `cmd\' ") {\n'
alpha_block = '''    else if "`cmd'" == "alpha" {
        local title "alpha — Cronbach's alpha 量表信度"
        local purpose1 "评估多个题项的内部一致性，并可生成求和/标准化量表。"
        local purpose2 "直接选择属于同一量表的题项变量；反向题应先核对方向或使用相应 options。"
        local has_depvar 0
        local has_varlist 1
        local vars_label "同一量表的题项变量"
        local example1 "alpha item1-item10"
        local explain1 "计算 item1 到 item10 的 Cronbach's alpha。"
        local example2 "alpha item1-item10, item"
        local explain2 "同时查看删除各题项后的信度信息。"
    }
'''
if s.count(insert_marker) != 1:
    raise SystemExit(f"multivariate family marker count={s.count(insert_marker)}")
s = s.replace(insert_marker, alpha_block + insert_marker, 1)
if " cca " in f" {s} ":
    raise SystemExit("cca token remains in semantics")
sp.write_text(s, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''for survey_cmd in ("svyset", "svydescribe", "svy"):
    if survey_cmd not in stats_cmds:
        fail(f"survey workflow command missing: {survey_cmd}")
'''
extra = '''multivariate_core = {
    "alpha", "factor", "pca", "canon", "ca", "candisc", "hotelling", "manova", "mvreg",
    "mca", "mds", "mdslong", "mdsmat", "mvtest", "procrustes", "discrim", "cluster",
}
missing_mv = sorted(multivariate_core - stats_cmds)
if missing_mv:
    fail("multivariate core commands missing: " + ", ".join(missing_mv))
if "cca" in stats_cmds or re.search(r"(?<![A-Za-z0-9_])cca(?![A-Za-z0-9_])", registry):
    fail("nonofficial cca token leaked into official multivariate catalog")
for needle in (
    'alpha item1-item10',
    'candisc x1 x2 x3, group(group)',
    'mvtest normality x1 x2 x3',
):
    if needle not in semantics:
        fail(f"multivariate semantic contract missing: {needle}")
'''
v = once(v, anchor, anchor + extra, "multivariate static contracts")
v = v.replace(
    'survey_workflow=1 docs_source_split=1',
    'survey_workflow=1 multivariate_catalog=1 docs_source_split=1',
)
vp.write_text(v, encoding="utf-8", newline="\n")

print("HX_MULTIVARIATE_CATALOG_PATCH_OK")
