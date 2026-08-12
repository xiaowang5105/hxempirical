*! hxrefresh 3.0.0  09aug2026
*! Refresh variable lists and toolbox status text stored in dataset characteristics
program define hxrefresh
    version 16.0

    capture quietly ds
    if _rc local allvars ""
    else local allvars `"`r(varlist)'"'

    capture quietly ds, has(type numeric)
    if _rc local numericvars ""
    else local numericvars `"`r(varlist)'"'

    local k : word count `allvars'
    capture quietly count
    if _rc local n 0
    else local n = r(N)

    local filename `"`c(filename)'"'
    if trim(`"`filename'"') == "" local filename "未保存/内存数据"

    char _dta[hxselect_numeric_vars] `"`numericvars'"'
    char _dta[hxtoolbox_all_vars] `"`allvars'"'
    char _dta[hxtoolbox_status_data] `"当前数据：`filename'"'
    char _dta[hxtoolbox_status_nk] `"样本数：`n'    变量数：`k'"'
    char _dta[hxtoolbox_status_cpu] `"处理器：`c(processors)' / `c(processors_lic)'"'
    char _dta[hxtoolbox_perf_now] `"当前使用：`c(processors)' 个处理器"'
    char _dta[hxtoolbox_perf_max] `"许可证上限：`c(processors_lic)' 个处理器"'

    capture quietly xtset
    local panelvar `"`r(panelvar)'"'
    local timevar `"`r(timevar)'"'
    if _rc | `"`panelvar'"' == "" char _dta[hxtoolbox_panel_status] "面板状态：尚未 xtset"
    else {
        local pstatus `"面板状态：xtset `panelvar'"'
        if `"`timevar'"' != "" local pstatus `"`pstatus' `timevar'"'
        char _dta[hxtoolbox_panel_status] `"`pstatus'"'
    }

    capture quietly hxregistry
end
