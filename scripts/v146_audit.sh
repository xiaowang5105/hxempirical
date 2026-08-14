#!/usr/bin/env bash
set -euo pipefail
python3 scripts/v146_patch.py

rm -rf /tmp/sfi /tmp/classes audit-v146
mkdir -p /tmp/sfi/com/stata/sfi /tmp/classes audit-v146
cat > /tmp/sfi/com/stata/sfi/SFIToolkit.java <<'EOF'
package com.stata.sfi; public class SFIToolkit { public static int executeCommand(String s, boolean b){return 0;} public static void errorln(String s){} public static void displayln(String s){} public static String stackTraceToString(Throwable t){return "";} }
EOF
cat > /tmp/sfi/com/stata/sfi/Characteristic.java <<'EOF'
package com.stata.sfi; public class Characteristic { public static String getDtaChar(String s){return "";} public static void setDtaChar(String s,String v){} }
EOF
cat > /tmp/sfi/com/stata/sfi/Macro.java <<'EOF'
package com.stata.sfi; public class Macro { public static String getGlobal(String s){return "";} public static String getLocal(String s){return "";} public static void setGlobal(String s,String v){} public static void setLocal(String s,String v){} }
EOF
cat > /tmp/sfi/com/stata/sfi/Missing.java <<'EOF'
package com.stata.sfi; public class Missing { public static boolean isMissing(double d){return Double.isNaN(d);} }
EOF
cat > /tmp/sfi/com/stata/sfi/Scalar.java <<'EOF'
package com.stata.sfi; public class Scalar { public static double getValue(String s){return Double.NaN;} }
EOF
cat > /tmp/sfi/com/stata/sfi/Data.java <<'EOF'
package com.stata.sfi; public class Data { static final String[] N={"make","price","mpg","rep78","headroom","trunk","weight","length","turn","displacement","gear_ratio","foreign"}; public static long getObsTotal(){return 74;} public static int getVarCount(){return N.length;} public static String getVarName(int i){return i>0&&i<=N.length?N[i-1]:"";} public static String getVarLabel(int i){return i>0&&i<=N.length?"label_"+N[i-1]:"";} public static String getVarFormat(int i){return "%9.0g";} public static int getVarIndex(String s){for(int i=0;i<N.length;i++)if(N[i].equals(s))return i+1;return -1;} public static boolean isVarTypeString(int i){return i==1;} public static double getNum(int i,long j){return i*100+j;} public static String getStr(int i,long j){return "car"+j;} public static String getFormattedValue(int i,long j){return isVarTypeString(i)?getStr(i,j):String.valueOf(getNum(i,j));} public static String getFormattedValue(int i,long j,boolean b){return getFormattedValue(i,j);} public static void storeNum(int i,long j,double d){} public static void storeStr(int i,long j,String s){} }
EOF
cat > /tmp/sfi/com/stata/sfi/Frame.java <<'EOF'
package com.stata.sfi; public class Frame { public static Frame create(String s){return new Frame();} public static Frame connect(String s){return new Frame();} public void drop(){} public long getObsTotal(){return 0;} public int getVarCount(){return 0;} public String getVarName(int i){return "";} public String getVarLabel(int i){return "";} public int getVarIndex(String s){return -1;} public boolean isVarTypeString(int i){return false;} public double getNum(int i,long j){return Double.NaN;} public String getStr(int i,long j){return "";} public String getFormattedValue(int i,long j){return "";} public String getFormattedValue(int i,long j,boolean b){return "";} }
EOF

