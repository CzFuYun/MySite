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

function getMouseWindowLocation(e){
    var ev = e || window.event;
    return [ev.clientX, ev.clientY];
}

function getMousePageLocation(e){
    var ev = e || window.event;
    var scrollX = document.documentElement.scrollLeft || document.body.scrollLeft;
    var scrollY = document.documentElement.scrollTop || document.body.scrollTop;
    var x = ev.pageX || ev.clientX + scrollX;
    var y = ev.pageY || ev.clientY + scrollY;
    return [x, y];
}

function addDate(daysNum, dateStr, returnMode){
    var d = dateStr ? new Date(dateStr) : new Date();
    d.setDate(d.getDate() + daysNum);
    if(!returnMode || returnMode === 'd'){
        // 返回日期对象
        return d;
    }else if(returnMode === 's'){
        // 返回日期字符串
        return d.getFullYear() + '-' + d.getMonth() + 1 + '-' + d.getDate();
    }else if(returnMode === 'n'){
        // 返回时间戳
        return Date.parse(d);
    }
}

function dateDif(dateStr1, dateStr2){
    let d1 = new Date(dateStr1),
        d2 = dateStr2 ? new Date(dateStr2) : new Date();
    let deltaMS = d1 - d2;
    return parseInt(deltaMS / (1000 * 3600 * 24));
}

function buildTableStructure(tableHeadStructure, rowLabel, tableId, tableClass, tablePropertyDict, needTableFoot) {
    // tablePropertyDict: {'th': '', 'td': ''}
    $('#' + tableId).remove();
    let table = document.createElement('table');
    let thead = document.createElement('thead');
    let tbody = document.createElement('tbody');
    let theadRow1 = document.createElement('tr');
    let theadRow2;
    let colNum = 0;
    if(tableClass){
        table.className = tableClass;
    }
    if(tableId){
        table.id = tableId;
    }
    for(let i in tableHeadStructure){
        let th = document.createElement('th');
        if(tablePropertyDict.th){
            for(let p in tablePropertyDict.th){
                th.setAttribute(p, tablePropertyDict.th[p]);
            }
        }
        if(tableHeadStructure[i].length){
            if(!theadRow2){
                theadRow2 = document.createElement('tr');
            }
            let colSpan = tableHeadStructure[i].length;
            th.setAttribute('colspan', colSpan);
            for(let j=0; j<tableHeadStructure[i].length; j++){
                let th2 = document.createElement('th');
                if(tablePropertyDict.th){
                    for(let p in tablePropertyDict.th){
                        th2.setAttribute(p, tablePropertyDict.th[p]);
                    }
                }
                let tmp = tableHeadStructure[i][j];
                th2.innerText = typeof tmp === 'object' ? tmp[0] : tmp;
                theadRow2.appendChild(th2);
                colNum ++;
            }
        }else{
            th.setAttribute('rowspan', 2);
            colNum ++;
        }
        th.innerText = i;
        theadRow1.appendChild(th);
    }
    thead.appendChild(theadRow1);
    if(theadRow2){
        thead.appendChild(theadRow2);
    }
    table.appendChild(thead);
    if(rowLabel){
        for(let i=0; i<rowLabel.length; i++){
            let tr = document.createElement('tr');
            for(let j=0; j<colNum; j++){
                let td = document.createElement('td');
                if(tablePropertyDict.td){
                    for(let p in tablePropertyDict.td){
                        td.setAttribute(p, tablePropertyDict.td[p]);
                    }
                }
                if(j){
                    td.className = 'value_td';
                }else{
                    td.innerText = rowLabel[i];
                }
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }
    }
    table.appendChild(tbody);
    if(needTableFoot){
        let thead = document.createElement('thead');
        let tr = document.createElement('tr');
        for(let j=0; j<colNum; j++){
            let th = document.createElement('th');
            if(tablePropertyDict.th){
                for(let p in tablePropertyDict.th){
                    th.setAttribute(p, tablePropertyDict.th[p]);
                }
            }
            if(j){
                th.className = 'value_td';
            }else{
                th.innerText = '汇总';
            }
            tr.appendChild(th);
        }
        thead.appendChild(tr);
        table.appendChild(thead);
    }
    return {table: table, colNum: colNum};
}

function fillTable(tableId, valuesListByRow){
    console.log(valuesListByRow);
    let table = document.getElementById(tableId);
    let td = document.getElementById(tableId).getElementsByClassName('value_td'),
        n = 0;
    for(let i=0; i<valuesListByRow.length; i++){
        for (let j=0; j<valuesListByRow[i].length; j++){
            td[n].innerText = valuesListByRow[i][j];
            n++;
        }
    }
}

// function scrollHandle() {
//     var scrollTop = window.tableScroll.scrollTop();
//     // 当滚动距离大于0时设置top及相应的样式
//     if (scrollTop > 0) {
//         window.tableCont.css({
//             "top": scrollTop + 'px',
//             "marginTop": "-1px",
//             "padding": 0
//         });
//         window.tableCont_child.css({
//             "borderTop": "1px solid gainsboro",
//             "borderBottom": "1px solid gainsboro",
//             "marginTop": "-1px",
//             "padding": "8px"
//         })
//     } else {
//     // 当滚动距离小于0时设置top及相应的样式
//         window.tableCont.css({
//             "top": scrollTop + 'px',
//             "marginTop": "0",
//         });
//         window.tableCont_child.css({
//             "border": "none",
//             "marginTop": 0,
//             "marginBottom": 0,
//         })
//     }
// }

function lockThead(tableDivId, tableId){
    var r = window.devicePixelRatio;        // 屏幕缩放比例
    $('#' + tableDivId).addClass('table-responsive section-scroll').attr('style', 'height:' + String(screen.availHeight * 0.68 /r) + 'px');
    $('#' + tableId + ' thead:first th').addClass('table-th-css');
    tableCont = $('.section-scroll tr th');
    tableCont_child = $('.section-scroll tr th div');
    tableScroll = $('.section-scroll');
    tableScroll.on('scroll', function(){
        var scrollTop = tableScroll.scrollTop();
        // 当滚动距离大于0时设置top及相应的样式
        if (scrollTop > 0) {
            tableCont.css({
                "top": scrollTop + 'px',
                "marginTop": "-1px",
                "padding": 0
            });
            tableCont_child.css({
                "borderTop": "1px solid gainsboro",
                "borderBottom": "1px solid gainsboro",
                "marginTop": "-1px",
                "padding": "8px"
            })
        } else {
        // 当滚动距离小于0时设置top及相应的样式
            tableCont.css({
                "top": scrollTop + 'px',
                "marginTop": "0",
            });
            tableCont_child.css({
                "border": "none",
                "marginTop": 0,
                "marginBottom": 0,
            })
        }

    });
}

