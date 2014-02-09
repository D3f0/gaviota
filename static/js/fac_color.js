(function (){
    var $D = YAHOO.util.Dom,
        $ = $D.get,
        $E = YAHOO.util.Event,
        el = 'id_color';
        
    function colorFieldClickListener(event){
        try{
        console.log(this);
        console.log(event);
        } catch(e){
            alert(e);
        }
    }
    
    $E.onAvailable(el, function (){
        // $E.addListener(el, 'click', colorFieldClickListener);
        var new_id = $D.generateId(),
            div = document.createElement('div'),
            element = $(el);
        div.id = new_id;
        element.parentNode.appendChild(div);
        //div.innerHTML = "Hola";
        //var document.getE
        function onRgbChange(event, cp){
            element.value = cp.get('hex');
        }
        var cp = new YAHOO.widget.ColorPicker(new_id,{
                showhsvcontrols: true, 
                showhexcontrols: true, 
                images: { 
		           PICKER_THUMB: "picker_thumb.png", 
		           HUE_THUMB: "hue_thumb.png" 
            }});
        cp.on('rgbChange', onRgbChange, cp);
    });
    
})();
