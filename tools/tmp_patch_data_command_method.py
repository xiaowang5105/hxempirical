from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")
old = '''      private static String commandMethod(String var0) {
         if ("hxconvert".equals(var0)) {
            return "数据处理|导入与转换";
         } else if (Arrays.asList("缺失值分析", "duplicates", "misstable").contains(var0)) {
            return "数据处理|数据检查";
         } else if (Arrays.asList("generate", "replace", "encode", "decode", "destring", "tostring", "winsor2").contains(var0)) {
            return "数据处理|变量处理";
         } else if (Arrays.asList("keep", "drop").contains(var0)) {
            return "数据处理|样本处理";
         } else if (Arrays.asList("merge", "append").contains(var0)) {
            return "数据处理|合并与追加";
         } else if (Arrays.asList("reshape", "collapse", "xtset", "tsset").contains(var0)) {
            return "数据处理|数据结构";
         } else if (Arrays.asList("summarize", "tabstat").contains(var0)) {
'''
new = '''      private static String commandMethod(String var0) {
         if ("hxconvert".equals(var0)) {
            return "HX Workflow|数据转换";
         } else if (Arrays.asList("use", "import", "export", "save").contains(var0)) {
            return "数据处理|导入与转换";
         } else if (Arrays.asList("缺失值分析", "describe", "codebook", "isid", "assert", "count", "compare", "duplicates", "misstable").contains(var0)) {
            return "数据处理|数据检查";
         } else if (Arrays.asList("generate", "egen", "replace", "recode", "clonevar", "split", "rename", "order", "label", "format", "compress", "encode", "decode", "destring", "tostring", "winsor2").contains(var0)) {
            return "数据处理|变量处理";
         } else if (Arrays.asList("keep", "drop", "expand").contains(var0)) {
            return "数据处理|样本处理";
         } else if (Arrays.asList("merge", "append", "joinby", "cross", "frlink", "frget").contains(var0)) {
            return "数据处理|合并与追加";
         } else if (Arrays.asList("reshape", "collapse", "contract", "fillin", "stack", "xpose", "sort", "gsort", "xtset", "tsset", "frame", "frames").contains(var0)) {
            return "数据处理|数据结构";
         } else if (Arrays.asList("summarize", "tabstat").contains(var0)) {
'''
j = once(j, old, new, "Data commandMethod prefix")
jp.write_text(j, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''if 'return "打开、导入、导出和保存 Stata 或外部数据";' not in java:
    fail("Data import/export method summary still reflects the old HX converter")
'''
checks = '''if 'return "HX Workflow|数据转换";' not in java:
    fail("hxconvert command path must be labeled as HX Workflow")
for data_method_contract in (
    'Arrays.asList("use", "import", "export", "save").contains(var0)',
    'Arrays.asList("缺失值分析", "describe", "codebook", "isid", "assert", "count", "compare", "duplicates", "misstable").contains(var0)',
    'Arrays.asList("generate", "egen", "replace", "recode", "clonevar", "split", "rename", "order", "label", "format", "compress", "encode", "decode", "destring", "tostring", "winsor2").contains(var0)',
    'Arrays.asList("keep", "drop", "expand").contains(var0)',
    'Arrays.asList("merge", "append", "joinby", "cross", "frlink", "frget").contains(var0)',
    'Arrays.asList("reshape", "collapse", "contract", "fillin", "stack", "xpose", "sort", "gsort", "xtset", "tsset", "frame", "frames").contains(var0)',
):
    if data_method_contract not in java:
        fail(f"Java Data commandMethod parity missing: {data_method_contract}")
'''
v = once(v, anchor, anchor + checks, "Data commandMethod static contracts")
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_DATA_COMMAND_METHOD_PATCH_OK")
