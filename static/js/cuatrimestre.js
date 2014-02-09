(function (){
    var $ = YAHOO.util.Dom.get,
        $$ = YAHOO.util.Selector.query,
        $E = YAHOO.util.Event;
        
    // Cuando se cargue la página
    $E.addListener(window, 'load', function (){
        
        var fields = $$('.CutrimestreField');
        
        $E.on(fields, 'click', function (){
            alert("Hoa");
        });

    
    });
    console.log('hoa');
})();