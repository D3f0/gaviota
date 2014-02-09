/**
 * Utiliza YUI y Prototype.
 */

AULAS = (function (){
	try{
    // Alias
    //
    var $E = YAHOO.util.Event,
        $J = YAHOO.lang.JSON.parse;

	// Variables
	var tip_div = document.createElement('div'),
		current = null,
		tiempo = 140,
		timeoutId,
		verbose = true, 
		DIAS = {1: 'Lunes', 2: 'Martes', 3: 'Miercoles', 4: 'Jueves',
				5: 'Viernes', 6: 'Sábado'};
				
	// Setear los atributos
	
	tip_div.style.position = 'absolute';
	tip_div.style.top = '0px';
	tip_div.style.left = '0px';
	tip_div.style.border = '1px solid #D1A019';
	tip_div.style.borderBottomColor = '#60490B';
	tip_div.style.borderRightColor = '#60490B';
	tip_div.style.padding = '5px';
	
	tip_div.innerHTML = "Sin informacion";
	tip_div.style.display = 'none';
	tip_div.style.backgroundColor = '#FFF878'; 
	//tip_div.className = 'tip_div';
	
	// Agregamos el tipo al markup
	document.getElementsByTagName('body')[0].appendChild(tip_div);
	
	function my_log(msg){
		if (verbose)
			console.log(msg);
	}
	/**
	 * Mostrar un mensaje en el DIV.
	 * @param {Object} msg
	 */
	function mostrar_div(msg){
		console.log('Muestra mensaje');
		tip_div.innerHTML = msg;
		tip_div.style.display = 'block';
		// Manejamos el corrimiento
		
		
	}
	
	function showTip(mouseEvent){
		var ev = mouseEvent[0],
			target = ev.target;
		window.clearTimeout(timeoutId);
		tip_div.style.top = ( ev.pointerY() + 10)+'px';
		tip_div.style.left = ( ev.pointerX() + 10)+'px';
		mostrar_div('<div class="loading">Cargando...</div>');
		// Tomamos el JSON incrustado en la celda...
		var json = target.getElementsByClassName('data')[0].innerHTML;
		try {
            // Por alguna razon no funciona el parser de JSON de YUI
            //json = $J(json);
            json = json.evalJSON(); // lo hacemos con prototype
            
        var tmpl = '<table border="0">#{cont}</table>',
			tmp = '';
			
		for (var k in json){
			var v = json[k];
			if (k == 'dia'){
				v = DIAS[v];
			}
			tmp += '<tr><th>#{k}</th><td>#{v}</td></tr>'.interpolate(
				{'k': k, 'v': v}
			);
			console.log(k, json[k]);
		}
		tmp = tmpl.interpolate({'cont': tmp});
		mostrar_div(tmp);
		} catch (e) { console.log(e)}
		
	}
	
	function hideTip(){
		window.clearTimeout(timeoutId);
		tip_div.style.display = 'none';
	}
	
	function mouseIn(e) {
		timeoutId = window.setTimeout(showTip, tiempo, [e]);
	}
	
	function mouseOut(e){
		hideTip();
	}
	
	$E.on(window, 'load', function (){
        var celdas = YAHOO.util.Selector.query('.aula_hora');
        if (verbose)
            console.log("Cantidad de celdas:", celdas.length);
        for (var i = 0; i < celdas.length; i++){
            var celda = celdas[i];
            $E.on(celda, 'mouseover', mouseIn);
            $E.on(celda, 'mouseout', mouseOut);
            
        }
    });
    // Publicamos parte de la clase...
	return {
		setVerbose: function (b) {
			if (YAHOO.lang.isBoolean(b))
				verbose = b;
		}
		
	}
	} catch(e){
		console.log(e);
	}
})();
