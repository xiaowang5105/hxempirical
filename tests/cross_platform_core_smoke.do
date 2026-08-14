version 17.0
clear all
set more off

/* Run from the repository root on Windows or macOS. */
capture quietly which hxsetup
if _rc adopath ++ "."

local original_personal `"`c(sysdir_personal)'"'
local test_personal `"`c(tmpdir)'hxempirical_profile_smoke"'
local test_profile `"`test_personal'/profile.do"'
local test_backup `"`test_personal'/profile.before_hxempirical.do"'
local begin "* >>> HXEMPIRICAL MANAGED MENU >>>"

capture quietly erase `"`test_profile'"'
capture quietly erase `"`test_backup'"'
capture quietly erase `"`test_personal'/__hxempirical_profile_write_test.tmp"'
capture quietly rmdir `"`test_personal'"'

sysdir set PERSONAL `"`test_personal'/"'

/* A clean account starts without the PERSONAL directory. */
capture noisily hxsetup, persist
if _rc {
    local rc = _rc
    sysdir set PERSONAL `"`original_personal'"'
    display as error "HX_TEST_FAIL clean profile persistence r(`rc')"
    exit `rc'
}
confirm file `"`test_profile'"'

/* Repeating persistence must keep exactly one managed block. */
quietly hxsetup, persist
tempname profile_in
file open `profile_in' using `"`test_profile'"', read text
local begin_count 0
file read `profile_in' line
while r(eof) == 0 {
    if trim(`"`line'"') == `"`begin'"' local ++begin_count
    file read `profile_in' line
}
file close `profile_in'
if `begin_count' != 1 {
    sysdir set PERSONAL `"`original_personal'"'
    display as error "HX_TEST_FAIL duplicate managed profile blocks: `begin_count'"
    exit 459
}

/* Removal keeps unrelated profile.do content and removes the HX block. */
quietly hxsetup, remove
confirm file `"`test_profile'"'
tempname profile_after
file open `profile_after' using `"`test_profile'"', read text
local begin_count 0
file read `profile_after' line
while r(eof) == 0 {
    if trim(`"`line'"') == `"`begin'"' local ++begin_count
    file read `profile_after' line
}
file close `profile_after'
if `begin_count' != 0 {
    sysdir set PERSONAL `"`original_personal'"'
    display as error "HX_TEST_FAIL managed profile block remains after remove"
    exit 459
}

/* Core health and optional extensions are reported separately. */
capture noisily hxempirical doctor
if _rc {
    local rc = _rc
    sysdir set PERSONAL `"`original_personal'"'
    display as error "HX_TEST_FAIL doctor r(`rc')"
    exit `rc'
}
if r(core_healthy) != 1 {
    sysdir set PERSONAL `"`original_personal'"'
    display as error "HX_TEST_FAIL core components incomplete"
    exit 111
}
if r(optional_missing) < 0 | r(optional_missing) > 8 {
    sysdir set PERSONAL `"`original_personal'"'
    display as error "HX_TEST_FAIL invalid optional dependency count"
    exit 459
}

sysdir set PERSONAL `"`original_personal'"'
capture quietly erase `"`test_profile'"'
capture quietly erase `"`test_backup'"'
capture quietly erase `"`test_personal'/__hxempirical_profile_write_test.tmp"'
capture quietly rmdir `"`test_personal'"'

display as result "HX_CROSS_PLATFORM_CORE_SMOKE_OK"
