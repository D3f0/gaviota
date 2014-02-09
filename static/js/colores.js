(function (){
    
    var $ = YAHOO.util.Dom.get,
        $$ = YAHOO.util.Selector.query,
        $E = YAHOO.util.Event;
        
    $E.onDOMReady(function (){
        
        var color_select = $('id_color'),
            div = document.createElement('div');
        color_select.parentNode.appendChild(div);
//        div.innerHTML = "Hola";
        div.style.width = '40px';
        div.style.height = '40px';
        div.style.border = '1px solid #CCC';
        div.style.backgroundColor = '#'+color_select.value;
        
        $E.addListener(color_select, 'change', function (){
            div.style.backgroundColor = '#'+color_select.value;
        });
    });
})();
