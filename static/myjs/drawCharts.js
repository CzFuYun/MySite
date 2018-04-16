COLOR_NONE = 'rgba(255, 255, 255, 0)';
COLOR_LIGHT = ['#FF6666', '#FF9966', '#FFFF99', '#CCFF99', '#CCFFFF', '#99CCCC', '#FFCCCC'];
COLOR_HAPPY = [
    'rgba(73,150,255,1)',
    'rgba(156,255,42,1)',
    'rgba(255,78,68,1)',
    'rgba(158,57,255,1)',
    'rgba(54,255,128,1)',
    'rgba(255,198,51,1)',
    'rgba(255,59,196,1)',
    'rgba(68,255,239,1)',
    'rgba(238,255,49,1)',
    'rgba(255,41,111,1)',
    'rgba(123,67,255,1)',
    'rgba(57,255,51,1)',
    'rgba(255,126,47,1)',
    'rgba(228,56,255,1)'
];
COLOR_HAPPY_HO = [
    'rgba(73,150,255,0.5)',
    'rgba(156,255,42,0.5)',
    'rgba(255,78,68,0.5)',
    'rgba(158,57,255,0.5)',
    'rgba(54,255,128,0.5)',
    'rgba(255,198,51,0.5)',
    'rgba(255,59,196,0.5)',
    'rgba(68,255,239,0.5)',
    'rgba(238,255,49,0.5)',
    'rgba(255,41,111,0.5)',
    'rgba(123,67,255,0.5)',
    'rgba(57,255,51,0.5)',
    'rgba(255,126,47,0.5)',
    'rgba(228,56,255,0.5)'
];
LINE_BAR_DEFAULT_OPTIONS = {

    //Boolean - If we show the scale above the chart data
    scaleOverlay : false,

    //Boolean - If we want to override with a hard coded scale
    scaleOverride : false,

    //** Required if scaleOverride is true **
    //Number - The number of steps in a hard coded scale
    scaleSteps : null,
    //Number - The value jump in the hard coded scale
    scaleStepWidth : null,
    //Number - The scale starting value
    scaleStartValue : null,

    //String - Colour of the scale line
    scaleLineColor : "rgba(0,0,0,.1)",

    //Number - Pixel width of the scale line
    scaleLineWidth : 1,

    //Boolean - Whether to show labels on the scale
    scaleShowLabels : true,

    //Interpolated JS string - can access value
    scaleLabel : "<%=value%>",

    //String - Scale label font declaration for the scale label
    scaleFontFamily : "'Arial'",

    //Number - Scale label font size in pixels
    scaleFontSize : 12,

    //String - Scale label font weight style
    scaleFontStyle : "normal",

    //String - Scale label font colour
    scaleFontColor : "#666",

    ///Boolean - Whether grid lines are shown across the chart
    scaleShowGridLines : true,

    //String - Colour of the grid lines
    scaleGridLineColor : "rgba(0,0,0,.05)",

    //Number - Width of the grid lines
    scaleGridLineWidth : 1,

    //Boolean - Whether the line is curved between points
    bezierCurve : true,

    //Boolean - Whether to show a dot for each point
    pointDot : true,

    //Number - Radius of each point dot in pixels
    pointDotRadius : 3,

    //Number - Pixel width of point dot stroke
    pointDotStrokeWidth : 1,

    //Boolean - Whether to show a stroke for datasets
    datasetStroke : true,

    //Number - Pixel width of dataset stroke
    datasetStrokeWidth : 2,

    //Boolean - Whether to fill the dataset with a colour
    datasetFill : true,

    //Boolean - Whether to animate the chart
    animation : true,

    //Number - Number of animation steps
    animationSteps : 60,

    //String - Animation easing effect
    animationEasing : "easeOutQuart",

    //Function - Fires when the animation is complete
    onAnimationComplete : null

};
RADAR_DEFAULT_OPTIONS = {

    //Boolean - If we show the scale above the chart data
    scaleOverlay : false,

    //Boolean - If we want to override with a hard coded scale
    scaleOverride : false,

    //** Required if scaleOverride is true **
    //Number - The number of steps in a hard coded scale
    scaleSteps : null,
    //Number - The value jump in the hard coded scale
    scaleStepWidth : null,
    //Number - The centre starting value
    scaleStartValue : null,

    //Boolean - Whether to show lines for each scale point
    scaleShowLine : true,

    //String - Colour of the scale line
    scaleLineColor : "rgba(0,0,0,.1)",

    //Number - Pixel width of the scale line
    scaleLineWidth : 1,

    //Boolean - Whether to show labels on the scale
    scaleShowLabels : false,

    //Interpolated JS string - can access value
    scaleLabel : "<%=value%>",

    //String - Scale label font declaration for the scale label
    scaleFontFamily : "'Arial'",

    //Number - Scale label font size in pixels
    scaleFontSize : 12,

    //String - Scale label font weight style
    scaleFontStyle : "normal",

    //String - Scale label font colour
    scaleFontColor : "#666",

    //Boolean - Show a backdrop to the scale label
    scaleShowLabelBackdrop : true,

    //String - The colour of the label backdrop
    scaleBackdropColor : "rgba(255,255,255,0.75)",

    //Number - The backdrop padding above & below the label in pixels
    scaleBackdropPaddingY : 2,

    //Number - The backdrop padding to the side of the label in pixels
    scaleBackdropPaddingX : 2,

    //Boolean - Whether we show the angle lines out of the radar
    angleShowLineOut : true,

    //String - Colour of the angle line
    angleLineColor : "rgba(0,0,0,.1)",

    //Number - Pixel width of the angle line
    angleLineWidth : 1,

    //String - Point label font declaration
    pointLabelFontFamily : "'Arial'",

    //String - Point label font weight
    pointLabelFontStyle : "normal",

    //Number - Point label font size in pixels
    pointLabelFontSize : 12,

    //String - Point label font colour
    pointLabelFontColor : "#666",

    //Boolean - Whether to show a dot for each point
    pointDot : true,

    //Number - Radius of each point dot in pixels
    pointDotRadius : 3,

    //Number - Pixel width of point dot stroke
    pointDotStrokeWidth : 1,

    //Boolean - Whether to show a stroke for datasets
    datasetStroke : true,

    //Number - Pixel width of dataset stroke
    datasetStrokeWidth : 2,

    //Boolean - Whether to fill the dataset with a colour
    datasetFill : true,

    //Boolean - Whether to animate the chart
    animation : true,

    //Number - Number of animation steps
    animationSteps : 60,

    //String - Animation easing effect
    animationEasing : "easeOutQuart",

    //Function - Fires when the animation is complete
    onAnimationComplete : null

};
PIE_DEFAULT_OPTIONS = {
    //Boolean - Whether we should show a stroke on each segment
    segmentShowStroke : true,

    //String - The colour of each segment stroke
    segmentStrokeColor : "#fff",

    //Number - The width of each segment stroke
    segmentStrokeWidth : 2,

    //Boolean - Whether we should animate the chart
    animation : true,

    //Number - Amount of animation steps
    animationSteps : 100,

    //String - Animation easing effect
    animationEasing : "easeOutBounce",

    //Boolean - Whether we animate the rotation of the Pie
    animateRotate : true,

    //Boolean - Whether we animate scaling the Pie from the centre
    animateScale : false,

    //Function - Will fire on animation completion.
    onAnimationComplete : null
};
DOUGHTNUT_DEFAULT_OPTIONS = {
    //Boolean - Whether we should show a stroke on each segment
    segmentShowStroke : true,

    //String - The colour of each segment stroke
    segmentStrokeColor : "#fff",

    //Number - The width of each segment stroke
    segmentStrokeWidth : 2,

    //The percentage of the chart that we cut out of the middle.
    percentageInnerCutout : 50,

    //Boolean - Whether we should animate the chart
    animation : true,

    //Number - Amount of animation steps
    animationSteps : 100,

    //String - Animation easing effect
    animationEasing : "easeOutBounce",

    //Boolean - Whether we animate the rotation of the Doughnut
    animateRotate : true,

    //Boolean - Whether we animate scaling the Doughnut from the centre
    animateScale : false,

    //Function - Will fire on animation completion.
    onAnimationComplete : null
};
POLARAREA_DEFAULT_OPTIONS = {
    //Boolean - Show a backdrop to the scale label
    scaleShowLabelBackdrop : true,

    //String - The colour of the label backdrop
    scaleBackdropColor : "rgba(255,255,255,0.75)",

    // Boolean - Whether the scale should begin at zero
    scaleBeginAtZero : true,

    //Number - The backdrop padding above & below the label in pixels
    scaleBackdropPaddingY : 2,

    //Number - The backdrop padding to the side of the label in pixels
    scaleBackdropPaddingX : 2,

    //Boolean - Show line for each value in the scale
    scaleShowLine : true,

    //Boolean - Stroke a line around each segment in the chart
    segmentShowStroke : true,

    //String - The colour of the stroke on each segement.
    segmentStrokeColor : "#fff",

    //Number - The width of the stroke value in pixels
    segmentStrokeWidth : 2,

    //Number - Amount of animation steps
    animationSteps : 100,

    //String - Animation easing effect.
    animationEasing : "easeOutBounce",

    //Boolean - Whether to animate the rotation of the chart
    animateRotate : true,

    //Boolean - Whether to animate scaling the chart from the centre
    animateScale : false,

    //String - A legend template
    legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<segments.length; i++){%><li><span style=\"background-color:<%=segments[i].fillColor%>\"></span><%if(segments[i].label){%><%=segments[i].label%><%}%></li><%}%></ul>"

};

