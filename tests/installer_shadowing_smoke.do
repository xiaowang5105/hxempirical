version 17.0
clear all
set more off

args repository
if `"`repository'"' == "" local repository `"`c(pwd)'"'
local repository : subinstr local repository "\" "/", all
local installer `"`repository'/hxinstall.do"'
capture quietly confirm file `"`installer'"'
if _rc {
    display as error "HX_INSTALLER_SHADOWING_FAIL cannot find hxinstall.do"
    exit 601
}

local original_personal `"`c(sysdir_personal)'"'
local original_plus `"`c(sysdir_plus)'"'
local original_pwd `"`c(pwd)'"'
tempfile shadow_base stale_copy
local test_personal `"`shadow_base'_personal"'
local test_plus `"`shadow_base'_plus"'
local personal_h `"`test_personal'/h"'
local plus_h `"`test_plus'/h"'

sysdir set PERSONAL `"`test_personal'/"'
sysdir set PLUS `"`test_plus'/"'
capture quietly mkdir `"`test_personal'"'
capture quietly mkdir `"`test_plus'"'
capture quietly mkdir `"`personal_h'"'
capture quietly mkdir `"`plus_h'"'

capture noisily do `"`installer'"' auto `"`repository'"'
local install_rc = _rc
if `install_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    sysdir set PLUS `"`original_plus'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_SHADOWING_FAIL initial install r(`install_rc')"
    exit `install_rc'
}

/* Keep a current lower-priority PLUS copy, then make only the PERSONAL header
   stale.  The executable body remains current so the new doctor can diagnose
   the fixture exactly as a historical multi-version installation. */
capture quietly copy `"`repository'/hxempirical.ado"' `"`plus_h'/hxempirical.ado"', replace
if _rc {
    sysdir set PERSONAL `"`original_personal'"'
    sysdir set PLUS `"`original_plus'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_SHADOWING_FAIL cannot create PLUS fixture"
    exit 603
}

tempname stale_in stale_out
file open `stale_in' using `"`personal_h'/hxempirical.ado"', read text
file open `stale_out' using `"`stale_copy'"', write text replace
local first 1
file read `stale_in' line
while r(eof) == 0 {
    if `first' {
        file write `stale_out' "*! hxempirical 1.5.12  20aug2026" _n
        local first 0
    }
    else file write `stale_out' `"`line'"' _n
    file read `stale_in' line
}
file close `stale_in'
file close `stale_out'
copy `"`stale_copy'"' `"`personal_h'/hxempirical.ado"', replace

discard
capture noisily hxempirical doctor
local doctor_rc = _rc
local shadowing = .
local personal_version ""
local plus_version ""
if !`doctor_rc' {
    local shadowing = r(shadowing_detected)
    local personal_version `"`r(personal_version)'"'
    local plus_version `"`r(plus_version)'"'
}
if `doctor_rc' | `shadowing' != 1 | `"`personal_version'"' != "1.5.12" | `"`plus_version'"' != "1.5.13" {
    sysdir set PERSONAL `"`original_personal'"'
    sysdir set PLUS `"`original_plus'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_SHADOWING_FAIL doctor did not detect divergent PERSONAL/PLUS versions"
    exit 459
}

capture noisily do `"`installer'"' repair `"`repository'"'
local repair_rc = _rc
if `repair_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    sysdir set PLUS `"`original_plus'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_SHADOWING_FAIL repair r(`repair_rc')"
    exit `repair_rc'
}

discard
capture quietly findfile hxempirical.ado
local active_rc = _rc
local active_path ""
if !`active_rc' local active_path `"`r(fn)'"'
local active_norm : subinstr local active_path "\" "/", all
local expected_norm `"`personal_h'/hxempirical.ado"'
if lower("`c(os)'") == "windows" {
    local active_norm = lower(`"`active_norm'"')
    local expected_norm = lower(`"`expected_norm'"')
}
if `active_rc' | `"`active_norm'"' != `"`expected_norm'"' {
    sysdir set PERSONAL `"`original_personal'"'
    sysdir set PLUS `"`original_plus'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_SHADOWING_FAIL repair did not make PERSONAL/h effective"
    exit 459
}

capture noisily hxempirical doctor
local clean_doctor_rc = _rc
local clean_shadow = .
if !`clean_doctor_rc' local clean_shadow = r(shadowing_detected)
if `clean_doctor_rc' | `clean_shadow' != 0 | `"`r(personal_version)'"' != "1.5.13" | `"`r(plus_version)'"' != "1.5.13" {
    sysdir set PERSONAL `"`original_personal'"'
    sysdir set PLUS `"`original_plus'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_SHADOWING_FAIL repair did not converge versions"
    exit 459
}

sysdir set PERSONAL `"`original_personal'"'
sysdir set PLUS `"`original_plus'"'
cd `"`original_pwd'"'
discard
display as result "HX_INSTALLER_SHADOWING_OK"
