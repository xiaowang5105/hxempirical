*! hxprecheck 1.1.0  14aug2026
*! Beginner-facing preflight checks for commands with structural prerequisites.
program define hxprecheck, rclass
    version 16.0
    syntax , COMMAND(name) [TYPE(string) KEYS(string asis) USINGFILE(string asis)]

    local command = lower("`command'")
    local type = lower(trim(`"`type'"'))
    local keys = trim(`"`keys'"')
    local usingfile = trim(`"`usingfile'"')
    foreach item in type keys usingfile {
        if substr(`"``item''"', 1, 1) == char(34) & ///
            substr(`"``item''"', -1, 1) == char(34) {
            local `item' = substr(`"``item''"', 2, strlen(`"``item''"') - 2)
        }
    }

    if "`command'" == "merge" {
        if !inlist("`type'", "1:1", "m:1", "1:m") {
            display as error "请选择 1:1、m:1 或 1:m 合并关系。"
            exit 198
        }
        if `"`keys'"' == "" {
            display as error "请选择主表和副表共有的关联变量。"
            exit 198
        }
        if `"`usingfile'"' == "" {
            display as error "请选择副表文件。"
            exit 198
        }
        capture quietly confirm file `"`usingfile'"'
        if _rc {
            display as error "无法读取所选副表：`usingfile'"
            display as text "请重新选择文件，并确认路径和读取权限。"
            exit 601
        }
        capture quietly confirm variable `keys'
        if _rc {
            display as error "当前主表中没有完整的关联变量：`keys'"
            exit 111
        }

        local master_unique 1
        if inlist("`type'", "1:1", "1:m") {
            capture isid `keys'
            if _rc local master_unique 0
        }

        local using_unique 1
        preserve
        capture quietly use `"`usingfile'"', clear
        local using_rc = _rc
        if !`using_rc' {
            capture quietly confirm variable `keys'
            local using_rc = _rc
        }
        if !`using_rc' & inlist("`type'", "1:1", "m:1") {
            capture quietly isid `keys'
            if _rc local using_unique 0
        }
        restore
        if `using_rc' {
            display as error "副表中没有完整的关联变量，或该文件无法作为 Stata 数据读取：`keys'"
            exit `using_rc'
        }

        if !`master_unique' {
            char _dta[hxtoolbox_precheck] "检查未通过：当前主表的关联变量不唯一。"
            display as error "当前主表中 `keys' 不能唯一识别每行，不能使用 `type'。"
            display as text "可先运行：duplicates report `keys'"
            exit 459
        }
        if !`using_unique' {
            char _dta[hxtoolbox_precheck] "检查未通过：副表的关联变量不唯一。"
            display as error "副表中 `keys' 不能唯一识别每行，不能使用 `type'。"
            display as text "请打开副表检查重复记录，或重新选择合并关系。"
            exit 459
        }

        char _dta[hxtoolbox_precheck] "检查通过：主表和副表满足当前合并关系。"
        display as result "合并前检查通过：`type' `keys'"
        return scalar passed = 1
        exit
    }

    if inlist("`command'", "xtreg", "xtlogit", "xtprobit") {
        capture quietly xtset
        local xt_rc = _rc
        local panelvar ""
        local timevar ""
        if !`xt_rc' {
            local panelvar `"`r(panelvar)'"'
            local timevar `"`r(timevar)'"'
        }
        if `xt_rc' | `"`panelvar'"' == "" {
            char _dta[hxtoolbox_precheck] "当前数据尚未 xtset。"
            display as error "当前数据尚未设置面板结构。请先选择个体变量和时间变量并点击“设置面板数据”。"
            exit 459
        }
        char _dta[hxtoolbox_precheck] `"检查通过：xtset `panelvar' `timevar'"'
        display as result `"面板结构已设置：xtset `panelvar' `timevar'"'
        return scalar passed = 1
        exit
    }

    display as text "该命令当前没有额外的结构前置检查。"
    return scalar passed = 1
end