function clearCanvas(strCanvasId){
    var oldCanvas = document.getElementById(strCanvasId);
    var attr = oldCanvas.attributes;
    // var p = oldCanvas.parentElement;
    var newCanvas = document.createElement('canvas');
    for(var i=0;i<attr.length;i++){
        $(newCanvas).attr(attr[i].name, attr[i].value);
    }
    $(oldCanvas).before(newCanvas);     // 将新的画布添加到老画布之前
    oldCanvas.remove();
    // p.appendChild(newCanvas);
    context = newCanvas.getContext('2d');
    return context;
}

function markLegend(strCanvasId, dataLabelAndValue){
    // 创建图例，需要事先在HTML文档中植入ul标签：<ul class="list-inline m-b-0" id="strCanvasId_legend"></ul>
    var legend = $('#' + strCanvasId + '_legend');
    legend.children().remove();       // 清空现有图例
    var fragment = document.createElement('fragment');
    var n = 0;
    for(var k in dataLabelAndValue.value){
        var li = document.createElement('li');
        var h6 = document.createElement('h6');
        $(h6).attr('style', 'color:' + COLOR_HAPPY[n]);
        n ++;
        h6.innerHTML = '<i class="fa fa-circle font-10 m-r-10"></i>' + k.replace('_', '');
        li.appendChild(h6);
        fragment.appendChild(li);
    }
    legend.append(fragment);
}

