package com.hexie.stata;

import java.awt.*;
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.util.List;
import java.util.function.*;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;

/** Project UI and lifecycle, separated from individual estimator pages. */
final class ProjectController {
    interface Gateway {
        int execute(String command);
        String characteristic(String name);
    }
    private final JFrame owner;
    private final Gateway stata;
    private final Supplier<String> captureSettings;
    private final Consumer<String> restoreSettings;
    private final Runnable refresh;
    private final BooleanSupplier busy;
    private final JButton button = new JButton("研究项目");
    private ResearchProject project;
    private String pendingSettings = "";
    private int stepsSinceCheckpoint;

    ProjectController(JFrame owner, Gateway stata, Supplier<String> captureSettings,
                      Consumer<String> restoreSettings, Runnable refresh, BooleanSupplier busy) {
        this.owner=owner; this.stata=stata; this.captureSettings=captureSettings;
        this.restoreSettings=restoreSettings; this.refresh=refresh; this.busy=busy;
        JPopupMenu menu = new JPopupMenu();
        action(menu,"新建项目…",this::create);
        action(menu,"打开项目…",this::open);
        action(menu,"保存项目和当前数据",this::save);
        action(menu,"设置自动恢复点频率…",this::checkpointFrequency);
        action(menu,"查看步骤 / 恢复模型设置",this::showRuns);
        action(menu,"导出完整 do-file…",()->export(false));
        action(menu,"比较已保存模型",this::compare);
        action(menu,"命名模型…",this::renameModel);
        action(menu,"导出所选模型表格（TSV）…",this::exportTable);
        action(menu,"导出项目 ZIP（含数据与文件依赖）…",this::exportBundle);
        action(menu,"导出共同样本重估 do-file…",()->export(true));
        button.addActionListener(e->menu.show(button,0,button.getHeight()));
    }

    JButton button() { return button; }
    private interface Task { void run() throws Exception; }
    private void action(JPopupMenu menu,String label,Task task) {
        JMenuItem item = new JMenuItem(label);
        item.addActionListener(e->{
            if(busy.getAsBoolean()) { message("请等待当前命令运行结束。"); return; }
            try { task.run(); } catch(Exception ex) { error(ex); }
        }); menu.add(item);
    }
    private void error(Exception e) { JOptionPane.showMessageDialog(owner,e.getMessage(),"项目操作未完成",JOptionPane.ERROR_MESSAGE); }
    private void message(String text) { JOptionPane.showMessageDialog(owner,text,"研究项目",JOptionPane.INFORMATION_MESSAGE); }
    private void check(int rc) throws IOException { if(rc!=0) throw new IOException("Stata 返回 r("+rc+")，请查看 Results。"); }
    private void requireProject() throws IOException { if(project==null) throw new IOException("请先新建或打开研究项目。"); }
    private void updateTitle() { button.setText(project==null?"研究项目":project.file.getFileName()+(project.dirty?" *":"")); }

    boolean canClose() {
        if(project==null || !project.dirty) return true;
        int choice=JOptionPane.showConfirmDialog(owner,"保存当前项目和数据后继续？","项目有未保存的步骤",JOptionPane.YES_NO_CANCEL_OPTION);
        if(choice==JOptionPane.CANCEL_OPTION || choice==JOptionPane.CLOSED_OPTION) return false;
        if(choice==JOptionPane.YES_OPTION) try { save(); } catch(Exception e) { error(e); return false; }
        return true;
    }

    private Path choose(String title,String extension,boolean writing) throws IOException {
        JFileChooser chooser=new JFileChooser(project==null?null:project.file.getParent().toFile());
        chooser.setDialogTitle(title);
        chooser.setFileFilter(new javax.swing.filechooser.FileNameExtensionFilter(extension+" 文件",extension));
        int result=writing?chooser.showSaveDialog(owner):chooser.showOpenDialog(owner);
        if(result!=JFileChooser.APPROVE_OPTION) return null;
        Path path=chooser.getSelectedFile().toPath().toAbsolutePath();
        if(writing && !path.toString().toLowerCase(Locale.ROOT).endsWith("."+extension)) path=Paths.get(path+"."+extension);
        if(writing && Files.exists(path) && JOptionPane.showConfirmDialog(owner,"替换已有文件："+path.getFileName()+"？","确认保存",JOptionPane.OK_CANCEL_OPTION)!=JOptionPane.OK_OPTION) return null;
        return path;
    }

