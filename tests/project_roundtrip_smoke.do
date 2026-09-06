version 17.0
clear all
set more off
args repository
adopath ++ `"`repository'"'
set obs 100
generate double x = _n if _n > 10
generate double z = cos(_n) if _n <= 80
generate double y = 2*_n + sin(_n)
local projectdir `"`c(pwd)'/hx-roundtrip"'
mkdir `"`projectdir'"'
local hxjar `"`repository'/hxworkbench.jar"'
javacall com.hexie.stata.HxWorkbench projectSelfTest, args(`"`projectdir'"') classpath(`"`hxjar'"')
assert _rc == 0
matrix expected = e(b)
do `"`projectdir'/replay.do"'
assert e(N) == 70
assert mreldif(e(b),expected) < 1e-12
do `"`projectdir'/common.do"'
estimates restore HX_common_M1
assert e(N) == 70
estimates restore HX_common_M2
assert e(N) == 70
display as result "HX_PROJECT_ROUNDTRIP_SMOKE_OK"
