/*
 * Copyright (c) 2010-2020 Haifeng Li. All rights reserved.
 *
 * Smile is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version.
 *
 * Smile is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with Smile.  If not, see <https://www.gnu.org/licenses/>.
 */

package xdevs.core.examples.efp;

import java.awt.Color;
import java.awt.GridLayout;
import java.util.Arrays;

import javax.swing.JFrame;
import javax.swing.JPanel;

import smile.plot.swing.Canvas;
import smile.interpolation.CubicSplineInterpolation1D;
import smile.interpolation.KrigingInterpolation;
import smile.interpolation.KrigingInterpolation1D;
import smile.interpolation.LinearInterpolation;
import smile.interpolation.RBFInterpolation1D;
import smile.interpolation.ShepardInterpolation1D;
import smile.math.rbf.GaussianRadialBasis;
import smile.plot.swing.LinePlot;
import smile.plot.swing.ScatterPlot;

/**
 *
 * @author Haifeng Li
 */
@SuppressWarnings("serial")
public class Interpolation1DemoB extends JPanel {
    public Interpolation1DemoB() {
        super(new GridLayout(2,3));
        setBackground(Color.WHITE);
        // ,-?\d*.?\d*,-?\d*.?\d*,-?\d*.?\d*$
        //^(2010-03-21 \d\d:\d\d:[0-9][1-9]).*
        double [] real_x = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20};
        double [] real_y = {170.752, 293.352, 418.825, 538.784, 651.004, 748.875, 
        		834.702, 904.046, 941.071, 1026.89, 712.118, 1040.47, 1037.16, 981.06, 902.211, 
        		712.855, 766.064, 143.817, 504.856, 118.144, 254.669};
        
