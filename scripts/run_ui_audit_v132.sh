#!/usr/bin/env bash
set -euo pipefail

mkdir -p /tmp/sfi/com/stata/sfi /tmp/classes
cat > /tmp/sfi/com/stata/sfi/SFIToolkit.java <<'EOF'
package com.stata.sfi;
public class SFIToolkit {
  public static int executeCommand(String s, boolean b){return 0;}
  public static void errorln(String s){}
  public static void displayln(String s){}
  public static String stackTraceToString(Throwable t){return "";}
}
EOF
cat > /tmp/sfi/com/stata/sfi/Characteristic.java <<'EOF'
package com.stata.sfi;
public class Characteristic { public static String getDtaChar(String s){return "";} }
EOF
cat > /tmp/sfi/com/stata/sfi/Macro.java <<'EOF'
package com.stata.sfi;
public class Macro {
  public static String getGlobal(String s){return "";}
  public static String getLocal(String s){return "";}
  public static void setGlobal(String s,String v){}
  public static void setLocal(String s,String v){}
}
EOF
cat > /tmp/sfi/com/stata/sfi/Missing.java <<'EOF'
package com.stata.sfi;
public class Missing { public static boolean isMissing(double d){return Double.isNaN(d);} }
EOF
cat > /tmp/sfi/com/stata/sfi/Scalar.java <<'EOF'
package com.stata.sfi;
public class Scalar { public static double getValue(String s){return Double.NaN;} }
EOF
cat > /tmp/sfi/com/stata/sfi/Data.java <<'EOF'
package com.stata.sfi;
public class Data {
  public static long getObsTotal(){return 0L;}
  public static int getVarCount(){return 0;}
  public static String getVarName(int i){return "";}
  public static String getVarLabel(int i){return "";}
  public static String getVarFormat(int i){return "";}
  public static int getVarIndex(String s){return -1;}
  public static boolean isVarTypeString(int i){return false;}
  public static double getNum(int i,long j){return Double.NaN;}
  public static String getStr(int i,long j){return "";}
  public static String getFormattedValue(int i,long j){return "";}
  public static String getFormattedValue(int i,long j,boolean b){return "";}
  public static void storeNum(int i,long j,double d){}
  public static void storeStr(int i,long j,String s){}
}
EOF
cat > /tmp/sfi/com/stata/sfi/Frame.java <<'EOF'
package com.stata.sfi;
public class Frame {
  public static Frame create(String s){return new Frame();}
  public static Frame connect(String s){return new Frame();}
  public void drop(){}
  public long getObsTotal(){return 0L;}
  public int getVarCount(){return 0;}
  public String getVarName(int i){return "";}
  public int getVarIndex(String s){return -1;}
  public boolean isVarTypeString(int i){return false;}
  public double getNum(int i,long j){return Double.NaN;}
  public String getStr(int i,long j){return "";}
  public String getFormattedValue(int i,long j){return "";}
  public String getFormattedValue(int i,long j,boolean b){return "";}
}
EOF

