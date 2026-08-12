*! hxsetup 2.2.0  11aug2026
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
    if `"`profile'"' == "" local profile `"`c(sysdir_personal)'profile.do"'

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

    file open `output' using `"`rewritten'"', write text replace
    if `profile_exists' {
        /* Keep a one-time backup before the first HX-managed edit. */
        local backup `"`c(sysdir_personal)'profile.before_hxempirical.do"'
        capture confirm file `"`backup'"'
        if _rc capture copy `"`profile'"' `"`backup'"'

        file open `input' using `"`profile'"', read text
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
    copy `"`rewritten'"' `"`profile'"', replace

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
