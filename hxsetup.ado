*! hxsetup 2.4.0  20aug2026
*! Opt-in persistence for the single HX menu entry; never rewrites unrelated profile.do lines.
program define hxsetup, rclass
    version 17.0
    syntax [, PERSIST REMOVE PROFILE(string) MENUSOURCE(string)]

    if "`persist'" != "" & "`remove'" != "" {
        display as error "persist 与 remove 不能同时指定。"
        exit 198
    }

    local profile = trim(`"`profile'"')
    if substr(`"`profile'"', 1, 1) == char(34) & substr(`"`profile'"', -1, 1) == char(34) {
        local profile = substr(`"`profile'"', 2, strlen(`"`profile'"') - 2)
    }
    local default_profile = (`"`profile'"' == "")
    local personal `"`c(sysdir_personal)'"'
    if `"`personal'"' != "" {
        local lastchar = substr(`"`personal'"', strlen(`"`personal'"'), 1)
        if !inlist(`"`lastchar'"', "/", "\") local personal `"`personal'/"'
    }
    if `default_profile' {
        if `"`personal'"' == "" {
            display as error "Stata 没有返回 PERSONAL ado 目录。请先运行 sysdir 检查环境。"
            exit 603
        }
        local profile `"`personal'profile.do"'
    }

    local menusource = trim(`"`menusource'"')
    if substr(`"`menusource'"', 1, 1) == char(34) & substr(`"`menusource'"', -1, 1) == char(34) {
        local menusource = substr(`"`menusource'"', 2, strlen(`"`menusource'"') - 2)
    }
    if `"`menusource'"' == "" & `"`personal'"' != "" local menusource `"`personal'hxmenu.ado"'

    /* Load the exact managed menu program.  Command-name resolution would let
       a stale hxmenu.ado in the current directory shadow the installed file. */
    if "`remove'" == "" {
        capture quietly confirm file `"`menusource'"'
        if _rc {
            display as error "找不到受管菜单程序：`menusource'"
            exit 601
        }
    }

    /* No option means session-only setup. */
    if "`persist'`remove'" == "" {
        capture program drop hxmenu
        capture quietly run `"`menusource'"'
        local menu_loader_rc = _rc
        if `menu_loader_rc' exit `menu_loader_rc'
        quietly hxmenu
        return scalar installed = 1
        exit
    }

    local begin  "* >>> HXEMPIRICAL MANAGED MENU >>>"
    local finish "* <<< HXEMPIRICAL MANAGED MENU <<<"
    tempfile rewritten profile_snapshot
    tempname input output scan

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

    if `profile_exists' {
        /* Validate the complete marker structure before creating a rewritten
           profile.  An unclosed marker must preserve every user line. */
        capture quietly file open `scan' using `"`profile'"', read text
        local scan_rc = _rc
        if `scan_rc' {
            display as error "无法读取现有 profile.do：`profile'"
            display as text "文件可能被其他程序占用，或当前用户没有读取权限。"
            exit 603
        }
        local managed 0
        local marker_error 0
        file read `scan' line
        while r(eof) == 0 {
            if trim(`"`line'"') == `"`begin'"' {
                if `managed' local marker_error 1
                local managed 1
            }
            else if trim(`"`line'"') == `"`finish'"' {
                if !`managed' local marker_error 1
                local managed 0
            }
            file read `scan' line
        }
        file close `scan'
        if `managed' local marker_error 1
        if `marker_error' {
            display as error "profile.do 中的 HXEMPIRICAL 管理标记不完整。"
            display as text "为保护用户代码，profile.do 保持原样；请先修复或移除损坏的标记后重试。"
            exit 459
        }

        /* Keep a one-time backup before the first HX-managed edit.  A failed
           backup is a hard stop; persistence must never continue unprotected. */
        if `default_profile' local backup `"`personal'profile.before_hxempirical.do"'
        else local backup `"`profile'.before_hxempirical"'
        capture quietly confirm file `"`backup'"'
        if _rc {
            capture quietly copy `"`profile'"' `"`backup'"'
            local backup_rc = _rc
            if `backup_rc' {
                display as error "无法备份现有 profile.do，菜单配置已停止。"
                display as text "原文件保持不变：`profile'"
                exit 603
            }
        }

        /* Snapshot the current profile for this operation as well.  The
           one-time backup above may describe an earlier user configuration. */
        capture quietly copy `"`profile'"' `"`profile_snapshot'"', replace
        if _rc {
            display as error "无法创建本次 profile.do 事务快照，菜单配置已停止。"
            exit 603
        }
    }

    capture quietly file open `output' using `"`rewritten'"', write text
    if _rc {
        display as error "无法创建菜单配置临时文件。请检查 Stata 临时目录的写权限。"
        exit 603
    }
    if `profile_exists' {
        capture quietly file open `input' using `"`profile'"', read text
        if _rc {
            capture file close `output'
            display as error "无法读取现有 profile.do：`profile'"
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
        file write `output' "capture program drop hxmenu" _n
        file write `output' `"capture quietly run `"`menusource'"'"' _n
        file write `output' "if !_rc capture noisily hxmenu" _n
        file write `output' `"`finish'"' _n
    }
    file close `output'
    quietly checksum `"`rewritten'"'
    local rewritten_bytes = r(filelen)
    local rewritten_checksum = r(checksum)
    capture quietly copy `"`rewritten'"' `"`profile'"', replace
    local write_rc = _rc
    if !`write_rc' {
        capture quietly checksum `"`profile'"'
        if _rc local write_rc 603
        else if r(filelen) != `rewritten_bytes' | r(checksum) != `rewritten_checksum' local write_rc 603
    }
    if `write_rc' {
        display as error "无法写入 profile.do：`profile'"
        local restore_rc 0
        if `profile_exists' {
            capture quietly checksum `"`profile_snapshot'"'
            local snapshot_checksum_rc = _rc
            if `snapshot_checksum_rc' local restore_rc 603
            else {
                local snapshot_bytes = r(filelen)
                local snapshot_checksum = r(checksum)
                capture quietly copy `"`profile_snapshot'"' `"`profile'"', replace
                local restore_rc = _rc
                if !`restore_rc' {
                    capture quietly checksum `"`profile'"'
                    if _rc local restore_rc 603
                    else if r(filelen) != `snapshot_bytes' | r(checksum) != `snapshot_checksum' local restore_rc 603
                }
            }
        }
        else {
            capture quietly erase `"`profile'"'
            capture quietly confirm file `"`profile'"'
            if !_rc local restore_rc 603
        }
        if `restore_rc' {
            local recovery `"`profile'.hxempirical.recovery"'
            capture quietly copy `"`profile_snapshot'"' `"`recovery'"', replace
            local recovery_rc = _rc
            if !`recovery_rc' & `profile_exists' {
                capture quietly checksum `"`recovery'"'
                if _rc local recovery_rc 603
                else if r(filelen) != `snapshot_bytes' | r(checksum) != `snapshot_checksum' local recovery_rc 603
            }
            if !`recovery_rc' display as text "当前事务快照已保留在：`recovery'"
            else if `profile_exists' display as text "请使用备份恢复：`backup'"
        }
        else display as text "原 profile.do 已从本次事务快照恢复。"
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

    capture program drop hxmenu
    capture quietly run `"`menusource'"'
    local menu_loader_rc = _rc
    if `menu_loader_rc' exit `menu_loader_rc'
    quietly hxmenu
    display as result "已设置：Stata 启动后显示 用户(U) > 我的实证工具箱。"
    return local profile `"`profile'"'
    return scalar installed = 1
end
