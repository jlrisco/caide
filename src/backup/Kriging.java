package backup;

public class Kriging {
    /*
	static ArrayList<Double> x_list = new ArrayList<Double>(); // Create an ArrayList object
	static ArrayList<Double> y_list = new ArrayList<Double>(); // Create an ArrayList object
	static ArrayList<Double> valores = new ArrayList<Double>(); // Create an ArrayList object
	
	static ArrayList<Double> hh = new ArrayList<Double>(); // Create an ArrayList object
	static ArrayList<Double> vv = new ArrayList<Double>(); // Create an ArrayList object
	static double x0= 5.0;
	static double y0= 5.0;
	static double f0;
	
	
	public static void distancia(ArrayList<Double> x, ArrayList<Double> y, ArrayList<Double> valores) {
		
		for (int i=0; i < x.size();i++) {
			for(int j=1; j < x.size(); j++) {
				hh.add(Math.sqrt( Math.pow((x.get(i) - x.get(j)),2) + Math.pow((y.get(i) - y.get(j)), 2) ));
				vv.add(0.5 * Math.pow((valores.get(i) - valores.get(j)), 2));

				
			}
		}
		Collections.sort(hh);
		Collections.sort(vv);
		
		regresion_esferica(hh, vv);
	}
	
	public static double variograma(Double c0, Double c, int a, double h) {
		if(h<a) {
			return c0 + c * (1.5 *(h/a) - 0.5 * Math.pow((h/a), 3));
		}
		return c0+c;
		
	}
	
	public static void regresion_esferica(ArrayList<Double> h, ArrayList<Double> v) {
		int  N = 2; // Indices de la Meseta
		double c0 = v.get(0);
		int cmax = v.size() - N;
		double c = cmax - c0;
		int a = h.size() - N;
		
		
		System.out.println(x_list.size());
		double [][] A = new double[x_list.size()+1][x_list.size()+1];
		for(int i=0; i<x_list.size()+1; i++) {
			for(int j=0; j<x_list.size()+1; j++) {
				A[i][j] = 1.0;
			}	
		}
		for(int i=0; i<x_list.size(); i++) {
			for(int j=0; j<x_list.size(); j++) {
				if(i==j) {
					A[i][j] = 0;
				}
				else {
					A[i][j] = variograma(c0, c, a, Math.sqrt( Math.pow(x_list.get(i) - x_list.get(j), 2) + Math.pow(y_list.get(i) - y_list.get(j), 2)));
				}
			}
		}
		A[x_list.size()][x_list.size()] = 0;
		//Print matriz A
		System.out.println("valores introducidos A:");
        for (int i = 0; i < A.length; i++) { 
            for (int j = 0; j < A[i].length; j++) {
                System.out.print(A[i][j] + " ");
            }
            System.out.println();
        }
        double [][] B = new double[x_list.size()+1][1];
        for(int i=0; i <x_list.size(); i++) {
        	B[i][0] = variograma(c0, c, a, Math.sqrt(Math.pow(x_list.get(i) - x0, 2)+ Math.pow(y_list.get(i) - y0, 2)));
        }
        
        Matrix A_matrix = new Matrix(A);
        Matrix B_matrix = new Matrix(B);
        A_matrix.print(5, 2);
        B_matrix.print(5, 2);
        
        Matrix w = A_matrix.inverse().times(B_matrix);
        w.print(5, 2);
        
        for(int i=0; i<valores.size(); i++) {
        	f0 += w.get(i, 0)*valores.get(i);
        }
        System.out.println("f0= " + f0);
	}
	
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		
		x_list.add(2.33);
		x_list.add(1.80);
		x_list.add(-4.0);
		x_list.add(2.53);
		x_list.add(6.5);
		x_list.add(8.11);
		x_list.add(3.5);
		x_list.add(-2.9);
		x_list.add(-1.1);
		x_list.add(7.3);

		y_list.add(1.2);
		y_list.add(-1.1);
		y_list.add(2.9);
		y_list.add(3.5);
		y_list.add(8.11);
		y_list.add(-6.5);
		y_list.add(-2.53);
		y_list.add(-4.0);
		y_list.add(1.80);
		y_list.add(-2.33);
		
		valores.add(130.1);
		valores.add(113.7);
		valores.add(28.6);
		valores.add(119.3);
		valores.add(54.2);
		valores.add(37.8);
		valores.add(61.1);
		valores.add(19.8);
		valores.add(62.9);
		valores.add(116.0);

		distancia(x_list, y_list, valores);
	}

	
    */
}
