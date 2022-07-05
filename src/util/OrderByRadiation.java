package util;

import java.util.Comparator;

public class OrderByRadiation implements Comparator<Input>{

	@Override
	public int compare(Input i1, Input i2) {
		if(i1.getRadiacion() > i2.getRadiacion()){
			return 1;
		}else if(i1.getRadiacion() < i2.getRadiacion()) {
			return -1;
		}else {
			return 0;
		}
	}
	
}
