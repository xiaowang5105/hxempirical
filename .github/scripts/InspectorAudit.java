import java.lang.reflect.*;
import java.nio.file.*;
import javax.swing.*;
import com.stata.sfi.*;

public class InspectorAudit {
  static Field f(Class<?> c,String n)throws Exception{Field x=c.getDeclaredField(n);x.setAccessible(true);return x;}
  static Method m(Class<?> c,String n,Class<?>...a)throws Exception{Method x=c.getDeclaredMethod(n,a);x.setAccessible(true);return x;}
  static void ck(boolean v,String s){if(!v)throw new AssertionError(s);}
  public static void main(String[] args)throws Exception{
    final Throwable[] err={null};
    SwingUtilities.invokeAndWait(()->{try{
      Class<?> c=Class.forName("com.hexie.stata.HxWorkbench$WorkbenchFrame");
      Constructor<?> ct=c.getDeclaredConstructor(boolean.class); ct.setAccessible(true);
      JFrame fr=(JFrame)ct.newInstance(true); fr.addNotify();
      JTabbedPane tabs=(JTabbedPane)f(c,"dataTabs").get(fr);
      JLabel title=(JLabel)f(c,"rightPaneTitle").get(fr);
      JLabel sub=(JLabel)f(c,"dataLabel").get(fr);
      JButton refresh=(JButton)f(c,"refreshButton").get(fr);
      Field last=f(c,"lastExecutedCommand");
      last.set(fr,"xtreg price mpg weight, fe vce(robust)");
      Method sync=m(c,"syncRightPaneTitle");
      tabs.setSelectedIndex(1); sync.invoke(fr);
      ck("结果".equals(title.getText()),"result title");
      ck(!refresh.isVisible(),"refresh visible in Results");
      ck(sub.getText().contains("最近命令")&&sub.getText().contains("xtreg"),"result subtitle="+sub.getText());
      Method refreshData=m(c,"refreshDataset",boolean.class);
      refreshData.invoke(fr,false);
      ck(sub.getText().contains("最近命令"),"dataset refresh overwrote Results subtitle: "+sub.getText());
      tabs.setSelectedIndex(2); sync.invoke(fr);
      ck("运行日志".equals(title.getText()),"log title");
      ck(!refresh.isVisible(),"refresh visible in Logs");
      ck(sub.getText().contains("Return code")&&sub.getText().contains("History"),"log subtitle="+sub.getText());
      tabs.setSelectedIndex(0); sync.invoke(fr);
      ck("当前数据".equals(title.getText()),"data title");
      ck(refresh.isVisible(),"refresh hidden in Data");
      ck("尚未载入数据".equals(sub.getText()),"data subtitle="+sub.getText());
      JTextArea result=(JTextArea)f(c,"resultSummaryArea").get(fr);
      ck(!result.getLineWrap(),"Results mirror wraps");
      fr.dispose();
    }catch(Throwable t){err[0]=t;}});
    if(err[0]!=null)throw new RuntimeException(err[0]);

    Path huge=Paths.get("/tmp/hx_huge_result.txt");
    String chunk="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ\n";
    StringBuilder b=new StringBuilder();
    while(b.length()<3*1024*1024)b.append(chunk);
    Files.writeString(huge,b.toString());
    Characteristic.setDtaChar("hxtoolbox_last_results_file",huge.toString());
    Class<?> bridge=Class.forName("com.hexie.stata.HxWorkbench$StataBridge");
    Method read=m(bridge,"lastNativeOutput");
    String out=(String)read.invoke(null);
    ck(out.length()<2200000,"huge output not bounded: "+out.length());
    ck(out.contains("仅显示前 2 MB"),"truncation marker missing");

    Path small=Paths.get("/tmp/hx_small_result.txt");
    Files.writeString(small,"Fixed-effects regression\nprice | Coefficient Std. err. t P>|t|\nmpg | -49.5 86.1 -0.57 0.567\n");
    Characteristic.setDtaChar("hxtoolbox_last_results_file",small.toString());
    String raw=(String)read.invoke(null);
    ck(raw.contains("Coefficient")&&!raw.contains("仅显示前 2 MB"),"small output altered");
    System.out.println("INSPECTOR_AUDIT_OK");
  }
}
