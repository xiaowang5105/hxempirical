#!/usr/bin/env bash
set -euo pipefail

python3 scripts/sidebar_v144_selfcheck.py

rm -rf /tmp/sfi /tmp/classes
mkdir -p /tmp/sfi/com/stata/sfi /tmp/classes audit
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

cat > /tmp/SidebarV144Audit.java <<'EOF'
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.lang.reflect.*;
import javax.imageio.ImageIO;
import javax.swing.*;

public class SidebarV144Audit {
  static Class<?> C; static JFrame F; static Throwable E;
  static Field f(String n)throws Exception{Field x=C.getDeclaredField(n);x.setAccessible(true);return x;}
  static void lay(Container c){c.doLayout();for(Component x:c.getComponents())if(x instanceof Container)lay((Container)x);}
  static void ck(boolean v,String s){if(!v)throw new AssertionError(s);}
  static void edt(Runnable r)throws Exception{SwingUtilities.invokeAndWait(()->{try{r.run();}catch(Throwable t){E=t;}});if(E!=null){Throwable t=E;E=null;throw new RuntimeException(t);}}
  static Point at(Component c){return SwingUtilities.convertPoint(c,0,0,F.getContentPane());}
  static void shot(String path)throws Exception{BufferedImage im=new BufferedImage(F.getContentPane().getWidth(),F.getContentPane().getHeight(),BufferedImage.TYPE_INT_ARGB);Graphics2D g=im.createGraphics();F.getContentPane().paintAll(g);g.dispose();ImageIO.write(im,"png",new File(path));}
  public static void main(String[] a){try{run();System.out.println("SIDEBAR_V144_AUDIT_OK");System.exit(0);}catch(Throwable t){t.printStackTrace();System.exit(2);}}
  static void run()throws Exception{
    C=Class.forName("com.hexie.stata.HxWorkbench$WorkbenchFrame"); Constructor<?> ct=C.getDeclaredConstructor(boolean.class); ct.setAccessible(true);
    edt(()->{try{F=(JFrame)ct.newInstance(true);F.setSize(1672,901);F.setVisible(true);F.validate();lay(F.getContentPane());}catch(Exception e){throw new RuntimeException(e);}});
    JPanel side=(JPanel)f("sidebarPanel").get(F); JButton toggle=(JButton)f("sidebarToggleButton").get(F); JPanel stages=(JPanel)f("stageCards").get(F); JSplitPane cmd=(JSplitPane)f("commandDataSplit").get(F);
    final int[] toggleX={0}, stageW={0};
    edt(()->{
      F.validate();lay(F.getContentPane());
      ck(side.isVisible(),"sidebar should start visible");
      ck(side.getWidth()>=200 && side.getWidth()<=210,"expanded width wrong: "+side.getWidth());
      ck(toggle.isVisible()&&toggle.getWidth()>=36,"toggle missing");
      ck("☰".equals(toggle.getText()),"toggle icon changed");
      Point tp=at(toggle), sp=at(side), gp=at(stages);
      ck(tp.x<=20,"toggle should stay at far-left, x="+tp.x);
      ck(sp.x==0,"sidebar should start at far-left, x="+sp.x);
      ck(sp.y>=40,"sidebar should sit below global toggle row, y="+sp.y);
      ck(gp.x>=200,"content should start after expanded sidebar, x="+gp.x);
      ck(gp.y>=40,"content should sit below toggle row, y="+gp.y);
      toggleX[0]=tp.x; stageW[0]=stages.getWidth();
      try{shot("audit/sidebar-expanded.png");}catch(Exception e){throw new RuntimeException(e);}
    });
    edt(()->{toggle.doClick();F.validate();lay(F.getContentPane());});
    edt(()->{
      F.validate();lay(F.getContentPane());
      ck(!side.isVisible(),"sidebar did not fully hide");
      ck(side.getPreferredSize().width==0,"hidden sidebar reserves preferred width");
      Point tp=at(toggle), gp=at(stages);
      ck(Math.abs(tp.x-toggleX[0])<=2,"toggle moved when sidebar closed: "+toggleX[0]+" -> "+tp.x);
      ck(gp.x<=2,"content did not reclaim left edge, x="+gp.x);
      ck(stages.getWidth()>stageW[0]+180,"content did not reclaim sidebar width: "+stageW[0]+" -> "+stages.getWidth());
      try{shot("audit/sidebar-collapsed.png");}catch(Exception e){throw new RuntimeException(e);}
    });
    edt(()->{toggle.doClick();F.validate();lay(F.getContentPane());ck(side.isVisible(),"sidebar did not reopen");ck(side.getPreferredSize().width==205,"sidebar width not restored");ck(at(toggle).x<=20,"toggle not far-left after reopen");F.dispose();});
  }
}
EOF

javac --release 11 -cp /tmp/classes -d /tmp/classes /tmp/SidebarV144Audit.java
timeout 45s xvfb-run -a java -cp /tmp/classes SidebarV144Audit

grep -q 'VERSION = "1.4.4"' src/main/java/com/hexie/stata/HxWorkbench.java
grep -q 'shell.add(this.buildSidebarToggleBar(), BorderLayout.NORTH);' src/main/java/com/hexie/stata/HxWorkbench.java
! grep -q 'center.add(this.buildSidebarToggleBar(), BorderLayout.NORTH);' src/main/java/com/hexie/stata/HxWorkbench.java
grep -q 'collapsible left' hxempirical.sthlp
grep -q '^\*! hxempirical 1.4.4' hxempirical.ado
grep -q '^d Version 1.4.4$' hxempirical.pkg

for mode in preview home regress monitor-details oneclick graph did; do
  if [ "$mode" = preview ]; then arg=--render-preview; else arg=--render-${mode}-preview; fi
  xvfb-run -a java -cp /tmp/classes com.hexie.stata.HxWorkbench "$arg" "audit/${mode}.png"
  test -s "audit/${mode}.png"
done

echo SIDEBAR_V144_ALL_OK
