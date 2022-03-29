package cloud;

import java.util.logging.Logger;

import util.Input;
import xdevs.core.modeling.Atomic;
import xdevs.core.modeling.Port;

public class DataCenter extends Atomic {
    private static final Logger LOGGER = Logger.getLogger(DataCenter.class.getName());

    // PORTINIT
    public Port<Input> in01 = new Port<>("in01");

    public DataCenter(String name) {
        super(name);
        // CONSTRUCTOR
        super.addInPort(in01);
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
        if (!in01.isEmpty()) {
            LOGGER.info("Data Center received:" + in01.getSingleValue().toString());
        }
    }

    @Override
    public void lambda() {
    }
}
