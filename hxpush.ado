*! hxpush 1.0.0  10aug2026
*! Write a generated command to Stata History without executing it.
program define hxpush, rclass
    version 16.0
    syntax , COMMAND(string asis)

    local native = trim(`"`command'"')
    if substr(`"`native'"', 1, 2) == char(96) + char(34) & ///
        substr(`"`native'"', -2, 2) == char(34) + char(39) {
        local native = substr(`"`native'"', 3, strlen(`"`native'"') - 4)
    }
    else if substr(`"`native'"', 1, 1) == char(34) & ///
        substr(`"`native'"', -1, 1) == char(34) {
        local native = substr(`"`native'"', 2, strlen(`"`native'"') - 2)
    }
    if `"`native'"' == "" exit 198

    char _dta[hxtoolbox_last_native_command] `"`native'"'
    capture window push `native'
    local rc = _rc
    if `rc' char _dta[hxtoolbox_history_status] "写入失败"
    else char _dta[hxtoolbox_history_status] "已写入"
    return scalar rc = `rc'
    return local command `"`native'"'
    if `rc' exit `rc'
end
