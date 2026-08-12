*! hxtestdata 2.2.0  10aug2026
*! Test-data buttons used by the unified toolbox
program define hxtestdata
    version 16.0
    syntax anything(name=action)
    local action = lower(trim(`"`action'"'))

    if inlist(`"`action'"', "auto", "nlsw88", "nlswork", "grunfeld", "union") {
        local loader = cond(inlist(`"`action'"', "auto", "nlsw88"), "sysuse", "webuse")
        local cmd "`loader' `action', clear"
        capture window push `cmd'
        local history_rc = _rc
        capture noisily `cmd'
        local rc = _rc
        capture hxhistory, add(`"`cmd'"')

        /* webuse 需要联网；断网时载入随工具箱安装的同结构练习数据。 */
        if `rc' & "`loader'" == "webuse" {
            capture findfile hx_`action'.dta
            if !_rc {
                local fallback `"`r(fn)'"'
                local cmd `"use "`fallback'", clear"'
                capture window push `cmd'
                local history_rc = _rc
                capture noisily `cmd'
                local rc = _rc
                capture hxhistory, add(`"`cmd'"')
                if !`rc' {
                    display as text "Stata 官网数据当前不可达；已载入工具箱内置的 `action' 练习数据。"
                }
            }
        }
        char _dta[hxtoolbox_last_native_command] `"`cmd'"'
        if `history_rc' {
            char _dta[hxtoolbox_history_status] "写入失败"
        }
        else {
            char _dta[hxtoolbox_history_status] "已写入"
        }
        capture quietly hxrefresh
        if `rc' exit `rc'
        exit
    }

    if `"`action'"' == "dir" {
        local cmd "sysuse dir"
        capture window push `cmd'
        local history_rc = _rc
        capture noisily `cmd'
        local rc = _rc
        capture hxhistory, add(`"`cmd'"')
        char _dta[hxtoolbox_last_native_command] `"`cmd'"'
        if `history_rc' {
            char _dta[hxtoolbox_history_status] "写入失败"
        }
        else {
            char _dta[hxtoolbox_history_status] "已写入"
        }
        if `rc' exit `rc'
        exit
    }

    if !inlist(`"`action'"', "merge", "append") {
        display as error "未知测试数据操作：`action'"
        exit 198
    }

    local testdir `"`c(tmpdir)'/hxtoolbox_test"'
    capture mkdir `"`testdir'"'
    preserve
    if `"`action'"' == "merge" {
        local f1 `"`testdir'/hx_merge_master.dta"'
        local f2 `"`testdir'/hx_merge_using.dta"'
        local commands `"clear|set obs 6|generate id = _n|generate year = 2020 + mod(_n,2)|generate y = 10 + _n|save "`f1'", replace|clear|set obs 6|generate id = _n|generate year = 2020 + mod(_n,2)|generate x = 2 * _n|save "`f2'", replace"'
    }
    else {
        local f1 `"`testdir'/hx_append_a.dta"'
        local f2 `"`testdir'/hx_append_b.dta"'
        local commands `"clear|set obs 4|generate id = _n|generate group = 1|generate value = 10 + _n|save "`f1'", replace|clear|set obs 4|generate id = _n + 4|generate group = 2|generate value = 20 + _n|save "`f2'", replace"'
    }

    local rest `"`commands'"'
    while `"`rest'"' != "" {
        gettoken cmd rest : rest, parse("|")
        if `"`cmd'"' == "|" continue
        local cmd = trim(`"`cmd'"')
        if `"`cmd'"' == "" continue
        capture window push `cmd'
        local history_rc = _rc
        capture noisily `cmd'
        if _rc {
            local rc = _rc
            restore
            exit `rc'
        }
        capture hxhistory, add(`"`cmd'"')
    }
    restore
    char _dta[hxtoolbox_last_native_command] `"`cmd'"'
    if `history_rc' {
        char _dta[hxtoolbox_history_status] "写入失败"
    }
    else {
        char _dta[hxtoolbox_history_status] "已写入"
    }
    char _dta[hxtoolbox_testfile1] `"`f1'"'
    char _dta[hxtoolbox_testfile2] `"`f2'"'
    char _dta[hxtoolbox_testdir] `"`testdir'"'
    display as result "测试文件已创建："
    display as text `"  `f1'"'
    display as text `"  `f2'"'
end
