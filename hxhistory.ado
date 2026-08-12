*! hxhistory 2.0.0  09aug2026
*! History is Stata's Review window; this command does not create sidecar files.
program define hxhistory
    version 17.0
    syntax [, ADD(string asis)]
    if `"`add'"' != "" {
        /* Compatibility no-op: callers already push the actual command. */
        exit
    }
    display as text "工具箱执行的完整命令保存在 Stata 左侧 History（历史）窗口中。"
end
