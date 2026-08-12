#!/usr/bin/env bash
set -euo pipefail

python3 -m py_compile tools/complete_command_layer.py

# Static production checks after the refactor script has run.
grep -Fq '*! hxregistry 2.9.0' hxregistry.ado
grep -Fq '*! hxsemantics 1.4.0' hxsemantics.ado
grep -Fq '*! hxpreview 1.3.0' hxpreview.ado
grep -Fq 'local graph_methods "数据分布 变量关系 回归结果"' hxregistry.ado
grep -Fq 'local absorb_label "分组变量 by()（可多选；不分组可留空）"' hxsemantics.ado
grep -Fq 'local opt `"`opt'"'"' by(`absorb'"'"')"'"'' hxpreview.ado
grep -Fq 'local opt `"`opt'"'"' quantile(`expression'"'"')"'"'' hxpreview.ado
grep -Fq 'local opt `"`opt'"'"' constraints(`expression'"'"')"'"'' hxpreview.ado
grep -Fq 'local opt `"`opt'"'"' reliab(`expression'"'"')"'"'' hxpreview.ado
grep -Fq 'local opt `"`opt'"'"' lag(`expression'"'"')"'"'' hxpreview.ado
grep -Fq 'private boolean validateOrdinaryCommandBeforeRun()' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq 'this.sem("panel_label")' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq '"rreg", "cnsreg", "vwls", "eivreg", "newey", "prais"' src/main/java/com/hexie/stata/HxWorkbench.java
grep -Fq 'Arrays.asList("reshape", "collapse", "xtset", "tsset")' src/main/java/com/hexie/stata/HxWorkbench.java

# Audit current ordinary command catalog and ensure every catalog command has a known
# command path or an intentional dynamic/search/workflow path.
python3 - <<'PY'
from pathlib import Path
import re
reg = Path('hxregistry.ado').read_text(encoding='utf-8')
java = Path('src/main/java/com/hexie/stata/HxWorkbench.java').read_text(encoding='utf-8')
sem = Path('hxsemantics.ado').read_text(encoding='utf-8')
for local in ['data_cmds','stats_cmds','reg_cmds','post_cmds','graph_cmds']:
    m = re.search(rf'local {local} "([^"]+)"', reg)
    assert m, local
    commands = m.group(1).split()
    for cmd in commands:
        # hxconvert and graph_box are intentional workbench aliases; all other ordinary
        # catalog commands must occur in either explicit semantics or Java command paths.
        if cmd in {'hxconvert','graph_box','twoway'}:
            continue
        if cmd not in sem and cmd not in java:
            raise SystemExit(f'catalog command missing from semantics/java coverage: {cmd}')
print('HX_CATALOG_COVERAGE_OK')
PY

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

javac --release 11 -d build/classes $(find .ci-sfi -name '*.java' -print) src/main/java/com/hexie/stata/HxWorkbench.java
jar --create --file hxworkbench.jar -C build/classes com/hexie/stata

class_count=$(find build/classes/com/hexie/stata -name '*.class' | wc -l | tr -d ' ')
test "$class_count" = "44"
javap -verbose -classpath hxworkbench.jar com.hexie.stata.HxWorkbench | grep -q 'major version: 55'

if ! command -v xvfb-run >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y xvfb >/dev/null
fi

modes=(
  --render-preview
  --render-missing-preview
  --render-missing-results-preview
  --render-convert-preview
  --render-home-preview
  --render-method-preview
  --render-correlation-preview
  --render-workflow-preview
  --render-cluster-preview
  --render-monitor-preview
  --render-monitor-details-preview
  --render-graph-preview
  --render-did-preview
  --render-did-encode-preview
  --render-did-event-preview
  --render-did-pretrend-preview
  --render-oneclick-preview
  --render-oneclick-results-preview
  --render-regress-preview
)

for mode in "${modes[@]}"; do
  name=${mode#--render-}
  name=${name%-preview}
  out="build/previews/${name}.png"
  xvfb-run -a java -cp build/classes com.hexie.stata.HxWorkbench "$mode" "$out"
  test -s "$out"
done

# No transient build products should be committed by the workflow.
rm -rf build .ci-sfi tools/__pycache__

echo "HX_COMPLETE_COMMAND_LAYER_BUILD_OK classes=$class_count previews=${#modes[@]}"
