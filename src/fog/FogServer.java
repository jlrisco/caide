/*
 * Copyright (C) 2014-2015 José Luis Risco Martín <jlrisco@ucm.es> and 
 * Saurabh Mittal <smittal@duniptech.com>.
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 3 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, see
 * http://www.gnu.org/licenses/
 *
 * Contributors:
 *  - José Luis Risco Martín
 */
package fog;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.logging.Logger;

import util.CommandRequest;
import util.DataMongoDB;
import util.Input;
import util.ManagerMongoDB;
import util.Request;
import xdevs.core.modeling.Atomic;
import xdevs.core.modeling.Port;

public class FogServer extends Atomic {

    private static final Logger LOGGER = Logger.getLogger(FogServer.class.getName());
    
    public Port<Input> in01 = new Port<>("in01");
    public Port<Request> in02 = new Port<>("in02");
    public DataMongoDB mongodb;
    
    /* 
       TODO: Tenemos que pensar qué arroja el Fog hacia el
       DataCenter. De momento simplemente propagamos el dato.
    */
    public Port<Input> out = new Port<>("out");

    /*
      Esto es una técnica habitual que suelo usar para evitarme
      atributos para su uso en deltext.
     */
    protected HashMap<String, LinkedList<Input>> queue = new HashMap<>();
    protected LinkedList<Request> commands = new LinkedList<Request>();

    public FogServer(String name) {
        super(name);
        super.addInPort(in01);
        super.addInPort(in02);
        super.addOutPort(out);
        queue.put(out.getName(), new LinkedList<Input>());
        String nmongodb = "solar_irradiation_fogserver";
        ManagerMongoDB.dropDatabase(nmongodb);
        mongodb = new DataMongoDB(nmongodb);
    }

    @Override
    public void initialize() {
        super.passivate();
    }

    @Override
    public void exit() {
    	mongodb.close();
    }

    @Override
    public void deltint() {
        queue.get(out.getName()).clear();
        super.passivate();
    }

    @Override
    public void deltext(double e) {
    	if (!in02.isEmpty()) {
    		Request r = (Request)in02.getSingleValue();
        	commands.add(r); 
        	LOGGER.info(FogServer.class.getName() + " sends: " + commands.toString());
        }
        if (!in01.isEmpty()) {
        	Collection<Input> data = in01.getValues();
        	queue.get(out.getName()).addAll(data);
            this.save(data);
            performRequest(data);
        }        
        super.activate();
    }

    @Override
    public void lambda() {
        LOGGER.info(FogServer.class.getName() + " sends: " + queue.get(out.getName()).toString());
        out.addValues(queue.get(out.getName()));
    }
    
    private void performRequest(Collection<Input> in) {
    	//Collections.sort(this.commands, Collections.reverseOrder()); 
    	Collections.sort(this.commands); 
    	Object[] lin = in.toArray();
    	//Arrays.sort(lin, Collections.reverseOrder());
    	Arrays.sort(lin);
    	LocalDateTime minDT = ((Input)lin[0]).getDate(); // Get first value
    	try {	        
    		for (Request d : this.commands) {
    			if(!d.getRequestDatetime().isAfter(minDT)) {
    				System.out.println("DTimeMin: " + minDT);
    				Request rq = this.commands.removeFirst();
    				if(d.getCommandRequest().compareTo(CommandRequest.H5)==0) {
    		    		this.generateH5File(rq);
    		    	}else {
    		    		this.calcutateOutliersCubicSpline(rq);
    		    	}
    			}
            }
    	} catch (Exception e) {
			LOGGER.severe(e.getLocalizedMessage());
		}
    }
    
    private void generateH5File(Request r) {
    	System.out.println("h5.....");
    	DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    	String[] parts = (r.getInitialDatetime().format(formatter)).split(" ");
    	String initialDate =  parts[0] + "T" + parts[1] + "+00:00";
    	parts = (r.getEndDatetime().format(formatter)).split(" ");
    	String endDate = parts[0] + "T" + parts[1] + "+00:00";    	 
    	String args = r.getSeconds() + " " + initialDate + " " + endDate;
    	String cmdStr ="C:/Users/Solutio/anaconda3/python.exe c:/empresas/luisfernando/DoctoradoInformatica/Code/simuladorIoT/src/fog/ToResume.py " + args;
    	try {
			Runtime.getRuntime().exec(cmdStr);
		} catch (IOException e) {
			LOGGER.severe(e.getLocalizedMessage());
		}
    }
    
    private void calcutateOutliersCubicSpline(Request r) {
    	System.out.println("cubicspline.....");
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
