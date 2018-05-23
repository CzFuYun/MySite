function prepareBaseDataForEcharts(dataArray){
    // dataArray:[["2017-11-10", "对公定期保证金存款", 3000],["2017-11-10", "对公活期存款", 7],["2017-11-20", "对公定期保证金存款", 3000],["2017-11-20", "对公活期存款", 17]]
    let xAxisData = [],
        unsortedSeriesData = {},
        seriesData = {};
    let tmp = {};
    for(let i=0; i<dataArray.length; i++){
        tmp[dataArray[i][0] + dataArray[i][1]] = dataArray[i][2];
        if($.inArray(dataArray[i][0], xAxisData) < 0)
            xAxisData.push(dataArray[i][0]);
        if(!unsortedSeriesData.hasOwnProperty(dataArray[i][1]))
            unsortedSeriesData[dataArray[i][1]] = [];
    }
    let valueAvg_seriesData = {};
    for(let k in unsortedSeriesData) {
        let valueSum = 0;
        for (let i = 0; i < xAxisData.length; i++) {
            let value = 0;
            if (tmp.hasOwnProperty(xAxisData[i] + k)) {
                value = tmp[xAxisData[i] + k];
                valueSum += value;
            }
            unsortedSeriesData[k].push(value);
        }
        if(valueSum){
            let valueAvg = Math.round(valueSum / xAxisData.length);
            valueAvg_seriesData[valueAvg] = {};
            valueAvg_seriesData[valueAvg][k] = unsortedSeriesData[k];
        }
    }
    valueAvg_seriesData = sortDict(valueAvg_seriesData);
    console.log(valueAvg_seriesData);
    for(let k in valueAvg_seriesData){
        // seriesData[Object.keys(valueAvg_seriesData[k])[0]] = Object.values(valueAvg_seriesData[k])[0];
        let kvp = valueAvg_seriesData[k];
        seriesData[getKeyFromOneKvp(kvp)] = getValueFromOneKvp(kvp);
    }
    return {
        xAxisData: xAxisData,
        seriesData: seriesData,
    }

}

function prepareOptionForEchatrsCommonLine(dataArray, needStack, isSmooth){
    // dataArray:[["2017-11-10", "对公定期保证金存款", 3000],["2017-11-10", "对公活期存款", 7],["2017-11-20", "对公定期保证金存款", 3000],["2017-11-20", "对公活期存款", 17]]
    let series = [],
        legend = {data: []};
    let stack = needStack ? '总量' : '';
    dataForEcharts = prepareBaseDataForEcharts(dataArray);
    let seriesData = dataForEcharts.seriesData;
    for(let k in seriesData){
        legend['data'].push(k);
        series.push({
            name: k,
            type: 'line',
            stack: stack,
            data: seriesData[k],
            areaStyle: {normal: {}},
            smooth: isSmooth,
        });
    }
    return {
        legend: legend,
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                label: {backgroundColor: '#6a7985'}
            }
        },
        toolbox: {
            show: true,
            y: 'bottom',
            feature: {
                mark: {show:true},
                dataView : {show: true, readOnly: false},
                magicType : {show: true, type: ['line', 'bar', 'stack', 'tiled']},
                restore : {show: true},
                saveAsImage: {show: true},
            },
        },
        xAxis: [
            {
                type : 'category',
                boundaryGap : false,
                data : dataForEcharts.xAxisData
            }
        ],
        yAxis: {type: 'value'},
        series: series,
    }
}