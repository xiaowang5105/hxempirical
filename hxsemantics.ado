*! hxsemantics 1.4.1  12aug2026
*! Interpret parsed Stata syntax as beginner-facing parameter roles.
program define hxsemantics, rclass
    version 16.0
    #delimit ;
    syntax , COMMAND(name)
        DEPVAR(integer) VARLIST(integer) IFLAG(integer) INFLAG(integer)
        WEIGHT(integer) USING(integer) NEWVAR(integer) EXPRESSION(integer)
        ABSORB(integer) VCE(integer) CLUSTER(integer) IV(integer)
        PANEL(integer) MODELBEFORE(integer)
        [MODELS(string asis) VCES(string asis) QUALITY(string asis)];
    #delimit cr

    local cmd = lower("`command'")
    foreach item in models vces quality {
        local `item' = trim(`"``item''"')
        if substr(`"``item''"', 1, 1) == char(34) & ///
            substr(`"``item''"', -1, 1) == char(34) {
            local `item' = substr(`"``item''"', 2, strlen(`"``item''"') - 2)
        }
    }

    /* Start from the unified parser.  Semantic rules only translate roles. */
    local has_depvar `depvar'
    local has_varlist `varlist'
    local has_if `iflag'
    local has_in `inflag'
    local has_weight `weight'
    local has_using `using'
    local has_newvar `newvar'
    local has_expression `expression'
    local has_absorb `absorb'
    local has_vce `vce'
    local has_cluster `cluster'
    local has_iv `iv'
    local needs_panel `panel'
    local model_before `modelbefore'

    local template "generic"
    local title "`cmd' — Stata 命令"
    local purpose1 "根据 Stata 的 syntax、help、Examples 和官方窗口生成设置页面。"
    local purpose2 "先填写能够确认的参数；少数无法解释的内容放在“更多设置”。"
    local dep_label "因变量（解释谁）"
    local vars_label "变量"
    local newvar_label "新变量名（自己起）"
    local expr_label "数值或计算公式"
    local model_label "方法 / 模型"
    local default_model ""
    local absorb_label "固定效应 absorb()"
    local endog_label "内生变量（需要处理）"
    local inst_label "工具变量"
    local using_label "副表 / using 文件"
    local panel_label "个体 / 面板变量"
    local time_label "时间变量"
    local if_label "样本条件 if（可选）"
    local example1 "`cmd' y x"
    local explain1 "示意：请结合页面字段和 Help 确认该命令的实际参数。"
    local example2 "help `cmd'"
    local explain2 "查看 Stata 当前安装版本提供的完整说明和 Examples。"
    local default_expression ""
    local show_advanced = (`"`quality'"' == "部分参数需要手动输入")
    local show_merge_check 0
    local is_xtset 0
    local keepdrop_mode 0
    local winsor_mode 0
    local predict_mode 0

    if "`cmd'" == "generate" {
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
    else if inlist("`cmd'", "test", "lincom", "predict", "margins") {
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

    if `"`models'"' != "" {
        local models = trim(itrim(`"`models'"'))
        local models : list uniq models
    }
    if `"`default_model'"' == "" local default_model : word 1 of `models'
    if `"`vces'"' == "" local vces "default"

    foreach key in title purpose1 purpose2 dep_label vars_label newvar_label ///
        expr_label model_label absorb_label endog_label inst_label ///
        using_label panel_label time_label if_label example1 explain1 example2 explain2 ///
        template default_expression {
        char _dta[hxtoolbox_sem_`key'] `"``key''"'
    }
    foreach key in show_advanced show_merge_check is_xtset keepdrop_mode ///
        winsor_mode predict_mode {
        char _dta[hxtoolbox_sem_`key'] "``key''"
    }

    foreach flag in has_depvar has_varlist has_if has_in has_weight ///
        has_using has_newvar has_expression has_absorb has_vce ///
        has_cluster has_iv needs_panel model_before {
        return scalar `flag' = ``flag''
    }
    return scalar show_advanced = `show_advanced'
    return scalar show_merge_check = `show_merge_check'
    return scalar is_xtset = `is_xtset'
    return scalar keepdrop_mode = `keepdrop_mode'
    return scalar winsor_mode = `winsor_mode'
    return scalar predict_mode = `predict_mode'
    return local template `"`template'"'
    return local title `"`title'"'
    return local models `"`models'"'
    return local default_model `"`default_model'"'
    return local vces `"`vces'"'
end
