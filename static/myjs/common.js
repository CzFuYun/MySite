function parseUrl(urlName){
    var ret = false;
    $.post({
        async: false,
        url: 'url.convert',
        data: {url_name: urlName},
        dataType: 'json',
        success: function(response){
            if(response.success){
                ret = response.data;
            }else{
                alert(response.error);
            }
        },
        error: function(){}
    });
    return ret;
}

function getValues(dict){
    var values = [];
    for(var key in dict){
        values.push(dict[key]);
    }
    return values;
}

function getOrderedDeptDict() {
    var deptDict;
    $.get({
        url: parseUrl('ajaxDeptOrder'),
        async: false,
        dataType: 'json',
        success: function (data) {
                deptDict = data;
        },
        error: function(){
            alert('\u83b7\u53d6\u7ecf\u8425\u90e8\u95e8\u4fe1\u606f\u5931\u8d25');
        }
    });
    return deptDict;
}

function getStaffDict(deptCode){
    var staffDict;
    $.post({
        url: parseUrl('ajaxStaff'),
        async: false,
        data: {dept_code: deptCode},
        dataType: 'json',
        success: function (data) {
            staffDict = data;
        },
        error: function () {
            alert('\u83b7\u53d6\u5458\u5de5\u540d\u5355\u5931\u8d25');
        }
    });
    return staffDict;
}

function sortDict(dict, asc){
    var sort_key,
        new_dict = {};
    if(asc == null || asc){
        sort_key = Object.keys(dict).sort();
    }
    else{
        sort_key = Object.keys(dict).sort().reverse();
    }
    for(var i in sort_key){
        new_dict[sort_key[i]] = dict[sort_key[i]];
    }
    return new_dict;
}

function sortNumber(a,b) {
    return  a - b;
}

function getValuesOrderByKeys(dict, needReverse){
    // 获取字典的全部值，按键排序
    needReverse = needReverse || false;
    var dictKeysAreNumric = true;
    var keyList = Object.keys(dict);
    for(var i=0; i<keyList.length; i++){
        var tmp = Number(keyList[i]);
        if(tmp){
            keyList[i] = tmp;
        }
        else{
            dictKeysAreNumric = false;
            break;
        }
    }
    if(dictKeysAreNumric){
        keyList.sort(sortNumber);
    }
    else{
        keyList.sort();
    }
    var valuesList = [];
    if(needReverse){
        keyList.reverse();
    }
    for(var i=0; i<keyList.length; i++){
        valuesList.push(dict[keyList[i]]);
    }
    return valuesList;
}

function getKeyFromOneKvp(kvp){
    for(var k in kvp){
        return k;
    }
}

function getValueFromOneKvp(kvp){
    for(var k in kvp){
        return kvp[k];
    }
}

function downloadSmallFile(urlList){
    for(var i=0; i<urlList.length; i++){
        $('<a href="' + urlList[i] + '" download></a>')[0].click();
    }
}

function getElemLocation(elem, offsetX, offsetY){
    // elem: 元素对象或id字符串
    offsetX = offsetX || '+0';
    offsetY = offsetY || '+0';
    var obj = typeof elem === 'string' ? $('#' + elem) : $(elem);
    var location = obj.offset();
    return [
        eval(location.left /*- document.documentElement.scrollLeft*/ + offsetX),
        eval(location.top /*- document.documentElement.scrollTop*/ + offsetY)
    ];
}

function locateScreen(elem){
    // 将屏幕滚动至指定位置，elem: 元素对象或id字符串或数值或坐标
    var location;
    if(typeof elem === 'string' || $(elem)[0].tagName){
        location = getElemLocation(elem);
    }else if(typeof elem === 'number'){
        location = [0, elem];
    }else{
        location = elem;
    }
    $(window).scrollLeft(location[0]);
    $(window).scrollTop(location[1]);
}

function getMouseLocation(e){

}