function drawLines(strCanvasId, dataLabelAndValue, needLegend){
    // 重复绘图时需要先删除当前canvas，再重新添加一个属性一样的canvas，为保证插入位置与之前一致，canvas最好是其父元素的唯一子元素！！！
    // dataLabelAndValue LIKE {label: string_array, value: {key1: num_array1, key2: num_array2, ...}}，key1,key2会被用作图例的文字说明
    var context = clearCanvas(strCanvasId);
    var l = [];
    var d = [];
    for(var i=0; i<dataLabelAndValue.label.length; i++){
        l.push(dataLabelAndValue.label[i]);
    }
    var n = 0;
    for(var key in dataLabelAndValue.value){
        d.push({
            fillColor: key.indexOf('_') < 0 ? COLOR_HAPPY_HO[n] : COLOR_NONE,     // 填充色
            strokeColor: COLOR_HAPPY[n],       // 曲线颜色
            pointColor: COLOR_HAPPY[n],        // 节点色
            pointStrokeColor: "#fff",          // 节点框线
            data: dataLabelAndValue.value[key]
        });
        n ++;
    }
    var factor = {labels: l, datasets: d};
    new Chart(context).Line(factor, LINE_BAR_DEFAULT_OPTIONS);      // 创建对象，生成图表
    if(needLegend){
        markLegend(strCanvasId, dataLabelAndValue);
    }
}

