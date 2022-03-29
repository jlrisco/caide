package edge;

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

import util.Input;
import xdevs.core.modeling.Atomic;
import xdevs.core.modeling.Port;

public class NodoVirtual extends Atomic {
    private static final Logger LOGGER = Logger.getLogger(NodoVirtual.class.getName());
    public Port<Input> out = new Port<>("out");

    protected LocalDateTime start;
    protected LocalDateTime stop;
    protected ArrayList<String> files = new ArrayList<>();
    protected BufferedReader reader = null;
    protected int contadorFicheros = 0;
    protected Input currentInput = null;
    protected Input nextInput = null;
    
    public NodoVirtual(String name, LocalDateTime start, LocalDateTime stop) {
        super(name);
        super.addOutPort(out);
        this.start = start;
        this.stop = stop;
        try {
            File folder = new File("data" + File.separator + "input" + File.separator + name);
            for (File fileEntry : folder.listFiles()) {
                files.add(fileEntry.getPath());
            }
            /*
              TODO: Se asume que los ficheros se organizarán en orden
              por fecha, y que al menos hay un fichero. Esto
              convendría mejorarlo, pero como vamos a incorporar el
              formato H5, puede que no sea necesario.
             */
            Collections.sort(files);
        } catch (Exception e) {
            LOGGER.severe(e.getLocalizedMessage());
        }
    }

    @Override
    public void initialize() {
        currentInput = null;
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
        if (nextInput == null) {
            super.passivate();
        }
        else {
            double sigmaAux = currentInput.getDate().until(nextInput.getDate(), ChronoUnit.SECONDS);
            super.holdIn("active", sigmaAux);
            currentInput = nextInput;
            nextInput = getNextInput();
        }
    }

    @Override
    public void deltext(double e) {
        super.passivate();
    }

    @Override
    public void lambda() {
        out.addValue(currentInput);
    }

    private void updateInputs() {
        while (currentInput == null || currentInput.getDate().isBefore(stop)) { // No se ha leído nunca la primera entrada.
            currentInput = getNextInput();
        }
        nextInput = getNextInput();
    }

    private Input getNextInput() {
        Input input = null;
        try {
            // Se abre reader por primera vez:
            if(reader==null && contadorFicheros<files.size()) {
                reader = new BufferedReader(new FileReader(files.get(contadorFicheros++)));
                reader.readLine(); // Nos saltamos la cabecera
            }
            if (reader==null) {
                return null;
            }
            String line = reader.readLine();
            if (line==null && contadorFicheros<files.size()) { // Hemos llegado al final del fichero
                reader = new BufferedReader(new FileReader(files.get(contadorFicheros++)));
                reader.readLine(); // Nos saltamos la cabecera
                line = reader.readLine();
            }
            else {
                return null;
            }
            input = Input.parse(name, line);
            if (input.getDate().isAfter(stop)) {
                return null;
            }
        } catch (IOException | ParseException ee) {
            LOGGER.severe(ee.getLocalizedMessage());
        }
        return input;
    }
}
