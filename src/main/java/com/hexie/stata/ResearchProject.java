package com.hexie.stata;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.util.*;
import java.util.regex.*;

/** Portable project journal, independent of Swing and Stata's live API. */
final class ResearchProject {
    final Path file;
    String assets, baseline = "", current = "", workingDirectory = "", rng = "", rngState = "";
    String currentRng = "", currentRngState = "";
    String sortRngState = "", currentSortRngState = "";
    final List<Run> runs = new ArrayList<>();
    boolean dirty;

    static final class Run {
        String command = "", settings = "", output = "", time = "", model = "", signature = "", vce = "";
        int rc;
        double n = Double.NaN, r2 = Double.NaN;
    }

    ResearchProject(Path file) {
        this.file = file.toAbsolutePath().normalize();
        this.assets = "hx-assets-" + UUID.randomUUID();
    }

    Path asset(String relative) throws IOException {
        Path parent = file.getParent();
        Path path = parent.resolve(relative).normalize();
        if (relative.isBlank() || !path.startsWith(parent.resolve(assets)) || !path.startsWith(parent)
                || Paths.get(relative).isAbsolute() || !path.startsWith(parent.resolve(assets).normalize())) {
            throw new IOException("项目资源路径无效：" + relative);
        }
        if (Files.exists(path) && !path.toRealPath().startsWith(parent.toRealPath())) {
            throw new IOException("项目资源位于项目目录之外。");
        }
        return path;
    }

    String newAsset(String suffix) { return assets + "/" + UUID.randomUUID() + suffix; }

    void save() throws IOException {
        Properties p = new Properties();
        p.setProperty("format", "HXPROJECT-1");
        p.setProperty("assets", assets);
        p.setProperty("baseline", baseline); p.setProperty("current", current);
        p.setProperty("workingDirectory", workingDirectory);
        p.setProperty("rng", rng); p.setProperty("rngState", rngState);
        p.setProperty("currentRng", currentRng); p.setProperty("currentRngState", currentRngState);
        p.setProperty("sortRngState", sortRngState); p.setProperty("currentSortRngState", currentSortRngState);
        p.setProperty("count", Integer.toString(runs.size()));
        for (int i = 0; i < runs.size(); i++) {
            Run r = runs.get(i); String key = "run." + i + ".";
            p.setProperty(key + "command", r.command); p.setProperty(key + "settings", r.settings);
            p.setProperty(key + "output", r.output); p.setProperty(key + "time", r.time);
            p.setProperty(key + "model", r.model); p.setProperty(key + "signature", r.signature);
            p.setProperty(key + "vce", r.vce); p.setProperty(key + "rc", Integer.toString(r.rc));
            p.setProperty(key + "n", Double.toString(r.n)); p.setProperty(key + "r2", Double.toString(r.r2));
        }
        StringWriter writer = new StringWriter();
        p.store(writer, "HX Empirical research project");
        atomicWrite(file, writer.toString());
        dirty = false;
    }

