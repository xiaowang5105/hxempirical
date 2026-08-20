*! hxsemantics 1.4.31  16aug2026
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

    capture findfile hxsemantics_rules.do
    if _rc {
        display as error "hxsemantics_rules.do not found"
        exit 601
    }
    local hx_semantics_rules `"`r(fn)'"'
    include `"`hx_semantics_rules'"'

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
