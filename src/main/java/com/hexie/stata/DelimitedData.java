package com.hexie.stata;

import java.io.*;
import java.nio.charset.*;
import java.nio.file.*;
import java.util.*;

/** Bounded-memory CSV inspection using logical records and strict decoding. */
final class DelimitedData {
    static Reader reader(Path path, Charset charset) throws IOException {
        return new BufferedReader(new InputStreamReader(Files.newInputStream(path), charset.newDecoder()
                .onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT)));
    }
    static String encoding(Path path, String choice) throws IOException {
        if (choice != null && !choice.isBlank() && !choice.equals("自动识别")) {
            Charset.forName(choice); return choice;
        }
        for (String name : Arrays.asList("UTF-8", "GB18030")) {
            try (Reader r = reader(path, Charset.forName(name))) {
                char[] block = new char[8192];
                while (r.read(block) >= 0) interrupted();
                return name;
            } catch (CharacterCodingException invalid) { /* Try the next encoding. */ }
        }
        return "Windows-1252";
    }
    static void interrupted() throws InterruptedIOException {
        if (Thread.currentThread().isInterrupted()) throw new InterruptedIOException("文件检查已取消。");
    }
    static char delimiter(Path path, Charset charset, String choice) throws IOException {
        switch (choice) {
            case "Tab": return '\t'; case "逗号": return ','; case "分号": return ';';
            case "空格": return ' '; case "竖线": return '|';
            default:
                if (path.toString().toLowerCase(Locale.ROOT).endsWith(".tsv")) return '\t';
                int[] counts = new int[4]; char[] candidates = {',', '\t', ';', '|'};
                try (Reader r = reader(path, charset)) {
                    boolean quoted = false; int c, length = 0;
                    while ((c = r.read()) != -1) {
                        if (++length > 16 * 1024 * 1024) throw new IOException("CSV 表头过长。");
                        if (c == '"') quoted = !quoted;
                        if (!quoted && (c == '\n' || c == '\r')) break;
                        if (!quoted) for (int i=0;i<4;i++) if (c==candidates[i]) counts[i]++;
                    }
                }
                int best=0; for(int i=1;i<4;i++) if(counts[i]>counts[best]) best=i;
                return candidates[best];
        }
    }
    static final class Records implements AutoCloseable {
        final PushbackReader input; final char delimiter;
        boolean first = true;
        Records(Path path, Charset charset, char delimiter) throws IOException {
            input = new PushbackReader(reader(path, charset), 1); this.delimiter=delimiter;
        }
        List<String> next() throws IOException {
            interrupted(); List<String> fields=new ArrayList<>(); StringBuilder field=new StringBuilder();
            boolean quoted=false, closed=false, any=false; int length=0, c;
            while ((c=input.read())!=-1) {
                if(first) { first=false; if(c==0xfeff) continue; }
                any=true;
                if(++length>16*1024*1024) throw new IOException("CSV 单条记录超过 16 MB，请拆分长文本。");
                if((length&8191)==0) interrupted();
                if(quoted) {
                    if(c=='"') {
                        int next=input.read();
                        if(next=='"') field.append('"');
                        else { quoted=false; closed=true; if(next!=-1) input.unread(next); }
                    } else field.append((char)c);
                } else if(c==delimiter || c=='\r' || c=='\n') {
                    fields.add(field.toString()); field.setLength(0); closed=false;
                    if(fields.size()>32767) throw new IOException("CSV 列数超过 32,767。");
                    if(c!=delimiter) {
                        if(c=='\r') { int next=input.read(); if(next!=-1 && next!='\n') input.unread(next); }
                        return fields;
                    }
                } else if(c=='"' && field.length()==0 && !closed) quoted=true;
                else {
                    if(closed || c=='"') throw new IOException("CSV 引号格式无效，请检查字段边界。");
                    field.append((char)c);
                }
            }
            if(quoted) throw new IOException("CSV 引号未闭合。");
            if(!any) return null;
            fields.add(field.toString()); return fields;
        }
        public void close() throws IOException { input.close(); }
    }
    static final class Scan {
        final List<String> names = new ArrayList<>();
        final List<Integer> stringColumns = new ArrayList<>();
        final LinkedHashSet<String> warnings = new LinkedHashSet<>();
        long rows;
        char delimiter;
    }
    static Scan scan(Path path, String encoding, String choice, boolean header) throws IOException {
        Scan result=new Scan(); Charset charset=Charset.forName(encoding);
        result.delimiter=delimiter(path,charset,choice);
        try(Records records=new Records(path,charset,result.delimiter)) {
            List<String> row=records.next(); if(row==null) return result;
            int columns=row.size();
            for(int i=0;i<columns;i++) result.names.add(header?row.get(i):"v"+(i+1));
            boolean[] numeric=new boolean[columns], text=new boolean[columns], zeros=new boolean[columns];
            if(header) row=records.next();
            while(row!=null) {
                if(row.size()==1 && row.get(0).isEmpty()) { row=records.next(); continue; }
                result.rows++;
                if(row.size()!=columns) throw new IOException("CSV 第 "+result.rows+" 条数据记录列数为 "+row.size()+"，应为 "+columns+"。");
                for(int i=0;i<columns;i++) {
                    String value=row.get(i).trim(); if(value.isEmpty()) continue;
                    if(value.matches("[+-]?(?:0[0-9]+|[0-9]{16,})")) zeros[i]=true;
                    if(value.matches("[+-]?(?:\\d+(?:\\.\\d*)?|\\.\\d+)(?:[eE][+-]?\\d+)?")) numeric[i]=true;
                    else text[i]=true;
                }
                row=records.next();
            }
            Set<String> names=new HashSet<>();
            for(int i=0;i<columns;i++) {
                String name=result.names.get(i).trim();
                if(!names.add(name.toLowerCase(Locale.ROOT))) result.warnings.add("发现重复变量名："+name);
                if(zeros[i]) { result.stringColumns.add(i+1); result.warnings.add("第 "+(i+1)+" 列（"+name+"）含前导零或长整数，将按字符串读取。"); }
                if(numeric[i] && text[i]) result.warnings.add("第 "+(i+1)+" 列（"+name+"）同时包含数字和文本。");
                if(!numeric[i] && !text[i]) result.warnings.add("第 "+(i+1)+" 列（"+name+"）完全为空。");
            }
        }
        return result;
    }
}
