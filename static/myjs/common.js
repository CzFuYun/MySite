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
        url: parseUrl('ajaxStaffName'),
        async: false,
        data: {dept_code: deptCode},
        dataType: 'json',
        success: function (data) {
            staffDict = data;
            console.log(data);
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

function getDictFromPageLocation(){
    let loca = location.search.substring(1),
        dict = {};
    $.each(loca.split('&'), function(){
        var pair = this.split('=');
        var key = pair[0],
            value = pair[1];
        try{
            dict[key] = value;
        }catch (e) {
            if(typeof dict[key] === 'object'){
                dict[key].push(value);
            }else {
                let v = dict[key];
                dict[key] = [v, value];
            }
        }
    });
    return dict;
}

function downloadFileByForm(url, data, method){
    //data can be string of parameters or array/object
    data = typeof data === 'string' ? data : jQuery.param(data);
    var inputs ='';
    $.each(data.split('&'), function(){
        var pair = this.split('=');
        inputs += '<input type="hidden" name="'+ pair[0] + '" value="' + pair[1] + '" />';
    });
    $('<form target="_blank" action="' + url +'" method="' + (method || 'post') + '">' + inputs + '</form>').appendTo('body').submit().remove();
}

function openSmallFile(url){
    let a = '<a href="' + url + '" target="_blank"></a>';
    $(a)[0].click();
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
    // console.log(valuesListByRow);
    // let table = document.getElementById(tableId);
    let td = document.getElementById(tableId).getElementsByClassName('value_td'),
        n = 0;
    for(let i=0; i<valuesListByRow.length; i++){
        for (let j=0; j<valuesListByRow[i].length; j++){
            td[n].innerText = valuesListByRow[i][j];
            n++;
        }
    }
}


function lockThead(tableParentDivId, tableId){
    var r = window.devicePixelRatio;        // 屏幕缩放比例
    let $div = $('#' + tableParentDivId),
        $thead = tableId ? $('#' + tableId + ' thead:first th') : $('table thead:first th', $div);
    $div.addClass('table-responsive section-scroll').attr('style', 'height:' + String(screen.availHeight * 0.78 / r) + 'px');
    $thead.addClass('table-th-css');
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
            });
        }
    });
}

function getCnChars(string){
    let r = /^[\u4e00-\u9fa5]+$/;
    try{
        return r.exec(string)[0];
    }catch (e) {
        return null;
    }
}

function valuesListToDict(valuesList){
    let dict = {};
    for(let i=0; i<valuesList.length; i++){
        dict[valuesList[i][0]] = valuesList[i][1];
    }
    return dict;
}

function makeListHtml(tableCol, tableColOrder, dataList){
    let htmlTable = '<table class="table full-color-table full-dark-table table-sm table-hover table-bordered">';
    htmlTable += '<thead><tr>';
    for(let i=0; i<tableColOrder.length; i++){
        let colIndex = tableColOrder[i];
        let colWidth = tableCol[colIndex]['width'];
        let colName = tableCol[colIndex]['col_name'];
        htmlTable += '<th width="' + colWidth +'">' + colName + '</th>';
    }
    htmlTable += '</tr></thead><tbody>';
    for(let r=0; r<dataList.length; r++){
        let data = dataList[r];
        htmlTable += '<tr>';
        for(let c=0; c<tableColOrder.length; c++){
            htmlTable += '<td';
            let tdAttrDict = tableCol[tableColOrder[c]]['td_attr'];
            let tdValue = data[tableColOrder[c]];
            if(tdAttrDict){
                for(let k in tdAttrDict){
                    if(k === 'choice_to_display'){
                        let choicesDict = tdAttrDict[k];
                        tdValue = choicesDict[tdValue];
                    }else if(k.indexOf('!') === 0){
                        if(typeof tdAttrDict[k] === 'object'){
                            htmlTable += (' ' + k.substring(1) + '=\'' + JSON.stringify(tdAttrDict[k]) + '\'');
                        }else {
                            htmlTable += (' ' + k.substring(1) + '="' + tdAttrDict[k] + '"');
                        }
                    }else if(typeof data[tdAttrDict[k]] === 'object'){
                        htmlTable += (' ' + k + '=\'' + JSON.stringify(data[tdAttrDict[k]]) + '\'');
                    }
                    else{
                        htmlTable += (' ' + k + '="' + data[tdAttrDict[k]] + '"');
                    }
                }
            }
            htmlTable += ('>' + tdValue + '</td>');
        }
        htmlTable += '</tr>'
    }
    htmlTable += '</tbody></table>';
    return htmlTable;
}

Date.prototype.Format = function(fmt) {
    //author: meizz
    var o = {
        "M+" : this.getMonth() + 1, //月份
        "d+" : this.getDate(), //日
        "h+" : this.getHours(), //小时
        "m+" : this.getMinutes(), //分
        "s+" : this.getSeconds(), //秒
        "q+" : Math.floor((this.getMonth() + 3) / 3), //季度
        "S" : this.getMilliseconds() //毫秒
    };
    if (/(y+)/.test(fmt))
        fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
        if (new RegExp("(" + k + ")").test(fmt))
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length === 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
};