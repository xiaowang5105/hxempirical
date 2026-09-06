package com.hexie.stata;
import java.nio.file.*;
import java.util.*;

public final class ResearchProjectTest {
    private static void check(boolean condition,String message) { if(!condition) throw new AssertionError(message); }
    public static void main(String[] args) throws Exception {
        if (args.length==1) {
            ResearchProject linked=new ResearchProject(Paths.get(args[0]).resolve("linked.hxproj"));
            linked.assets="hx-assets-00000000-0000-0000-0000-000000000000";
            try { linked.asset(linked.assets+"/new.dta"); throw new AssertionError("junction accepted"); }
            catch(java.io.IOException expected) { System.out.println("HX_PROJECT_JUNCTION_REJECTED"); }
            return;
        }
        WorkSnapshot a=new WorkSnapshot(); a.command="regress"; a.depvar="y"; a.x="x";
        a.ifcond="year >= 2020"; a.vce="robust"; a.nativeCommand="regress y x if year >= 2020, vce(robust)";
        WorkSnapshot b=WorkSnapshot.decode(a.encode());
        check(b!=null && b.encode().equals(a.encode()),"settings round trip");
        b.vce="cluster"; b.cluster="firm";
        check(!a.signature().equals(b.signature()),"cluster settings must distinguish models");
        b=WorkSnapshot.decode(a.encode()); b.ifcond="year < 2020";
        check(!a.signature().equals(b.signature()),"samples must distinguish models");
        b=WorkSnapshot.decode(a.encode()); b.flags="absorb=firm,year";
        check(!a.signature().equals(b.signature()),"fixed effects must distinguish models");
        b=WorkSnapshot.decode(a.encode()); b.weightVar="weight";
        check(!a.signature().equals(b.signature()),"weights must distinguish models");
        String[] fields=a.encode().split("\\|",-1);
        check(WorkSnapshot.decode(String.join("|",Arrays.copyOf(fields,33)))!=null,"legacy 33-field snapshot");
        check(WorkSnapshot.decode(String.join("|",Arrays.copyOf(fields,34)))!=null,"legacy 34-field snapshot");
        a.endog="endogenous"; a.instruments="z1 z2"; a.model="2sls";
        WorkSnapshot iv=WorkSnapshot.decode(a.encode());
        check(iv.endog.equals(a.endog) && iv.instruments.equals(a.instruments) && iv.model.equals(a.model),"IV fields survive serialization");
        iv.instruments="z3";
        check(!iv.signature().equals(a.signature()),"different IV sets must distinguish models");
        check(ResearchProject.withSample("regress y x if year>2000 in 1/99, vce(robust)","s").equals("regress y x if (year>2000) & s in 1/99, vce(robust)"),"existing sample condition");
        check(ResearchProject.withSample("regress y x [aw=w], vce(robust)","s").equals("regress y x if s [aw=w], vce(robust)"),"weight placement");
        check(ResearchProject.withSample("regress y x if group == \"a in b\", vce(robust)","s").equals("regress y x if (group == \"a in b\") & s, vce(robust)"),"quoted condition text");
        try { ResearchProject.withSample("bootstrap: regress y x","s"); throw new AssertionError("complex prefix accepted"); } catch(java.io.IOException expected) {}
        Path directory=Files.createTempDirectory("hx-project-test-");
        try {
            ResearchProject p=new ResearchProject(directory.resolve("中文项目.hxproj"));
            Files.createDirectories(directory.resolve(p.assets));
            p.baseline=p.newAsset(".dta"); p.current=p.baseline;
            Files.writeString(p.asset(p.baseline),"test fixture");
            p.rng="mt64"; p.rngState="123456";
            ResearchProject.Run first=p.add("regress y x",a.encode(),"中文结果\nsecond line",0,3,.5);
            first.model=p.newAsset("-model"); first.signature="same-data";
            ResearchProject.Run second=p.add("regress y x z",b.encode(),"",0,3,.6);
            second.model=p.newAsset("-model"); second.signature="same-data";
            Files.writeString(p.asset(first.model+".sample"),"1\n1\n0\n1\n");
            Files.writeString(p.asset(second.model+".sample"),"1\n0\n1\n1\n");
            for (ResearchProject.Run r : p.models()) {
                Files.writeString(p.asset(r.model+".ster"),"fixture model");
                Files.writeString(p.asset(r.model+".tsv"),"term\tcoefficient\tse\nx\t2\t0.1\n");
            }
            check(!p.sameSamples(p.models()),"equal N does not imply identical samples");
            p.save(); ResearchProject restored=ResearchProject.load(p.file);
            check(restored.runs.size()==2 && restored.runs.get(0).output.equals(first.output),"project journal round trip");
            check(restored.runs.get(0).settings.equals(a.encode()),"model settings persisted");
            check(restored.exportDo().contains("use ") && restored.exportDo().contains("regress y x z"),"complete command export");
            check(restored.commonSampleDo(restored.models()).contains("HX_common_M2"),"common sample script");
            try { restored.asset("../outside.dta"); throw new AssertionError("path traversal accepted"); } catch(java.io.IOException expected) {}
            p.add("summarize y", "", "checkpoint", 0, Double.NaN, Double.NaN);
            p.checkpoint();
            check(ResearchProject.load(p.file).runs.size()==2,"checkpoint must not overwrite manual save");
            ResearchProject recovered=ResearchProject.loadFrom(p.file,p.recoveryFile());
            check(recovered.file.equals(p.file) && recovered.runs.size()==3,"recovery keeps original project destination");
            p.save();
            check(ResearchProject.loadFrom(p.file,p.backupFile()).runs.size()==2,"previous project backup readable");
            Set<String> oldSnapshots=p.savedSnapshots();
            String oldCurrent=p.current;
            p.current=p.newAsset(".dta"); Files.writeString(p.asset(p.current),"new snapshot"); p.checkpoint();
            p.pruneSnapshots(oldSnapshots);
            check(Files.exists(p.asset(oldCurrent)),"manual-save snapshot retained after checkpoint");
            oldSnapshots=p.savedSnapshots(); String priorRecovery=p.current;
            p.current=p.newAsset(".dta"); Files.writeString(p.asset(p.current),"next snapshot"); p.checkpoint();
            p.pruneSnapshots(oldSnapshots);
            check(!Files.exists(p.asset(priorRecovery)),"obsolete recovery snapshot reclaimed");
            Files.delete(p.asset(first.model+".tsv"));
            try { ResearchProject.load(p.file); throw new AssertionError("missing model accepted"); }
            catch(java.io.IOException expected) { check(expected.getMessage().contains(".tsv"),"name missing resource"); }
            Files.writeString(p.asset(first.model+".tsv"),"term\tcoefficient\tse\nx\t2\t0.1\n");
            String before=Files.readString(p.file);
            while(p.runs.size()<=ResearchProject.MAX_RUNS) p.add("display 1","","",0,Double.NaN,Double.NaN);
            try { p.save(); throw new AssertionError("oversize journal saved"); } catch(java.io.IOException expected) {}
            check(Files.readString(p.file).equals(before),"failed save must retain old project");
            String generated=p.newAsset(".dta"); Files.writeString(p.asset(generated),"orphan");
            p.discardNewAsset(generated); check(!Files.exists(p.asset(generated)),"remove owned failed snapshot");
            try { p.discardNewAsset(p.assets+"/user.dta"); throw new AssertionError("user file cleanup accepted"); } catch(java.io.IOException expected) {}
            Path atomicTarget=directory.resolve("occupied"); Files.createDirectory(atomicTarget);
            Files.writeString(atomicTarget.resolve("keep.txt"),"keep");
            try { ResearchProject.atomicWrite(atomicTarget,"new"); throw new AssertionError("directory replaced"); } catch(java.io.IOException expected) {}
            check(Files.readString(atomicTarget.resolve("keep.txt")).equals("keep"),"replacement failure retains destination");
            try(java.util.stream.Stream<Path> files=Files.list(directory)) {
                check(files.noneMatch(f->f.getFileName().toString().startsWith(".hx-write-")),"temporary writes cleaned");
            }
            System.out.println("HX_RESEARCH_PROJECT_TEST_OK");
        } finally {
            try(java.util.stream.Stream<Path> paths=Files.walk(directory)) {
                for(Path path:paths.sorted(Comparator.reverseOrder()).toArray(Path[]::new)) Files.delete(path);
            }
        }
    }
}
