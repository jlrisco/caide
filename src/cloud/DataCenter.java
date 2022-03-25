package cloud;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Collection;
import java.util.Iterator;
import java.util.logging.Logger;

import xdevs.core.modeling.Atomic;
import xdevs.core.modeling.Port;
import util.Input;
import fog.FogServer;

public class DataCenter extends Atomic {
    private static final Logger LOGGER = Logger.getLogger(DataCenter.class.getName());

    // PORTINIT
    protected Port<Input> iInFogserver1 = new Port<>("iInFogserver1");
    protected Input currentInputFogserver1 = null;

    protected Port<Input> iInFogserver2 = new Port<>("iInFogserver2");
    protected Input currentInputFogserver2 = null;

    protected Port<Input> oOutDataCenter = new Port<>("oOutDataCenter");
    protected double processingTime;
    protected Input currentInput = null;

    public DataCenter(String name, double processingTime) {
        super(name);
        // CONSTRUCTOR
        super.addInPort(iInFogserver1);
        super.addInPort(iInFogserver2);

        // super.addInPort(iInDataCenter);
        super.addOutPort(oOutDataCenter);
        this.processingTime = processingTime;

    }

    @Override
    public void deltint() {
        super.passivate();
    }

    @Override
    public void deltext(double e) {
        if (super.phaseIs("passive")) {

            // DELTEXT
            Collection<Input> collectionFogserver1 = iInFogserver1.getValues();

            if (collectionFogserver1 != null) {
                try {
                    storeCollection(collectionFogserver1);
                } catch (IOException e1) {
                    e1.printStackTrace();
                }
            }

            Collection<Input> collectionFogserver2 = iInFogserver2.getValues();

            if (collectionFogserver2 != null) {
                try {
                    storeCollection(collectionFogserver2);
                } catch (IOException e1) {
                    e1.printStackTrace();
                }
            }

            if (currentInput != null) {
                System.out.println("DataCenter: " + currentInput.toString());
            }
            super.holdIn("active", processingTime);
        }

    }

    @Override
    public void lambda() {
    }

    @Override
    public void initialize() {
        super.passivate();

    }

    @Override
    public void exit() {
    }

    public void storeCollection(Collection<Input> collection) throws IOException {
        LOGGER.info(this.name + "- Storing data in file");
        BufferedWriter writerOutliers = new BufferedWriter(new FileWriter("sensorDataOutliers.csv", true));
        BufferedWriter writer = new BufferedWriter(new FileWriter("sensorData.csv", true));
        boolean firstOutliers = true;
        boolean first = true;
        Iterator<Input> it = collection.iterator();
        boolean hasEndLine = it.hasNext() ? true : false;
        while (it.hasNext()) {
            // Print sensor data + outliers
            Input row = it.next();
            if (firstOutliers) {
                writerOutliers.append(row.toCSV());
                firstOutliers = false;
            } else {
                writerOutliers.newLine();
                writerOutliers.append(row.toCSV());
            }
            // Print only sensor data
            String gen = row.getGenerador();
            if (!FogServer.CUBICSPLINE.equals(gen) && !FogServer.RBF.equals(gen) && !FogServer.SHEPARD.equals(gen)) {
                if (first) {
                    writer.append(row.toCSV());
                    first = false;
                } else {
                    writer.newLine();
                    writer.append(row.toCSV());
                }
            }
        }
        if (hasEndLine) {
            writerOutliers.newLine();
            writer.newLine();
        }
        writerOutliers.close();
        writer.close();
    }

}
