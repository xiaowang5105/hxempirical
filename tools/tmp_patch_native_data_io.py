from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.29  16aug2026", "*! hxregistry 3.1.30  16aug2026", "registry version")
r = once(
    r,
    'local data_cmds "hxconvert describe codebook isid duplicates misstable generate egen replace recode rename order label format compress encode decode destring tostring winsor2 keep drop merge append joinby reshape collapse sort gsort xtset tsset"',
    'local data_cmds "use import export save describe codebook isid duplicates misstable generate egen replace recode rename order label format compress encode decode destring tostring winsor2 keep drop merge append joinby reshape collapse sort gsort xtset tsset"',
    "native data command catalog",
)
r = once(r, '    /* Data/HX compatibility paths. */\n    if inlist(`"`method\'"\', "导入与转换", "import_convert") local view "hxconvert"', '    /* Stata Data menu paths. HX-only conversion stays in Workflow. */\n    if inlist(`"`method\'"\', "导入与转换", "import_convert") local view "use import export save"', "native import route")
anchor = '        local key_describe "describe data variables 数据 描述 变量 类型"\n'
keywords = '''        local key_use "use dta dataset open load 数据 打开 载入"
        local key_import "import excel delimited sas spss data 导入 Excel CSV SAS SPSS 数据"
        local key_export "export excel delimited data 导出 Excel CSV 数据"
        local key_save "save dta dataset replace 数据 保存 覆盖"
'''
r = once(r, anchor, keywords + anchor, "native data I/O search keywords")
rp.write_text(r, encoding="utf-8", newline="\n")

sp = Path("hxsemantics.ado")
s = sp.read_text(encoding="utf-8")
s = once(s, "*! hxsemantics 1.4.25  16aug2026", "*! hxsemantics 1.4.26  16aug2026", "semantics version")
marker = '''    if "`cmd'" == "generate" {
'''
blocks = '''    if "`cmd'" == "use" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_if 0
        local has_in 0
        local has_weight 0
        local has_using 0
        local has_newvar 0
        local has_expression 1
        local show_advanced 0
        local title "use — 打开 Stata 数据文件"
        local purpose1 "把 .dta 文件载入当前内存，作为后续清洗和分析的数据。"
        local purpose2 "当前内存已有未保存修改时，使用 clear 会直接替换这些数据；运行前确认是否需要先 save。"
        local expr_label "数据文件路径 + clear（例如 mydata.dta, clear）"
        local example1 "use mydata.dta, clear"
        local explain1 "打开当前目录中的 mydata.dta，并允许替换内存数据。"
        local example2 "use firm year sales using panel.dta, clear"
        local explain2 "只读取 panel.dta 中的 firm、year、sales 三个变量。"
    }
    else if "`cmd'" == "import" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_if 0
        local has_in 0
        local has_weight 0
        local has_using 0
        local has_newvar 0
        local has_expression 1
        local show_advanced 1
        local title "import — 用 Stata 官方命令导入外部数据"
        local purpose1 "从 Excel、CSV/文本、SAS、SPSS 等外部格式读取数据。"
        local purpose2 "第一项先写 import 子命令，再写文件和格式选项；复杂编码或批量转换可转到 HX 数据转换 Workflow。"
        local expr_label "import 后面的完整主体（如 excel \"data.xlsx\", firstrow clear）"
        local example1 "import excel \"data.xlsx\", firstrow clear"
        local explain1 "把 Excel 第一行作为变量名并载入当前内存。"
        local example2 "import delimited \"data.csv\", clear"
        local explain2 "用 Stata 官方 delimited importer 读取 CSV/分隔文本。"
    }
    else if "`cmd'" == "export" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_if 0
        local has_in 0
        local has_weight 0
        local has_using 0
        local has_newvar 0
        local has_expression 1
        local show_advanced 1
        local title "export — 用 Stata 官方命令导出数据"
        local purpose1 "把当前 Stata 数据导出到 Excel、CSV/分隔文本等外部格式。"
        local purpose2 "导出不会改变当前内存数据；replace 会覆盖同名目标文件，运行前检查输出路径。"
        local expr_label "export 后面的完整主体（如 excel using \"result.xlsx\", firstrow(variables) replace）"
        local example1 "export excel using \"result.xlsx\", firstrow(variables) replace"
        local explain1 "把当前数据导出到 Excel，并把变量名写入第一行。"
        local example2 "export delimited using \"result.csv\", replace"
        local explain2 "把当前数据导出为 CSV/分隔文本。"
    }
    else if "`cmd'" == "save" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_if 0
        local has_in 0
        local has_weight 0
        local has_using 0
        local has_newvar 0
        local has_expression 1
        local show_advanced 0
        local title "save — 保存当前 Stata 数据"
        local purpose1 "把当前内存数据保存为 .dta 文件。"
        local purpose2 "replace 会覆盖已有文件；建议原始数据保持只读，把清洗结果保存为新文件。"
        local expr_label "目标 .dta 文件 + replace 等选项（例如 cleaned.dta, replace）"
        local example1 "save cleaned.dta"
        local explain1 "把当前数据保存为 cleaned.dta；若文件已存在，Stata 会阻止覆盖。"
        local example2 "save cleaned.dta, replace"
        local explain2 "确认后覆盖已有 cleaned.dta。"
    }
    else if "`cmd'" == "generate" {
'''
s = once(s, marker, blocks, "native data I/O semantics insertion")
sp.write_text(s, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor2 = 'if \'local title "graph — 管理、保存与输出图形"\' not in semantics:\n    fail("graph management must have dedicated semantics")\n'
checks = '''if 'local view "use import export save"' not in registry:
    fail("Data import/convert navigation must surface native Stata I/O commands")
if 'local data_cmds "hxconvert ' in registry:
    fail("HX converter must not occupy the public native Data command catalog")
if 'local workflow_cmds "hxconvert oneclick oneclick_robustness"' not in registry:
    fail("HX converter must remain available in the Workflow catalog")
for native_io in ("use", "import", "export", "save"):
    if f'local title "{native_io} —' not in semantics:
        fail(f"native Data I/O semantics missing: {native_io}")
'''
v = once(v, anchor2, anchor2 + checks, "native data I/O static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_NATIVE_DATA_IO_PATCH_OK")
