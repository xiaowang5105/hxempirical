*! hxtoolbox 4.5.0  11aug2026
*! Open the Java single-window workbench; keep the native dialog as fallback.
program define hxtoolbox
    version 17.0
    syntax [, CLASSIC]

    capture quietly hxmenu

    quietly hxrefresh
    quietly hxpick, target(all) action(clear)
    quietly hxmonitor, action(refresh)

    /* Batch runs and explicit classic mode use the tested native dialog. */
    if "`classic'" != "" | "`c(mode)'" == "batch" {
        db hxtoolbox_v2
        exit
    }

    local jarfile ""
    capture quietly findfile hxworkbench.jar
    if !_rc local jarfile `"`r(fn)'"'
    if `"`jarfile'"' == "" {
        capture quietly findfile hxempirical.ado
        if !_rc {
            local entry `"`r(fn)'"'
            local entry : subinstr local entry "\" "/", all
            local suffix "h/hxempirical.ado"
            local root = substr(`"`entry'"', 1, strlen(`"`entry'"') - strlen("`suffix'"))
            local jarfile `"`root'jar/hxworkbench.jar"'
            capture confirm file `"`jarfile'"'
            if _rc local jarfile ""
        }
    }
    if `"`jarfile'"' == "" {
        capture quietly findfile hxtoolbox.ado
        if !_rc {
            local entry `"`r(fn)'"'
            local entry : subinstr local entry "\" "/", all
            local jarfile = substr(`"`entry'"', 1, strlen(`"`entry'"') - strlen("hxtoolbox.ado")) + "hxworkbench.jar"
            capture confirm file `"`jarfile'"'
            if _rc local jarfile ""
        }
    }
    if `"`jarfile'"' == "" {
        display as text "未找到单窗口工作台组件，已打开经典界面。"
        db hxtoolbox_v2
        exit
    }
    capture noisily javacall com.hexie.stata.HxWorkbench launch, ///
        classpath(`"`jarfile'"')
    if _rc {
        local rc = _rc
        display as error "单窗口工作台启动失败（返回码 `rc'），已打开经典界面。"
        display as text "可运行 hxtoolbox, classic 随时使用原有窗口。"
        db hxtoolbox_v2
    }
end
