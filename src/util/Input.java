package util;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;

public class Input {

    protected String source;
    protected LocalDateTime date;
    protected Double radiacion;

    public Input(String source, LocalDateTime date, Double radiacion) {
        this.source = source;
        this.date = date;
        this.radiacion = radiacion;
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

    @Override
    public String toString() {
        return "Input [source=" + source + ", date=" + date.toString() + ", radiaction=" + radiacion + "]";
    }
}