        double [] real_x2 = new double[600];
        for (int i = 0; i < 600; i++) {
        	real_x2[i] = i;
        }
        //https://raw.githubusercontent.com/iregue/simuladorIoT/master/data/ap1/20100321_ap1.csv
        double [] real_y2 =
        	{
        		170.752,
        		174.79,
        		179.561,
        		182.866,
        		186.903,
        		190.572,
        		194.608,
        		199.379,
        		203.416,
        		207.453,
        		212.224,
        		216.628,
        		220.3,
        		223.603,
        		227.273,
        		231.31,
        		234.981,
        		239.386,
        		241.955,
        		247.095,
        		253.336,
        		257.741,
        		259.944,
        		264.716,
        		268.02,
        		271.691,
        		274.995,
        		279.034,
        		283.439,
        		288.947,
        		293.352,
        		297.758,
        		301.796,
        		306.936,
        		310.975,
        		314.279,
        		318.318,
        		323.458,
        		328.231,
        		331.902,
        		335.207,
        		339.61,
        		344.746,
        		349.517,
        		353.919,
        		357.954,
        		363.093,
        		366.393,
        		370.794,
        		375.195,
        		379.596,
        		384.362,
        		387.294,
        		391.695,
        		395.733,
        		400.133,
        		404.531,
        		407.83,
        		412.23,
        		415.16,
        		418.825,
        		423.958,
        		428.724,
        		432.395,
        		436.794,
        		440.46,
        		444.86,
        		448.527,
        		453.295,
        		456.595,
        		460.63,
        		465.402,
        		468.703,
        		472.738,
        		476.774,
        		480.076,
        		483.745,
        		489.616,
        		492.552,
        		495.487,
        		498.424,
        		502.093,
        		506.864,
        		510.901,
        		515.672,
        		520.076,
        		522.278,
        		528.15,
        		532.554,
        		533.652,
        		538.784,
        		539.515,
        		545.381,
        		547.948,
        		552.351,
        		554.182,
        		558.215,
        		564.821,
        		567.017,
        		571.782,
        		577.648,
        		581.312,
        		586.077,
        		589.008,
        		590.839,
        		595.609,
        		595.605,
        		605.143,
        		609.544,
        		608.44,
        		612.108,
        		616.876,
        		619.076,
        		624.212,
        		628.249,
        		631.922,
        		634.125,
        		638.529,
        		640.731,
        		645.867,
        		651.004,
        		654.306,
        		657.976,
        		659.809,
        		663.111,
        		668.248,
        		672.279,
        		669.34,
        		670.438,
        		682.547,
        		680.344,
        		685.849,
        		691.353,
        		693.188,
        		695.757,
        		700.161,
        		703.831,
        		704.561,
        		707.489,
        		714.094,
        		713.719,
        		717.746,
        		721.773,
        		729.102,
        		730.194,
        		731.654,
        		733.848,
        		733.108,
        		737.144,
        		741.909,
        		748.875,
        		748.871,
        		753.27,
        		758.036,
        		763.17,
        		764.636,
        		767.204,
        		769.77,
        		767.934,
        		770.868,
        		778.205,
        		781.506,
        		781.505,
        		785.173,
        		786.64,
        		791.777,
        		796.913,
        		801.682,
        		804.617,
        		804.617,
        		805.717,
        		810.12,
        		814.523,
        		817.091,
        		821.861,
        		814.156,
        		824.429,
        		835.436,
        		835.803,
        		833.968,
        		834.702,
        		833.968,
        		838.738,
        		844.608,
        		828.465,
        		607.956,
        		840.939,
        		841.306,
        		854.515,
        		866.255,
        		852.68,
        		861.853,
        		865.522,
        		859.284,
        		862.586,
        		863.687,
        		871.392,
        		866.622,
        		883.867,
        		875.428,
        		883.867,
        		892.672,
        		884.234,
        		875.428,
        		868.457,
        		886.068,
        		893.406,
        		897.809,
        		901.478,
        		902.579,
        		904.046,
        		908.816,
        		906.248,
        		902.946,
        		899.644,
        		910.651,
        		917.255,
        		920.924,
        		915.42,
        		922.391,
        		909.917,
        		906.615,
        		917.255,
        		918.356,
        		916.888,
        		928.629,
        		932.665,
        		932.298,
        		930.096,
        		903.306,
        		934.85,
        		939.247,
        		943.279,
        		946.215,
        		928.603,
        		933.74,
        		945.115,
        		951.721,
        		959.061,
        		941.079,
        		941.071,
        		947.675,
        		971.151,
        		982.517,
        		989.112,
        		1004.51,
        		1007.07,
        		1018.45,
        		1025.42,
        		1028.36,
        		1030.19,
        		1016.62,
        		1017.35,
        		1031.29,
        		1027.62,
        		1008.92,
        		994.613,
        		990.583,
        		982.512,
        		985.086,
        		980.688,
        		977.025,
        		988.77,
        		1002.35,
        		1002.71,
        		1008.21,
        		996.092,
        		1008.2,
        		1012.96,
        		1021.39,
        		1026.89,
        		1036.06,
        		1042.3,
        		1053.3,
        		1047.8,
        		1044.13,
        		1045.6,
        		1054.41,
        		1058.44,
        		1056.61,
        		1055.14,
        		1069.08,
        		1076.42,
        		1094.76,
        		1119.34,
        		1138.06,
        		1137.69,
        		1160.45,
        		1234.56,
        		1181.74,
        		1178.43,
        		1179.53,
        		1158.98,
        		1190.16,
        		1230.16,
        		1245.94,
        		1226.12,
        		1237.13,
        		1231.26,
        		715.053,
        		712.118,
        		889.689,
        		583.34,
        		1198.96,
        		1093.66,
        		1168.13,
        		1160.06,
        		1165.2,
        		1089.63,
        		1233.07,
        		779.98,
        		653.037,
        		431.078,
        		1145.01,
        		1080.81,
        		1058.8,
        		1051.84,
        		1058.81,
        		1063.58,
        		1087.44,
        		1081.57,
        		1055.16,
        		1052.22,
        		1041.57,
        		1034.96,
        		1036.8,
        		1038.26,
        		1039.36,
        		1039.0,
        		1039.0,
        		1040.47,
        		1041.94,
        		1045.99,
        		1050.02,
        		1050.76,
        		1070.93,
        		1070.93,
        		1065.43,
        		490.522,
        		811.181,
        		928.581,
        		1064.33,
        		1059.56,
        		1058.83,
        		1051.49,
        		1055.53,
        		1051.87,
        		1055.17,
        		1058.84,
        		1071.68,
        		1070.95,
        		1065.44,
        		1054.43,
        		1048.2,
        		1032.05,
        		1026.19,
        		1019.95,
        		1014.8,
        		1013.69,
        		1010.01,
        		1037.16,
        		879.033,
        		825.831,
        		1042.64,
        		1060.61,
        		411.991,
        		971.459,
        		1000.44,
        		997.513,
        		994.945,
        		985.78,
        		981.745,
        		978.074,
        		982.105,
        		981.732,
        		980.999,
        		976.6,
        		974.032,
        		969.636,
        		963.039,
        		961.947,
        		970.753,
        		975.893,
        		974.797,
        		973.702,
        		984.714,
        		991.685,
        		946.564,
        		961.612,
        		837.975,
        		981.06,
        		970.053,
        		660.033,
        		946.576,
        		935.202,
        		941.442,
        		944.747,
        		906.593,
        		924.94,
        		887.519,
        		794.33,
        		672.155,
        		912.474,
        		815.98,
        		925.684,
        		936.692,
        		884.594,
        		928.623,
        		931.926,
        		922.02,
        		920.92,
        		916.884,
        		915.417,
        		915.051,
        		916.152,
        		909.181,
        		905.512,
        		905.879,
        		906.247,
        		905.146,
        		902.211,
        		899.642,
        		886.067,
        		873.226,
        		892.305,
        		897.435,
        		897.432,
        		903.3,
        		904.401,
        		905.134,
        		900.358,
        		896.319,
        		891.916,
        		882.377,
        		862.198,
        		807.166,
        		799.463,
        		776.715,
        		733.423,
        		670.319,
        		654.172,
        		783.317,
        		865.501,
        		871.733,
        		881.997,
        		881.264,
        		878.691,
        		866.216,
        		828.795,
        		791.002,
        		712.855,
        		525.012,
        		484.285,
        		616.359,
        		631.768,
        		741.464,
        		803.467,
        		837.589,
        		852.268,
        		847.136,
        		832.465,
        		821.829,
        		758.724,
        		790.275,
        		785.5,
        		780.362,
        		769.723,
        		773.026,
        		767.526,
        		768.629,
        		768.999,
        		773.402,
        		764.6,
        		775.609,
        		777.08,
        		751.766,
        		766.444,
        		764.607,
        		768.636,
        		772.672,
        		766.064,
        		753.956,
        		742.216,
        		745.519,
        		744.421,
        		731.943,
        		690.851,
        		631.416,
        		593.259,
        		633.614,
        		661.863,
        		645.721,
        		618.205,
        		667.737,
        		657.829,
        		581.883,
        		472.551,
        		214.262,
        		194.818,
        		195.552,
        		189.316,
        		197.755,
        		174.64,
        		158.863,
        		163.633,
        		165.468,
        		157.029,
        		154.46,
        		148.589,
        		146.019,
        		143.817,
        		146.385,
        		151.155,
        		155.925,
        		238.107,
        		238.108,
        		329.097,
        		268.562,
        		217.565,
        		206.926,
        		354.418,
        		231.877,
        		222.338,
        		231.511,
        		233.346,
        		223.073,
        		210.232,
        		200.693,
        		198.125,
        		193.356,
        		186.752,
        		178.313,
        		175.011,
        		170.975,
        		173.177,
        		178.314,
        		190.055,
        		206.932,
        		438.447,
        		451.288,
        		504.856,
        		318.47,
        		221.241,
        		195.192,
        		182.717,
        		176.113,
        		174.278,
        		172.077,
        		177.58,
        		181.983,
        		189.321,
        		241.788,
        		278.478,
        		405.059,
        		202.897,
        		161.437,
        		155.933,
        		155.933,
        		151.53,
        		146.394,
        		136.854,
        		128.782,
        		119.977,
        		111.538,
        		105.668,
        		105.301,
        		106.768,
        		108.236,
        		109.337,
        		112.273,
        		118.144,
        		129.518,
        		150.799,
        		183.086,
        		174.281,
        		242.894,
        		307.472,
        		314.812,
        		223.82,
        		195.936,
        		152.274,
        		165.85,
        		140.167,
        		156.314,
        		182.368,
        		187.874,
        		182.003,
        		155.217,
        		186.775,
        		251.357,
        		304.565,
        		294.292,
        		164.761,
        		162.926,
        		165.129,
        		159.258,
        		159.626,
        		162.562,
        		241.091,
        		255.036
        	};
        
