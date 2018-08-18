// 获取form中的input对象
function getInputsOnForm(formId){
    var inputTags = ['input', 'select', 'textarea'],
        form = document.getElementById(formId),
        ret = [];
    for(var i=0; i<inputTags.length; i++){
        var inputs = form.getElementsByTagName(inputTags[i]);
        for(var j=0; j<inputs.length; j++){
            ret.push(inputs[j]);
        }
    }
    return ret;
}

function getFormChildren(formId){
    var form = document.getElementById(formId),
        formChildren = form.children;
}

// 获取或设置表单中单个子对象的键值对
function getOrSetFormChildValue(formChildElem, valueToSet) {
    var valueSourceList = ['value', 'innerText'];
    var tag = formChildElem.tagName.toLowerCase();
    var elemType = tag === 'input' ? formChildElem.type.toLowerCase() : tag;
    var elemName = formChildElem.name, elemValue;
    if((elemType !== 'radio' && elemType !=='checkbox') || formChildElem.checked){
        var valueSource;
        for(var i=0; i<valueSourceList.length; i++){
            valueSource = valueSourceList[i];
            elemValue = formChildElem[valueSource];
            if(elemValue){
                break;
            }
        }
        if(valueToSet){
            formChildElem[valueSource] = elemValue;
        }else{
            return [elemName, elemValue];
        }
    }
}

function getFormData(formId){
    // 获取表单中的数据，若需上传文件，返回FormData对象；否则返回键值对
    var inputElemArray = getInputsOnForm(formId),
        formData;
    for(var i=0; i<inputElemArray.length; i++){
        if(inputElemArray[i].type === 'file'){      // enctype="multipart/form-data"
            formData = new FormData();
            break;
        }
    }
    if(formData){
        for(var i=0; i<inputElemArray.length; i++){
            if(inputElemArray[i].type === 'file'){
                formData.append(inputElemArray[i].name, inputElemArray[i].files[0]);
            }else{
                formData.append(inputElemArray[i].name, getOrSetFormChildValue(inputElemArray[i])[1]);
            }
        }
        return formData;
    } else{
        var dataDict = {};
        for(var i=0; i<inputElemArray.length; i++){
            var tmp = getOrSetFormChildValue(inputElemArray[i]);
            if(tmp){
                if(!dataDict[tmp[0]]){
                    dataDict[tmp[0]] = [];
                }
                dataDict[tmp[0]].push(tmp[1]);
            }
        }
        return dataDict;
    }
}

function addItems(selectElemId, optionData, defaultSelectedText, clearBeforeAdd, onchangeFunctionObject){
    var $selectElem = $('#' + selectElemId),
        $oldOptions = $('option', $selectElem),
        $newOption,
        index = 0;
    if(clearBeforeAdd){
        $oldOptions.remove();
        if(!defaultSelectedText){
            // ↓如果没有指定默认选项，则需要添加一个空选项
            $newOption = $('<option value="">请选择</option>');
            $newOption.appendTo($selectElem);
            $selectElem.selectedIndex = index;
        }
    }
    else{
        for(var i=0; i<$oldOptions.length; i++){
            if($oldOptions[i].text === defaultSelectedText){
                $selectElem.selectedIndex = index;
            }
            index ++;
        }
    }
    if(Array.isArray(optionData)){
        // optionData为数组（列表）
        for(let i=0; i<optionData.length; i++){
            $newOption = $('<option value="' + optionData[i][0] + '">' + optionData[i][1] + '</option>');
            $newOption.appendTo($selectElem);
            if(optionData[i][1] === defaultSelectedText){
                $selectElem.selectedIndex = index;
            }
            index ++;
        }
    }else{
        // optionData为字典
        for(var v in optionData){
            $newOption = $('<option value="' + v + '">' + optionData[v] + '</option>');
            $newOption.appendTo($selectElem);
            if(optionData[v] === defaultSelectedText){
                $selectElem.selectedIndex = index;
            }
            index ++;
        }
    }
    if(onchangeFunctionObject){
        $selectElem.setAttribute('onchange', onchangeFunctionObject.name + '(this)');
    }
}

