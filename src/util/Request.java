package util;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;

public class Request implements Comparable<Request>{
	// Attributes
    protected LocalDateTime requestDatetime;
    protected String commandRequest;
    protected LocalDateTime initialDatetime;
    protected LocalDateTime endDatetime;
    protected String arguments;
    protected String dataCenter;
    protected String farm;
    protected String sensor;
    protected int seconds;
    
    // Constructors
    public Request(LocalDateTime requestDatetime, String commandRequest, LocalDateTime initialDatetime,	LocalDateTime endDatetime, String arguments){
        this.requestDatetime = requestDatetime;
        this.commandRequest = commandRequest;
        this.initialDatetime = initialDatetime;
        this.endDatetime = endDatetime;
        this.arguments = arguments;
    	String[] args = (this.arguments).split("\\|");
        if( (this.commandRequest.compareTo(CommandRequest.H5)==0) && (args.length == 3) ){
        	this.dataCenter = args[0];
        	this.farm = args[1];
        	this.seconds = Integer.parseInt(args[2]);
        }else if( (	this.commandRequest.compareTo(CommandRequest.OUTLIER_CUBICSPLINE)==0 ||
        			this.commandRequest.compareTo(CommandRequest.OUTLIER_RBF)==0 ||
        			this.commandRequest.compareTo(CommandRequest.OUTLIER_SHEPARD)==0 ) && 
        		 (args.length == 4) ) {
        	this.dataCenter = args[0];
        	this.farm = args[1];
        	this.sensor = args[2];
        	this.seconds = Integer.parseInt(args[3]);
        }else {
        	this.dataCenter = "";
        	this.farm = "";
        	this.sensor = "";
        	this.seconds = 0;
        }
    }
    
    // Methods
    @Override
    public int compareTo(Request r) {
    	LocalDateTime rdt = r.getRequestDatetime();
    	if (this.requestDatetime.isAfter(rdt)) {
    		return 1;
    	} else if (this.requestDatetime.isBefore(rdt)) {
    		return -1;
    	} else {
    		return 0;
    	}
    }

    public static Request parse(String line) throws ParseException {
        String[] parts = line.split(";");
        
        String[] rdate = parts[0].split("-");
        SimpleDateFormat fmt = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        Date rdateAux = fmt.parse(rdate[0] + "-" + rdate[1] + "-" + rdate[2]);
        LocalDateTime requestDatetime = rdateAux.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
        
        String commandRequest = parts[1];
        
        rdate = parts[2].split("-");
        rdateAux = fmt.parse(rdate[0] + "-" + rdate[1] + "-" + rdate[2]);
        LocalDateTime initialDatetime = rdateAux.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
        
        rdate = parts[3].split("-");
        rdateAux = fmt.parse(rdate[0] + "-" + rdate[1] + "-" + rdate[2]);
        LocalDateTime endDatetime = rdateAux.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
        
        String args = parts[4];
        
        Request request = new Request(requestDatetime, commandRequest, initialDatetime, endDatetime, args);
        return request;
    }

	public LocalDateTime getRequestDatetime() {
		return requestDatetime;
	}

	public void setRequestDatetime(LocalDateTime requestDatetime) {
		this.requestDatetime = requestDatetime;
	}

	public String getCommandRequest() {
		return commandRequest;
	}

	public void setCommandRequest(String commandRequest) {
		this.commandRequest = commandRequest;
	}

	public LocalDateTime getInitialDatetime() {
		return initialDatetime;
	}

	public void setInitialDatetime(LocalDateTime initialDatetime) {
		this.initialDatetime = initialDatetime;
	}

	public LocalDateTime getEndDatetime() {
		return endDatetime;
	}

	public void setEndDatetime(LocalDateTime endDatetime) {
		this.endDatetime = endDatetime;
	}

	public String getArguments() {
		return arguments;
	}

	public void setArguments(String arguments) {
		this.arguments = arguments;
	}

	public String getDataCenter() {
		return dataCenter;
	}

	public void setDataCenter(String dataCenter) {
		this.dataCenter = dataCenter;
	}

	public String getFarm() {
		return farm;
	}

	public void setFarm(String farm) {
		this.farm = farm;
	}

	public String getSensor() {
		return sensor;
	}

	public void setSensor(String sensor) {
		this.sensor = sensor;
	}

	public int getSeconds() {
		return seconds;
	}

	public void setSeconds(int seconds) {
		this.seconds = seconds;
	}

	@Override
	public String toString() {
		return "Request [requestDatetime=" + requestDatetime + ", commandRequest=" + commandRequest
				+ ", initialDatetime=" + initialDatetime + ", endDatetime=" + endDatetime + ", arguments=" + arguments
				+ ", dataCenter=" + dataCenter + ", farm=" + farm + ", sensor=" + sensor + ", seconds=" + seconds + "]";
	}
    
}
