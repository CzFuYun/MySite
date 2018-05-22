//
//
// function convertDailyDepositAmountsToCsv(data){
//     /* data: [["2017-11-10", "对公活期存款", 335] ,
//     ["2017-11-10", "对公通知存款", 27553],
//     ["2017-11-20", "对公定期存款", 10274], ...]
//     mid_status: {label1: {date1: xxxx.xx, date2: xxxx.xx},
//                  label2: {date1: xxxx.xx, date2: xxxx.xx}}
//     return: stringCsv*/
//     let dict = {},
//         dateList = [],
//         labelList = [],
//         csv = 'Date';
//     for(let i=0; i<data.length; i++){
//         let date = data[i][0],
//             label = data[i][1],
//             amount = data[i][2];
//         if(!dict[label]){
//             csv += (',' + label);
//             labelList.push(label);
//             dict[label] = {};
//         }
//         dict[label][date] = amount;
//         if($.inArray(date, dateList) < 0){
//             dateList.push(date);
//         }
//     }
//     csv += '\n';
//     for(let i=0; i<dateList.length; i++){
//         csv += dateList[i];
//         for(let j=0; j<labelList.length; j++){
//             let temp = dict[labelList[j]][dateList[i]];
//             csv += ',';
//             if(temp){
//                 csv += temp;
//             }
//             else{
//                 csv += 0;
//             }
//         }
//         csv += '\n';
//     }
//     return csv;
// }
//

