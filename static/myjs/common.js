function getValues(dict){
    var values = [];
    for(var key in dict){
        values.push(dict[key]);
    }
    return values;
}

function getOrderedDeptDict() {
    var deptDict;
    $.ajax({
        url: '/dc/deptorder.ajax',        // '{% url "ajaxDeptOrder" %}',
        type: 'POST',
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
        url: '/dc/staff.ajax',
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

