package com.hexie.stata;

import com.stata.sfi.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import javax.swing.*;

/** Real SFI and Swing regression tests; compiled only by the test runner. */
public final class WorkflowRegressionTest {
    private static Object field(Object target, String name) throws Exception {
        Field f=target.getClass().getDeclaredField(name); f.setAccessible(true); return f.get(target);
    }
    private static Object call(Object target, String name, Class<?>[] types, Object... args) throws Exception {
        Method m=target.getClass().getDeclaredMethod(name,types); m.setAccessible(true); return m.invoke(target,args);
    }
    private static void check(boolean ok,String message) { if(!ok) throw new AssertionError(message); }
    private static JOptionPane optionPane(java.awt.Container container) {
        for (java.awt.Component child : container.getComponents()) {
            if (child instanceof JOptionPane) return (JOptionPane)child;
            if (child instanceof java.awt.Container) {
                JOptionPane nested=optionPane((java.awt.Container)child);
                if (nested!=null) return nested;
            }
        }
        return null;
    }
    private static void execute(String command) {
        int rc=SFIToolkit.executeCommand(command,false);
        check(rc==0,command+" returned r("+rc+")");
    }
    private static void select(Object ui,String name,String... values) throws Exception {
        JList<String> list=(JList<String>)field(ui,name);
        List<Integer> indices=new ArrayList<>();
        for(int i=0;i<list.getModel().getSize();i++)
            if(Arrays.asList(values).contains(list.getModel().getElementAt(i))) indices.add(i);
        list.setSelectedIndices(indices.stream().mapToInt(Integer::intValue).toArray());
        check(list.getSelectedValuesList().equals(Arrays.asList(values)),"test role not available: "+name);
    }
    public static int run(String[] args) {
        try {
            Path trace=Paths.get(args[0]).getParent().resolve("workflow-threads.txt");
            Thread watchdog=new Thread(()->{
                try {
                    Thread.sleep(8000);
                    StringBuilder dump=new StringBuilder();
                    Thread.getAllStackTraces().forEach((t,stack)->{
                        dump.append(t.getName()).append(" ").append(t.getState()).append('\n');
                        for(StackTraceElement line:stack) dump.append("  ").append(line).append('\n');
                    });
                    Files.writeString(trace,dump.toString());
                } catch(Exception ignored) {}
            }); watchdog.setDaemon(true); watchdog.start();
            // javacall holds Stata's execution thread. Run SFI on that thread;
            // waiting for an EDT that calls SFI would deadlock the test harness.
            {
                JFrame ui=null;
                try {
                    Class<?> type=Class.forName("com.hexie.stata.HxWorkbench$WorkbenchFrame");
                    Constructor<?> constructor=type.getDeclaredConstructor(boolean.class); constructor.setAccessible(true);
                    ui=(JFrame)constructor.newInstance(false);
                    // This synchronous harness drives previews explicitly; a live timer
                    // would call SFI from EDT while javacall owns the native thread.
                    javax.swing.Timer previewTimer=(javax.swing.Timer)field(ui,"previewTimer");
                    previewTimer.stop();
                    for(java.awt.event.ActionListener listener:previewTimer.getActionListeners()) previewTimer.removeActionListener(listener);
                    // Capture, encode, decode and restore the real generic IV controls.
                    call(ui,"openCommandPage",new Class<?>[]{String.class},"ivregress");
                    select(ui,"endog","x"); select(ui,"instruments","z");
                    ((JComboBox<?>)field(ui,"depvar")).setSelectedItem("y");
                    ((JComboBox<?>)field(ui,"model")).setSelectedItem("广义矩估计（GMM）");
                    WorkSnapshot snapshot=(WorkSnapshot)call(ui,"captureWorkSnapshot",new Class<?>[]{});
                    ((JList<?>)field(ui,"endog")).clearSelection();
                    ((JList<?>)field(ui,"instruments")).clearSelection();
                    ((JComboBox<?>)field(ui,"model")).setSelectedItem("两阶段最小二乘（2SLS）");
                    call(ui,"restoreWorkSnapshot",new Class<?>[]{WorkSnapshot.class},WorkSnapshot.decode(snapshot.encode()));
                    check(((JList<?>)field(ui,"endog")).getSelectedValuesList().equals(Arrays.asList("x")),"IV endogenous lost");
                    check(((JList<?>)field(ui,"instruments")).getSelectedValuesList().equals(Arrays.asList("z")),"IV instruments lost");
                    call(ui,"updatePreview",new Class<?>[]{});
                    String preview=((JTextArea)field(ui,"previewArea")).getText();
                    check(preview.contains("(x = z)"),"restored IV command incomplete: "+preview);
                    check(preview.startsWith("ivregress gmm "),"restored estimator choice lost: "+preview);
                    execute(preview);

                    // A rounded display, value labels, dates, strings and extended missings
                    // must retain their original value when editing is accepted unchanged.
                    Object model=field(ui,"dataModel");
                    call(model,"reload",new Class<?>[]{});
                    JTable table=(JTable)field(ui,"dataTable");
                    for(String variable:Arrays.asList("precise","labelled","day","extmiss","padded")) {
                        int index=Data.getVarIndex(variable), col=index-1;
                        String raw=(String)call(model,"editValueAt",new Class<?>[]{int.class,int.class},0,col);
                        if(variable.equals("precise")) check(raw.equals("1.23456789"),"numeric edit rounded: "+raw);
                        if(variable.equals("labelled")) check(raw.equals("1.0"),"label became data: "+raw);
                        if(variable.equals("extmiss")) check(raw.equals(".a"),"extended missing lost: "+raw);
                        if(variable.equals("padded")) check(raw.equals("  keep spaces  "),"string trimmed");
                        int view=table.convertColumnIndexToView(col);
                        table.changeSelection(0,view,false,false);
                        call(ui,"syncSpreadsheetSelection",new Class<?>[]{});
                        check(((JTextField)field(ui,"dataFormulaField")).getText().equals(raw),"formula bar uses display value");
                        check(table.editCellAt(0,view),"cell not editable");
                        check(((JTextField)table.getEditorComponent()).getText().equals(raw),"editor uses display value");
                        check(table.getCellEditor().stopCellEditing(),"unchanged edit rejected");
                        check(raw.equals(call(model,"editValueAt",new Class<?>[]{int.class,int.class},0,col)),"unchanged edit changed data");
                    }
                    check((Boolean)call(ui,"commitSpreadsheetCellEdit",new Class<?>[]{int.class,int.class,Object.class},0,Data.getVarIndex("precise")-1,"2.34567890123456"),"numeric update rejected");
                    check(Data.getNum(Data.getVarIndex("precise"),1)==2.34567890123456,"numeric update lost precision");
                    String quoted="  say \"hello\"  ";
                    check((Boolean)call(ui,"commitSpreadsheetCellEdit",new Class<?>[]{int.class,int.class,Object.class},0,Data.getVarIndex("padded")-1,quoted),"quoted string update rejected");
                    check(Data.getStr(Data.getVarIndex("padded"),1).equals(quoted),"nested quoting or whitespace changed string");

                    // Use the same setup recorder used by panel wizard and generic pages.
                    Path directory=Paths.get(args[0]); Files.createDirectories(directory);
                    ResearchProject p=new ResearchProject(directory.resolve("panel.hxproj"));
                    Files.createDirectories(directory.resolve(p.assets));
                    p.baseline=p.newAsset(".dta"); p.current=p.baseline;
                    execute("hxproject snapshot using "+ResearchProject.stataQuote(p.asset(p.baseline).toString()));
                    p.rng=Characteristic.getDtaChar("hxproject_rng"); p.currentRng=p.rng;
                    p.rngState=Characteristic.getDtaChar("hxproject_rngstate"); p.currentRngState=p.rngState;
                    p.save();
                    Object controller=field(ui,"researchProject");
                    Field project=controller.getClass().getDeclaredField("project"); project.setAccessible(true); project.set(controller,p);
                    check((Integer)call(ui,"runProjectSetup",new Class<?>[]{String.class},"xtset id year")==0,"panel setup failed");
                    check(p.runs.get(0).command.equals("xtset id year"),"panel setup not recorded");
                    call(ui,"openCommandPage",new Class<?>[]{String.class},"xtlogit");
                    ((JComboBox<?>)field(ui,"panel")).setSelectedItem("id");
                    ((JComboBox<?>)field(ui,"time")).setSelectedItem("year");
                    check((Boolean)call(ui,"ensureGenericPanelDeclarationBeforeRun",new Class<?>[]{}),"generic panel preparation failed");
                    check(p.runs.size()==2 && p.runs.get(1).command.equals("xtset id year"),"generic panel setup not recorded");
                    Field busy=type.getDeclaredField("runInProgress"); busy.setAccessible(true); busy.setBoolean(ui,true);
                    try {
                        check((Integer)call(ui,"runProjectSetup",new Class<?>[]{String.class},"xtset, clear")!=0,"setup ran during estimation");
                        ((JTextArea)field(ui,"previewArea")).setText("busy sentinel");
                        call(ui,"updatePreview",new Class<?>[]{});
                        check(((JTextArea)field(ui,"previewArea")).getText().equals("busy sentinel"),"preview ran during estimation");
                    } finally { busy.setBoolean(ui,false); }
                    execute("xtreg y x, fe");
                    execute("scalar hx_expected_coef = _b[x]");
                    p.add("xtreg y x, fe","","",0,Scalar.getValue("e(N)"),Scalar.getValue("e(r2)"));
                    Path replay=directory.resolve("replay.do"); ResearchProject.atomicWrite(replay,p.exportDo());
                    execute("xtset, clear");
                    execute("do "+ResearchProject.stataQuote(replay.toString()));
                    execute("assert abs(_b[x] - scalar(hx_expected_coef)) < 1e-12");

                    // Exercise the real replacement dialog: Cancel leaves the dataset untouched.
                    javax.swing.Timer cancelDialog=new javax.swing.Timer(50,null);
                    cancelDialog.addActionListener(event->{
                        for (java.awt.Window window : java.awt.Window.getWindows()) {
                            if (window instanceof JDialog && window.isVisible()
                                  && ((JDialog)window).getTitle().equals("确认替换当前数据")) {
                                JOptionPane pane=optionPane((JDialog)window);
                                if(pane!=null) { pane.setValue(JOptionPane.CANCEL_OPTION); cancelDialog.stop(); }
                            }
                        }
                    });
                    cancelDialog.start();
                    try {
                        call(ui,"loadConvertedData",new Class<?>[]{Path.class,int.class},directory.resolve("absent.dta"),0);
                        check(Data.getObsTotal()==40,"cancelled load changed observations");
                    } finally { cancelDialog.stop(); }

                    Path csv=directory.resolve("企业 数据.csv"), dta=directory.resolve("企业 数据.dta");
                    Files.writeString(csv,"code,amount\n0012,2\n0034,4\n");
                    String importCommand="import delimited using "+ResearchProject.stataQuote(csv.toString())+", clear varnames(1) stringcols(1)";
                    Class<?>[] conversionTypes={Path.class,Path.class,DataWorkflow.OutputTarget.class,String.class};
                    Object outcome=call(ui,"convertOne",conversionTypes,csv,dta,new DataWorkflow.OutputTarget(dta,false),importCommand);
                    check((Boolean)field(outcome,"success"),"conversion failed: "+field(outcome,"message"));
                    check(Data.getObsTotal()==40,"file conversion replaced active data");
                    execute("assert abs(_b[x] - scalar(hx_expected_coef)) < 1e-12");
                    String conversion=(String)field(outcome,"replayCommand");
                    p.add(conversion,"","",0,Double.NaN,Double.NaN);
                    // Failure during conversion leaves an already approved output intact.
                    byte[] previous=Files.readAllBytes(dta);
                    Object failed=call(ui,"convertOne",conversionTypes,csv,dta,new DataWorkflow.OutputTarget(dta,true),
                        "import delimited using "+ResearchProject.stataQuote(csv+".absent")+", clear");
                    check(!(Boolean)field(failed,"success"),"invalid import unexpectedly succeeded");
                    check(Arrays.equals(previous,Files.readAllBytes(dta)),"failed conversion overwrote old DTA");
                    check(Data.getObsTotal()==40,"failed conversion changed active data");
                    check(((String)field(failed,"replayCommand")).lines().allMatch(line->line.startsWith("*")),"failed conversion remains executable");
                    p.add((String)field(failed,"replayCommand"),"","",(Integer)field(failed,"rc"),Double.NaN,Double.NaN);
                    p.add("display as text \"expected failure\"\nerror 198","","",198,Double.NaN,Double.NaN);
                    String load="hxproject load using "+ResearchProject.stataQuote(dta.toString());
                    check((Integer)call(ui,"runRecorded",new Class<?>[]{String.class},load)==0,"converted data load failed");
                    check(Data.getObsTotal()==2 && Data.getStr(Data.getVarIndex("code"),1).equals("0012"),"loaded data differ");
                    p.add(load,"","",0,Double.NaN,Double.NaN);
                    Path conversionReplay=directory.resolve("conversion-replay.do");
                    ResearchProject.atomicWrite(conversionReplay,p.exportDo());
                    execute("do "+ResearchProject.stataQuote(conversionReplay.toString()));
                    check(Data.getObsTotal()==2 && Data.getStr(Data.getVarIndex("code"),2).equals("0034"),"conversion journal did not replay");
                    execute("frames dir");
                    execute("assert wordcount(\"`r(frames)'\") == 1");
                    try (java.util.stream.Stream<Path> files=Files.list(directory)) {
                        check(files.noneMatch(path->path.getFileName().toString().startsWith(".hx-convert-")),"staged DTA leaked");
                    }
                } catch(Exception e) { throw new RuntimeException(e); }
                finally {
                    if(ui!=null) {
                        try { ((javax.swing.Timer)field(ui,"previewTimer")).stop(); } catch(Exception ignored) {}
                        ui.dispose();
                    }
                }
            }
            SFIToolkit.displayln("HX_WORKFLOW_REGRESSION_OK"); return 0;
        } catch(Throwable e) { SFIToolkit.errorln(SFIToolkit.stackTraceToString(e)); return 459; }
    }
}
