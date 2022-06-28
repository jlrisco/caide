package cloud;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Collection;
import java.util.logging.Level;
import java.util.logging.Logger;

import util.DataMongoDB;
import util.Input;
import util.ManagerMongoDB;
import xdevs.core.modeling.Atomic;
import xdevs.core.modeling.Port;

public class DataCenter extends Atomic {
    private static final Logger LOGGER = Logger.getLogger(DataCenter.class.getName());

    // PORTINIT
    public Port<Input> in01 = new Port<>("in01");
    
    // Mongo
    public DataMongoDB mongodb;
    
    public DataCenter(String name) {
        super(name);
        // CONSTRUCTOR
        super.addInPort(in01);
        
        String nmongodb = "solar_irradiation_datacenter";
        ManagerMongoDB.dropDatabase(nmongodb);
        mongodb = new DataMongoDB(nmongodb);
    }

    @Override
    public void initialize() {
        super.passivate();

    }

    @Override
    public void exit() {
    this.mongodb.close();
    }

    @Override
    public void deltint() {
        super.passivate();
    }

    @Override
    public void deltext(double e) {
        if (!in01.isEmpty()) {
            LOGGER.info("Data Center received:" + in01.getValues().toString());
            this.save(in01.getValues());
        }
    }

    @Override
    public void lambda() {
    }
    
    public void save(Collection<Input> iData){    	
    	try {	        
    		for (Input d : iData) {
    			mongodb.insertSensorData(d);
            }
    	} catch (Exception e) {
			LOGGER.severe(e.getLocalizedMessage());
		}
    } 
}
