package fog;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.text.ParseException;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Collections;
import java.util.logging.Logger;

import util.Request;
import xdevs.core.modeling.Atomic;
import xdevs.core.modeling.Port;

public class Service extends Atomic {
    private static final Logger LOGGER = Logger.getLogger(Service.class.getName());
    public Port<Request> out = new Port<>("out");

    protected LocalDateTime start;
    protected LocalDateTime stop;
    protected BufferedReader reader = null;
    protected Request currentRequest = null;
    protected Request nextRequest = null;
    
    public Service(String name, LocalDateTime start, LocalDateTime stop) {
        super(name);
        super.addOutPort(out);
        this.start = start;
        this.stop = stop;
        try {
            reader = new BufferedReader(new FileReader("." + File.separator + "data" + File.separator + "input" + File.separator + "services_data" + File.separator + name));
            reader.readLine(); // Nos saltamos la cabecera
        } catch (Exception e) {
            LOGGER.severe(e.getLocalizedMessage());
        }
    }

    @Override
    public void initialize() {
        currentRequest = null;
        updateInputs();
        this.holdIn("active", 0);
    }

    @Override
    public void exit() {
        try {
            reader.close();
        } catch (IOException e) {
            LOGGER.severe(e.getLocalizedMessage());
        }
    }

    @Override
    public void deltint() {
        if (nextRequest == null) {
            super.passivate();
        }
        else {
            double sigmaAux = currentRequest.getRequestDatetime().until(nextRequest.getRequestDatetime(), ChronoUnit.SECONDS);
            super.holdIn("active", sigmaAux);
            currentRequest = nextRequest;
            nextRequest = getNextRequest();
        }
    }

    @Override
    public void deltext(double e) {
        super.passivate();
    }

    @Override
    public void lambda() {
        LOGGER.info(Service.class.getName() + " sends: " + currentRequest.toString());
        out.addValue(currentRequest);
    }

    private void updateInputs() {
    	// No se ha leído nunca la primera entrada.
        while (currentRequest == null || currentRequest.getRequestDatetime().isBefore(start)) {
            currentRequest = getNextRequest();
        }
        nextRequest = getNextRequest();
    }

    private Request getNextRequest() {
        Request request = null;
        try {
            String line = reader.readLine();
            if (line==null) { 
                return null;
            }
            request = Request.parse(line);
            if (request.getRequestDatetime().isAfter(stop)) { // No quedan más datos en el intervalo de simulación.
                return null;
            }
        } catch (IOException | ParseException ee) {
            LOGGER.severe(ee.getLocalizedMessage());
        }
        return request;
    }
}
