version 17.0
clear all
set more off
args repository
adopath ++ `"`repository'"'
set obs 40
generate id = ceil(_n/4)
generate year = mod(_n-1,4)+2000
generate double z = cos(_n)
generate double x = z + sin(_n)*.2
generate double y = 2*x + id + cos(_n*3)
generate double precise = 1.23456789
format precise %9.2f
generate labelled = 1
label define group 1 "label text"
label values labelled group
generate day = 20000
format day %td
generate extmiss = .a
generate str20 padded = "  keep spaces  "
local cp `"`repository'/hxworkbench.jar;`c(pwd)'/hx-tests.jar"'
javacall com.hexie.stata.WorkflowRegressionTest run, args(`"`c(pwd)'/workflow"') classpath(`"`cp'"')
assert _rc == 0
display as result "HX_WORKFLOW_REGRESSION_SMOKE_OK"
