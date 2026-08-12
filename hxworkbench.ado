*! hxworkbench 1.0.0  09aug2026
*! Open and focus Stata-native windows used by the toolbox workbench.
program define hxworkbench, rclass
    version 16.0
    syntax , ACTION(string) [PREVIEW]

    local action = lower(trim(`"`action'"'))
    local native ""
    local needs_data 0

    if inlist("`action'", "browser", "browse", "refresh") {
        local native "browse"
        local needs_data 1
    }
    else if inlist("`action'", "editor", "edit") {
        local native "edit"
        local needs_data 1
    }
    else if "`action'" == "variables" local native "window manage forward variables"
    else if "`action'" == "results" local native "window manage forward results"
    else if "`action'" == "graph" local native "window manage forward graph"
    else if "`action'" == "history" local native "window manage forward history"
    else if "`action'" == "command" local native "window manage forward command"
    else {
        display as error "未知工作台窗口：`action'"
        exit 198
    }

    return local command `"`native'"'
    if "`preview'" != "" exit

    if `needs_data' & (_N == 0 | c(k) == 0) {
        display as error "当前没有可显示的数据。请先载入数据。"
        exit 2000
    }

    capture window push `native'
    capture noisily `native'
    local rc = _rc
    if `rc' {
        display as error "无法打开对应的 Stata 原生窗口，返回码为 `rc'。"
        exit `rc'
    }
end
