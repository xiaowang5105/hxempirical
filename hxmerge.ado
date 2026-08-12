*! hxmerge 1.0.0 - guarded native merge behind hxselect
program define hxmerge, rclass
    version 16.0
    syntax , MASTER(string) USINGFILE(string) KEYS(string asis) ///
        [TYPE(string) KEEP(string asis) KEEPUSING(string asis) ///
         GENERATE(name) UPDATE REPLACE FORCE SAVING(string) SAVEREPLACE]

    local master = trim(`"`master'"')
    local usingfile = trim(`"`usingfile'"')
    local saving = trim(`"`saving'"')
    local keys = trim(`"`keys'"')
    local type = lower(trim(`"`type'"'))
    local keep = lower(trim(`"`keep'"'))
    if `"`type'"' == "" local type "1:1"
    if `"`keep'"' == "" local keep "master match using"
    if `"`generate'"' == "" local generate "_hxmerge"

    local keepusingopt
    if `"`keepusing'"' != "" local keepusingopt "keepusing(`keepusing')"
    local usecmd `"use `"`master'"', clear"'
    local mergecmd `"merge `type' `keys' using `"`usingfile'"', generate(`generate') keep(`keep') `update' `replace' `force' `keepusingopt'"'
    local mergecmd = trim(itrim(`"`mergecmd'"'))
    capture window push `usecmd'
    capture window push `mergecmd'
    if `"`saving'"' != "" {
        local savecmd `"save `"`saving'"'"'
        if `"`savereplace'"' != "" local savecmd `"`savecmd', replace"'
        capture window push `savecmd'
    }

    if !inlist(`"`type'"', "1:1", "m:1", "1:m") {
        display as error "合并方式只能是 1:1、m:1 或 1:m。"
        exit 198
    }
    if `"`master'"' == "" | `"`usingfile'"' == "" | `"`keys'"' == "" {
        display as error "请选择主表、副表，并填写关联变量。"
        exit 198
    }
    if `"`replace'"' != "" & `"`update'"' == "" {
        display as error "“用副表覆盖主表”需要同时勾选“用副表补充主表缺失值”。"
        exit 198
    }
    confirm file `"`master'"'
    confirm file `"`usingfile'"'

    preserve
    capture noisily {
        quietly use `"`master'"', clear
        confirm variable `keys'
        capture confirm new variable `generate'
        if _rc {
            display as error "主表中已经有变量 `generate'，请更换合并标记名。"
            error 110
        }
        if inlist(`"`type'"', "1:1", "1:m") {
            capture isid `keys'
            if _rc {
                display as error "主表的关联变量不能唯一识别每行，不能使用 `type'。"
                error 459
            }
        }

        quietly use `"`usingfile'"', clear
        confirm variable `keys'
        if inlist(`"`type'"', "1:1", "m:1") {
            capture isid `keys'
            if _rc {
                display as error "副表的关联变量不能唯一识别每行，不能使用 `type'。"
                error 459
            }
        }
        if `"`keepusing'"' != "" confirm variable `keepusing'

        quietly use `"`master'"', clear
        merge `type' `keys' using `"`usingfile'"', generate(`generate') ///
            keep(`keep') `update' `replace' `force' `keepusingopt'

        quietly count if `generate' == 1
        local N_master = r(N)
        quietly count if `generate' == 2
        local N_using = r(N)
        quietly count if `generate' == 3
        local N_match = r(N)

        if `"`saving'"' != "" {
            if `"`savereplace'"' != "" save `"`saving'"', replace
            else save `"`saving'"'
        }
    }
    local rc = _rc
    if `rc' {
        restore
        exit `rc'
    }
    restore, not

    return scalar N_master = `N_master'
    return scalar N_using = `N_using'
    return scalar N_match = `N_match'

    capture hxhistory, add(`"`usecmd'"')
    capture hxhistory, add(`"`mergecmd'"')
    if `"`saving'"' != "" capture hxhistory, add(`"`savecmd'"')
end
