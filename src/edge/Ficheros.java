package edge;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.logging.Logger;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;

import xdevs.core.modeling.Atomic;
import util.Input;
import xdevs.core.modeling.Port;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;

public class Ficheros extends Atomic {
    private static final Logger LOGGER = Logger.getLogger(Ficheros.class.getName());
    public Port<Input> oOut = new Port<>("oOut");

    protected ArrayList<String> files = new ArrayList<>();
    protected BufferedReader reader = null;
    protected int contadorFicheros = 0;
    String line = null;

    public Ficheros(String name, String path, LocalDateTime start, LocalDateTime stop) {
        super(name);
        super.addOutPort(oOut);
        try {
            File folder = new File(path);
            for (File fileEntry : folder.listFiles()) {
                files.add(fileEntry.getPath());
            }
            /*
              TODO: Se asume que los ficheros se organizarán en orden
              por fecha, y que al menos hay un fichero.
             */
            Collections.sort(files);
        } catch (Exception e) {
            LOGGER.severe(e.getLocalizedMessage());
        }
    }

    @Override
    public void initialize() {
        Input currentInput = null;
        try {
            reader = new BufferedReader(new FileReader(files.get(contadorFicheros)));
            // TODO: Hay que encontrar el primer Input >= start
            // Continuar aquí ...
            line = reader.readLine(); // Se salta la primera linea
            line = reader.readLine();
            if (line != null) {
                String[] arrOfStr = line.split(",");
                try {
                    datosEntrada = new Input(arrOfStr[0], Double.parseDouble(arrOfStr[1]), name);
                } catch (Exception e) {
                    e.printStackTrace();
                    LOGGER.warning(this.name + "- Exception parsing radiation value to double:" + arrOfStr[1]);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        if (datosEntrada.getDate() != null) {
            try {
                initialDate = parseDate(datosEntrada.getDate()).getTime();
            } catch (Exception e) {
                e.printStackTrace();
                LOGGER.warning(this.name + "- Exception parsing date:" + datosEntrada.getDate());
            }
            if ((startDate <= initialDate && initialDate <= endDate) || startDate == 0) {
                inputToSend = datosEntrada;
            }
        }

        this.holdIn("active", 0);

    }

    @Override
    public void exit() {
        try {
            reader.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void deltint() {
        boolean existOtherFile = true;
        Input datosEntrada = null;
        try {
            line = reader.readLine();
            if (line == null) {
                existOtherFile = nextFile();
            }
            if (!existOtherFile) {
                this.passivate();
            }
            if (line != null && existOtherFile) {
                String[] arrOfStr = line.split(",");
                try {
                    datosEntrada = new Input(arrOfStr[0], Double.parseDouble(arrOfStr[1]), name);

                    if (datosEntrada.getDate() != null) {
                        try {
                            actualDate = parseDate(datosEntrada.getDate()).getTime();
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                        if ((startDate <= initialDate && initialDate <= endDate) || startDate == 0) {
                            inputToSend = datosEntrada;
                        }
                    }
                    double period = (actualDate - initialDate) / 1000;
                    this.holdIn("active", period);
                    initialDate = actualDate;
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

    }

    @Override
    public void deltext(double e) {
        super.passivate();
    }

    @Override
    public void lambda() {

        LOGGER.info(this.name + "- Send value to NodoVirtual" + inputToSend);
        oOut.addValue(inputToSend);
    }

    @Override
    public String toString() {
        return "Generator [iStart=" + iStart + ", iStop=" + iStop + ", oOut=" + oOut + ", period=" + period;
    }

    public Date parseDate(String sDate) throws Exception {
        String[] splitDate = line.split("-");
        // 2010-03-20 17:29:59-10:00
        String stringDate = splitDate[0] + "-" + splitDate[1] + "-" + splitDate[2];
        SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        Date date = formatter.parse(stringDate);
        return date;
    }

    public boolean nextFile() {
        contadorFicheros++;
        if (contadorFicheros < files.size()) {
            try {
                LOGGER.info(this.name + ": Start reading new file");
                reader = new BufferedReader(new FileReader(files.get(contadorFicheros)));
                line = reader.readLine(); // Se salta la primera linea del fichero
                line = reader.readLine();
            } catch (Exception e) {
                e.printStackTrace();
            }
            return true;
        } else {
            LOGGER.info(this.name + ": Not more files to read");
            return false;
        }
    }
}
