/*
 * Copyright (C) 2014-2015 José Luis Risco Martín <jlrisco@ucm.es> and 
 * Saurabh Mittal <smittal@duniptech.com>.
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 3 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, see
 * http://www.gnu.org/licenses/
 *
 * Contributors:
 *  - José Luis Risco Martín
 */
package fog;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.logging.Logger;

import smile.interpolation.CubicSplineInterpolation1D;
import smile.interpolation.RBFInterpolation1D;
import smile.interpolation.ShepardInterpolation1D;
import smile.math.rbf.GaussianRadialBasis;
import xdevs.core.modeling.Atomic;
import util.Input;
import xdevs.core.modeling.Port;

/**
 *
 * @author José Luis Risco Martín TODO: I keep the Transducer atomic model for
 *         the end ...
 */
public class FogServer extends Atomic {

    private static final Logger LOGGER = Logger.getLogger(FogServer.class.getName());
    public static final String CUBICSPLINE = "CubicSpline";
    public static final String RBF = "RBF";
    public static final String SHEPARD = "Shepard";

    public Port<Input> iArrived = new Port<>("iArrived");

    // PORTINIT
    public Port<Input> iInNodovirtual1 = new Port<>("iInNodovirtual1");
    protected Input currentInputNodovirtual1 = null;

    public Port<Input> iInNodovirtual2 = new Port<>("iInNodovirtual2");
    protected Input currentInputNodovirtual2 = null;

    public Port<Input> iInNodovirtual3 = new Port<>("iInNodovirtual3");
    protected Input currentInputNodovirtual3 = null;

    public Port<Input> iInNodovirtual4 = new Port<>("iInNodovirtual4");
    protected Input currentInputNodovirtual4 = null;

    public Port<Input> iInNodovirtual5 = new Port<>("iInNodovirtual5");
    protected Input currentInputNodovirtual5 = null;

    public Port<Input> iInNodovirtual6 = new Port<>("iInNodovirtual6");
    protected Input currentInputNodovirtual6 = null;

    public Port<Input> iInNodovirtual7 = new Port<>("iInNodovirtual7");
    protected Input currentInputNodovirtual7 = null;

    public Port<Input> iInNodovirtual8 = new Port<>("iInNodovirtual8");
    protected Input currentInputNodovirtual8 = null;

    public Port<Input> oOut = new Port<>("oOut");

    protected double processingTime;
    protected ArrayList<Input> listaInputs = new ArrayList<Input>();
    protected int contadorArray = 0;
    protected int contadorPrint = 0;

    protected Collection<Input> collection = null;

    boolean outliersProcessed = false;

    final int MUESTRA = 99;

    // KRIGINGINIT

    // ########################################
    // double krigingiInNodoVirtual1 = 0.0;
    // double krigingiInNodoVirtual2 = 0.0;
    // ########################################
    public FogServer(String name, double processingTime) {
        super(name);
        super.addInPort(iArrived);

        // CONSTRUCTOR
        super.addInPort(iInNodovirtual1);
        super.addInPort(iInNodovirtual2);
        super.addInPort(iInNodovirtual3);
        super.addInPort(iInNodovirtual4);
        super.addInPort(iInNodovirtual5);
        super.addInPort(iInNodovirtual6);
        super.addInPort(iInNodovirtual7);
        super.addInPort(iInNodovirtual8);

        this.processingTime = processingTime;

        super.addOutPort(oOut);
    }

    @Override
    public void initialize() {
        super.passivate();
    }

    @Override
    public void exit() {
    }

