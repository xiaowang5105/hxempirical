*! hxpick 1.0.0  09aug2026
*! Store click-only variable selections for the dynamic dialog.
program define hxpick, rclass
    version 16.0
    syntax , TARGET(name) ACTION(name) [VALUE(name)]

    local target = lower("`target'")
    local action = lower("`action'")
    if !inlist("`action'", "add", "clear") {
        display as error "hxpick action 只能是 add 或 clear。"
        exit 198
    }

    if "`target'" == "all" {
        if "`action'" != "clear" {
            display as error "target(all) 只支持 clear。"
            exit 198
        }
        foreach item in vars absorb endog inst {
            char _dta[hxtoolbox_pick_`item'] ""
        }
        exit
    }
    if !inlist("`target'", "vars", "absorb", "endog", "inst") {
        display as error "未知选择目标：`target'"
        exit 198
    }

    local slot hxtoolbox_pick_`target'
    if "`action'" == "clear" {
        char _dta[`slot'] ""
    }
    else {
        if "`value'" == "" {
            display as error "请先选择一个变量。"
            exit 198
        }
        local chosen : char _dta[`slot']
        local chosen "`chosen' `value'"
        local chosen = trim(itrim("`chosen'"))
        local chosen : list uniq chosen
        char _dta[`slot'] "`chosen'"
    }
    local chosen : char _dta[`slot']
    return local selected "`chosen'"
end
