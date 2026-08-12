*! hxselect 2.2.0  09aug2026
*! 统一图形入口：显著组合、变量处理与数据合并
program define hxselect, rclass
    version 16.0

    local raw0 `"`0'"'

    if `"`0'"' == "" {
        // 为只点选的下拉框准备当前数据中的数值变量。
        capture quietly ds, has(type numeric)
        local hx_numeric_vars `"`r(varlist)'"'
        if `"`hx_numeric_vars'"' == "" {
            display as error "当前数据中没有可供回归选择的数值变量。"
            exit 111
        }
        char _dta[hxselect_numeric_vars] `"`hx_numeric_vars'"'
        db hxselect
        exit
    }

    capture window push hxselect `raw0'

    // 组合搜索由内部引擎完成；用户始终通过 hxselect 使用。
    hxmulti `0'
    return scalar models = r(models)
    return scalar tested = r(tested)
    return scalar passed = r(passed)
    return local bestsubset `"`r(bestsubset)'"'
    return local saving `"`r(saving)'"'
end
