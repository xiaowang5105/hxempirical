*! hxregistry 2.8.0  12aug2026
*! Command-first catalog plus HX workflow navigation, search, favorites, and recent-command state
program define hxregistry, rclass
    version 16.0
    syntax [, SEARCH(string asis) CATEGORY(string) FAVORITE(string) ///
        UNFAVORITE(string) RECENT(string) METHOD(string asis) RESET]

    local data_cmds "hxconvert generate replace keep drop merge append reshape collapse xtset tsset encode decode destring tostring winsor2 duplicates misstable"
    local stats_cmds "summarize tabstat pwcorr correlate ttest tabulate"
    local reg_cmds "regress areg reghdfe rreg cnsreg vwls eivreg qreg newey prais xtreg xtlogit xtprobit logit probit poisson nbreg ppmlhdfe ivregress ivreghdfe"
    local post_cmds "test lincom predict margins"
    local graph_cmds "histogram kdensity scatter lfit graph_box twoway marginsplot coefplot"
    local did_cmds "did_builder did_trends event_plot"
    local oneclick_cmds "oneclick oneclick_robustness"
    local workflow_cmds "hxconvert did_builder did_trends oneclick oneclick_robustness"
    local all_cmds "`data_cmds' `stats_cmds' `reg_cmds' `post_cmds' `graph_cmds' `did_cmds' `oneclick_cmds'"

    local data_methods "导入与转换 数据检查 变量处理 样本处理 合并与追加 数据结构"
    local stats_methods "描述统计 相关分析 均值检验 频数列联"
    local reg_methods "普通线性回归 固定效应线性回归 稳健与特殊线性回归 分位数回归 时间序列线性回归 面板模型 二元结果 计数模型 工具变量"
    local post_methods "系数检验 预测边际"
    local graph_methods "数据分布 变量关系 分组趋势 回归结果"
    local did_methods "DID分步构建 平行趋势与动态图"
    local oneclick_methods "控制变量组合筛选 控制变量组合稳健性"

    local defaults "regress xtreg reghdfe merge summarize margins"

    if "`reset'" != "" {
        global HXEMPIRICAL_FAVORITES ""
        global HXEMPIRICAL_RECENT ""
    }

    local favorites `"$HXEMPIRICAL_FAVORITES"'
    local favorites = trim(itrim(`"`favorites'"'))
    if `"`favorites'"' == "" local favorites "`defaults'"

    local favorite = lower(trim(`"`favorite'"'))
    local unfavorite = lower(trim(`"`unfavorite'"'))
    if `"`favorite'"' != "" {
        if !regexm("`favorite'", "^[A-Za-z_][A-Za-z0-9_]*$") {
            display as error "收藏的命令名无效。"
            exit 198
        }
        if !strpos(" `favorites' ", " `favorite' ") local favorites "`favorites' `favorite'"
    }
    if `"`unfavorite'"' != "" {
        local kept ""
        foreach cmd of local favorites {
            if "`cmd'" != "`unfavorite'" local kept "`kept' `cmd'"
        }
        local favorites = trim(itrim("`kept'"))
    }
    if `"`favorite'`unfavorite'"' != "" {
        global HXEMPIRICAL_FAVORITES `"`favorites'"'
    }

    local recentcmds `"$HXEMPIRICAL_RECENT"'
    local recentcmds = trim(itrim(`"`recentcmds'"'))
    local recent = lower(trim(`"`recent'"'))
    if `"`recent'"' != "" {
        gettoken recent_name unused : recent
        local updated "`recent_name'"
        local n 1
        foreach cmd of local recentcmds {
            if "`cmd'" != "`recent_name'" & `n' < 12 {
                local updated "`updated' `cmd'"
                local ++n
            }
        }
        local recentcmds = trim(itrim("`updated'"))
        global HXEMPIRICAL_RECENT `"`recentcmds'"'
    }

    local search = lower(trim(`"`search'"'))
    if substr(`"`search'"', 1, 1) == char(34) & substr(`"`search'"', -1, 1) == char(34) {
        local search = substr(`"`search'"', 2, strlen(`"`search'"') - 2)
    }
    local matches ""
    if `"`search'"' == "" local matches "`all_cmds'"
    else {
        local key_generate "generate gen 生成 创建 新变量 计算"
        local key_hxconvert "转换为dta 转换 dta excel csv txt 导入 文件"
        local key_replace "replace 修改 替换 更新变量"
        local key_keep "keep 保留 筛选 样本 变量"
        local key_drop "drop 删除 剔除 样本 缺失"
        local key_merge "merge 合并 主表 副表 匹配 关联"
        local key_append "append 追加 拼接 纵向合并"
        local key_reshape "reshape 宽表 长表 转换"
        local key_collapse "collapse 汇总 聚合 分组 均值"
        local key_xtset "xtset panel data 面板 设置 个体 时间"
        local key_tsset "tsset time series 时间序列 时间变量 声明"
        local key_encode "encode 字符串 数值 编码 标签"
        local key_decode "decode 数值 字符串 解码 标签"
        local key_destring "destring 字符串 转 数值"
        local key_tostring "tostring 数值 转 字符串"
        local key_winsor2 "winsor2 缩尾 极端值"
        local key_duplicates "duplicates 重复值 重复记录"
        local key_misstable "misstable 缺失值"
        local key_summarize "summarize sum 描述统计 均值 标准差"
        local key_tabstat "tabstat 分组统计 描述统计"
        local key_pwcorr "pwcorr 相关系数 显著性"
        local key_correlate "correlate corr 相关系数"
        local key_ttest "ttest 均值检验 t检验"
        local key_tabulate "tabulate tab 频数 列联表"
        local key_regress "regress ols linear regression 线性回归 最小二乘 基准回归 普通回归 稳健标准误 聚类"
        local key_areg "areg absorb fixed effect 吸收固定效应 线性模型"
        local key_qreg "qreg quantile median 分位数回归 中位数"
        local key_rreg "rreg robust regression 稳健回归 异常值 outlier"
        local key_cnsreg "cnsreg constrained regression 约束回归 constraints 参数约束"
        local key_vwls "vwls variance weighted least squares 方差加权 最小二乘"
        local key_eivreg "eivreg errors in variables measurement error 测量误差 可靠度"
        local key_newey "newey newey west hac 标准误 自相关 时间序列"
        local key_prais "prais prais winsten cochrane orcutt ar1 自相关 时间序列"
        local key_xtreg "xtreg panel regression fixed effects random effects 面板回归 固定效应 随机效应"
        local key_xtlogit "xtlogit panel binary 面板 二元 逻辑回归"
        local key_xtprobit "xtprobit panel binary 面板 二元 概率回归"
        local key_reghdfe "reghdfe high dimensional fixed effects absorb 高维固定效应 吸收 固定效应 企业固定效应 年份固定效应"
        local key_logit "logit 二元 逻辑回归"
        local key_probit "probit 二元 概率回归"
        local key_poisson "poisson count 泊松 计数模型"
        local key_nbreg "nbreg negative binomial 负二项 计数模型"
        local key_ivregress "ivregress iv 工具变量 2sls liml gmm 内生性"
        local key_ivreghdfe "ivreghdfe high dimensional fixed effects instrument 高维固定效应 工具变量 内生性"
        local key_did_builder "did difference in differences event study treat post event_time 平行趋势 事件研究 双重差分 政策冲击 动态效应"
        local key_ppmlhdfe "ppmlhdfe poisson pseudo maximum likelihood fixed effects 泊松 伪极大似然 高维固定效应"
        local key_test "test 系数检验 联合检验"
        local key_lincom "lincom 线性组合 系数"
        local key_predict "predict 预测值 残差"
        local key_margins "margins 边际效应 调节效应"
        local key_histogram "histogram 直方图 分布 频数 密度"
        local key_kdensity "kdensity 核密度 系数分布"
        local key_scatter "scatter 散点图 变量关系"
        local key_lfit "lfit 线性拟合 拟合线"
        local key_graph_box "graph box 箱线图 分组分布 异常值"
        local key_twoway "twoway 叠加图 自定义图形"
        local key_marginsplot "marginsplot 边际效应图 调节效应图"
        local key_coefplot "coefplot 系数图 回归结果图"
        local key_did_trends "did trends 平行趋势 处理组 对照组 趋势图"
        local key_event_plot "event plot 事件研究 动态效应 平行趋势"
        local key_oneclick "oneclick 控制变量 组合 筛选 显著性"
        local key_oneclick_robustness "oneclick robustness 稳健性 specification curve 系数分布 控制变量组合 模型稳健性"
        foreach cmd of local all_cmds {
            local hay = lower(`"`cmd' `key_`cmd''"')
            if strpos(`"`hay'"', `"`search'"') local matches "`matches' `cmd'"
        }
        local matches = trim(itrim("`matches'"))
    }

    char _dta[hxtoolbox_commands] `"`all_cmds'"'
    char _dta[hxtoolbox_data_cmds] `"`data_cmds'"'
    char _dta[hxtoolbox_stats_cmds] `"`stats_cmds'"'
    char _dta[hxtoolbox_reg_cmds] `"`reg_cmds'"'
    char _dta[hxtoolbox_post_cmds] `"`post_cmds'"'
    char _dta[hxtoolbox_graph_cmds] `"`graph_cmds'"'
    char _dta[hxtoolbox_did_cmds] `"`did_cmds'"'
    char _dta[hxtoolbox_oneclick_cmds] `"`oneclick_cmds'"'
    char _dta[hxtoolbox_workflow_cmds] `"`workflow_cmds'"'
    char _dta[hxtoolbox_data_methods] `"`data_methods'"'
    char _dta[hxtoolbox_stats_methods] `"`stats_methods'"'
    char _dta[hxtoolbox_reg_methods] `"`reg_methods'"'
    char _dta[hxtoolbox_post_methods] `"`post_methods'"'
    char _dta[hxtoolbox_graph_methods] `"`graph_methods'"'
    char _dta[hxtoolbox_did_methods] `"`did_methods'"'
    char _dta[hxtoolbox_oneclick_methods] `"`oneclick_methods'"'
    char _dta[hxtoolbox_favorites] `"`favorites'"'
    char _dta[hxtoolbox_recent] `"`recentcmds'"'
    char _dta[hxtoolbox_search] `"`matches'"'
    local category = lower(trim(`"`category'"'))
    local view `"`matches'"'
    local method_view ""
    local browser_mode "commands"
    if `"`category'"' == "data" {
        local method_view `"`data_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "stats" {
        local method_view `"`stats_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "reg" {
        local method_view `"`reg_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "post" {
        local method_view `"`post_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "graph" {
        local method_view `"`graph_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "did" {
        local method_view `"`did_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "oneclick" {
        local method_view `"`oneclick_methods'"'
        local view ""
        local browser_mode "methods"
    }
    if `"`category'"' == "favorites" local view `"`favorites'"'
    if `"`category'"' == "recent" local view `"`recentcmds'"'

    local method = trim(`"`method'"')
    if substr(`"`method'"', 1, 1) == char(34) & substr(`"`method'"', -1, 1) == char(34) {
        local method = substr(`"`method'"', 2, strlen(`"`method'"') - 2)
    }
    local method_title `"`method'"'
    local method_desc "选择下面的具体 Stata 命令，再进入该命令自己的设置页面。"
    if inlist(`"`method'"', "导入与转换", "import_convert") local view "hxconvert"
    else if inlist(`"`method'"', "数据检查", "data_check") local view "misstable duplicates"
    else if inlist(`"`method'"', "变量处理", "variable_processing") local view "generate replace encode decode destring tostring winsor2"
    else if inlist(`"`method'"', "样本处理", "sample_processing") local view "keep drop"
    else if inlist(`"`method'"', "合并与追加", "merge_append") local view "merge append"
    else if inlist(`"`method'"', "数据结构", "data_structure") local view "reshape collapse xtset tsset"
    else if inlist(`"`method'"', "描述统计", "descriptive") local view "summarize tabstat"
    else if inlist(`"`method'"', "相关分析", "correlation") local view "correlate pwcorr"
    else if inlist(`"`method'"', "均值检验", "mean_test") local view "ttest"
    else if inlist(`"`method'"', "频数列联", "frequency") local view "tabulate"
    else if inlist(`"`method'"', "普通线性回归", "linear_ols") local view "regress"
    else if inlist(`"`method'"', "固定效应线性回归", "linear_fe") local view "reghdfe areg"
    else if inlist(`"`method'"', "稳健与特殊线性回归", "linear_special") local view "rreg cnsreg vwls eivreg"
    else if inlist(`"`method'"', "分位数回归", "linear_quantile") local view "qreg"
    else if inlist(`"`method'"', "时间序列线性回归", "linear_ts") local view "newey prais"
    else if inlist(`"`method'"', "线性模型", "linear") local view "regress reghdfe areg qreg rreg cnsreg vwls eivreg newey prais"
    else if inlist(`"`method'"', "面板模型", "panel") local view "xtreg xtlogit xtprobit"
    else if inlist(`"`method'"', "二元结果", "binary") local view "logit probit"
    else if inlist(`"`method'"', "计数模型", "count") local view "poisson nbreg ppmlhdfe"
    else if inlist(`"`method'"', "工具变量", "iv") local view "ivregress ivreghdfe"
    else if inlist(`"`method'"', "DID分步构建", "did_build", "DID模型构建", "did_model") local view "did_builder"
    else if inlist(`"`method'"', "系数检验", "coefficient") local view "test lincom"
    else if inlist(`"`method'"', "预测边际", "prediction") local view "predict margins"
    else if inlist(`"`method'"', "数据分布", "graph_distribution") local view "histogram kdensity graph_box"
    else if inlist(`"`method'"', "变量关系", "graph_relation") local view "scatter lfit twoway"
    else if inlist(`"`method'"', "分组趋势", "graph_trend") local view "did_trends"
    else if inlist(`"`method'"', "回归结果", "graph_estimation") local view "coefplot marginsplot"
    else if inlist(`"`method'"', "平行趋势与动态图", "did_graph", "DID与事件研究", "graph_did") local view "did_trends event_plot"
    else if inlist(`"`method'"', "控制变量组合筛选", "oneclick_screen") local view "oneclick"
    else if inlist(`"`method'"', "控制变量组合稳健性", "oneclick_robustness") local view "oneclick_robustness"
    if `"`method'"' != "" local browser_mode "commands"

    char _dta[hxtoolbox_command_view] `"`view'"'
    char _dta[hxtoolbox_method_view] `"`method_view'"'
    char _dta[hxtoolbox_method_title] `"`method_title'"'
    char _dta[hxtoolbox_method_desc] `"`method_desc'"'
    char _dta[hxtoolbox_browser_mode] `"`browser_mode'"'

    return local commands `"`all_cmds'"'
    return local favorites `"`favorites'"'
    return local recent `"`recentcmds'"'
    return local matches `"`matches'"'
    return local methods `"`method_view'"'
    return local view `"`view'"'
end
