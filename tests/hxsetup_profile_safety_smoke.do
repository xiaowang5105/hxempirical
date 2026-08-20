version 17.0
clear all
set more off

args repository
if `"`repository'"' == "" local repository `"`c(pwd)'"'
local repository : subinstr local repository "\" "/", all

capture program drop hxsetup
capture quietly run `"`repository'/hxsetup.ado"'
if _rc {
    display as error "HX_SETUP_PROFILE_TEST_FAIL could not load hxsetup"
    exit _rc
}

tempfile profile filtered
local begin "* >>> HXEMPIRICAL MANAGED MENU >>>"
tempname profile_out
file open `profile_out' using `"`profile'"', write text replace
file write `profile_out' "global USER_LINE_BEFORE 1" _n
file write `profile_out' `"`begin'"' _n
file write `profile_out' "global USER_LINE_AFTER_BROKEN_MARKER 2" _n
file close `profile_out'

quietly checksum `"`profile'"'
local original_bytes = r(filelen)
local original_checksum = r(checksum)
capture noisily hxsetup, persist profile(`"`profile'"') menusource(`"`repository'/hxmenu.ado"')
local persist_rc = _rc
quietly checksum `"`profile'"'
if `persist_rc' == 0 | r(filelen) != `original_bytes' | r(checksum) != `original_checksum' {
    display as error "HX_SETUP_PROFILE_TEST_FAIL malformed profile changed"
    exit 459
}
quietly filefilter `"`profile'"' `"`filtered'"', ///
    from("USER_LINE_AFTER_BROKEN_MARKER") to("USER_LINE_PRESERVED") replace
if r(occurrences) != 1 {
    display as error "HX_SETUP_PROFILE_TEST_FAIL trailing user code lost"
    exit 459
}

display as result "HX_SETUP_PROFILE_SAFETY_OK"
