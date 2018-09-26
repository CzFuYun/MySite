function getPkName(modelClass) {
    let pk;
    $.ajax({
        url: '/pk/',
        async: false,
        type: 'get',
        data: {modelClass: modelClass},
        dataType: 'text',
        success: function(response){
            pk = response;
        }
    });
    return pk;
}
;
(function($){
    // add select render
    $.fn.exform.renders.push(function(f){
      if($.fn.selectize){
        f.find('select:not(.select-search):not([multiple=multiple])').selectize();
        f.find('.select-search').each(function(){
            var $el = $(this);

            var s = this.getAttribute('data-search-url');
            var r = /\/(\w+)\/(\w+)\/$/g;
            var res = r.exec(s);
            var appName = res[1];
            var modelName = res[2];
            var modelClass = appName + '.' + modelName;
            // console.log(modelClass);
            var pk = getPkName(modelClass);

            var preload = $el.hasClass('select-preload');
            $el.selectize({
                valueField: pk,  // 'id',
                labelField: '__str__',
                searchField: '__str__',
                create: false,
                maxItems: 1,
                preload: preload,
                load: function(query, callback) {
                    if(!preload && !query.length) return callback();
                    $.ajax({
                        url: $el.data('search-url')+$el.data('choices'),
                        dataType: 'json',
                        async: false,
                        data: {
                            '_q_': query,
                            '_cols': pk + '.__str__'   // 'id.__str__'
                        },
                        type: 'GET',
                        error: function() {
                            callback();
                        },
                        success: function(res) {
                            callback(res.objects);
                        }
                    });
                }
            });
        });
    }});
})(jQuery);