    static ResearchProject load(Path file) throws IOException {
        if (Files.size(file) > 64L * 1024 * 1024) throw new IOException("项目文件超过 64 MB。");
        Properties p = new Properties();
        try (Reader reader = Files.newBufferedReader(file, StandardCharsets.UTF_8)) { p.load(reader); }
        if (!"HXPROJECT-1".equals(p.getProperty("format"))) throw new IOException("无法识别项目格式。");
        ResearchProject project = new ResearchProject(file);
        project.assets = p.getProperty("assets", "");
        if (!project.assets.matches("hx-assets-[0-9a-f-]{36}")) throw new IOException("项目资源目录无效。");
        project.baseline = p.getProperty("baseline", ""); project.current = p.getProperty("current", "");
        project.workingDirectory = p.getProperty("workingDirectory", "");
        project.rng = p.getProperty("rng", ""); project.rngState = p.getProperty("rngState", "");
        project.currentRng = p.getProperty("currentRng", project.rng);
        project.currentRngState = p.getProperty("currentRngState", project.rngState);
        project.sortRngState = p.getProperty("sortRngState", "");
        project.currentSortRngState = p.getProperty("currentSortRngState", project.sortRngState);
        if (!Files.isRegularFile(project.asset(project.baseline)) || !Files.isRegularFile(project.asset(project.current)))
            throw new IOException("项目数据快照缺失；请将 .hxproj 与 hx-assets 目录一同移动。");
        try {
            int count = Integer.parseInt(p.getProperty("count", "0"));
            if (count < 0 || count > 10000) throw new IOException("项目步骤数量无效。");
            for (int i = 0; i < count; i++) {
                Run r = new Run(); String k = "run." + i + ".";
                r.command = p.getProperty(k + "command", ""); r.settings = p.getProperty(k + "settings", "");
                r.output = p.getProperty(k + "output", ""); r.time = p.getProperty(k + "time", "");
                r.model = p.getProperty(k + "model", ""); r.signature = p.getProperty(k + "signature", "");
                r.vce = p.getProperty(k + "vce", ""); r.rc = Integer.parseInt(p.getProperty(k + "rc", "0"));
                r.n = Double.parseDouble(p.getProperty(k + "n", "NaN")); r.r2 = Double.parseDouble(p.getProperty(k + "r2", "NaN"));
                if (!r.model.isBlank()) project.asset(r.model + ".ster");
                project.runs.add(r);
            }
        } catch (IllegalArgumentException e) { throw new IOException("项目记录格式无效。", e); }
        return project;
    }

    Run add(String command, String settings, String output, int rc, double n, double r2) {
        Run run = new Run(); run.command = command; run.settings = settings;
        run.output = output.length() > 65536 ? output.substring(0, 65536) + "\n[项目仅保留输出前 64 KB]" : output;
        run.rc = rc; run.n = n; run.r2 = r2; run.time = LocalDateTime.now().toString();
        runs.add(run); dirty = true; return run;
    }

    List<Run> models() {
        List<Run> result = new ArrayList<>();
        for (Run run : runs) if (!run.model.isBlank()) result.add(run);
        return result;
    }

    String exportDo() throws IOException {
        StringBuilder s = new StringBuilder("version 17.0\nset more off\n");
        if (!workingDirectory.isBlank()) s.append("cd ").append(stataQuote(workingDirectory)).append('\n');
        s.append("use ").append(stataQuote(asset(baseline).toString())).append(", clear\n");
        if (!rng.isBlank()) s.append("set rng ").append(rng).append('\n');
        if (!rngState.isBlank()) s.append("set rngstate ").append(rngState).append('\n');
        if (!sortRngState.isBlank()) s.append("set sortrngstate ").append(sortRngState).append('\n');
        s.append("\n* Recorded steps start from the saved project baseline.\n");
        for (Run r : runs) {
            s.append("\n* ").append(r.time).append("; observed return code ").append(r.rc).append('\n');
            if (r.rc != 0) s.append("capture noisily ");
            s.append(r.command).append('\n');
        }
        return s.toString();
    }

    Map<String,String> coefficients(Run run) throws IOException {
        Map<String,String> values = new LinkedHashMap<>();
        for (String line : Files.readAllLines(asset(run.model + ".tsv"), StandardCharsets.UTF_8)) {
            String[] columns = line.split("\t");
            if (columns.length == 3 && !columns[0].equals("term"))
                values.put(columns[0], columns[1].trim() + " (" + columns[2].trim() + ")");
        }
        return values;
    }

    boolean sameSamples(List<Run> models) throws IOException {
        if (models.size() < 2) return true;
        Run first = models.get(0);
        byte[] reference = Files.readAllBytes(asset(first.model + ".sample"));
        for (Run model : models) {
            if (!first.signature.equals(model.signature) || !Arrays.equals(reference, Files.readAllBytes(asset(model.model + ".sample")))) return false;
        }
        return true;
    }

