from pathlib import Path

# Normalize small source-text differences so the release patch can stay strict
# and fail loudly on any unexpected structural change.
p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')
old = '{"工具变量", "ivregress / ivreghdfe", "reg", "工具变量"}'
if old in s:
    s = s.replace(old, '{"工具变量", "内生变量与工具变量", "reg", "工具变量"}', 1)
old_block = '''            "专题与图形",
            new String[][]{
               {"DID", "双重差分与事件研究", "methodcategory", "did"},
               {"OneClick", "控制变量组合", "methodcategory", "oneclick"},
               {"数据图形", "分布、散点与拟合", "graph", "数据分布"},
               {"回归结果图", "系数与边际效应", "graph", "回归结果"}
            },
            true'''
new_block = '''            "专题与图形",
            new String[][]{
               {"DID", "双重差分与事件研究", "methodcategory", "did"},
               {"OneClick", "控制变量组合与稳健性", "methodcategory", "oneclick"},
               {"数据图形", "分布、散点与趋势", "graph", "数据分布"},
               {"回归结果图", "系数图与边际效应", "graph", "回归结果"}
            },
            true'''
if old_block in s:
    s = s.replace(old_block, new_block, 1)
p.write_text(s, encoding='utf-8')

reg_path = Path('hxregistry.ado')
reg = reg_path.read_text(encoding='utf-8')
old_key = '    local key_ivregress "ivregress iv 工具变量 2sls liml gmm 内生性"'
expected_key = '    local key_ivregress "ivregress iv 2sls gmm liml 工具变量 内生性"'
if old_key in reg:
    reg = reg.replace(old_key, expected_key, 1)
reg_path.write_text(reg, encoding='utf-8')

help_path = Path('hxempirical.sthlp')
help_text = help_path.read_text(encoding='utf-8')
anchor = '{pstd}\nThe built-in linear-regression catalog also exposes'
normalized = 'Command settings use structured variables.\n\n{pstd}\nThe built-in linear-regression catalog also exposes'
if anchor in help_text and normalized not in help_text:
    help_text = help_text.replace(anchor, normalized, 1)
help_path.write_text(help_text, encoding='utf-8')

print('HX_PREPATCH_HOME_103_OK')