function fillForm(formId, idValueDict){
    var form = document.getElementById(formId);
    for(var i in idValueDict){
        var e = $('#' + formId + ' #' + i)[0];


        e.value = idValueDict[i];
    }
}

function submitByAjax(url, formId){
    var requestSuccess;
    // var formData = getFormData(formId);
    $.post({
        url: url,
        data: getFormData(formId),
        dataType:'json',
        cache: false,
        processData: false,
        contentType: false,
        async: false,
        success: function(response){
            requestSuccess = response.success;
            if(!requestSuccess){
                alert(response.error);
            }
        }
    });
    return requestSuccess;
}

function makeForm(urlName, data, sizeX, sizeY, formId){
    $('#'+ formId + '_container').remove();
    $.get({
        url: parseUrl(urlName),
        async: false,
        timeout: 10000,
        data: $.extend({}, data, {
            urlName: urlName,
            sizeX: sizeX,
            sizeY: sizeY,
            screenX: screen.availWidth,
            screenY: screen.availHeight,
            formId: formId
        }),
        dataType: 'text',
        success: function(response){
            let $form = $(response);
            $('script:first').before($form);
        }
    });
}

function fillForm2(formId, dataDic){
    $('[name]', '#' + formId).each(
        function(index, elem){
            let name = elem.name;
            elem.value = dataDic[name];
        }
    );
}

// function modifyForm(formId){
//     let selector = formId ? '#' + formId : 'form';
//     // $(selector + ' p').each(
//     //     function(index, elem){
//     //         $(elem).addClass('form-group');
//     //     }
//     // );
//     $(selector + ' li label input').each(
//         function(index, elem){
//             $(elem).parent().before($(elem));
//         }
//     );
//     $(selector + ' ul').each(
//         function(index, elem){
//             $(elem).addClass('form-control list-unstyled list-inline');
//         }
//     );
//     $(selector + ' select').each(
//         function(index, elem){
//             $(elem).addClass('form-control custom-select');
//         }
//     );
//     $(selector + ' [type=date]').each(
//         function(index, elem){
//             $(elem).addClass('form-control');
//         }
//     );
//
// }
function modifyForm(form){
    let $form = form ? form : $('form');
    $('p', $form).each(
        function(index, elem){
            let $elem = $(elem);
            $elem.addClass('from-group');
            $elem.css({
                'margin-bottom': '20px'
            });
        }
    );
    $('li label input', $form).each(
        function(index, elem){
            $(elem).parent().before($(elem));
        }
    );
    $('ul[id]', $form).each(
        function(index, elem){
            let $elem = $(elem);
            $elem.addClass('form-control list-unstyled list-inline');
            $elem.css({
                'display': 'block',
                'margin-bottom': 0,
                'padding': 0,
                'height': '39px'
                // 'padding-left': 0
            });
            $elem.children('li').css({
                'padding': '6px'
            });
            $elem.appendTo($elem.prev());
        }
    );
    $('ul[class*=errorlist]', $form).each(
        function(index, elem){
            $elem = $(elem);
            // $elem.removeClass('form-control');
            $elem.addClass('form-control-feedback');
            let $p = $elem.next();
            $elem.appendTo($p);
            $p.addClass('has-danger');
        }
    );
    $('select', $form).each(
        function(index, elem){
            $(elem).addClass('form-control custom-select');
        }
    );

    $('input', $form).each(
        function(index, elem){
            $(elem).addClass('form-control');
        }
    );

    $('[select2]', $form).each(
        function(index, elem){
            $(elem).select2();
        }
    );
    $('[required]', $form).each(       // 必填项标签加粗
        function(index, elem){
            let $elem = $(elem);
            try{
                $elem.prev()[0].style['font-weight'] = 'bold';
            }catch (e) {
                $elem.parents('ul').prev()[0].style['font-weight'] = 'bold';
            }
            
        }
    );
    $('[hidden][readonly]', $form).each(       // 必填项标签加粗
        function(index, elem){
            let $elem = $(elem);
            $elem.parent()[0].style['display'] = 'none';
        }
    );

}

function showForm(formId, status){
    showMask(status);
    document.getElementById(formId).style.display = status ? 'block' : 'none';
}

