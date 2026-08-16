from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.30  16aug2026", "*! hxregistry 3.1.31  16aug2026", "registry version")
r = once(
    r,
    'local data_cmds "use import export save describe codebook isid duplicates misstable generate egen replace recode rename order label format compress encode decode destring tostring winsor2 keep drop merge append joinby reshape collapse sort gsort xtset tsset"',
    'local data_cmds "use import export save describe codebook isid assert count compare duplicates misstable generate egen replace recode clonevar split rename order label format compress encode decode destring tostring winsor2 keep drop expand merge append joinby cross reshape collapse contract fillin stack xpose sort gsort xtset tsset frame frames frlink frget"',
    "expanded data command catalog",
)
r = once(r, 'else if inlist(`"`method\'"\', "数据检查", "data_check") local view "describe codebook isid duplicates misstable"', 'else if inlist(`"`method\'"\', "数据检查", "data_check") local view "describe codebook isid assert count compare duplicates misstable"', "data check route")
r = once(r, 'else if inlist(`"`method\'"\', "变量处理", "variable_processing") local view "generate egen replace recode rename order label format compress encode decode destring tostring winsor2"', 'else if inlist(`"`method\'"\', "变量处理", "variable_processing") local view "generate egen replace recode clonevar split rename order label format compress encode decode destring tostring winsor2"', "variable processing route")
r = once(r, 'else if inlist(`"`method\'"\', "样本处理", "sample_processing") local view "keep drop"', 'else if inlist(`"`method\'"\', "样本处理", "sample_processing") local view "keep drop expand"', "sample processing route")
r = once(r, 'else if inlist(`"`method\'"\', "合并与追加", "merge_append") local view "merge append joinby"', 'else if inlist(`"`method\'"\', "合并与追加", "merge_append") local view "merge append joinby cross frlink frget"', "combine route")
r = once(r, 'else if inlist(`"`method\'"\', "数据结构", "data_structure") local view "reshape collapse sort gsort xtset tsset"', 'else if inlist(`"`method\'"\', "数据结构", "data_structure") local view "reshape collapse contract fillin stack xpose sort gsort xtset tsset frame frames"', "structure route")
anchor = '        local key_describe "describe data variables 数据 描述 变量 类型"\n'
keywords = '''        local key_assert "assert validate condition 数据 验证 条件 断言"
        local key_count "count observations sample 样本 观测数 计数"
        local key_compare "compare variables values 变量 比较 差异"
        local key_clonevar "clonevar copy variable 克隆 复制 变量"
        local key_split "split string parse 字符串 拆分 分列"
        local key_expand "expand duplicate observations 扩展 复制 样本 观测"
        local key_cross "cross Cartesian datasets 笛卡尔积 数据 组合"
        local key_contract "contract frequency dataset 频数 汇总 数据重组"
        local key_fillin "fillin rectangularize combinations 补齐 组合 面板"
        local key_stack "stack variables reshape 堆叠 变量 数据重组"
        local key_xpose "xpose transpose rows columns 转置 行列"
        local key_frame "frame multiple datasets 多数据集 内存 frame"
        local key_frames "frames dir save use 多数据集 frameset"
        local key_frlink "frlink link frames 连接 frame 多数据集"
        local key_frget "frget copy linked frame variables 复制 frame 变量"
'''
r = once(r, anchor, keywords + anchor, "data expansion search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")

sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.26  16aug2026", "*! hxsemantics 1.4.27  16aug2026", "semantics version")
marker = '''    else if "`cmd'" == "generate" {
'''
blocks = '''    else if "`cmd'" == "assert" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "assert — 验证数据条件"
        local purpose1 "检查所有指定观测是否满足逻辑条件；只要有一条不满足，Stata 就会报错。"
        local purpose2 "适合在清洗流程中锁定取值范围、唯一逻辑和业务规则。"
        local expr_label "必须成立的条件 + if/in（例如 sales >= 0 if !missing(sales)）"
        local example1 "assert sales >= 0 if !missing(sales)"
        local explain1 "确认所有非缺失 sales 都不小于 0。"
        local example2 "assert inrange(year, 2000, 2026)"
        local explain2 "确认 year 全部位于指定范围内。"
        local show_advanced 0
    }
    else if "`cmd'" == "count" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "count — 统计观测数"
        local purpose1 "计算当前数据或指定条件下有多少条观测。"
        local purpose2 "常用于清洗前后核对样本量，或检查某类样本是否存在。"
        local expr_label "if/in 条件（全部样本可留空）"
        local example1 "count"
        local explain1 "统计当前数据中的全部观测数。"
        local example2 "count if treated == 1"
        local explain2 "统计 treated=1 的观测数。"
        local show_advanced 0
    }
    else if "`cmd'" == "compare" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "compare — 比较两个变量"
        local purpose1 "逐观测比较两个变量，并汇总相等、大小关系和缺失组合。"
        local purpose2 "适合核对旧变量与新变量、原始字段与清洗字段是否一致。"
        local expr_label "两个要比较的变量（例如 sales sales_clean）"
        local example1 "compare sales sales_clean"
        local explain1 "汇总 sales 与 sales_clean 的逐观测差异。"
        local example2 "compare id_old id_new"
        local explain2 "检查两个 ID 字段的匹配关系。"
        local show_advanced 0
    }
    else if "`cmd'" == "clonevar" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "clonevar — 完整复制变量"
        local purpose1 "复制变量的值及其存储类型、格式、变量标签和值标签。"
        local purpose2 "适合修改变量前创建可追溯备份。"
        local expr_label "新变量 = 原变量（例如 sales_backup = sales）"
        local example1 "clonevar sales_backup = sales"
        local explain1 "完整复制 sales 为 sales_backup。"
        local example2 "clonevar industry_raw = industry"
        local explain2 "在重编码前保留 industry 的原始版本。"
        local show_advanced 0
    }
    else if "`cmd'" == "split" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "split — 拆分字符串变量"
        local purpose1 "按分隔符把一个字符串变量拆成多个新变量。"
        local purpose2 "先检查分隔符是否稳定；生成变量数量由每条字符串的最大分段数决定。"
        local expr_label "字符串变量 + parse()/generate() 等（例如 fullname, parse(\" \" ) gen(namepart)）"
        local example1 "split fullname, parse(\" \" ) gen(namepart)"
        local explain1 "按空格拆分 fullname，并生成 namepart1、namepart2 等变量。"
        local example2 "split code, parse(\"-\")"
        local explain2 "按连字符拆分 code。"
        local show_advanced 1
    }
    else if "`cmd'" == "expand" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "expand — 复制观测"
        local purpose1 "按照固定次数或变量给出的次数复制每条观测。"
        local purpose2 "会直接增加当前数据行数；运行前先核对复制规则和预期样本量。"
        local expr_label "复制次数/变量 + generate()（例如 2, generate(copy)）"
        local example1 "expand 2, generate(copy)"
        local explain1 "每条观测变成两条，并用 copy 标记新增副本。"
        local example2 "expand n_copies"
        local explain2 "按每条观测的 n_copies 值决定复制次数。"
        local show_advanced 1
    }
    else if "`cmd'" == "cross" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "cross — 两张数据做笛卡尔组合"
        local purpose1 "把当前数据的每条观测与 using 数据的每条观测两两组合。"
        local purpose2 "结果行数约等于两表行数乘积，可能迅速膨胀；只有研究设计确实需要全组合时使用。"
        local expr_label "using 文件（例如 using products.dta）"
        local example1 "cross using products.dta"
        local explain1 "把当前每条观测与 products.dta 中每条观测组合。"
        local example2 "help cross"
        local explain2 "运行前先核对两张表的行数和预计组合规模。"
        local show_advanced 0
    }
    else if "`cmd'" == "contract" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "contract — 把明细数据压缩为频数表"
        local purpose1 "按一个或多个变量的组合生成唯一行，并记录频数或比例。"
        local purpose2 "contract 会用汇总后的频数数据替换当前明细数据；正式运行前先保存或 preserve。"
        local expr_label "分组变量 + freq()/percent() 等（例如 industry year, freq(n)）"
        local example1 "contract industry year, freq(n)"
        local explain1 "每个 industry-year 组合保留一行，并生成频数 n。"
        local example2 "contract group, percent(pct)"
        local explain2 "按 group 汇总并生成百分比变量 pct。"
        local show_advanced 1
    }
    else if "`cmd'" == "fillin" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "fillin — 补齐变量组合"
        local purpose1 "为指定变量实际出现过的取值补齐缺少的组合，并生成 _fillin 标记。"
        local purpose2 "常用于把非平衡组合补成矩形结构；新增行中的其他变量通常为缺失值。"
        local expr_label "要补齐组合的变量（例如 firm year）"
        local example1 "fillin firm year"
        local explain1 "补齐 firm 与 year 的取值组合，并用 _fillin 标记新增行。"
        local example2 "fillin region product year"
        local explain2 "补齐 region-product-year 组合。"
        local show_advanced 0
    }
    else if "`cmd'" == "stack" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "stack — 把变量组纵向堆叠"
        local purpose1 "把多组变量纵向堆成统一列，用于把重复结构整理成长格式。"
        local purpose2 "stack 的变量组和 into() 必须一一对应；复杂结构运行前先查看 Stata Help 示例。"
        local expr_label "变量组 + into()/clear 等原生 stack 主体"
        local example1 "help stack"
        local explain1 "先按当前 Stata 版本确认变量组与 into() 的对应写法。"
        local example2 "reshape long"
        local explain2 "若变量名具有规则 stub-year 结构，通常优先考虑 reshape long。"
        local show_advanced 1
    }
    else if "`cmd'" == "xpose" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "xpose — 转置观测与变量"
        local purpose1 "把数据的行和列互换，适合矩阵型小数据或特殊整理任务。"
        local purpose2 "xpose 会重构整个数据集，变量名和类型可能发生变化；运行前先保存原数据。"
        local expr_label "xpose 选项（通常使用 , clear；可加 varname）"
        local example1 "xpose, clear"
        local explain1 "把当前数据行列互换，并替换内存数据。"
        local example2 "xpose, clear varname"
        local explain2 "转置时同时保留原变量名信息。"
        local show_advanced 1
    }
    else if "`cmd'" == "frame" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "frame — 管理内存中的多个数据集"
        local purpose1 "创建、切换、复制、删除或在指定 frame 中运行命令。"
        local purpose2 "frame 让多个 .dta 同时留在内存中，适合主表、映射表和临时结果并行工作。"
        local expr_label "frame 子命令与参数（如 create lookup / change lookup / drop lookup）"
        local example1 "frame create lookup"
        local explain1 "创建名为 lookup 的空 frame。"
        local example2 "frame change lookup"
        local explain2 "切换到 lookup frame。"
        local show_advanced 1
    }
    else if "`cmd'" == "frames" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "frames — 查看和管理 Frames 集合"
        local purpose1 "列出当前 frames，并在支持的版本中保存、载入或描述 frameset。"
        local purpose2 "基础 frame 操作用 frame；frames 更适合查看集合和管理多个 frame。"
        local expr_label "frames 子命令与参数（如 dir / describe / save / use）"
        local example1 "frames dir"
        local explain1 "列出当前内存中的所有 frame。"
        local example2 "frames describe"
        local explain2 "查看当前 frames 的结构信息。"
        local show_advanced 1
    }
    else if "`cmd'" == "frlink" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "frlink — 按键连接两个 Frame"
        local purpose1 "在当前 frame 与另一个 frame 之间建立 1:1、m:1 等链接关系。"
        local purpose2 "链接前先用 isid 检查目标 frame 的键唯一性；frlink 不会像 merge 那样复制全部变量。"
        local expr_label "关系 + 键变量 + frame()（例如 m:1 countyid, frame(counties)）"
        local example1 "frlink m:1 countyid, frame(counties)"
        local explain1 "把当前数据按 countyid 链接到 counties frame。"
        local example2 "frlink 1:1 state, frame(census)"
        local explain2 "按 state 建立一对一 frame 链接。"
        local show_advanced 1
    }
    else if "`cmd'" == "frget" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local title "frget — 从已链接 Frame 复制变量"
        local purpose1 "在 frlink 建立链接后，把另一个 frame 的指定变量复制到当前 frame。"
        local purpose2 "变量会真正复制到当前数据；若只需要动态引用且版本支持，可另考虑 frame alias。"
        local expr_label "变量列表 + from()（例如 med_income, from(counties)）"
        local example1 "frget med_income, from(counties)"
        local explain1 "从已链接的 counties frame 复制 med_income。"
        local example2 "frget x1 x2, from(lookup)"
        local explain2 "从 lookup frame 一次复制两个变量。"
        local show_advanced 1
    }
    else if "`cmd'" == "generate" {
'''
s = once(s, marker, blocks, "data validation/reorganization semantics")
sp.write_text(s, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor2 = 'for native_io in ("use", "import", "export", "save"):\n    if f\'local title "{native_io} —\' not in semantics:\n        fail(f"native Data I/O semantics missing: {native_io}")\n'
checks = '''data_validation_reorg = {"assert", "count", "compare", "clonevar", "split", "expand", "cross", "contract", "fillin", "stack", "xpose", "frame", "frames", "frlink", "frget"}
missing_data_validation_reorg = sorted(data_validation_reorg - data_cmds)
if missing_data_validation_reorg:
    fail("data validation/reorganization commands missing: " + ", ".join(missing_data_validation_reorg))
for data_cmd in sorted(data_validation_reorg):
    if f'local title "{data_cmd} —' not in semantics:
        fail(f"data validation/reorganization semantics missing: {data_cmd}")
'''
v = once(v, anchor2, anchor2 + checks, "data validation/reorg static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_DATA_VALIDATION_REORG_PATCH_OK")