    private void create() throws Exception {
        if(!canClose()) return;
        Path file=choose("保存新项目（从当前数据开始记录）","hxproj",true);
        if(file==null) return;
        ResearchProject next=new ResearchProject(file);
        Files.createDirectories(file.getParent().resolve(next.assets));
        next.baseline=next.newAsset(".dta"); next.current=next.baseline;
        try {
        check(stata.execute("hxproject snapshot using "+ResearchProject.stataQuote(next.asset(next.baseline).toString())));
        next.workingDirectory=stata.characteristic("hxproject_pwd");
        next.environment=stata.characteristic("hxproject_environment");
        next.rng=stata.characteristic("hxproject_rng"); next.rngState=stata.characteristic("hxproject_rngstate");
        next.currentRng=next.rng; next.currentRngState=next.rngState;
        next.sortRngState=stata.characteristic("hxproject_sortrngstate"); next.currentSortRngState=next.sortRngState;
        next.save();
        } catch (Exception e) { cleanup(next, next.baseline, e); throw e; }
        project=next; stepsSinceCheckpoint=0; updateTitle();
        message("项目已创建。每个完成的步骤会保存恢复点；手动保存时更新项目并保留上一版本。\n项目快照支持单 frame。请将 .hxproj、.recovery、.bak 与 hx-assets 目录一同保留。");
    }

    private void open() throws Exception {
        if(!canClose()) return;
        Path file=choose("打开研究项目","hxproj",false);
        if(file==null) return;
        ResearchProject next;
        Path recovery=file.resolveSibling(file.getFileName()+".recovery");
        Path backup=file.resolveSibling(file.getFileName()+".bak");
        if(Files.isRegularFile(recovery) && (!Files.exists(file) || Files.getLastModifiedTime(recovery).compareTo(Files.getLastModifiedTime(file))>0)
                && JOptionPane.showConfirmDialog(owner,"发现较新的自动恢复点，载入这些已完成的步骤和数据？","恢复项目",JOptionPane.YES_NO_OPTION)==JOptionPane.YES_OPTION) {
            next=ResearchProject.loadFrom(file,recovery);
            next.dirty=true;
        } else {
            try { next=ResearchProject.load(file); }
            catch(IOException failed) {
                if(!Files.isRegularFile(backup) || JOptionPane.showConfirmDialog(owner,failed.getMessage()+"\n尝试打开上一份备份？","项目恢复",JOptionPane.YES_NO_OPTION)!=JOptionPane.YES_OPTION) throw failed;
                next=ResearchProject.loadFrom(file,backup); next.dirty=true;
            }
        }
        validatedRng(next.currentRng);
        validatedState(next.currentRngState);
        if(!next.currentSortRngState.isBlank()) validatedState(next.currentSortRngState);
        if(JOptionPane.showConfirmDialog(owner,"载入项目保存的数据并恢复随机数状态？\n当前内存数据将被替换，请先保存需要保留的修改。","恢复项目",JOptionPane.OK_CANCEL_OPTION)!=JOptionPane.OK_OPTION) return;
        // Read the project first; loading never automatically runs recorded commands.
        check(stata.execute(restoreCommand(next)));
        project=next; stepsSinceCheckpoint=0; refresh.run(); updateTitle();
        if(!project.runs.isEmpty()) restoreSettings.accept(project.runs.get(project.runs.size()-1).settings);
    }