function showMask(status){
    if(!document.getElementById('mask')){
        let mask = document.createElement('div');
        mask.style = 'position: fixed; background-color: black; opacity: 0.5; display: none; top: 0px; bottom: 0px; left: 0px; right: 0px;';
        document.appendChild(mask);
    }
    document.getElementById('mask').style.display = status ? 'block' : 'none';
}

function makeDataList(id, urlName, postDataDict){
    $.post({
        url: parseUrl(urlName),
        data: postDataDict,
        dataType: 'json',
        success: function(response){
            // console.log(response);
            let $dataList = $('#' + id);
            if(!$dataList.length){
                $dataList = $('<datalist id="' + id + '" class="form-group">');
                $('[list=' + id + ']').after($dataList);
            }else {
                $('#' + id + ' option').remove();
            }
            for(let i=0; i<response.length; i++){
                $('<option value="' + response[i] + '"></option>').appendTo($dataList);
            }

        }
    });
}

function bindAjaxDataSourceToSelect2(url, $select2Elem){
    // console.log(url);
    // console.log($select2Elem);
    $select2Elem.select2({
        placeholder: '请选择',
        width: '100%',
        language: 'zh-CN',
        minimumInputLength: 1,
        allowClear: true,
        ajax: {
            url: url,
            async: false,
            delay : 250,        // 延迟显示
            dataType: 'json',
            cache : false,
            data: function(params){
                return{
                    term: params.term,      // 搜索框内输入的内容
                    page: params.page,      // 第几页，分页
                    rows: 10               // 每页显示多少行
                };
            },
            processResults: function(data, params){
                params.page = params.page || 1;
                let ret = [];
                for(let i=0; i<data.length; i++)
                {
                    ret.push(
                        {id: data[i][0], text: data[i][1]}
                    );
                }
                return {
                    results: ret,    //必须处理成[{ id: , text: }, { id: , text:  }, ]格式
                    pagination: {
                        more: params.page < data.total_count
                    }
                };
            },
            templateResult: function(repo){return repo.text;},
            templateSelection: function(repo){return repo.text;}
        }
    });
}

function bindStaticDataSourceToSelect2(href, $select2Elem){
    let optionData = [{id: '', text: ''}];
    $.get({
        url: href,
        async: false,
        dataType: 'json',
        success: function (response) {
            for(let i=0; i<response.length; i++){
                optionData.push({id: response[i][0], text: response[i][1]});
            }
        }
    });
    $select2Elem.select2({
        placeholder: '请选择',
        width: '100%',
        language: 'zh-CN',
        minimumInputLength: 1,
        allowClear: true,
        data: optionData
    });
}

function bindDataSourceToSelect2(){
    $('select[select2]').each(function(index, elem){
        let $select2Elem = $(elem),
            href = $select2Elem.attr('href'),
            srcType = $select2Elem.attr('src_type');
        if(srcType === 'static'){
            bindStaticDataSourceToSelect2(href, $select2Elem);
        }else if (srcType === 'dynamic'){
            bindAjaxDataSourceToSelect2(href, $select2Elem);
        }
        $('.select2-selection[aria-labelledby]', $select2Elem.next()).each(
            function(index, elem){
                $(elem).css({
                    'height': '39px',
                    'border': '1px solid rgba(0,0,0,.15)'
                });
                $(elem).children('span').css({
                    'margin': '0px',
                    'padding': '6px',
                    'height': '39px'
                });
            }
        );
    });
}

function addSatelliteButtonForInput(inputId, buttonInfo){
    // buttonInfo = [{icon, title, onclick}]
    let $buttonGroup = $('<div class="btn-group"></div>');
    let $input = $('#' + inputId);
    let $div = $('<div class="input-group"></div>');
    $input.after($div);
    $input.appendTo($div);
    for(let i=0; i<buttonInfo.length; i++){
        let $button = $('<button type="button" title="' + buttonInfo[i].title + '" class="btn btn-info" onclick="' + buttonInfo[i].onclick + '"><i class="' + buttonInfo[i].icon + '"></i></button>');
        $buttonGroup.append($button);
    }
    $input.after($buttonGroup);
}

function makeModalDialog(){
    let $dialogDiv = $('<div style=""></div>');
}