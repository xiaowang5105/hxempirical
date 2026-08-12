#!/usr/bin/env bash
set -euo pipefail

python3 -m py_compile tools/patch_native_did_103.py
python3 tools/patch_native_did_103.py

# Static architecture checks.
grep -Fq 'public static final String VERSION = "1.0.3";' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq 'homeLauncherButton("双重差分", "didregress / xtdidregress"' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq 'this.browseMethod("reg", "双重差分")' src/main/java/com/hexie/stata/HxWorkbench.java
if grep -Fq 'new HxWorkbench.Category("DID 专区", "did")' src/main/java/com/hexie/stata/HxWorkbench.java; then
  echo 'Visible DID category still present' >&2
  exit 1
fi
grep -Fq 'local reg_methods "线性模型 面板模型 二元结果 计数模型 工具变量 双重差分"' hxregistry.ado
grep -Fq 'local view "didregress xtdidregress"' hxregistry.ado
grep -Fq 'local template "didregress"' hxsemantics.ado
grep -Fq 'group(`absorb' hxpreview.ado
grep -Fq 'd Version 1.0.3' hxempirical.pkg

# Compile with lightweight Stata SFI stubs under Java 11.
rm -rf build .ci-sfi
mkdir -p .ci-sfi/com/stata/sfi build/classes

cat > .ci-sfi/com/stata/sfi/Characteristic.java <<'JAVA'
package com.stata.sfi;
public final class Characteristic {
   private Characteristic() {}
   public static String getDtaChar(String name) { return ""; }
}
JAVA

cat > .ci-sfi/com/stata/sfi/Data.java <<'JAVA'
package com.stata.sfi;
public final class Data {
   private Data() {}
   public static long getObsTotal() { return 0L; }
   public static int getVarCount() { return 0; }
   public static String getVarName(int index) { return ""; }
   public static int getVarIndex(String name) { return -1; }
   public static boolean isVarTypeString(int index) { return false; }
   public static String getFormattedValue(int index, long obs, boolean formatted) { return ""; }
   public static double getNum(int index, long obs) { return Double.NaN; }
   public static String getStr(int index, long obs) { return ""; }
   public static String getVarLabel(int index) { return ""; }
   public static String getVarFormat(int index) { return ""; }
}
JAVA

cat > .ci-sfi/com/stata/sfi/Frame.java <<'JAVA'
package com.stata.sfi;
public class Frame {
   public static Frame connect(String name) { return new Frame(); }
   public static Frame create(String name) { return new Frame(); }
   public void drop() {}
   public long getObsTotal() { return 0L; }
   public int getVarCount() { return 0; }
   public int getVarIndex(String name) { return -1; }
   public boolean isVarTypeString(int index) { return false; }
   public String getStr(int index, long obs) { return ""; }
   public double getNum(int index, long obs) { return Double.NaN; }
   public String getVarName(int index) { return ""; }
   public String getFormattedValue(int index, long obs, boolean formatted) { return ""; }
}
JAVA

cat > .ci-sfi/com/stata/sfi/Macro.java <<'JAVA'
package com.stata.sfi;
public final class Macro {
   private Macro() {}
   public static String getGlobal(String name) { return ""; }
}
JAVA

cat > .ci-sfi/com/stata/sfi/Missing.java <<'JAVA'
package com.stata.sfi;
public final class Missing {
   private Missing() {}
   public static boolean isMissing(double value) { return Double.isNaN(value); }
}
JAVA

cat > .ci-sfi/com/stata/sfi/SFIToolkit.java <<'JAVA'
package com.stata.sfi;
public final class SFIToolkit {
   private SFIToolkit() {}
   public static int executeCommand(String command, boolean echo) { return 0; }
   public static void errorln(String text) { System.err.println(text); }
   public static void displayln(String text) { System.out.println(text); }
   public static String stackTraceToString(Throwable t) { return t == null ? "" : t.toString(); }
}
JAVA

cat > .ci-sfi/com/stata/sfi/Scalar.java <<'JAVA'
package com.stata.sfi;
public final class Scalar {
   private Scalar() {}
   public static double getValue(String name) { return Double.NaN; }
}
JAVA

javac --release 11 -d build/classes $(find .ci-sfi -name '*.java' -print) src/main/java/com/hexie/stata/HxWorkbench.java
jar --create --file hxworkbench.jar -C build/classes com/hexie/stata
javap -verbose -classpath hxworkbench.jar com.hexie.stata.HxWorkbench | grep -q 'major version: 55'
class_count=$(find build/classes/com/hexie/stata -name '*.class' | wc -l | tr -d ' ')
[ "$class_count" -ge 40 ]

# Headless UI smoke tests. Xvfb is preinstalled on GitHub Ubuntu images.
xvfb-run -a java -cp build/classes com.hexie.stata.HxWorkbench --render-home-preview /tmp/hx-home.png
xvfb-run -a java -cp build/classes com.hexie.stata.HxWorkbench --render-method-preview /tmp/hx-method.png
[ -s /tmp/hx-home.png ]
[ -s /tmp/hx-method.png ]

# Final source checks after compilation.
grep -Fq 'didregress' README.md
grep -Fq 'xtdidregress' README.md
grep -Fq 'package version 1.0.3' hxempirical.sthlp

echo "HX_NATIVE_DID_103_BUILD_OK classes=$class_count"
rm -rf build .ci-sfi
