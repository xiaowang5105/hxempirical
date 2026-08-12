*! hxdidencode 1.1.0  11aug2026
*! Create a nonnegative event-time code for Stata factor-variable event-study regressions.
program define hxdidencode, rclass
    version 17.0
    syntax varname(numeric) [if] [in], Generate(name) [BASE(integer -1)]

    marksample touse, novarlist
    confirm new variable `generate'

    quietly count if `touse' & !missing(`varlist')
    if r(N) == 0 {
        display as error "`varlist' 在当前样本中没有可用的非缺失值。"
        exit 2000
    }

    capture assert `varlist' == floor(`varlist') if `touse' & !missing(`varlist')
    if _rc {
        display as error "事件时间变量必须是整数期（例如 -3、-2、-1、0、1、2）。"
        exit 459
    }

    quietly count if `touse' & `varlist' == `base'
    if r(N) == 0 {
        quietly levelsof `varlist' if `touse' & !missing(`varlist'), local(levels)
        display as error "当前样本中不存在所选基准期 `base'。"
        display as text  "当前可用事件期：`levels'"
        display as text  "请选择一个实际存在的基准期后再生成 event_code。"
        exit 459
    }

    quietly summarize `varlist' if `touse', meanonly
    local min = r(min)
    local max = r(max)
    local shift = cond(`min' < 0, -floor(`min'), 0)
    local basecode = `base' + `shift'

    if `basecode' < 0 {
        display as error "基准期 `base' 在当前编码下仍为负值。请确认事件时间范围与基准期。"
        exit 459
    }
    if (`max' + `shift') > 32740 {
        display as error "事件时间编码超过 Stata factor-variable 允许范围。"
        exit 459
    }

    generate long `generate' = `varlist' + `shift' if `touse' & !missing(`varlist')
    label variable `generate' "事件研究编码：`varlist' + `shift'（原基准期 `base'）"
    fvset base `basecode' `generate'

    char _dta[hxtoolbox_event_source] "`varlist'"
    char _dta[hxtoolbox_event_code] "`generate'"
    char _dta[hxtoolbox_event_shift] "`shift'"
    char _dta[hxtoolbox_event_base_relative] "`base'"
    char _dta[hxtoolbox_event_base_code] "`basecode'"

    display as result "已生成事件研究编码 `generate'。"
    display as text "原事件时间：`varlist'；平移量：`shift'；原基准期：`base'；编码基准值：`basecode'。"
    display as text "后续事件研究回归可直接使用 i.treat##i.`generate'；工具箱会自动换算基准期。"

    return local source "`varlist'"
    return local generate "`generate'"
    return scalar shift = `shift'
    return scalar base_relative = `base'
    return scalar base_code = `basecode'
    return scalar min_relative = `min'
    return scalar max_relative = `max'
end