javac --release 11 -d /tmp/classes /tmp/sfi/com/stata/sfi/*.java src/main/java/com/hexie/stata/HxWorkbench.java
jar cf hxworkbench.jar -C /tmp/classes com/hexie/stata
test -s hxworkbench.jar

cat > /tmp/V146Audit.java <<'EOF'
import java.awt.*; import java.lang.reflect.*; import java.util.*; import javax.swing.*;
public class V146Audit {
 static Class<?> C; static JFrame F; static Throwable E;
 static Field f(String n)throws Exception{Field x=C.getDeclaredField(n);x.setAccessible(true);return x;}
 static Method m(String n)throws Exception{Method x=C.getDeclaredMethod(n);x.setAccessible(true);return x;}
 static void lay(Container c){c.doLayout();for(Component x:c.getComponents())if(x instanceof Container)lay((Container)x);}
 static void ck(boolean v,String s){if(!v)throw new AssertionError(s);}
 static void edt(Runnable r)throws Exception{SwingUtilities.invokeAndWait(()->{try{r.run();}catch(Throwable t){E=t;}});if(E!=null){Throwable t=E;E=null;throw new RuntimeException(t);}}
 static String sel(JComboBox<?> c){return Objects.toString(c.getSelectedItem(),"");}
 static boolean listHas(JList<?> l,String v){return l.getSelectedValuesList().stream().anyMatch(x->v.equals(String.valueOf(x)));}
 public static void main(String[] z){try{run();System.out.println("V146_AUDIT_OK");System.exit(0);}catch(Throwable t){t.printStackTrace();System.exit(2);}}
 static void run()throws Exception{
   C=Class.forName("com.hexie.stata.HxWorkbench$WorkbenchFrame"); Constructor<?> ct=C.getDeclaredConstructor(boolean.class);ct.setAccessible(true);
   edt(()->{try{F=(JFrame)ct.newInstance(true);F.setSize(1672,901);F.addNotify();Method show=C.getDeclaredMethod("showXtregWizardPageV130");show.setAccessible(true);show.invoke(F);F.validate();lay(F.getContentPane());Method ap=C.getDeclaredMethod("applyDividerRatios");ap.setAccessible(true);ap.invoke(F);}catch(Exception e){throw new RuntimeException(e);}});
   edt(()->{F.validate();lay(F.getContentPane());});
   JTextArea cmd=(JTextArea)f("xtregCommandPreview").get(F); JComboBox<?> panel=(JComboBox<?>)f("xtregPanelVar").get(F); JComboBox<?> time=(JComboBox<?>)f("xtregTimeVar").get(F); JComboBox<?> dep=(JComboBox<?>)f("xtregDepVar").get(F); JList<?> xs=(JList<?>)f("xtregIndepList").get(F); JRadioButton fe=(JRadioButton)f("xtregFeButton").get(F); JRadioButton re=(JRadioButton)f("xtregReButton").get(F); JComboBox<?> se=(JComboBox<?>)f("xtregSeCombo").get(F); Method sync=m("syncXtregControlsFromCommand");
   edt(()->{try{cmd.setText("xtset rep78 turn\nxtreg price mpg weight, re vce(robust)");sync.invoke(F);}catch(Exception e){throw new RuntimeException(e);}});
   edt(()->{ck("rep78".equals(sel(panel)),"simple panel sync");ck("turn".equals(sel(time)),"simple time sync");ck("price".equals(sel(dep)),"simple y sync");ck(listHas(xs,"mpg")&&listHas(xs,"weight"),"simple x sync");ck(re.isSelected(),"simple re sync");ck("稳健标准误".equals(sel(se)),"simple robust sync");});

   // Omitting the second xtset variable must clear stale time state.
   edt(()->{try{cmd.setText("xtset rep78\nxtreg price mpg, fe");sync.invoke(F);}catch(Exception e){throw new RuntimeException(e);}});
   edt(()->{ck("rep78".equals(sel(panel)),"panel after one-var xtset");ck(sel(time).isBlank(),"stale time variable not cleared: "+sel(time));});

   // Prefix + factor/TS/interaction + continuation + explicit cluster + unknown option.
   edt(()->{try{cmd.setText("xtset rep78 turn\nquietly xtreg price i.foreign L.weight c.mpg##c.weight ///\n    , re vce(cluster foreign) noconstant");sync.invoke(F);}catch(Exception e){throw new RuntimeException(e);}});
   edt(()->{
      ck(re.isSelected(),"prefixed RE not selected"); ck("按面板聚类".equals(sel(se)),"cluster mode not selected");
      ck(listHas(xs,"foreign")&&listHas(xs,"weight")&&listHas(xs,"mpg"),"factor/TS bases not reflected in X list: "+xs.getSelectedValuesList());
      try{ck("foreign".equals(String.valueOf(f("xtregClusterVar").get(F))),"cluster variable not preserved");ck((Boolean)f("xtregPreserveCustomX").get(F),"custom X mode not preserved");ck(String.valueOf(f("xtregExtraOptions").get(F)).contains("noconstant"),"extra option missing");ck(String.valueOf(f("xtregCommandPrefix").get(F)).toLowerCase().contains("quietly"),"prefix missing");}catch(Exception e){throw new RuntimeException(e);}
   });

   // A later UI change must not silently destroy the manual X syntax, cluster variable or extra option.
   edt(()->fe.doClick());
   edt(()->{String t=cmd.getText();ck(t.contains("i.foreign")&&t.contains("L.weight")&&t.contains("c.mpg##c.weight"),"custom X syntax destroyed: "+t);ck(t.contains("vce(cluster foreign)"),"manual cluster changed: "+t);ck(t.contains("noconstant"),"extra option lost: "+t);ck(t.toLowerCase().contains("quietly xtreg"),"prefix lost: "+t);ck(fe.isSelected(),"FE click failed");});

   // Explicitly changing SE away from cluster should hand control back to the UI; choosing cluster again defaults to panel ID.
   edt(()->se.setSelectedItem("稳健标准误"));
   edt(()->{String t=cmd.getText();ck(t.contains("vce(robust)"),"robust UI change failed");ck(!t.contains("vce(cluster foreign)"),"stale manual cluster survived explicit SE change");ck(t.contains("noconstant"),"extra option lost after SE change");});
   edt(()->se.setSelectedItem("按面板聚类"));
   edt(()->{String t=cmd.getText();ck(t.contains("vce(cluster rep78)"),"UI cluster should default to current panel ID: "+t);});

   // capture/noisily prefixes are parseable and continuation is collapsed.
   edt(()->{try{cmd.setText("xtset rep78 turn\ncapture noisily xtreg price mpg ///\n weight, re");sync.invoke(F);}catch(Exception e){throw new RuntimeException(e);}});
   edt(()->{ck(re.isSelected(),"capture/noisily RE sync failed");ck(listHas(xs,"mpg")&&listHas(xs,"weight"),"continuation X sync failed");});

   // Source-level guard: running no longer depends on literal JList X selections and uses editable command extraction.
   F.dispose();
 }
}
EOF
javac --release 11 -cp /tmp/classes -d /tmp/classes /tmp/V146Audit.java
timeout 45s xvfb-run -a java -cp /tmp/classes V146Audit

xvfb-run -a java -cp /tmp/classes com.hexie.stata.HxWorkbench --render-preview audit-v146/xtreg.png
test -s audit-v146/xtreg.png
xvfb-run -a java -cp /tmp/classes com.hexie.stata.HxWorkbench --render-home-preview audit-v146/home.png
test -s audit-v146/home.png
xvfb-run -a java -cp /tmp/classes com.hexie.stata.HxWorkbench --render-regress-preview audit-v146/regress.png
test -s audit-v146/regress.png

grep -q 'VERSION = "1.4.6"' src/main/java/com/hexie/stata/HxWorkbench.java
grep -q 'extractXtregCommands(commandPreview.getText())' src/main/java/com/hexie/stata/HxWorkbench.java
! grep -q 'pv.isBlank() || y.isBlank() || xs.isEmpty()' src/main/java/com/hexie/stata/HxWorkbench.java
grep -q 'xtregPreserveCustomX' src/main/java/com/hexie/stata/HxWorkbench.java
grep -q '^d Version 1.4.6$' hxempirical.pkg
echo V146_ALL_OK
