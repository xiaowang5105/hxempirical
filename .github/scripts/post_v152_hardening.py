from pathlib import Path

# Make uninstall wording location-neutral now that a managed install can live in PLUS/h.
p = Path('hxinstaller.ado')
s = p.read_text(encoding='utf-8')
s = s.replace('noisily display as result _newline "hxempirical 的 PERSONAL 安装已卸载。"', "noisily display as result _newline \"hxempirical 的受管安装已卸载（`target_kind'）。\"", 1)
p.write_text(s, encoding='utf-8')

# Permanent CI compiles the Java source against a small SFI surface stub in addition
# to checking release/package integrity. UI rendering stays in the release audit.
Path('.github/workflows/ci.yml').write_text(r'''name: HX release consistency

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Verify managed release
        run: python tools/verify_release.py

      - name: Create Stata SFI compile stubs
        run: |
          mkdir -p /tmp/sfi/com/stata/sfi /tmp/hxclasses
          cat >/tmp/sfi/com/stata/sfi/SFIToolkit.java <<'EOF'
          package com.stata.sfi;
          public class SFIToolkit {
            public static int executeCommand(String s, boolean b){return 0;}
            public static void displayln(String s){}
            public static void errorln(String s){}
            public static String stackTraceToString(Throwable t){return t==null?"":t.toString();}
          }
          EOF
          cat >/tmp/sfi/com/stata/sfi/Characteristic.java <<'EOF'
          package com.stata.sfi;
          public class Characteristic { public static String getDtaChar(String s){return "";} }
          EOF
          cat >/tmp/sfi/com/stata/sfi/Macro.java <<'EOF'
          package com.stata.sfi;
          public class Macro { public static String getGlobal(String s){return "";} }
          EOF
          cat >/tmp/sfi/com/stata/sfi/Missing.java <<'EOF'
          package com.stata.sfi;
          public class Missing { public static boolean isMissing(double v){return Double.isNaN(v);} }
          EOF
          cat >/tmp/sfi/com/stata/sfi/Scalar.java <<'EOF'
          package com.stata.sfi;
          public class Scalar { public static double getValue(String s){return Double.NaN;} }
          EOF
          cat >/tmp/sfi/com/stata/sfi/Data.java <<'EOF'
          package com.stata.sfi;
          public class Data {
            public static long getObsTotal(){return 0L;}
            public static int getVarCount(){return 0;}
            public static int getVarIndex(String s){return 0;}
            public static String getVarName(int i){return "";}
            public static String getVarLabel(int i){return "";}
            public static String getVarFormat(int i){return "";}
            public static boolean isVarTypeString(int i){return false;}
            public static double getNum(int i,long j){return Double.NaN;}
            public static String getStr(int i,long j){return "";}
            public static String getFormattedValue(int i,long j,boolean b){return "";}
          }
          EOF
          cat >/tmp/sfi/com/stata/sfi/Frame.java <<'EOF'
          package com.stata.sfi;
          public class Frame {
            public static Frame connect(String s){return new Frame();}
            public static Frame create(String s){return new Frame();}
            public void drop(){}
            public long getObsTotal(){return 0L;}
            public int getVarCount(){return 0;}
            public int getVarIndex(String s){return 0;}
            public String getVarName(int i){return "";}
            public boolean isVarTypeString(int i){return false;}
            public double getNum(int i,long j){return Double.NaN;}
            public String getStr(int i,long j){return "";}
            public String getFormattedValue(int i,long j,boolean b){return "";}
          }
          EOF

      - name: Compile Java 11
        run: javac --release 11 -Xmaxerrs 200 -d /tmp/hxclasses /tmp/sfi/com/stata/sfi/*.java src/main/java/com/hexie/stata/HxWorkbench.java

      - name: Check shipped JAR Java level
        run: |
          python - <<'PY'
          import struct, zipfile
          with zipfile.ZipFile('hxworkbench.jar') as z:
              classes=[n for n in z.namelist() if n.endswith('.class')]
              assert classes, 'jar contains no class files'
              majors=set()
              for name in classes:
                  magic, minor, major=struct.unpack('>IHH',z.read(name)[:8])
                  assert magic == 0xCAFEBABE
                  majors.add(major)
              assert max(majors) <= 55, f'Java class level too new: {sorted(majors)}'
              print('HX_JAR_LEVEL_OK', sorted(majors))
          PY
''', encoding='utf-8')

print('POST_V152_OK')
