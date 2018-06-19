function getValues(dict){
    let values = [];
    for(let key in dict)
        values.push(dict[key]);
    return values;
}

function getDeptOrder() {
    let ordered_dept = [];
    $.ajax(
        {
            url: '/dc/deptorder.ajax',        // '{% url "ajaxDeptOrder" %}',
            type: 'POST',
            async: false,
            dataType: 'json',
            success: function (data) {
                ordered_dept = data;
            }
        }
    );
    return ordered_dept;
}

function sortDict(dict, asc){
    let sort_key,
        new_dict = {};
    if(asc == null || asc)
        sort_key = Object.keys(dict).sort();
    else
        sort_key = Object.keys(dict).sort().reverse();
    for(let i in sort_key)
        new_dict[sort_key[i]] = dict[sort_key[i]];
    return new_dict;
}

function sortNumber(a,b) {
    return  a - b;
}

function getValuesOrderByKeys(dict, needReverse){
    // 获取字典的全部值，按键排序
    needReverse = needReverse || false;
    let dictKeysAreNumric = true;
    let keyList = Object.keys(dict);
    for(let i=0; i<keyList.length; i++){
        let tmp = Number(keyList[i]);
        if(tmp)
            keyList[i] = tmp;
        else{
            dictKeysAreNumric = false;
            break;
        }
    }
    if(dictKeysAreNumric)
        keyList.sort(sortNumber);
    else
        keyList.sort();
    let valuesList = [];
    if(needReverse)
        keyList.reverse();
    for(let i=0; i<keyList.length; i++){
        valuesList.push(dict[keyList[i]])
    }
    return valuesList;
}

function getKeyFromOneKvp(kvp){
    for(let k in kvp)
        return k;
}

function getValueFromOneKvp(kvp){
    for(let k in kvp)
        return kvp[k];
}