function drawPie(strCanvasId, dataLabelAndValue, needLegend) {
    // 重复绘图时需要先删除当前canvas，再重新添加一个属性一样的canvas，为保证插入位置与之前一致，canvas最好是其父元素的唯一子元素！！！
    // dataLabelAndValue LIKE {label: string_array, value: {key1: num_array1, key2: num_array2, ...}}，key1,key2会被用作图例的文字说明
    var context = clearCanvas(strCanvasId);
    var d = [];
    for(var i=0; i<dataLabelAndValue.label.length; i++){
        d.push(
            {
                color: COLOR_HAPPY_HO[i],
                label: dataLabelAndValue.label[i],
                value: dataLabelAndValue.value[i]
            }
        )
    }
    new Chart(context).Pie(d, PIE_DEFAULT_OPTIONS);
    if(needLegend){
        markLegend(strCanvasId, dataLabelAndValue);
    }
}

// function drawBars(strCanvasId, strLabels, numValues){
//     // strLabels LIKE ["January","February","March","April","May","June","July"]
//     // numValues LIKE [[65,59,90,81,56,55,40], [28,48,40,19,96,27,100]]
//     var l = [];
//     var d = [];
//     for(i=0;i<strLabels.length;i++){
//         l.push(strLabels[i]);
//     }
//     for(i=0;i<numValues.length;i++){
//         d.push({
//             fillColor: COLOR_HAPPY_HO[i],      // 填充色
//             strokeColor: COLOR_HAPPY[i],       // 线色
//             data: numValues[i]
//         })
//     }
//     var factor = {labels: l, datasets: d};
//     var ctx = document.getElementById(strCanvasId).getContext("2d");
//     /// 创建对象，生成图表
//     new Chart(ctx).Bar(factor, LINE_BAR_DEFAULT_OPTIONS);
// }
// function drawRadar(strCanvasId, strLabels, numValues){
//     // strLabels LIKE ["January","February","March","April","May","June","July"]
//     // numValues LIKE [[65,59,90,81,56,55,40], [28,48,40,19,96,27,100]]
//     var l = [];
//     var d = [];
//     for(i=0;i<strLabels.length;i++){
//         l.push(strLabels[i]);
//     }
//     for(i=0;i<numValues.length;i++){
//         d.push({
//             fillColor: COLOR_HAPPY_HO[i],
//             strokeColor: COLOR_HAPPY[i],
//             pointColor: COLOR_HAPPY[i],
//             pointStrokeColor: "#fff",
//             data: numValues[i]
//         })
//     }
//     var factor = {labels: l, datasets: d};
//     var ctx = document.getElementById(strCanvasId).getContext("2d");
//     new Chart(ctx).Radar(factor, RADAR_DEFAULT_OPTIONS);
// }
// function drawPie(strCanvasId, strLabels, numValues){
//     // strLabels LIKE ["January","February","March","April","May","June","July"]
//     // numValues LIKE [65,59,90,81,56,55,40]
//     var d = [];
//     for(i=0;i<numValues.length;i++){
//         d.push({
//             color: COLOR_HAPPY_HO[i],
//             value: numValues[i],
//             label: strLabels[i]
//         })
//     }
//     var ctx = document.getElementById(strCanvasId).getContext("2d");
//     new Chart(ctx).Pie(d, PIE_DEFAULT_OPTIONS);
// }
// function drawDoughnut(strCanvasId, strLabels, numValues){
//     // strLabels LIKE ["January","February","March","April","May","June","July"]
//     // numValues LIKE [65,59,90,81,56,55,40]
//     var d = [];
//     for(i=0;i<numValues.length;i++){
//         d.push({
//             color: COLOR_HAPPY_HO[i],
//             value: numValues[i],
//             label: strLabels[i]
//         })
//     }
//     var ctx = document.getElementById(strCanvasId).getContext("2d");
//     new Chart(ctx).Pie(d, DOUGHTNUT_DEFAULT_OPTIONS);
// }
// function drawPolarArea(strCanvasId, strLabels, numValues){
//     // strLabels LIKE ["January","February","March","April","May","June","July"]
//     // numValues LIKE [65,59,90,81,56,55,40]
//     var d = [];
//     for(i=0;i<numValues.length;i++){
//         d.push({
//             color: COLOR_HAPPY_HO[i],
//             value: numValues[i],
//             label: strLabels[i]
//         })
//     }
//     var ctx = document.getElementById(strCanvasId).getContext("2d");
//     new Chart(ctx).PolarArea(d, POLARAREA_DEFAULT_OPTIONS);
// }
//drawPolarArea('myChart', ["January","February","March","April","May","June","July","August","September","October","November","December"], [28,48,40,19,96,27,100,55,31,78,33,60]);