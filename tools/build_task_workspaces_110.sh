#!/usr/bin/env bash
set -euo pipefail

python3 -m py_compile tools/patch_task_workspaces_110.py
python3 tools/patch_task_workspaces_110.py

# Architecture checks.
grep -Fq 'public static final String VERSION = "1.1.0";' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq 'homeLauncherButton("基准回归", "xtreg · 可切换估计方法"' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq 'private final JComboBox<String> baselineEstimator' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq 'this.openBaselineRegressionWorkspace()' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq 'private void updateBaselinePreview()' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq 'case "时间序列线性回归":' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq 'return "linear_ts";' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq '选择一个命令进入参数设置；详细说明放在命令页面中。' src/main/java/com/hexie/stata/HxWorkbench.java
if grep -Fq '展开全部功能' src/main/java/com/hexie/stata/HxWorkbench.java; then
  echo 'Homepage expand/collapse UI still present' >&2
  exit 1
fi
if grep -Fq '<b>适合：</b>' src/main/java/com/hexie/stata/HxWorkbench.java; then
  echo 'Large chooser tutorial card content still present' >&2
  exit 1
fi
grep -Fq 'd Version 1.1.0' hxempirical.pkg
grep -Fq '**当前发布版本：1.1.0**' README.md
grep -Fq '2026-08-12 19:14（UTC+8）' README.md

# Compile against lightweight Stata SFI stubs under Java 11.
rm -rf build .ci-sfi
mkdir -p .ci-sfi/com/stata/sfi build/classes
cat > .ci-sfi/com/stata/sfi/Characteristic.java <<'JAVA'
package com.stata.sfi;
public final class Characteristic { private Characteristic() {} public static String getDtaChar(String name) { return ""; } }
JAVA
cat > .ci-sfi/com/stata/sfi/Data.java <<'JAVA'
package com.stata.sfi;
public final class Data {
 private Data() {}
 public static long getObsTotal(){return 0L;} public static int getVarCount(){return 0;}
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
package com.stata.sfi; public final class SFIToolkit { private SFIToolkit(){} public static int executeCommand(String c, boolean e){return 0;} public static void errorln(String t){System.err.println(t);} public static void displayln(String t){System.out.println(t);} public static String stackTraceToString(Throwable t){return t==null?"":t.toString();} }
JAVA
cat > .ci-sfi/com/stata/sfi/Scalar.java <<'JAVA'
package com.stata.sfi; public final class Scalar { private Scalar(){} public static double getValue(String n){return Double.NaN;} }
JAVA

javac --release 11 -d build/classes $(find .ci-sfi -name '*.java' -print) src/main/java/com/hexie/stata/HxWorkbench.java
jar --create --file hxworkbench.jar -C build/classes com/hexie/stata
javap -verbose -classpath hxworkbench.jar com.hexie.stata.HxWorkbench | grep -q 'major version: 55'
class_count=$(find build/classes/com/hexie/stata -name '*.class' | wc -l | tr -d ' ')
[ "$class_count" -ge 40 ]

# UI smoke tests: stable home, compact chooser, baseline workspace.
xvfb-run -a java -cp build/classes com.hexie.stata.HxWorkbench --render-home-preview /tmp/hx-home-110.png
xvfb-run -a java -cp build/classes com.hexie.stata.HxWorkbench --render-method-preview /tmp/hx-method-110.png
xvfb-run -a java -cp build/classes com.hexie.stata.HxWorkbench --render-regress-preview /tmp/hx-baseline-110.png
[ -s /tmp/hx-home-110.png ]
[ -s /tmp/hx-method-110.png ]
[ -s /tmp/hx-baseline-110.png ]

echo "HX_TASK_WORKSPACES_110_BUILD_OK classes=$class_count"
rm -rf build .ci-sfi
