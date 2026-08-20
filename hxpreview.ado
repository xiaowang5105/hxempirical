*! hxpreview 1.3.4  16aug2026
*! Build the native Stata command shown by the dynamic dialog.
program define hxpreview, rclass
    version 16.0
    syntax [, DEPVAR(string) NEWVAR(string) MODEL(string) ///
        EXPRESSION(string) USINGFILE(string) ///
        PANEL(string) TIME(string) VCE(string) CLUSTER(string) ///
        IFCOND(string) INCOND(string) ///
        SPECIAL(string) OPTIONS(string) ///
        WEIGHT(string) WEIGHTVAR(string) ///
        CONDVAR(string) CONDOP(string) CONDVALUE(string) CONDITION]

    local command : char _dta[hxtoolbox_resolve_name]
    local template : char _dta[hxtoolbox_schema_template]
    local vars : char _dta[hxtoolbox_pick_vars]
    local absorb : char _dta[hxtoolbox_pick_absorb]
    local endog : char _dta[hxtoolbox_pick_endog]
    local inst : char _dta[hxtoolbox_pick_inst]
    foreach flag in has_depvar has_varlist has_if has_in has_weight ///
        has_using has_newvar has_expression has_absorb has_vce ///
        has_cluster has_iv needs_panel model_before {
        local `flag' : char _dta[hxtoolbox_schema_`flag']
    }
    foreach flag in is_xtset keepdrop_mode winsor_mode predict_mode {
        local `flag' : char _dta[hxtoolbox_sem_`flag']
    }

    local command = trim(`"`command'"')
    if `"`command'"' == "" {
        char _dta[hxtoolbox_preview] ""
        return local command ""
        exit
    }

    local preview `"`command'"'
    if "`command'" == "lfit" local preview "twoway lfit"
    if "`command'" == "graph_bar" local preview "graph bar"
    if "`command'" == "graph_dot" local preview "graph dot"
    if "`command'" == "graph_pie" local preview "graph pie"
    if "`command'" == "graph_box" local preview "graph box"
    if "`command'" == "graph_matrix" local preview "graph matrix"
    if "`command'" == "twoway_contour" local preview "twoway contour"
    if "`command'" == "graph_combine" local preview "graph combine"
    if "`command'" == "cluster_dendrogram" local preview "cluster dendrogram"
    if "`command'" == "sts_graph" local preview "sts graph"
    if "`command'" == "misstable" local preview "misstable summarize"
    if "`command'" == "duplicates" local preview "duplicates report"
    local opt ""

    if `"`template'"' == "didregress" {
        local did_outcome `"`depvar'"'
        if `"`vars'"' != "" local did_outcome `"`did_outcome' `vars'"'
        local preview `"`command'"'
        if `"`did_outcome'"' != "" local preview `"`preview' (`did_outcome')"'
        if `"`panel'"' != "" local preview `"`preview' (`panel')"'
        if `"`absorb'"' != "" local opt `"`opt' group(`absorb')"'
        if `"`time'"' != "" local opt `"`opt' time(`time')"'
        local has_depvar 0
        local has_varlist 0
        local has_absorb 0
        local needs_panel 0
    }

    if "`is_xtset'" == "1" {
        if `"`panel'"' != "" local preview `"`preview' `panel'"'
        if `"`time'"' != "" local preview `"`preview' `time'"'
    }

    if "`model_before'" == "1" & `"`model'"' != "" {
        local model_native `"`model'"'
        if `"`model'"' == "两阶段最小二乘（2SLS）" local model_native "2sls"
        else if `"`model'"' == "有限信息极大似然（LIML）" local model_native "liml"
        else if `"`model'"' == "广义矩估计（GMM）" local model_native "gmm"
        else if `"`model'"' == "宽表转长表（long）" local model_native "long"
        else if `"`model'"' == "长表转宽表（wide）" local model_native "wide"
        local preview `"`preview' `model_native'"'
    }

    if `"`template'"' == "collapse" {
        local collapse_stat "mean"
        if `"`model'"' == "总和（sum）" local collapse_stat "sum"
        else if `"`model'"' == "中位数（median）" local collapse_stat "median"
        else if `"`model'"' == "样本数（count）" local collapse_stat "count"
        local preview `"collapse (`collapse_stat')"'
    }

    if "`has_newvar'" == "1" & `"`newvar'"' != "" & `"`template'"' != "conversion" {
        local preview `"`preview' `newvar'"'
        if `"`template'"' == "generate" local preview `"`preview' = `expression'"'
    }
    if "`has_depvar'" == "1" & `"`depvar'"' != "" {
        local preview `"`preview' `depvar'"'
    }
    if `"`template'"' == "replace" & `"`expression'"' != "" {
        local preview `"`preview' = `expression'"'
    }
    if inlist(`"`template'"', "expression_body", "command_body") & `"`expression'"' != "" {
        local body = trim(`"`expression'"')
        if `"`template'"' == "command_body" & inlist(substr(`"`body'"', 1, 1), ":", ",") {
            local preview `"`preview'`body'"'
        }
        else local preview `"`preview' `body'"'
    }
    if `"`template'"' == "reshape" & `"`expression'"' != "" {
        local preview `"`preview' `expression'"'
    }

    if `"`template'"' == "ttest" {
        if `"`vars'"' != "" local preview `"`preview' `vars'"'
        if inlist(`"`model'"', "单样本（=数值）", "配对比较") & `"`expression'"' != "" {
            local preview `"`preview' == `expression'"'
        }
        if `"`model'"' == "分组比较" & `"`expression'"' != "" {
            local opt `"`opt' by(`expression')"'
        }
    }
    else if "`keepdrop_mode'" == "1" {
        if `"`model'"' == "处理变量" & `"`vars'"' != "" {
            local preview `"`preview' `vars'"'
        }
    }
    else if "`has_varlist'" == "1" & `"`vars'"' != "" {
        local preview `"`preview' `vars'"'
    }
    else if `"`template'"' == "generic" & "`has_depvar'`has_varlist'`has_expression'" == "000" & `"`vars'"' != "" {
        local preview `"`preview' `vars'"'
    }

    if "`has_iv'" == "1" & `"`endog'"' != "" {
        local preview `"`preview' (`endog' = `inst')"'
    }
    if `"`special'"' != "" local preview `"`preview' `special'"'
    if "`has_using'" == "1" & `"`usingfile'"' != "" {
        local preview `"`preview' using `usingfile'"'
    }
    if `"`template'"' == "replace" & "`condition'" != "" {
        if `"`condvar'`condop'`condvalue'"' != "" {
            local preview `"`preview' if `condvar' `condop' `condvalue'"'
        }
    }
    else if "`has_if'" == "1" {
        if "`keepdrop_mode'" == "1" {
            if `"`model'"' == "处理样本" & `"`ifcond'"' != "" {
                local preview `"`preview' if `ifcond'"'
            }
        }
        else if `"`ifcond'"' != "" local preview `"`preview' if `ifcond'"'
    }
    if "`has_in'" == "1" & `"`incond'"' != "" {
        local preview `"`preview' in `incond'"'
    }
    if "`has_weight'" == "1" & `"`weight'"' != "" & `"`weightvar'"' != "" {
        local preview `"`preview' [`weight'=`weightvar']"'
    }

    if `"`template'"' == "margins" & `"`expression'"' != "" {
        local opt `"`opt' `expression'"'
    }
    if `"`template'"' == "qreg" & `"`expression'"' != "" {
        local opt `"`opt' quantile(`expression')"'
    }
    if `"`template'"' == "cnsreg" & `"`expression'"' != "" {
        local opt `"`opt' constraints(`expression')"'
    }
    if `"`template'"' == "vwls" & `"`expression'"' != "" {
        local opt `"`opt' sd(`expression')"'
    }
    if `"`template'"' == "eivreg" & `"`expression'"' != "" {
        local opt `"`opt' reliab(`expression')"'
    }
    if `"`template'"' == "newey" & `"`expression'"' != "" {
        local opt `"`opt' lag(`expression')"'
    }
    if `"`model'"' != "" & "`model_before'" == "0" & ///
        "`keepdrop_mode'`winsor_mode'`predict_mode'" == "000" & ///
        !inlist(`"`template'"', "ttest", "collapse", "conversion") {
        local model_native `"`model'"'
        if `"`model'"' == "固定效应（FE）" local model_native "fe"
        else if `"`model'"' == "随机效应（RE）" local model_native "re"
        else if `"`model'"' == "组间效应（Between）" local model_native "be"
        else if `"`model'"' == "总体平均（PA）" local model_native "pa"
        local opt `"`opt' `model_native'"'
    }
    if "`winsor_mode'" == "1" {
        if `"`expression'"' != "" local opt `"`opt' cuts(`expression')"'
        if `"`model'"' == "覆盖原变量" local opt `"`opt' replace"'
        else local opt `"`opt' suffix(_w)"'
    }
    if "`predict_mode'" == "1" {
        if `"`model'"' == "残差" local opt `"`opt' residuals"'
        else if `"`model'"' == "标准化残差" local opt `"`opt' rstandard"'
    }
    if `"`template'"' == "reshape" {
        if `"`panel'"' != "" local opt `"`opt' i(`panel')"'
        if `"`time'"' != "" local opt `"`opt' j(`time')"'
    }
    if `"`template'"' == "collapse" & `"`absorb'"' != "" {
        local opt `"`opt' by(`absorb')"'
    }
    if `"`template'"' == "conversion" {
        if inlist("`command'", "encode", "decode") {
            if `"`newvar'"' != "" local opt `"`opt' generate(`newvar')"'
        }
        else if `"`model'"' == "覆盖原变量" {
            local opt `"`opt' replace"'
        }
        else if `"`newvar'"' != "" {
            local opt `"`opt' generate(`newvar')"'
        }
    }
    if "`has_absorb'" == "1" & `"`absorb'"' != "" & `"`template'"' != "collapse" {
        local opt `"`opt' absorb(`absorb')"'
    }
    if "`has_vce'" == "1" {
        if `"`vce'"' == "robust" local opt `"`opt' vce(robust)"'
        else if `"`vce'"' == "cluster" & `"`cluster'"' != "" {
            if "`command'" == "ivreghdfe" local opt `"`opt' cluster(`cluster')"'
            else local opt `"`opt' vce(cluster `cluster')"'
        }
    }
    if `"`options'"' != "" local opt `"`opt' `options'"'

    local preview = trim(itrim(`"`preview'"'))
    local opt = trim(itrim(`"`opt'"'))
    if `"`opt'"' != "" local preview `"`preview', `opt'"'
    char _dta[hxtoolbox_preview] `"`preview'"'
    return local command `"`preview'"'
end
