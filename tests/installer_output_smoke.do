version 17.0
clear all
set more off

/* Verify that the public do-file no longer echoes the installer core source. */
args repository
if `"`repository'"' == "" local repository `"`c(pwd)'"'
local repository : subinstr local repository "\" "/", all
local installer `"`repository'/hxinstall.do"'

local original_personal `"`c(sysdir_personal)'"'
local original_pwd `"`c(pwd)'"'
tempfile output_base output_log
local test_personal `"`output_base'_personal"'
sysdir set PERSONAL `"`test_personal'/"'
cd `"`c(tmpdir)'"'

capture log close hxoutput
log using `"`output_log'"', text replace name(hxoutput)
capture noisily do `"`installer'"' auto `"`repository'"'
local install_rc = _rc
log close hxoutput
if `install_rc' {
    sysdir set PERSONAL `"`original_personal'"'
    cd `"`original_pwd'"'
    display as error "HX_INSTALLER_OUTPUT_TEST_FAIL install r(`install_rc')"
    exit `install_rc'
}

tempfile filtered_manifest filtered_parts filtered_result
quietly filefilter `"`output_log'"' `"`filtered_manifest'"', ///
    from("Read the release manifest") to("HX_LEAKED_MANIFEST") replace
local leaked_manifest = r(occurrences)
quietly filefilter `"`output_log'"' `"`filtered_parts'"', ///
    from("foreach part of local parts") to("HX_LEAKED_PARTS") replace
local leaked_parts = r(occurrences)
quietly filefilter `"`output_log'"' `"`filtered_result'"', ///
    from("hxempirical 安装完成") to("HX_VISIBLE_RESULT") replace
local saw_result = (r(occurrences) > 0)
local leaked_core = (`leaked_manifest' > 0 | `leaked_parts' > 0)

capture noisily do `"`installer'"' uninstall `"`repository'"'
local uninstall_rc = _rc
sysdir set PERSONAL `"`original_personal'"'
cd `"`original_pwd'"'
capture quietly erase `"`test_personal'/profile.do"'
capture quietly erase `"`test_personal'/profile.before_hxempirical.do"'
capture quietly rmdir `"`test_personal'"'

if `leaked_core' {
    display as error "HX_INSTALLER_OUTPUT_TEST_FAIL installer core source was echoed"
    exit 459
}
if !`saw_result' {
    display as error "HX_INSTALLER_OUTPUT_TEST_FAIL final result was not visible"
    exit 459
}
if `uninstall_rc' {
    display as error "HX_INSTALLER_OUTPUT_TEST_FAIL uninstall r(`uninstall_rc')"
    exit `uninstall_rc'
}
display as result "HX_INSTALLER_OUTPUT_OK"