    private static String validatedRng(String rng) throws IOException {
        if(!Arrays.asList("mt64", "mt64s", "kiss32").contains(rng)) throw new IOException("项目随机数生成器名称无效。"); return rng;
    }
    private static String validatedState(String state) throws IOException {
        if(!state.matches("[a-zA-Z0-9]+")) throw new IOException("项目随机数状态无效。"); return state;
    }

    static String restoreCommand(ResearchProject next) throws IOException {
        return "hxproject restore using "+ResearchProject.stataQuote(next.asset(next.current).toString())
                +", rng("+validatedRng(next.currentRng)+") rngstate("+validatedState(next.currentRngState)+")"
                +(next.currentSortRngState.isBlank()?"":" sortrngstate("+validatedState(next.currentSortRngState)+")");
    }

    private void save() throws Exception {
        saveSnapshot(false);
    }

    private void saveSnapshot(boolean recovery) throws Exception {
        requireProject();
        Set<String> previousSnapshots;
        try { previousSnapshots=project.savedSnapshots(); }
        catch(IOException e) { previousSnapshots=Collections.emptySet(); }
        String previous=project.current, previousRng=project.currentRng, previousState=project.currentRngState, previousSort=project.currentSortRngState;
        String snapshot=project.newAsset(".dta");
        try {
        check(stata.execute("hxproject snapshot using "+ResearchProject.stataQuote(project.asset(snapshot).toString())));
        project.current=snapshot; project.currentRng=stata.characteristic("hxproject_rng"); project.currentRngState=stata.characteristic("hxproject_rngstate");
        project.currentSortRngState=stata.characteristic("hxproject_sortrngstate");
        if(recovery) project.checkpoint(); else project.save();
        stepsSinceCheckpoint=0;
        } catch(Exception e) {
            project.current=previous; project.currentRng=previousRng; project.currentRngState=previousState; project.currentSortRngState=previousSort;
            cleanup(project,snapshot,e); throw e;
        }
        try { project.pruneSnapshots(previousSnapshots); }
        catch(IOException e) { button.setToolTipText("保存成功；旧快照清理未完成："+e.getMessage()); }
        updateTitle();
    }

    private static void cleanup(ResearchProject p,String resource,Exception failure) {
        try { p.discardNewAsset(resource); } catch(IOException e) { failure.addSuppressed(e); }
    }

    void beginRun() { pendingSettings=project==null?"":captureSettings.get(); }

    void record(String command,int rc,double n,double r2,String output) {
        if(project==null) return;
        ResearchProject.Run run=project.add(command,pendingSettings,output,rc,n,r2);
        if(rc==0 && !Double.isNaN(n)) {
            String prefix=project.newAsset("-model");
            try {
                check(stata.execute("hxproject model using "+ResearchProject.stataQuote(project.asset(prefix).toString())));
                run.model=prefix; run.signature=stata.characteristic("hxproject_signature"); run.vce=stata.characteristic("hxproject_vce");
            } catch(Exception e) {
                for(String suffix:Arrays.asList(".ster",".tsv",".sample")) cleanup(project,prefix+suffix,e);
                run.output+="\n[模型快照未保存："+e.getMessage()+"]"; error(e);
            }
        }
        stepsSinceCheckpoint++;
        if(project.checkpointInterval>0 && stepsSinceCheckpoint>=project.checkpointInterval) {
            try { saveSnapshot(true); }
            catch(Exception e) { run.output+="\n[自动恢复点未保存："+e.getMessage()+"]"; error(e); }
        } else button.setToolTipText("距上次数据恢复点有 "+stepsSinceCheckpoint+" 个步骤；异常退出时这些步骤可能丢失。手动保存会立即更新。");
        updateTitle();
    }

