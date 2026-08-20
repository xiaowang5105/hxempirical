*! hxsemantics_rules 1.5.12  20aug2026
*! Included by hxsemantics.ado in the same local-macro scope.
    if "`cmd'" == "use" {
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
        local expr_label "import 后面的完整主体（如 excel "data.xlsx", firstrow clear）"
        local example1 "import excel "data.xlsx", firstrow clear"
        local explain1 "把 Excel 第一行作为变量名并载入当前内存。"
        local example2 "import delimited "data.csv", clear"
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
        local expr_label "export 后面的完整主体（如 excel using "result.xlsx", firstrow(variables) replace）"
        local example1 "export excel using "result.xlsx", firstrow(variables) replace"
        local explain1 "把当前数据导出到 Excel，并把变量名写入第一行。"
        local example2 "export delimited using "result.csv", replace"
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
    else if "`cmd'" == "assert" {
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
        local expr_label "字符串变量 + parse()/generate() 等（例如 fullname, parse(" " ) gen(namepart)）"
        local example1 "split fullname, parse(" " ) gen(namepart)"
        local explain1 "按空格拆分 fullname，并生成 namepart1、namepart2 等变量。"
        local example2 "split code, parse("-")"
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
        local template "generate"
        local title "generate — 创建新变量"
        local purpose1 "根据现有变量或计算公式创建一个新的变量。"
        local purpose2 "新变量名由你填写；公式可以是 log(x)、x*c1 等。"
        local newvar_label "1. 新变量叫什么？"
        local expr_label "2. 怎样计算新变量？"
        local if_label "3. 只计算哪些样本？if（可选）"
        local example1 "generate newx = log(x)"
        local explain1 "创建新变量 newx，它等于 x 的自然对数。"
        local example2 "generate interaction = x*c1"
        local explain2 "创建 x 和 c1 的交互项。"
        local has_depvar 0
        local has_varlist 0
        local has_newvar 1
        local has_expression 1
        local has_if 1
        local show_advanced 0
    }
    else if "`cmd'" == "describe" {
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
        local expr_label "label 子命令主体（如 variable sales "Sales revenue"）"
        local title "label — 管理变量标签和值标签"
        local purpose1 "给变量增加可读说明，或定义/绑定分类变量的 value label。"
        local purpose2 "label 是一组子命令；页面保留原生主体，避免把 variable/define/values 混成同一参数。"
        local example1 "label variable sales "Sales revenue""
        local explain1 "为 sales 设置变量标签。"
        local example2 "label define yesno 0 "No" 1 "Yes""
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
    else if "`cmd'" == "replace" {
        local template "replace"
        local title "replace — 修改已有变量的值"
        local purpose1 "重新计算一个已经存在的变量，可以只修改符合条件的样本。"
        local purpose2 "例如把 y 改成 1，或根据 x 重新计算 y。"
        local dep_label "1. 要修改哪个变量？"
        local expr_label "2. 修改成什么？"
        local if_label "3. 只修改哪些样本？if（可选）"
        local example1 "replace y = 1"
        local explain1 "把 y 的值全部修改成 1。"
        local example2 "replace y = 1 if year >= 2020"
        local explain2 "只对 2020 年及以后，把 y 修改成 1。"
        local has_depvar 1
        local has_varlist 0
        local has_newvar 0
        local has_expression 1
        local has_if 1
        local show_advanced 0
    }
    else if inlist("`cmd'", "keep", "drop") {
        local template "keepdrop"
        local keepdrop_mode 1
        local has_depvar 0
        local has_varlist 1
        local has_if 1
        local has_in 1
        local models "处理变量 处理样本"
        local model_before 0
        local model_label "你要处理什么？"
        if "`cmd'" == "keep" {
            local title "keep — 保留变量或样本"
            local purpose1 "只保留选中的变量，或者只保留符合条件的样本。"
            local purpose2 "选择“处理样本”时填写 if 条件；选择“处理变量”时点选变量。"
            local vars_label "要保留的变量"
            local if_label "要保留的样本条件 if"
            local example1 "keep y x c1 c2"
            local explain1 "数据中只保留 y、x、c1、c2 这几个变量。"
            local example2 "keep if year >= 2020"
            local explain2 "只保留 2020 年及以后的样本。"
        }
        else {
            local title "drop — 删除变量或样本"
            local purpose1 "删除选中的变量，或者删除符合条件的样本。"
            local purpose2 "运行前先看实时命令，避免误删重要数据。"
            local vars_label "要删除的变量"
            local if_label "要删除的样本条件 if"
            local example1 "drop c1 c2"
            local explain1 "删除变量 c1 和 c2。"
            local example2 "drop if year < 2020"
            local explain2 "删除 2020 年以前的样本。"
        }
        local show_advanced 0
    }
    else if "`cmd'" == "merge" {
        local template "merge"
        local title "merge — 按关联变量合并两张数据表"
        local purpose1 "把副表中的变量按企业、年份等关联变量合并到当前主表。"
        local purpose2 "运行前可检查主表和副表的关联变量是否满足 1:1、m:1 或 1:m。"
        local model_label "合并关系"
        local vars_label "关联变量（主表和副表共有）"
        local using_label "副表文件 using"
        local example1 "merge 1:1 firm year using otherdata.dta"
        local explain1 "主表和副表中，每个 firm-year 都只有一条记录。"
        local example2 "merge m:1 firm year using otherdata.dta"
        local explain2 "主表可有多个相同 firm-year，副表必须唯一。"
        local has_depvar 0
        local has_varlist 1
        local has_using 1
        local has_if 0
        local has_in 0
        local has_weight 0
        local models "1:1 m:1 1:m"
        local model_before 1
        local show_merge_check 1
        local show_advanced 1
    }
    else if "`cmd'" == "append" {
        local template "append"
        local title "append — 把另一张表追加到当前数据下方"
        local purpose1 "用于合并字段相同或相近的不同年份、地区或批次数据。"
        local purpose2 "当前内存数据是第一张表，using 文件中的观测会追加到后面。"
        local using_label "要追加的数据文件 using"
        local example1 "append using data2021.dta"
        local explain1 "把 data2021.dta 的样本追加到当前数据下方。"
        local example2 "append using data2021.dta data2022.dta"
        local explain2 "一次追加两张数据表。"
        local has_depvar 0
        local has_varlist 0
        local has_using 1
        local show_advanced 1
    }
    else if "`cmd'" == "reshape" {
        local template "reshape"
        local title "reshape — 在宽表和长表之间转换"
        local purpose1 "把 income2019、income2020 等宽表变量转换成长表，或把长表转换回宽表。"
        local purpose2 "填写变量前缀 stub、个体标识 i() 和维度变量 j()；转换前应检查重复键。"
        local model_label "转换方向"
        local models "宽表转长表（long） 长表转宽表（wide）"
        local model_before 1
        local expr_label "变量前缀 stub（如 income）"
        local panel_label "个体标识 i()"
        local time_label "维度变量 j()"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local needs_panel 1
        local example1 "reshape long income, i(firm) j(year)"
        local explain1 "把 income2019、income2020 等变量转换为 firm-year 长表。"
        local example2 "reshape wide income, i(firm) j(year)"
        local explain2 "把 firm-year 长表中的 income 转换回多个年份列。"
        local show_advanced 1
    }
    else if "`cmd'" == "collapse" {
        local template "collapse"
        local title "collapse — 按组汇总并替换当前数据"
        local purpose1 "把明细数据聚合成企业、年份或地区层面的均值、总和、中位数等统计量。"
        local purpose2 "collapse 会替换当前数据；建议先 preserve，或保存原始数据副本。"
        local model_label "汇总统计量"
        local models "均值（mean） 总和（sum） 中位数（median） 样本数（count）"
        local vars_label "要汇总的数值变量"
        local absorb_label "分组变量 by()（可多选；不分组可留空）"
        local has_depvar 0
        local has_varlist 1
        local has_absorb 1
        local needs_panel 0
        local example1 "collapse (mean) y x, by(firm)"
        local explain1 "按 firm 汇总 y、x 的均值，每个企业保留一行。"
        local example2 "collapse (sum) sales, by(firm year)"
        local explain2 "按企业和年份汇总 sales 总和。"
        local show_advanced 1
    }
    else if inlist("`cmd'", "xtset", "tsset") {
        local template "xtset"
        if "`cmd'" == "xtset" {
            local title "xtset — 设置面板数据结构"
            local purpose1 "告诉 Stata 哪个变量表示企业或个人，哪个变量表示时间。"
            local purpose2 "设置后才能正确使用 xtreg 等面板命令。"
            local example1 "xtset firm year"
            local explain1 "firm 是企业，year 是年份。"
            local example2 "xtset firm"
            local explain2 "只有个体变量，没有规则的时间变量。"
            local panel_label "面板变量（必填）"
            local time_label "时间变量（可选）"
        }
        else {
            local title "tsset — 设置时间序列结构"
            local purpose1 "告诉 Stata 哪个变量表示时间；面板时间序列时也可以同时提供面板变量。"
            local purpose2 "newey、prais 和时间序列运算需要先正确声明时间结构。"
            local example1 "tsset year"
            local explain1 "year 是时间变量。"
            local example2 "tsset firm year"
            local explain2 "firm 是面板变量，year 是时间变量。"
            local panel_label "面板变量（可选；纯时间序列留空）"
            local time_label "时间变量（必填）"
        }
        local has_depvar 0
        local has_varlist 0
        local has_if 0
        local has_in 0
        local needs_panel 1
        local is_xtset 1
        local show_advanced 0
    }
    else if inlist("`cmd'", "encode", "decode", "destring", "tostring") {
        local template "conversion"
        local has_depvar 1
        local has_varlist 0
        local has_newvar 1
        local show_advanced 1
        local dep_label "要转换的原变量"
        local newvar_label "转换后的新变量名"
        if "`cmd'" == "encode" {
            local title "encode — 把字符串类别转换为带标签的数值"
            local purpose1 "把省份、行业、性别等字符串类别转换成 Stata 可用于模型的数值编码。"
            local purpose2 "数值编码默认按字符串排序；需要固定顺序时应先定义 value label。"
            local example1 "encode industry, gen(industry_id)"
            local explain1 "把字符串 industry 转换成带标签的数值变量 industry_id。"
            local example2 "tabulate industry_id, nolabel"
            local explain2 "查看转换后实际使用的数值编码。"
        }
        else if "`cmd'" == "decode" {
            local title "decode — 把带标签数值转换回字符串"
            local purpose1 "把带 value label 的数值类别恢复成可读字符串。"
            local purpose2 "原变量必须已经绑定数值标签。"
            local example1 "decode industry_id, gen(industry)"
            local explain1 "把 industry_id 的标签文字写入新字符串变量 industry。"
            local example2 "describe industry industry_id"
            local explain2 "对照检查转换前后的变量类型。"
        }
        else if "`cmd'" == "destring" {
            local title "destring — 把数字字符串转换为数值"
            local purpose1 "把看起来像 123.4 的字符串变量转换成可计算的数值变量。"
            local purpose2 "遇到货币符号、逗号等字符时，可在更多设置填写 ignore()。"
            local model_label "保存方式"
            local models "生成新变量 覆盖原变量"
            local example1 "destring income, generate(income_num)"
            local explain1 "保留 income，并生成数值变量 income_num。"
            local example2 "destring income, replace ignore(\",\")"
            local explain2 "忽略逗号并直接把 income 转换成数值。"
        }
        else {
            local title "tostring — 把数值转换为字符串"
            local purpose1 "把数值编号转换成字符串，常用于合并键、代码拼接或导出。"
            local purpose2 "有前导零的代码需要设置 format()，避免编码信息丢失。"
            local model_label "保存方式"
            local models "生成新变量 覆盖原变量"
            local example1 "tostring firm, generate(firm_str)"
            local explain1 "保留 firm，并生成字符串变量 firm_str。"
            local example2 "tostring firm, replace format(%06.0f)"
            local explain2 "把 firm 转成六位字符串并保留前导零。"
        }
    }
    else if "`cmd'" == "winsor2" {
        local template "winsor2"
        local winsor_mode 1
        local title "winsor2 — 对极端值进行缩尾处理"
        local purpose1 "把变量两端的极端值压到指定分位点，常用于经济学论文的数据清理。"
        local purpose2 "默认上下 1% 缩尾；可覆盖原变量或生成带后缀的新变量。"
        local vars_label "要缩尾的变量"
        local expr_label "缩尾分位点 cuts()"
        local model_label "处理方式"
        local default_expression "1 99"
        local models "覆盖原变量 创建新变量"
        local example1 "winsor2 x c1 c2, cuts(1 99) replace"
        local explain1 "对 x、c1、c2 做上下 1% 缩尾，并覆盖原变量。"
        local example2 "winsor2 x, cuts(1 99) suffix(_w)"
        local explain2 "保留 x，并创建缩尾后的 x_w。"
        local has_depvar 0
        local has_varlist 1
        local has_expression 1
        local show_advanced 1
    }
    else if inlist("`cmd'", "duplicates", "misstable") {
        local has_depvar 0
        local has_varlist 1
        local vars_label "检查变量（可选；留空按命令默认范围）"
        local show_advanced 1
        if "`cmd'" == "duplicates" {
            local title "duplicates report — 检查重复记录"
            local purpose1 "检查整行记录或指定变量组合是否重复。"
            local purpose2 "页面最终执行 Stata 官方 duplicates report；选变量时按这些变量判断重复。"
            local example1 "duplicates report firm year"
            local explain1 "检查 firm-year 键是否出现重复。"
            local example2 "duplicates report"
            local explain2 "检查整行完全重复的记录。"
        }
        else {
            local title "misstable summarize — 汇总缺失值"
            local purpose1 "使用 Stata 官方 misstable summarize 查看变量缺失情况。"
            local purpose2 "可选择变量；留空时按 Stata 默认范围汇总。"
            local example1 "misstable summarize y x c1"
            local explain1 "汇总 y、x、c1 的缺失情况。"
            local example2 "misstable summarize"
            local explain2 "按 Stata 默认范围汇总缺失情况。"
        }
    }
    else if inlist("`cmd'", "ameans", "centile", "mean", "proportion", "total") {
        local has_depvar 0
        local has_varlist 1
        local vars_label "要汇总 / 估计的变量"
        local show_advanced 1
        if "`cmd'" == "ameans" {
            local title "ameans — 算术、几何和调和平均数"
            local purpose1 "同时报告变量的算术平均数、几何平均数和调和平均数及其区间估计。"
            local purpose2 "适合正值变量；几何/调和平均数对零值和负值有定义限制。"
            local example1 "ameans y"
            local explain1 "报告 y 的三类平均数。"
            local example2 "ameans y x"
            local explain2 "一次汇总多个正值变量。"
        }
        else if "`cmd'" == "centile" {
            local title "centile — 百分位数及置信区间"
            local purpose1 "估计中位数或指定百分位点，并报告相应置信区间。"
            local purpose2 "常用 centile() 指定 25、50、75 等百分位。"
            local example1 "centile y, centile(25 50 75)"
            local explain1 "报告 y 的第 25、50、75 百分位。"
            local example2 "centile y"
            local explain2 "按 Stata 默认百分位设定估计 y。"
        }
        else if "`cmd'" == "mean" {
            local title "mean — 均值及设计型标准误"
            local purpose1 "估计一个或多个变量的总体均值、标准误和置信区间。"
            local purpose2 "可配合 over()、权重、稳健或聚类 VCE；调查设计数据可使用 svy: mean。"
            local example1 "mean y x"
            local explain1 "估计 y、x 的均值及置信区间。"
            local example2 "mean y, over(group)"
            local explain2 "按 group 分组估计 y 的均值。"
        }
        else if "`cmd'" == "proportion" {
            local title "proportion — 类别比例及置信区间"
            local purpose1 "估计类别变量各水平的总体比例并报告标准误和置信区间。"
            local purpose2 "与 tabulate 的频数展示不同，本页面向比例参数估计和推断。"
            local example1 "proportion group"
            local explain1 "估计 group 各类别的总体比例。"
            local example2 "proportion group, over(region)"
            local explain2 "按 region 分层报告 group 的比例。"
        }
        else {
            local title "total — 总量估计"
            local purpose1 "估计一个或多个变量的总体总量，并报告标准误和置信区间。"
            local purpose2 "可配合 over()、权重以及 survey 前缀。"
            local example1 "total sales"
            local explain1 "估计 sales 的总体总量。"
            local example2 "total sales, over(region)"
            local explain2 "按 region 分组估计 sales 总量。"
        }
    }
    else if inlist("`cmd'", "summarize", "tabstat", "correlate", "pwcorr", "ttest", "tabulate") {
        local has_depvar 0
        local has_varlist 1
        local vars_label "要分析的变量"
        local show_advanced 1
        if "`cmd'" == "summarize" {
            local title "summarize — 查看变量的描述统计"
            local purpose1 "显示样本数、均值、标准差、最小值和最大值。"
            local purpose2 "选择一个或多个变量即可。"
            local example1 "summarize y x c1 c2"
            local explain1 "查看 y、x、c1、c2 的基本描述统计。"
            local example2 "summarize y, detail"
            local explain2 "进一步显示分位数、偏度和峰度等详细统计。"
        }
        else if "`cmd'" == "tabstat" {
            local title "tabstat — 自定义描述统计指标"
            local purpose1 "按需要显示均值、标准差、中位数等指标，也可以分组统计。"
            local purpose2 "常用指标可在更多设置中填写 statistics()。"
            local example1 "tabstat y x, statistics(mean sd min p50 max n)"
            local explain1 "显示均值、标准差、最小值、中位数、最大值和样本数。"
            local example2 "tabstat y, by(firm) statistics(mean sd)"
            local explain2 "按 firm 分组显示 y 的均值和标准差。"
        }
        else if "`cmd'" == "correlate" {
            local title "correlate — 计算相关系数"
            local purpose1 "查看多个变量之间的线性相关程度。"
            local purpose2 "至少选择两个变量。"
            local example1 "correlate y x c1 c2"
            local explain1 "计算 y、x、c1、c2 的相关系数矩阵。"
            local example2 "correlate x c1"
            local explain2 "计算 x 与 c1 的相关系数。"
        }
        else if "`cmd'" == "pwcorr" {
            local title "pwcorr — 计算成对相关系数"
            local purpose1 "逐对使用非缺失样本计算相关系数，可同时显示显著性。"
            local purpose2 "至少选择两个变量；常用 options 是 sig 和 obs。"
            local example1 "pwcorr y x c1 c2, sig obs"
            local explain1 "显示相关系数、p 值和每一对变量的样本数。"
            local example2 "pwcorr x c1, sig"
            local explain2 "计算 x 与 c1 的相关系数并显示显著性。"
        }
        else if "`cmd'" == "ttest" {
            local template "ttest"
            local title "ttest — 检验均值是否存在差异"
            local purpose1 "比较一个变量与某个数值，或比较两个组的均值。"
            local purpose2 "选择检验方式后，填写比较值、分组变量或第二个变量。"
            local model_label "检验方式"
            local models "单样本（=数值） 分组比较 配对比较"
            local expr_label "比较值 / 分组变量 / 第二变量（随检验方式填写）"
            local has_expression 1
            local example1 "ttest y == 0"
            local explain1 "检验 y 的均值是否等于 0。"
            local example2 "ttest y, by(firm)"
            local explain2 "比较 firm 两组之间 y 的均值。"
        }
        else {
            local title "tabulate — 查看频数或列联表"
            local purpose1 "统计类别变量的频数，或查看两个类别变量的交叉分布。"
            local purpose2 "选择一个变量得到频数表，选择两个变量得到列联表。"
            local example1 "tabulate firm"
            local explain1 "查看 firm 各类别的频数。"
            local example2 "tabulate firm year, row column"
            local explain2 "查看 firm 与 year 的列联表并显示行列比例。"
        }
    }
    else if inlist("`cmd'", "regress", "areg", "reghdfe", "qreg", "rreg", "cnsreg", "vwls", "eivreg") | ///
        inlist("`cmd'", "newey", "prais", "xtreg", "xtlogit", "xtprobit", "logit", "probit", "poisson") | ///
        inlist("`cmd'", "nbreg", "ppmlhdfe", "ivregress", "ivreghdfe", "didregress", "xtdidregress") {
        local template "estimation"
        local has_depvar 1
        local has_varlist 1
        local dep_label "因变量（解释谁）"
        local vars_label "解释变量（影响因变量）"
        local show_advanced 1
        if "`cmd'" == "regress" {
            local title "regress — 普通线性回归"
            local purpose1 "分析因变量 y 与一个或多个解释变量之间的线性关系。"
            local purpose2 "可以在标准误中选择默认、稳健或按变量聚类。"
            local example1 "regress y x c"
            local explain1 "用 x 解释 y，并加入控制变量 c。"
            local example2 "regress y x c1 c2, vce(robust)"
            local explain2 "加入 c1、c2，并使用稳健标准误。"
        }
        else if "`cmd'" == "areg" {
            local title "areg — 吸收一个固定效应的线性回归"
            local purpose1 "在线性回归中吸收一个类别固定效应，适合固定效应维度较少的情况。"
            local purpose2 "固定效应变量填入 absorb()。"
            local has_absorb 1
            local example1 "areg y x c1 c2, absorb(firm)"
            local explain1 "回归 y 对 x、c1、c2，同时控制 firm 固定效应。"
            local example2 "areg y x, absorb(firm) vce(cluster firm)"
            local explain2 "控制企业固定效应，并按企业聚类标准误。"
        }
        else if "`cmd'" == "reghdfe" {
            local title "reghdfe — 高维固定效应回归"
            local purpose1 "进行线性回归，同时吸收一个或多个固定效应。"
            local purpose2 "企业面板中常控制企业和年份固定效应。"
            local has_absorb 1
            local has_vce 1
            local has_cluster 1
            local example1 "reghdfe y x c1 c2, absorb(firm year)"
            local explain1 "回归 y 对 x、c1、c2，并控制企业和年份固定效应。"
            local example2 "reghdfe y x c1 c2, absorb(firm year) vce(cluster firm)"
            local explain2 "进一步把标准误按企业聚类。"
        }
        else if "`cmd'" == "qreg" {
            local template "qreg"
            local has_expression 1
            local expr_label "分位点 quantile()（可选；默认 0.5）"
            local title "qreg — 分位数回归"
            local purpose1 "估计解释变量对因变量某个分位点的影响，而不仅是均值影响。"
            local purpose2 "默认估计中位数；需要其他分位点时直接填写 0 到 1 之间的数值。"
            local example1 "qreg y x c1 c2"
            local explain1 "估计 y 的中位数回归。"
            local example2 "qreg y x c1 c2, quantile(.25)"
            local explain2 "估计 y 的第 25 百分位回归。"
        }
        else if "`cmd'" == "rreg" {
            local title "rreg — 稳健回归"
            local purpose1 "通过迭代加权降低异常观测对回归系数的影响。"
            local purpose2 "它与 regress, vce(robust) 不同：rreg 改变点估计，稳健标准误只改变推断。"
            local example1 "rreg y x c1 c2"
            local explain1 "对异常点更不敏感的线性回归。"
            local example2 "rreg y x, genwt(rw)"
            local explain2 "同时保存每个观测最终获得的稳健权重。"
        }
        else if "`cmd'" == "cnsreg" {
            local template "cnsreg"
            local has_expression 1
            local expr_label "约束编号 constraints()（如 1 2）"
            local title "cnsreg — 约束线性回归"
            local purpose1 "在预先定义的线性参数约束下估计线性回归。"
            local purpose2 "先用 constraint 定义限制，再在本页填写要使用的约束编号。"
            local example1 "constraint 1 x1 = x2"
            local explain1 "先定义第 1 条参数约束。"
            local example2 "cnsreg y x1 x2, constraints(1)"
            local explain2 "在第 1 条约束下估计模型。"
        }
        else if "`cmd'" == "vwls" {
            local template "vwls"
            local has_expression 1
            local expr_label "条件标准差变量 sd()（可选）"
            local title "vwls — 方差加权最小二乘"
            local purpose1 "使用已知或预先估计的条件标准差进行方差加权线性回归。"
            local purpose2 "有条件标准差信息时直接填写对应变量；只有方差信息有依据时才使用。"
            local example1 "vwls y x c, sd(sdvar)"
            local explain1 "使用 sdvar 作为 y 条件标准差的估计。"
            local example2 "vwls y i.group"
            local explain2 "也可用于某些分组数据设定。"
        }
        else if "`cmd'" == "eivreg" {
            local template "eivreg"
            local has_expression 1
            local expr_label "可靠度 reliab()（如 x .85）"
            local title "eivreg — 测量误差回归"
            local purpose1 "在已知解释变量测量可靠度时修正经典测量误差偏误。"
            local purpose2 "直接填写变量及其可靠度，例如 x .85；最终仍执行 Stata 官方 eivreg。"
            local example1 "eivreg y x c, reliab(x .85)"
            local explain1 "假设 x 的测量可靠度为 0.85。"
            local example2 "eivreg y x1 x2, reliab(x1 .8 x2 .9)"
            local explain2 "同时指定多个解释变量的可靠度。"
        }
        else if "`cmd'" == "newey" {
            local template "newey"
            local has_expression 1
            local expr_label "Newey–West 滞后阶数 lag()（非负整数）"
            local title "newey — Newey–West 线性回归"
            local purpose1 "用 HAC / Newey–West 标准误处理时间序列中的异方差与自相关。"
            local purpose2 "运行前应先用 tsset 声明时间变量，并在本页填写 lag 阶数。"
            local needs_panel 0
            local example1 "tsset year"
            local explain1 "先声明时间变量。"
            local example2 "newey y x c, lag(4)"
            local explain2 "使用 4 阶 Newey–West 标准误。"
        }
        else if "`cmd'" == "prais" {
            local title "prais — Prais–Winsten / Cochrane–Orcutt 回归"
            local purpose1 "针对 AR(1) 误差结构估计时间序列线性模型。"
            local purpose2 "默认使用 Prais–Winsten；需要 Cochrane–Orcutt 时在更多设置填写 corc。"
            local needs_panel 0
            local example1 "tsset year"
            local explain1 "先声明时间变量。"
            local example2 "prais y x c"
            local explain2 "估计带 AR(1) 误差的 Prais–Winsten 回归。"
        }
        else if inlist("`cmd'", "didregress", "xtdidregress") {
            local template "didregress"
            local has_depvar 1
            local has_varlist 1
            local has_if 1
            local has_in 1
            local has_weight 1
            local has_absorb 1
            local has_vce 1
            local has_cluster 1
            local needs_panel 1
            local models ""
            local default_model ""
            local vces "default robust cluster"
            local dep_label "结果变量 Y"
            local vars_label "协变量 / 控制变量（可多选）"
            local panel_label "处理变量（通常为 0/1）"
            local time_label "时间变量 time()"
            local absorb_label "处理发生层级 group()（可多选）"
            if "`cmd'" == "didregress" {
                local title "didregress — Stata 官方双重差分（重复截面）"
                local purpose1 "使用 Stata 官方 didregress 估计标准 DID / DDD 的 ATET。"
                local purpose2 "适合重复截面数据；处理变量放在第二组括号，group() 指定处理发生层级，time() 指定时间。"
                local example1 "didregress (y x1 x2) (treat), group(group) time(year)"
                local explain1 "用官方 didregress 估计重复截面 DID，并加入 x1、x2 协变量。"
                local example2 "estat trendplots"
                local explain2 "估计后可继续使用 Stata 官方 DID 诊断工具。"
            }
            else {
                local title "xtdidregress — Stata 官方面板双重差分"
                local purpose1 "使用 Stata 官方 xtdidregress 在纵向 / 面板数据中估计标准 DID。"
                local purpose2 "运行前先单独使用 xtset 声明面板结构；本页填写结果、协变量、处理变量、group() 和 time()。"
                local example1 "xtdidregress (y x1 x2) (treat), group(group) time(year)"
                local explain1 "在已 xtset 的面板数据上使用官方 xtdidregress。"
                local example2 "estat ptrends"
                local explain2 "估计后可继续使用 Stata 官方平行趋势检验。"
            }
        }
        else if inlist("`cmd'", "xtreg", "xtlogit", "xtprobit") {
            /* xtset is a separate Stata command.  Keep these pages limited to
               parameters that belong to the estimation command itself. */
            local needs_panel 0
            if "`cmd'" == "xtreg" {
                local title "xtreg — 面板数据回归"
                local purpose1 "适合企业、个人或地区在多个年份重复观察的数据。"
                local purpose2 "运行前应先单独用 xtset 声明面板结构；本页只设置 xtreg 自己的参数。"
                local models "固定效应（FE） 随机效应（RE） 组间效应（Between）"
                local default_model "随机效应（RE）"
                local example1 "xtset firm year"
                local explain1 "先告诉 Stata：firm 是企业，year 是年份。"
                local example2 "xtreg y x c1 c2, fe"
                local explain2 "运行企业固定效应面板回归。"
            }
            else if "`cmd'" == "xtlogit" {
                local title "xtlogit — 面板二元结果模型"
                local purpose1 "用于面板数据中取值为 0/1 的因变量。"
                local purpose2 "运行前应先单独用 xtset 声明面板结构；本页只设置 xtlogit 自己的参数。"
                local models "固定效应（FE） 随机效应（RE） 总体平均（PA）"
                local default_model "随机效应（RE）"
                local example1 "xtset firm year"
                local explain1 "设置企业和年份面板结构。"
                local example2 "xtlogit y x c1 c2, fe"
                local explain2 "固定效应面板 Logit 模型。"
            }
            else {
                local title "xtprobit — 面板 Probit 模型"
                local purpose1 "用于面板数据中取值为 0/1 的因变量，使用 Probit 概率模型。"
                local purpose2 "运行前应先单独用 xtset 声明面板结构；本页只设置 xtprobit 自己的参数。"
                local models "随机效应（RE） 总体平均（PA）"
                local default_model "随机效应（RE）"
                local example1 "xtset firm year"
                local explain1 "设置企业和年份面板结构。"
                local example2 "xtprobit y x c1 c2, re"
                local explain2 "随机效应面板 Probit 模型。"
            }
        }
        else if inlist("`cmd'", "logit", "probit") {
            if "`cmd'" == "logit" {
                local title "logit — 二元结果逻辑回归"
                local purpose1 "当因变量只有 0 和 1 两种结果时，估计事件发生概率。"
                local purpose2 "系数使用 Logit 链接函数；可在回归后使用 margins。"
                local example1 "logit y x c1 c2"
                local explain1 "用 x、c1、c2 解释二元结果 y。"
                local example2 "logit y x c1 c2, vce(robust)"
                local explain2 "使用稳健标准误。"
            }
            else {
                local title "probit — 二元结果 Probit 回归"
                local purpose1 "当因变量只有 0 和 1 两种结果时，使用正态分布链接估计概率。"
                local purpose2 "回归后可用 margins 计算边际效应。"
                local example1 "probit y x c1 c2"
                local explain1 "用 x、c1、c2 解释二元结果 y。"
                local example2 "probit y x c1 c2, vce(robust)"
                local explain2 "使用稳健标准误。"
            }
        }
        else if inlist("`cmd'", "poisson", "nbreg", "ppmlhdfe") {
            if "`cmd'" == "poisson" {
                local title "poisson — 泊松计数模型"
                local purpose1 "用于非负整数计数型因变量，例如专利数量或事件次数。"
                local purpose2 "可使用稳健或聚类标准误。"
                local example1 "poisson y x c1 c2"
                local explain1 "用 x、c1、c2 解释计数结果 y。"
                local example2 "poisson y x c1 c2, vce(robust)"
                local explain2 "使用稳健标准误。"
            }
            else if "`cmd'" == "nbreg" {
                local title "nbreg — 负二项计数模型"
                local purpose1 "用于方差明显大于均值的计数型因变量。"
                local purpose2 "它允许计数数据存在过度离散。"
                local example1 "nbreg y x c1 c2"
                local explain1 "用负二项模型解释计数结果 y。"
                local example2 "nbreg y x c1 c2, vce(robust)"
                local explain2 "使用稳健标准误。"
            }
            else {
                local title "ppmlhdfe — 高维固定效应 PPML"
                local purpose1 "使用泊松伪极大似然估计，并吸收多个固定效应。"
                local purpose2 "常用于贸易流量、非负结果和存在大量零值的数据。"
                local has_absorb 1
                local has_vce 1
                local has_cluster 1
                local example1 "ppmlhdfe y x c1 c2, absorb(firm year)"
                local explain1 "估计 PPML，并控制企业和年份固定效应。"
                local example2 "ppmlhdfe y x c1 c2, absorb(firm year) vce(cluster firm)"
                local explain2 "标准误按企业聚类。"
            }
        }
        else if inlist("`cmd'", "ivregress", "ivreghdfe") {
            local has_iv 1
            local endog_label "内生变量（需处理）"
            local inst_label "工具变量（解释内生）"
            local vars_label "正常解释变量 / 控制"
            if "`cmd'" == "ivregress" {
                local title "ivregress — 工具变量回归"
                local purpose1 "当某个解释变量可能存在内生性时，使用工具变量进行估计。"
                local purpose2 "正常解释变量放在括号外，内生变量与工具变量放在括号内。"
                local model_label "估计方法"
                local models "两阶段最小二乘（2SLS） 有限信息极大似然（LIML） 广义矩估计（GMM）"
                local model_before 1
                local example1 "ivregress 2sls y c1 c2 (x = z)"
                local explain1 "用 z 作为 x 的工具变量，估计 y 的方程。"
                local example2 "ivregress 2sls y c1 c2 (x = z), first"
                local explain2 "同时显示第一阶段回归结果。"
            }
            else {
                local title "ivreghdfe — 带高维固定效应的工具变量回归"
                local purpose1 "在工具变量回归中同时吸收一个或多个高维固定效应。"
                local purpose2 "需要填写内生变量、工具变量和固定效应。"
                local has_absorb 1
                local example1 "ivreghdfe y c1 c2 (x = z), absorb(firm year)"
                local explain1 "使用 z 处理 x 的内生性，并控制企业和年份固定效应。"
                local example2 "ivreghdfe y c1 c2 (x = z), absorb(firm year) cluster(firm)"
                local explain2 "进一步把标准误按企业聚类。"
            }
        }
    }
    else if inlist("`cmd'", "test", "testparm", "testnl", "lincom", "nlcom", "predict", "margins") {
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local expr_label "要计算或检验的表达式"
        local show_advanced 1
        if "`cmd'" == "test" {
            local template "expression_body"
            local title "test — 检验一个或多个回归系数"
            local purpose1 "在回归后检验某个系数是否等于指定值，或联合检验多个系数。"
            local purpose2 "直接填写系数名或等式。"
            local example1 "test x = 0"
            local explain1 "检验 x 的回归系数是否等于 0。"
            local example2 "test x c1 c2"
            local explain2 "联合检验 x、c1、c2 的系数是否都为 0。"
        }
        else if "`cmd'" == "testparm" {
            local template "expression_body"
            local title "testparm — 联合检验一组模型项"
            local purpose1 "对一组系数、因子变量 levels 或交互项执行联合 Wald 检验。"
            local purpose2 "特别适合检验 i.group、交互项或一组滞后项是否整体显著。"
            local example1 "testparm i.group"
            local explain1 "联合检验 group 的所有非基准类别系数是否同时为 0。"
            local example2 "testparm c.x#i.group"
            local explain2 "联合检验 x 与 group 的全部交互项。"
        }
        else if "`cmd'" == "testnl" {
            local template "expression_body"
            local title "testnl — 非线性 Wald 假设检验"
            local purpose1 "检验由回归系数组成的非线性约束，并用 delta method 计算 Wald statistic。"
            local purpose2 "表达式直接引用 _b[var] 或 equation-specific coefficient names。"
            local example1 "testnl (_b[x])^2 = 1"
            local explain1 "检验 x 系数平方是否等于 1。"
            local example2 "testnl _b[x1]/_b[x2] = 1"
            local explain2 "检验两个系数之比是否等于 1。"
        }
        else if "`cmd'" == "lincom" {
            local template "expression_body"
            local title "lincom — 计算回归系数的线性组合"
            local purpose1 "在回归后计算系数之和、差或其他线性组合，并给出标准误。"
            local purpose2 "表达式中使用回归变量名。"
            local example1 "lincom x + c1"
            local explain1 "计算 x 与 c1 两个系数之和。"
            local example2 "lincom x - c1"
            local explain2 "计算 x 与 c1 两个系数之差。"
        }
        else if "`cmd'" == "nlcom" {
            local template "expression_body"
            local title "nlcom — 非线性系数组合"
            local purpose1 "计算系数的比率、乘积、转折点等非线性函数，并用 delta method 给出标准误和区间。"
            local purpose2 "表达式通常直接引用 _b[var]；多方程模型应使用 equation-specific coefficient names。"
            local example1 "nlcom (_b[x])^2"
            local explain1 "报告 x 系数平方及其 delta-method 标准误。"
            local example2 "nlcom -_b[x]/(2*_b[c.x#c.x])"
            local explain2 "计算二次项模型的 turning point。"
        }
        else if "`cmd'" == "predict" {
            local template "predict"
            local predict_mode 1
            local title "predict — 根据上一项模型生成预测或残差"
            local purpose1 "在回归之后创建预测值、残差或诊断变量。"
            local purpose2 "新变量名由你填写，结果类型从下拉框选择。"
            local newvar_label "新变量名（自己起名）"
            local model_label "要生成什么？"
            local models "预测值 残差 标准化残差"
            local has_expression 0
            local has_newvar 1
            local example1 "predict yhat"
            local explain1 "根据上一项回归生成预测值 yhat。"
            local example2 "predict residual, residuals"
            local explain2 "生成残差变量 residual。"
        }
        else {
            local template "margins"
            local title "margins — 计算预测值或边际效应"
            local purpose1 "在回归后计算平均边际效应、指定取值下的预测结果等。"
            local purpose2 "例如填写 dydx(x)；复杂设置可在更多设置中填写 at()。"
            local expr_label "margins 选项（如 dydx(x) 或 at(x=(0 1 2))）"
            local example1 "margins, dydx(x)"
            local explain1 "计算 x 的平均边际效应。"
            local example2 "margins, at(x=(0 1 2))"
            local explain2 "计算 x 分别取 0、1、2 时的预测结果。"
        }
    }
    else if inlist("`cmd'", "histogram", "kdensity") {
        local template "graph_univariate"
        local has_depvar 1
        local has_varlist 0
        local has_if 1
        local has_in 0
        local has_weight 1
        local show_advanced 1
        local dep_label "要查看分布的变量"
        if "`cmd'" == "histogram" {
            local title "histogram — 查看变量分布"
            local purpose1 "用直方图查看连续变量的集中位置、离散程度、偏态和异常区间。"
            local purpose2 "右侧先显示当前数据的近似预览；运行后生成 Stata 原生图形。"
            local example1 "histogram y, percent normal"
            local explain1 "绘制 y 的百分比直方图，并叠加正态曲线。"
            local example2 "histogram y, by(group) percent"
            local explain2 "按 group 分面查看 y 的分布。"
        }
        else {
            local title "kdensity — 核密度分布图"
            local purpose1 "用平滑密度曲线查看连续变量的分布形状。"
            local purpose2 "适合比较峰值、偏态和多峰结构；带宽会影响曲线平滑程度。"
            local example1 "kdensity y"
            local explain1 "绘制 y 的核密度曲线。"
            local example2 "kdensity y, normal"
            local explain2 "绘制核密度并叠加正态密度。"
        }
    }
    else if inlist("`cmd'", "scatter", "lfit") {
        local template "graph_xy"
        local has_depvar 1
        local has_varlist 1
        local has_if 1
        local has_in 0
        local has_weight 1
        local dep_label "纵轴 Y"
        local vars_label "横轴 X（通常选择一个）"
        local show_advanced 1
        if "`cmd'" == "scatter" {
            local title "scatter — 查看两个变量之间的关系"
            local purpose1 "用散点图观察 Y 与 X 的方向、形状、离群点和可能的非线性。"
            local purpose2 "图形用于探索关系；相关形状本身不提供因果识别。"
            local example1 "scatter y x"
            local explain1 "纵轴是 y，横轴是 x。"
            local example2 "scatter y x, mlabel(id)"
            local explain2 "在散点旁标注 id。"
        }
        else {
            local title "lfit — 线性拟合线"
            local purpose1 "绘制 Y 对 X 的最小二乘线性拟合线。"
            local purpose2 "常与 scatter 叠加，用于快速查看线性趋势。"
            local example1 "twoway lfit y x"
            local explain1 "绘制 y 与 x 的线性拟合线。"
            local example2 "twoway (scatter y x) (lfit y x)"
            local explain2 "把散点和拟合线叠加。"
        }
    }
    else if "`cmd'" == "event_plot" {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_expression 1
        local has_if 0
        local has_in 0
        local has_weight 0
        local expr_label "event_plot 命令主体（按作者 help 填写）"
        local show_advanced 1
        local title "event_plot — 事件研究结果图"
        local purpose1 "调用已安装的第三方 event_plot 命令绘制事件研究动态系数。"
        local purpose2 "不同估计器的结果对象写法可能不同；本页保留原作者命令主体和 options，不用 HX 算法替代。"
        local example1 "help event_plot"
        local explain1 "先核对当前安装版本支持的结果对象语法。"
        local example2 "event_plot ..."
        local explain2 "在命令主体中填写作者 help 要求的结果对象，再补充图形 options。"
    }
    else if inlist("`cmd'", "marginsplot", "coefplot") {
        local template "graph_postestimation"
        local has_depvar 0
        local has_varlist 0
        local has_if 0
        local has_in 0
        local has_weight 0
        local show_advanced 1
        if "`cmd'" == "marginsplot" {
            local title "marginsplot — 绘制边际效应或预测结果"
            local purpose1 "把上一条 margins 的结果绘制成带置信区间的图形。"
            local purpose2 "需要先成功运行 margins；横轴和分组由 margins 结果决定。"
            local example1 "marginsplot"
            local explain1 "绘制上一项 margins 结果。"
            local example2 "marginsplot, yline(0)"
            local explain2 "增加系数为 0 的参考线。"
        }
        else {
            local template "command_body"
            local has_expression 1
            local expr_label "模型 / 结果对象（可选，如 m1 m2）"
            local title "coefplot — 回归系数图"
            local purpose1 "把一个或多个已保存模型的系数和置信区间画在同一张图中。"
            local purpose2 "适合主结果、异质性或稳健性模型的视觉比较。"
            local example1 "coefplot, drop(_cons) xline(0)"
            local explain1 "绘制当前模型系数，隐藏常数项并增加 0 参考线。"
            local example2 "coefplot m1 m2, drop(_cons)"
            local explain2 "比较已保存的 m1 和 m2 两个模型。"
        }
    }



    /* stcox models the failure/time declared by stset; variables entered here are covariates. */
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

    if "`cmd'" == "betareg" {
        local template "generic"
        local title "betareg — Beta 回归"
        local purpose1 "用于严格落在 0 与 1 之间的连续比例 / 分数结果，直接建模条件均值并允许 precision 子模型。"
        local purpose2 "结果中出现 0 或 1 时应优先考虑 fracreg；betareg 的标准 Beta 分布要求 0<Y<1。"
        local has_depvar 1
        local has_varlist 1
        local dep_label "分数结果 Y（必须严格位于 0 与 1 之间）"
        local vars_label "解释变量"
        local example1 "betareg gini i.rural i.democracy i.colony, nolog"
        local explain1 "对严格位于 (0,1) 的 gini 进行 Beta 回归。"
        local example2 "help betareg"
        local explain2 "precision()、link() 等参数决定离散程度与均值链接，复杂设定运行前核对。"
    }

    /* bmaregress is the executable estimation command in Stata's BMA suite. */
    if "`cmd'" == "bmaregress" {
        local template "generic"
        local title "bmaregress — 贝叶斯模型平均线性回归"
        local purpose1 "在多个候选线性模型之间进行贝叶斯模型平均，反映模型选择不确定性。"
        local purpose2 "基础页面用于普通候选预测变量；需要 always/group 等内联变量组时，可直接在下方实时命令中按 Stata 原生语法补充；模型先验和 g-prior 等 options 运行前核对。"
        local has_depvar 1
        local has_varlist 1
        local dep_label "结果变量 Y"
        local vars_label "候选预测变量"
        local example1 "bmaregress y x1-x10"
        local explain1 "对 y 的候选预测变量 x1 到 x10 进行 BMA 线性回归。"
        local example2 "bmaregress y (x1-x3, always) x4-x10"
        local explain2 "把 x1 到 x3 设为所有候选模型都保留的变量。"
    }

    /* Complex prefixes, workflow commands, and multi-equation grammars are safer
       as one guided native command body than as guessed depvar/varlist roles. */
    if strpos(" sem gsem mi meta fmm irt irtgraph diflogistic difmh dsge dsgenl svyset svydescribe svy bootstrap jackknife permute simulate statsby bayes bayesmh bayespredict bayesreps bayesstats bayesgraph bayestest bayesvarstable bayesirf bayesfcast bmacoefsample bmagraph bmastats bmapredict contrast pwcompare predictnl lrtest hausman suest linktest estimates estat power ciwidth gsbounds gsdesign teffects eteffects stteffects mediate hdidregress xthdidregress sts sts_graph irf graph set screeplot scoreplot loadingplot biplot cluster_dendrogram cabiplot caprojection mdsconfig mdsshepard procoverlay discrim cluster table ci ratio dtable prtest sdtest oneway anova ranksum median signrank signtest exlogistic expoisson bitest bitesti ksmirnov symmetry tetrachoric tabi cc cs ir mcc dstdize pkexamine pksumm pkcross pkequiv pkcollapse pkshape hetregress sqreg intreg tobit truncreg churdle boxcox fp nl nlsur gmm sureg reg3 mvreg frontier gnbreg cpoisson binreg biprobit hetoprobit ziologit zioprobit clogit slogit cmset cmsummarize cmchoiceset cmtab cmsample cmclogit cmmixlogit cmxtmixlogit cmmprobit cmroprobit cmrologit nlogit canon ca candisc hotelling manova mca mds mdslong mdsmat mvtest procrustes heckman heckprobit heckoprobit heckpoisson eregress eprobit eoprobit eintreg ivprobit ivtobit ivpoisson ivfprobit ivqregress mixed mecloglog melogit meprobit mepoisson menbreg meologit meoprobit meintreg menl mestreg metobit meglm lasso elasticnet poregress pologit popoisson dslogit dspoisson xpologit xpopoisson telasso npregress nptrend ctset cttost ltable snapspan stset stdescribe stsum stci stcurve stbase stfill stgen stsplit stvary sttocc sttoct streg stintreg stintcox stcrreg stir strate stptime stmh stmc arima arfima arimasoc arfimasoc arch ucm mswitch threshold dfgls dfuller pperron corrgram cumsp pergram wntestb wntestq psdensity rolling forecast tsappend tsfill tsfilter tsreport tssmooth var svar vec varbasic varsoc vargranger varlmar varnorm varstable varwle vecrank veclmar vecnorm vecstable irf lpirf mgarch dfactor sspace xcorr spregress spivregress spxtregress xtivreg xtpcse xtgls xtregar xtrc xtstreg xteregress xteprobit xteoprobit xteintreg xtheckman xthtaylor xtdpd xtunitroot xtcointtest xtdescribe xtsum xttab xtdata xtgee xttobit xtintreg xtfrontier xtabond xtdpdsys dsregress poivregress xporegress xpoivregress etregress etpoisson fracreg zip zinb tpoisson tnbreg glm hetprobit asclogit asmprobit ", " `cmd' ") {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_if 0
        local has_in 0
        local has_weight 0
        local has_using 0
        local has_newvar 0
        local has_expression 1
        local has_absorb 0
        local has_vce 0
        local has_cluster 0
        local has_iv 0
        local needs_panel 0
        local model_before 0
        local models ""
        local default_model ""
        local vces "default"
        local show_advanced 0
        local expr_label "命令主体（不重复命令名）"
        local example1 "help `cmd'"
        local explain1 "先查看当前 Stata 版本支持的子命令、前缀或方程语法。"
        local example2 "`cmd' ..."
        local explain2 "页面会把这里填写的主体原样接到命令名后，并在运行前显示完整 Stata 命令。"

        if "`cmd'" == "sem" {
            local expr_label "线性 SEM 路径 / 方程（不重复 sem；如 (y <- x1 x2)）"
            local example1 "sem (y <- x1 x2)"
            local explain1 "最小线性路径模型：用 x1、x2 解释连续结果 y。"
            local example2 "sem (L1 -> m1 m2) (L2 -> m3 m4) (L3 <- L1 L2)"
            local explain2 "测量模型和结构路径可以在同一条 sem 命令中组合。"
        }
        if "`cmd'" == "gsem" {
            local expr_label "广义 SEM 方程 + family()/link()/随机效应/潜在类别设定"
            local example1 "gsem (y <- x1 x2, family(bernoulli) link(logit))"
            local explain1 "对二元结果 y 拟合 logit 链接的广义结构方程。"
            local example2 "gsem (alcohol truant weapon theft vandalism <-), logit lclass(C 3)"
            local explain2 "LCA 使用 gsem 的 lclass()；这里拟合 3 个潜在类别的二元题项模型。"
        }
        if "`cmd'" == "dsge" {
            local expr_label "线性化 DSGE 方程系统：控制变量方程 + (F.state = ..., state) 状态方程"
            local example1 "dsge (p = {beta}*E(F.p) + {kappa}*y) (F.y = {rho}*y, state)"
            local explain1 "两方程线性化 DSGE：p 是前瞻控制变量，y 是带冲击的状态变量；花括号内参数由模型估计。"
            local example2 "help dsge"
            local explain2 "正式模型应先 tsset；可继续加入 observed/unobserved 控制变量、多个状态方程和参数约束。"
        }
        if "`cmd'" == "dsgenl" {
            local expr_label "非线性 DSGE 方程系统 + observed()/unobserved()/endostate()/exostate()"
            local example1 "dsgenl (1 = {beta}*(x/F.x)*(r/(F.p*z))) (1/{phi} + (p-1) = {phi}*x + {beta}*(F.p-1)) ({beta}*r = p^(1/{beta})*u) (ln(F.u) = {rhou}*ln(u)) (ln(F.z) = {rhoz}*ln(z)), observed(r p) unobserved(x) exostate(z u)"
            local explain1 "官方 New Keynesian 示例：r、p 为 observed，x 为 unobserved control，z、u 为外生 state；F. 表示一期前瞻值。"
            local example2 "help dsgenl"
            local explain2 "需要内生 state 时继续使用 endostate()；稳态、识别与收敛诊断是非线性 DSGE 的模型核心。"
        }
        if "`cmd'" == "mi" {
            local expr_label "mi 子命令与完整参数（如 set / impute / estimate）"
            local example1 "mi set mlong"
            local explain1 "先声明多重插补数据格式。"
            local example2 "mi estimate: regress y x1 x2"
            local explain2 "估计阶段可把完整 mi estimate 前缀主体直接写在这里。"
        }
        if "`cmd'" == "meta" {
            local expr_label "meta 子命令与完整参数（先 set/esize，再 summarize/regress/forest）"
            local example1 "meta set es se"
            local explain1 "第一步声明已计算好的效应量 es 和标准误 se。"
            local example2 "meta summarize"
            local explain2 "在已经声明的 meta 数据上汇总总体效应与异质性。"
        }
        if "`cmd'" == "fmm" {
            local expr_label "类别数 + lcprob() class-membership 模型 + 冒号后的基础估计命令"
            local example1 "fmm 2: regress y x1 x2"
            local explain1 "拟合两类有限混合线性回归；类别数位于冒号前。"
            local example2 "fmm 2, lcprob(z1 z2): poisson y x1 x2"
            local explain2 "两类 Poisson mixture，并让 z1、z2 通过 multinomial-logit class model 解释潜在类别归属。"
        }
        if "`cmd'" == "irt" {
            local expr_label "IRT 模型类型 + 题项变量 + group()/constraints 等（1pl / 2pl / 3pl / grm / pcm / rsm / nrm / hybrid）"
            local example1 "irt 2pl item1-item10"
            local explain1 "二元题项拟合 2PL：每个 item 可有不同 difficulty 和 discrimination。"
            local example2 "irt grm item1-item10, group(urban)"
            local explain2 "有序题项拟合 graded-response model，并用 group() 做多组 IRT / DIF 分析。"
        }
        if "`cmd'" == "irtgraph" {
            local expr_label "图形类型 icc/tcc/iif/tif + item()/at()/by() 等图形参数"
            local example1 "irtgraph icc"
            local explain1 "绘制上一项 IRT 模型的 item characteristic curves。"
            local example2 "irtgraph tif"
            local explain2 "绘制 test information function，查看量表在哪些 latent-trait 区间提供最多信息。"
        }
        if "`cmd'" == "diflogistic" {
            local expr_label "题项变量 + group() + ability() 等 logistic-regression DIF 设定"
            local example1 "help diflogistic"
            local explain1 "使用 logistic regression 检验 uniform / nonuniform differential item functioning；先按当前 help 指定 group 与 ability 变量。"
            local example2 "irt 2pl item1-item10, group(urban)"
            local explain2 "DIF 结果应与多组 IRT 的 item 参数差异一起判断。"
        }
        if "`cmd'" == "difmh" {
            local expr_label "题项变量 + group() + score() 等 Mantel–Haenszel DIF 设定"
            local example1 "help difmh"
            local explain1 "使用 Mantel–Haenszel 方法检查二元题项的 DIF；分组变量与匹配 score 必须按 help 明确指定。"
            local example2 "irtgraph icc"
            local explain2 "统计检验后可用 ICC 进一步查看题项在 latent trait 上的组间差异。"
        }
        if "`cmd'" == "svyset" {
            local expr_label "PSU + sampling weight + strata()/fpc()/多阶段设计等声明"
            local example1 "svyset psu [pweight=finalwgt], strata(strata)"
            local explain1 "声明主抽样单元 psu、抽样权重 finalwgt 和分层变量 strata。"
            local example2 "svyset school_id, weight(wt_school) || _n, weight(wt_student)"
            local explain2 "多阶段调查可以逐层声明 sampling unit 和 stage-level weight。"
        }
        if "`cmd'" == "svydescribe" {
            local expr_label "要检查的变量（可留空）+ 调查设计描述 options"
            local example1 "svydescribe"
            local explain1 "查看当前 svyset 设计中的 strata、PSU、权重与设计结构。"
            local example2 "svydescribe y"
            local explain2 "同时查看 y 在各 strata / stage 中的缺失与非缺失情况。"
        }
        if "`cmd'" == "svy" {
            local expr_label "冒号后的估计命令（以 : 开头，如 : mean y）"
            local example1 "svy: mean weight"
            local explain1 "在已 svyset 的调查设计下估计总体均值并使用设计型标准误。"
            local example2 "svy: regress y x1 x2"
            local explain2 "在复杂抽样设计下运行线性回归。"
        }
        if strpos(" bootstrap jackknife permute simulate statsby ", " `cmd' ") {
            local expr_label "统计量 / 前缀参数 + 冒号后的命令（完整写出命令名后的部分）"
            if "`cmd'" == "bootstrap" {
                local example1 "bootstrap r(mean), reps(500): summarize y"
                local explain1 "对 summarize 返回的均值进行 bootstrap。"
            }
            else if "`cmd'" == "jackknife" {
                local example1 "jackknife r(mean): summarize y"
                local explain1 "对 summarize 返回的均值进行 jackknife。"
            }
            else if "`cmd'" == "permute" {
                local example1 "permute treatment _b[treatment], reps(500): regress y treatment x1 x2"
                local explain1 "随机置换 treatment，并用每次回归的 treatment 系数构造 permutation distribution。"
                local example2 "help permute"
                local explain2 "分层、聚类或复杂实验设计下必须让置换机制符合真实随机化结构。"
            }
            else if "`cmd'" == "statsby" {
                local example1 "statsby mean=r(mean) sd=r(sd), by(group): summarize y"
                local explain1 "对每个 group 重复 summarize y，并把均值、标准差收集成结果数据。"
                local example2 "help statsby"
                local explain2 "也可收集回归系数、检验统计量等 e()/r() 返回结果。"
            }
            else {
                local example1 "help simulate"
                local explain1 "simulate 需要一个能够在每次重复中生成随机数据并 return 标量的命令或 program；先定义该程序，再填写返回统计量与 reps()/seed()。"
            }
        }
        if "`cmd'" == "bayes" {
            local expr_label "Bayes 前缀主体（如 : regress y x；前缀 options 也写在这里）"
            local example1 "bayes: regress y x1 x2"
            local explain1 "用 bayes: 前缀估计标准回归模型。"
            local example2 "bayes, gibbs: regress y x1 x2"
            local explain2 "Bayes 前缀自身的 options 位于冒号前。"
        }
        if "`cmd'" == "bayesmh" {
            local expr_label "Bayesian 模型主体（结果变量、解释变量、likelihood、prior 等）"
            local example1 "bayesmh y x, likelihood(normal({sigma2})) prior({y:x _cons}, normal(0,100))"
            local explain1 "bayesmh 的似然和先验均属于完整模型主体。"
        }
        if "`cmd'" == "bayespredict" {
            local expr_label "预测结果变量 / 模拟结果对象 + mean/median/saving() 等 posterior-predictive 设定"
            local example1 "bayespredict pmean, mean"
            local explain1 "在上一项 Bayesian 模型后，为每条观测计算 posterior predictive mean 并保存为 pmean。"
            local example2 "help bayespredict"
            local explain2 "完整 MCMC predictions 可保存到独立数据文件；需要可重复结果时显式设置随机数种子。"
        }
        if "`cmd'" == "bayesreps" {
            local expr_label "新变量前缀 + nreps() + rseed()（MCMC replicated outcomes）"
            local example1 "bayesreps yrep*, nreps(10)"
            local explain1 "从 posterior predictive distribution 随机抽取 10 组 outcome replicates，写入当前数据的 yrep1–yrep10。"
            local example2 "help bayesreps"
            local explain2 "适合快速 posterior predictive model checks；Stata 16+。"
        }
        if "`cmd'" == "bayesstats" {
            local expr_label "summary/ic/ess/grubin/ppvalues 等 Bayesian 后验统计子命令"
            local example1 "bayesstats summary"
            local explain1 "汇总当前 Bayesian MCMC 样本中的参数后验均值、中位数和 credible intervals。"
            local example2 "help bayesstats"
            local explain2 "模型比较、有效样本量、多链收敛和 posterior predictive p-values 继续按对应子命令设置。"
        }
        if "`cmd'" == "bayesgraph" {
            local expr_label "diagnostics/trace/ac 等图形子命令 + 参数对象"
            local example1 "bayesgraph diagnostics {inflation:L1.ogap}"
            local explain1 "对指定 Bayesian 参数同时检查 trace、autocorrelation 等 MCMC 诊断图。"
            local example2 "help bayesgraph"
            local explain2 "运行前确认参数名来自当前 Bayesian estimation results。"
        }
        if "`cmd'" == "bayestest" {
            local expr_label "interval/model 等 Bayesian hypothesis-test 子命令 + 参数或 stored estimates"
            local example1 "bayestest model lag1 lag2 lag3"
            local explain1 "比较已保存的 lag1、lag2、lag3 Bayesian 模型，报告 marginal likelihood 与 posterior model probabilities。"
            local example2 "help bayestest"
            local explain2 "interval 可做区间假设检验；model 比较前必须保存兼容的 Bayesian estimation results。"
        }
        if "`cmd'" == "bayesvarstable" {
            local expr_label "上一项 bayes: var 的稳定性检验参数（通常可直接运行）"
            local example1 "bayesvarstable"
            local explain1 "检查 Bayesian VAR companion matrix 的 eigenvalue stability，并报告所有根位于单位圆内的 posterior probability。"
            local example2 "help bayesvarstable"
            local explain2 "该入口为 Stata 17+，前一项结果必须来自 bayes: var。"
        }
        if "`cmd'" == "bayesirf" {
            local expr_label "create/graph/table/cgraph/ograph + IRF 结果集与 impulse/response 设定"
            local example1 "bayesirf create birf, set(birfex)"
            local explain1 "在 Bayesian VAR 或 Bayesian DSGE 后创建 birf，并保存到 birfex.irf。"
            local example2 "bayesirf graph irf, impulse(fedfunds)"
            local explain2 "绘制 fedfunds shock 的 posterior IRF credible bands；Stata 17+。"
        }
        if "`cmd'" == "bayesfcast" {
            local expr_label "compute/graph + 新变量前缀 + step()/credible interval 等动态预测设定"
            local example1 "bayesfcast compute f_, step(10)"
            local explain1 "在 bayes: var 后生成未来 10 期 Bayesian dynamic forecasts，并以 f_ 为变量名前缀。"
            local example2 "bayesfcast graph f_inflation f_ogap f_fedfunds"
            local explain2 "绘制 posterior dynamic forecasts 及不确定性区间；Stata 17+。"
        }
        if "`cmd'" == "bmacoefsample" {
            local expr_label "simulate/saving()/rseed() 等 BMA 系数 posterior-sample 设定"
            local example1 "bmacoefsample, rseed(18)"
            local explain1 "在 bmaregress 后模拟 regression coefficients 的 posterior sample，供 credible intervals 和后续 Bayesian summaries 使用。"
            local example2 "bmacoefsample, saving(bmacoef)"
            local explain2 "把 BMA 参数 posterior sample 保存为 bmacoef.dta；Stata 18+。"
        }
        if "`cmd'" == "bmagraph" {
            local expr_label "pmp/msize/varmap/coefdensity 等 BMA 图形子命令"
            local example1 "bmagraph pmp"
            local explain1 "绘制 posterior model probabilities，查看模型空间中的主要高概率模型。"
            local example2 "bmagraph msize"
            local explain2 "绘制 posterior model-size distribution；Stata 18+。"
        }
        if "`cmd'" == "bmastats" {
            local expr_label "models/msize/pip/jointness/lps 等 BMA 统计子命令"
            local example1 "bmastats pip"
            local explain1 "报告候选 predictors 的 posterior inclusion probabilities。"
            local example2 "bmastats models"
            local explain2 "汇总 posterior model probabilities 与变量包含情况；Stata 18+。"
        }
        if "`cmd'" == "bmapredict" {
            local expr_label "新预测变量 + mean/cri 等 BMA posterior-predictive 设定"
            local example1 "bmapredict pmean, mean"
            local explain1 "计算包含 model uncertainty 的 BMA posterior predictive mean。"
            local example2 "bmapredict cri_l cri_u, cri rseed(18)"
            local explain2 "生成 posterior predictive credible interval 上下界；需要可用的 BMA posterior sample。"
        }
        if "`cmd'" == "ci" {
            local expr_label "CI 类型 + 变量（means / proportions / variances）"
            local example1 "ci means y"
            local explain1 "计算 y 均值的置信区间。"
            local example2 "ci proportions binaryvar"
            local explain2 "计算二元变量成功比例的置信区间。"
        }
        if "`cmd'" == "ratio" {
            local expr_label "分子/分母表达式（可一次填写多个 ratio）"
            local example1 "ratio sales/cost"
            local explain1 "估计总体均值之比 sales/cost，并报告标准误和置信区间。"
            local example2 "help ratio"
            local explain2 "多个 ratio、over()、权重和 VCE 设置可继续按当前 help 填写。"
        }
        if "`cmd'" == "dtable" {
            local expr_label "连续变量 + i.分类变量 + by()/tests/export 等 Table 1 设置"
            local example1 "dtable price weight mpg i.rep78"
            local explain1 "连续变量报告均值/标准差，i.rep78 报告类别频数与比例。"
            local example2 "dtable age weight i.sex, by(group, tests)"
            local explain2 "按 group 生成 Table 1，并请求组间差异检验。"
        }
        if "`cmd'" == "contrast" {
            local expr_label "contrast operator + factor variable/interaction + effects/nowald/mcompare() 等"
            local example1 "contrast ar.agegroup, nowald effects"
            local explain1 "对 agegroup 做 reverse-adjacent contrasts，直接比较每一档与前一档的 adjusted linear prediction。"
            local example2 "contrast p.agegroup"
            local explain2 "用 orthogonal polynomial contrasts 检查有序类别的 linear/quadratic/cubic 等趋势。"
        }
        if "`cmd'" == "pwcompare" {
            local expr_label "factor variable + effects + mcompare() 多重比较校正"
            local example1 "pwcompare agegrp, effects mcompare(tukey)"
            local explain1 "对 agegrp 所有 level 做 pairwise comparisons，并用 Tukey HSD 调整推断。"
            local example2 "help pwcompare"
            local explain2 "Bonferroni、Sidak、Scheffe 等 mcompare() 选择应与预先设定的比较族对应。"
        }
        if "`cmd'" == "predictnl" {
            local expr_label "新变量 = nonlinear prediction expression + se()/ci()"
            local example1 "predictnl xb2 = predict(xb)^2, se(se_xb2)"
            local explain1 "把 linear prediction 的平方作为非线性预测量，并用 delta method 生成标准误 se_xb2。"
            local example2 "help predictnl"
            local explain2 "expression 可组合 predict()、系数与数据变量；复杂表达式运行前核对当前模型支持的 predict statistic。"
        }
        if "`cmd'" == "lrtest" {
            local expr_label "受限模型 estimates-name + 非受限模型 estimates-name"
            local example1 "lrtest restricted unrestricted"
            local explain1 "比较两个已保存且使用同一数据/likelihood 的 nested maximum-likelihood models。"
            local example2 "help lrtest"
            local explain2 "LR test 依赖模型嵌套与可比 likelihood；robust/pseudolikelihood 场景应改用适当 Wald 或 score-type 检验。"
        }
        if "`cmd'" == "hausman" {
            local expr_label "consistent model estimates-name + efficient-under-H0 model estimates-name + sigmamore/sigmaless 等"
            local example1 "hausman fixed random"
            local explain1 "比较已保存的 fixed 与 random effects estimates，检验两组系数系统差异。"
            local example2 "help hausman"
            local explain2 "Hausman 检验需要两组可比估计结果；协方差矩阵差与模型设定应在解释前核对。"
        }
        if "`cmd'" == "suest" {
            local expr_label "两个或多个 estimates-name + vce()/cluster() 等 stacked sandwich 设定"
            local example1 "suest model1 model2"
            local explain1 "把 model1、model2 的参数向量与 robust covariance 合并，随后可用 test/testnl 做跨模型系数检验。"
            local example2 "help suest"
            local explain2 "先 estimates store 各模型；部分估计器不支持 suest，需要查看对应 postestimation help。"
        }
        if "`cmd'" == "linktest" {
            local expr_label "模型设定 link test options（通常直接运行）"
            local example1 "linktest"
            local explain1 "在兼容的单方程模型后回归结果对 _hat 与 _hatsq；_hatsq 显著提示函数形式可能遗漏。"
            local example2 "help linktest"
            local explain2 "linktest 是 specification diagnostic，不能替代对理论变量、残差和识别假设的检查。"
        }
        if "`cmd'" == "estimates" {
            local expr_label "store/restore/table/stats/save/use/replay 等 estimates suite 子命令"
            local example1 "estimates store model1"
            local explain1 "把当前 estimation results 在内存中命名为 model1，供后续比较、预测或检验。"
            local example2 "estimates table model1 model2, b(%9.3f) se"
            local explain2 "把两个已保存模型的 coefficients 与 standard errors 并列表格。"
        }
        if "`cmd'" == "estat" {
            local expr_label "当前估计器支持的 estat 子命令：ic/vif/gof/hettest/vce/..."
            local example1 "estat ic"
            local explain1 "在支持的 likelihood-based model 后显示 AIC/BIC 等 information criteria。"
            local example2 "estat vce"
            local explain2 "显示当前 coefficient variance–covariance matrix；具体可用 estat 子命令随估计器变化。"
        }
        if "`cmd'" == "power" {
            local expr_label "检验类型与设计参数（如 onemean 0 0.5, power(.8)）"
            local example1 "power onemean 0 0.5, power(.8)"
            local explain1 "一元均值检验的效能 / 样本量设计。"
            local example2 "power twomeans 0 0.5, power(.8)"
            local explain2 "两组均值比较的效能 / 样本量设计。"
        }
        if "`cmd'" == "ciwidth" {
            local expr_label "CI 设计类型 + width()/sd()/probwidth()/N() 等精度参数"
            local example1 "ciwidth twomeans, width(6) sd(5) probwidth(.96)"
            local explain1 "计算两独立样本均值差 CI 宽度不超过 6 所需的样本量。"
            local example2 "help ciwidth"
            local explain2 "可求样本量、CI 宽度或达到目标宽度的概率。"
        }
        if "`cmd'" == "gsbounds" {
            local expr_label "efficacy()/futility() + nlooks() + power()/alpha() 等停止界值设定"
            local example1 "gsbounds, efficacy(obfleming) futility(obfleming) nlooks(5) power(.9) alpha(.05)"
            local explain1 "为 5 次分析计算 O'Brien–Fleming 疗效和无效停止界值。"
            local example2 "help gsbounds"
            local explain2 "边界类型、信息时间和单/双侧设计应在研究设计阶段明确。"
        }
        if "`cmd'" == "gsdesign" {
            local expr_label "检验类型 + 原假设/备择参数 + SD/alpha/power/information/边界设定"
            local example1 "gsdesign twomeans 5.5 6.5, sd1(2) sd2(3) knownsds onesided alpha(.025) power(.9) nratio(2) information(50 65 80 90 100) efficacy(errobfleming) futility(errobfleming)"
            local explain1 "设计两样本均值 group-sequential trial，并计算每次 look 的停止界值与样本量。"
            local example2 "help gsdesign"
            local explain2 "可切换 one/two-sample means、proportions、log-rank 或 user-defined method。"
        }
        if "`cmd'" == "arfima" {
            local expr_label "时间序列 Y + AR/MA 阶数（分数差分参数 d 由模型估计）"
            local example1 "arfima y, ar(1) ma(1)"
            local explain1 "为长记忆过程拟合 ARFIMA，并同时允许短记忆 AR(1) 与 MA(1) 动态。"
            local example2 "help arfima"
            local explain2 "ARFIMA 适用于自相关缓慢衰减的长记忆序列；运行前先 tsset。"
        }
        if inlist("`cmd'", "arimasoc", "arfimasoc") {
            local expr_label "时间序列 Y + maxar() + maxma() 候选最大阶数"
            local example1 "`cmd' ogap, maxar(4) maxma(3)"
            local explain1 "比较候选 ARMA/ARFIMA 规格并报告 AIC、BIC、HQIC；该入口仅在 Stata 18+ 展示。"
            local example2 "help `cmd'"
            local explain2 "信息准则用于辅助选择动态阶数，最终模型仍需结合残差诊断与经济机制。"
        }
        if "`cmd'" == "mswitch" {
            local expr_label "dr/ar 模型类型 + Y + X + switch()/varswitch 等状态切换设定"
            local example1 "mswitch dr fedfunds"
            local explain1 "拟合两状态 Markov-switching dynamic regression，状态间允许参数随隐含 regime 转换。"
            local example2 "help mswitch"
            local explain2 "需要自回归状态过程时使用 ar；switch() 与 varswitch 用于指定哪些参数跨状态变化。"
        }
        if "`cmd'" == "threshold" {
            local expr_label "Y + threshvar() + regionvars() + nthresholds()/optthresh()"
            local example1 "threshold pollution, threshvar(hour) regionvars(oldbus newbus car)"
            local explain1 "自动估计 hour 的门槛，使 oldbus/newbus/car 的系数在门槛两侧不同。"
            local example2 "help threshold"
            local explain2 "可指定或选择多个 threshold；AIC/BIC/HQIC 与研究机制共同决定状态数。"
        }
        if "`cmd'" == "dfgls" {
            local expr_label "时间序列变量 + maxlag()/trend 等 DF-GLS 单位根设定"
            local example1 "dfgls y"
            local explain1 "对 y 执行 Elliott–Rothenberg–Stock DF-GLS 单位根检验。"
            local example2 "help dfgls"
            local explain2 "趋势项与最大滞后选择会影响检验；运行前先确认序列频率和 tsset。"
        }
        if inlist("`cmd'", "wntestb", "wntestq") {
            local expr_label "要检验的时间序列 + lag 等检验设定"
            local example1 "`cmd' y"
            local explain1 "检验 y 是否可视为白噪声；wntestb 基于 Bartlett periodogram，wntestq 使用 portmanteau Q。"
            local example2 "help `cmd'"
            local explain2 "白噪声检验常用于模型前识别或残差诊断，滞后阶数应与数据频率匹配。"
        }
        if "`cmd'" == "cumsp" {
            local expr_label "时间序列变量（累计谱分布图）"
            local example1 "cumsp y"
            local explain1 "绘制 y 的累计谱分布，用于观察频域能量是否集中在特定频率。"
            local example2 "help cumsp"
            local explain2 "适合与 periodogram 和白噪声检验配合进行频域诊断。"
        }
        if "`cmd'" == "psdensity" {
            local expr_label "频率新变量 + 谱密度新变量（在 arima/arfima/ucm 后运行）"
            local example1 "psdensity omega density"
            local explain1 "根据上一项 ARIMA、ARFIMA 或 UCM 估计生成参数化谱密度。"
            local example2 "help psdensity"
            local explain2 "这是模型后频域分析入口，必须先存在兼容的时间序列估计结果。"
        }
        if "`cmd'" == "rolling" {
            local expr_label "要保存的统计量 + window()/recursive + : 后估计命令"
            local example1 "rolling _b, window(20) saving(roll, replace): regress y x"
            local explain1 "用 20 期滚动窗口重复 regress y x，并保存各窗口系数。"
            local example2 "help rolling"
            local explain2 "rolling 会生成结果数据文件；window、step 和 recursive 应与研究的实时信息集一致。"
        }
        if "`cmd'" == "forecast" {
            local expr_label "forecast 子命令与参数（create / estimates / identity / exogenous / solve 等）"
            local example1 "forecast create model"
            local explain1 "先创建 forecast model；随后逐步加入估计结果、恒等式和外生变量。"
            local example2 "forecast solve"
            local explain2 "完成模型定义后求解静态或动态预测；复杂多方程预测保留原生 suite 工作流。"
        }
        if "`cmd'" == "tsappend" {
            local expr_label "add() / last() 等追加时间范围"
            local example1 "tsappend, add(12)"
            local explain1 "在时间序列末尾新增 12 期空观测，常用于生成未来期预测。"
            local example2 "help tsappend"
            local explain2 "该命令会增加内存中的观测数；运行前确认当前 tsset 频率与样本末期。"
        }
        if "`cmd'" == "tsfill" {
            local expr_label "填补时间轴缺口；面板数据可按当前 tsset/xtset 结构补齐"
            local example1 "tsfill"
            local explain1 "为当前时间轴中的缺失期间添加空观测，使时间索引连续。"
            local example2 "help tsfill"
            local explain2 "新增观测中的业务变量通常仍为缺失值；补齐时间索引后还需决定如何处理这些缺失。"
        }
        if "`cmd'" == "tsfilter" {
            local expr_label "滤波器 hp/bk/cf/bw + 新变量 = 原序列 + smooth()/maxperiod() 等参数"
            local example1 "tsfilter hp y_cycle = y, smooth(1600)"
            local explain1 "使用 Hodrick–Prescott filter 从季度序列 y 中提取周期成分 y_cycle。"
            local example2 "help tsfilter"
            local explain2 "HP、BK、CF、Butterworth 的边界与频率响应不同，应按数据频率和研究目标选型。"
        }
        if "`cmd'" == "tsreport" {
            local expr_label "时间序列结构报告 options（通常可直接运行）"
            local example1 "tsreport"
            local explain1 "报告时间范围、缺口、重复/不连续时间等当前 time-series 数据结构信息。"
            local example2 "help tsreport"
            local explain2 "适合在 ARIMA、滤波、单位根等正式分析前检查时间轴质量。"
        }
        if "`cmd'" == "tssmooth" {
            local expr_label "平滑方法 + 新变量 = 原序列 + window()/parms() 等参数"
            local example1 "tssmooth ma y_ma = y, window(2 1 2)"
            local explain1 "生成 y 的中心移动平均平滑序列 y_ma。"
            local example2 "help tssmooth"
            local explain2 "还可使用 exponential、dexponential、Holt–Winters seasonal/nonseasonal 等平滑方法。"
        }
        if "`cmd'" == "varbasic" {
            local expr_label "内生变量列表 + lags()/step() 等快速 VAR/IRF 设置"
            local example1 "varbasic y1 y2"
            local explain1 "快速拟合基础 VAR，并生成常用 IRF/FEVD 结果，适合探索性分析。"
            local example2 "help varbasic"
            local explain2 "正式研究通常进一步使用 var + irf suite 明确滞后、识别和结果文件。"
        }
        if strpos(" varlmar varnorm varwle veclmar vecnorm vecstable ", " `cmd' ") {
            local expr_label "上一项 VAR/VEC 模型的后估计检验参数（多数可直接运行）"
            local example1 "`cmd'"
            local explain1 "对上一项 VAR/VEC 结果执行对应的残差、自相关、正态性、稳定性或 lag-exclusion 诊断。"
            local example2 "help `cmd'"
            local explain2 "先确认当前 e() 结果来自兼容的 VAR/VEC 模型。"
        }
        if "`cmd'" == "vecrank" {
            local expr_label "协整变量列表 + lags()/trend() 等 Johansen rank-test 设定"
            local example1 "vecrank y1 y2"
            local explain1 "使用 Johansen 方法估计 y1、y2 的 cointegrating rank，为后续 vec 规格提供依据。"
            local example2 "help vecrank"
            local explain2 "滞后阶数、确定性趋势与样本区间都会改变 rank test 的结论。"
        }
        if "`cmd'" == "lpirf" {
            local expr_label "响应变量列表 + lags() + exog() 等 local-projection IRF 设定"
            local example1 "lpirf indpro inflation, lags(1/12) exog(L(0/12).money_shock)"
            local explain1 "直接用 local projections 估计工业产出和通胀对外生货币冲击的动态响应；Stata 18+。"
            local example2 "help lpirf"
            local explain2 "估计后继续用 irf create / graph / table 保存和比较 impulse responses。"
        }
        if "`cmd'" == "mgarch" {
            local expr_label "ccc/dcc/vcc/dvech + 多元均值方程 + arch()/garch()/distribution()"
            local example1 "mgarch dcc (toyota honda =), arch(1) garch(1) distribution(t)"
            local explain1 "拟合两资产收益的 DCC-MGARCH，并允许条件相关随时间变化。"
            local example2 "help mgarch"
            local explain2 "CCC/DCC/VCC/dvech 对协方差动态施加不同结构，不能按普通多元回归解释。"
        }
        if "`cmd'" == "dfactor" {
            local expr_label "观测方程 + 潜在动态因子方程"
            local example1 "dfactor (D.(ipman income hours unemp) =, noconstant) (f=, ar(1/2)), nolog"
            local explain1 "用一个 AR(2) 潜在因子解释四个宏观序列的一阶差分共同波动。"
            local example2 "help dfactor"
            local explain2 "观测方程与 factor 的 VAR/AR 动态都属于模型主体，应直接保留原生方程语法。"
        }
        if "`cmd'" == "sspace" {
            local expr_label "状态方程 + 观测方程 + covariance/error-form 约束"
            local example1 "help sspace"
            local explain1 "state-space 语法需要同时定义不可观测 state 与观测方程；页面保留完整原生方程主体。"
            local example2 "predict statehat, states"
            local explain2 "估计完成后可预测不可观测状态，再用 tsline 检查动态路径。"
        }
        if "`cmd'" == "xcorr" {
            local expr_label "两个时间序列 + lag() 等 cross-correlogram 设定"
            local example1 "xcorr y x"
            local explain1 "计算并绘制 y 与 x 在不同领先/滞后期的交叉相关。"
            local example2 "help xcorr"
            local explain2 "交叉相关主要用于动态先后关系探索，不能单独建立因果识别。"
        }
        if "`cmd'" == "teffects" {
            local expr_label "估计器 + 结果方程 + 处理方程（如 psmatch (y) (treat x1 x2)）"
            local example1 "teffects psmatch (y) (treat x1 x2)"
            local explain1 "使用倾向得分匹配估计处理效应。"
            local example2 "teffects ipwra (y x1 x3) (treat x1 x2)"
            local explain2 "使用双重稳健 IPWRA。"
        }
        if "`cmd'" == "eteffects" {
            local expr_label "(结果方程) + (内生处理方程)"
            local example1 "eteffects (wage tenure c.age##c.age) (college c.age##c.age i.pcollege)"
            local explain1 "用控制函数处理 college 的内生处理分配，并直接报告潜在结果框架下的处理效应。"
            local example2 "help eteffects"
            local explain2 "结果分布、处理模型和 ATE/ATET 目标按研究设计继续核对。"
        }
        if "`cmd'" == "stteffects" {
            local expr_label "估计器 + 生存结果方程 / 处理方程 / 删失方程（按估计器填写）"
            local example1 "stteffects ra (age exercise diet education) (smoke)"
            local explain1 "在已经 stset 的数据上，用生存回归调整估计 smoke 对生存时间的处理效应。"
            local example2 "stteffects ipwra (age exercise diet education) (smoke age exercise education) (age exercise diet education)"
            local explain2 "IPWRA 同时建模生存结果、处理分配和删失机制。"
        }
        if "`cmd'" == "mediate" {
            local expr_label "(结果模型) + (中介模型) + (处理变量[, 协变量])"
            local example1 "mediate (wellbeing, logit) (bonotonin, logit) (exercise)"
            local explain1 "把 exercise 的总效应分解为经 bonotonin 的间接效应和直接效应。"
            local example2 "help mediate"
            local explain2 "结果、中介和处理变量类型决定可用的模型组合。"
        }
        if "`cmd'" == "hdidregress" {
            local expr_label "估计器 + (结果方程) + (处理方程) + group() + time()"
            local example1 "hdidregress aipw (bmi medu i.girl i.sports) (hhabit parksd), group(schools) time(year)"
            local explain1 "重复截面异质 DID：AIPW 允许 ATET 随处理 cohort 和时间变化。"
            local example2 "help hdidregress"
            local explain2 "可在 RA、IPW、AIPW、TWFE 中选择；group() 和 time() 属于核心识别结构。"
        }
        if "`cmd'" == "xthdidregress" {
            local expr_label "估计器 + (结果方程) + (处理方程) + group()；面板与时间由上方 xtset 设定"
            local example1 "xthdidregress ra (registered best) (movie), group(breed)"
            local explain1 "面板异质 DID：页面运行前先按所选 panel/time 执行 xtset，再估计 cohort×time ATET。"
            local example2 "help xthdidregress"
            local explain2 "时间变量必须能够识别处理 cohort；估计器和协变量结构按研究设计核对。"
        }
        if strpos(" table prtest sdtest oneway anova ranksum median signrank signtest bitesti tabi ", " `cmd' ") {
            local expr_label "检验 / 表格主体（变量、分组、比较值或计数参数）"
            local example1 "help `cmd'"
            local explain1 "这些命令的变量角色和参数顺序差异较大，页面保留官方原生命令主体，避免把分组变量或比较值误标成解释变量。"
        }
        if "`cmd'" == "exlogistic" {
            local expr_label "二元/二项结果变量 + 解释变量"
            local example1 "exlogistic response treatment gender hypertension"
            local explain1 "使用 exact logistic 对小样本二元结果做条件精确推断。"
            local example2 "help exlogistic"
            local explain2 "条件化变量、内存/时间限制与 Monte Carlo 设置属于精确估计的重要选项。"
        }
        if "`cmd'" == "expoisson" {
            local expr_label "计数结果变量 + 解释变量 + exposure()/offset() 等设定"
            local example1 "expoisson y x1 x2"
            local explain1 "对计数结果执行 exact Poisson 回归。"
            local example2 "help expoisson"
            local explain2 "暴露量、条件化和计算控制选项运行前按当前 help 核对。"
        }
        if "`cmd'" == "bitest" {
            local expr_label "二元变量 = 原假设概率（如 outcome = .5）"
            local example1 "bitest outcome = .5"
            local explain1 "检验二元 outcome 的成功概率是否等于 0.5，使用精确二项分布。"
            local example2 "help bitest"
            local explain2 "即时汇总数据可改用 bitesti。"
        }
        if "`cmd'" == "ksmirnov" {
            local expr_label "变量 = 理论 CDF 表达式，或变量 + by() 两样本分组"
            local example1 "ksmirnov x, by(group)"
            local explain1 "比较 group 两组的经验分布是否相同。"
            local example2 "help ksmirnov"
            local explain2 "单样本检验需要提供理论累计分布函数表达式。"
        }
        if "`cmd'" == "symmetry" {
            local expr_label "配对/方阵分类变量 + exact 等检验选项"
            local example1 "symmetry before after, exact"
            local explain1 "检验配对分类结果 before/after 的对称性，并请求精确检验。"
            local example2 "help symmetry"
            local explain2 "边际同质与 exact 选项按表结构继续核对。"
        }
        if "`cmd'" == "tetrachoric" {
            local expr_label "两个或多个二元变量"
            local example1 "tetrachoric y x1 x2"
            local explain1 "估计二元变量背后潜在连续变量之间的 tetrachoric correlation。"
            local example2 "help tetrachoric"
            local explain2 "变量应具有二元编码；多变量时返回相关矩阵。"
        }
        if strpos(" cc cs ir ", " `cmd' ") {
            local expr_label "流行病学命令主体（病例 / 暴露 / 时间 / 分层参数）"
            local example1 "help `cmd'"
            local explain1 "病例对照、队列和发病率命令的变量角色不同，按当前 help 填写完整主体。"
        }
        if "`cmd'" == "mcc" {
            local expr_label "病例暴露变量 + 配对对照暴露变量（1:1 matched pairs）"
            local example1 "mcc smoke1 smoke0"
            local explain1 "每行是一对 matched case-control；smoke1 为病例暴露，smoke0 为其配对对照暴露。"
            local example2 "help mcc"
            local explain2 "mcc 适用于 1:1 配对；1:M 匹配应转用条件 logistic 等方法。"
        }
        if "`cmd'" == "dstdize" {
            local expr_label "事件变量 + 人口/权重变量 + 标准化分层变量 + by()/using()"
            local example1 "dstdize deaths pop age_group, by(state)"
            local explain1 "按 age_group 对各 state 的率做标准化；实际标准人口来源需结合研究设计核对。"
            local example2 "help dstdize"
            local explain2 "直接/间接标准化、外部标准人口和保存选项请按当前 Stata help 设置。"
        }
        if "`cmd'" == "gnbreg" {
            local expr_label "计数 Y + 均值方程 X + lnalpha() 离散参数方程"
            local example1 "gnbreg y x1 x2, lnalpha(z1 z2)"
            local explain1 "均值由 x1、x2 解释，同时允许负二项离散参数 alpha 随 z1、z2 系统变化。"
            local example2 "help gnbreg"
            local explain2 "当 dispersion 无需协变量解释时，普通 nbreg 更直接；lnalpha() 应有明确异质性依据。"
        }
        if "`cmd'" == "cpoisson" {
            local expr_label "计数 Y + X + ll()/ul() 删失界限"
            local example1 "cpoisson accidents i.past i.parent i.ntickets, ul(3) irr"
            local explain1 "3 表示 3 次及以上时，用 ul(3) 处理右删失计数并报告 incidence-rate ratios。"
            local example2 "help cpoisson"
            local explain2 "删失保留观测但隐藏界限外真实计数；截断则是整个观测未进入样本。"
        }
        if "`cmd'" == "binreg" {
            local expr_label "二元结果 Y + X + rr/rd/or 或 link() 报告尺度"
            local example1 "binreg y x1 x2, rr"
            local explain1 "用 binomial GLM 估计风险比；rr 决定报告尺度。"
            local example2 "binreg y x1 x2, rd"
            local explain2 "改用风险差尺度；研究问题应先明确需要 RR、RD 还是 OR。"
        }
        if "`cmd'" == "biprobit" {
            local expr_label "两个二元 Probit 方程（每个方程一组括号）"
            local example1 "biprobit (private years) (vote logptax loginc)"
            local explain1 "联合估计 private 与 vote 两个二元结果，并允许两方程潜在误差相关。"
            local example2 "help biprobit"
            local explain2 "递归设定、约束和边际效应应结合两方程的识别结构核对。"
        }
        if "`cmd'" == "hetoprobit" {
            local expr_label "序数 Y + X + het() 异方差方程"
            local example1 "hetoprobit health age bmi i.exercise, het(age)"
            local explain1 "主方程解释有序健康状态，het(age) 让潜在误差尺度随年龄变化。"
            local example2 "help hetoprobit"
            local explain2 "异方差方程变量应有明确的尺度异质性依据。"
        }
        if "`cmd'" == "ziologit" {
            local expr_label "序数 Y + X + inflate() 零膨胀/最低类别生成方程"
            local example1 "ziologit tobacco education income i.female, inflate(income education i.parent)"
            local explain1 "有序 logit 方程解释吸烟强度，inflate() 区分额外最低类别来源。"
            local example2 "help ziologit"
            local explain2 "该命令从 Stata 17 开始提供；两套预测变量可以不同。"
        }
        if "`cmd'" == "zioprobit" {
            local expr_label "序数 Y + X + inflate() 零膨胀/最低类别生成方程"
            local example1 "zioprobit tobacco income i.female age, inflate(income i.female age i.parent i.religion)"
            local explain1 "有序 probit 方程和 inflation probit 方程共同解释最低类别的两个来源。"
            local example2 "help zioprobit"
            local explain2 "最低类别的数值不必等于 0；关键是存在额外生成机制。"
        }
        if "`cmd'" == "clogit" {
            local expr_label "二元结果 Y + X + group() 条件组/匹配组"
            local example1 "clogit case exposure x1 x2, group(matchid)"
            local explain1 "在每个 matchid 内条件化，适合匹配病例对照或组固定效应二元模型。"
            local example2 "help clogit"
            local explain2 "同组内不变化的变量无法识别；组定义属于核心设计信息。"
        }
        if "`cmd'" == "slogit" {
            local expr_label "多类别结果 Y + X + stereotype dimension / constraints"
            local example1 "slogit y x1 x2"
            local explain1 "拟合 stereotype logistic model，在多项 logit 与有序结构之间提供更紧凑参数化。"
            local example2 "help slogit"
            local explain2 "维度、约束和结果类别解释应结合具体分类结构设置。"
        }
        if "`cmd'" == "cmset" {
            local expr_label "case ID + time（面板时）+ alternatives 变量"
            local example1 "cmset id travelmode"
            local explain1 "横截面选择数据：id 标识 choice case，travelmode 标识备选项。"
            local example2 "cmset id t alt"
            local explain2 "重复选择/面板数据：同时声明个体 id、时间 t 和备选项 alt。"
        }
        if "`cmd'" == "cmsummarize" {
            local expr_label "要按 chosen alternatives 汇总的 choice-data 变量（可留空看默认）"
            local example1 "cmsummarize"
            local explain1 "在已 cmset 的数据上查看 choice-data 的总体结构与变量摘要。"
            local example2 "help cmsummarize"
            local explain2 "先 cmset，再用本页确认备选项变量与 case-specific 变量分布。"
        }
        if "`cmd'" == "cmchoiceset" {
            local expr_label "choice-set 检查参数（已 cmset 后运行）"
            local example1 "cmchoiceset"
            local explain1 "检查 choice sets 的规模和可用备选项，发现不平衡或异常选择集。"
            local example2 "help cmchoiceset"
            local explain2 "适合正式估计前做 choice-set 结构诊断。"
        }
        if "`cmd'" == "cmtab" {
            local expr_label "要按 chosen alternative 列联/汇总的变量"
            local example1 "cmtab"
            local explain1 "查看各备选项被选择的频数与选择结构。"
            local example2 "help cmtab"
            local explain2 "可进一步按 choice-data covariates 做列联检查。"
        }
        if "`cmd'" == "cmsample" {
            local expr_label "估计命令后的 sample-exclusion 诊断参数（通常可留空）"
            local example1 "cmsample"
            local explain1 "报告 choice model 样本被排除的原因，适合估计后诊断。"
            local example2 "help cmsample"
            local explain2 "先成功运行兼容的 cm estimation command。"
        }
        if "`cmd'" == "cmclogit" {
            local expr_label "chosen 指示 + alternative-specific X + casevars() 个体/案例变量"
            local example1 "cmclogit chosen time, casevars(income partysize)"
            local explain1 "time 随备选项变化；income、partysize 在同一 choice case 内不变，放入 casevars()。"
            local example2 "help cmclogit"
            local explain2 "运行前先 cmset；casevars() 与 alternative-specific variables 的角色必须分清。"
        }
        if "`cmd'" == "cmmixlogit" {
            local expr_label "chosen + 固定系数变量 + random() 随机系数 + casevars()"
            local example1 "cmmixlogit choice mfee, random(price) casevars(traffic)"
            local explain1 "mfee 固定系数，price 随机系数，traffic 为 case-specific 变量。"
            local example2 "help cmmixlogit"
            local explain2 "随机系数分布和相关结构决定如何放松 IIA，属于核心模型设定。"
        }
        if "`cmd'" == "cmxtmixlogit" {
            local expr_label "chosen + 固定系数变量 + random() + casevars()；先 cmset panel/time/alt"
            local example1 "cmxtmixlogit choice trcost, random(trtime) casevars(age income)"
            local explain1 "对重复选择数据拟合 panel mixed logit；运行前应先用 cmset id t alt。"
            local example2 "help cmxtmixlogit"
            local explain2 "面板相关由随机系数建模，choice-data 结构由 cmset 声明。"
        }
        if "`cmd'" == "cmmprobit" {
            local expr_label "chosen + alternative-specific X + casevars()/scale()/correlation 设定"
            local example1 "help cmmprobit"
            local explain1 "multinomial probit 允许备选项误差相关；协方差结构和尺度约束属于模型核心。"
            local example2 "cmmprobit chosen time, casevars(income)"
            local explain2 "示意：time 是 alternative-specific，income 是 case-specific；运行前先 cmset。"
        }
        if "`cmd'" == "cmroprobit" {
            local expr_label "排名结果 + alternative-specific X + casevars()/协方差设定"
            local example1 "help cmroprobit"
            local explain1 "用于完整或部分排名的 rank-ordered probit，保留原生主体以表达 ranking 与协方差结构。"
            local example2 "cmroprobit rank x1 x2"
            local explain2 "示意：rank 是备选项排名；正式运行前按数据的排名编码核对。"
        }
        if "`cmd'" == "cmrologit" {
            local expr_label "排名结果 + alternative-specific X + casevars()/ties 设定"
            local example1 "help cmrologit"
            local explain1 "rank-ordered logit 可处理完整/不完整排名及 ties；先 cmset 并确认 ranking 编码。"
            local example2 "cmrologit rank x1 x2"
            local explain2 "示意：rank 为备选项顺序，x1、x2 为备选项特征。"
        }
        if "`cmd'" == "nlogit" {
            local expr_label "chosen + X + || 多层 nest tree + case()/base() 等结构"
            local example1 "nlogit chosen cost distance rating || type: income kids, base(family) || restaurant:, noconst case(family_id)"
            local explain1 "nested logit 的树层级直接写在 || 结构中；tree 需要事先按研究中的嵌套逻辑定义。"
            local example2 "help nlogit"
            local explain2 "多层 nesting、inclusive-value constraints 和 base alternatives 都属于识别结构。"
        }
        if "`cmd'" == "pkexamine" {
            local expr_label "时间变量 + 浓度变量 + if/in；可加 graph/trapezoid/fit()"
            local example1 "pkexamine time concentration, graph"
            local explain1 "从单个 subject 的 concentration–time 数据计算 AUC、Cmax、Tmax、elimination rate 和 half-life，并绘图。"
            local example2 "help pkexamine"
            local explain2 "对多 subject 数据通常先按 id 选择个体，或使用 pksumm 汇总全部 subjects 的 PK measures。"
        }
        if "`cmd'" == "pksumm" {
            local expr_label "subject ID + 时间变量 + 浓度变量 + graph/stat() 等汇总设定"
            local example1 "pksumm id time conc"
            local explain1 "对每个 subject 计算常见 PK measures，再汇总其均值、中位数、方差、偏度、峰度和正态性检验。"
            local example2 "pksumm id time conc, graph stat(auc)"
            local explain2 "在汇总全部 PK measures 的同时绘制 AUC 分布；stat() 可换成 half、ke、cmax 等。"
        }
        if "`cmd'" == "pkcross" {
            local expr_label "结果变量 + param() + id()/sequence()/treatment()/period() crossover 设计字段"
            local example1 "pkcross y, param(3) id(idvar) sequence(seq) treatment(treat) period(period)"
            local explain1 "分析 crossover experiment；显式给出 subject、sequence、treatment 与 period 角色。"
            local example2 "help pkcross"
            local explain2 "carryover、period 与 sequence 效应应结合 crossover 设计核对，不能按普通独立样本比较解释。"
        }
        if "`cmd'" == "pkequiv" {
            local expr_label "PK measure + treatment + period + sequence + subject ID + equivalence limits"
            local example1 "pkequiv auc treat period sequence id, limit(0.1) notost noboot"
            local explain1 "对 AUC 进行 crossover bioequivalence 分析，并把等效界限设为 10%。"
            local example2 "help pkequiv"
            local explain2 "bioequivalence 的 limit、TOST/CI 和 bootstrap 设定应来自研究方案与监管口径。"
        }
        if "`cmd'" == "pkcollapse" {
            local expr_label "时间变量 + 一个或多个浓度变量 + id() + stat()/keep()"
            local example1 "pkcollapse time conc1 conc2, id(id) stat(auc) keep(seq)"
            local explain1 "把原始 concentration–time 记录压缩为 subject-level PK measurement 数据，同时保留 seq。"
            local example2 "help pkcollapse"
            local explain2 "pkcollapse 会重构当前内存数据；运行前保存原始 concentration–time 明细。"
        }
        if "`cmd'" == "pkshape" {
            local expr_label "subject ID + sequence + period measurements + order()"
            local example1 "pkshape id seq period1 period2, order(RT TR)"
            local explain1 "把 2×2 crossover/Latin-square 的宽表 period measurements 重塑为 outcome、treat、carry、period 等长表字段。"
            local example2 "help pkshape"
            local explain2 "pkshape 会直接重组内存数据；order() 必须与实际 treatment sequence 一致，运行前先保存原数据。"
        }
        if "`cmd'" == "hetregress" {
            local expr_label "Y + X + het() 方差方程 + ML/twostep 等估计设定"
            local example1 "hetregress y x1 x2, het(z1 z2)"
            local explain1 "均值方程用 x1、x2，het() 中 z1、z2 建模残差方差。"
            local example2 "help hetregress"
            local explain2 "方差方程是否合理直接影响效率与推断；可按研究设计选择 ML 或 two-step GLS。"
        }
        if "`cmd'" == "sqreg" {
            local expr_label "Y + X + quantiles() + reps() 等同时分位数设定"
            local example1 "sqreg y x1 x2, quantile(.25 .5 .75) reps(100)"
            local explain1 "同时估计第 25、50、75 百分位，并用 bootstrap 得到跨分位数协方差。"
            local example2 "help sqreg"
            local explain2 "适合需要正式比较不同分位点系数的场景。"
        }
        if "`cmd'" == "intreg" {
            local expr_label "结果下界 + 结果上界 + X"
            local example1 "intreg ylower yupper x1 x2"
            local explain1 "ylower、yupper 表示区间结果的下界和上界；相等可表示精确观测，缺失可表示单侧删失。"
            local example2 "help intreg"
            local explain2 "区间、左删失、右删失和精确观测可在同一模型中组合。"
        }
        if "`cmd'" == "tobit" {
            local expr_label "Y + X + ll()/ul() 删失界限"
            local example1 "tobit y x1 x2, ll(0)"
            local explain1 "对在 0 处左删失的连续结果估计 Tobit 模型。"
            local example2 "tobit y x1 x2, ll(0) ul(100)"
            local explain2 "同时指定左右删失界限。"
        }
        if "`cmd'" == "truncreg" {
            local expr_label "Y + X + ll()/ul() 截断界限"
            local example1 "truncreg y x1 x2, ll(0)"
            local explain1 "样本只观察到 y>0 的个体时，用左截断回归修正抽样机制。"
            local example2 "help truncreg"
            local explain2 "截断意味着界限外观测整体未进入样本；界限必须对应真实抽样规则。"
        }
        if "`cmd'" == "churdle" {
            local expr_label "结果模型类型 + Y + X + select() hurdle 方程 + ll()/ul() 界限"
            local example1 "churdle linear money dating teenager nkids, select(newborn hours distance weekends) ll(0)"
            local explain1 "正值部分用线性模型解释 money，select() 用 Probit 建模是否跨过 0 这一 hurdle。"
            local example2 "help churdle"
            local explain2 "可选择 linear、exponential 或 probit outcome model；hurdle 方程与结果方程可使用不同变量。"
        }
        if "`cmd'" == "boxcox" {
            local expr_label "Y + X + model()/lrtest 等 Box–Cox 变换设定"
            local example1 "boxcox y x1 x2, model(lhsonly)"
            local explain1 "只对因变量侧估计 Box–Cox 变换参数。"
            local example2 "help boxcox"
            local explain2 "lhs、rhs 或两侧变换的模型形式不同，运行前明确变量必须为正等数据要求。"
        }
        if "`cmd'" == "fp" {
            local expr_label "<连续变量> + FP options + 冒号后的估计命令"
            local example1 "fp <age>, scale: regress y x <age>"
            local explain1 "让 Stata 在候选 fractional powers 中为 age 选择函数形式，再估计线性回归。"
            local example2 "help fp"
            local explain2 "fp 是前缀工作流；尖括号标记参与 fractional-polynomial 搜索的连续变量。"
        }
        if "`cmd'" == "nl" {
            local expr_label "非线性方程（参数写在 {} 中，可给初值）"
            local example1 "nl (y = {b0=1}*(1-exp(-{b1=.1}*x)))"
            local explain1 "直接在方程中定义非线性函数和参数初值，用 nonlinear least squares 估计。"
            local example2 "help nl"
            local explain2 "复杂函数也可封装成 function evaluator program。"
        }
        if "`cmd'" == "nlsur" {
            local expr_label "多个非线性方程（每个方程一组括号，共享参数可复用同名 {}）"
            local example1 "nlsur (y1 = {a1}*x1 + {a2}*x2) (y2 = {b1}*x1 + {b2}*x2)"
            local explain1 "联合估计两个非线性方程，并允许方程误差相关。"
            local example2 "help nlsur"
            local explain2 "需求系统等复杂模型常需自定义 evaluator；参数约束应显式记录。"
        }
        if "`cmd'" == "gmm" {
            local expr_label "矩条件 / 残差方程 + instruments() + weight/VCE 设定"
            local example1 "gmm (y - {b0} - {b1}*x), instruments(z x)"
            local explain1 "指定一个残差矩条件，并用 z、x 作为工具变量进行 GMM 估计。"
            local example2 "help gmm"
            local explain2 "非线性、多方程、动态或面板矩条件应直接保留原生表达式结构。"
        }
        if "`cmd'" == "reg3" {
            local expr_label "多个线性方程括号 + 2sls/3sls/sure 等系统估计设定"
            local example1 "reg3 (y1 x1 x2) (y2 y1 z1), 3sls"
            local explain1 "把两条联立线性方程作为系统，用三阶段最小二乘联合估计。"
            local example2 "help reg3"
            local explain2 "内生变量、排除限制和跨方程识别条件应在运行前明确。"
        }
        if "`cmd'" == "frontier" {
            local expr_label "Y + X + production/cost + distribution()/uhet()/vhet() 等前沿设定"
            local example1 "frontier y x1 x2"
            local explain1 "默认拟合生产随机前沿模型。"
            local example2 "frontier lncost lnout lnp_l lnp_k, cost"
            local explain2 "加 cost 后拟合成本前沿；效率方向与生产前沿不同。"
        }
        if strpos(" sureg mvreg canon manova ", " `cmd' ") {
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
        if "`cmd'" == "ca" {
            local expr_label "行类别变量 + 列类别变量（可含 crossed variables）"
            local example1 "ca rowcat colcat"
            local explain1 "对 rowcat × colcat 列联表执行简单对应分析。"
            local example2 "help ca"
            local explain2 "crossed variables、normalization 和图形设定按研究任务继续核对。"
        }
        if "`cmd'" == "candisc" {
            local expr_label "判别变量 + group() 已知组别"
            local example1 "candisc x1 x2 x3, group(group)"
            local explain1 "用 x1–x3 构造典型判别函数来区分已知 group。"
            local example2 "help candisc"
            local explain2 "组别变量和判别变量都属于核心输入。"
        }
        if "`cmd'" == "hotelling" {
            local expr_label "多元变量 + by() 或 mu() 比较设定"
            local example1 "hotelling x1 x2, by(group)"
            local explain1 "比较两个 group 在 x1、x2 联合均值向量上的差异。"
            local example2 "help hotelling"
            local explain2 "单样本、配对或两组设定按当前 help 选择。"
        }
        if "`cmd'" == "mca" {
            local expr_label "多个分类变量 + dimensions()/method() 等 MCA/JCA 设定"
            local example1 "mca q1 q2 q3"
            local explain1 "对 q1–q3 执行多重对应分析。"
            local example2 "help mca"
            local explain2 "维数和 joint correspondence 等设定按数据结构核对。"
        }
        if "`cmd'" == "mds" {
            local expr_label "变量列表 + method()/measure()/dimensions() 等 MDS 设定"
            local example1 "mds x1 x2 x3"
            local explain1 "根据观测之间的多变量距离构造低维配置。"
            local example2 "help mds"
            local explain2 "metric/nonmetric、距离度量和维数是核心模型设定。"
        }
        if "`cmd'" == "mdslong" {
            local expr_label "距离变量 + id() / pair identifiers + MDS 设定"
            local example1 "help mdslong"
            local explain1 "输入是对象两两距离的长表；先核对对象 ID 和距离变量角色。"
            local example2 "mdslong ..."
            local explain2 "页面保留原生命令主体，避免把 long-format proximity 数据误当普通 X 变量。"
        }
        if "`cmd'" == "mdsmat" {
            local expr_label "距离 / 相异度矩阵名 + MDS 设定"
            local example1 "help mdsmat"
            local explain1 "输入核心是 Stata matrix，而非当前数据中的普通变量列表。"
            local example2 "mdsmat D"
            local explain2 "示意：对事先准备的相异度矩阵 D 做 MDS。"
        }
        if "`cmd'" == "mvtest" {
            local expr_label "子命令 + 变量与检验设定（means/correlations/covariances/normality）"
            local example1 "mvtest normality x1 x2 x3"
            local explain1 "检验 x1–x3 的多元正态性。"
            local example2 "help mvtest"
            local explain2 "不同子命令的假设与参数结构不同，第一步先明确检验目标。"
        }
        if "`cmd'" == "procrustes" {
            local expr_label "目标配置 + 来源配置 + transformation options"
            local example1 "help procrustes"
            local explain1 "Procrustes 比较两组多维配置；变量需要成对对应。"
            local example2 "procrustes ..."
            local explain2 "旋转、平移和缩放限制按比较目标设置。"
        }
        if strpos(" heckman heckprobit heckoprobit heckpoisson ", " `cmd' ") {
            local expr_label "结果方程 + select() 选择方程（两套变量角色必须同时明确）"
            if "`cmd'" == "heckman" {
                local example1 "heckman wage educ age, select(married children educ age)"
                local explain1 "连续结果 wage 只在被选择样本中观察；select() 描述进入样本的机制。"
                local example2 "help heckman"
                local explain2 "需要显式选择指示变量、两步法或 VCE 设置时继续核对当前 help。"
            }
            else if "`cmd'" == "heckprobit" {
                local example1 "heckprobit y x1 x2, select(selected = z1 z2 x1)"
                local explain1 "主方程是二元 Probit；selected 及 z1、z2、x1 构成选择方程。"
                local example2 "help heckprobit"
                local explain2 "运行前确认选择指示的 0/1 编码和排除限制。"
            }
            else if "`cmd'" == "heckoprobit" {
                local example1 "heckoprobit satisfaction educ age, select(work=educ age i.married##c.children)"
                local explain1 "主结果是有序类别，work 方程描述结果被观察到的选择过程。"
                local example2 "help heckoprobit"
                local explain2 "阈值、选择方程和标准误设置都应按研究设计核对。"
            }
            else {
                local example1 "heckpoisson patents investment i.firmtype, select(applied = investment size i.firmtype)"
                local explain1 "主方程解释计数结果 patents，applied 方程处理非随机样本选择。"
                local example2 "help heckpoisson"
                local explain2 "选择机制与计数过程应分别有清楚的经济含义。"
            }
        }
        if strpos(" eregress eprobit eoprobit eintreg ", " `cmd' ") {
            local expr_label "主结果方程 + endogenous()/select()/entreat() 等扩展方程"
            if "`cmd'" == "eregress" {
                local example1 "eregress y x1, endogenous(x2 = x3 x4)"
                local explain1 "在线性结果方程中把 x2 作为内生协变量，并用 x3、x4 建模。"
            }
            else if "`cmd'" == "eprobit" {
                local example1 "eprobit y x1, endogenous(x2 = x3 x4)"
                local explain1 "二元 Probit 结果方程，同时显式建立 x2 的内生协变量方程。"
            }
            else if "`cmd'" == "eoprobit" {
                local example1 "eoprobit y x1, endogenous(x2 = x3 x4)"
                local explain1 "有序 Probit 结果方程，同时显式建立 x2 的内生协变量方程。"
            }
            else {
                local example1 "eintreg ylower yupper x1, endogenous(x2 = x3 x4)"
                local explain1 "区间结果必须同时给出下界和上界，再加入内生协变量方程。"
            }
            local example2 "help `cmd'"
            local explain2 "ERM 还可组合 select() 与 entreat()；复杂联立结构运行前核对当前 Stata help。"
        }
        if "`cmd'" == "ctset" {
            local expr_label "时间 + 失败数 + 失访数 + 进入数 + by()（count-time 数据声明）"
            local example1 "ctset time failures lost entered, by(group)"
            local explain1 "把聚合的 count-time 生存表声明为 Stata count-time 数据；进入、失败和失访人数需要在各组内平衡。"
            local example2 "help ctset"
            local explain2 "ctset 后通常用 cttost 转成 st 数据，再进入 sts/streg/stcox 等工作流。"
        }
        if "`cmd'" == "cttost" {
            local expr_label "count-time → survival-time 转换 options"
            local example1 "cttost, clear"
            local explain1 "把已 ctset 的聚合 count-time 数据转换成 st 数据；clear 会重写当前内存数据。"
            local example2 "help cttost"
            local explain2 "转换前应保存原始数据，并检查 ctset 中进入、失败和失访人数是否一致。"
        }
        if "`cmd'" == "ltable" {
            local expr_label "时间变量 + 失败状态变量 + interval()/by()/failure 等 life-table 设定"
            local example1 "ltable studytime died, failure graph"
            local explain1 "按 actuarial life-table 方法汇总 studytime 与 died，并绘制失败函数。"
            local example2 "help ltable"
            local explain2 "ltable 会按区间聚合；若需要精确 Kaplan–Meier 风险集，优先使用 sts list/graph。"
        }
        if "`cmd'" == "snapspan" {
            local expr_label "subject ID + snapshot 时间 + 状态变量 + generate() 起点变量"
            local example1 "help snapspan"
            local explain1 "把 snapshot 记录转换为 time-span 记录；转换会重构每个 subject 的时间区间。"
            local example2 "stset endtime, id(id) time0(starttime) failure(event)"
            local explain2 "snapspan 后通常继续 stset；先核对生成的起止时间与状态变量。"
        }
        if "`cmd'" == "stdescribe" {
            local expr_label "已 stset 数据的结构描述 options（通常直接运行）"
            local example1 "stdescribe"
            local explain1 "检查 subjects、records、entry/exit time、gaps、time at risk 和 failures。"
            local example2 "help stdescribe"
            local explain2 "适合放在 stset 后第一步，先确认数据结构再估计生存模型。"
        }
        if "`cmd'" == "stsum" {
            local expr_label "by() 等生存时间汇总设定"
            local example1 "stsum, by(group)"
            local explain1 "按 group 汇总 time at risk、失败数和生存时间分布。"
            local example2 "help stsum"
            local explain2 "与普通 summarize 不同，stsum 使用 stset 后的 risk-time 定义。"
        }
        if "`cmd'" == "stci" {
            local expr_label "by() + mean/p() 等生存时间置信区间设定"
            local example1 "stci, by(group)"
            local explain1 "按 group 报告平均/中位等生存时间及置信区间。"
            local example2 "help stci"
            local explain2 "估计对象来自当前 stset 的 survivor function，分组和权重限制运行前核对。"
        }
        if "`cmd'" == "stcurve" {
            local expr_label "survival/failure/hazard/chazard + at() 等上一模型后曲线设定"
            local example1 "stcurve, survival"
            local explain1 "在兼容的 streg、stcox、stcrreg、stintreg 或 stintcox 估计后绘制调整后的生存函数。"
            local example2 "stcurve, cif"
            local explain2 "在 competing-risks 模型后可绘制 cumulative incidence function。"
        }
        if "`cmd'" == "stbase" {
            local expr_label "从已 stset 数据构造 baseline dataset 的 at()/failure 等设定"
            local example1 "help stbase"
            local explain1 "把多记录 survival-time 数据压成 baseline 数据；属于数据重构操作，运行前先保存当前数据。"
            local example2 "stdescribe"
            local explain2 "重构后重新检查 subject、entry/exit 和 failure 定义。"
        }
        if "`cmd'" == "stfill" {
            local expr_label "要在 subject 历史内 carry forward/backward 的协变量"
            local example1 "help stfill"
            local explain1 "在同一 subject 的多段记录之间填充协变量值；会修改当前数据中的变量。"
            local example2 "stvary"
            local explain2 "填充后用 stvary 检查哪些协变量仍随时间变化。"
        }
        if "`cmd'" == "stgen" {
            local expr_label "新变量 = survival-history function()"
            local example1 "help stgen"
            local explain1 "按每个 subject 的完整生存历史生成累计、首次/末次事件时间等派生变量。"
            local example2 "describe"
            local explain2 "生成后检查变量含义和记录级/subject 级重复方式，再进入模型。"
        }
        if "`cmd'" == "stsplit" {
            local expr_label "新时间段变量 + at()/after()/every() 等切分规则"
            local example1 "stsplit ageband, at(20(5)80)"
            local explain1 "把每个 subject 的风险时间按 5 年年龄段切成多条 time-span 记录。"
            local example2 "help stsplit"
            local explain2 "stsplit 会增加记录数并改变数据形态；切分后重新 stdescribe 检查 gaps 和 risk time。"
        }
        if "`cmd'" == "stvary" {
            local expr_label "要检查是否随时间变化的协变量列表"
            local example1 "stvary x1 x2"
            local explain1 "检查 x1、x2 在同一 subject 的多段记录中是否发生变化。"
            local example2 "help stvary"
            local explain2 "适合在构造 time-varying covariates 或 stfill 后验证数据。"
        }
        if "`cmd'" == "sttocc" {
            local expr_label "match() + number() 等 nested case-control 抽样设定"
            local example1 "sttocc, match(sex agegroup) number(4)"
            local explain1 "从 stset cohort 的每个 failure risk set 中抽取最多 4 个按 sex、agegroup 匹配的 controls。"
            local example2 "help sttocc"
            local explain2 "该命令会生成 nested case-control 数据；抽样前保存完整 cohort，并确认 risk-set 定义。"
        }
        if "`cmd'" == "sttoct" {
            local expr_label "survival-time → count-time 聚合转换设定"
            local example1 "help sttoct"
            local explain1 "把 st 数据转换成 count-time 表；属于数据重构操作，运行前先保存原始 survival-time 数据。"
            local example2 "ctset"
            local explain2 "转换后用 ctset 检查 time、failure、lost/entered 与分组定义。"
        }
        if "`cmd'" == "stir" {
            local expr_label "二元 exposure + by()/level() 等 incidence-rate ratio 设定"
            local example1 "stir exposed"
            local explain1 "比较 exposed=1 与 exposed=0 的 incidence rate 并报告 incidence-rate ratio。"
            local example2 "help stir"
            local explain2 "exposure 应是二元变量；多分类率比较更适合 strate/stptime。"
        }
        if "`cmd'" == "strate" {
            local expr_label "一个或多个分组变量 + per()/smr() 等 failure-rate 设定"
            local example1 "strate group, per(1000)"
            local explain1 "按 group 报告每 1,000 person-time 的 failure rate。"
            local example2 "help strate"
            local explain2 "可进一步计算 SMR；分母来自当前 stset 的 person-time。"
        }
        if "`cmd'" == "stptime" {
            local expr_label "by() + per()/smr() 等 person-time 率汇总设定"
            local example1 "stptime, by(group) per(1000)"
            local explain1 "按 group 汇总 person-time、failure 数和每 1,000 person-time 的 incidence rate。"
            local example2 "help stptime"
            local explain2 "适合直接查看风险人时与率；率比检验可进一步使用 stir/stmh/stmc。"
        }
        if inlist("`cmd'", "stmh", "stmc") {
            local expr_label "二元 exposure + by() 分层变量（Mantel–Haenszel / Mantel–Cox rate ratio）"
            local example1 "help `cmd'"
            local explain1 "在分层 person-time 数据中计算调整后的 rate ratio；分层变量和 exposure 编码应先核对。"
            local example2 "strate"
            local explain2 "先用 strate/stptime 检查各层 person-time 和 failures，再进行分层率比汇总。"
        }
        if "`cmd'" == "stintreg" {
            local expr_label "协变量 + interval(下界 上界) + distribution() 区间删失生存设定"
            local example1 "stintreg i.stage, interval(ltime rtime) distribution(weibull)"
            local explain1 "用 ltime/rtime 表示事件发生区间，并拟合 Weibull 参数生存模型。"
            local example2 "help stintreg"
            local explain2 "区间、左、右删失都由 interval() 边界表达；分布假设应结合研究对象与诊断确定。"
        }
        if "`cmd'" == "stintcox" {
            local expr_label "协变量 + interval(下界 上界)；区间删失 Cox 比例风险模型"
            local example1 "stintcox age_mean i.male i.needle i.inject i.jail, interval(ltime rtime)"
            local explain1 "在事件仅能定位到时间区间时拟合半参数 Cox 比例风险模型；该入口仅在 Stata 17+ 展示。"
            local example2 "help stintcox"
            local explain2 "interval() 的左右端点定义属于数据结构核心，比例风险设定仍需结合研究设计检查。"
        }
        if "`cmd'" == "arima" {
            local expr_label "结果变量 + 外生变量（可选）+ ARIMA 阶数 / AR-MA 设定"
            local example1 "arima y, arima(1,0,1)"
            local explain1 "估计 ARIMA(1,0,1)；阶数是模型核心设定。"
            local example2 "arima y x1 x2, arima(1,0,0)"
            local explain2 "在 AR(1) 动态回归中加入 x1、x2 外生解释变量。"
        }
        if "`cmd'" == "arch" {
            local expr_label "结果变量 + 均值方程变量（可选）+ arch()/garch() 等波动设定"
            local example1 "arch y, arch(1) garch(1)"
            local explain1 "估计标准 GARCH(1,1) 波动模型。"
            local example2 "arch y x1, arch(1) garch(1)"
            local explain2 "在均值方程加入 x1，同时估计 GARCH(1,1)。"
        }
        if "`cmd'" == "ucm" {
            local expr_label "结果变量 + 外生变量（可选）+ seasonal()/cycle() 等成分"
            local example1 "ucm y, seasonal(12) cycle(1)"
            local explain1 "按 12 期季节项和一阶周期成分拟合不可观测成分模型。"
            local example2 "help ucm"
            local explain2 "趋势、季节和周期成分取决于研究设计；运行前核对当前 Stata 版本支持的成分。"
        }
        if "`cmd'" == "dfuller" {
            local expr_label "待检验序列 + lags() / trend 等 ADF 设定"
            local example1 "dfuller y, lags(1)"
            local explain1 "对 y 进行带 1 阶增广项的 Dickey–Fuller 单位根检验。"
            local example2 "dfuller y, lags(1) trend"
            local explain2 "在检验回归中加入确定性时间趋势。"
        }
        if "`cmd'" == "pperron" {
            local expr_label "待检验序列 + Newey–West 滞后 / trend 等设定"
            local example1 "pperron y"
            local explain1 "对 y 进行 Phillips–Perron 单位根检验。"
            local example2 "pperron y, trend"
            local explain2 "在检验回归中加入确定性时间趋势。"
        }
        if "`cmd'" == "corrgram" {
            local expr_label "待诊断序列 + lags() 等相关图设定"
            local example1 "corrgram y, lags(12)"
            local explain1 "查看 y 到 12 阶的自相关、偏自相关和 Q 统计量。"
        }
        if "`cmd'" == "pergram" {
            local expr_label "待分析序列 + periodogram options"
            local example1 "pergram y"
            local explain1 "绘制 y 的 periodogram，用于查看周期频率结构。"
        }
        if "`cmd'" == "var" {
            local expr_label "系统内生变量 + lags() 等 VAR 设定"
            local example1 "var y1 y2, lags(1/2)"
            local explain1 "把 y1、y2 都作为内生变量估计 1 至 2 阶 VAR。"
        }
        if "`cmd'" == "svar" {
            local expr_label "系统变量 + lags() + A/B 识别矩阵（aeq()/beq()）"
            local example1 "help svar"
            local explain1 "SVAR 需要由识别假设定义 A/B 矩阵；先核对官方示例再填写。"
            local example2 "svar y1 y2, lags(1/2) aeq(A) beq(B)"
            local explain2 "使用事先定义的 A、B 识别矩阵估计结构 VAR。"
        }
        if "`cmd'" == "vec" {
            local expr_label "系统变量 + rank() + lags() 等协整/VEC 设定"
            local example1 "vec y1 y2, rank(1) lags(2)"
            local explain1 "在协整秩为 1、VAR 阶数为 2 的设定下估计 VEC 模型。"
        }
        if "`cmd'" == "varsoc" {
            local expr_label "系统变量 + maxlag() 等阶数选择设定"
            local example1 "varsoc y1 y2, maxlag(4)"
            local explain1 "比较 y1、y2 的候选滞后阶数，最大检查 4 阶。"
        }
        if "`cmd'" == "vargranger" {
            local expr_label "VAR/VEC 估计后的 Granger 因果检验 options（通常可留空）"
            local example1 "vargranger"
            local explain1 "对上一项 VAR/VEC 结果执行 Granger 因果检验。"
            local example2 "help vargranger"
            local explain2 "需要更细的限制或显示设置时核对当前 Stata 版本的 options。"
        }
        if "`cmd'" == "varstable" {
            local expr_label "VAR/SVAR 估计后的稳定性检验 options（通常可留空）"
            local example1 "varstable"
            local explain1 "检查上一项 VAR/SVAR 的特征根稳定性条件。"
            local example2 "help varstable"
            local explain2 "图形或其他稳定性设置按当前 Stata 版本核对。"
        }
        if "`cmd'" == "spregress" {
            local expr_label "Y + X + 估计方法 + dvarlag()/ivarlag()/errorlag()"
            local example1 "spregress y x, gs2sls dvarlag(W)"
            local explain1 "使用预先创建的 W 对因变量加入空间滞后，并用 GS2SLS 估计。"
            local example2 "spregress y x, ml dvarlag(W)"
            local explain2 "使用 ML 估计因变量空间滞后模型。"
        }
        if "`cmd'" == "spivregress" {
            local expr_label "Y + 外生 X + (内生变量 = 工具变量) + 空间权重设定"
            local example1 "spivregress y x1 (x2 = z), dvarlag(W) errorlag(M)"
            local explain1 "同时保留 IV 方程、因变量空间滞后和空间误差；W/M 需事先创建。"
            local example2 "help spivregress"
            local explain2 "ivarlag() 等更复杂空间结构按研究设定继续补充。"
        }
        if "`cmd'" == "spxtregress" {
            local expr_label "Y + X + FE/RE + dvarlag()/ivarlag()/errorlag()"
            local example1 "spxtregress y x, fe dvarlag(W) errorlag(M)"
            local explain1 "在已声明的空间面板数据上估计固定效应空间自回归模型。"
            local example2 "spxtregress y x, re dvarlag(W) errorlag(M)"
            local explain2 "随机效应空间面板模型使用同样的空间权重结构。"
        }
        if "`cmd'" == "xteregress" {
            local expr_label "Y + X + endogenous()/select()/entreat() 扩展随机效应方程"
            local example1 "xteregress y x1, endogenous(x2 = x3 x4)"
            local explain1 "在线性随机效应面板结果方程中，把 x2 作为内生协变量并用 x3、x4 建模。"
            local example2 "help xteregress"
            local explain2 "还可联合 select() 与 entreat()；复杂多方程结构应直接保留 Stata ERM 原生语法。"
        }
        if "`cmd'" == "xteprobit" {
            local expr_label "二元 Y + X + endogenous()/select()/entreat() 扩展随机效应 Probit"
            local example1 "xteprobit y x1, endogenous(x2 = x3 x4)"
            local explain1 "在随机效应 Probit 面板模型中显式建立 x2 的内生协变量方程。"
            local example2 "help xteprobit"
            local explain2 "内生协变量、样本选择和处理分配可在同一 ERM 框架联合建模。"
        }
        if "`cmd'" == "xteoprobit" {
            local expr_label "有序 Y + X + endogenous()/select()/entreat() 扩展随机效应有序 Probit"
            local example1 "xteoprobit y x1, endogenous(x2 = x3 x4)"
            local explain1 "对面板有序结果建立随机效应 ordered-probit 主方程和内生协变量方程。"
            local example2 "help xteoprobit"
            local explain2 "结果类别必须有明确顺序；多方程结构继续使用 ERM 原生 options。"
        }
        if "`cmd'" == "xteintreg" {
            local expr_label "结果下界 + 上界 + X + endogenous()/select()/entreat()"
            local example1 "xteintreg ylower yupper x1, endogenous(x2 = x3 x4)"
            local explain1 "区间结果由 ylower/yupper 表达，并在随机效应面板框架中处理 x2 的内生性。"
            local example2 "help xteintreg"
            local explain2 "左删失、右删失、精确值与区间值的编码应先核对上下界变量。"
        }
        if "`cmd'" == "xtheckman" {
            local expr_label "结果方程 + select() 选择方程（随机效应面板 Heckman）"
            local example1 "xtheckman income c.age##c.age i.training#(c.exp##c.exp), select(working = age exp i.region i.training)"
            local explain1 "income 只在 working=1 时被观察；select() 显式建模进入结果样本的概率。"
            local example2 "help xtheckman"
            local explain2 "模型同时允许个体随机效应与结果/选择过程相关，选择方程属于核心识别结构。"
        }
        if "`cmd'" == "xthtaylor" {
            local expr_label "Y + X + endog()（与个体效应相关的解释变量）"
            local example1 "xthtaylor y x1 x2 z1, endog(x2)"
            local explain1 "Hausman–Taylor 通过模型内部工具变量处理与个体效应相关的 x2，同时保留时间不变变量 z1。"
            local example2 "help xthtaylor"
            local explain2 "endog() 指变量与个体效应相关，识别依赖时间变/不变且外生/内生变量的划分。"
        }
        if "`cmd'" == "xtdpd" {
            local expr_label "动态方程 + div()/dgmmiv()/lgmmiv() 等矩条件与工具变量集合"
            local example1 "xtdpd L(0/1).y x, div(x) dgmmiv(y)"
            local explain1 "直接声明动态回归项以及差分方程 GMM 工具变量；比 xtabond/xtdpdsys 提供更灵活的矩条件。"
            local example2 "help xtdpd"
            local explain2 "工具变量滞后区间和数量会直接影响识别与有限样本表现，运行前逐项核对。"
        }
        if "`cmd'" == "xtgls" {
            local expr_label "Y + X + panels() + corr() 等 FGLS 协方差结构"
            local example1 "xtgls y x1 x2, panels(heteroskedastic) corr(ar1)"
            local explain1 "允许 panel-level heteroskedasticity，并用共同 AR(1) 描述面板内序列相关。"
            local example2 "help xtgls"
            local explain2 "FGLS 对 N/T 与协方差结构假设较敏感，panels() 和 corr() 应由数据结构决定。"
        }
        if "`cmd'" == "xtunitroot" {
            local expr_label "检验方法 + 变量 + lags()/trend/demean 等单位根设定"
            local example1 "xtunitroot ips hprice"
            local explain1 "对 hprice 进行 Im–Pesaran–Shin 面板单位根检验；该命令需要已声明的 panel/time。"
            local example2 "help xtunitroot"
            local explain2 "LLC、HT、Breitung、IPS、Fisher、Hadri 等检验的 N/T 渐近条件并不相同。"
        }
        if "`cmd'" == "xtcointtest" {
            local expr_label "Kao/Pedroni/Westerlund + 协整变量列表"
            local example1 "xtcointtest kao hprice aprice nprice"
            local explain1 "在已确认变量存在单位根后，使用 Kao 检验考察 panel 长期协整关系。"
            local example2 "help xtcointtest"
            local explain2 "Kao、Pedroni、Westerlund 对协整向量与面板异质性的假设不同，应与研究设定对应。"
        }
        if "`cmd'" == "xtdescribe" {
            local expr_label "面板结构描述（通常直接运行；可补充 patterns 等 options）"
            local example1 "xtdescribe"
            local explain1 "查看 panel 数量、时间跨度、T_i 分布以及平衡/非平衡观测模式。"
            local example2 "help xtdescribe"
            local explain2 "适合在正式面板回归前检查面板覆盖、缺口与时间模式。"
        }
        if "`cmd'" == "xtsum" {
            local expr_label "要汇总的变量列表"
            local example1 "xtsum hours"
            local explain1 "同时报告 hours 的 overall、between 和 within 变异，直接对应面板数据的三个层次。"
            local example2 "help xtsum"
            local explain2 "within 与 between 的标准差含义不同，不能按普通 summarize 的单一方差解释。"
        }
        if "`cmd'" == "xttab" {
            local expr_label "一个分类变量"
            local example1 "xttab msp"
            local explain1 "把分类变量的总体频率、panel 间出现比例和 panel 内状态变化分开汇总。"
            local example2 "help xttab"
            local explain2 "适合检查二元/分类状态在面板内是否具有足够变化。"
        }
        if "`cmd'" == "xtdata" {
            local expr_label "要转换的变量 + fe/re/be 等变换设定"
            local example1 "xtdata y x1 x2, fe clear"
            local explain1 "把当前变量转换为 fixed-effects within 形式；clear 会替换内存数据，运行前必须确认已保存原数据。"
            local example2 "help xtdata"
            local explain2 "这是数据变换工具，会影响后续分析数据；用于手工估计前应保留可恢复的原始数据。"
        }
        if "`cmd'" == "xtivreg" {
            local expr_label "Y + 外生 X + (内生变量 = 工具变量) + fe/re 等面板 IV 设定"
            local example1 "xtivreg y x1 (x2 = z1 z2), fe"
            local explain1 "在面板固定效应模型中，把 x2 视为内生变量并使用 z1、z2 作为排除工具变量。"
            local example2 "help xtivreg"
            local explain2 "FE、RE、BE 与 G2SLS/EC2SLS 等可用设定应按识别策略和当前 Stata help 核对。"
        }
        if "`cmd'" == "xtpcse" {
            local expr_label "Y + X + correlation() + pairwise/hetonly 等 PCSE 设定"
            local example1 "xtpcse y x1 x2, correlation(ar1) pairwise"
            local explain1 "使用面板校正标准误，并允许面板内 AR(1) 相关；pairwise 控制协方差估计的样本使用。"
            local example2 "help xtpcse"
            local explain2 "PCSE 的适用性取决于 N、T、同期截面相关与序列相关结构，应按数据结构选择。"
        }
        if "`cmd'" == "xtregar" {
            local expr_label "Y + X + fe/re + AR(1) 面板误差设定"
            local example1 "xtregar y x1 x2, fe"
            local explain1 "估计带 AR(1) 扰动结构的固定效应面板线性模型。"
            local example2 "xtregar y x1 x2, re"
            local explain2 "随机效应版本同时建模个体效应与面板内一阶自相关。"
        }
        if "`cmd'" == "xtrc" {
            local expr_label "Y + X（随机系数面板回归）"
            local example1 "xtrc y x1 x2"
            local explain1 "允许回归系数在面板个体之间随机变化，适用于参数异质性本身属于研究对象的场景。"
            local example2 "help xtrc"
            local explain2 "运行前应确认每个 panel 内有足够时间维度用于识别个体层面的系数差异。"
        }
        if "`cmd'" == "xtstreg" {
            local expr_label "生存协变量 + distribution()；运行前还需 stset，并由页面执行 xtset"
            local example1 "xtstreg age female, distribution(weibull)"
            local explain1 "在已 stset 的面板生存数据上估计 Weibull 随机效应生存模型；页面会按所选 panel/time 先执行 xtset。"
            local example2 "help xtstreg"
            local explain2 "xtstreg 同时属于 st 与 xt 工作流；失败事件、分析时间和 censoring 定义必须先由 stset 正确声明。"
        }
        if "`cmd'" == "xtgee" {
            local expr_label "Y + X + family() + link() + corr()（GEE 核心设定）"
            local example1 "xtgee union age not_smsa, family(binomial) link(probit) corr(exchangeable)"
            local explain1 "二元结果采用 Probit 链接，并用 exchangeable 工作相关结构处理面板内相关。"
            local example2 "xtgee y x1 x2, family(gaussian) link(identity) corr(independent)"
            local explain2 "连续结果可使用 Gaussian + identity；相关结构应由数据与研究设计决定。"
        }
        if "`cmd'" == "xttobit" {
            local expr_label "Y + X + ll()/ul() 截尾界限"
            local example1 "xttobit y x1 x2, ll(0)"
            local explain1 "随机效应面板 Tobit，结果在 0 处左删失。"
            local example2 "help xttobit"
            local explain2 "右删失或双侧删失时继续设置 ul() / ll()。"
        }
        if "`cmd'" == "xtintreg" {
            local expr_label "结果下界 + 结果上界 + X（例如 ylower yupper x1 x2）"
            local example1 "xtintreg ylower yupper x1 x2 x3"
            local explain1 "ylower、yupper 分别记录区间结果的下界和上界；这两个结果变量都属于核心语法。"
            local example2 "help xtintreg"
            local explain2 "左删失、右删失和精确观测通过上下界变量中的缺失/相等关系表达。"
        }
        if "`cmd'" == "xtfrontier" {
            local expr_label "Y + X + ti/tvd + production/cost 等前沿设定"
            local example1 "xtfrontier y x1 x2, ti"
            local explain1 "估计时间不变 inefficiency 的面板随机前沿模型。"
            local example2 "xtfrontier y x1 x2, tvd"
            local explain2 "tvd 允许 inefficiency 随时间按共同衰减结构变化。"
        }
        if "`cmd'" == "xtabond" {
            local expr_label "Y + X + lags()/maxldep()/pre()/endogenous()/twostep 等动态面板设定"
            local example1 "xtabond y x1 x2, lags(1)"
            local explain1 "Arellano–Bond 差分 GMM；lags(1) 指定因变量动态滞后阶数。"
            local example2 "help xtabond"
            local explain2 "工具变量集合、预定变量、两步估计和 AR 检验会显著影响结果，运行前逐项核对。"
        }
        if "`cmd'" == "xtdpdsys" {
            local expr_label "Y + X + lags()/maxldep()/pre()/endogenous()/twostep 等系统 GMM 设定"
            local example1 "xtdpdsys y x1 x2, lags(1)"
            local explain1 "Arellano–Bover/Blundell–Bond 系统估计同时利用差分方程和水平方程矩条件。"
            local example2 "help xtdpdsys"
            local explain2 "系统 GMM 的工具变量数量与有效性需要在研究中单独诊断。"
        }
        if "`cmd'" == "ivprobit" {
            local expr_label "二元 Y + 外生 X + (内生连续变量 = 工具变量)"
            local example1 "ivprobit y x1 (x2 = z1 z2)"
            local explain1 "在 Probit 结果方程中把 x2 视为连续内生协变量，并用 z1、z2 作为排除工具变量。"
            local example2 "help ivprobit"
            local explain2 "ML 与 two-step 的后估计能力不同；工具变量相关性和外生性仍需单独诊断。"
        }
        if "`cmd'" == "ivtobit" {
            local expr_label "删失 Y + 外生 X + (内生连续变量 = 工具变量) + ll()/ul()"
            local example1 "ivtobit y x1 (x2 = z1 z2), ll(0)"
            local explain1 "对在 0 处左删失的结果建模，同时用 z1、z2 处理 x2 的内生性。"
            local example2 "help ivtobit"
            local explain2 "删失界限必须对应真实观测机制；ML/two-step 与 VCE 选项运行前核对。"
        }
        if "`cmd'" == "ivpoisson" {
            local expr_label "估计器 + 计数 Y + 外生 X + (内生变量 = 工具变量)"
            local example1 "ivpoisson gmm accidents x1 x2 (horsepower = x3 x4)"
            local explain1 "使用 GMM Poisson，以 x3、x4 作为 horsepower 的工具变量。"
            local example2 "help ivpoisson"
            local explain2 "gmm 与 cfunction 的识别假设和可用后估计不同，先明确估计器再填方程。"
        }
        if "`cmd'" == "ivfprobit" {
            local expr_label "分数 Y + 外生 X + (内生连续变量 = 工具变量)"
            local example1 "ivfprobit prate c.ltotemp##c.ltotemp i.sole (mrate = c.age##c.age)"
            local explain1 "Stata 18 fractional probit IV：mrate 是内生协变量，plan age 及其平方作为工具变量。"
            local example2 "help ivfprobit"
            local explain2 "fracreg/ivfprobit 允许分数结果包含 0 和 1；该入口仅在 Stata 18+ 展示。"
        }
        if "`cmd'" == "ivqregress" {
            local expr_label "IQR/smooth + Y + (内生变量 = 工具变量) + 外生 X + quantile()"
            local example1 "ivqregress iqr assets (i.p401k = i.e401k) income age familysize i.married i.ira i.pension i.ownhome educ"
            local explain1 "使用 inverse quantile regression 估计内生 401(k) 参与对条件中位数的影响。"
            local example2 "ivqregress smooth assets (i.p401k = i.e401k) income age familysize, quantile(10(10)90)"
            local explain2 "smooth estimator 可同时研究多个条件分位数；该入口仅在 Stata 18+ 展示。"
        }
        if strpos(" mixed mecloglog melogit meprobit mepoisson menbreg meologit meoprobit meintreg menl mestreg metobit meglm ", " `cmd' ") {
            local expr_label "固定部分 + || 随机效应层级（如 y x1 x2 || school: x2 || class:）"
            if "`cmd'" == "mixed" {
                local example1 "mixed y x1 x2 || school: x2 || class:"
                local explain1 "固定效应写在前面，|| 后按层级写随机截距 / 随机斜率。"
            }
            else if "`cmd'" == "mecloglog" {
                local example1 "mecloglog y x1 x2 || school:"
                local explain1 "对二元结果使用 complementary log-log 链接，并在 school 层加入随机截距。"
            }
            else if "`cmd'" == "meintreg" {
                local example1 "meintreg ylower yupper x1 x2 x3 || id:"
                local explain1 "ylower/yupper 给出区间结果边界，并在 id 层加入随机截距；还可扩展随机系数。"
            }
            else if "`cmd'" == "menl" {
                local example1 "menl weight = ({b1}+{U[id]})/(1+exp(-(time-{b2})/{b3}))"
                local explain1 "直接写非线性均值函数，并把 U[id] 作为 id 层随机效应嵌入参数表达式。"
            }
            else {
                local example1 "help `cmd'"
                local explain1 "多层模型的 || 随机效应结构属于核心模型主体，不能只用普通 Y/X 框代替。"
            }
        }
        if inlist("`cmd'", "lasso", "elasticnet") {
            local expr_label "模型类型 + 因变量 + 候选变量（如 linear y x1-x100）"
            local example1 "`cmd' linear y x1-x100"
            local explain1 "lasso / elasticnet 在因变量前需要明确 linear、logit、probit、poisson 或 cox 等模型类型。"
        }
        if strpos(" poregress pologit popoisson dslogit dspoisson xpologit xpopoisson ", " `cmd' ") {
            local expr_label "Y + 关注变量 + controls() 高维候选控制"
            local example1 "`cmd' y d1, controls(x1-x100)"
            if strpos(" poregress pologit popoisson ", " `cmd' ") {
                local explain1 "Partialing-out Lasso：d1 是关注变量，controls() 中的高维候选控制由 lasso 选择并部分化。"
            }
            else if strpos(" dslogit dspoisson ", " `cmd' ") {
                local explain1 "Double-selection Lasso：分别围绕结果与关注变量选择 controls()，再对 d1 做有效推断。"
            }
            else {
                local explain1 "Cross-fit partialing-out Lasso：用交叉拟合降低高维 nuisance 模型过拟合对 d1 推断的影响。"
            }
            local example2 "help `cmd'"
            local explain2 "模型分布、选择方法、聚类和交叉拟合设置按当前 Stata 版本继续核对。"
        }
        if "`cmd'" == "telasso" {
            local expr_label "(结果变量 + 高维结果模型控制) + (处理变量 + 高维处理模型控制)"
            local example1 "telasso (y x1-x100) (treat w1-w100)"
            local explain1 "第一组括号是结果模型，第二组是处理分配模型；lasso 在两组高维候选控制中选择变量。"
            local example2 "telasso (y x1-x100) (treat w1-w100), atet"
            local explain2 "加 atet 后估计已接受处理者的平均处理效应。"
        }
        if "`cmd'" == "npregress" {
            local expr_label "非参数方法 + Y + X：kernel 或 series；series 还可用 asis()/nointeract() 施加半参数结构"
            local example1 "npregress kernel y x1 x2"
            local explain1 "kernel regression 通过核与带宽平滑估计 E(y|x1,x2)，适合低维连续/离散协变量。"
            local example2 "npregress series output taxlevel rainfall i.irrigate"
            local explain2 "series regression 用 spline/polynomial series 逼近未知响应面；asis() 可保留线性项，nointeract() 可限制可加结构。"
        }
        if "`cmd'" == "nptrend" {
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
        if "`cmd'" == "stset" {
            local expr_label "生存数据声明主体（分析时间、failure()、id()、enter()/exit() 等）"
            local example1 "help stset"
            local explain1 "stset 同时定义分析时间、失败事件和风险区间，完整主体比单一变量框更清楚。"
        }
        if "`cmd'" == "streg" {
            local expr_label "协变量 + 参数分布等核心 options（如 age protect, distribution(weibull)）"
            local example1 "streg protect age, distribution(weibull)"
            local explain1 "失败事件与分析时间来自 stset；这里填写协变量和参数生存分布。"
            local example2 "streg age, distribution(exponential)"
            local explain2 "以指数分布拟合参数生存模型。"
        }
        if "`cmd'" == "stcrreg" {
            local expr_label "协变量 + compete()（如 ifp tumsize, compete(failtype==2)）"
            local example1 "stcrreg ifp tumsize pelnode, compete(failtype==2)"
            local explain1 "失败事件来自 stset，compete() 指定竞争事件。"
        }
        if "`cmd'" == "dsregress" {
            local expr_label "Y + 关注变量 + controls()（如 y d1, controls(x1-x100)）"
            local example1 "dsregress y d1, controls(x1-x100)"
            local explain1 "d1 是关注变量，controls() 中的高维候选控制由 lasso 选择。"
        }
        if inlist("`cmd'", "poivregress", "xpoivregress") {
            local expr_label "Y + 关注变量 + (内生变量 = 工具变量) + controls()"
            local example1 "`cmd' y d1 (x = z1-z20), controls(c1-c100)"
            local explain1 "把关注变量、IV 方程和高维候选控制完整保留在一个主体中。"
        }
        if "`cmd'" == "xporegress" {
            local expr_label "Y + 关注变量 + controls()（交叉拟合 partialing-out）"
            local example1 "xporegress y d1, controls(x1-x100)"
            local explain1 "d1 是需要推断的变量，controls() 交给 lasso 选择并交叉拟合。"
        }
        if inlist("`cmd'", "etregress", "etpoisson") {
            local expr_label "结果方程 + treat() 处理方程"
            local example1 "etregress wage age grade, treat(union = south black tenure)"
            local explain1 "主结果方程写在前面，内生处理变量及其协变量写进 treat()。"
            local example2 "help `cmd'"
            local explain2 "etpoisson 与 etregress 的结果分布不同，处理方程结构仍需显式保留。"
        }
        if "`cmd'" == "fracreg" {
            local expr_label "链接模型 + Y + X（如 probit prate mrate sole）"
            local example1 "fracreg probit prate mrate sole"
            local explain1 "fracreg 的 probit/logit 等模型词位于结果变量之前。"
            local example2 "fracreg logit prate mrate sole"
            local explain2 "使用 fractional logit 拟合比例结果。"
        }
        if inlist("`cmd'", "zip", "zinb") {
            local expr_label "计数方程 + inflate() 零膨胀方程"
            local example1 "`cmd' y x1 x2, inflate(z1 z2)"
            local explain1 "主计数方程与产生额外零值的 inflate() 方程需要同时明确。"
        }
        if inlist("`cmd'", "tpoisson", "tnbreg") {
            local expr_label "Y + X + 截断点 options（ll()/ul()）"
            local example1 "`cmd' y x1 x2, ll(0)"
            local explain1 "截断模型必须把样本截断边界作为模型核心设定核对。"
        }
        if "`cmd'" == "glm" {
            local expr_label "Y + X + family()/link()（如 y x, family(poisson) link(log)）"
            local example1 "glm y x, family(poisson) link(log)"
            local explain1 "GLM 的分布族和链接函数决定模型形式，因此和变量一起放在核心主体。"
        }
        if "`cmd'" == "hetprobit" {
            local expr_label "主 Probit 方程 + het() 异方差方程"
            local example1 "hetprobit y x1 x2, het(z1 z2)"
            local explain1 "het() 中的变量决定潜在误差方差，需要与主方程一起确认。"
        }
        if inlist("`cmd'", "asclogit", "asmprobit") {
            local expr_label "选择指示 + 备选项变量 + case()/alternatives()/casevars()"
            local example1 "`cmd' choice price, case(id) alternatives(alt) casevars(income age)"
            local explain1 "备选项特征、选择场景 ID、备选项 ID 与个体特征都属于离散选择模型的核心结构。"
        }
        if "`cmd'" == "sts" {
            local expr_label "sts 子命令与参数（如 graph / list / test group）"
        }
        if "`cmd'" == "irf" {
            local expr_label "irf 子命令与参数（如 create / graph / table）"
        }
        if "`cmd'" == "sts_graph" {
            local title "sts graph — 生存函数图"
            local purpose1 "在已经 stset 的生存数据上绘制 Kaplan–Meier 生存曲线、失败函数等非参数生存图。"
            local purpose2 "失败事件和分析时间沿用当前 stset；分组、failure、risktable 等设置写在 sts graph 的原生 options 中。"
            local expr_label "sts graph 后面的 options（可留空；例如 , by(treat)）"
            local example1 "sts graph"
            local explain1 "绘制当前 stset 数据的默认 Kaplan–Meier 生存曲线。"
            local example2 "sts graph, by(treat)"
            local explain2 "按 treat 分组绘制生存曲线。"
        }
        if "`cmd'" == "screeplot" {
            local title "screeplot — 碎石图"
            local purpose1 "在 factor、pca 或兼容多元分析后绘制特征值/惯量随维度变化的 scree plot。"
            local purpose2 "先完成相应多元模型；本页只设置要展示的维度、置信区间和图形 options。"
            local expr_label "screeplot 选项（通常可留空直接绘图）"
            local example1 "screeplot"
            local explain1 "绘制最近一次 factor/PCA 等结果的碎石图。"
            local example2 "screeplot, yline(1)"
            local explain2 "增加 eigenvalue=1 的参考线。"
        }
        if "`cmd'" == "scoreplot" {
            local title "scoreplot — 因子/主成分得分图"
            local purpose1 "在 factor 或 pca 后绘制因子/主成分 scores 的二维关系。"
            local purpose2 "需要先成功估计 factor/factormat 或 pca/pcamat。"
            local expr_label "维度与图形 options（如 factors(1 2)）"
            local example1 "scoreplot"
            local explain1 "绘制默认前两个因子或主成分的 score plot。"
            local example2 "help scoreplot"
            local explain2 "维度选择、标签和 marker 选项按当前 Stata Help 设置。"
        }
        if "`cmd'" == "loadingplot" {
            local title "loadingplot — 因子/主成分载荷图"
            local purpose1 "在 factor 或 pca 后比较变量在两个因子/主成分上的 loadings。"
            local purpose2 "变量箭头/点的位置反映载荷结构，解释时结合旋转方式和保留维度。"
            local expr_label "维度与图形 options（通常可直接运行）"
            local example1 "loadingplot"
            local explain1 "绘制最近一次 factor/PCA 的默认 loading plot。"
            local example2 "help loadingplot"
            local explain2 "旋转结果、标签和坐标轴选项按当前 Stata Help 设置。"
        }
        if "`cmd'" == "biplot" {
            local title "biplot — 多元双标图"
            local purpose1 "同时显示观测在低维空间中的位置与变量方向，用二维图概括多变量结构。"
            local purpose2 "biplot 可以直接对数据执行双标图分析；dim() 等选项决定显示维度。"
            local expr_label "变量列表 + dim()/rowlabel()/rowover() 等"
            local example1 "biplot x1 x2 x3 x4"
            local explain1 "对四个变量执行 biplot analysis 并绘制二维双标图。"
            local example2 "help biplot"
            local explain2 "分组、高亮、维度和坐标生成选项按当前 Stata Help 设置。"
        }
        if "`cmd'" == "cluster_dendrogram" {
            local title "cluster dendrogram — 层次聚类树状图"
            local purpose1 "在层次聚类结果后绘制 dendrogram，查看对象如何逐步合并成簇。"
            local purpose2 "实时命令生成原生 cluster dendrogram；需要先存在兼容的 hierarchical cluster result。"
            local expr_label "cluster dendrogram 后面的分析名与 options（可留空使用当前聚类结果）"
            local example1 "cluster dendrogram"
            local explain1 "为当前层次聚类结果绘制完整树状图。"
            local example2 "cluster dendrogram, horizontal"
            local explain2 "改为水平树状图。"
        }
        if "`cmd'" == "cabiplot" {
            local title "cabiplot — 对应分析双标图"
            local purpose1 "在 ca/camat 后同时显示行类别和列类别在主维度空间中的位置。"
            local purpose2 "先完成 correspondence analysis；本页只负责图形维度、标签和 marker options。"
            local expr_label "cabiplot 选项（如 dimensions()/origin/rowopts()/colopts()）"
            local example1 "cabiplot"
            local explain1 "绘制最近一次 correspondence analysis 的默认 biplot。"
            local example2 "cabiplot, origin"
            local explain2 "在图中显示原点。"
        }
        if "`cmd'" == "caprojection" {
            local title "caprojection — 对应分析维度投影图"
            local purpose1 "在 ca/camat 后显示行、列类别在各 principal dimensions 上的投影顺序。"
            local purpose2 "适合直接比较类别沿主要对应分析维度的位置。"
            local expr_label "caprojection 图形 options"
            local example1 "caprojection"
            local explain1 "绘制最近一次 correspondence analysis 的维度投影图。"
            local example2 "help caprojection"
            local explain2 "维度、行列 marker labels 等设置按当前 Help 调整。"
        }
        if "`cmd'" == "mdsconfig" {
            local title "mdsconfig — MDS 配置图"
            local purpose1 "在 mds/mdslong/mdsmat 后绘制低维 Euclidean configuration。"
            local purpose2 "点之间的图上距离用于近似原始 dissimilarities；应结合 stress 等拟合指标判断。"
            local expr_label "mdsconfig 维度、标签和 marker options"
            local example1 "mdsconfig"
            local explain1 "绘制最近一次 MDS 的前两个维度配置图。"
            local example2 "help mdsconfig"
            local explain2 "对象标签和维度选择按当前 Stata Help 设置。"
        }
        if "`cmd'" == "mdsshepard" {
            local title "mdsshepard — MDS Shepard 图"
            local purpose1 "在 MDS 后比较原始 dissimilarities 与低维配置中的 fitted distances。"
            local purpose2 "点越接近拟合关系，低维表示越能保持原始距离结构；同时结合 stress 评价。"
            local expr_label "mdsshepard 图形 options"
            local example1 "mdsshepard"
            local explain1 "绘制最近一次 MDS 的 Shepard diagram。"
            local example2 "help mdsshepard"
            local explain2 "标记、拟合线和图形选项按当前 Help 设置。"
        }
        if "`cmd'" == "procoverlay" {
            local title "procoverlay — Procrustes 叠加图"
            local purpose1 "在 procrustes 后把 target configuration 与由 source 拟合得到的位置叠加比较。"
            local purpose2 "用于直观看两个配置经过 Procrustean transformation 后的贴合程度。"
            local expr_label "procoverlay 图形 options"
            local example1 "procoverlay"
            local explain1 "绘制最近一次 Procrustes analysis 的 overlay plot。"
            local example2 "help procoverlay"
            local explain2 "标签、连接线和图形样式按当前 Help 调整。"
        }
        if "`cmd'" == "graph" {
            local title "graph — 管理、保存与输出图形"
            local purpose1 "管理已经生成的 Stata 图形，包括显示、保存、导出、重命名、关闭和查询图形对象。"
            local purpose2 "这里填写 graph 后面的原生子命令；绘图本身请从对应图形类型入口进入。"
            local expr_label "graph 子命令与参数（如 display / save / export / dir / close）"
            local example1 "graph dir"
            local explain1 "列出当前内存中的已命名图形。"
            local example2 "graph export result.png, replace"
            local explain2 "把当前图形导出为 PNG 文件。"
        }
        if "`cmd'" == "set" {
            local title "set — 设置默认图形方案"
            local purpose1 "用 Stata 官方 set scheme 命令修改后续新图形默认使用的 scheme。"
            local purpose2 "单张图的宽高和整体缩放属于绘图命令 options：在具体图形页使用 xsize()/ysize()/scale()；本页只负责默认 scheme。"
            local expr_label "set 后面的图形设置（通常填写 scheme 方案名 [, permanently]）"
            local example1 "set scheme stcolor"
            local explain1 "把当前会话后续新图形的默认 scheme 设为 Stata 18 默认的 stcolor。"
            local example2 "set scheme s2color, permanently"
            local explain2 "把 s2color 保存为以后启动 Stata 时继续使用的默认 scheme。"
        }
        if inlist("`cmd'", "discrim", "cluster") {
            local expr_label "子命令 + 变量与参数（按当前 Stata help 填写）"
        }
    }

    /* Panel estimators whose Y/X grammar remains safe still get command-specific examples. */
    if "`cmd'" == "xtpoisson" {
        local example1 "xtpoisson y x1 x2, fe"
        local explain1 "固定效应面板 Poisson；运行前页面会先按所选数据结构执行 xtset。"
        local example2 "xtpoisson y x1 x2, re"
        local explain2 "随机效应面板 Poisson。"
    }
    else if "`cmd'" == "xtnbreg" {
        local example1 "xtnbreg y x1 x2, re"
        local explain1 "随机效应面板负二项模型。"
        local example2 "xtnbreg y x1 x2, fe"
        local explain2 "固定效应参数化应结合研究目标和 Stata 定义解释。"
    }
    else if "`cmd'" == "xtcloglog" {
        local example1 "xtcloglog y x1 x2, re"
        local explain1 "随机效应面板 complementary log-log 模型。"
        local example2 "help xtcloglog"
        local explain2 "总体平均等模型选项按当前 Stata 版本核对。"
    }
    else if "`cmd'" == "xtoprobit" {
        local example1 "xtoprobit y x1 x2"
        local explain1 "有序结果的随机效应面板 Probit。"
        local example2 "help xtoprobit"
        local explain2 "先确认结果类别具有明确顺序。"
    }
    else if "`cmd'" == "xtmlogit" {
        local example1 "xtmlogit y x1 x2, re"
        local explain1 "无序多类别结果的随机效应面板 multinomial logit。"
        local example2 "help xtmlogit"
        local explain2 "基准类别、固定/随机效应可用性和面板内变异要求运行前核对。"
    }

    /* Graphics aliases preserve native multiword Stata syntax while offering one navigable UI token. */
    if strpos(" graph_bar graph_dot graph_pie graph_box graph_matrix twoway_contour graph_combine ", " `cmd' ") {
        local template "command_body"
        local has_depvar 0
        local has_varlist 0
        local has_if 0
        local has_in 0
        local has_weight 0
        local has_using 0
        local has_newvar 0
        local has_expression 1
        local has_absorb 0
        local has_vce 0
        local has_cluster 0
        local has_iv 0
        local needs_panel 0
        local model_before 0
        local show_advanced 1
        if "`cmd'" == "graph_bar" {
            local title "graph bar — 条形图"
            local purpose1 "对一个或多个数值变量绘制统计量条形图，并可用 over() 按类别分组。"
            local purpose2 "页面主体只填写 graph bar 后面的原生内容；实时命令始终生成真正的 graph bar。"
            local expr_label "统计量 + 数值变量 + over()/asyvars 等（graph bar 后面的内容）"
            local example1 "graph bar le le_w le_b"
            local explain1 "绘制三个变量的默认均值条形图。"
            local example2 "graph bar heatdd cooldd, over(region) blabel(total)"
            local explain2 "按 region 分组并显示 bar labels。"
        }
        else if "`cmd'" == "graph_dot" {
            local title "graph dot — 汇总点图"
            local purpose1 "绘制均值、百分位等 summary statistics 的 dot chart；这与分布型 dotplot 是两类图。"
            local purpose2 "需要按类别比较时直接写 over()；实时命令生成 graph dot。"
            local expr_label "统计量 + 数值变量 + over() 等（graph dot 后面的内容）"
            local example1 "graph dot wage, over(occ)"
            local explain1 "按 occupation 显示 wage 的汇总点图。"
            local example2 "graph dot wage hours, over(occ) vertical"
            local explain2 "同时画 wage、hours，并改为 vertical dot chart。"
        }
        else if "`cmd'" == "graph_pie" {
            local title "graph pie — 饼图"
            local purpose1 "用数值变量的总量或 over() 分组构造 pie slices。"
            local purpose2 "类别频数型饼图通常直接使用 over(category)。"
            local expr_label "数值变量 + over()/plabel()/pie() 等（graph pie 后面的内容）"
            local example1 "graph pie pop, over(region)"
            local explain1 "按 region 划分 pop 的饼图。"
            local example2 "graph pie pop, over(region) plabel(_all name)"
            local explain2 "在每个 slice 上显示类别名称。"
        }
        else if "`cmd'" == "graph_box" {
            local title "graph box — 箱线图"
            local purpose1 "展示连续变量的中位数、四分位距、须线和潜在异常值，并可用 over() 比较组间分布。"
            local purpose2 "Java 专页会直接提供结果变量和可选分组变量；这里保留同一真实 Stata 语义，确保搜索/解析链一致。"
            local expr_label "数值变量 + over() 等（graph box 后面的内容）"
            local example1 "graph box y"
            local explain1 "查看 y 的整体箱线分布。"
            local example2 "graph box y, over(group)"
            local explain2 "按 group 比较 y 的中位数、四分位距和潜在异常值。"
        }
        else if "`cmd'" == "graph_matrix" {
            local title "graph matrix — 散点图矩阵"
            local purpose1 "一次查看多个变量两两关系，并在对角线显示变量标签。"
            local purpose2 "变量较多时矩阵会迅速变密；先放核心连续变量。"
            local expr_label "变量列表 + half/diagonal()/marker options（graph matrix 后面的内容）"
            local example1 "graph matrix mpg weight length"
            local explain1 "绘制 mpg、weight、length 的 scatterplot matrix。"
            local example2 "help graph matrix"
            local explain2 "需要半矩阵、标签或 marker 调整时按原生 graph matrix options 补充。"
        }
        else if "`cmd'" == "twoway_contour" {
            local title "twoway contour — 等高线图"
            local purpose1 "把 z 在 y–x 平面上的数值变化显示为填充等高区域。"
            local purpose2 "前三个变量顺序固定为 z y x；当前 Stata 16–18 兼容层不展示 Stata 19 heatmap。"
            local expr_label "z y x + levels()/ccuts()/color options（twoway contour 后面的内容）"
            local example1 "twoway contour z y x"
            local explain1 "以 x、y 为坐标，用 z 的大小形成填充等高线。"
            local example2 "help twoway contour"
            local explain2 "等高层数、cutpoints 和颜色等继续使用原生 contour options。"
        }
        else if "`cmd'" == "graph_combine" {
            local title "graph combine — 组合已有图形"
            local purpose1 "把多个已命名或已保存的 Stata graphs 排成一张组合图。"
            local purpose2 "先确保子图已经存在；cols()/rows()/xcommon/ycommon 控制布局与公共坐标。"
            local expr_label "图形名/文件 + cols()/rows()/xcommon/ycommon 等（graph combine 后面的内容）"
            local example1 "graph combine gr1 gr2, cols(2)"
            local explain1 "把 gr1、gr2 横向排成两列。"
            local example2 "graph combine gr1 gr2, ycommon"
            local explain2 "组合两图并强制使用共同 y-axis scale。"
        }
    }

    if strpos(" symplot quantile qnorm pnorm qchi pchi qqplot gladder qladder dotplot spikeplot sunflower ", " `cmd' ") {
        local title "`cmd' — 分布诊断图"
        local purpose1 "用于检查对称性、分位数/概率分布、变量变换或密集散点的分布结构。"
        local purpose2 "这组是 Stata 官方 distributional diagnostic graphics；graph dot 另用于 summary dot charts。"
        if "`cmd'" == "symplot" {
            local example1 "symplot price"
            local explain1 "检查 price 分布关于中位数的对称程度。"
        }
        else if "`cmd'" == "quantile" {
            local example1 "quantile price"
            local explain1 "绘制 price 的 quantile plot。"
        }
        else if "`cmd'" == "qnorm" {
            local example1 "qnorm price"
            local explain1 "用 quantile–normal plot 检查 price 与正态分布的偏离。"
        }
        else if "`cmd'" == "pnorm" {
            local example1 "pnorm price"
            local explain1 "绘制 normal probability plot。"
        }
        else if "`cmd'" == "qchi" {
            local example1 "qchi ch, df(2)"
            local explain1 "将 ch 的分位数与 2 自由度 chi-squared 分布比较。"
        }
        else if "`cmd'" == "pchi" {
            local example1 "pchi ch, df(2)"
            local explain1 "绘制相对于 chi-squared 分布的 probability plot。"
        }
        else if "`cmd'" == "qqplot" {
            local example1 "qqplot weightd weightf"
            local explain1 "直接比较两个变量的 empirical quantiles。"
        }
        else if "`cmd'" == "gladder" {
            local example1 "gladder mpg, fraction"
            local explain1 "用 ladder-of-powers 图探索使 mpg 更接近正态/对称的变换。"
        }
        else if "`cmd'" == "qladder" {
            local example1 "qladder heatdd"
            local explain1 "比较多种 power transformations 的 quantile-normal 表现。"
        }
        else if "`cmd'" == "dotplot" {
            local example1 "dotplot age"
            local explain1 "把原始 age 分布显示为堆叠 dots；用途不同于 graph dot 的 summary chart。"
        }
        else if "`cmd'" == "spikeplot" {
            local example1 "spikeplot age"
            local explain1 "用 spikes 显示一维分布。"
        }
        else if "`cmd'" == "sunflower" {
            local example1 "sunflower mpg displ"
            local explain1 "用 sunflower rays 表示重叠观测密度，适合密集 bivariate scatter。"
        }
        local example2 "help `cmd'"
        local explain2 "查看当前 Stata 版本的完整绘图 options。"
    }

    if strpos(" cchart pchart rchart xchart shewhart serrbar ", " `cmd' ") {
        local title "`cmd' — 质量控制图"
        local purpose1 "用于 statistical process control：count/proportion/range/mean/Shewhart control charts 或 standard-error bars。"
        local purpose2 "控制图的样本单位、控制限和 subgroup 结构必须与实际过程采样设计一致。"
        if "`cmd'" == "shewhart" {
            local example1 "shewhart m1-m5, connect(l)"
            local explain1 "对 m1–m5 的 subgroup measurements 绘制 Shewhart control chart。"
        }
        else if "`cmd'" == "serrbar" {
            local example1 "serrbar mean se x"
            local explain1 "在 x 轴上绘制 mean ± se 的 standard-error bars。"
        }
        else {
            local example1 "help `cmd'"
            local explain1 "先按当前命令 Help 确认 count/proportion/range/mean control-chart 的样本结构字段。"
        }
        local example2 "help `cmd'"
        local explain2 "查看控制限、nograph、generate() 和图形定制等命令特有选项。"
    }

    if "`cmd'" == "rocregplot" {
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
        local title "rocregplot — 绘制 ROC regression 结果"
        local expr_label "rocregplot 后面的完整主体（可留空，或填写 at1()/at2()/legend() 等）"
        local example1 "rocregplot"
        local explain1 "绘制最近一次 rocreg 模型对应的 ROC 曲线。"
        local example2 "rocregplot, at1(currage=40) at2(currage=50)"
        local explain2 "在两个协变量取值下比较模型隐含的 ROC 曲线。"
    }

    /* Family-level copy for catalog commands that rely on the generic syntax parser.
       Keep the parsed Stata syntax/flags unchanged; only improve beginner-facing semantics. */
    if strpos(" ivprobit ivtobit ivpoisson ivfprobit ivqregress ", " `cmd' ") {
        local title "`cmd' — 工具变量与内生性"
        local purpose1 "用于二元、删失、计数、分数或分位数结果中存在内生解释变量的 IV 模型。"
        local purpose2 "页面保留估计器、结果分布、删失界限和 (内生变量 = 工具变量) 的原生位置，避免普通 IV Y/X 模板拆错语法。"
    }
    else if strpos(" gnbreg cpoisson ", " `cmd' ") {
        local title "`cmd' — 计数结果扩展模型"
        local purpose1 "用于离散程度本身存在协变量异质性，或计数结果发生左/右/区间删失的场景。"
        local purpose2 "lnalpha() 与 ll()/ul() 都属于数据生成过程的核心设定，页面直接保留原生语法。"
    }
    else if strpos(" binreg biprobit ", " `cmd' ") {
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
    else if strpos(" hetregress sqreg intreg tobit truncreg churdle boxcox fp nl nlsur gmm reg3 frontier ", " `cmd' ") {
        local title "`cmd' — 线性模型及相关"
        local purpose1 "用于异方差、删失/截断、非线性、方程系统、GMM、函数形式或随机前沿等线性模型扩展。"
        local purpose2 "这些命令的核心语法差异较大；页面直接保留真正的方程、边界、矩条件或前缀结构。"
    }
    else if strpos(" ameans centile ci mean proportion ratio total dtable ", " `cmd' ") {
        local title "`cmd' — 汇总统计与参数估计"
        local purpose1 "用于均值、百分位、置信区间、比例、比率、总量或 Table 1 等基础描述与推断任务。"
        local purpose2 "第一步只保留该命令真正需要的变量/表达式；分组、权重、VCE 和表格选项在运行前核对。"
    }
    else if strpos(" power ciwidth gsbounds gsdesign ", " `cmd' ") {
        local title "`cmd' — 效能、精度与样本量设计"
        local purpose1 "用于研究设计阶段计算 power、CI precision、停止界值或 group-sequential sample size。"
        local purpose2 "效应大小、alpha、power、CI width、looks 和边界方法都应来自预先设定的研究设计。"
    }

    if strpos(" table prtest sdtest oneway anova ranksum median signrank signtest ", " `cmd' ") {
        local title "`cmd' — 表格与假设检验"
        local purpose1 "用于描述分组结果或执行常见参数/非参数假设检验。"
        local purpose2 "先按页面填写检验对象和分组信息；方向、显著性和其他 Stata 选项放在最后检查。"
    }
    else if strpos(" iqreg bsqreg sureg mvreg ", " `cmd' ") {
        local title "`cmd' — 线性与多方程模型"
        local purpose1 "用于分位数估计、稳健分位数推断或多个线性方程的联合估计。"
        local purpose2 "先区分结果变量与解释变量；命令特有设定继续以 Stata 当前语法和 options 为准。"
    }
    else if strpos(" logistic hetprobit scobit cloglog ", " `cmd' ") {
        local title "`cmd' — 二元结果模型"
        local purpose1 "用于因变量只有两类结果时的概率模型估计。"
        local purpose2 "先选择二元因变量和解释变量；链接函数、异方差或显示方式等命令特有设置放在最后。"
    }
    else if strpos(" ologit oprobit ", " `cmd' ") {
        local title "`cmd' — 序数结果模型"
        local purpose1 "用于因变量具有明确等级顺序的离散选择模型。"
        local purpose2 "先选择序数因变量和解释变量；阈值与其他模型选项由 Stata 按当前命令处理。"
    }
    else if strpos(" mlogit mprobit asclogit asmprobit ", " `cmd' ") {
        local title "`cmd' — 多类别选择模型"
        local purpose1 "用于无序多类别结果或备选项层面的离散选择问题。"
        local purpose2 "先明确结果/选择变量和解释变量；基准类别、备选项结构等设置在运行前按 Stata 语法核对。"
    }
    else if strpos(" zip zinb tpoisson tnbreg ", " `cmd' ") {
        local title "`cmd' — 扩展计数结果模型"
        local purpose1 "用于零膨胀、截断或过度离散等特殊计数数据。"
        local purpose2 "先选择计数因变量和解释变量；inflate()、截断点等命令特有参数放在最后设置。"
    }
    else if strpos(" fracreg betareg glm ", " `cmd' ") {
        local title "`cmd' — 分数结果与广义线性模型"
        local purpose1 "用于比例/分数型结果或需要自定义分布与链接函数的广义线性模型。"
        local purpose2 "fracreg 可处理 0/1 端点；betareg 要求 0<Y<1；GLM 的 family()/link() 决定模型形式。"
    }
    else if strpos(" heckman heckprobit heckoprobit heckpoisson ", " `cmd' ") {
        local title "`cmd' — 样本选择模型"
        local purpose1 "用于处理样本进入观察过程可能非随机所产生的选择问题。"
        local purpose2 "结果方程与选择方程需要按命令语法分别确认；复杂方程选项保留在原生 Stata options 中。"
    }
    else if strpos(" arima arfima arimasoc arfimasoc arch ucm mswitch threshold dfgls dfuller pperron corrgram cumsp pergram wntestb wntestq psdensity rolling forecast tsappend tsfill tsfilter tsreport tssmooth ", " `cmd' ") {
        local title "`cmd' — 单变量时间序列模型"
        local purpose1 "用于 ARIMA/ARFIMA、波动率、状态转换、门槛、单位根/白噪声、频域、滚动估计、滤波平滑与预测工作流。"
        local purpose2 "运行前应先确认时间变量和 tsset；滞后阶数、波动方程或状态成分按 Stata 语法设置。"
    }
    else if strpos(" dfuller pperron corrgram pergram ", " `cmd' ") {
        local title "`cmd' — 时间序列诊断与检验"
        local purpose1 "用于单位根、相关结构或周期特征等时间序列诊断。"
        local purpose2 "先确认时间序列已正确声明；滞后阶数、趋势项和检验选项在最后核对。"
    }
    else if strpos(" var svar vec varbasic varsoc vargranger varlmar varnorm varstable varwle vecrank veclmar vecnorm vecstable irf lpirf mgarch dfactor sspace xcorr ", " `cmd' ") {
        local title "`cmd' — 多变量时间序列"
        local purpose1 "用于 VAR/SVAR/VEC、协整秩与系统诊断、local projections、MGARCH、动态因子、状态空间和脉冲响应分析。"
        local purpose2 "先确认系统变量与时间结构；识别限制、滞后阶数和结果对象等参数按当前命令设置。"
    }
    else if strpos(" spregress spivregress spxtregress ", " `cmd' ") {
        local title "`cmd' — 空间回归模型"
        local purpose1 "用于结果变量受到空间相关、空间滞后或空间内生性影响的模型。"
        local purpose2 "运行前应先准备 Stata 空间数据与权重矩阵；空间权重和模型类型按命令语法填写。"
    }
    else if strpos(" xtunitroot xtcointtest xtdescribe xtsum xttab xtdata ", " `cmd' ") {
        local title "`cmd' — 面板数据工具与检验"
        local purpose1 "用于检查面板结构、分解 within/between 变异、变换 panel 数据，或执行单位根与协整检验。"
        local purpose2 "页面会先按 panel/time 执行 xtset；数据变换或时间序列检验还需核对命令自身的样本与渐近条件。"
        local panel_label "个体 / 面板变量"
        if inlist("`cmd'", "xtunitroot", "xtcointtest") local time_label "时间变量（检验必填）"
        else local time_label "时间变量（可按数据结构留空）"
    }
    else if strpos(" xtologit xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtivreg xtpcse xtgls xtregar xtrc xtstreg xteregress xteprobit xteoprobit xteintreg xtheckman xthtaylor xtdpd xtabond xtdpdsys ", " `cmd' ") {
        local title "`cmd' — 面板数据模型"
        local purpose1 "用于面板数据下的有序/计数结果、IV、FGLS/PCSE、序列相关、ERM、样本选择、Hausman–Taylor、生存、GEE、前沿或动态模型。"
        local purpose2 "页面会要求面板结构；模型、动态项和估计选项继续按 Stata 当前命令语法确认。"
        local panel_label "个体 / 面板变量"
        if inlist("`cmd'", "xtabond", "xtdpdsys", "xtdpd") local time_label "时间变量（动态面板必填）"
        else local time_label "时间变量（可按数据结构留空）"
    }
    else if strpos(" mixed mecloglog melogit meprobit mepoisson menbreg meologit meoprobit meintreg menl mestreg metobit meglm ", " `cmd' ") {
        local title "`cmd' — 多层混合效应模型"
        local purpose1 "用于观测嵌套在个体、学校、地区等层级结构中的混合效应模型。"
        local purpose2 "固定部分与随机部分应按层级结构填写；随机效应方程和协方差结构按 Stata 原生语法核对。"
    }
    else if strpos(" ctset cttost ltable snapspan stset stdescribe stsum stci stcurve stbase stfill stgen stsplit stvary sttocc sttoct sts stcox streg stintreg stintcox stcrreg stir strate stptime stmh stmc ", " `cmd' ") {
        if "`cmd'" != "stcox" {
            local title "`cmd' — 生存与事件史分析"
            local purpose1 "用于声明/检查/转换 survival data、非参数生存分析、率与人时汇总，以及 Cox、参数、区间删失和竞争风险模型。"
            local purpose2 "先确认失败事件、分析时间和删失定义；生存数据声明与模型 options 需在运行前核对。"
        }
    }
    else if strpos(" cc cs ir mcc dstdize pkexamine pksumm pkcross pkequiv pkcollapse pkshape ", " `cmd' ") {
        local title "`cmd' — 流行病学效应量"
        local purpose1 "用于病例对照、队列、发病率资料，以及 pharmacokinetic concentration–time、crossover 和 bioequivalence 分析。"
        local purpose2 "先确认病例/暴露或事件/时间变量角色；分层与置信区间选项按 Stata 命令设置。"
    }
    else if strpos(" eregress eprobit eoprobit eintreg ", " `cmd' ") {
        local title "`cmd' — 内生协变量模型"
        local purpose1 "用于结果方程中存在内生解释变量时的扩展回归模型。"
        local purpose2 "需要明确主结果方程与内生变量方程；复杂联立结构按 Stata 原生语法填写。"
    }
    else if strpos(" teffects eteffects etregress etpoisson stteffects telasso mediate hdidregress xthdidregress ", " `cmd' ") {
        local title "`cmd' — 处理效应与因果推断"
        local purpose1 "用于潜在结果框架下的处理效应估计或内生处理模型。"
        local purpose2 "先明确结果变量、处理变量和协变量；处理模型、倾向得分或结果模型选项在最后核对。"
    }
    else if strpos(" sem gsem ", " `cmd' ") {
        local title "`cmd' — 结构方程模型"
        local purpose1 "用于同时估计多个路径、潜变量和测量/结构关系。"
        local purpose2 "模型方程通常需要直接按 Stata SEM/GSEM 语法表达；复杂路径和 family/link 设置保留原生写法。"
    }
    else if "`cmd'" == "fmm" {
        local title "fmm — 有限混合模型"
        local purpose1 "把总体表示为若干未观测组分，并允许不同组分拥有不同回归参数或分布。"
        local purpose2 "第一步先确定潜在组分数量和冒号后的基础估计命令；类别数应结合理论与模型比较判断。"
    }
    else if strpos(" dsge dsgenl ", " `cmd' ") {
        local title "`cmd' — 动态随机一般均衡模型"
        local purpose1 "用于求解或估计线性化与非线性 DSGE 方程系统，并保留前瞻变量、状态变量和结构参数的原生模型表达。"
        local purpose2 "先 tsset 并明确 observed/unobserved controls 与 endogenous/exogenous states；稳定性、识别和稳态属于必要诊断。"
    }
    else if strpos(" irt irtgraph diflogistic difmh ", " `cmd' ") {
        local title "`cmd' — 项目反应理论"
        local purpose1 "用于估计 IRT 模型、绘制 item/test characteristic 与 information curves，并检查 differential item functioning。"
        local purpose2 "先确定题项类型与 IRT 模型，再选择全部题项变量；不同题型不能随意套用同一响应模型。"
    }
    else if "`cmd'" == "alpha" {
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
    else if strpos(" factor pca canon ca candisc hotelling manova mca mds mdslong mdsmat mvtest procrustes discrim cluster ", " `cmd' ") {
        local title "`cmd' — 多元统计分析"
        local purpose1 "用于降维、典型相关、多元方差、判别或聚类等多变量分析。"
        local purpose2 "先选择参与分析的变量；提取方法、距离、类别或维度等命令特有参数放在最后。"
    }
    else if "`cmd'" == "svyset" {
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
    else if "`cmd'" == "sqrtlasso" {
        local title "sqrtlasso — Square-root Lasso"
        local purpose1 "对连续结果进行 Square-root Lasso 预测与变量选择；它只对应线性结果模型。"
        local purpose2 "直接选择结果变量和候选预测变量，无需像 lasso / elasticnet 那样在因变量前填写 linear。"
        local has_depvar 1
        local has_varlist 1
        local dep_label "连续结果变量 Y"
        local vars_label "候选预测变量"
        local example1 "sqrtlasso y x1-x1000"
        local explain1 "官方基础语法：对连续结果 y 在 x1 到 x1000 中进行 Square-root Lasso 选择。"
        local example2 "help sqrtlasso"
        local explain2 "惩罚参数选择、聚类等设置按当前 Stata 版本核对。"
    }
    else if strpos(" lasso elasticnet poregress pologit popoisson dsregress dslogit dspoisson poivregress xporegress xpologit xpopoisson xpoivregress ", " `cmd' ") {
        local title "`cmd' — Lasso 与高维变量选择"
        local purpose1 "用于高维协变量下的正则化、双重选择、部分化或交叉拟合推断。"
        local purpose2 "先区分关注变量和 controls() 高维候选控制；预测型 lasso / elasticnet 还需要在因变量前明确模型类型。"
    }
    else if "`cmd'" == "meta" {
        local title "meta — Meta 分析"
        local purpose1 "用于汇总多项研究的效应量并进行异质性、亚组或回归分析。"
        local purpose2 "应先正确声明效应量及其标准误；模型和图形设置按 Stata meta 工作流继续完成。"
    }
    else if "`cmd'" == "mi" {
        local title "mi — 多重插补"
        local purpose1 "用于多重插补数据的声明、插补、管理与估计。"
        local purpose2 "mi 是工作流型命令；应先明确当前处于 set、impute、estimate 或数据管理的哪一步。"
    }
    else if strpos(" npregress nptrend lowess lpoly ", " `cmd' ") {
        local title "`cmd' — 非参数与平滑分析"
        local purpose1 "用于 kernel/series 非参数回归、跨有序组趋势检验或局部平滑，减少对函数形式和分布的强假设。"
        local purpose2 "带宽、核函数和局部多项式阶数会影响结果；建议结合右侧图形或结果诊断。"
    }
    else if strpos(" exlogistic expoisson bitest bitesti ksmirnov symmetry tetrachoric tabi ", " `cmd' ") {
        local title "`cmd' — 精确统计"
        local purpose1 "用于小样本或汇总计数资料的精确检验与列联表分析。"
        local purpose2 "直接填写计数或概率参数；检验方向和置信水平等选项在运行前核对。"
    }
    else if strpos(" bootstrap jackknife permute simulate statsby ", " `cmd' ") {
        local title "`cmd' — 重抽样与模拟"
        local purpose1 "用于 bootstrap、jackknife、置换检验、模拟或按组重复统计。"
        local purpose2 "需要明确被重复执行的统计量/命令以及重复次数；随机种子与保存选项建议在运行前显式设置。"
    }
    else if "`cmd'" == "power" {
        local title "power — 效能与样本量"
        local purpose1 "用于研究设计阶段计算统计效能、所需样本量或可检测效应。"
        local purpose2 "先明确检验类型、效应大小、显著性水平和目标 power，再核对设计参数。"
    }
    else if strpos(" bayes bayesmh bayespredict bayesreps bayesstats bayesgraph bayestest bayesvarstable bayesirf bayesfcast ", " `cmd' ") {
        local title "`cmd' — 贝叶斯分析"
        local purpose1 "用于贝叶斯模型估计、MCMC、后验预测、诊断或结果图形。"
        local purpose2 "先验、采样设置和后验结果对象是核心；运行前应明确当前是估计、诊断还是后估计任务。"
    }
    else if strpos(" bmaregress bmacoefsample bmagraph bmastats bmapredict ", " `cmd' ") {
        local title "`cmd' — 贝叶斯模型平均"
        local purpose1 "用于 BMA 线性回归、posterior coefficient sampling、模型概率/变量包含诊断与 model-averaged prediction。"
        local purpose2 "这些入口都属于 Stata 18+；先完成 bmaregress，再按当前后估计任务选择 sampling、graph、stats 或 predict。"
    }
    else if "`cmd'" == "graph" {
        local title "graph — Stata 图形管理入口"
        local purpose1 "用于调用、管理或组合 Stata 图形命令。"
        local purpose2 "具体图形类型差异较大；建议从左侧图形分类选择更具体的命令页面。"
    }
    else if "`cmd'" == "twoway" {
        local title "twoway — 二维叠加图"
        local purpose1 "用于把散点、折线、拟合线、置信区间等多个二维图层叠加。"
        local purpose2 "图层主体保持 Stata 原生 twoway 语法，适合在实时命令中继续精修。"
    }
    else if strpos(" line connected qfit dotplot graph_box ", " `cmd' ") {
        local title "`cmd' — 基础统计图形"
        local purpose1 "用于展示变量随 X 的变化、拟合关系或分布/分组特征。"
        local purpose2 "先确定主要变量与坐标/分组角色；样本条件和图形 options 放在最后。"
    }
    else if strpos(" rvfplot rvpplot avplot avplots lvr2plot cprplot acprplot ", " `cmd' ") {
        local title "`cmd' — 回归诊断图"
        local purpose1 "用于回归后检查残差、影响点、部分关系或模型设定。"
        local purpose2 "需要先成功运行兼容的估计命令；诊断图的解释应结合残差结构和模型假设。"
    }
    else if strpos(" tsline xtline ", " `cmd' ") {
        local title "`cmd' — 时间/面板趋势图"
        local purpose1 "用于按时间展示单序列或面板变量的变化轨迹。"
        local purpose2 "运行前应正确声明时间或面板结构；分组、叠加和样式 options 放在最后。"
    }
    else if strpos(" roctab rocfit roccomp rocgold rocreg rocregplot ", " `cmd' ") {
        local title "`cmd' — ROC 分析"
        if "`cmd'" == "rocfit" {
            local purpose1 "拟合单一 classifier 的参数化 binormal ROC 模型；本命令首先产生估计结果，而不是直接绘图。"
            local purpose2 "需要拟合后的 ROC 图时使用 rocfit 的后估计绘图工具；不要把 rocfit 本身当成纯绘图命令。"
        }
        else if "`cmd'" == "rocreg" {
            local purpose1 "用协变量调整敏感度/特异度并进行 ROC regression；这是 ROC suite 中更一般的估计模型。"
            local purpose2 "roccov()/ctrlcov() 等结构属于模型本身；拟合后的协变量特定 ROC 曲线交给 rocregplot。"
        }
        else if "`cmd'" == "rocregplot" {
            local purpose1 "在 rocreg 估计之后绘制模型隐含的 ROC 曲线，可按 classifier 或协变量取值比较。"
            local purpose2 "这是 rocreg 的后估计绘图命令；先成功运行 rocreg，再设置 at#()、图例、标题和其他 graph options。"
        }
        else {
            local purpose1 "用于非参数 ROC 估计、ROC 面积比较或与 gold-standard ROC 曲线比较。"
            local purpose2 "先明确真实二元结局和预测评分；比较与图形设置按当前命令语法填写。"
        }
    }

