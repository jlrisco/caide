package util;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Date;
import java.util.TimeZone;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.bson.Document;
import org.bson.conversions.Bson;

import com.mongodb.client.model.Filters;

public class DataMongoDB extends ManagerMongoDB {
	
	// Constructors
	public DataMongoDB(String database) {
		super(database);
	}
	
	public DataMongoDB(String host, int port, String database) {
		super(host, port, database);
	}
	
	// Methods
	public void insertSensorData(Input data) {
		Document d = new Document();		
		d.append("datacenter", data.getDataCenter()).
			append("farm", data.getFarm()).
			append("sensor", data.getSensor()).
			append("datetime", data.getDate()).
			append("radiation_src", data.getRadiacion()).
			append("outlier", 0).
			append("radiation", data.getRadiacion()
		);
		this.insertDocument("sensors", d);
	}
	
	public void updateSensorData(Input data) {
		Document d = new Document();		
		d.append("outlier", 1).
			append("radiation", data.getRadiacion()
		);
		Document f = new Document();
		f.append("datacenter", data.getDataCenter()).
		append("farm", data.getFarm()).
		append("sensor", data.getSensor()).
		append("datetime", data.getDate());
		this.updateDocument("sensors", f, new Document("$set", d));
	}
	
	public ArrayList<Input> getSensorDataByDate(String source, LocalDateTime initialDate, LocalDateTime endDate){
		ArrayList<Input> data= new ArrayList<Input>();
		String[] s = source.split("\\.");
		Bson filter = 	Filters.and(Filters.eq("datacenter",s[0]),
									Filters.eq("farm",s[1]),
									Filters.eq("sensor", s[2]),
									Filters.gte("datetime", initialDate),
									Filters.lte("datetime", endDate)
						);
		for (Document e : this.getDocuments("sensors", filter)) {           
			Date d = e.getDate("datetime");
			String ISO_FORMAT = "yyyy-MM-dd'T'HH:mm:ss.SSS zzz";
		    TimeZone utc = TimeZone.getTimeZone("UTC");
		    SimpleDateFormat isoFormatter = new SimpleDateFormat(ISO_FORMAT);
	        isoFormatter.setTimeZone(utc);
	        	        
	        DateTimeFormatter formatter = DateTimeFormatter.ofPattern(ISO_FORMAT);
	        LocalDateTime ldt = LocalDateTime.parse(isoFormatter.format(d).toString(), formatter);

            data.add(new Input(source, ldt, e.getDouble("radiation")));
		}
		return data;
	}
	
    public boolean existsIndexDateTimeSensors() {
    	boolean response = false; 
    	for (Document e : this.getListIndexes("sensors")) {
			if(e.getString("name").compareTo("idx_datetime_1")==0) {
				response = true;
				break;
			}
		}
    	return response;	
    }
    
    public boolean createIndexDateTimeSensors() {
    	return this.createIndex("sensors", "idx_datetime");
    }

}
