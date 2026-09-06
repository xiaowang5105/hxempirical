package com.hexie.stata;
import java.nio.file.*;
import java.util.*;

public final class ResearchProjectTest {
    private static void check(boolean condition,String message) { if(!condition) throw new AssertionError(message); }
    public static void main(String[] args) throws Exception {
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
        check(WorkSnapshot.decode(a.encode().substring(0,a.encode().lastIndexOf('|')))!=null,"legacy 33-field snapshot");
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
            check(!p.sameSamples(p.models()),"equal N does not imply identical samples");
            p.save(); ResearchProject restored=ResearchProject.load(p.file);
            check(restored.runs.size()==2 && restored.runs.get(0).output.equals(first.output),"project journal round trip");
            check(restored.runs.get(0).settings.equals(a.encode()),"model settings persisted");
            check(restored.exportDo().contains("use ") && restored.exportDo().contains("regress y x z"),"complete command export");
            check(restored.commonSampleDo(restored.models()).contains("HX_common_M2"),"common sample script");
            try { restored.asset("../outside.dta"); throw new AssertionError("path traversal accepted"); } catch(java.io.IOException expected) {}
            System.out.println("HX_RESEARCH_PROJECT_TEST_OK");
        } finally {
            try(java.util.stream.Stream<Path> paths=Files.walk(directory)) {
                for(Path path:paths.sorted(Comparator.reverseOrder()).toArray(Path[]::new)) Files.delete(path);
            }
        }
    }
}
