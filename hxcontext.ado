*! hxcontext 1.0.0 05sep2026
*! Execute an internal UI query without replacing the user's returned results.
program define hxcontext
    version 17.0
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
    tempname caller
    _return hold `caller'
    _return restore `caller', hold
    capture noisily `native'
    local rc = _rc
    _return restore `caller'
    if `rc' exit `rc'
end
