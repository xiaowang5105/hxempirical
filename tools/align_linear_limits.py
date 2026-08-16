from pathlib import Path
import sys

jp = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
sp = Path('tools/verify_static_contracts.py')
java = jp.read_text(encoding='utf-8')
static = sp.read_text(encoding='utf-8')


def one(text, old, new, label):
    n = text.count(old)
    if n != 1:
        print(f'HX_LINEAR_LIMIT_ALIGN_FAIL {label}: expected 1, found {n}', file=sys.stderr)
        raise SystemExit(1)
    return text.replace(old, new)

java = one(
    java,
    'methodSubtitle = "至少设置一个界限；数字或变量名会生成 ll()/ul()，min/max 分别生成裸 ll/ul。";',
    'methodSubtitle = "界限可以留空；若设置，数字或变量名会生成 ll()/ul()，min/max 分别生成裸 ll/ul。留空前请确认模型确实不需要显式删失界限。";',
    'tobit subtitle',
)
java = one(
    java,
    'methodSubtitle = "至少设置一个截断点；可填数值或包含逐观测截断点的变量名。";',
    'methodSubtitle = "界限可以留空；若设置，可填数值或包含逐观测截断点的变量名。留空前请确认模型确实不需要显式截断点。";',
    'truncreg subtitle',
)
block = '''         if ((tobit || truncreg) && this.expression.getText().trim().isBlank() && this.newvar.getText().trim().isBlank()) {
            JOptionPane.showMessageDialog(this, command + " 至少需要设置一个 ll()/ul() 界限；无删失/截断的普通连续结果请优先使用 regress。", "界限尚未设置", 1);
            return false;
         }
'''
java = one(java, block, '', 'hard limit validation')
static = one(
    static,
    "    '至少需要设置一个 ll()/ul() 界限',\n",
    "    '界限可以留空；若设置，数字或变量名会生成 ll()/ul()',\n",
    'static limit needle',
)
marker = '''    elif needle not in java:
        fail(f"structured linear-related UI contract missing: {needle}")
'''
replacement = marker + '''if '至少需要设置一个 ll()/ul() 界限' in java:
    fail("tobit/truncreg UI must not require limits more strictly than native Stata syntax")
'''
static = one(static, marker, replacement, 'static no-hard-limit gate')

jp.write_text(java, encoding='utf-8')
sp.write_text(static, encoding='utf-8')
print('HX_LINEAR_LIMIT_ALIGN_OK')