    private void showRuns() throws Exception {
        requireProject();
        DefaultTableModel model=readOnlyTable(new String[]{"步骤","时间","返回码","命令"});
        for(int i=0;i<project.runs.size();i++) { ResearchProject.Run r=project.runs.get(i); model.addRow(new Object[]{i+1,r.time,r.rc,r.command}); }
        JTable table=new JTable(model); table.setAutoCreateRowSorter(true);
        JTextArea output=new JTextArea(12,80); output.setEditable(false);
        table.getSelectionModel().addListSelectionListener(e->{ if(table.getSelectedRow()>=0) output.setText(project.runs.get(table.convertRowIndexToModel(table.getSelectedRow())).output); });
        JSplitPane split=new JSplitPane(JSplitPane.VERTICAL_SPLIT,new JScrollPane(table),new JScrollPane(output));
        split.setPreferredSize(new Dimension(900,550)); split.setResizeWeight(.5);
        int selected=JOptionPane.showOptionDialog(owner,split,"项目步骤",JOptionPane.DEFAULT_OPTION,JOptionPane.PLAIN_MESSAGE,null,new String[]{"恢复所选模型设置","关闭"},"关闭");
        if(selected==0 && table.getSelectedRow()>=0) restoreSettings.accept(project.runs.get(table.convertRowIndexToModel(table.getSelectedRow())).settings);
    }

    private void export(boolean common) throws Exception {
        requireProject();
        List<ResearchProject.Run> selected=common?selectModels():Collections.emptyList();
        if(common && selected.isEmpty()) return;
        if(common) save();
        String text=common?project.commonSampleDo(selected):project.exportDo();
        Path path=choose(common?"导出共同样本重估（检查后在 Stata 运行）":"导出项目完整 do-file","do",true);
        if(path==null) return;
        ResearchProject.atomicWrite(path,text);
        message("已导出："+path+"\n脚本从项目快照开始。使用前请检查外部文件路径和第三方命令依赖。");
    }

    private void compare() throws Exception {
        requireProject(); List<ResearchProject.Run> models=selectModels();
        if(models.isEmpty()) { message("在项目中运行回归后，这里会保存系数、标准误和样本信息。"); return; }
        String[] columns=new String[models.size()+1]; columns[0]="指标 / 系数（标准误）";
        for(int i=0;i<models.size();i++) columns[i+1]=models.get(i).name.isBlank()?"M"+(i+1):models.get(i).name;
        DefaultTableModel table=readOnlyTable(columns);
        Object[] commands=new Object[columns.length], n=new Object[columns.length], r2=new Object[columns.length], vce=new Object[columns.length];
        commands[0]="完整命令（含样本条件、固定效应）"; n[0]="N"; r2[0]="R²"; vce[0]="标准误";
        List<Map<String,String>> coefficients=new ArrayList<>(); Set<String> terms=new LinkedHashSet<>();
        for(int i=0;i<models.size();i++) { ResearchProject.Run m=models.get(i); commands[i+1]=m.command; n[i+1]=m.n; r2[i+1]=Double.isNaN(m.r2)?"—":m.r2; vce[i+1]=m.vce; Map<String,String> c=project.coefficients(m); coefficients.add(c); terms.addAll(c.keySet()); }
        table.addRow(commands); table.addRow(n); table.addRow(r2); table.addRow(vce);
        for(String term:terms) { Object[] row=new Object[columns.length]; row[0]=term; for(int i=0;i<models.size();i++) row[i+1]=coefficients.get(i).getOrDefault(term,"—"); table.addRow(row); }
        JTable view=new JTable(table) {
            public String getToolTipText(java.awt.event.MouseEvent event) {
                int row=rowAtPoint(event.getPoint()), col=columnAtPoint(event.getPoint());
                return row<0 || col<0 ? null : String.valueOf(getValueAt(row,col));
            }
        }; view.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
        for(int i=0;i<columns.length;i++) view.getColumnModel().getColumn(i).setPreferredWidth(i==0?240:240);
        JPanel panel=new JPanel(new BorderLayout(0,10));
        panel.add(new JLabel(project.sameSamples(models)?"所选模型的数据版本与实际估计样本一致。":"数据版本或实际样本不同；共同样本重估要求数据版本一致且命令受支持。"),BorderLayout.NORTH);
        panel.add(new JScrollPane(view),BorderLayout.CENTER); panel.setPreferredSize(new Dimension(950,550));
        JOptionPane.showMessageDialog(owner,panel,"模型比较",JOptionPane.PLAIN_MESSAGE);
    }

