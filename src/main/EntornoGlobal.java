package main;

import java.nio.file.Paths;
import java.text.SimpleDateFormat;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Date;
import java.util.logging.Level;
import java.util.logging.Logger;

import xdevs.core.modeling.Coupled;
import xdevs.core.simulation.Coordinator;
import xdevs.core.util.DevsLogger;

import edge.Ficheros;
import edge.NodoVirtual;
import fog.FogServer;
import cloud.DataCenter;

public class EntornoGlobal extends Coupled {

    private static final Logger LOGGER = Logger.getLogger(EntornoGlobal.class.getName());

    public EntornoGlobal(String name, LocalDateTime start, LocalDateTime stop) {
        super(name);

        // FICHEROS
        // Ficheros ap1 = new Ficheros("ap1", period, userDirectory + "/data/ap1/",
        // null, null);
        // Abrir el fichero en 2010-03-20, desde las 07:30:00 hasta las 07:40:00, por ejemplo.
        // El fichero estará en data/ap1/20100320_ap1.csv por ejemplo.
        Ficheros ap1 = new Ficheros("ap1", "data/ap1", start, stop);
        super.addComponent(ap1);
        /*
         * Ficheros ap5 = new Ficheros("ap5", period, userDirectory + "/data/ap5/",
         * null, null); super.addComponent(ap5);
         * 
         * Ficheros ap6 = new Ficheros("ap6", period, userDirectory + "/data/ap6/",
         * null, null); super.addComponent(ap6);
         * 
         * Ficheros ap7 = new Ficheros("ap7", period, userDirectory + "/data/ap7/",
         * null, null); super.addComponent(ap7);
         * 
         * Ficheros dh1 = new Ficheros("dh1", period, userDirectory + "/data/dh1/",
         * null, null); super.addComponent(dh1);
         * 
         * Ficheros dh2 = new Ficheros("dh2", period, userDirectory + "/data/dh2/",
         * null, null); super.addComponent(dh2);
         * 
         * Ficheros dh3 = new Ficheros("dh3", period, userDirectory + "/data/dh3/",
         * null, null); super.addComponent(dh3);
         * 
         * Ficheros dh4 = new Ficheros("dh4", period, userDirectory + "/data/dh4/",
         * null, null); super.addComponent(dh4);
         */

        // NVIRTUAL
        NodoVirtual nodoVirtual1 = new NodoVirtual("nodoVirtual1", period);
        super.addComponent(nodoVirtual1);
        /*
         * NodoVirtual nodoVirtual2 = new NodoVirtual("nodoVirtual2", period);
         * super.addComponent(nodoVirtual2);
         * 
         * NodoVirtual nodoVirtual3 = new NodoVirtual("nodoVirtual3", period);
         * super.addComponent(nodoVirtual3);
         * 
         * NodoVirtual nodoVirtual4 = new NodoVirtual("nodoVirtual4", period);
         * super.addComponent(nodoVirtual4);
         * 
         * NodoVirtual nodoVirtual5 = new NodoVirtual("nodoVirtual5", period);
         * super.addComponent(nodoVirtual5);
         * 
         * NodoVirtual nodoVirtual6 = new NodoVirtual("nodoVirtual6", period);
         * super.addComponent(nodoVirtual6);
         * 
         * NodoVirtual nodoVirtual7 = new NodoVirtual("nodoVirtual7", period);
         * super.addComponent(nodoVirtual7);
         * 
         * NodoVirtual nodoVirtual8 = new NodoVirtual("nodoVirtual8", period);
         * super.addComponent(nodoVirtual8);
         */

        // FOGSERVER
        FogServer fogserver1 = new FogServer("fogserver1", period);
        super.addComponent(fogserver1);

        /*
         * FogServer fogserver2 = new FogServer("fogserver2", period );
         * super.addComponent(fogserver2);
         */

        // DATACENTER
        DataCenter dataCenter = new DataCenter("dataCenter", period);
        super.addComponent(dataCenter);

        // CONECTOR
        super.addCoupling(ap1.oOut, nodoVirtual1.iInFichero);
        /*
         * super.addCoupling(ap5.oOut, nodoVirtual2.iInFichero);
         * super.addCoupling(ap6.oOut, nodoVirtual3.iInFichero);
         * super.addCoupling(ap7.oOut, nodoVirtual4.iInFichero);
         * super.addCoupling(dh1.oOut, nodoVirtual5.iInFichero);
         * super.addCoupling(dh2.oOut, nodoVirtual6.iInFichero);
         * super.addCoupling(dh3.oOut, nodoVirtual7.iInFichero);
         * super.addCoupling(dh4.oOut, nodoVirtual8.iInFichero);
         */
        super.addCoupling(nodoVirtual1.oOut, fogserver1.iInNodovirtual1);
        /*
         * super.addCoupling(nodoVirtual2.oOut, fogserver1.iInNodovirtual2);
         * super.addCoupling(nodoVirtual3.oOut, fogserver1.iInNodovirtual3);
         * super.addCoupling(nodoVirtual4.oOut, fogserver1.iInNodovirtual4);
         * super.addCoupling(nodoVirtual5.oOut, fogserver2.iInNodovirtual5);
         * super.addCoupling(nodoVirtual6.oOut, fogserver2.iInNodovirtual6);
         * super.addCoupling(nodoVirtual7.oOut, fogserver2.iInNodovirtual7);
         * super.addCoupling(nodoVirtual8.oOut, fogserver2.iInNodovirtual8);
         */
        super.addCoupling(fogserver1.oOut, dataCenter.iInFogserver1);
        /* super.addCoupling(fogserver2.oOut, dataCenter.iInFogserver2); */

    }

    public static void main(String args[]) {
        DevsLogger.setup(Level.INFO);
        SimpleDateFormat fmt = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        LocalDateTime start = null;
        LocalDateTime stop = null;
        try {
            Date startAux = fmt.parse("2010-03-20 07:00:00");
            start = startAux.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
            Date stopAux = fmt.parse("2010-03-20 07:10:00");
            stop = stopAux.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
        } catch (Exception ee) {
            LOGGER.severe(ee.getLocalizedMessage());
            return;
        }
        EntornoGlobal eg = new EntornoGlobal("EntornoGlobal", start, stop);
        Coordinator coordinator = new Coordinator(eg);
        coordinator.initialize();
        coordinator.simulate(Long.MAX_VALUE);
        coordinator.exit();
    }
}