        double[] x = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
        double[] y = {170.752, 418.825, 651.004, 834.702, 941.071, 1071.118, 1037.16, 902.211, 
        		766.064, 504.856, 254.669};
        
        System.out.println(real_x2.length);
        System.out.println(real_y2.length);
        double[][] real2 = new double[real_x2.length][2];
        for (int i = 0; i < real2.length; i++) {
            real2[i][0] = real_x2[i];
            real2[i][1] = real_y2[i];
        }
        Canvas canvas = ScatterPlot.of(real2, '@').canvas();
        canvas.setTitle("Real2");
        LinearInterpolation linear = new LinearInterpolation(real_x2, real_y2);
        double[][] real_yy2 = new double[6001][2];
        for (int i = 0; i <= 6000; i++) {
            real_yy2[i][0] = i * 0.1;
            real_yy2[i][1] = linear.interpolate(real_yy2[i][0]);
        }
        canvas.add(LinePlot.of(real_yy2, Color.RED));
        add(canvas.panel());
        
        //double[] x = {0, 1, 2, 3, 4, 5, 6};
        //double[] y = {170.752, 418.825, 651.004, 834.702, 941.071, 712.118, 1037.16 };
        
        
        /*
        double[][] real = new double[real_x.length][2];
        for (int i = 0; i < real.length; i++) {
            real[i][0] = real_x[i];
            real[i][1] = real_y[i];
        }
        */
        /*
        Canvas canvas = ScatterPlot.of(real, '@').canvas();
        canvas.setTitle("Real");
        LinearInterpolation linear = new LinearInterpolation(real_x, real_y);
        double[][] real_yy = new double[201][2];
        for (int i = 0; i <= 200; i++) {
            real_yy[i][0] = i * 0.1;
            real_yy[i][1] = linear.interpolate(real_yy[i][0]);
        }
        canvas.add(LinePlot.of(real_yy, Color.RED));
        add(canvas.panel());
        */
        
