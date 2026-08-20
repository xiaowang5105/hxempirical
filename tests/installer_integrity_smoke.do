version 17.0
clear all
set more off

/* Verify strict release-index parsing and non-destructive failure. */
args repository
if `"`repository'"' == "" local repository `"`c(pwd)'"'
local repository : subinstr local repository "\" "/", all
local launcher `"`repository'/hxinstall.do"'

local original_personal `"`c(sysdir_personal)'"'
local original_pwd `"`c(pwd)'"'
tempfile integrity_base damaged_index bad_version_index
local test_personal `"`integrity_base'_personal"'
local install_target `"`test_personal'/h"'
local bad_source `"`integrity_base'_bad_source"'
capture quietly mkdir `"`bad_source'"'
sysdir set PERSONAL `"`test_personal'/"'
cd `"`c(tmpdir)'"'

capture noisily do `"`launcher'"' install `"`repository'"'
local install_rc = _rc
if `install_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_INTEGRITY_TEST_FAIL install r(`install_rc')"
    exit `install_rc'
}

quietly checksum `"`install_target'/hxworkbench.jar"'
local jar_bytes = r(filelen)
local jar_checksum = r(checksum)

/* The bootstrap core and both metadata files are present, while the declared
   part count is deliberately inconsistent with the listed f records. */
copy `"`repository'/hxinstaller.ado"' `"`bad_source'/hxinstaller.ado"', replace
copy `"`repository'/hxempirical.pkg"' `"`bad_source'/hxempirical.pkg"', replace
quietly filefilter `"`repository'/hxempirical-release.index"' `"`damaged_index'"', ///
    from("d parts ") to("d parts 999") replace
if r(occurrences) != 1 {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_INTEGRITY_TEST_FAIL parts fixture"
    exit 459
}
copy `"`damaged_index'"' `"`bad_source'/hxempirical-release.index"', replace

capture noisily do `"`launcher'"' repair `"`bad_source'"'
local damaged_rc = _rc
capture quietly checksum `"`install_target'/hxworkbench.jar"'
local after_checksum_rc = _rc
local after_bytes 0
local after_checksum -1
if !`after_checksum_rc' {
    local after_bytes = r(filelen)
    local after_checksum = r(checksum)
}
if `damaged_rc' == 0 | `after_checksum_rc' | `after_bytes' != `jar_bytes' | `after_checksum' != `jar_checksum' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_INTEGRITY_TEST_FAIL invalid index changed installation"
    exit 459
}
foreach required in hxinstaller.ado hxempirical.pkg hxempirical.integrity {
    capture quietly confirm file `"`install_target'/`required'"'
    if _rc {
        sysdir set PERSONAL `"`original_personal'"'
        cd `"`original_pwd'"'
        display as error "HX_INSTALLER_INTEGRITY_TEST_FAIL retry file missing: `required'"
        exit 601
    }
}
display as result "HX_INSTALLER_INDEX_VALIDATION_OK"

/* An unknown metadata format must fail closed even when every current field is
   otherwise valid. */
quietly filefilter `"`repository'/hxempirical-release.index"' `"`bad_version_index'"', ///
    from("v 1") to("v 999") replace
if r(occurrences) != 1 {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_INTEGRITY_TEST_FAIL version fixture"
    exit 459
}
copy `"`bad_version_index'"' `"`bad_source'/hxempirical-release.index"', replace
capture noisily do `"`launcher'"' repair `"`bad_source'"'
local bad_version_rc = _rc
capture quietly checksum `"`install_target'/hxworkbench.jar"'
local version_after_rc = _rc
if `bad_version_rc' == 0 | `version_after_rc' | r(filelen) != `jar_bytes' | r(checksum) != `jar_checksum' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_INTEGRITY_TEST_FAIL unsupported index version accepted"
    exit 459
}
display as result "HX_INSTALLER_INDEX_VERSION_OK"

capture noisily do `"`launcher'"' uninstall `"`repository'"'
local uninstall_rc = _rc
sysdir set PERSONAL `"`original_personal'"'
cd `"`original_pwd'"'

capture quietly erase `"`bad_source'/hxinstaller.ado"'
capture quietly erase `"`bad_source'/hxempirical.pkg"'
capture quietly erase `"`bad_source'/hxempirical-release.index"'
capture quietly rmdir `"`bad_source'"'
capture quietly erase `"`test_personal'/profile.do"'
capture quietly erase `"`test_personal'/profile.before_hxempirical.do"'
capture quietly rmdir `"`test_personal'"'

if `uninstall_rc' {
    display as error "HX_INSTALLER_INTEGRITY_TEST_FAIL uninstall r(`uninstall_rc')"
    exit `uninstall_rc'
}
display as result "HX_INSTALLER_INTEGRITY_OK"
