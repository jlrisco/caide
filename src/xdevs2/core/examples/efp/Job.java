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
package xdevs.core.examples.efp;

import xdevs.core.modeling.Input;

/**
 *
 * @author jlrisco
 */
public class Job {

  protected String id;
  protected double time;
  protected Input input;

  public Job(String name) {
    this.id = name;
    this.time = 0.0;
  }
  
  public Job(String name, Input input) {
	    this.id = name;
	    this.time = 0.0;
	    this.input = input;
	  }
  @Override
  public String toString() {
	  System.out.println("input value: " + input);
	  if(input != null) {
		  return "(id,t,energia,velocidad,radiacion)=(" + id + ", " + time + ")";
	  }
      return "(id,t)=(" + id + "," + time + ")";
  }
}
