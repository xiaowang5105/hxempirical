{smcl}
{* *! version 1.4.9  14aug2026}{...}
{vieweralsosee "hxtoolbox" "help hxtoolbox"}{...}
{title:Title}

{phang}
{bf:hxempirical} {hline 2} open and manage the HX empirical workbench

{title:Syntax}

{p 8 16 2}{cmd:hxempirical} [{cmd:, classic}]
{p 8 16 2}{cmd:hxempirical about}
{p 8 16 2}{cmd:hxempirical doctor}
{p 8 16 2}{cmd:hxempirical menu}
{p 8 16 2}{cmd:hxempirical menu persist}
{p 8 16 2}{cmd:hxempirical menu remove}
{p 8 16 2}{cmd:hxempirical install} {it:command}
{p 8 16 2}{cmd:hxempirical update}
{p 8 16 2}{cmd:hxempirical uninstall}

{title:Description}

{pstd}
{cmd:hxempirical} opens one desktop-style workbench with a fixed left sidebar,
task-oriented pages, live command preview, and a read-only view of the dataset
currently in Stata memory. Commands run in Stata itself. The complete command is
added to Stata's History window before execution.

{pstd}
The 1.4.9 interface uses a stable desktop-workbench layout: a collapsible left
navigation sidebar, a task-focused main workspace, and one shared right-side
Current Data inspector. OneClick and ordinary command pages reuse that same
inspector instead of maintaining separate look-alike data/result panels.

{pstd}
Research tasks can open a task workspace directly. The baseline-regression
workspace defaults to {cmd:xtreg} and uses a compact estimator selector to switch
between {cmd:xtreg}, {cmd:reghdfe}, {cmd:areg}, and {cmd:regress} without leaving
the page. Y, the core X, controls, sample restrictions, and other common settings
are preserved while estimator-specific fields and the real Stata command update.

{pstd}
When a method still needs a command chooser, the chooser is a compact directory:
it shows only the command name, Chinese title, one-line purpose, and source tag.
Detailed examples and limitations are kept in the command page. Breadcrumbs,
{bf:上一级}, {bf:首页}, and command help use fixed positions.

{pstd}
The right side has three stable tabs: {bf:数据}, {bf:结果}, and {bf:日志}.
The content inside {bf:结果} changes with the active task. Missing-value,
conversion, graph, DID, and OneClick pages therefore expose only their relevant
outputs instead of a permanent row of unrelated tabs.

{pstd}
The workbench uses one resolver/parser/schema/renderer pipeline for official and
community-contributed commands. Syntax, help, examples, ado source, and an
official dialog are used when available. Unresolved syntax remains available in
the advanced-options field.


{title:Ordinary linear regression workspace}

{pstd}
The start page is task-first and keeps only six common jobs visible. A large
search field accepts command names, analysis keywords, and short task phrases;
common multi-concept requests such as enterprise-and-year fixed effects or
control-variable robustness are routed to the relevant method. The page also
shows the current Stata dataset status. {bf:继续工作} stores the last three model
specifications locally and restores their parameters without automatically
running them. Methods
that contain only one command open that command directly, avoiding an extra
chooser click. The full regression category remains available under
{bf:回归模型}; it separates ordinary OLS, fixed-effects linear regression, robust
and special linear regression, quantile regression, time-series linear
regression, panel models, binary outcomes, count models, and instrumental
variables.

