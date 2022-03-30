package main;

import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;
import java.util.logging.Level;
import java.util.logging.Logger;

import cloud.DataCenter;
import edge.NodoVirtual;
import fog.FogServer;
import xdevs.core.modeling.Coupled;
import xdevs.core.simulation.Coordinator;
import xdevs.core.util.DevsLogger;

public class EntornoGlobal extends Coupled {

    private static final Logger LOGGER = Logger.getLogger(EntornoGlobal.class.getName());

    public EntornoGlobal(String name, LocalDateTime start, LocalDateTime stop) {
        super(name);

        // SENSORS
        NodoVirtual ap1 = new NodoVirtual("ap1", start, stop);
        super.addComponent(ap1);
        // FOGSERVER
        FogServer fogServer01 = new FogServer("FogServer01");
        super.addComponent(fogServer01);
        // DATACENTER
        DataCenter dataCenter = new DataCenter("DataCenter");
        super.addComponent(dataCenter);

        // COUPLINGS
        super.addCoupling(ap1.out, fogServer01.in01);
        super.addCoupling(fogServer01.out, dataCenter.in01);
    }

    public static void main(String args[]) {
        DevsLogger.setup(Level.INFO);
        SimpleDateFormat fmt = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        LocalDateTime start = null;
        LocalDateTime stop = null;
        try {
            Date startAux = fmt.parse("2010-03-20 07:35:00");
            start = startAux.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
            Date stopAux = fmt.parse("2010-03-21 07:40:00");
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
