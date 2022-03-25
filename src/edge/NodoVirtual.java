package edge;

import java.util.logging.Logger;
import xdevs.core.modeling.Atomic;
import xdevs.core.modeling.Port;
import util.Input;

/**
 *
 * @author jlrisco
 */
public class NodoVirtual extends Atomic {
    private static final Logger LOGGER = Logger.getLogger(NodoVirtual.class.getName());
    public Port<Input> iInFichero = new Port<>("iInFichero");
    public Port<Input> iInFisico = new Port<>("iInFisico");
    public Port<Input> iInDB = new Port<>("iInDB");

    public Port<Input> oOut = new Port<>("oOut");
    protected Input currentInput = null;
    protected double processingTime;

    public NodoVirtual(String name, double processingTime) {
        super(name);
        super.addInPort(iInFichero);
        super.addInPort(iInFisico);
        super.addInPort(iInDB);
        super.addOutPort(oOut);

        this.processingTime = processingTime;

    }

    @Override
    public void initialize() {
        super.passivate();
    }

    @Override
    public void exit() {
    }

    @Override
    public void deltint() {
        super.passivate();
    }

    @Override
    public void deltext(double e) {
        if (super.phaseIs("passive")) {

            currentInput = iInFichero.getSingleValue();
            if (currentInput != null) {
                System.out.println("NodoVirtual: " + currentInput.toString());

            }
            super.holdIn("active", processingTime);
        }
    }

    @Override
    public void lambda() {
        oOut.addValue(currentInput);
        LOGGER.info(this.name + "- Send value to FogServer" + currentInput);
    }

}
