from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.27  16aug2026", "*! hxregistry 3.1.28  16aug2026", "registry version")
old_data = 'local data_cmds "hxconvert generate replace keep drop merge append reshape collapse xtset tsset encode decode destring tostring winsor2 duplicates misstable"'
new_data = 'local data_cmds "hxconvert describe codebook isid duplicates misstable generate egen replace recode rename order label format compress encode decode destring tostring winsor2 keep drop merge append joinby reshape collapse sort gsort xtset tsset"'
r = once(r, old_data, new_data, "data command catalog")
r = once(r, 'else if inlist(`"`method\'"\', "数据检查", "data_check") local view "misstable duplicates"', 'else if inlist(`"`method\'"\', "数据检查", "data_check") local view "describe codebook isid duplicates misstable"', "data-check route")
r = once(r, 'else if inlist(`"`method\'"\', "变量处理", "variable_processing") local view "generate replace encode decode destring tostring winsor2"', 'else if inlist(`"`method\'"\', "变量处理", "variable_processing") local view "generate egen replace recode rename order label format compress encode decode destring tostring winsor2"', "variable-processing route")
r = once(r, 'else if inlist(`"`method\'"\', "合并与追加", "merge_append") local view "merge append"', 'else if inlist(`"`method\'"\', "合并与追加", "merge_append") local view "merge append joinby"', "merge-append route")
r = once(r, 'else if inlist(`"`method\'"\', "数据结构", "data_structure") local view "reshape collapse xtset tsset"', 'else if inlist(`"`method\'"\', "数据结构", "data_structure") local view "reshape collapse sort gsort xtset tsset"', "data-structure route")
anchor = '        local key_destring "destring 字符串 转 数值"\n'
keywords = '''        local key_describe "describe data variables 数据 描述 变量 类型"
        local key_codebook "codebook data variables 数据 字典 取值 缺失 标签"
        local key_isid "isid unique identifier key 唯一键 主键 合并 检查"
        local key_egen "egen extended generate group rowmean total 扩展生成 分组 行均值"
        local key_recode "recode category bins 分类 重编码 分箱"
        local key_rename "rename variable 变量 重命名"
        local key_order "order variables columns 变量 列 顺序"
        local key_label "label variable value labels 标签 变量标签 值标签"
        local key_format "format display numeric date 显示格式 数值 日期"
        local key_compress "compress storage memory 压缩 存储 内存"
        local key_sort "sort ascending 排序 升序"
        local key_gsort "gsort descending ascending 排序 降序 升序"
        local key_joinby "joinby merge pairwise groups 连接 多对多 组合"
'''
r = once(r, anchor, keywords + anchor, "data search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")

sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.23  16aug2026", "*! hxsemantics 1.4.24  16aug2026", "semantics version")
marker = '''    else if "`cmd'" == "replace" {
'''
if s.count(marker) != 1:
    raise SystemExit(f"data semantics insertion marker count={s.count(marker)}")
