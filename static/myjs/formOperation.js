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

function addItems(selectElemId, valueTextDict, defaultSelectedText, clearBeforeAdd, onchangeFunctionObject){
    var selectElem = document.getElementById(selectElemId),
        index = 0,
        oldOptions = selectElem.options,
        newOption;
    if(clearBeforeAdd){
        for(var i=oldOptions.length-1; i>=0; i--){
            oldOptions[i].remove();
        }
        if(!defaultSelectedText){
            // ↓添加一个空选项
            newOption = document.createElement('option');
            newOption.setAttribute('value', '');
            newOption.innerText = '';
            selectElem.appendChild(newOption);
            selectElem.selectedIndex = index;
        }
    }
    else{
        for(var i=0; i<oldOptions.length; i++){
            if(oldOptions[i].text === defaultSelectedText){
                selectElem.selectedIndex = index;
            }
            index ++;
        }
    }
    for(var v in valueTextDict){
        newOption = document.createElement('option');
        newOption.setAttribute('value', v);
        newOption.innerText = valueTextDict[v];
        selectElem.appendChild(newOption);
        if(valueTextDict[v] === defaultSelectedText){
            selectElem.selectedIndex = index;
        }
        index ++;
    }
    if(onchangeFunctionObject){
        selectElem.setAttribute('onchange', onchangeFunctionObject.name + '(this)');
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
    $('li label input', $form).each(
        function(index, elem){
            $(elem).parent().before($(elem));
        }
    );
    $('ul[id]', $form).each(
        function(index, elem){
            let $elem = $(elem);
            $elem.addClass('form-control list-unstyled list-inline');
            elem.style.display = 'block';
            elem.style['margin-bottom'] = 0;
            elem.style['padding-bottom'] = 0;
            elem.style['padding-left'] = 0;
            // elem.style({display: 'block', margin: 0, 'padding-bottom': 0});
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
            let $elem = $(elem);
            $elem.select2({
                language: 'zh-CN',
                placeholder: '请选择',
                width: '100%',
                minimumInputLength: 2,
                theme: 'default'
            });
        }
    );


    $('[required]', $form).each(       // 必填项标签加粗
        function(index, elem){
            let $elem = $(elem);
            try{
                $elem.prev()[0].style['font-weight'] = 'bold';
            }catch (e) {
                console.log(elem);
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