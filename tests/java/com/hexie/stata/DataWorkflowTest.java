package com.hexie.stata;

import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.FileTime;
import java.util.*;

public final class DataWorkflowTest {
    private interface Checked { void run() throws Exception; }
    private static void rejects(Checked work) throws Exception {
        try { work.run(); } catch (IOException expected) { return; }
        throw new AssertionError("Expected a protected failure");
    }
    private static void check(boolean result) { if (!result) throw new AssertionError(); }
    public static void main(String[] args) throws Exception {
        Path dir=Files.createTempDirectory("hx-data-workflow-");
        try {
            rejects(()->DataWorkflow.batchOutputs(Arrays.asList(dir.resolve("firm.csv"),dir.resolve("FIRM.xlsx")),dir));
            check(DataWorkflow.batchOutputs(Arrays.asList(dir.resolve("a.csv"),dir.resolve("b.xlsx")),dir).size()==2);
            Path target=dir.resolve("data.dta"), staged=dir.resolve("staged.dta");
            Files.writeString(target,"original");
            rejects(()->new DataWorkflow.OutputTarget(target,false));
            DataWorkflow.OutputTarget approved=new DataWorkflow.OutputTarget(target,true);
            // A failed save must never remove the approved existing file.
            rejects(()->approved.publish(staged));
            check(Files.readString(target).equals("original"));
            Files.writeString(staged,"new data");
            approved.publish(staged);
            check(Files.readString(target).equals("new data") && !Files.exists(staged));
            DataWorkflow.OutputTarget changed=new DataWorkflow.OutputTarget(target,true);
            Files.writeString(target,"user edit after approval");
            Files.setLastModifiedTime(target,FileTime.fromMillis(12345678));
            Files.writeString(staged,"converted");
            rejects(()->changed.publish(staged));
            check(Files.readString(target).equals("user edit after approval"));
            Path later=dir.resolve("appeared.dta");
            DataWorkflow.OutputTarget fresh=new DataWorkflow.OutputTarget(later,false);
            Files.writeString(later,"created by someone else");
            rejects(()->fresh.publish(staged));
            check(Files.readString(later).equals("created by someone else"));
            new DataWorkflow.OutputTarget(dir.resolve("fresh.dta"),false).publish(staged);
            check(Files.readString(dir.resolve("fresh.dta")).equals("converted"));
            rejects(()->new DataWorkflow.OutputTarget(dir,true));
            System.out.println("HX_DATA_WORKFLOW_TEST_OK");
        } finally {
            Path tempRoot=Paths.get(System.getProperty("java.io.tmpdir")).toRealPath();
            if (!dir.toRealPath().getParent().equals(tempRoot) || !dir.getFileName().toString().startsWith("hx-data-workflow-"))
                throw new IOException("Refusing cleanup outside the test temporary directory");
            try (java.util.stream.Stream<Path> entries=Files.walk(dir)) {
                for (Path path : (Iterable<Path>)entries.sorted(Comparator.reverseOrder())::iterator) Files.delete(path);
            }
        }
    }
}