blocks = '''    else if "`cmd'" == "describe" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "变量列表（可留空查看全部；例如 firm year sales）"
        local title "describe — 查看变量结构"
        local purpose1 "快速查看变量名、类型、显示格式、变量标签和数据规模。"
        local purpose2 "建议在合并、类型转换或回归前先用 describe 确认变量结构。"
        local example1 "describe"
        local explain1 "查看当前数据中全部变量的结构信息。"
        local example2 "describe firm year sales"
        local explain2 "只检查 firm、year、sales 三个变量。"
        local show_advanced 0
    }
    else if "`cmd'" == "codebook" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "要检查的变量（可留空查看全部）"
        local title "codebook — 检查变量取值与数据质量"
        local purpose1 "查看变量类型、标签、唯一值、缺失值以及取值范围等信息。"
        local purpose2 "适合在正式清洗前理解变量编码和异常取值。"
        local example1 "codebook industry"
        local explain1 "查看 industry 的编码、标签、唯一值和缺失情况。"
        local example2 "codebook firm year"
        local explain2 "同时检查企业标识和年份变量。"
        local show_advanced 1
    }
    else if "`cmd'" == "isid" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "应当唯一的键变量（例如 firm year）"
        local title "isid — 检查唯一键"
        local purpose1 "检验一个或多个变量能否唯一识别每条观测。"
        local purpose2 "在 merge、reshape 或面板数据处理前检查 firm-year 等键尤其重要。"
        local example1 "isid firm year"
        local explain1 "检查每个 firm-year 是否只有一条观测。"
        local example2 "isid id, sort"
        local explain2 "检查 id 唯一，并按 id 排序。"
        local show_advanced 1
    }
    else if "`cmd'" == "egen" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "新变量 = egen 函数（例如 firm_id = group(firm)）"
        local title "egen — 扩展生成变量"
        local purpose1 "用于 group()、rowmean()、total()、mean() 等跨变量或分组计算。"
        local purpose2 "需要分组计算时可在命令主体前使用 bysort；函数参数按 Stata egen 语法填写。"
        local example1 "egen firm_id = group(firm)"
        local explain1 "把企业标识转换为连续的数值组编号。"
        local example2 "bysort firm: egen mean_sales = mean(sales)"
        local explain2 "为每家企业计算 sales 的组内均值。"
        local show_advanced 1
    }
    else if "`cmd'" == "recode" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "变量 + 重编码规则（例如 age (0/17=1) (18/64=2) (65/max=3), gen(agegrp)）"
        local title "recode — 重编码或分组"
        local purpose1 "把连续或类别变量按区间/旧值重新编码，可生成新变量或覆盖原变量。"
        local purpose2 "重编码规则会直接改变数据含义；运行前检查区间边界和遗漏值。"
        local example1 "recode age (0/17=1) (18/64=2) (65/max=3), gen(agegrp)"
        local explain1 "按年龄区间生成三组 agegrp，同时保留原 age。"
        local example2 "recode status (9=.)"
        local explain2 "把 status 中编码为 9 的特殊缺失码改为 Stata 缺失值。"
        local show_advanced 1
    }
    else if "`cmd'" == "rename" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "旧变量名 新变量名（或 rename group 语法）"
        local title "rename — 重命名变量"
        local purpose1 "修改变量名，不改变变量取值。"
        local purpose2 "合并数据前可先统一键变量和字段命名；批量重命名按 Stata rename group 语法填写。"
        local example1 "rename oldname newname"
        local explain1 "把 oldname 改名为 newname。"
        local example2 "rename (sales2019 sales2020) (sales19 sales20)"
        local explain2 "一次重命名多个变量。"
        local show_advanced 0
    }
    else if "`cmd'" == "order" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "要移动的变量及 after()/before()/first/last 选项"
        local title "order — 调整变量列顺序"
        local purpose1 "重新排列变量在数据表中的列位置，不改变观测值。"
        local purpose2 "适合把 id、year、核心变量放到数据表前部，便于检查和导出。"
        local example1 "order firm year, first"
        local explain1 "把 firm 和 year 移到最前面。"
        local example2 "order treatment, after(year)"
        local explain2 "把 treatment 移到 year 后面。"
        local show_advanced 0
    }
    else if "`cmd'" == "label" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "label 子命令主体（如 variable sales \"Sales revenue\"）"
        local title "label — 管理变量标签和值标签"
        local purpose1 "给变量增加可读说明，或定义/绑定分类变量的 value label。"
        local purpose2 "label 是一组子命令；页面保留原生主体，避免把 variable/define/values 混成同一参数。"
        local example1 "label variable sales \"Sales revenue\""
        local explain1 "为 sales 设置变量标签。"
        local example2 "label define yesno 0 \"No\" 1 \"Yes\""
        local explain2 "定义名为 yesno 的值标签。"
        local show_advanced 1
    }
    else if "`cmd'" == "format" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "变量 + 显示格式（例如 date %td）"
        local title "format — 设置显示格式"
        local purpose1 "控制数值、日期和字符串在 Stata 中如何显示，不改变底层数值。"
        local purpose2 "日期变量常需要 %td/%tm/%tq 等格式；格式设置不会完成日期值本身的转换。"
        local example1 "format date %td"
        local explain1 "把数值日期 date 按日历日期显示。"
        local example2 "format sales %12.2fc"
        local explain2 "以两位小数和千位分隔形式显示 sales。"
        local show_advanced 0
    }
    else if "`cmd'" == "compress" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "变量列表（通常留空，压缩整个数据集）"
        local title "compress — 无损缩小数据存储"
        local purpose1 "在不损失当前数据精度的前提下，把变量改成足够容纳其取值的较小存储类型。"
        local purpose2 "适合大数据处理前节省内存；运行后可用 describe 检查存储类型变化。"
        local example1 "compress"
        local explain1 "尝试无损压缩当前数据集中的所有变量。"
        local example2 "compress x1 x2"
        local explain2 "只检查并压缩 x1、x2。"
        local show_advanced 0
    }
    else if "`cmd'" == "sort" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "排序键（例如 firm year）"
        local title "sort — 按变量升序排序"
        local purpose1 "按一个或多个变量从小到大排列观测。"
        local purpose2 "分组运算、人工检查和部分 by: 工作流会依赖当前排序。"
        local example1 "sort firm year"
        local explain1 "先按 firm，再在企业内按 year 升序排列。"
        local example2 "sort year firm"
        local explain2 "先按年份，再在年份内按企业排列。"
        local show_advanced 0
    }
    else if "`cmd'" == "gsort" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "+/- 排序键（例如 firm -sales）"
        local title "gsort — 混合升序和降序排序"
        local purpose1 "允许不同排序键分别使用升序或降序。"
        local purpose2 "+ 表示升序，- 表示降序；适合企业内按指标从高到低排列。"
        local example1 "gsort firm -sales"
        local explain1 "firm 升序，同一企业内 sales 从高到低。"
        local example2 "gsort -year firm"
        local explain2 "年份从新到旧，再按 firm 升序。"
        local show_advanced 0
    }
    else if "`cmd'" == "joinby" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "键变量 using 文件（例如 industry year using policy.dta）"
        local title "joinby — 按组生成两表组合"
        local purpose1 "对主表与 using 表中具有相同键值的观测生成组内两两组合。"
        local purpose2 "结果行数可能快速膨胀；普通 1:1、m:1、1:m 数据连接优先使用 merge。"
        local example1 "joinby industry year using policy.dta"
        local explain1 "对相同 industry-year 的主表与副表观测生成全部配对组合。"
        local example2 "help joinby"
        local explain2 "运行前确认多对多组合确实符合研究设计，并预估组合后的观测数量。"
        local show_advanced 1
    }
'''
s = s.replace(marker, blocks + marker, 1)
sp.write_text(s, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'stats_cmds = set(local_words(registry, "stats_cmds"))\n'
checks = '''data_cmds = set(local_words(registry, "data_cmds"))
core_data_management = {"describe", "codebook", "isid", "egen", "recode", "rename", "order", "label", "format", "compress", "sort", "gsort", "joinby"}
missing_core_data = sorted(core_data_management - data_cmds)
if missing_core_data:
    fail("core data-management commands missing: " + ", ".join(missing_core_data))
for needle in (
    'isid firm year',
    'egen firm_id = group(firm)',
    'recode age (0/17=1) (18/64=2) (65/max=3), gen(agegrp)',
    'rename oldname newname',
    'order firm year, first',
    'compress — 无损缩小数据存储',
    'gsort firm -sales',
    'joinby industry year using policy.dta',
):
    if needle not in semantics:
        fail(f"core data-management semantic contract missing: {needle}")

'''
v = once(v, anchor, checks + anchor, "core data static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_CORE_DATA_MANAGEMENT_PATCH_OK")