        double[][] controls = new double[x.length][2];
        for (int i = 0; i < controls.length; i++) {
            controls[i][0] = x[i];
            controls[i][1] = y[i];
        }
        System.out.println(controls.length);
        
        /*
        Canvas canvas = ScatterPlot.of(controls, '@').canvas();
        canvas.setTitle("Linear");
        LinearInterpolation linear = new LinearInterpolation(x, y);
        double[][] yy = new double[101][2];
        for (int i = 0; i <= 100; i++) {
            yy[i][0] = i * 0.1;
            yy[i][1] = linear.interpolate(yy[i][0]);
        }
        canvas.add(LinePlot.of(yy, Color.RED));
        add(canvas.panel());
        
        System.out.println(Arrays.deepToString(yy));
       */ 
        
        
        
        
        canvas = ScatterPlot.of(controls, '@').canvas();
        canvas.setTitle("Cubic Spline");
        CubicSplineInterpolation1D spline = new CubicSplineInterpolation1D(x, y);
        double[][] zz = new double[101][2];
        for (int i = 0; i <= 100; i++) {
            zz[i][0] = i * 0.1;
            zz[i][1] = spline.interpolate(zz[i][0]);
        }
        canvas.add(LinePlot.of(zz, Color.BLUE));
        add(canvas.panel());

        canvas = ScatterPlot.of(controls, '@').canvas();
        canvas.setTitle("RBF");
        RBFInterpolation1D rbf = new RBFInterpolation1D(x, y, new GaussianRadialBasis());
        double[][] ww = new double[101][2];
        for (int i = 0; i <= 100; i++) {
            ww[i][0] = i * 0.1;
            ww[i][1] = rbf.interpolate(zz[i][0]);
        }
        canvas.add(LinePlot.of(ww, Color.GREEN));
        add(canvas.panel());

        canvas = ScatterPlot.of(controls, '@').canvas();
        canvas.setTitle("Kriging");
        KrigingInterpolation1D kriging = new KrigingInterpolation1D(x, y);
        double[][] uu = new double[101][2];
        for (int i = 0; i <= 100; i++) {
            uu[i][0] = i * 0.1;
            uu[i][1] = kriging.interpolate(zz[i][0]);
        }
        canvas.add(LinePlot.of(uu, Color.PINK));
        add(canvas.panel());

        canvas = ScatterPlot.of(controls, '@').canvas();
        canvas.setTitle("Shepard");
        ShepardInterpolation1D shepard = new ShepardInterpolation1D(x, y, 3);
        double[][] vv = new double[101][2];
        for (int i = 0; i <= 100; i++) {
            vv[i][0] = i * 0.1;
            vv[i][1] = shepard.interpolate(zz[i][0]);
        }
        canvas.add(LinePlot.of(vv, Color.CYAN));
        add(canvas.panel());

    }


    @Override
    public String toString() {
        return "1D";
    }

    public static void main(String[] args) {
        JFrame frame = new JFrame("Interpolation 1D");
        frame.setSize(1000, 1000);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLocationRelativeTo(null);
        frame.getContentPane().add(new Interpolation1DemoB());
        frame.setVisible(true);
    }
}