#!/usr/bin/env bash
set -euo pipefail

rm -rf build .ci-sfi
mkdir -p .ci-sfi/com/stata/sfi build/classes build/previews

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

grep -Fq '请选择因变量。' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq 'this.flag("has_weight")' src/main/java/com/hexie/stata/HxWorkbench.java

javac --release 11 -d build/classes $(find .ci-sfi -name '*.java' -print) src/main/java/com/hexie/stata/HxWorkbench.java
jar --create --file hxworkbench.jar -C build/classes com/hexie/stata

class_count=$(find build/classes/com/hexie/stata -name '*.class' | wc -l | tr -d ' ')
test "$class_count" = "44"
javap -verbose -classpath hxworkbench.jar com.hexie.stata.HxWorkbench | grep -q 'major version: 55'

if ! command -v xvfb-run >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y xvfb >/dev/null
fi

xvfb-run -a java -cp build/classes com.hexie.stata.HxWorkbench --render-preview build/previews/generic-command.png
xvfb-run -a java -cp build/classes com.hexie.stata.HxWorkbench --render-regress-preview build/previews/regress.png

test -s build/previews/generic-command.png
test -s build/previews/regress.png

echo "HX_FOCUSED_VALIDATION_BUILD_OK classes=$class_count"
