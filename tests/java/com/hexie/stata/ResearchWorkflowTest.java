package com.hexie.stata;
import java.nio.file.*;
import java.nio.charset.*;
import java.util.*;
import java.util.zip.*;

public final class ResearchWorkflowTest {
    static void check(boolean condition,String message) { if(!condition) throw new AssertionError(message); }
    public static void main(String[] args) throws Exception {
        Path dir=Files.createTempDirectory("hx-research-test-");
        try {
            Path csv=dir.resolve("input.csv");
            Files.writeString(csv,"a".repeat(65535)+"中\n");
            check(DelimitedData.encoding(csv,"自动识别").equals("UTF-8"),"UTF-8 boundary");
            Files.write(csv,("id,note\n"+"123,abc\n".repeat(9000)+"001,中文\n").getBytes(Charset.forName("GB18030")));
            check(DelimitedData.encoding(csv,"自动识别").equals("GB18030"),"late non-UTF8 text");
            Files.writeString(csv,"id,note\n"+"123,abc\n".repeat(310)+"001234,\"first\nsecond\"\n12345678901234567,\"a,\"\"b\"\"\"\n");
            DelimitedData.Scan scan=DelimitedData.scan(csv,"UTF-8","自动识别",true);
            check(scan.rows==312 && scan.stringColumns.equals(Arrays.asList(1)),"full logical records and precision protection");
            Files.writeString(csv,"\ufeffid;\"a,b,c\"\n001;ok\n");
            scan=DelimitedData.scan(csv,"UTF-8","自动识别",true);
            check(scan.delimiter==';' && scan.names.get(0).equals("id"),"quoted header delimiter / BOM");
            for(String bad:Arrays.asList("a,b\n1,\"open", "a,b\n1,2,3\n", "a,b\n1,\"a\"oops\n")) {
                Files.writeString(csv,bad);
                try { DelimitedData.scan(csv,"UTF-8","逗号",true); throw new AssertionError("malformed CSV accepted"); }
                catch(java.io.IOException expected) {}
            }
            for(String model:Arrays.asList("regress y x","quietly: regress y x","bootstrap, reps(20): regress y x","svy: regress y x","mi estimate: regress y x","arima y"))
                check(RunResult.isEstimationCommand(model),"model prefix "+model);
            for(String command:Arrays.asList("generate x=1","mi describe","statsby: regress y x","regress y x\ndrop x"))
                check(!RunResult.isEstimationCommand(command),"not a single supported model");
            ResearchProject p=new ResearchProject(dir.resolve("project.hxproj"));
            Files.createDirectories(p.asset(p.newAsset(".dta")).getParent());
            p.baseline=p.newAsset(".dta"); p.current=p.baseline;
            Files.writeString(p.asset(p.baseline),"fixture"); p.workingDirectory=dir.toString(); p.environment="Stata test";
            ResearchProject.Run a=p.add("regress y x","","",0,10,.5); a.name="基准模型"; a.model=p.newAsset("-model"); a.signature="same";
            for(String suffix:Arrays.asList(".ster",".sample")) Files.writeString(p.asset(a.model+suffix),"fixture");
            Files.writeString(p.asset(a.model+".tsv"),"term\tcoefficient\tse\nx\t2\t0.1\n");
            ResearchProject.Run b=p.add("svy: regress y x","","",0,10,.4); b.name="Excluded";
            p.save();
            check(ResearchProject.load(p.file).runs.get(0).name.equals("基准模型"),"model name persists");
            String table=p.modelTable(Arrays.asList(a));
            check(table.contains("基准模型") && table.contains("2 (0.1)") && !table.contains("Excluded"),"selected TSV export");
            Files.writeString(csv,"id\n001\n");
            WorkSnapshot settings=new WorkSnapshot(); settings.usingFile=csv.toString();
            settings.nativeCommand="import delimited using "+ResearchProject.stataQuote(csv.toString())+", clear";
            p.add(settings.nativeCommand,settings.encode(),"",0,Double.NaN,Double.NaN);
            p.add("generate str40 note = \"input.csv\"","","",0,Double.NaN,Double.NaN);
            p.add("save \"generated.dta\", replace\nuse \"generated.dta\", clear","","",0,Double.NaN,Double.NaN);p.save();
            Path bundle=dir.resolve("bundle.zip"); ProjectBundle.write(p,bundle);
            try(ZipFile zip=new ZipFile(bundle.toFile())) {
                String replay=new String(zip.getInputStream(zip.getEntry("replay.do")).readAllBytes(),StandardCharsets.UTF_8);
                check(!replay.contains(dir.toString().replace('\\','/')) && replay.contains("external/file-1.csv"),"bundle uses copied relative files");
                check(zip.getEntry(p.baseline)!=null && zip.getEntry("SHA256.tsv")!=null,"bundle resources and manifest");
                check(replay.contains("generate str40 note = \"input.csv\""),"ordinary filename string was rewritten");
                Path moved=dir.resolve("moved"); Files.createDirectories(moved);
                for(Enumeration<? extends ZipEntry> entries=zip.entries();entries.hasMoreElements();) {
                    ZipEntry entry=entries.nextElement(); Path target=moved.resolve(entry.getName()).normalize();
                    check(target.startsWith(moved),"unexpected archive path");
                    if(entry.isDirectory()) { Files.createDirectories(target);continue; }
                    Files.createDirectories(target.getParent());
                    try(java.io.InputStream in=zip.getInputStream(entry)) { Files.copy(in,target); }
                }
                ResearchProject reopened=ResearchProject.load(moved.resolve("project.hxproj"));
                check(reopened.portable && Path.of(reopened.workingDirectory).equals(moved),"portable project working directory");
                String again=reopened.exportDo();
                check(!again.contains("cd "+ResearchProject.stataQuote(dir.toString())),"reexport returned to source directory");
                check(WorkSnapshot.decode(reopened.runs.get(2).settings).usingFile.equals("external/file-1.csv"),"file setting not migrated");
                Files.delete(csv);
                ProjectBundle.write(reopened,moved.resolve("second.zip"));
            }
            final int[] calls={0};
            String literals="generate note = \"input.csv\"\nlabel variable x \"input.csv\"\n* use \"input.csv\"\ndisplay \"input.csv\"";
            check(StataFilePaths.rewrite(literals,(path,write)->{calls[0]++;return "changed";}).equals(literals) && calls[0]==0,"file parser touched literals");
            check(StataFilePaths.rewrite("frame f: import delimited using \"input.csv\", clear",(path,write)->"copied.csv").contains("using \"copied.csv\""),"frame file argument not migrated");
            for(String ambiguous:Arrays.asList("append using a.dta b.dta", "use \"$data/input.dta\", clear", "cd old")) {
                try { StataFilePaths.rewrite(ambiguous,(path,write)->"copied.dta"); throw new AssertionError("ambiguous path accepted: "+ambiguous); }
                catch(java.io.IOException expected) {}
            }
            System.out.println("HX_RESEARCH_WORKFLOW_TEST_OK");
        } finally {
            try(java.util.stream.Stream<Path> files=Files.walk(dir)) {
                for(Path p:(Iterable<Path>)files.sorted(Comparator.reverseOrder())::iterator) Files.deleteIfExists(p);
            }
        }
    }
}