    /** Generate a reviewable common-sample rerun on the saved current data. */
    String commonSampleDo(List<Run> models) throws IOException {
        if (models.size() < 2) throw new IOException("请至少保存两个模型。");
        String signature = models.get(0).signature;
        for (Run r : models) {
            if (signature.isBlank() || !signature.equals(r.signature))
                throw new IOException("这些模型的数据内容或行顺序不同，请在同一数据版本下重新估计后比较。");
            withSample(r.command, "`hx_common'"); // validate before creating an artifact
        }
        StringBuilder s = new StringBuilder("version 17.0\nset more off\nuse ");
        s.append(stataQuote(asset(current).toString())).append(", clear\nquietly datasignature\n");
        s.append("assert r(datasignature) == ").append(stataQuote(signature)).append('\n');
        s.append("tempvar hx_common\ngenerate byte `hx_common' = 1\n");
        int i = 0;
        for (Run r : models) {
            s.append(r.command).append('\n');
            s.append("quietly replace `hx_common' = `hx_common' & e(sample)\n");
        }
        s.append("quietly count if `hx_common'\nassert r(N) > 0\n");
        for (Run r : models) {
            s.append('\n').append(withSample(r.command, "`hx_common'")).append('\n');
            s.append("assert e(sample) == `hx_common'\n");
            s.append("estimates store HX_common_M").append(++i).append('\n');
        }
        s.append("\nestimates table");
        for (int j=1;j<=i;j++) s.append(" HX_common_M").append(j);
        s.append(", b(%9.4f) se(%9.4f) stats(N r2)\n");
        return s.toString();
    }

    static String withSample(String command, String sample) throws IOException {
        // Intentionally bounded to plain linear models; reject prefixes/macros and complex bodies.
        if (!command.matches("(?s)^(regress|areg|xtreg|reghdfe)\\s+.*") || command.contains("\n")
                || command.contains(";") || command.contains("`") || command.contains("$"))
            throw new IOException("共同样本导出支持普通 regress、areg、xtreg、reghdfe 命令；复杂命令请手动设置样本。");
        boolean quoted=false; int comma=command.length();
        for(int i=0;i<command.length();i++) {
            if(command.charAt(i)=='"') quoted=!quoted;
            if(command.charAt(i)==',' && !quoted) { comma=i; break; }
        }
        String body=command.substring(0,comma), options=command.substring(comma);
        int condition=clauseIndex(body, "if");
        if(condition>=0) {
            int start=condition, expression=condition+2;
            String rest=body.substring(expression);
            int end=tailIndex(rest);
            return body.substring(0,start).stripTrailing()+" if ("+rest.substring(0,end).trim()+") & "+sample+(end<rest.length()?" "+rest.substring(end):"")+options;
        }
        int end=tailIndex(body);
        return body.substring(0,end).stripTrailing()+" if "+sample+(end<body.length()?" "+body.substring(end):"")+options;
    }

    private static int tailIndex(String body) {
        int in=clauseIndex(body,"in"), weight=clauseIndex(body,"[");
        return Math.min(in<0?body.length():in,weight<0?body.length():weight);
    }

    private static int clauseIndex(String text,String token) {
        boolean quoted=false; int depth=0;
        for(int i=0;i<text.length();i++) {
            char c=text.charAt(i);
            if(c=='"') { quoted=!quoted; continue; }
            if(quoted) continue;
            if(c=='(') depth++;
            if(c==')') depth--;
            if(depth==0 && text.startsWith(token,i) && (i==0 || Character.isWhitespace(text.charAt(i-1)))
                    && (token.equals("[") || i+token.length()==text.length() || Character.isWhitespace(text.charAt(i+token.length())))) return i;
        }
        return -1;
    }

    static String stataQuote(String value) throws IOException {
        if (value.contains("\"") || value.contains("\n") || value.contains("\r") || value.contains("`") || value.contains("$"))
            throw new IOException("路径含有 Stata 无法安全引用的字符。");
        return "\"" + value.replace('\\','/') + "\"";
    }

    static void atomicWrite(Path file, String text) throws IOException {
        Path temp = Files.createTempFile(file.toAbsolutePath().getParent(), ".hx-write-", ".tmp");
        try {
            Files.writeString(temp, text, StandardCharsets.UTF_8);
            try { Files.move(temp, file, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING); }
            catch (AtomicMoveNotSupportedException e) { Files.move(temp,file,StandardCopyOption.REPLACE_EXISTING); }
        } finally { Files.deleteIfExists(temp); }
    }
}
