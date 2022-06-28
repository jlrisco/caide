package util;
import java.text.ParseException;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
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
			append("radiation", data.getRadiacion()
		);
		this.insertDocument("sensors", d);
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
			LocalDateTime ldt = e.getDate("date_time").toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
            data.add(new Input(source, ldt, e.getDouble("radiation")));
		}
		return data;
	}

}
