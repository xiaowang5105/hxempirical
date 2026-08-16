*! hxsemantics 1.4.3  16aug2026
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
    if strpos(" sem gsem mi meta fmm irt svy bootstrap jackknife permute simulate statsby bayes bayesmh bayespredict bayesstats bayesgraph power teffects sts irf graph discrim cluster table prtest sdtest oneway anova ranksum median signrank signtest bitesti tabi cc cs ir sureg mvreg canon cca manova heckman heckprobit heckoprobit heckpoisson eregress eprobit eoprobit eintreg mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm lasso elasticnet npregress stset streg stcrreg arima arch ucm dfuller pperron corrgram pergram var svar vec varsoc vargranger varstable spregress spivregress spxtregress xtgee xttobit xtintreg xtfrontier xtabond xtdpdsys dsregress poivregress xporegress xpoivregress etregress etpoisson fracreg zip zinb tpoisson tnbreg glm hetprobit asclogit asmprobit ", " `cmd' ") {
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
        else if "`cmd'" == "gsem" {
            local expr_label "广义 SEM 方程 + family()/link()/随机效应/潜在类别设定"
            local example1 "gsem (y <- x1 x2, family(bernoulli) link(logit))"
            local explain1 "对二元结果 y 拟合 logit 链接的广义结构方程。"
            local example2 "help gsem"
            local explain2 "多层、潜在类别、选择模型等 gsem 结构差异很大，复杂模型继续按当前 help 核对。"
        }
        else if "`cmd'" == "mi" {
            local expr_label "mi 子命令与完整参数（如 set / impute / estimate）"
            local example1 "mi set mlong"
            local explain1 "先声明多重插补数据格式。"
            local example2 "mi estimate: regress y x1 x2"
            local explain2 "估计阶段可把完整 mi estimate 前缀主体直接写在这里。"
        }
        else if "`cmd'" == "meta" {
            local expr_label "meta 子命令与完整参数（如 set / summarize / regress）"
            local example1 "meta summarize"
            local explain1 "对已经声明的 meta 数据进行汇总。"
            local example2 "meta regress x1 x2"
            local explain2 "执行 meta 回归；数据声明可使用 meta set / meta esize。"
        }
        else if "`cmd'" == "fmm" {
            local expr_label "类别数 + 冒号后的估计命令（如 2: regress y x1 x2）"
            local example1 "fmm 2: regress y x1 x2"
            local explain1 "拟合两类有限混合线性回归。"
            local example2 "fmm 3: poisson y x1 x2"
            local explain2 "拟合三类有限混合 Poisson 模型。"
        }
        else if "`cmd'" == "irt" {
            local expr_label "IRT 模型 + 题项变量（如 2pl item1-item10）"
            local example1 "irt 2pl item1-item10"
            local explain1 "拟合二参数 Logistic IRT 模型。"
            local example2 "irt grm item1-item10"
            local explain2 "拟合 graded response model。"
        }
        else if "`cmd'" == "svy" {
            local expr_label "冒号后的估计命令（以 : 开头，如 : mean y）"
            local example1 "svy: mean y"
            local explain1 "在已 svyset 的调查设计下估计总体均值。"
            local example2 "svy: regress y x1 x2"
            local explain2 "在复杂抽样设计下运行线性回归。"
        }
        else if strpos(" bootstrap jackknife permute simulate statsby ", " `cmd' ") {
            local expr_label "统计量 / 前缀参数 + 冒号后的命令（完整写出命令名后的部分）"
            if "`cmd'" == "bootstrap" {
                local example1 "bootstrap r(mean), reps(500): summarize y"
                local explain1 "对 summarize 返回的均值进行 bootstrap。"
            }
            else if "`cmd'" == "jackknife" {
                local example1 "jackknife r(mean): summarize y"
                local explain1 "对 summarize 返回的均值进行 jackknife。"
            }
            else {
                local example1 "help `cmd'"
                local explain1 "该命令包含前缀统计量、重复设置或冒号后的被执行命令，请按当前 help 填写完整主体。"
            }
        }
        else if "`cmd'" == "bayes" {
            local expr_label "Bayes 前缀主体（如 : regress y x；前缀 options 也写在这里）"
            local example1 "bayes: regress y x1 x2"
            local explain1 "用 bayes: 前缀估计标准回归模型。"
            local example2 "bayes, gibbs: regress y x1 x2"
            local explain2 "Bayes 前缀自身的 options 位于冒号前。"
        }
        else if "`cmd'" == "bayesmh" {
            local expr_label "Bayesian 模型主体（结果变量、解释变量、likelihood、prior 等）"
            local example1 "bayesmh y x, likelihood(normal({sigma2})) prior({y:x _cons}, normal(0,100))"
            local explain1 "bayesmh 的似然和先验均属于完整模型主体。"
        }
        else if strpos(" bayespredict bayesstats bayesgraph ", " `cmd' ") {
            local expr_label "Bayesian 后估计子命令 / 结果对象与参数"
            local example1 "help `cmd'"
            local explain1 "先确认上一项 Bayesian 估计结果，再按当前后估计命令的子命令语法填写。"
        }
        else if "`cmd'" == "power" {
            local expr_label "检验类型与设计参数（如 onemean 0 0.5, power(.8)）"
            local example1 "power onemean 0 0.5, power(.8)"
            local explain1 "一元均值检验的效能 / 样本量设计。"
            local example2 "power twomeans 0 0.5, power(.8)"
            local explain2 "两组均值比较的效能 / 样本量设计。"
        }
        else if "`cmd'" == "teffects" {
            local expr_label "估计器 + 结果方程 + 处理方程（如 psmatch (y) (treat x1 x2)）"
            local example1 "teffects psmatch (y) (treat x1 x2)"
            local explain1 "使用倾向得分匹配估计处理效应。"
            local example2 "teffects ipwra (y x1 x3) (treat x1 x2)"
            local explain2 "使用双重稳健 IPWRA。"
        }
        else if strpos(" table prtest sdtest oneway anova ranksum median signrank signtest bitesti tabi ", " `cmd' ") {
            local expr_label "检验 / 表格主体（变量、分组、比较值或计数参数）"
            local example1 "help `cmd'"
            local explain1 "这些命令的变量角色和参数顺序差异较大，页面保留官方原生命令主体，避免把分组变量或比较值误标成解释变量。"
        }
        else if strpos(" cc cs ir ", " `cmd' ") {
            local expr_label "流行病学命令主体（病例 / 暴露 / 时间 / 分层参数）"
            local example1 "help `cmd'"
            local explain1 "病例对照、队列和发病率命令的变量角色不同，按当前 help 填写完整主体。"
        }
        else if strpos(" sureg mvreg canon cca manova ", " `cmd' ") {
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
        else if strpos(" heckman heckprobit heckoprobit heckpoisson ", " `cmd' ") {
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
        else if strpos(" eregress eprobit eoprobit eintreg ", " `cmd' ") {
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
        else if "`cmd'" == "arima" {
            local expr_label "结果变量 + 外生变量（可选）+ ARIMA 阶数 / AR-MA 设定"
            local example1 "arima y, arima(1,0,1)"
            local explain1 "估计 ARIMA(1,0,1)；阶数是模型核心设定。"
            local example2 "arima y x1 x2, arima(1,0,0)"
            local explain2 "在 AR(1) 动态回归中加入 x1、x2 外生解释变量。"
        }
        else if "`cmd'" == "arch" {
            local expr_label "结果变量 + 均值方程变量（可选）+ arch()/garch() 等波动设定"
            local example1 "arch y, arch(1) garch(1)"
            local explain1 "估计标准 GARCH(1,1) 波动模型。"
            local example2 "arch y x1, arch(1) garch(1)"
            local explain2 "在均值方程加入 x1，同时估计 GARCH(1,1)。"
        }
        else if "`cmd'" == "ucm" {
            local expr_label "结果变量 + 外生变量（可选）+ seasonal()/cycle() 等成分"
            local example1 "ucm y, seasonal(12) cycle(1)"
            local explain1 "按 12 期季节项和一阶周期成分拟合不可观测成分模型。"
            local example2 "help ucm"
            local explain2 "趋势、季节和周期成分取决于研究设计；运行前核对当前 Stata 版本支持的成分。"
        }
        else if "`cmd'" == "dfuller" {
            local expr_label "待检验序列 + lags() / trend 等 ADF 设定"
            local example1 "dfuller y, lags(1)"
            local explain1 "对 y 进行带 1 阶增广项的 Dickey–Fuller 单位根检验。"
            local example2 "dfuller y, lags(1) trend"
            local explain2 "在检验回归中加入确定性时间趋势。"
        }
        else if "`cmd'" == "pperron" {
            local expr_label "待检验序列 + Newey–West 滞后 / trend 等设定"
            local example1 "pperron y"
            local explain1 "对 y 进行 Phillips–Perron 单位根检验。"
            local example2 "pperron y, trend"
            local explain2 "在检验回归中加入确定性时间趋势。"
        }
        else if "`cmd'" == "corrgram" {
            local expr_label "待诊断序列 + lags() 等相关图设定"
            local example1 "corrgram y, lags(12)"
            local explain1 "查看 y 到 12 阶的自相关、偏自相关和 Q 统计量。"
        }
        else if "`cmd'" == "pergram" {
            local expr_label "待分析序列 + periodogram options"
            local example1 "pergram y"
            local explain1 "绘制 y 的 periodogram，用于查看周期频率结构。"
        }
        else if "`cmd'" == "var" {
            local expr_label "系统内生变量 + lags() 等 VAR 设定"
            local example1 "var y1 y2, lags(1/2)"
            local explain1 "把 y1、y2 都作为内生变量估计 1 至 2 阶 VAR。"
        }
        else if "`cmd'" == "svar" {
            local expr_label "系统变量 + lags() + A/B 识别矩阵（aeq()/beq()）"
            local example1 "help svar"
            local explain1 "SVAR 需要由识别假设定义 A/B 矩阵；先核对官方示例再填写。"
            local example2 "svar y1 y2, lags(1/2) aeq(A) beq(B)"
            local explain2 "使用事先定义的 A、B 识别矩阵估计结构 VAR。"
        }
        else if "`cmd'" == "vec" {
            local expr_label "系统变量 + rank() + lags() 等协整/VEC 设定"
            local example1 "vec y1 y2, rank(1) lags(2)"
            local explain1 "在协整秩为 1、VAR 阶数为 2 的设定下估计 VEC 模型。"
        }
        else if "`cmd'" == "varsoc" {
            local expr_label "系统变量 + maxlag() 等阶数选择设定"
            local example1 "varsoc y1 y2, maxlag(4)"
            local explain1 "比较 y1、y2 的候选滞后阶数，最大检查 4 阶。"
        }
        else if "`cmd'" == "vargranger" {
            local expr_label "VAR/VEC 估计后的 Granger 因果检验 options（通常可留空）"
            local example1 "vargranger"
            local explain1 "对上一项 VAR/VEC 结果执行 Granger 因果检验。"
            local example2 "help vargranger"
            local explain2 "需要更细的限制或显示设置时核对当前 Stata 版本的 options。"
        }
        else if "`cmd'" == "varstable" {
            local expr_label "VAR/SVAR 估计后的稳定性检验 options（通常可留空）"
            local example1 "varstable"
            local explain1 "检查上一项 VAR/SVAR 的特征根稳定性条件。"
            local example2 "help varstable"
            local explain2 "图形或其他稳定性设置按当前 Stata 版本核对。"
        }
        else if "`cmd'" == "spregress" {
            local expr_label "Y + X + 估计方法 + dvarlag()/ivarlag()/errorlag()"
            local example1 "spregress y x, gs2sls dvarlag(W)"
            local explain1 "使用预先创建的 W 对因变量加入空间滞后，并用 GS2SLS 估计。"
            local example2 "spregress y x, ml dvarlag(W)"
            local explain2 "使用 ML 估计因变量空间滞后模型。"
        }
        else if "`cmd'" == "spivregress" {
            local expr_label "Y + 外生 X + (内生变量 = 工具变量) + 空间权重设定"
            local example1 "spivregress y x1 (x2 = z), dvarlag(W) errorlag(M)"
            local explain1 "同时保留 IV 方程、因变量空间滞后和空间误差；W/M 需事先创建。"
            local example2 "help spivregress"
            local explain2 "ivarlag() 等更复杂空间结构按研究设定继续补充。"
        }
        else if "`cmd'" == "spxtregress" {
            local expr_label "Y + X + FE/RE + dvarlag()/ivarlag()/errorlag()"
            local example1 "spxtregress y x, fe dvarlag(W) errorlag(M)"
            local explain1 "在已声明的空间面板数据上估计固定效应空间自回归模型。"
            local example2 "spxtregress y x, re dvarlag(W) errorlag(M)"
            local explain2 "随机效应空间面板模型使用同样的空间权重结构。"
        }
        else if "`cmd'" == "xtgee" {
            local expr_label "Y + X + family() + link() + corr()（GEE 核心设定）"
            local example1 "xtgee union age not_smsa, family(binomial) link(probit) corr(exchangeable)"
            local explain1 "二元结果采用 Probit 链接，并用 exchangeable 工作相关结构处理面板内相关。"
            local example2 "xtgee y x1 x2, family(gaussian) link(identity) corr(independent)"
            local explain2 "连续结果可使用 Gaussian + identity；相关结构应由数据与研究设计决定。"
        }
        else if "`cmd'" == "xttobit" {
            local expr_label "Y + X + ll()/ul() 截尾界限"
            local example1 "xttobit y x1 x2, ll(0)"
            local explain1 "随机效应面板 Tobit，结果在 0 处左删失。"
            local example2 "help xttobit"
            local explain2 "右删失或双侧删失时继续设置 ul() / ll()。"
        }
        else if "`cmd'" == "xtintreg" {
            local expr_label "结果下界 + 结果上界 + X（例如 ylower yupper x1 x2）"
            local example1 "xtintreg ylower yupper x1 x2 x3"
            local explain1 "ylower、yupper 分别记录区间结果的下界和上界；这两个结果变量都属于核心语法。"
            local example2 "help xtintreg"
            local explain2 "左删失、右删失和精确观测通过上下界变量中的缺失/相等关系表达。"
        }
        else if "`cmd'" == "xtfrontier" {
            local expr_label "Y + X + ti/tvd + production/cost 等前沿设定"
            local example1 "xtfrontier y x1 x2, ti"
            local explain1 "估计时间不变 inefficiency 的面板随机前沿模型。"
            local example2 "xtfrontier y x1 x2, tvd"
            local explain2 "tvd 允许 inefficiency 随时间按共同衰减结构变化。"
        }
        else if "`cmd'" == "xtabond" {
            local expr_label "Y + X + lags()/maxldep()/pre()/endogenous()/twostep 等动态面板设定"
            local example1 "xtabond y x1 x2, lags(1)"
            local explain1 "Arellano–Bond 差分 GMM；lags(1) 指定因变量动态滞后阶数。"
            local example2 "help xtabond"
            local explain2 "工具变量集合、预定变量、两步估计和 AR 检验会显著影响结果，运行前逐项核对。"
        }
        else if "`cmd'" == "xtdpdsys" {
            local expr_label "Y + X + lags()/maxldep()/pre()/endogenous()/twostep 等系统 GMM 设定"
            local example1 "xtdpdsys y x1 x2, lags(1)"
            local explain1 "Arellano–Bover/Blundell–Bond 系统估计同时利用差分方程和水平方程矩条件。"
            local example2 "help xtdpdsys"
            local explain2 "系统 GMM 的工具变量数量与有效性需要在研究中单独诊断。"
        }
        else if strpos(" mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm ", " `cmd' ") {
            local expr_label "固定部分 + || 随机效应层级（如 y x1 x2 || school: x2 || class:）"
            if "`cmd'" == "mixed" {
                local example1 "mixed y x1 x2 || school: x2 || class:"
                local explain1 "固定效应写在前面，|| 后按层级写随机截距 / 随机斜率。"
            }
            else {
                local example1 "help `cmd'"
                local explain1 "多层模型的 || 随机效应结构属于核心模型主体，不能只用普通 Y/X 框代替。"
            }
        }
        else if inlist("`cmd'", "lasso", "elasticnet") {
            local expr_label "模型类型 + 因变量 + 候选变量（如 linear y x1-x100）"
            local example1 "`cmd' linear y x1-x100"
            local explain1 "lasso / elasticnet 在因变量前需要明确 linear、logit、probit、poisson 或 cox 等模型类型。"
        }
        else if "`cmd'" == "npregress" {
            local expr_label "非参数方法 + 因变量 + 协变量（如 kernel y x1 x2 或 series y x1 x2）"
            local example1 "npregress kernel y x1 x2"
            local explain1 "kernel / series 是 npregress 的核心方法词，必须放在因变量之前。"
            local example2 "npregress series y x1 x2"
            local explain2 "使用 series 非参数回归。"
        }
        else if "`cmd'" == "stset" {
            local expr_label "生存数据声明主体（分析时间、failure()、id()、enter()/exit() 等）"
            local example1 "help stset"
            local explain1 "stset 同时定义分析时间、失败事件和风险区间，完整主体比单一变量框更清楚。"
        }
        else if "`cmd'" == "streg" {
            local expr_label "协变量 + 参数分布等核心 options（如 age protect, distribution(weibull)）"
            local example1 "streg protect age, distribution(weibull)"
            local explain1 "失败事件与分析时间来自 stset；这里填写协变量和参数生存分布。"
            local example2 "streg age, distribution(exponential)"
            local explain2 "以指数分布拟合参数生存模型。"
        }
        else if "`cmd'" == "stcrreg" {
            local expr_label "协变量 + compete()（如 ifp tumsize, compete(failtype==2)）"
            local example1 "stcrreg ifp tumsize pelnode, compete(failtype==2)"
            local explain1 "失败事件来自 stset，compete() 指定竞争事件。"
        }
        else if "`cmd'" == "dsregress" {
            local expr_label "Y + 关注变量 + controls()（如 y d1, controls(x1-x100)）"
            local example1 "dsregress y d1, controls(x1-x100)"
            local explain1 "d1 是关注变量，controls() 中的高维候选控制由 lasso 选择。"
        }
        else if inlist("`cmd'", "poivregress", "xpoivregress") {
            local expr_label "Y + 关注变量 + (内生变量 = 工具变量) + controls()"
            local example1 "`cmd' y d1 (x = z1-z20), controls(c1-c100)"
            local explain1 "把关注变量、IV 方程和高维候选控制完整保留在一个主体中。"
        }
        else if "`cmd'" == "xporegress" {
            local expr_label "Y + 关注变量 + controls()（交叉拟合 partialing-out）"
            local example1 "xporegress y d1, controls(x1-x100)"
            local explain1 "d1 是需要推断的变量，controls() 交给 lasso 选择并交叉拟合。"
        }
        else if inlist("`cmd'", "etregress", "etpoisson") {
            local expr_label "结果方程 + treat() 处理方程"
            local example1 "etregress wage age grade, treat(union = south black tenure)"
            local explain1 "主结果方程写在前面，内生处理变量及其协变量写进 treat()。"
            local example2 "help `cmd'"
            local explain2 "etpoisson 与 etregress 的结果分布不同，处理方程结构仍需显式保留。"
        }
        else if "`cmd'" == "fracreg" {
            local expr_label "链接模型 + Y + X（如 probit prate mrate sole）"
            local example1 "fracreg probit prate mrate sole"
            local explain1 "fracreg 的 probit/logit 等模型词位于结果变量之前。"
            local example2 "fracreg logit prate mrate sole"
            local explain2 "使用 fractional logit 拟合比例结果。"
        }
        else if inlist("`cmd'", "zip", "zinb") {
            local expr_label "计数方程 + inflate() 零膨胀方程"
            local example1 "`cmd' y x1 x2, inflate(z1 z2)"
            local explain1 "主计数方程与产生额外零值的 inflate() 方程需要同时明确。"
        }
        else if inlist("`cmd'", "tpoisson", "tnbreg") {
            local expr_label "Y + X + 截断点 options（ll()/ul()）"
            local example1 "`cmd' y x1 x2, ll(0)"
            local explain1 "截断模型必须把样本截断边界作为模型核心设定核对。"
        }
        else if "`cmd'" == "glm" {
            local expr_label "Y + X + family()/link()（如 y x, family(poisson) link(log)）"
            local example1 "glm y x, family(poisson) link(log)"
            local explain1 "GLM 的分布族和链接函数决定模型形式，因此和变量一起放在核心主体。"
        }
        else if "`cmd'" == "hetprobit" {
            local expr_label "主 Probit 方程 + het() 异方差方程"
            local example1 "hetprobit y x1 x2, het(z1 z2)"
            local explain1 "het() 中的变量决定潜在误差方差，需要与主方程一起确认。"
        }
        else if inlist("`cmd'", "asclogit", "asmprobit") {
            local expr_label "选择指示 + 备选项变量 + case()/alternatives()/casevars()"
            local example1 "`cmd' choice price, case(id) alternatives(alt) casevars(income age)"
            local explain1 "备选项特征、选择场景 ID、备选项 ID 与个体特征都属于离散选择模型的核心结构。"
        }
        else if "`cmd'" == "sts" {
            local expr_label "sts 子命令与参数（如 graph / list / test group）"
        }
        else if "`cmd'" == "irf" {
            local expr_label "irf 子命令与参数（如 create / graph / table）"
        }
        else if "`cmd'" == "graph" {
            local expr_label "graph 子命令与参数（如 combine / save / export / display）"
        }
        else if inlist("`cmd'", "discrim", "cluster") {
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

    /* Family-level copy for catalog commands that rely on the generic syntax parser.
       Keep the parsed Stata syntax/flags unchanged; only improve beginner-facing semantics. */
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
        local purpose1 "用于比例/分数型因变量或需要自定义分布与链接函数的广义线性模型。"
        local purpose2 "先设置因变量和解释变量；family()、link() 等分布与链接设置按当前命令填写。"
    }
    else if strpos(" heckman heckprobit heckoprobit heckpoisson ", " `cmd' ") {
        local title "`cmd' — 样本选择模型"
        local purpose1 "用于处理样本进入观察过程可能非随机所产生的选择问题。"
        local purpose2 "结果方程与选择方程需要按命令语法分别确认；复杂方程选项保留在原生 Stata options 中。"
    }
    else if strpos(" arima arch ucm ", " `cmd' ") {
        local title "`cmd' — 单变量时间序列模型"
        local purpose1 "用于 ARIMA、ARCH/GARCH 或不可观测成分等时间序列建模。"
        local purpose2 "运行前应先确认时间变量和 tsset；滞后阶数、波动方程或状态成分按 Stata 语法设置。"
    }
    else if strpos(" dfuller pperron corrgram pergram ", " `cmd' ") {
        local title "`cmd' — 时间序列诊断与检验"
        local purpose1 "用于单位根、相关结构或周期特征等时间序列诊断。"
        local purpose2 "先确认时间序列已正确声明；滞后阶数、趋势项和检验选项在最后核对。"
    }
    else if strpos(" var svar vec varsoc vargranger varstable irf ", " `cmd' ") {
        local title "`cmd' — 多变量时间序列"
        local purpose1 "用于 VAR/SVAR/VEC、滞后阶数选择、Granger 检验、稳定性或脉冲响应分析。"
        local purpose2 "先确认系统变量与时间结构；识别限制、滞后阶数和结果对象等参数按当前命令设置。"
    }
    else if strpos(" spregress spivregress spxtregress ", " `cmd' ") {
        local title "`cmd' — 空间回归模型"
        local purpose1 "用于结果变量受到空间相关、空间滞后或空间内生性影响的模型。"
        local purpose2 "运行前应先准备 Stata 空间数据与权重矩阵；空间权重和模型类型按命令语法填写。"
    }
    else if strpos(" xtpoisson xtnbreg xtgee xttobit xtcloglog xtintreg xtoprobit xtmlogit xtfrontier xtabond xtdpdsys ", " `cmd' ") {
        local title "`cmd' — 面板数据模型"
        local purpose1 "用于面板数据下的计数、受限因变量、GEE、前沿或动态面板模型。"
        local purpose2 "页面会要求面板结构；模型、动态项和估计选项继续按 Stata 当前命令语法确认。"
        local panel_label "个体 / 面板变量"
        if inlist("`cmd'", "xtabond", "xtdpdsys") local time_label "时间变量（动态面板必填）"
        else local time_label "时间变量（可按数据结构留空）"
    }
    else if strpos(" mixed melogit meprobit mepoisson menbreg meologit meoprobit mestreg metobit meglm ", " `cmd' ") {
        local title "`cmd' — 多层混合效应模型"
        local purpose1 "用于观测嵌套在个体、学校、地区等层级结构中的混合效应模型。"
        local purpose2 "固定部分与随机部分应按层级结构填写；随机效应方程和协方差结构按 Stata 原生语法核对。"
    }
    else if strpos(" stset sts stcox streg stcrreg ", " `cmd' ") {
        if "`cmd'" != "stcox" {
            local title "`cmd' — 生存与事件史分析"
            local purpose1 "用于声明生存数据、绘制生存函数或估计参数生存与竞争风险模型。"
            local purpose2 "先确认失败事件、分析时间和删失定义；生存数据声明与模型 options 需在运行前核对。"
        }
    }
    else if strpos(" cc cs ir ", " `cmd' ") {
        local title "`cmd' — 流行病学效应量"
        local purpose1 "用于病例对照、队列或发病率资料的比值比、风险比和相关效应量计算。"
        local purpose2 "先确认病例/暴露或事件/时间变量角色；分层与置信区间选项按 Stata 命令设置。"
    }
    else if strpos(" eregress eprobit eoprobit eintreg ", " `cmd' ") {
        local title "`cmd' — 内生协变量模型"
        local purpose1 "用于结果方程中存在内生解释变量时的扩展回归模型。"
        local purpose2 "需要明确主结果方程与内生变量方程；复杂联立结构按 Stata 原生语法填写。"
    }
    else if strpos(" teffects etregress etpoisson ", " `cmd' ") {
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
    else if "`cmd'" == "irt" {
        local title "irt — 项目反应理论"
        local purpose1 "用 Rasch、1PL/2PL/3PL、GRM 等模型分析潜在能力与题项反应之间的关系。"
        local purpose2 "先确定题项类型与 IRT 模型，再选择全部题项变量；不同题型不能随意套用同一响应模型。"
    }
    else if strpos(" factor pca canon cca manova discrim cluster ", " `cmd' ") {
        local title "`cmd' — 多元统计分析"
        local purpose1 "用于降维、典型相关、多元方差、判别或聚类等多变量分析。"
        local purpose2 "先选择参与分析的变量；提取方法、距离、类别或维度等命令特有参数放在最后。"
    }
    else if "`cmd'" == "svy" {
        local title "svy — 调查数据估计"
        local purpose1 "用于复杂抽样设计下的加权估计和设计型标准误。"
        local purpose2 "应先用 svyset 正确声明抽样设计；本页执行的估计命令需与该设计保持一致。"
    }
    else if strpos(" lasso elasticnet sqrtlasso dsregress poivregress xporegress xpoivregress ", " `cmd' ") {
        local title "`cmd' — Lasso 与高维变量选择"
        local purpose1 "用于高维协变量下的正则化、双重选择或部分线性/工具变量估计。"
        local purpose2 "结果变量、候选变量和惩罚/选择规则应结合具体方法设置；运行前核对模型目标与推断口径。"
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
    else if strpos(" npregress lowess lpoly ", " `cmd' ") {
        local title "`cmd' — 非参数与平滑分析"
        local purpose1 "用于非参数回归或局部平滑，减少对函数形式的强假设。"
        local purpose2 "带宽、核函数和局部多项式阶数会影响结果；建议结合右侧图形或结果诊断。"
    }
    else if strpos(" bitesti tabi ", " `cmd' ") {
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
    else if strpos(" bayes bayesmh bayespredict bayesstats bayesgraph ", " `cmd' ") {
        local title "`cmd' — 贝叶斯分析"
        local purpose1 "用于贝叶斯模型估计、MCMC、后验预测、诊断或结果图形。"
        local purpose2 "先验、采样设置和后验结果对象是核心；运行前应明确当前是估计、诊断还是后估计任务。"
    }
    else if "`cmd'" == "bmaregress" {
        local title "bmaregress — 贝叶斯模型平均线性回归"
        local purpose1 "用于在线性回归候选模型之间进行贝叶斯模型平均并反映模型不确定性。"
        local purpose2 "候选变量、always/group、模型先验和 g-prior 会影响结果，运行前应明确模型空间。"
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
    else if strpos(" roctab rocfit roccomp rocgold rocreg ", " `cmd' ") {
        local title "`cmd' — ROC 分析"
        local purpose1 "用于评估、比较或回归建模二元结局预测的 ROC 曲线与区分能力。"
        local purpose2 "先明确真实二元结局和预测评分/模型；比较、协变量调整和图形设置按命令语法填写。"
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
