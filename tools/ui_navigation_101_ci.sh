#!/usr/bin/env bash
set -euo pipefail

python3 tools/apply_ui_navigation_101.py

python3 - <<'PY'
from pathlib import Path
java = Path('src/main/java/com/hexie/stata/HxWorkbench.java').read_text(encoding='utf-8')
readme = Path('README.md').read_text(encoding='utf-8')
checks = {
    'version constant': 'public static final String VERSION = "1.0.1";',
    'workspace back': 'new JButton("← 上一级")',
    'chooser home': 'chooserHomeButton = new JButton("首页")',
    'clickable breadcrumb': 'private void renderBreadcrumb(JPanel bar, String path)',
    'category breadcrumb': 'openActiveCategoryFromBreadcrumb',
    'stable scrollbar': 'setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS)',
}
for label, needle in checks.items():
    if needle not in java:
        raise SystemExit(f'missing static check: {label}')
if 'breadcrumbLabel' in java or 'chooserBreadcrumb =' in java:
    raise SystemExit('legacy breadcrumb widget remains')
if '当前发布版本：**1.0.1**' not in readme or '### 1.0.1（当前版本）' not in readme:
    raise SystemExit('README 1.0.1 record missing')
print('HX_UI_NAV_STATIC_OK')
PY

rm -rf build .ci-sfi
mkdir -p .ci-sfi/com/stata/sfi build/classes build/previews

cat > .ci-sfi/com/stata/sfi/Characteristic.java <<'JAVA'
package com.stata.sfi;
public final class Characteristic { private Characteristic() {} public static String getDtaChar(String name) { return ""; } }
JAVA
cat > .ci-sfi/com/stata/sfi/Data.java <<'JAVA'
package com.stata.sfi;
public final class Data {
 private Data() {} public static long getObsTotal(){return 0L;} public static int getVarCount(){return 0;}
 public static String getVarName(int i){return "";} public static int getVarIndex(String n){return -1;}
 public static boolean isVarTypeString(int i){return false;} public static String getFormattedValue(int i,long o,boolean f){return "";}
 public static double getNum(int i,long o){return Double.NaN;} public static String getStr(int i,long o){return "";}
 public static String getVarLabel(int i){return "";} public static String getVarFormat(int i){return "";}
}
JAVA
cat > .ci-sfi/com/stata/sfi/Frame.java <<'JAVA'
package com.stata.sfi;
public class Frame {
 public static Frame connect(String n){return new Frame();} public static Frame create(String n){return new Frame();} public void drop(){}
 public long getObsTotal(){return 0L;} public int getVarCount(){return 0;} public int getVarIndex(String n){return -1;}
 public boolean isVarTypeString(int i){return false;} public String getStr(int i,long o){return "";} public double getNum(int i,long o){return Double.NaN;}
 public String getVarName(int i){return "";} public String getFormattedValue(int i,long o,boolean f){return "";}
}
JAVA
cat > .ci-sfi/com/stata/sfi/Macro.java <<'JAVA'
package com.stata.sfi; public final class Macro { private Macro(){} public static String getGlobal(String n){return "";} }
JAVA
cat > .ci-sfi/com/stata/sfi/Missing.java <<'JAVA'
package com.stata.sfi; public final class Missing { private Missing(){} public static boolean isMissing(double v){return Double.isNaN(v);} }
JAVA
cat > .ci-sfi/com/stata/sfi/SFIToolkit.java <<'JAVA'
package com.stata.sfi;
public final class SFIToolkit { private SFIToolkit(){} public static int executeCommand(String c,boolean e){return 0;} public static void errorln(String t){System.err.println(t);} public static void displayln(String t){System.out.println(t);} public static String stackTraceToString(Throwable t){return t==null?"":t.toString();} }
JAVA
cat > .ci-sfi/com/stata/sfi/Scalar.java <<'JAVA'
package com.stata.sfi; public final class Scalar { private Scalar(){} public static double getValue(String n){return Double.NaN;} }
JAVA

javac --release 11 -d build/classes $(find .ci-sfi -name '*.java' -print) src/main/java/com/hexie/stata/HxWorkbench.java
jar --create --file hxworkbench.jar -C build/classes com/hexie/stata
class_count=$(find build/classes/com/hexie/stata -name '*.class' | wc -l | tr -d ' ')
[ "$class_count" -ge 44 ]
javap -verbose -classpath hxworkbench.jar com.hexie.stata.HxWorkbench | grep -q 'major version: 55'

if ! command -v xvfb-run >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y xvfb >/dev/null
fi
for mode in --render-home-preview --render-method-preview --render-oneclick-preview --render-regress-preview; do
  name=${mode#--render-}; name=${name%-preview}; out="build/previews/${name}.png"
  xvfb-run -a java -cp build/classes com.hexie.stata.HxWorkbench "$mode" "$out"
  test -s "$out"
done

# Package metadata consistency.
grep -Fq 'd Version 1.0.1' hxempirical.pkg
grep -Fq '*! hxempirical 1.0.1  12aug2026' hxempirical.ado
grep -Fq 'return local version "1.0.1"' hxempirical.ado
grep -Fq '{* *! version 1.0.1  12aug2026}{...}' hxempirical.sthlp
awk '$1=="f" {print $2}' hxempirical.pkg | while read -r file; do test -f "$file" || { echo "missing package file: $file"; exit 1; }; done

rm -rf build .ci-sfi
echo "HX_UI_NAV_1_0_1_BUILD_OK classes=$class_count"