javac --release 11 -d /tmp/classes /tmp/sfi/com/stata/sfi/*.java src/main/java/com/hexie/stata/HxWorkbench.java
jar cf hxworkbench.jar -C /tmp/classes com/hexie/stata
test -s hxworkbench.jar

cat > /tmp/UiAuditHarness.java <<'EOF'
import java.awt.*;
import java.awt.datatransfer.StringSelection;
import java.awt.image.BufferedImage;
import java.io.File;
import java.lang.reflect.*;
import java.util.Map;
import javax.imageio.ImageIO;
import javax.swing.*;

public class UiAuditHarness {
  static Field field(Class<?> c, String name) throws Exception {
    Field f = c.getDeclaredField(name); f.setAccessible(true); return f;
  }
  static Method method(Class<?> c, String name, Class<?>... args) throws Exception {
    Method m = c.getDeclaredMethod(name, args); m.setAccessible(true); return m;
  }
  static void layoutTree(Container c) {
    c.doLayout();
    for (Component x : c.getComponents()) if (x instanceof Container) layoutTree((Container)x);
  }
  static void render(JFrame f, String path) throws Exception {
    Container c = f.getContentPane(); layoutTree(c);
    BufferedImage img = new BufferedImage(c.getWidth(), c.getHeight(), BufferedImage.TYPE_INT_RGB);
    Graphics2D g = img.createGraphics(); c.printAll(g); g.dispose(); ImageIO.write(img, "png", new File(path));
  }
  static AbstractButton findButton(Container root, String text) {
    for (Component c : root.getComponents()) {
      if (c instanceof AbstractButton && text.equals(((AbstractButton)c).getText())) return (AbstractButton)c;
      if (c instanceof Container) { AbstractButton b = findButton((Container)c, text); if (b != null) return b; }
    }
    return null;
  }
  static int countText(Container root, String needle) {
    int n = 0;
    for (Component c : root.getComponents()) {
      String t = null;
      if (c instanceof JLabel) t = ((JLabel)c).getText();
      if (c instanceof AbstractButton) t = ((AbstractButton)c).getText();
      if (t != null && t.contains(needle)) n++;
      if (c instanceof Container) n += countText((Container)c, needle);
    }
    return n;
  }
  static void assertTrue(boolean ok, String msg) { if (!ok) throw new AssertionError(msg); }

  public static void main(String[] args) throws Exception {
    final Throwable[] error = new Throwable[1];
    SwingUtilities.invokeAndWait(() -> {
      try {
        Class<?> c = Class.forName("com.hexie.stata.HxWorkbench$WorkbenchFrame");
        Constructor<?> ctor = c.getDeclaredConstructor(boolean.class); ctor.setAccessible(true);
        JFrame frame = (JFrame)ctor.newInstance(true);
        method(c, "showXtregWizardPageV130").invoke(frame);
        frame.setSize(1672, 901); frame.addNotify(); frame.getContentPane().setSize(1672, 901); frame.validate(); layoutTree(frame.getContentPane());

        JSplitPane split = (JSplitPane)field(c, "commandDataSplit").get(frame);
        split.setDividerLocation(0.58); layoutTree(frame.getContentPane());

        JScrollPane formScroll = (JScrollPane)field(c, "formScroll").get(frame);
        JPanel formPanel = (JPanel)field(c, "formPanel").get(frame);
        assertTrue(formScroll.getHorizontalScrollBarPolicy() == JScrollPane.HORIZONTAL_SCROLLBAR_NEVER, "horizontal scrollbar policy is not NEVER");
        assertTrue(formPanel.getWidth() <= formScroll.getViewport().getExtentSize().width + 2, "form panel is wider than viewport");

        AbstractButton run = findButton(formPanel, "运行 xtreg");
        AbstractButton pa = findButton(formPanel, "population-averaged");
        assertTrue(run != null && run.getWidth() > 20, "run xtreg button missing");
        assertTrue(pa != null && pa.getWidth() > 20, "population-averaged option missing");
        Rectangle runRect = SwingUtilities.convertRectangle(run.getParent(), run.getBounds(), formPanel);
        Rectangle paRect = SwingUtilities.convertRectangle(pa.getParent(), pa.getBounds(), formPanel);
        assertTrue(runRect.x >= 0 && runRect.x + runRect.width <= formPanel.getWidth() + 2, "run button horizontally clipped");
        assertTrue(paRect.x >= 0 && paRect.x + paRect.width <= formPanel.getWidth() + 2, "PA option horizontally clipped");

        JPanel breadcrumb = (JPanel)field(c, "breadcrumbBar").get(frame);
        assertTrue(countText(breadcrumb, "首页") == 1, "breadcrumb contains duplicate 首页");

        @SuppressWarnings("unchecked") JComboBox<String> panelVar = (JComboBox<String>)field(c, "xtregPanelVar").get(frame);
        @SuppressWarnings("unchecked") JComboBox<String> depVar = (JComboBox<String>)field(c, "xtregDepVar").get(frame);
        @SuppressWarnings("unchecked") JList<String> indep = (JList<String>)field(c, "xtregIndepList").get(frame);
        assertTrue(panelVar.getItemCount() >= 10, "xtreg panel variables did not load in preview mode");
        assertTrue(panelVar.getTransferHandler() != null && depVar.getTransferHandler() != null && indep.getTransferHandler() != null, "drop handlers missing");

        TransferHandler.TransferSupport d1 = new TransferHandler.TransferSupport(depVar, new StringSelection("price"));
        assertTrue(depVar.getTransferHandler().canImport(d1) && depVar.getTransferHandler().importData(d1), "drop into dependent variable failed");
        assertTrue("price".equals(depVar.getSelectedItem()), "dependent variable drop selected wrong item");
        TransferHandler.TransferSupport x1 = new TransferHandler.TransferSupport(indep, new StringSelection("mpg"));
        TransferHandler.TransferSupport x2 = new TransferHandler.TransferSupport(indep, new StringSelection("weight"));
        assertTrue(indep.getTransferHandler().importData(x1) && indep.getTransferHandler().importData(x2), "drop into X list failed");
        java.util.List<String> selected = indep.getSelectedValuesList();
        assertTrue(selected.contains("mpg") && selected.contains("weight"), "multi-drop X selection not preserved");

        JTable dataTable = (JTable)field(c, "dataTable").get(frame);
        assertTrue(dataTable.getTableHeader().getTransferHandler() != null, "data header drag handler missing");
        assertTrue(!dataTable.getTableHeader().getReorderingAllowed(), "column reorder still conflicts with header drag");

        render(frame, args[0]);

        JPanel sidebar = (JPanel)field(c, "sidebarPanel").get(frame);
        method(c, "toggleSidebarCollapsed").invoke(frame);
        frame.validate(); layoutTree(frame.getContentPane());
        assertTrue(sidebar.getPreferredSize().width <= 60, "sidebar did not collapse");
        @SuppressWarnings("unchecked") Map<String,JButton> buttons = (Map<String,JButton>)field(c, "sidebarButtons").get(frame);
        assertTrue(buttons.get("data").getText().contains("▤"), "collapsed data icon is not stable");
        split.setDividerLocation(0.55); layoutTree(frame.getContentPane());
        assertTrue(formPanel.getWidth() <= formScroll.getViewport().getExtentSize().width + 2, "form width breaks after sidebar collapse");
        render(frame, args[1]);

        frame.dispose();
      } catch (Throwable t) { error[0] = t; }
    });
    if (error[0] != null) throw new RuntimeException(error[0]);
    System.out.println("HX_UI_AUDIT_OK");
  }
}
EOF

javac --release 11 -cp /tmp/classes -d /tmp/classes /tmp/UiAuditHarness.java
xvfb-run -a java -cp /tmp/classes UiAuditHarness /tmp/xtreg-expanded.png /tmp/xtreg-collapsed.png
test -s /tmp/xtreg-expanded.png
test -s /tmp/xtreg-collapsed.png

grep -q 'VERSION = "1.3.2"' src/main/java/com/hexie/stata/HxWorkbench.java
grep -q 'WidthTrackingPanel' src/main/java/com/hexie/stata/HxWorkbench.java
grep -q 'HORIZONTAL_SCROLLBAR_NEVER' src/main/java/com/hexie/stata/HxWorkbench.java
grep -q 'refreshXtregVariableControls' src/main/java/com/hexie/stata/HxWorkbench.java
grep -q '可直接把右侧数据表表头拖入' src/main/java/com/hexie/stata/HxWorkbench.java
grep -q 'commandPreviewScroll.setPreferredSize(new Dimension(100, 62))' src/main/java/com/hexie/stata/HxWorkbench.java
! grep -q 'commandPreviewScroll.setPreferredSize(new Dimension(640, 62))' src/main/java/com/hexie/stata/HxWorkbench.java
grep -q 'd Version 1.3.2' hxempirical.pkg

echo 'HX_UI_SOURCE_AUDIT_OK'
