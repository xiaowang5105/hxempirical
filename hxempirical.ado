*! hxempirical 1.4.6  13aug2026
*! Public entry point for the HX empirical workbench
program define hxempirical, rclass
    version 13.0
    syntax [anything(name=request)] [, CLASSIC]

    if c(stata_version) < 17 {
        display as error "hxempirical 需要 Stata 17 或更高版本。"
        display as text  "当前版本：Stata `c(stata_version)'。"
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
            display as result "本次 Stata 会话已添加：用户(U) > 我的实证工具箱。"
            display as text "如需以后每次启动 Stata 都显示：hxempirical menu persist"
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
        display as error "菜单用法：hxempirical menu | hxempirical menu persist | hxempirical menu remove"
        exit 198
    }

    if `"`action'"' == "about" {
        display as text _newline "hxempirical：我的实证工具箱"
        display as text "版本：" as result "1.4.6"
        display as text "Stata：" as result "`c(stata_version)' (`c(os)')"
        display as text "最低支持：" as result "Stata 17"
        display as text "界面：" as result "Java 单窗口工作台；经典 .dlg 自动后备"
        return local package "hxempirical"
        return local version "1.4.6"
        return local os "`c(os)'"
        return scalar stata_version = c(stata_version)
        exit
    }

    if `"`action'"' == "doctor" {
        hxdependency check
        exit
    }

    if `"`action'"' == "install" {
        if `"`rest'"' == "" {
            display as error "请指定扩展命令，例如：hxempirical install reghdfe"
            exit 198
        }
        hxdependency install `rest'
        exit
    }

    if `"`action'"' == "update" {
        local updatecmd "adoupdate hxempirical, update"
        capture window push `updatecmd'
        capture noisily `updatecmd'
        local rc = _rc
        if `rc' {
            display as error "更新失败，返回码 `rc'。原安装仍由 Stata 包管理器保留。"
            exit `rc'
        }
        display as result "hxempirical 更新检查完成。若安装了新文件，请重新启动 Stata。"
        exit
    }

    display as error "无法识别子命令：`action'"
    display as text  "可用：hxempirical | about | doctor | menu [persist|remove] | classic | install 命令名 | update"
    exit 198
end
