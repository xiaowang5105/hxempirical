package com.hexie.stata;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.regex.*;
import java.util.zip.*;

/** Explicitly exported project archive, with copied file dependencies and a manifest. */
final class ProjectBundle {
    static void write(ResearchProject project, Path output) throws IOException {
        Map<String,Path> files=new LinkedHashMap<>();
        files.put(project.file.getFileName().toString(),project.file);
        files.put(project.baseline,project.asset(project.baseline));
        files.put(project.current,project.asset(project.current));
        for(ResearchProject.Run model:project.models())
            for(String suffix:Arrays.asList(".ster",".tsv",".sample"))
                files.put(model.model+suffix,project.asset(model.model+suffix));
        String script=project.exportDo();
        if(!project.workingDirectory.isBlank()) script=script.replace("cd "+ResearchProject.stataQuote(project.workingDirectory)+"\n", "");
        script=script.replace(ResearchProject.stataQuote(project.asset(project.baseline).toString()),ResearchProject.stataQuote(project.baseline));
        Map<Path,String> external=new LinkedHashMap<>();
        StringBuilder notes=new StringBuilder("# Project bundle\n\nExtract the ZIP into a new folder. In Stata, cd to that folder and run replay.do.\n")
                .append("Open the .hxproj file to restore the saved current data and model settings.\n")
                .append("replay.do recreates successful recorded outputs inside this bundle when their paths were resolved.\n")
                .append("Review the script before running. Relative cd commands, macros, unquoted paths and commands with network dependencies require manual review.\n\n")
                .append("This archive includes project data and referenced local data files; review contents before sharing.\n\n");
        Pattern quoted=Pattern.compile("\"([^\"\\r\\n]+\\.(?:dta|csv|tsv|txt|xlsx|xls))\"",Pattern.CASE_INSENSITIVE);
        Matcher matcher=quoted.matcher(script); StringBuffer rewritten=new StringBuffer();
        while(matcher.find()) {
            String value=matcher.group(1);
            if(value.equals(project.baseline)) continue;
            if(value.contains("`") || value.contains("$")) { notes.append("Unresolved macro path: ").append(value).append('\n'); continue; }
            Path source;
            try {
                source=Path.of(value);
                if(!source.isAbsolute()) source=Path.of(project.workingDirectory).resolve(source);
                source=source.toAbsolutePath().normalize();
            } catch(InvalidPathException e) { notes.append("Unresolved path: ").append(value).append('\n'); continue; }
            if(!Files.isRegularFile(source)) { notes.append("Missing or generated file: ").append(value).append('\n'); continue; }
            String relative=external.get(source);
            if(relative==null) {
                relative="external/file-"+(external.size()+1)+source.getFileName().toString().substring(source.getFileName().toString().lastIndexOf('.'));
                external.put(source,relative); files.put(relative,source);
                notes.append("Copied ").append(source).append(" -> ").append(relative).append('\n');
            }
            matcher.appendReplacement(rewritten,Matcher.quoteReplacement('"'+relative+'"'));
        }
        matcher.appendTail(rewritten);
        Path temporary=Files.createTempFile(output.toAbsolutePath().getParent(),".hx-bundle-",".tmp");
        try {
            StringBuilder manifest=new StringBuilder("SHA256\tFile\n");
            try(ZipOutputStream zip=new ZipOutputStream(Files.newOutputStream(temporary))) {
                byte[] buffer=new byte[65536];
                for(Map.Entry<String,Path> file:files.entrySet()) {
                    DelimitedData.interrupted();
                    zip.putNextEntry(new ZipEntry(file.getKey().replace('\\','/')));
                    MessageDigest digest;
                    try { digest=MessageDigest.getInstance("SHA-256"); } catch(NoSuchAlgorithmException e) { throw new IOException(e); }
                    try(InputStream input=Files.newInputStream(file.getValue())) {
                        int count; while((count=input.read(buffer))!=-1) { zip.write(buffer,0,count); digest.update(buffer,0,count); DelimitedData.interrupted(); }
                    }
                    zip.closeEntry();
                    for(byte b:digest.digest()) manifest.append(String.format("%02x",b&255));
                    manifest.append('\t').append(file.getKey()).append('\n');
                }
                entry(zip,"replay.do",rewritten.toString());
                entry(zip,"README.txt",notes.toString());
                entry(zip,"SHA256.tsv",manifest.toString());
                entry(zip,"environment.txt",project.environment+"\nThird-party commands must be installed separately; their original versions are not pinned.\n");
            }
            Files.move(temporary,output,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
        } finally { Files.deleteIfExists(temporary); }
    }
    private static void entry(ZipOutputStream zip,String name,String text) throws IOException {
        zip.putNextEntry(new ZipEntry(name)); zip.write(text.getBytes(StandardCharsets.UTF_8)); zip.closeEntry();
    }
}