    @Override
    public void deltint() {

        List<Input> outliers = new ArrayList<Input>();

        if (contadorArray >= MUESTRA) {

            try {
                LOGGER.info(this.name + "- Search for Outliers");
                outliers = getOutliers(listaInputs);
                // System.out.println("outliers" + outliers.toString());
                if (outliers.size() > 0) {
                    int contadorArray_local = contadorArray;
                    for (int w = 0; w < outliers.size(); w++) {
                        try {
                            int index_outlier = findIndex(listaInputs, outliers.get(w).getRadiacion());
                            int first = index_outlier - 3;
                            if (first < 0) {
                                first = first + contadorArray_local;
                            }
                            int second = index_outlier - 2;
                            if (second < 0) {
                                second = second + contadorArray_local;
                            }
                            int third = index_outlier - 1;
                            if (third < 0) {
                                third = third + contadorArray_local;
                            }
                            int fourth = index_outlier + 1;
                            if (fourth >= contadorArray_local) {
                                fourth = fourth - contadorArray_local;
                            }
                            int fifth = index_outlier + 2;
                            if (fifth >= contadorArray_local) {
                                fifth = fifth - contadorArray_local;
                            }
                            int sixth = index_outlier + 3;
                            if (sixth >= contadorArray_local) {
                                sixth = sixth - contadorArray_local;
                            }
                            int seventh = index_outlier + 4;
                            if (seventh >= contadorArray_local) {
                                seventh = seventh - contadorArray_local;
                            }
                            double[] x = { 0, 1, 2, 3, 4, 5, 6 };
                            double[] y = { listaInputs.get(first).getRadiacion(),
                                    listaInputs.get(second).getRadiacion(), listaInputs.get(third).getRadiacion(),
                                    listaInputs.get(fourth).getRadiacion(), listaInputs.get(fifth).getRadiacion(),
                                    listaInputs.get(sixth).getRadiacion(), listaInputs.get(seventh).getRadiacion() };

                            double[][] controls = new double[x.length][2];
                            for (int i = 0; i < controls.length; i++) {
                                controls[i][0] = x[i];
                                controls[i][1] = y[i];
                            }

                            CubicSplineInterpolation1D spline = new CubicSplineInterpolation1D(x, y);
                            double[][] zz = new double[61][2];
                            for (int i = 0; i <= 60; i++) {
                                zz[i][0] = i * 0.1;
                                zz[i][1] = spline.interpolate(zz[i][0]);
                            }

                            RBFInterpolation1D rbf = new RBFInterpolation1D(x, y, new GaussianRadialBasis());
                            double[][] ww = new double[61][2];
                            for (int i = 0; i <= 60; i++) {
                                ww[i][0] = i * 0.1;
                                ww[i][1] = rbf.interpolate(zz[i][0]);
                            }

                            ShepardInterpolation1D shepard = new ShepardInterpolation1D(x, y, 3);
                            double[][] vv = new double[61][2];
                            for (int i = 0; i <= 60; i++) {
                                vv[i][0] = i * 0.1;
                                vv[i][1] = shepard.interpolate(zz[i][0]);
                            }

                            Input inputCubicSpline = new Input(listaInputs.get(index_outlier).getDate(), zz[30][1],
                                    CUBICSPLINE);
                            Input inputRBF = new Input(listaInputs.get(index_outlier).getDate(), ww[30][1], RBF);
                            Input inputShepard = new Input(listaInputs.get(index_outlier).getDate(), vv[30][1],
                                    SHEPARD);

                            replaceOutlier(inputCubicSpline, index_outlier);
                            processInput(inputRBF);
                            processInput(inputShepard);
                        } catch (Exception e) {
                            System.out.println(e);
                        }
                    }
                }

                outliers.clear();
                outliersProcessed = true;
            } catch (Exception e) {
                e.printStackTrace();
            }
            contadorPrint++;
        }

        super.passivate();

    }

