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
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.logging.Logger;

import util.Input;
import xdevs.core.modeling.Atomic;
import xdevs.core.modeling.Port;

public class FogServer extends Atomic {

    private static final Logger LOGGER = Logger.getLogger(FogServer.class.getName());
    
    public Port<Input> in01 = new Port<>("in01");
    /* 
       TODO: Tenemos que pensar qué arroja el Fog hacia el
       DataCenter. De momento simplemente propagamos el dato.
    */
    public Port<Input> out = new Port<>("out");

    /*
      Esto es una técnica habitual que suelo usar para evitarme
      atributos para su uso en deltext.
     */
    protected HashMap<String, LinkedList<Input>> queue = new HashMap<>();

    public FogServer(String name) {
        super(name);
        super.addInPort(in01);
        super.addOutPort(out);
        queue.put(out.getName(), new LinkedList<Input>());
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
        queue.get(out.getName()).clear();
        super.passivate();
    }

    @Override
    public void deltext(double e) {
        if (!in01.isEmpty()) {
            queue.get(out.getName()).add(in01.getSingleValue());
        }
    }

    @Override
    public void lambda() {
        out.addValues(queue.get(out.getName()));
    }
}
