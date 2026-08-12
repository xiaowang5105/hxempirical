*! hxpanel 1.0.0  09aug2026
*! Panel-data precheck and guarded xtset helper
program define hxpanel, rclass
    version 16.0
    syntax [anything(name=action)] [, PANEL(name) TIME(name)]
    local action = lower(trim(`"`action'"'))
    if `"`action'"' == "" local action "status"

    if `"`action'"' == "set" {
        if `"`panel'"' == "" {
            display as error "请选择面板个体变量。"
            exit 198
        }
        confirm variable `panel'
        local cmd "xtset `panel'"
        if `"`time'"' != "" {
            confirm variable `time'
            local cmd "xtset `panel' `time'"
        }
        capture window push `cmd'
        capture noisily `cmd'
        local rc = _rc
        capture hxregistry, recent(xtset)
        capture quietly hxrefresh
        if `rc' exit `rc'
    }

    capture quietly xtset
    local panelvar `"`r(panelvar)'"'
    local timevar `"`r(timevar)'"'
    if _rc | `"`panelvar'"' == "" {
        char _dta[hxtoolbox_panel_status] "面板状态：尚未 xtset"
        display as text "当前数据尚未设置面板结构。"
        return scalar isset = 0
        exit
    }
    local status `"面板状态：xtset `panelvar'"'
    if `"`timevar'"' != "" local status `"`status' `timevar'"'
    char _dta[hxtoolbox_panel_status] `"`status'"'
    display as text `"`status'"'
    return scalar isset = 1
    return local panelvar `"`panelvar'"'
    return local timevar `"`timevar'"'
end
