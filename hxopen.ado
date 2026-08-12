*! hxopen 1.0.0  09aug2026
*! Open help or the official Stata dialog for the resolved command
program define hxopen
    version 16.0
    syntax anything(name=command) [, DIALOG HELP]
    gettoken cmd rest : command
    if "`dialog'`help'" == "" local help "help"

    if "`dialog'" != "" {
        capture quietly findfile `cmd'.dlg
        if _rc {
            display as error "`cmd' 没有可用的官方 Stata dialog。"
            exit 601
        }
        db `cmd'
        exit
    }
    capture quietly findfile `cmd'.sthlp
    if _rc {
        capture quietly findfile `cmd'.hlp
        if _rc {
            display as error "没有找到 `cmd' 的 help 文件。"
            exit 601
        }
    }
    help `cmd'
end
