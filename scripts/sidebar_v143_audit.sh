#!/usr/bin/env bash
set -euo pipefail

python3 scripts/sidebar_v143.py

rm -rf /tmp/sfi /tmp/classes
mkdir -p /tmp/sfi/com/stata/sfi /tmp/classes
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
package com.stata.sfi; public class Data { static final String[] N={"firm","year","y","x1","x2","Size","Lev","ROA"}; public static long getObsTotal(){return 20;} public static int getVarCount(){return N.length;} public static String getVarName(int i){return i>0&&i<=N.length?N[i-1]:"";} public static String getVarLabel(int i){return i>0&&i<=N.length?"label_"+N[i-1]:"";} public static String getVarFormat(int i){return "%9.0g";} public static int getVarIndex(String s){for(int i=0;i<N.length;i++)if(N[i].equals(s))return i+1;return -1;} public static boolean isVarTypeString(int i){return false;} public static double getNum(int i,long j){return i*100+j;} public static String getStr(int i,long j){return "";} public static String getFormattedValue(int i,long j){return String.valueOf(getNum(i,j));} public static String getFormattedValue(int i,long j,boolean b){return getFormattedValue(i,j);} public static void storeNum(int i,long j,double d){} public static void storeStr(int i,long j,String s){} }
EOF
cat > /tmp/sfi/com/stata/sfi/Frame.java <<'EOF'
package com.stata.sfi; public class Frame { public static Frame create(String s){return new Frame();} public static Frame connect(String s){return new Frame();} public void drop(){} public long getObsTotal(){return 0;} public int getVarCount(){return 0;} public String getVarName(int i){return "";} public String getVarLabel(int i){return "";} public int getVarIndex(String s){return -1;} public boolean isVarTypeString(int i){return false;} public double getNum(int i,long j){return Double.NaN;} public String getStr(int i,long j){return "";} public String getFormattedValue(int i,long j){return "";} public String getFormattedValue(int i,long j,boolean b){return "";} }
EOF

javac --release 11 -d /tmp/classes /tmp/sfi/com/stata/sfi/*.java src/main/java/com/hexie/stata/HxWorkbench.java
jar cf hxworkbench.jar -C /tmp/classes com/hexie/stata
test -s hxworkbench.jar

cat > /tmp/SidebarAudit.java <<'EOF'
import java.awt.*; import java.lang.reflect.*; import javax.swing.*;
public class SidebarAudit { static Class<?> C; static JFrame F; static Throwable E; static Field f(String n)throws Exception{Field x=C.getDeclaredField(n);x.setAccessible(true);return x;} static void lay(Container c){c.doLayout();for(Component x:c.getComponents())if(x instanceof Container)lay((Container)x);} static void ck(boolean v,String s){if(!v)throw new AssertionError(s);} static void edt(Runnable r)throws Exception{SwingUtilities.invokeAndWait(()->{try{r.run();}catch(Throwable t){E=t;}});if(E!=null){Throwable t=E;E=null;throw new RuntimeException(t);}} public static void main(String[] a){try{run();System.out.println("SIDEBAR_AUDIT_OK");System.exit(0);}catch(Throwable t){t.printStackTrace();System.exit(2);}} static void run()throws Exception{C=Class.forName("com.hexie.stata.HxWorkbench$WorkbenchFrame");Constructor<?> ct=C.getDeclaredConstructor(boolean.class);ct.setAccessible(true);edt(()->{try{F=(JFrame)ct.newInstance(true);F.setSize(1672,901);F.addNotify();F.validate();lay(F.getContentPane());}catch(Exception e){throw new RuntimeException(e);}});JPanel side=(JPanel)f("sidebarPanel").get(F);JButton toggle=(JButton)f("sidebarToggleButton").get(F);JSplitPane cmd=(JSplitPane)f("commandDataSplit").get(F);edt(()->{ck(side.isVisible(),"sidebar should start visible");ck(side.getWidth()>=190,"expanded sidebar too narrow "+side.getWidth());ck(toggle.isVisible()&&toggle.getWidth()>20,"toggle missing");ck("☰".equals(toggle.getText()),"toggle icon wrong");});final int[] before={0};edt(()->{before[0]=cmd.getWidth();toggle.doClick();F.validate();lay(F.getContentPane());});edt(()->{F.validate();lay(F.getContentPane());ck(!side.isVisible(),"sidebar did not hide");ck(side.getPreferredSize().width==0,"hidden sidebar still reserves width");ck(toggle.isVisible(),"toggle disappeared with sidebar");ck(cmd.getWidth()>before[0]+150,"content did not gain sidebar width "+before[0]+"->"+cmd.getWidth());});edt(()->{toggle.doClick();F.validate();lay(F.getContentPane());ck(side.isVisible(),"sidebar did not reopen");ck(side.getPreferredSize().width==205,"sidebar width not restored");ck(toggle.isVisible(),"toggle missing after reopen");F.dispose();});} }
EOF
javac --release 11 -cp /tmp/classes -d /tmp/classes /tmp/SidebarAudit.java
timeout 45s xvfb-run -a java -cp /tmp/classes SidebarAudit

grep -q 'VERSION = "1.4.3"' src/main/java/com/hexie/stata/HxWorkbench.java
grep -q 'setVisible(!this.sidebarCollapsed)' src/main/java/com/hexie/stata/HxWorkbench.java
grep -q '^\*! hxempirical 1.4.3' hxempirical.ado
grep -q '^d Version 1.4.3$' hxempirical.pkg
for mode in preview home regress monitor-details oneclick graph did; do
  if [ "$mode" = preview ]; then arg=--render-preview; else arg=--render-${mode}-preview; fi
  xvfb-run -a java -cp /tmp/classes com.hexie.stata.HxWorkbench "$arg" /tmp/$mode.png
  test -s /tmp/$mode.png
done

echo SIDEBAR_V143_ALL_OK
