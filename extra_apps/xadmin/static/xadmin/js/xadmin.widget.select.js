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
    let pkDict = {};
    $.fn.exform.renders.push(function(f){
        if($.fn.selectize){
            f.find('select:not(.select-search):not([multiple=multiple])').selectize();
            f.find('.select-search').each(function(){
                var $el = $(this);

                var targetUrl = this.getAttribute('data-search-url');
                if(!pkDict.hasOwnProperty(targetUrl)){
                    var r = /\/(\w+)\/(\w+)\/$/g;
                    var appModel = r.exec(targetUrl);
                    var appName = appModel[1];
                    var modelName = appModel[2];
                    pkDict[targetUrl] = getPkName(appName + '.' + modelName);
                }

                var preload = $el.hasClass('select-preload');
                $el.selectize({
                    valueField: pkDict[targetUrl],
                    labelField: '__str__',
                    searchField: '__str__',
                    create: false,
                    maxItems: 1,
                    preload: preload,
                    load: function(query, callback) {
                        if(!preload && !query.length) return callback();
                        $.ajax({
                            url: $el.data('search-url') + $el.data('choices'),
                            dataType: 'json',
                            // async: false,
                            data: {
                                '_q_': query,
                                '_cols': pkDict[targetUrl] + '.__str__'
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
        }
    });
})(jQuery);