    @Override
    public void deltext(double e) {
        if (super.phaseIs("passive")) {
            // DELTEXT
            if (iInNodovirtual1.isEmpty() == false) {
                currentInputNodovirtual1 = iInNodovirtual1.getSingleValue();
                if (currentInputNodovirtual1 != null) {
                    processInput(currentInputNodovirtual1);
                }
            }

            if (iInNodovirtual2.isEmpty() == false) {
                currentInputNodovirtual2 = iInNodovirtual2.getSingleValue();
                if (currentInputNodovirtual2 != null) {
                    processInput(currentInputNodovirtual2);
                }
            }

            if (iInNodovirtual3.isEmpty() == false) {
                currentInputNodovirtual3 = iInNodovirtual3.getSingleValue();
                if (currentInputNodovirtual3 != null) {
                    processInput(currentInputNodovirtual3);
                }
            }

            if (iInNodovirtual4.isEmpty() == false) {
                currentInputNodovirtual4 = iInNodovirtual4.getSingleValue();
                if (currentInputNodovirtual4 != null) {
                    processInput(currentInputNodovirtual4);
                }
            }

            if (iInNodovirtual5.isEmpty() == false) {
                currentInputNodovirtual5 = iInNodovirtual5.getSingleValue();
                if (currentInputNodovirtual5 != null) {
                    processInput(currentInputNodovirtual5);
                }
            }

            if (iInNodovirtual6.isEmpty() == false) {
                currentInputNodovirtual6 = iInNodovirtual6.getSingleValue();
                if (currentInputNodovirtual6 != null) {
                    processInput(currentInputNodovirtual6);
                }
            }

            if (iInNodovirtual7.isEmpty() == false) {
                currentInputNodovirtual7 = iInNodovirtual7.getSingleValue();
                if (currentInputNodovirtual7 != null) {
                    processInput(currentInputNodovirtual7);
                }
            }

            if (iInNodovirtual8.isEmpty() == false) {
                currentInputNodovirtual8 = iInNodovirtual8.getSingleValue();
                if (currentInputNodovirtual8 != null) {
                    processInput(currentInputNodovirtual8);
                }
            }

            super.passivate();
            super.holdIn("active", 0);
        }
    }

    @Override
    public void lambda() {
        if (contadorArray >= MUESTRA && outliersProcessed) {
            oOut.addValues(listaInputs);
            listaInputs.clear();
            contadorArray = 0;
            outliersProcessed = false;
        }
    }

    // Calculo Outliers http://www.mathwords.com/o/outlier.htm
    public static List<Input> getOutliers(List<Input> input) {
        List<Input> output = new ArrayList<Input>();
        List<Input> data1 = new ArrayList<Input>();
        List<Input> data2 = new ArrayList<Input>();
        if (input.size() % 2 == 0) {
            data1 = input.subList(0, input.size() / 2);
            data2 = input.subList(input.size() / 2, input.size());
        } else {
            data1 = input.subList(0, input.size() / 2);
            data2 = input.subList(input.size() / 2 + 1, input.size());
        }
        double q1 = getMedian(data1);
        double q3 = getMedian(data2);

        double iqr = q3 - q1;
        if (iqr < 0) {
            iqr = -iqr;
        }

        double lowerFence = q1 - 2.5 * iqr;

        double upperFence = q3 + 2.5 * iqr;

        for (int i = 0; i < input.size(); i++) {
            if (input.get(i).getRadiacion() < lowerFence || input.get(i).getRadiacion() > upperFence) {
                output.add(input.get(i));
            }

        }
        return output;
    }

    private static double getMedian(List<Input> data) {
        if (data.size() % 2 == 0)
            return (data.get(data.size() / 2).getRadiacion() + data.get(data.size() / 2 - 1).getRadiacion()) / 2;
        else
            return data.get(data.size() / 2).getRadiacion();
    }

    private void processInput(Input currentInput) {
        if (currentInput != null) {
            listaInputs.add(contadorArray, currentInput);
            contadorArray++;
        }
    }

    private void replaceOutlier(Input currentInput, int index) {
        if (currentInput != null) {
            listaInputs.add(index, currentInput);
        }
    }

    public static double variograma(Double c0, Double c, int a, double h) {
        if (h < a) {
            return c0 + c * (1.5 * (h / a) - 0.5 * Math.pow((h / a), 3));
        }
        return c0 + c;

    }

    public int findIndex(ArrayList<Input> arr, double value) {
        if (arr == null) {
            return -1;
        }

        int len = arr.size();
        int i = 0;

        while (i < len) {
            if (arr.get(i).getRadiacion() == value) {
                return i;
            } else {
                i++;
            }
        }
        return -1;
    }
}