    private static DefaultTableModel readOnlyTable(String[] columns) {
        return new DefaultTableModel(columns,0) { public boolean isCellEditable(int row,int col) { return false; } };
    }

    private List<ResearchProject.Run> selectModels() throws IOException {
        requireProject(); List<ResearchProject.Run> models=project.models();
        if(models.isEmpty()) return Collections.emptyList();
        DefaultListModel<String> choices=new DefaultListModel<>();
        for(int i=0;i<models.size();i++) {
            ResearchProject.Run r=models.get(i);
            choices.addElement((r.name.isBlank()?"M"+(i+1):r.name)+" | N="+r.n+" | "+r.command);
        }
        JList<String> list=new JList<>(choices); list.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        list.setSelectionInterval(0,models.size()-1);
        JScrollPane scroll=new JScrollPane(list); scroll.setPreferredSize(new Dimension(800,320));
        if(JOptionPane.showConfirmDialog(owner,scroll,"选择模型（Ctrl / Shift 多选）",JOptionPane.OK_CANCEL_OPTION)!=JOptionPane.OK_OPTION)
            return Collections.emptyList();
        List<ResearchProject.Run> selected=new ArrayList<>();
        for(int i:list.getSelectedIndices()) selected.add(models.get(i));
        return selected;
    }

    private void renameModel() throws Exception {
        List<ResearchProject.Run> selected=selectModels();
        if(selected.isEmpty()) return;
        if(selected.size()!=1) { message("请只选择一个需要命名的模型。"); return; }
        ResearchProject.Run run=selected.get(0);
        String name=JOptionPane.showInputDialog(owner,"模型名称（如：基准回归 / 加入固定效应）",run.name);
        if(name==null) return;
        name=name.trim();
        if(name.isEmpty() || name.length()>120) throw new IOException("名称需为 1–120 个字符。");
        run.name=name; project.dirty=true; save(); updateTitle();
    }

    private void exportTable() throws Exception {
        List<ResearchProject.Run> selected=selectModels(); if(selected.isEmpty()) return;
        String table=project.modelTable(selected);
        Path path=choose("导出模型表格（Excel 可打开）","tsv",true); if(path==null) return;
        ResearchProject.atomicWrite(path,"\ufeff"+table);
        message("已导出所选模型的系数、标准误、N、R²、命令及样本说明：\n"+path);
    }

    private void exportBundle() throws Exception {
        requireProject(); Path path=choose("导出项目及本地数据依赖","zip",true); if(path==null) return;
        save(); ProjectBundle.write(project,path);
        message("项目 ZIP 已导出：\n"+path+"\n解压后在 Stata 切换到解压目录，再运行 replay.do。\nREADME.txt 列出文件依赖与未解析路径；第三方命令仍需安装。\n压缩包包含研究数据，分享前请核对内容。");
    }

    private void checkpointFrequency() throws Exception {
        requireProject();
        String[] labels={"每步保存（默认）","每 5 步保存","每 10 步保存","仅手动保存"};
        int[] intervals={1,5,10,0}; int current=0;
        for(int i=0;i<intervals.length;i++) if(intervals[i]==project.checkpointInterval) current=i;
        Object selected=JOptionPane.showInputDialog(owner,
            "完整数据快照的写入时间随数据量增加。\n降低频率可减少磁盘写入；异常退出会丢失上次恢复点之后的步骤。\n手动保存始终立即保存当前数据与全部步骤。",
            "自动恢复点频率",JOptionPane.QUESTION_MESSAGE,null,labels,labels[current]);
        if(selected==null) return;
        int previous=project.checkpointInterval;
        for(int i=0;i<labels.length;i++) if(labels[i].equals(selected)) project.checkpointInterval=intervals[i];
        try { save(); }
        catch(Exception e) { project.checkpointInterval=previous; throw e; }
        message("已保存当前数据；恢复点频率："+selected);
    }
}
