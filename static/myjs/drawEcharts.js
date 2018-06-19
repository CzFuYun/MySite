function prepareBaseDataForEcharts(dataArray){
    // dataArray:[["2017-11-10", "对公定期保证金存款", 3000],["2017-11-10", "对公活期存款", 7],["2017-11-20", "对公定期保证金存款", 3000],["2017-11-20", "对公活期存款", 17]]
    let xAxisData = [],
        unsortedSeriesData = {},
        seriesData = {},
        tmp = {};
    for(let i=0; i<dataArray.length; i++){
        tmp[dataArray[i][0] + dataArray[i][1]] = dataArray[i][2];
        if($.inArray(dataArray[i][0], xAxisData) < 0)
            xAxisData.push(dataArray[i][0]);
        if(!unsortedSeriesData.hasOwnProperty(dataArray[i][1]))
            unsortedSeriesData[dataArray[i][1]] = [];
    }
    let valueAvg_seriesData = {};
    for(let k in unsortedSeriesData){
        let valueSum = 0,
            values = [];
        for(let i=0; i<xAxisData.length; i++){
            let value = 0;
            if (tmp.hasOwnProperty(xAxisData[i] + k)){
                value = tmp[xAxisData[i] + k];
                valueSum += value;
            }
            values.push(value);
            unsortedSeriesData[k].push(value);
        }
        if(valueSum){
            let N = xAxisData.length,
                E = 0;
            let valueAvg = valueSum / N;
            for(let i=0; i<values.length; i++){
                E += Math.pow(values[i] - valueAvg, 2);
            }
            let S = Math.round(Math.sqrt(E / N)).toString();
            let randomStr = Math.round(Math.random()*9.9).toString();
            while((valueSum + S + randomStr) in valueAvg_seriesData){      // 末尾拼接一位随机值，防止方差S重复
                randomStr = Math.round(Math.random()*9.9).toString();
            }
            let keyStr = valueSum + S + randomStr;
            valueAvg_seriesData[keyStr] = {};
            valueAvg_seriesData[keyStr][k] = unsortedSeriesData[k];
        }
    }
    valueAvg_seriesData = getValuesOrderByKeys(valueAvg_seriesData);
    for(let k in valueAvg_seriesData){
        let kvp = valueAvg_seriesData[k];
        seriesData[getKeyFromOneKvp(kvp)] = getValueFromOneKvp(kvp);
    }
    return {
        xAxisData: xAxisData,
        seriesData: seriesData,
    }

}

function prepareOptionForEchatrsCommonLine(dataArray, needStack, isSmooth, stepType){
    // dataArray:[["2017-11-10", "对公定期保证金存款", 3000],["2017-11-10", "对公活期存款", 7],["2017-11-20", "对公定期保证金存款", 3000],["2017-11-20", "对公活期存款", 17]]
    let series = [],
        legend = {data: []},
        stack = needStack ? '总量' : '',
        step = stepType || '',
        dataForEcharts = prepareBaseDataForEcharts(dataArray),
        seriesData = dataForEcharts.seriesData;
    for(let k in seriesData){
        legend['data'].push(k);
        series.push({
            name: k,
            type: 'line',
            step: step,
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
        yAxis: [{
            // name : '流量(m^3/s)',
            type : 'value',
        }],
        series: series,
    }
}

function prepareOptionForEchartsInteractionLine(dataArray, commonLineOption, stepType){
    // dataArray: [["2018-03-31", "常州体育产业集团有限公司", 3000], ["2018-04-30", "常州体育产业集团有限公司", 3000], ["2018-05-10", "常州体育产业集团有限公司", 3000]]
    let legendData = commonLineOption.legend.data,
        xAxis = commonLineOption.xAxis,
        xAxis1Data = xAxis[0].data,
        yAxis = commonLineOption.yAxis,
        // yAxisData = yAxis.data,
        series = commonLineOption.series,
        newSeriesName = dataArray[0][1],
        newSeriesData = [],
        delta = 0;
    // console.log('commonLineOption');
    // console.log(commonLineOption);
    legendData.push(newSeriesName);
    // 补足缺失的用信数据
    while(xAxis1Data[delta] < dataArray[delta][0]){     // 若X轴上的最小日期小于传入数据的最小日期
        dataArray.splice(delta, 0, [xAxis1Data[delta], newSeriesName, 0]);
        delta++;
    }
    for(let i=0; i<dataArray.length; i++){
        newSeriesData.push(dataArray[i][2]);
    }
    commonLineOption.axisPointer = {link: {xAxisIndex: 'all'}};       // 联动全部X轴
    // commonLineOption.dataZoom =  [
    //     {
    //         show: true,
    //         realtime: true,
    //         start: 60,
    //         end: 100,
    //         xAxisIndex: [0, 1]
    //     },
    //     {
    //         type: 'inside',
    //         realtime: true,
    //         start: 60,
    //         end: 100,
    //         xAxisIndex: [0, 1]
    //     }
    // ;
    commonLineOption.grid = [{
        left: 50,
        right: 50,
        height: '35%'
    }, {
        left: 50,
        right: 50,
        top: '55%',
        height: '35%'
    }];
    xAxis.push({
        gridIndex: 1,
        type: 'category',
        boundaryGap: false,
        // axisLine: {onZero: true},
        data: xAxis1Data,
        // position: 'top'
    });
    yAxis.push({
        gridIndex: 1,
        // name: newSeriesName,
        type: 'value',
        // inverse: true
    });
    series.push({
        name: newSeriesName,
        type: 'line',
        step: stepType || '',
        xAxisIndex: 1,
        yAxisIndex: 1,
        stack: series[0].stack,
        data: newSeriesData,
        areaStyle: series[0].areaStyle,
        smooth: series[0].smooth,
    });
    // console.log(commonLineOption);
}

// function prepareOptionForEchartsBarLine(dataArray){
//
// }