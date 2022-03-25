package util;

public class Input {

    protected String date;
    protected double radiacion;
    protected String nodoVirtual;
    protected String source;

    public Input(String date, double radiacion, String generador) {
        this.date = date;
        this.radiacion = radiacion;
        this.nodoVirtual = generador;
    }

    public double getRadiacion() {
        return radiacion;
    }

    public void setRadiacion(double radiacion) {
        this.radiacion = radiacion;
    }

    public String getGenerador() {
        return nodoVirtual;
    }

    public void setGenerador(String generador) {
        this.nodoVirtual = generador;
    }

    public String getDate() {
        return date;
    }

    public void setDate(String date) {
        this.date = date;
    }

    public void setSource(String source) {
        this.source = source;
    }

    @Override
    public String toString() {
        return "Input [radiacion=" + radiacion + ", Generador=" + nodoVirtual + ", Date=" + date + "]";
    }

    public String toCSV() {
        return date + ";" + nodoVirtual + ";" + radiacion;
    }
}
