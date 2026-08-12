*! hxthreads 1.2.0  12aug2026
*! Manual Stata/MP processor switch for the HX empirical workbench
program define hxthreads, rclass
    version 16.0
    syntax [anything(name=action)]

    local action = lower(trim(`"`action'"'))
    if `"`action'"' == "" local action "status"

    if !inlist(`"`action'"', "on", "off", "status") {
        display as error "请选择 on（开启）、off（单核）或 status（查看状态）。"
        exit 198
    }

    local licensed = c(processors_lic)

    if `"`action'"' == "off" {
        set processors 1
        capture window push set processors 1
        local history_rc = _rc
        char _dta[hxtoolbox_last_native_command] "set processors 1"
        capture hxregistry, recent(set)
        display as result "多线程已关闭：当前使用 1 个处理器。"
    }

    if `"`action'"' == "on" {
        set processors `licensed'
        capture window push set processors `licensed'
        local history_rc = _rc
        char _dta[hxtoolbox_last_native_command] "set processors `licensed'"
        capture hxregistry, recent(set)
        if `licensed' > 1 {
            display as result "多线程已开启：当前使用 `licensed' 个处理器（许可证上限）。"
        }
        else {
            display as text "当前许可证最多允许 1 个处理器，已保持单核运行。"
        }
    }

    if `"`action'"' == "status" {
        capture window push display c(processors)
        local history_rc = _rc
        char _dta[hxtoolbox_last_native_command] "display c(processors)"
        display as text "当前使用处理器数：" as result c(processors)
        display as text "许可证允许上限：" as result `licensed'
        if c(processors) > 1 display as result "状态：多线程已开启"
        else display as result "状态：单核运行"
    }

    if `history_rc' {
        char _dta[hxtoolbox_history_status] "写入失败"
    }
    else {
        char _dta[hxtoolbox_history_status] "已写入"
    }

    return scalar processors = c(processors)
    return scalar licensed = `licensed'
    return scalar history_rc = `history_rc'
end
