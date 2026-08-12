*! hxmenu 6.1.0  11aug2026
*! Add exactly one HX entry without touching other user-installed menus.
program define hxmenu
    version 17.0

    if "`c(mode)'" == "batch" exit

    /*
       Public-package rule: never call window menu clear here.  That command
       removes menu entries owned by other packages as well.  The session
       global makes our own registration idempotent.
    */
    if "$HXEMPIRICAL_MENU_INSTALLED" == "1" {
        capture window menu refresh
        exit
    }

    capture window menu append item "stUser" "我的实证工具箱" "hxempirical"
    local rc = _rc
    if `rc' {
        display as error "无法添加 hxempirical 菜单入口，返回码 `rc'。"
        exit `rc'
    }
    capture window menu refresh
    global HXEMPIRICAL_MENU_INSTALLED 1
end
