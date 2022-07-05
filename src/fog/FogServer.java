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
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.logging.Logger;

import org.bson.Document;

import util.CommandRequest;
import util.DataMongoDB;
import util.Input;
import util.ManagerMongoDB;
import util.Request;
import util.OrderByRadiation;
import xdevs.core.modeling.Atomic;
import xdevs.core.modeling.Port;

import smile.interpolation.CubicSplineInterpolation1D;

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
    	Collections.sort(this.commands); 
    	Object[] lin = in.toArray();
    	Arrays.sort(lin);
    	LocalDateTime minDT = ((Input)lin[0]).getDate(); // Get first value
    	try {	        
    		for(Iterator<Request> rl = this.commands.iterator(); rl.hasNext();) {
    		    Request data = rl.next();
    		    if(!data.getRequestDatetime().isAfter(minDT)) {
    				System.out.println("DTimeMin: " + minDT);
    				rl.remove();
    				if(data.getCommandRequest().compareTo(CommandRequest.H5)==0) {
    		    		this.generateH5File(data);
    		    	}else if(data.getCommandRequest().compareTo(CommandRequest.OUTLIER_CUBICSPLINE)==0){
    		    		this.calcutateOutliersCubicSpline(data);
    		    	} else {
    		    		System.out.println("Comando no reconocido.");
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
    	// Create index if this is not exists
    	if(!mongodb.existsIndexDateTimeSensors()) {
    		mongodb.createIndexDateTimeSensors();
    	}
    	// Retrieve data
    	String source = r.getDataCenter()+'.'+r.getFarm()+'.'+r.getSensor();
    	LocalDateTime lowLimit = r.getInitialDatetime();
    	LocalDateTime highLimit = lowLimit.plusSeconds(r.getSeconds()-1).isAfter(r.getEndDatetime())?r.getEndDatetime():lowLimit.plusSeconds(r.getSeconds()-1);
    	List<Input> dataOutliers = new ArrayList<Input>();
    	while( !lowLimit.isAfter(r.getEndDatetime()) ) {
    		List<Input> data = mongodb.getSensorDataByDate(source, lowLimit, highLimit);
    		//Collections.sort(data, new OrderByRadiation());
    		if(data.size() > 1) {
    			dataOutliers = this.getOutliers(data);
    	    	for (Input d : dataOutliers) {
    	    		System.out.println(d);
    	    		this.setOutlier(d);
    	    	}
    		}
    			    	
	    	lowLimit = highLimit.plusSeconds(1);
	    	highLimit = lowLimit.plusSeconds(r.getSeconds()-1).isAfter(r.getEndDatetime())?r.getEndDatetime():lowLimit.plusSeconds(r.getSeconds()-1);
	    	System.out.println("--------------------");
    	}
    }

    //Correction outliers
    private void setOutlier(Input in) {
    	String source = in.getDataCenter()+'.'+in.getFarm()+'.'+in.getSensor();
    	LocalDateTime lowLimit = in.getDate().minusSeconds(3);
    	LocalDateTime highLimit = in.getDate().plusSeconds(4);
    	List<Input> data = mongodb.getSensorDataByDate(source, lowLimit, highLimit);
		double[] ty = new double[7];
		// First value ratio for previus
		double valueRatio;
		Input search = this.searchDateTime(in.getDate().minusSeconds(1), data);
		if (search != null) {
			valueRatio = search.getRadiacion().doubleValue();
		} else {
			search = this.searchDateTime(in.getDate().plusSeconds(1), data);
			valueRatio = search.getRadiacion().doubleValue();
		}
		// Three previus values
		ty[0] = valueRatio;
    	for(int i = 1; i < 3; i++) {
    		search = this.searchDateTime(in.getDate().minusSeconds(i+1), data);
    		if (search != null) {
    			valueRatio = search.getRadiacion().doubleValue();
			} 
    		ty[i] = valueRatio;
    	}
    	// First value ratio for next
		search = this.searchDateTime(in.getDate().plusSeconds(1), data);
		if (search != null) {
			valueRatio = search.getRadiacion().doubleValue();
		} else {
			search = this.searchDateTime(in.getDate().minusSeconds(1), data);
			valueRatio = search.getRadiacion().doubleValue();
		}
    	// Four next values
		ty[3] = valueRatio;
    	for(int i = 4; i < 7; i++) {
    		search = this.searchDateTime(in.getDate().plusSeconds(i-2), data);
    		if (search != null) {
    			valueRatio = search.getRadiacion().doubleValue();
			} 
    		ty[i] = valueRatio;
    	}
    	double[] x = {0, 1, 2, 3, 4, 5, 6};
    	double[] y = {ty[2],ty[1], ty[0], ty[3], ty[4], ty[5], ty[6]};
    	
    	CubicSplineInterpolation1D spline = new CubicSplineInterpolation1D(x, y);
	    double[][] zz = new double[61][2];
	    for (int i = 0; i <= 60; i++) {
	    	zz[i][0] = i * 0.1;
	        zz[i][1] = spline.interpolate(zz[i][0]);
	    }
	    
	    System.out.println("corregido: " + zz[30][1]);
	    mongodb.updateSensorData( new Input(source, in.getDate(),zz[30][1]) );
		
    }
    
    // Searching Input
    private Input searchDateTime(LocalDateTime ldt, List<Input> data) {
    	Input result = null;
    	for(Input i : data) {
    		if( ldt.isEqual(i.getDate()) ){
    			result = i;
    			break;
    		}
    	}
    	return result;
    }
    
    //Detection outliers http://www.mathwords.com/o/outlier.htm
    private List<Input> getOutliers(List<Input> inputs) {
    	Collections.sort(inputs, new OrderByRadiation());
        List<Input> outputs = new ArrayList<Input>();
        List<Input> data1 = new ArrayList<Input>();
        List<Input> data2 = new ArrayList<Input>();
        if (inputs.size() % 2 == 0) {
            data1 = inputs.subList(0, inputs.size() / 2);
            data2 = inputs.subList(inputs.size() / 2, inputs.size());
        }else {
            data1 = inputs.subList(0, (inputs.size() / 2) + 1);
            data2 = inputs.subList( (inputs.size() / 2) + 1, inputs.size());
        }
        double q1 = getMedian(data1);
        double q3 = getMedian(data2);
        double iqr = q3 - q1;       
        if(iqr < 0) {
        	iqr = -iqr;
        }
        //System.out.println("iqr: " + iqr);
        double lowerFence = q1 - 2.5 * iqr;
        //System.out.println("lowerFence: " + lowerFence);
        double upperFence = q3 + 2.5 * iqr;
        for (Input i : inputs) {
            if (i.getRadiacion() < lowerFence || i.getRadiacion() > upperFence) {
            	outputs.add(i);
            }
        }
        return outputs;
    }
    
    private static double getMedian(List<Input> data) {
        if (data.size() % 2 == 0)
            return (data.get(data.size() / 2).getRadiacion() + data.get(data.size() / 2 - 1).getRadiacion()) / 2;
        else
            return data.get(data.size() / 2).getRadiacion();
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
