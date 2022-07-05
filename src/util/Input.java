package util;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;
import java.util.Objects;

public class Input implements Comparable<Input>{

    protected String source;
    protected LocalDateTime date;
    protected Double radiacion;
    protected String dataCenter;
    protected String farm;
    protected String sensor;

    public Input(String source, LocalDateTime date, Double radiacion) {
        this.source = source;
        this.date = date;
        this.radiacion = radiacion;
        String[] args = (this.source).split("\\.");
        if( args.length==3 ) {
        	this.dataCenter = args[0];
        	this.farm = args[1];
        	this.sensor = args[2];
        }else{
        	this.dataCenter = "";
        	this.farm = "";
        	this.sensor = args[args.length-1];
        }
    }

    @Override
    public int compareTo(Input i) {
    	LocalDateTime d = i.getDate();
    	if (this.date.isAfter(d)) {
    		return 1;
    	} else if (this.date.isBefore(d)) {
    		return -1;
    	} else {
    		return 0;
    	}
    }
    
    public static Input parse(String source, String line) throws ParseException {
        String[] parts = line.split(",");
        String[] dates = parts[0].split("-");
        SimpleDateFormat fmt = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        Date dateAux = fmt.parse(dates[0] + "-" + dates[1] + "-" + dates[2]);
        LocalDateTime date = dateAux.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
        Double radiacion = Double.parseDouble(parts[1]);
        Input input = new Input(source, date, radiacion);
        return input;
    }

    public Double getRadiacion() {
        return radiacion;
    }

    public void setRadiacion(Double radiacion) {
        this.radiacion = radiacion;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public LocalDateTime getDate() {
        return date;
    }

    public void setDate(LocalDateTime date) {
        this.date = date;
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

	@Override
	public String toString() {
		return "Input [source=" + source + ", date=" + date + ", radiacion=" + radiacion + ", dataCenter=" + dataCenter
				+ ", farm=" + farm + ", sensor=" + sensor + "]";
	}
	
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Input in = (Input) o;
        return  source.equals(in.source) &&
        		date.isEqual(in.getDate()) &&
        		Double.compare(in.radiacion, radiacion) == 0;
    }

    @Override
    public int hashCode() {
        return Objects.hash(source, date, radiacion);
    }
}
