*! hxsetup 2.3.0  14aug2026
*! Opt-in persistence for the single HX menu entry; never rewrites unrelated profile.do lines.
program define hxsetup, rclass
    version 17.0
    syntax [, PERSIST REMOVE PROFILE(string asis)]

    if "`persist'" != "" & "`remove'" != "" {
        display as error "persist 与 remove 不能同时指定。"
        exit 198
    }

    /* No option means session-only setup. */
    if "`persist'`remove'" == "" {
        quietly hxmenu
        return scalar installed = 1
        exit
    }

    local profile = trim(`"`profile'"')
    if substr(`"`profile'"', 1, 1) == char(34) & substr(`"`profile'"', -1, 1) == char(34) {
        local profile = substr(`"`profile'"', 2, strlen(`"`profile'"') - 2)
    }
    local default_profile = (`"`profile'"' == "")
    local personal `"`c(sysdir_personal)'"'
    if `default_profile' {
        if `"`personal'"' == "" {
            display as error "Stata 没有返回 PERSONAL ado 目录。请先运行 sysdir 检查环境。"
            exit 603
        }
        local lastchar = substr(`"`personal'"', strlen(`"`personal'"'), 1)
        if !inlist(`"`lastchar'"', "/", "\") local personal `"`personal'/"'
        local profile `"`personal'profile.do"'
    }

    local begin  "* >>> HXEMPIRICAL MANAGED MENU >>>"
    local finish "* <<< HXEMPIRICAL MANAGED MENU <<<"
    tempfile rewritten
    tempname input output

    capture confirm file `"`profile'"'
    local profile_exists = (_rc == 0)

    /* Removing HX persistence from a profile that does not exist must not
       create a new empty profile.do. */
    if "`remove'" != "" & !`profile_exists' {
        global HXEMPIRICAL_MENU_INSTALLED 0
        display as result "未发现 profile.do；无需移除持久菜单，也未创建新文件。"
        return local profile `"`profile'"'
        return scalar installed = 0
        exit
    }

    /* A clean Stata user account may not have PERSONAL yet, especially on
       macOS when hxempirical was installed elsewhere on the adopath. */
    if "`persist'" != "" & `default_profile' {
        capture quietly mkdir `"`personal'"'
        local probe `"`personal'__hxempirical_profile_write_test.tmp"'
        tempname probehandle
        capture quietly file open `probehandle' using `"`probe'"', write text replace
        local probe_rc = _rc
        if `probe_rc' {
            display as error "无法创建或写入 Stata PERSONAL 目录：`personal'"
            display as text "请运行 sysdir 检查 PERSONAL 路径和当前用户的目录权限。"
            exit 603
        }
        file write `probehandle' "hxempirical profile write test" _n
        file close `probehandle'
        capture quietly erase `"`probe'"'
    }

    capture quietly file open `output' using `"`rewritten'"', write text
    if _rc {
        display as error "无法创建菜单配置临时文件。请检查 Stata 临时目录的写权限。"
        exit 603
    }
    if `profile_exists' {
        /* Keep a one-time backup before the first HX-managed edit. */
        local backup `"`personal'profile.before_hxempirical.do"'
        capture confirm file `"`backup'"'
        if _rc capture quietly copy `"`profile'"' `"`backup'"'

        capture quietly file open `input' using `"`profile'"', read text
        if _rc {
            display as error "无法读取现有 profile.do：`profile'"
            display as text "文件可能被其他程序占用，或当前用户没有读取权限。"
            exit 603
        }
        local managed 0
        file read `input' line
        while r(eof) == 0 {
            if trim(`"`line'"') == `"`begin'"' local managed 1
            else if trim(`"`line'"') == `"`finish'"' local managed 0
            else if !`managed' file write `output' `"`line'"' _n
            file read `input' line
        }
        file close `input'
    }

    if "`persist'" != "" {
        file write `output' `"`begin'"' _n
        file write `output' "capture which hxmenu" _n
        file write `output' "if !_rc capture noisily hxmenu" _n
        file write `output' `"`finish'"' _n
    }
    file close `output'
    capture quietly copy `"`rewritten'"' `"`profile'"', replace
    local write_rc = _rc
    if `write_rc' {
        display as error "无法写入 profile.do：`profile'"
        if !`default_profile' display as text "自定义 profile() 的上级目录必须已经存在且可写。"
        else display as text "请运行 sysdir 检查 PERSONAL 路径和当前用户的目录权限。"
        exit 603
    }

    if "`remove'" != "" {
        global HXEMPIRICAL_MENU_INSTALLED 0
        display as result "已移除 hxempirical 自己管理的启动菜单区块。其他 profile.do 内容未改动。"
        return local profile `"`profile'"'
        return scalar installed = 0
        exit
    }

    quietly hxmenu
    display as result "已设置：Stata 启动后显示 用户(U) > 我的实证工具箱。"
    return local profile `"`profile'"'
    return scalar installed = 1
end
