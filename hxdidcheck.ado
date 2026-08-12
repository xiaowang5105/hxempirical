*! hxdidcheck 1.0.0  11aug2026
*! Validate a 0/1 DID variable on the actual requested estimation sample.
program define hxdidcheck, rclass
    version 17.0
    syntax varname [if] [in], ROLE(string) [REQUIRED(varlist)]

    char _dta[hxtoolbox_didcheck_message] ""
    capture confirm numeric variable `varlist'
    if _rc {
        char _dta[hxtoolbox_didcheck_message] `"`role' 当前是字符串变量；DID 的该角色需要数值型 0/1 变量。"'
        exit 109
    }

    marksample touse, novarlist
    if `"`required'"' != "" quietly markout `touse' `required'

    quietly count if `touse' & !missing(`varlist')
    if r(N) == 0 {
        char _dta[hxtoolbox_didcheck_message] `"`role' 在当前回归样本中没有可用观测。请检查 if 条件和缺失值。"'
        exit 2000
    }

    quietly count if `touse' & !missing(`varlist') & !inlist(`varlist', 0, 1)
    if r(N) > 0 {
        quietly levelsof `varlist' if `touse' & !missing(`varlist') & !inlist(`varlist', 0, 1), local(other)
        char _dta[hxtoolbox_didcheck_message] `"`role' 需要使用 0/1 编码。当前回归样本检测到其他取值：`other'。工具不会自动重编码。"'
        exit 459
    }

    quietly count if `touse' & `varlist' == 0
    local n0 = r(N)
    quietly count if `touse' & `varlist' == 1
    local n1 = r(N)
    if `n0' == 0 | `n1' == 0 {
        char _dta[hxtoolbox_didcheck_message] `"`role' 在当前回归样本中没有同时出现 0 和 1（0：`n0'，1：`n1'）。请检查 if 条件、控制变量缺失和样本筛选。"'
        exit 459
    }

    char _dta[hxtoolbox_didcheck_message] `"通过：`role' 在当前回归样本中包含 0 和 1。"'
    return scalar N0 = `n0'
    return scalar N1 = `n1'
    return local role `"`role'"'
end
