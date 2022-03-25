package edge;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.logging.Logger;
import java.text.SimpleDateFormat;

import xdevs.core.modeling.Atomic;
import util.Input;
import xdevs.core.modeling.Port;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;

/**
 *
 * @author José Luis Risco Martín TODO: I must also modify this class, according
 *         to the source code implemented by Saurabh, a iStart input port must
 *         be added.
 */
public class Ficheros extends Atomic {
    private static final Logger LOGGER = Logger.getLogger(Ficheros.class.getName());
    public Port<Input> iStart = new Port<>("iStart");
    public Port<Input> iStop = new Port<>("iStop");
    public Port<Input> oOut = new Port<>("oOut");
    protected double period;
    protected String path;
    protected ArrayList<Input> listaEntrada = new ArrayList<Input>();
    int contador = 0;
    private String line;
    private BufferedReader reader;
    ArrayList<String> files = new ArrayList<String>();
    private int contadorFicheros = 0;
    long initialDate = 0;
    long startDate = 0;
    long endDate = 0;
    long actualDate = 0;
    Input inputToSend = null;

    public Ficheros(String name, double period, String path, String startDate, String endDate) {
        super(name);
        super.addInPort(iStop);
        super.addInPort(iStart);
        super.addOutPort(oOut);
        this.period = period;
        this.path = path;
        if (startDate != null && endDate != null) {
            try {
                this.startDate = parseDate(startDate).getTime();
                this.endDate = parseDate(endDate).getTime();
            } catch (Exception e1) {
                e1.printStackTrace();
                LOGGER.severe(this.name
                        + "- Exception parsing endDate and/or startDate. Format have to be yyyy-MM-dd HH:mm:ss");
            }
        }

        try {
            // Recorrer ficheros de un directorio
            final File folder = new File(path);
            for (final File fileEntry : folder.listFiles()) {
                files.add(fileEntry.getPath());
            }
            Collections.sort(files);
            System.out.println("Sorted: " + files.toString());
        } catch (Exception e) {
            e.printStackTrace();
            LOGGER.warning(this.name + "- Exception getting files list");
        }
    }

    @Override
    public void initialize() {
        LOGGER.info(this.name + ": Ficheros Initialize");
        Input datosEntrada = null;
        try {
            reader = new BufferedReader(new FileReader(files.get(contadorFicheros)));
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
