*! hxempirical 1.5.12  20aug2026
*! Public entry point for the HX empirical workbench
program define hxempirical, rclass
    version 13.0
    syntax [anything(name=request)] [, CLASSIC]

    if c(stata_version) < 17 {
        display as error ustrunescape("hxempirical \u9700\u8981 Stata 17 \u6216\u66f4\u9ad8\u7248\u672c\u3002")
        display as text ustrunescape("\u5f53\u524d\u7248\u672c\uff1a") as result "Stata `c(stata_version)'" ustrunescape("\u3002")
        exit 9
    }

    local request = trim(itrim(`"`request'"'))
    gettoken action rest : request
    local action = lower(trim(`"`action'"'))
    local rest = lower(trim(`"`rest'"'))

    if `"`action'"' == "" | `"`action'"' == "open" {
        /* Session menu only. Opening the workbench never edits profile.do. */
        capture quietly hxmenu
        hxtoolbox, `classic'
        exit
    }

    if `"`action'"' == "classic" {
        capture quietly hxmenu
        hxtoolbox, classic
        exit
    }

    if `"`action'"' == "menu" {
        if `"`rest'"' == "" {
            hxmenu
            display as result ustrunescape("\u672c\u6b21 Stata \u4f1a\u8bdd\u5df2\u6dfb\u52a0\uff1a\u7528\u6237(U) > \u6211\u7684\u5b9e\u8bc1\u5de5\u5177\u7bb1\u3002")
            display as text ustrunescape("\u5982\u9700\u4ee5\u540e\u6bcf\u6b21\u542f\u52a8 Stata \u90fd\u663e\u793a\uff1ahxempirical menu persist")
            exit
        }
        if `"`rest'"' == "persist" {
            hxsetup, persist
            exit
        }
        if `"`rest'"' == "remove" {
            hxsetup, remove
            exit
        }
        display as error ustrunescape("\u83dc\u5355\u7528\u6cd5\uff1ahxempirical menu | hxempirical menu persist | hxempirical menu remove")
        exit 198
    }

    if `"`action'"' == "about" {
        display as text _newline ustrunescape("hxempirical\uff1a\u6211\u7684\u5b9e\u8bc1\u5de5\u5177\u7bb1")
        display as text ustrunescape("\u7248\u672c\uff1a") as result "1.5.12"
        display as text ustrunescape("Stata\uff1a") as result "`c(stata_version)' (`c(os)')"
        display as text ustrunescape("\u6700\u4f4e\u652f\u6301\uff1a") as result "Stata 17"
        display as text ustrunescape("\u754c\u9762\uff1a") as result ustrunescape("Java \u5355\u7a97\u53e3\u5de5\u4f5c\u53f0\uff1b\u7ecf\u5178 .dlg \u624b\u52a8\u540e\u5907")
        return local package "hxempirical"
        return local version "1.5.12"
        return local os "`c(os)'"
        return scalar stata_version = c(stata_version)
        exit
    }

    if `"`action'"' == "doctor" {
        local core "hxtoolbox hxmenu hxsetup hxregistry hxresolve hxexecute hxmonitor hxrefresh hxpick"
        local core_total 11
        local core_ok 0
        local core_missing ""
        foreach component of local core {
            capture quietly which `component'
            if _rc local core_missing `"`core_missing' `component'"'
            else local ++core_ok
        }
        capture quietly findfile hxworkbench.jar
        if _rc local core_missing `"`core_missing' hxworkbench.jar"'
        else local ++core_ok
        capture quietly findfile hxtoolbox_v2.dlg
        if _rc local core_missing `"`core_missing' hxtoolbox_v2.dlg"'
        else local ++core_ok

        display as text _newline ustrunescape("\u6838\u5fc3\u5de5\u4f5c\u53f0\u68c0\u67e5")
        if `core_ok' == `core_total' {
            display as result ustrunescape("[\u6838\u5fc3\u7ec4\u4ef6\uff1a\u6b63\u5e38] ") "`core_ok'/`core_total'"
        }
        else {
            display as error ustrunescape("[\u6838\u5fc3\u7ec4\u4ef6\uff1a\u4e0d\u5b8c\u6574] ") "`core_ok'/`core_total'"
            display as error ustrunescape("\u7f3a\u5c11\uff1a") trim(`"`core_missing'"')
        }
        hxdependency check
        local optional_missing = r(optional_missing)
        return scalar core_healthy = (`core_ok' == `core_total')
        return scalar core_installed = `core_ok'
        return scalar core_total = `core_total'
        return scalar optional_missing = `optional_missing'
        exit
    }

    if `"`action'"' == "install" {
        if `"`rest'"' == "" {
            display as error ustrunescape("\u8bf7\u6307\u5b9a\u6269\u5c55\u547d\u4ee4\uff0c\u4f8b\u5982\uff1ahxempirical install reghdfe")
            exit 198
        }
        display as error ustrunescape("hxempirical 不再自动安装第三方命令。")
        display as text  ustrunescape("请按命令作者说明自行安装；安装后打开工作台 > 外部命令查看。")
        exit
    }

    if inlist(`"`action'"', "update", "repair", "uninstall") {
        local installer "https://xiaowang5105.github.io/hxempirical/hxinstall.do"
        local managecmd `"do "`installer'" `action'"'
        capture window push `managecmd'
        capture noisily do `"`installer'"' `action'
        local rc = _rc
        if `rc' {
            display as error "hxempirical `action' " ustrunescape("\u5931\u8d25\uff0c\u8fd4\u56de\u7801") " `rc'" ustrunescape("\u3002")
            exit `rc'
        }
        exit
    }

    display as error ustrunescape("\u65e0\u6cd5\u8bc6\u522b\u5b50\u547d\u4ee4\uff1a") "`action'"
    display as text ustrunescape("\u53ef\u7528\uff1ahxempirical | about | doctor | menu [persist|remove] | classic | update | repair | uninstall")
    exit 198
end