{pstd}
{bf:回归模型 > 普通线性回归 > regress} uses a dedicated workspace rather than
a generic syntax form. It separates the dependent variable Y, the core
explanatory variable X, and control variables. Beginner-facing builders add
categorical terms, interactions, and lags without requiring users to type
{cmd:i.}, {cmd:c.}, {cmd:##}, or {cmd:L.}. The page also exposes
{cmd:if}/{cmd:in}, f/a/p/i weights, conventional/robust/clustered standard
errors, {cmd:noconstant}, standardized {cmd:beta}, and the confidence level
while keeping free-form Stata syntax in an advanced section. The
right inspector can be hidden so the settings workspace can use the full width.

{pstd}
After a successful {cmd:regress}, the {bf:结果} tab groups common official
postestimation actions by purpose: {cmd:estat vif}, {cmd:estat hettest},
{cmd:estat imtest, white}, {cmd:estat ovtest}, {cmd:estat ic}, fitted values,
residuals, standardized and studentized residuals, Cook's distance, leverage,
and coefficient tests. These buttons execute native Stata commands through a
guarded runner and write those native commands to History. When the fitted
{cmd:regress} used robust or clustered VCE, the workbench disables influence
statistics that Stata only provides with the default OLS VCE; fitted values and
ordinary residuals remain available. For a no-constant model, the VIF action
automatically uses {cmd:estat vif, uncentered}.

Command settings use structured variables. The regression catalog also includes Stata 17+ official DID commands: {cmd:didregress} for repeated cross-sectional data and {cmd:xtdidregress} for panel/longitudinal data. The old custom DID section is no longer shown as a separate public workflow.

{pstd}
The built-in linear-regression catalog also exposes {cmd:areg}, {cmd:rreg},
{cmd:cnsreg}, {cmd:vwls}, {cmd:eivreg}, {cmd:qreg}, {cmd:newey}, and
{cmd:prais}; {cmd:reghdfe} remains an optional community command. The
{cmd:newey}/{cmd:prais} pages link directly to a beginner-facing {cmd:tsset}
page instead of showing misleading panel-only fields. Other Stata commands can
still be opened by typing their command name in search, where the resolver
builds a page from the installed command's syntax and help.

{title:Command dock and run monitor}

{pstd}
The command-settings page ends with a fixed command dock; low-frequency options remain in the normal scroll flow instead of an expand/collapse section. It shows the complete
editable Stata command in a monospaced field, provides one primary run action,
and reports the current run state and elapsed time without scrolling away.

{pstd}
The right-side {bf:日志} tab records the command, start and end times,
elapsed time, Stata return code, History-write status, processor status, data
shape before and after the run, and available estimation results such as
{cmd:e(N)} and {cmd:e(r2)}. The {bf:日志} tab keeps the timestamped execution log and run queue visible in
one fixed scrollable view; there is no expand/collapse details control. Ordinary
Stata estimation commands use an indeterminate progress state because their
internal percentage is unavailable. Batch file conversion
uses the actual number of completed files and displays a real percentage.

{title:Installation}

{pstd}
Run the maintained installer from GitHub Pages:

{phang2}{cmd:. do "https://xiaowang5105.github.io/hxempirical/hxinstall.do"}

{pstd}
Then open it with

{phang2}{cmd:. hxempirical}

{pstd}
Opening {cmd:hxempirical} never edits PERSONAL/profile.do. During the current
Stata session it can add exactly one visible entry:

{phang2}{bf:User > 我的实证工具箱}

{pstd}
Use {cmd:hxempirical menu} for a session-only menu entry. If the user explicitly
wants the entry at every Stata startup, run {cmd:hxempirical menu persist}.
That command adds one HX-managed block to profile.do while preserving all
unrelated lines. Remove only that managed block with
{cmd:hxempirical menu remove}. hxempirical never uses {cmd:window menu clear}.

{title:Missing-value analysis}

{pstd}
Open {bf:数据 > 数据检查 > 缺失值分析}. The page supports all or selected
variables, one-way grouping, joint grouping, separate summaries for multiple
group variables, missing-count/rate filters, record drill-down, and four graph
views. It reads the complete current dataset and does not modify it. The native
{cmd:misstable summarize} check is written to Stata History.

{title:Convert files to DTA}

{pstd}
Open {bf:数据 > 导入与转换 > 转换为 DTA}. Select an Excel, CSV, TXT, or
TSV file and the page adapts its settings to the detected format. A read-only
preview reports observations, variables, inferred types, empty columns, mixed
numeric/text columns, duplicate headers, and columns that may lose leading
zeroes. For CSV/TXT, UTF-8, GB18030, and Windows-1252 are supported; automatic
mode probes the file before import and writes the resolved encoding into the
actual {cmd:import delimited} command. Potential code columns such as 000001 are
kept as strings by default. For legacy {cmd:.xls}, hxempirical does not invent a
{cmd:Sheet1} name when the workbook sheet list cannot be inspected; leaving the
sheet field at {bf:(默认工作表)} lets Stata use its default sheet.

{pstd}
Single-file mode asks before replacing an existing DTA. Batch mode converts a
folder of selected file types, can skip existing outputs, and reports every
success, failure, and skipped file. Batch read settings are frozen when the run
starts, so changing the UI cannot silently change later files. A {bf:停止批量任务}
button stops before the next file and keeps all files already completed. Imports
and saves run in a temporary Stata frame, leaving the dataset already in memory
unchanged unless {bf:load after conversion} is selected. The source
Excel/CSV/TXT file is never modified. The actual {cmd:import} and {cmd:save}
commands are written to Stata History.

{title:Optional commands}

{pstd}
{cmd:reghdfe}, {cmd:winsor2}, {cmd:ivreghdfe}, {cmd:ppmlhdfe},
{cmd:oneclick}, {cmd:oneclick_robustness}, {cmd:coefplot}, and {cmd:event_plot} are optional.
The package checks for optional commands only when needed. Commands with a
verified SSC source (including {cmd:oneclick} and {cmd:event_plot}) can be
installed after user confirmation. {cmd:oneclick_robustness} is detected when
present but is not downloaded from an unverified source. Nothing is downloaded
merely by installing {cmd:hxempirical}.

{phang2}{cmd:. hxempirical doctor}
{phang2}{cmd:. hxempirical install reghdfe}

{title:Compatibility}

{pstd}
Minimum version: Stata 17. The Java workbench is compiled for Java 11 bytecode
and uses Stata's bundled Java/SFI interface. It contains no COM Automation,
native C plugin, drive-letter path, or platform-specific font. If Java cannot
start, {cmd:hxempirical, classic} opens the included Stata dialog.

{title:Update and uninstall}

{phang2}{cmd:. hxempirical update}
{phang2}{cmd:. hxempirical uninstall}

{pstd}
The maintained installer writes its file manifest into PERSONAL, retries
transient downloads, stages all files before replacement, and restores the
previous installation if a write fails. Uninstall also removes the managed
startup-menu block when present. Restart Stata after an update or uninstall so
the loaded Java class is released.

{title:Examples}

{phang2}{cmd:. sysuse auto, clear}
{phang2}{cmd:. hxempirical}
{phang2}{cmd:. hxempirical about}
{phang2}{cmd:. hxempirical doctor}

{title:Graphs and OneClick}

{pstd}
The {bf:图形} category provides distribution, relationship, grouped-trend,
postestimation, and DID/event-study graph building blocks. The right-side graph
preview updates with selected variables; the final graph is still produced by
Stata's native graph system and the complete command is retained in History.

{pstd}
Difference-in-differences is now exposed through Stata's official commands rather than a separate HX DID workflow. Use {cmd:didregress} for repeated cross-sectional data and {cmd:xtdidregress} for panel/longitudinal data. For panel data, declare the panel structure first with {cmd:xtset}. The workbench generates the native command, for example {cmd:didregress (y x1 x2) (treat), group(group) time(year)}. After estimation, Stata's official DID postestimation tools such as {cmd:estat trendplots}, {cmd:estat ptrends}, and {cmd:estat granger} remain available in Stata.

{pstd}
The {bf:OneClick 专区} calls the author's real external {cmd:oneclick} command;
hxempirical does not substitute its own control-combination algorithm. The GUI
translates Y, focal X, candidate controls, significance level, estimator, fixed
effects, and standard-error choices into the external command syntax. The exact
{cmd:oneclick ...} line displayed in the command dock is the line submitted to
Stata and written to History.

{pstd}
After the external command finishes, hxempirical reads the generated
{cmd:subset.dta} into a temporary uniquely named frame and displays it under Results. The
external command is run inside a unique temporary working directory, so a user
file named {cmd:subset.dta} in the active project directory is never renamed,
erased, or overwritten. The dataset already in Stata memory is not replaced. A selected result row can be sent to
the corresponding ordinary regression page for review without automatic
execution. {cmd:oneclick} can be installed from SSC on request.
{cmd:oneclick_robustness} is also treated as an external command; hxempirical
does not invent an unverified download source for it.

{pstd}
OneClick output is a model-sensitivity and robustness aid. Candidate controls
should be chosen from theory, prior literature, and the identification design.
It does not replace a prespecified main model or causal identification strategy.

{title:Author}

{pstd}
HX empirical workbench, package version 1.2.7.
