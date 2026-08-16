from pathlib import Path
import re


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


def scope(text: str, start_sig: str, end_sig: str) -> tuple[int, int, str]:
    a = text.find(start_sig)
    b = text.find(end_sig, a + 1)
    if a < 0 or b < 0:
        raise SystemExit(f"scope missing: {start_sig} -> {end_sig}")
    return a, b, text[a:b]


def replace_summary(sc: str, method: str, summary: str) -> str:
    pat = re.compile(rf'((?:if|else if) \("{re.escape(method)}"\.equals\(var0\)\) \{{\s*\n\s*)return "[^"]*";')
    sc2, n = pat.subn(rf'\1return "{summary}";', sc, count=1)
    if n != 1:
        raise SystemExit(f"summary patch failed: {method} count={n}")
    return sc2


def replace_preview(sc: str, method: str, preview: str) -> str:
    pat = re.compile(rf'case "{re.escape(method)}": return "[^"]*";')
    sc2, n = pat.subn(f'case "{method}": return "{preview}";', sc, count=1)
    if n != 1:
        raise SystemExit(f"preview patch failed: {method} count={n}")
    return sc2

jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")

# Public/home shortcuts must enter the native Data workflow. Keep hxconvert reachable only through HX Workflow.
old_excel = 'excel.addActionListener(e -> this.navigateTo("data", "导入与转换", "hxconvert"));'
excel_count = j.count(old_excel)
if excel_count < 2:
    raise SystemExit(f"expected two Excel/CSV hxconvert buttons, got {excel_count}")
j = j.replace(old_excel, 'excel.addActionListener(e -> this.openCommandPage("import"));')

old_var8 = 'var8.addActionListener(var1x -> this.navigateTo("data", "导入与转换", "hxconvert"));'
var8_count = j.count(old_var8)
if var8_count != 1:
    raise SystemExit(f"expected one compact import hxconvert button, got {var8_count}")
j = j.replace(old_var8, 'var8.addActionListener(var1x -> this.openCommandPage("import"));', 1)

old_route = '() -> this.navigateTo("data", "导入与转换", "hxconvert")'
route_count = j.count(old_route)
if route_count < 4:
    raise SystemExit(f"expected multiple stale native-data shortcuts, got {route_count}")
j = j.replace(old_route, '() -> this.browseMethod("data", "导入与转换")')

old_router = 'this.navigateTo("data", "导入与转换", "hxconvert");'
router_count = j.count(old_router)
if router_count != 1:
    raise SystemExit(f"expected one natural-language hxconvert route, got {router_count}")
j = j.replace(old_router, 'this.browseMethod("data", "导入与转换");', 1)

# Method-card command previews should reflect the actual current Registry routes.
a, b, data_prev = scope(j, "      private static String dataMethodPreview(String method)", "      private static String genericMethodPreview(String category, String method)")
preview_map = {
    "导入与转换": "use · import · export · save",
    "数据检查": "describe · codebook · isid · assert · duplicates",
    "变量处理": "generate · egen · recode · rename · encode",
    "样本处理": "keep · drop · expand",
    "合并与追加": "merge · append · joinby · frlink / frget",
    "数据结构": "reshape · collapse · contract · xtset / tsset · frame",
}
for method, preview in preview_map.items():
    data_prev = replace_preview(data_prev, method, preview)
j = j[:a] + data_prev + j[b:]

# Method summaries explain tasks rather than the old HX-converter-centric implementation.
a, b, summaries = scope(j, "      private static String methodSummary(String var0)", "      private static String methodRecommendation(String var0)")
summary_map = {
    "导入与转换": "打开、导入、导出和保存 Stata 或外部数据",
    "数据检查": "检查结构、编码、唯一键、约束、缺失和重复",
    "变量处理": "生成、重编码、重命名、标签、格式与类型转换",
    "样本处理": "筛选、删除或按规则扩展观测",
    "合并与追加": "按键合并、纵向追加、组合或跨 Frame 连接数据",
    "数据结构": "宽长转换、汇总、重组、排序并声明面板或时间结构",
}
for method, text in summary_map.items():
    summaries = replace_summary(summaries, method, text)
j = j[:a] + summaries + j[b:]

jp.write_text(j, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'if \'"内生协变量", "样本选择模型"\' in java:\n    fail("duplicate sample-selection method remains in Java public Statistics navigation")\n'
checks = '''if 'navigateTo("data", "导入与转换", "hxconvert")' in java:
    fail("public Java Data shortcuts must not bypass native Data I/O for hxconvert")
for data_entry_contract in (
    'case "导入与转换": return "use · import · export · save";',
    'case "数据检查": return "describe · codebook · isid · assert · duplicates";',
    'case "变量处理": return "generate · egen · recode · rename · encode";',
    'openCommandPage("import")',
    'browseMethod("data", "导入与转换")',
):
    if data_entry_contract not in java:
        fail(f"native Data entrypoint/card parity missing: {data_entry_contract}")
if 'return "打开、导入、导出和保存 Stata 或外部数据";' not in java:
    fail("Data import/export method summary still reflects the old HX converter")
'''
v = once(v, anchor, anchor + checks, "native Data entrypoint contracts")
vp.write_text(v, encoding="utf-8", newline="\n")
print(f"HX_NATIVE_DATA_ENTRYPOINT_PATCH_OK tiles={route_count} excel={excel_count} compact={var8_count} router={router_count}")
