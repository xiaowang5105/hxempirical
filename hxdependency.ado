*! hxdependency 0.5.0  14aug2026
*! Lazy checks and user-approved installation of optional community commands
program define hxdependency, rclass
    version 17.0
    syntax [anything(name=request)]

    local request = lower(trim(itrim(`"`request'"')))
    gettoken action target : request
    if `"`action'"' == "" local action "check"
    local supported "reghdfe winsor2 ivreghdfe ppmlhdfe oneclick oneclick_robustness coefplot event_plot"

    if `"`action'"' == "check" {
        if `"`target'"' == "" local targets "`supported'"
        else local targets "`target'"
        local optional_total 0
        local optional_installed 0
        local missing ""
        display as text _newline "可选扩展检查"
        display as text "这些命令不影响 hxempirical 启动；只有进入对应功能时才需要安装。"
        foreach cmd of local targets {
            capture quietly which `cmd'
            local installed = cond(_rc, 0, 1)
            local ++optional_total
            if `installed' {
                local ++optional_installed
                display as result "[可选扩展：已安装] `cmd'"
            }
            else {
                local missing `"`missing' `cmd'"'
                local note "进入对应功能时可按提示安装"
                if `"`cmd'"' == "oneclick_robustness" local note "需按命令作者说明手动安装"
                display as text "[可选扩展：未安装] `cmd' — `note'"
            }
            return scalar `cmd' = `installed'
        }
        local optional_missing = `optional_total' - `optional_installed'
        display as text "可选扩展：`optional_installed'/`optional_total' 已安装；`optional_missing' 个未安装。"
        if `optional_missing' display as text "当前核心工作台仍可正常使用。"
        return local missing = trim(`"`missing'"')
        return scalar optional_total = `optional_total'
        return scalar optional_installed = `optional_installed'
        return scalar optional_missing = `optional_missing'
        exit
    }

    if `"`action'"' != "install" | `"`target'"' == "" {
        display as error "用法：hxdependency check [命令名] 或 hxdependency install 命令名"
        exit 198
    }
    if !strpos(" `supported' ", " `target' ") {
        display as error "当前按需安装器尚未登记 `target'。"
        display as text  "可登记命令：`supported'"
        exit 198
    }

    if `"`target'"' == "oneclick_robustness" {
        display as error "oneclick_robustness 当前没有在 hxempirical 中配置经过验证的 SSC 自动安装源。"
        display as text  "请按作者发布说明安装；安装后工具箱会自动识别。"
        exit 601
    }

    local packages "`target'"
    if `"`target'"' == "reghdfe" local packages "ftools reghdfe"
    if `"`target'"' == "ivreghdfe" local packages "ftools reghdfe ranktest ivreg2 ivreghdfe"
    if `"`target'"' == "ppmlhdfe" local packages "ftools reghdfe ppmlhdfe"

    foreach pkg of local packages {
        capture quietly which `pkg'
        if _rc {
            local cmd "ssc install `pkg', replace"
            capture window push `cmd'
            display as text "正在从 SSC 安装 `pkg'..."
            capture noisily `cmd'
            local rc = _rc
            if `rc' {
                display as error "`pkg' 安装失败，返回码 `rc'。"
                display as text  "请检查网络，或查看该命令作者提供的最新安装说明。"
                exit `rc'
            }
        }
    }
    discard
    capture quietly which `target'
    if _rc {
        display as error "安装流程结束，但 Stata 仍未找到 `target'。"
        exit 111
    }
    display as result "`target' 已安装，可以回到工具箱继续使用。"
    return local command "`target'"
    return scalar installed = 1
end
