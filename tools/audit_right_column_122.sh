#!/usr/bin/env bash
set -euo pipefail
python3 -m py_compile tools/right_column_122.py
python3 tools/right_column_122.py

grep -Fq 'public static final String VERSION = "1.2.2";' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq 'private final JLabel rightPaneTitle = new JLabel("当前数据");' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq 'this.dataTabs.addTab("日志", this.buildRunMonitorPanel());' src/main/java/com/hexie/stata/HxWorkbench.java
! grep -Fq '推荐流程' src/main/java/com/hexie/stata/HxWorkbench.java || true
! grep -Fq '详细运行信息  +' src/main/java/com/hexie/stata/HxWorkbench.java || true

rm -rf build .ci-sfi
mkdir -p .ci-sfi/com/stata/sfi build/classes build/previews
cat > .ci-sfi/com/stata/sfi/Characteristic.java <<'JAVA'
package com.stata.sfi; public final class Characteristic { private Characteristic(){} public static String getDtaChar(String n){return "";} }
JAVA
cat > .ci-sfi/com/stata/sfi/Data.java <<'JAVA'
package com.stata.sfi; public final class Data { private Data(){} public static long getObsTotal(){return 0L;} public static int getVarCount(){return 0;} public static String getVarName(int i){return "";} public static int getVarIndex(String n){return -1;} public static boolean isVarTypeString(int i){return false;} public static String getFormattedValue(int i,long o,boolean f){return "";} public static double getNum(int i,long o){return Double.NaN;} public static String getStr(int i,long o){return "";} public static String getVarLabel(int i){return "";} public static String getVarFormat(int i){return "";} }
JAVA
cat > .ci-sfi/com/stata/sfi/Frame.java <<'JAVA'
package com.stata.sfi; public class Frame { public static Frame connect(String n){return new Frame();} public static Frame create(String n){return new Frame();} public void drop(){} public long getObsTotal(){return 0L;} public int getVarCount(){return 0;} public int getVarIndex(String n){return -1;} public boolean isVarTypeString(int i){return false;} public String getStr(int i,long o){return "";} public double getNum(int i,long o){return Double.NaN;} public String getVarName(int i){return "";} public String getFormattedValue(int i,long o,boolean f){return "";} }
JAVA
cat > .ci-sfi/com/stata/sfi/Macro.java <<'JAVA'
package com.stata.sfi; public final class Macro { private Macro(){} public static String getGlobal(String n){return "";} }
JAVA
cat > .ci-sfi/com/stata/sfi/Missing.java <<'JAVA'
package com.stata.sfi; public final class Missing { private Missing(){} public static boolean isMissing(double v){return Double.isNaN(v);} }
JAVA
cat > .ci-sfi/com/stata/sfi/SFIToolkit.java <<'JAVA'
package com.stata.sfi; public final class SFIToolkit { private SFIToolkit(){} public static int executeCommand(String c,boolean e){return 0;} public static void errorln(String t){System.err.println(t);} public static void displayln(String t){System.out.println(t);} public static String stackTraceToString(Throwable t){return t==null?"":t.toString();} }
JAVA
cat > .ci-sfi/com/stata/sfi/Scalar.java <<'JAVA'
package com.stata.sfi; public final class Scalar { private Scalar(){} public static double getValue(String n){return Double.NaN;} }
JAVA
javac --release 11 -d build/classes $(find .ci-sfi -name '*.java' -print) src/main/java/com/hexie/stata/HxWorkbench.java
jar --create --file hxworkbench.jar -C build/classes com/hexie/stata
javap -verbose -classpath hxworkbench.jar com.hexie.stata.HxWorkbench | grep -q 'major version: 55'

xvfb-run -a java -cp build/classes com.hexie.stata.HxWorkbench --render-oneclick-preview build/previews/oneclick.png
xvfb-run -a java -cp build/classes com.hexie.stata.HxWorkbench --render-monitor-preview build/previews/monitor.png
xvfb-run -a java -cp build/classes com.hexie.stata.HxWorkbench --render-monitor-details-preview build/previews/log.png
xvfb-run -a java -cp build/classes com.hexie.stata.HxWorkbench --render-regress-preview build/previews/regress.png
for f in oneclick monitor log regress; do test -s build/previews/$f.png; done
python3 - <<'PY'
import struct
for f in ['oneclick.png','monitor.png','log.png','regress.png']:
    with open('build/previews/'+f,'rb') as h:
        sig=h.read(24)
    assert sig[:8] == b'\x89PNG\r\n\x1a\n'
    w,hgt=struct.unpack('>II',sig[16:24])
    assert (w,hgt)==(1672,901),(f,w,hgt)
print('HX_RIGHT_COLUMN_122_RENDER_SIZE_OK')
PY

echo HX_RIGHT_COLUMN_122_BUILD_OK
rm -rf .ci-sfi
