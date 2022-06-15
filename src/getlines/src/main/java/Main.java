import spoon.Launcher;
import spoon.SpoonAPI;
import spoon.reflect.code.CtBlock;
import spoon.reflect.code.CtStatement;
import spoon.reflect.visitor.filter.TypeFilter;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class Main {

    public static void main(String[] args) {
        final SpoonAPI spoon = new Launcher();

        spoon.getEnvironment().setNoClasspath(true);
        spoon.addInputResource(args[0]);
        spoon.buildModel();

        List<CtBlock> blocks = spoon.getModel().getRootPackage().getElements(new TypeFilter<>(CtBlock.class));

        Set<String> lines = new HashSet<>();
        for (CtBlock block : blocks) {
            for (CtStatement statement : block.getStatements()) {
                if (statement.getPosition().isValidPosition()) {
                    String pos = statement.getPosition().getLine() + "-" + statement.getPosition().getEndLine();
                    if (!lines.contains(pos)) {
                        System.out.println(pos);
                        lines.add(pos);
                    }
                }
            }
        }
    }
}