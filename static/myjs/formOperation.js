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

