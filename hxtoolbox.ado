*! hxtoolbox 4.7.2  20aug2026
*! Open the Java single-window workbench; classic dialog requires explicit option.
program define hxtoolbox
    version 17.0
    syntax [, CLASSIC]

    capture quietly hxmenu

    quietly hxrefresh
    quietly hxpick, target(all) action(clear)
    quietly hxmonitor, action(refresh)

    /* Classic is a compatibility fallback with a deliberately smaller scope. */
    if "`classic'" != "" {
        display as text "正在打开经典兼容界面。该界面保留基础操作；最新工作台功能以 Java 界面为准。"
        db hxtoolbox_v2
        exit
    }
    if "`c(mode)'" == "batch" {
        display as error "hxempirical 图形工作台只能在 Stata 交互模式中打开。"
        display as text "批处理实证请直接运行生成的 Stata 命令或正式 .do 文件。"
        exit 198
    }

    local jarfile ""
    /* Prefer the JAR adjacent to the active hxtoolbox.ado. This prevents an older
       hxworkbench.jar elsewhere on adopath from shadowing the current package. */
    capture quietly findfile hxtoolbox.ado
    if !_rc {
        local entry `"`r(fn)'"'
        local entry : subinstr local entry "\" "/", all
        local jarfile = substr(`"`entry'"', 1, strlen(`"`entry'"') - strlen("hxtoolbox.ado")) + "hxworkbench.jar"
        capture confirm file `"`jarfile'"'
        if _rc local jarfile ""
    }
    if `"`jarfile'"' == "" {
        capture quietly findfile hxworkbench.jar
        if !_rc local jarfile `"`r(fn)'"'
    }
    if `"`jarfile'"' == "" {
        display as error "未找到 Java 工作台组件 hxworkbench.jar，当前安装可能不完整。"
        display as text "请先运行 hxempirical doctor；如需临时使用基础兼容界面，可运行 hxtoolbox, classic。"
        exit 601
    }
    capture noisily javacall com.hexie.stata.HxWorkbench launch, ///
        classpath(`"`jarfile'"')
    if _rc {
        local rc = _rc
        display as error "Java 工作台启动失败，返回码 `rc'。"
        display as text "请运行 hxempirical doctor 检查安装；基础兼容界面可用 hxtoolbox, classic 手动打开。"
        exit `rc'
    }
end
