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
import fog.Service;
import xdevs.core.modeling.Coupled;
import xdevs.core.simulation.Coordinator;
import xdevs.core.util.DevsLogger;

public class EntornoGlobal extends Coupled {

    private static final Logger LOGGER = Logger.getLogger(EntornoGlobal.class.getName());

    public EntornoGlobal(String name, LocalDateTime start, LocalDateTime stop) {
        super(name);

        // DATACENTER
        String nameDataCenter = "DataCenter";
        DataCenter dataCenter = new DataCenter(nameDataCenter);
        super.addComponent(dataCenter);
        
        // FOGSERVER
        String nameFogServer01 = nameDataCenter+"."+"FogServer01";
        FogServer fogServer01 = new FogServer(nameFogServer01);
        super.addComponent(fogServer01);
        
        // SENSORS
        String nameAp1 = nameFogServer01+"."+"ap1";
        NodoVirtual ap1 = new NodoVirtual(nameAp1, start, stop);
        super.addComponent(ap1);
        
        String nameAp3 = nameFogServer01+"."+"ap3";
        NodoVirtual ap3 = new NodoVirtual(nameAp3, start, stop);
        super.addComponent(ap3);
        
        String nameAp4 = nameFogServer01+"."+"ap4";
        NodoVirtual ap4 = new NodoVirtual(nameAp4, start, stop);
        super.addComponent(ap4);
        
        /*String nameAp5 = nameFogServer01+"."+"ap5";
        NodoVirtual ap5 = new NodoVirtual(nameAp5, start, stop);
        super.addComponent(ap5);
        
        String nameAp6 = nameFogServer01+"."+"ap6";
        NodoVirtual ap6 = new NodoVirtual(nameAp6, start, stop);
        super.addComponent(ap6);
        
        String nameAp7 = nameFogServer01+"."+"ap7";
        NodoVirtual ap7 = new NodoVirtual(nameAp7, start, stop);
        super.addComponent(ap7);
        
        String nameDh1 = nameFogServer01+"."+"dh1";
        NodoVirtual dh1 = new NodoVirtual(nameDh1, start, stop);
        super.addComponent(dh1);
        
        String nameDh2 = nameFogServer01+"."+"dh2";
        NodoVirtual dh2 = new NodoVirtual(nameDh2, start, stop);
        super.addComponent(dh2);
        
        String nameDh3 = nameFogServer01+"."+"dh3";
        NodoVirtual dh3 = new NodoVirtual(nameDh3, start, stop);
        super.addComponent(dh3);
        
        String nameDh4 = nameFogServer01+"."+"dh4";
        NodoVirtual dh4 = new NodoVirtual(nameDh4, start, stop);
        super.addComponent(dh4);        
        
        String nameDh5 = nameFogServer01+"."+"dh5";
        NodoVirtual dh5 = new NodoVirtual(nameDh5, start, stop);
        super.addComponent(dh5);
        
        String nameDh6 = nameFogServer01+"."+"dh6";
        NodoVirtual dh6 = new NodoVirtual(nameDh6, start, stop);
        super.addComponent(dh6);
        
        String nameDh7 = nameFogServer01+"."+"dh7";
        NodoVirtual dh7 = new NodoVirtual(nameDh7, start, stop);
        super.addComponent(dh7);
        
        String nameDh8 = nameFogServer01+"."+"dh8";
        NodoVirtual dh8 = new NodoVirtual(nameDh8, start, stop);
        super.addComponent(dh8);
        
        String nameDh9 = nameFogServer01+"."+"dh9";
        NodoVirtual dh9 = new NodoVirtual(nameDh9, start, stop);
        super.addComponent(dh9);
        
        String nameDh10 = nameFogServer01+"."+"dh10";
        NodoVirtual dh10 = new NodoVirtual(nameDh10, start, stop);
        super.addComponent(dh10);
        
        String nameDh11 = nameFogServer01+"."+"dh11";
        NodoVirtual dh11 = new NodoVirtual(nameDh11, start, stop);
        super.addComponent(dh11);
        */
        // SERVICE
        Service s1 = new Service("20220420_commands.csv", start, stop);
        super.addComponent(s1);
        
        
        // COUPLINGS
        super.addCoupling(ap1.out, fogServer01.in01);
        
        super.addCoupling(s1.out, fogServer01.in02);
        
        super.addCoupling(ap3.out, fogServer01.in01);
        super.addCoupling(ap4.out, fogServer01.in01);
        /*super.addCoupling(ap5.out, fogServer01.in01);
        super.addCoupling(ap6.out, fogServer01.in01);
        super.addCoupling(ap7.out, fogServer01.in01);
        super.addCoupling(dh1.out, fogServer01.in01);
        super.addCoupling(dh2.out, fogServer01.in01);
        super.addCoupling(dh3.out, fogServer01.in01);
        super.addCoupling(dh4.out, fogServer01.in01);
        super.addCoupling(dh5.out, fogServer01.in01);
        super.addCoupling(dh6.out, fogServer01.in01);
        super.addCoupling(dh7.out, fogServer01.in01);
        super.addCoupling(dh8.out, fogServer01.in01);
        super.addCoupling(dh9.out, fogServer01.in01);
        super.addCoupling(dh10.out, fogServer01.in01);
        super.addCoupling(dh11.out, fogServer01.in01);
        */
        super.addCoupling(fogServer01.out, dataCenter.in01);        
        
    }

    public static void main(String args[]) {
    	System.out.println("Begin.......");
        DevsLogger.setup(Level.INFO);
        SimpleDateFormat fmt = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        LocalDateTime start = null;
        LocalDateTime stop = null;
        try {
            Date startAux = fmt.parse("2010-03-20 07:30:00");
            start = startAux.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
            Date stopAux = fmt.parse("2010-03-20 07:30:04");
            //Date stopAux = fmt.parse("2010-03-25 17:29:59");
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
        System.out.println("End.......");
    }
}
