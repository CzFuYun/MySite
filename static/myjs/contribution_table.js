
CONTRIB_TREE = {};
BASE_RATE = 0.0435;
TS_RULE = {
    originally_value: 2,        // 非汇总行值： 显示原值
    col_accumulation: 1,        // 汇总规则：本列累加
    no_need_sum: 3,             // 汇总规则：不汇总
    keep_originally_value: 4    // 汇总规则：保持原值（仅针对在同一系列企业下的“静态”字段，例如系列名称、部门名称）
};

TABLE_STRUCTURE = {
    department_caption: tableCol('经营部门'   , 0     , TS_RULE.originally_value,TS_RULE.keep_originally_value),
    series_caption:     tableCol('系列'       , 0     , TS_RULE.originally_value,TS_RULE.keep_originally_value),
    cust_name:          tableCol('客户名称'   , '19%' , '<a style="color:white;cursor:pointer" customer_id=<cust_id> onclick="viewCustomerContributionHistory(this)"><cust_name></a>', '<department_caption>—<series_caption>汇总'),
    approve_line:       tableCol('所属条线'   , '6%'  , TS_RULE.originally_value,TS_RULE.no_need_sum),
    net_total:          tableCol('用信净额'   , '6%'  , TS_RULE.originally_value,TS_RULE.col_accumulation, true),
    loan:               tableCol('贷款金额'   , 0     , TS_RULE.originally_value,TS_RULE.col_accumulation),
    loan_interest:      tableCol('贷款利息'   , 0     , TS_RULE.originally_value,TS_RULE.col_accumulation),
    loan_rate:          tableCol('贷款利率'   , '6%'  , '(100*<loan_interest>/<loan>).toFixed(2)','(100*<loan_interest>/<loan>).toFixed(2)', true),
    lr_BAB:             tableCol('全额银票'   , '6%'  , TS_RULE.originally_value,TS_RULE.col_accumulation, true),
    invest_banking:     tableCol('投行项目'   , '6%'  , TS_RULE.originally_value,TS_RULE.col_accumulation, true),
    defuse_expire:      tableCol('化解到期'   , '8%'  , TS_RULE.originally_value,TS_RULE.no_need_sum),
    last_yd_avg:        tableCol('上年日均'   , '6%'  , TS_RULE.originally_value,TS_RULE.col_accumulation, true),
    deposit_amount:     tableCol('存款余额'   , '6%'  , TS_RULE.originally_value,TS_RULE.col_accumulation, true),
    yd_avg:             tableCol('本年日均'   , '6%'  , TS_RULE.originally_value,TS_RULE.col_accumulation, true),
    compare_yd_avg:     tableCol('日均较年初' , '6%'  , [setDepoCompForTd, '<last_yd_avg>', '<yd_avg>'],[setDepoCompForTd, '<last_yd_avg>', '<yd_avg>'], true),
    saving_yd_avg:      tableCol('派生储蓄'   , '6%'  , TS_RULE.originally_value,TS_RULE.col_accumulation, true),
    contrib_ratio:      tableCol('回报率'     , '8%'  , [setContribRatioForTd, '<loan_interest>', '<loan>', 'BASE_RATE', '<yd_avg>+<saving_yd_avg>', '<net_total>+0.333*<invest_banking>'],[setContribRatioForTd, '<loan_interest>', '<loan>', 'BASE_RATE', '<yd_avg>+<saving_yd_avg>', '<net_total>+0.333*<invest_banking>'], true)
};

function tableCol(description, col_width, solid_value, value_for_sum_td, shown_in_dept_sum){
    return {
        description: description,
        col_width: col_width,
        solid_value: solid_value,
        value_for_sum_td: value_for_sum_td,
        shown_in_dept_sum: shown_in_dept_sum
    }
}

function formatString(string, obj){
    let r = /<(\w+)>/g;
    let m = r.exec(string);
    let s = string;
    while (m){
        s = s.replace(m[0], obj[m[1]]);
        m = r.exec(string);
    }
    return s;
}

function calculate(formulaString, obj){
    try{
        return eval(formulaString);
    }catch (e){
        let s = formatString(formulaString, obj);
        let ret;
        try{
            ret = eval(s);
        }catch (e) {
            ret = s;
        }
        return ret;
    }
}

function batchCalculate(formulaStrings, obj){
    // Convert formular array To value array
    // formulaStrings   ['<last_yd_avg>', '<yd_avg>']
    let ret = [];
    for(let i=0; i<formulaStrings.length; i++){
        ret.push(calculate(formulaStrings[i], obj));
    }
    return ret;
}

function buildSeriesCard(series_code, series_customer_list, dept_div, filter_condict){
    // series_code:金峰
    // series_customer_list:[0000000008727622:{k1:v1,k2:v2,...}, 0000000010982506:{k1:v1,k2:v2,...}]
    let series_has_content = false,
        series_sum = {},
        series_name, series_card, series_table, series_tbody;
    for(let i=0; i<series_customer_list.length; i++){
        let cust = series_customer_list[i];
        let cust_detail = {},
            cust_temp_info = getValues(cust)[0];
        cust_detail.cust_id = Object.keys(cust)[0];
        for(let key in cust_temp_info){
            cust_detail[key] = cust_temp_info[key];
        }
        if(!filter_condict['gov'] && cust_detail.gov_plat_lev > 2)      // 如果不要平台，而这个企业又恰好是平台
            continue;
        if(!filter_condict['no_gov'] && cust_detail.gov_plat_lev <= 2)
            continue;
        if(!filter_condict['sme'] && (cust_detail.approve_line === '小微'))
            continue;
        if(!filter_condict['cp'] && cust_detail.approve_line === '地区')
            continue;
        if(!filter_condict['include_no_credit'] && cust_detail.net_total === 0)
            continue;
        if(!filter_condict['include_defuse'] && cust_detail.defuse_expire)     // 如果不计化解户，则将该户的用信剔除
            cust_detail.net_total = 0;
        // console.log(cust_detail);
        if(!series_has_content){
            series_name = getValues(series_customer_list[0])[0]['series_caption'];
            series_card = document.createElement('div');
            series_card.className = 'card-body';
            series_card.innerHTML = '<h2 style="cursor:pointer" onclick="viewSeriesContribution(this)" series_code="' + series_code + '">' + series_name + '</h2>';
            series_table = document.createElement('table');
            series_table.className = 'table full-color-table full-dark-table table-sm table-hover table-bordered';
            let series_thead = '<thead><tr>';
            for(let col in TABLE_STRUCTURE){
                series_sum[col] = TABLE_STRUCTURE[col].value_for_sum_td ? 0 : '';
                let col_width = TABLE_STRUCTURE[col].col_width;
                if(col_width)
                    series_thead += '<th width="' + col_width + '"><div>' + TABLE_STRUCTURE[col].description + '</div></th>';
            }
            series_thead += '</tr></thead>';
            series_table.innerHTML = series_thead;
            series_tbody = document.createElement('tbody');
            series_table.appendChild(series_tbody);
            series_has_content = true;
        }
        let customer_detail_tr = document.createElement('tr');
        let tvalue;
        for(let col in TABLE_STRUCTURE){
            let td_operation = TABLE_STRUCTURE[col].solid_value;
            switch (td_operation){
                case null:
                    break;
                case TS_RULE.originally_value:
                    tvalue = cust_detail[col];
                    break;
                default:
                    let td_operation_type = typeof td_operation;
                    switch (td_operation_type) {
                        case 'string':
                            tvalue = calculate(td_operation, cust_detail);
                            break;
                        case 'object':      // Array也是object。。。
                            let func = td_operation[0];
                            let func_params = td_operation.slice(1, td_operation.length);
                            tvalue = func.apply(func, batchCalculate(func_params, cust_detail));
                            break;
                    }
            }
            if(TABLE_STRUCTURE[col].col_width){
                let td = document.createElement('td');
                td.innerHTML = tvalue;
                customer_detail_tr.appendChild(td);
            }else{      // 若为辅助列（即列宽为0）
                cust_detail[col] = tvalue;
            }
            // ↓将上述计算结果计入本系列的汇总数
            let series_sum_operation = TABLE_STRUCTURE[col].value_for_sum_td;
            switch (series_sum_operation){
                case null:
                    break;
                case TS_RULE.keep_originally_value:
                    tvalue = cust_detail[col];
                    series_sum[col] = tvalue;
                    break;
                case TS_RULE.no_need_sum:
                    break;
                case TS_RULE.col_accumulation:
                    series_sum[col] += tvalue;
                    break;
                default:
                    series_sum_operation_type = typeof series_sum_operation;
                    switch (series_sum_operation_type){
                        case 'string':
                            series_sum[col] = calculate(series_sum_operation, series_sum);
                            break;
                        // case 'object':
                        //     let func = series_sum_operation[0],
                        //         func_params = series_sum_operation.slice(1, series_sum_operation.length);
                        //     series_sum[col] = func.apply(func, batchCalculate(func_params, series_sum));
                        //     break;
                    }
                    break;
            }
        }
        series_tbody.appendChild(customer_detail_tr);
    }
    // ↓构建系列汇总行
    if(!series_has_content)
        return null;
    let series_tfoot = document.createElement('thead');
    let series_sum_tr = document.createElement('tr');
    for(let col in TABLE_STRUCTURE){
        if(!TABLE_STRUCTURE[col].col_width)
            continue;
        let th = document.createElement('th');
        let series_sum_operation = TABLE_STRUCTURE[col].value_for_sum_td;
        if(series_sum_operation === TS_RULE.col_accumulation)
            th.innerHTML = series_sum[col];
        else {
            let series_sum_operation_type = typeof series_sum_operation;
            switch (series_sum_operation_type){
                case 'string':
                    th.innerHTML = series_sum[col] || '';
                    break;
                case 'object':
                    let func = series_sum_operation[0],
                        func_params = series_sum_operation.slice(1, series_sum_operation.length);
                    th.innerHTML = func.apply(func, batchCalculate(func_params, series_sum));
            }
        }
        series_sum_tr.appendChild(th)
    }
    series_tfoot.appendChild(series_sum_tr);
    series_table.appendChild(series_tfoot);
    series_card.appendChild(series_table);
    dept_div.appendChild(series_card);
    return series_sum;
}

function getContributionTree(data_date){
    let contrib_tree = {};
    $.ajax(
        {
            url: '/dc/contribution.ajax',       // '{% url "ajaxContribution" %}',
            type: 'POST',
            async: false,
            data: {
                data_date: data_date
            },
            dataType: 'json',
            success: function (data, status, xhr) {
                contrib_tree = data;
            }
        }
    );
    // {#console.log(contrib_tree);#}
    CONTRIB_TREE = contrib_tree;
    return contrib_tree;
}

function buildDeptContribCard(filter_condict, dept_code, depart_contrib, fragment_elem){
    // 单个部门的贡献度卡片
    // filter_condict: {department: "all", gov: "on", data_date: "2018-03-31"}
    // dept_code: 'YYB'
    // depart_contrib: contrib_tree[dept_code]
    // return: {SUM}
    let dept_has_content = false,
        dept_sum = {};
    let dept_card = document.createElement('div');
    dept_card.setAttribute('class', 'card');
    dept_card.setAttribute('dept', dept_code);
    dept_card.id = 'contribution_' + dept_code;
    let series_customer_data = sortDict(depart_contrib['series_customer_data'], false);
    for(let series in series_customer_data){
        let series_sum = buildSeriesCard(series.split('$')[1], series_customer_data[series], dept_card, filter_condict);
        // {#console.log(series_sum);#}
        if(series_sum){
            for(let s in series_sum){
                let sum_operation = TABLE_STRUCTURE[s].value_for_sum_td;
                if(sum_operation === TS_RULE.no_need_sum || sum_operation === TS_RULE.keep_originally_value){
                    continue;
                }
                else if(sum_operation === TS_RULE.col_accumulation){
                    // {#if(!dept_has_content)#}
                    // {#    dept_sum[s] = 0;#}
                    if(dept_sum[s] === undefined)
                        dept_sum[s] = 0;
                    dept_sum[s] += series_sum[s];
                }else{
                    let sum_operation_type = typeof sum_operation;
                    if(sum_operation_type === 'string'){
                        dept_sum[s] = calculate(sum_operation, series_sum)
                    }else if(sum_operation_type === 'object'){
                        // {#let func = TABLE_STRUCTURE[s].value_for_sum_td[0],#}
                        // {#    func_params = TABLE_STRUCTURE[s].value_for_sum_td.slice(1, sum_operation.length);#}
                        // {#dept_sum[s] = func.apply(func, batchCalculate(func_params, series_sum));#}
                    }
                }
            }
            dept_has_content = true;
        }
    }
    if(dept_has_content){
        let dept_name = depart_contrib['department_caption'],
            dept_title = document.createElement('h1');
        dept_title.id = dept_code;
        dept_title.className = 'text-themecolor';
        dept_title.innerText = dept_name;
        dept_title.setAttribute('onclick', 'viewDeptContributionHistory(this)');
        dept_title.setAttribute('dept_code', dept_code);
        dept_title.setAttribute('style', 'cursor:pointer');
        fragment_elem.appendChild(dept_title);
        let dept_sum_table = document.createElement('table'),
            dept_sum_thead = document.createElement('thead'),
            dept_sum_tbody = document.createElement('tbody');
        dept_sum_table.className = 'tablesaw table-striped table tablesaw-columntoggle';
        dept_sum_table.appendChild(dept_sum_thead);
        dept_sum_table.appendChild(dept_sum_tbody);
        for(let col in TABLE_STRUCTURE){
            if(TABLE_STRUCTURE[col].shown_in_dept_sum){
                let th = document.createElement('th');
                th.innerText = TABLE_STRUCTURE[col].description;
                dept_sum_thead.appendChild(th);
                let dept_sum_operation = TABLE_STRUCTURE[col].value_for_sum_td;
                let td = document.createElement('td');
                if(dept_sum_operation === TS_RULE.col_accumulation)
                    td.innerText = dept_sum[col];
                else if(typeof dept_sum_operation === 'string')
                    td.innerText = calculate(dept_sum_operation, dept_sum);
                else if(typeof dept_sum_operation === 'object'){
                    let func = dept_sum_operation[0],
                        func_params = dept_sum_operation.slice(1, dept_sum_operation.length);
                    td.innerHTML = func.apply(func, batchCalculate(func_params, dept_sum));
                }
                dept_sum_tbody.appendChild(td);
            }
        }
        fragment_elem.appendChild(dept_sum_table);
        fragment_elem.appendChild(dept_card);
    }
    return dept_has_content ? dept_sum : null;
}

function setDepoCompForTd(depoBefore, depoAfter){
    let compare = depoBefore
        ? depoAfter  / depoBefore - 1
        : (depoAfter ? 1 : 0);
        compare = Math.max(compare, -1);        // 最多-100%
        compare = (compare * 100).toFixed(2);
        let arrow, color;
        if(compare <= -20){
            arrow = '"fa fa-level-down"';
            color = '"text-danger text-semibold"';
        }else if(compare <= 0){
            arrow = '"fa fa-level-down"';
            color = '"text-warning text-semibold"';
        }else if(compare <= 20){
            arrow = '"fa fa-level-up"';
            color = '"text-success text-semibold"';
        }else{
            arrow = '"fa fa-level-up"';
            color = '"text-info text-semibold"';
        }
        return '<span class=' + color + '><i class=' + arrow + ' aria-hidden="true"></i>' + (depoAfter - depoBefore) + '</span>';
}

function setContribRatioForTd(interest, loan, base_rate, yd_avg, net_total){
    if(net_total === 0)
        return '';
    let depo_ratio = yd_avg / net_total,
        rate_float_ratio = interest / loan / base_rate - 1 || 0,
        combine_contrib_ratio = rate_float_ratio + depo_ratio,
        display_depo_ratio = (depo_ratio * 100).toFixed(2),
        display_combine_contrib_ratio = (combine_contrib_ratio * 100).toFixed(2),
        pro_bar_color;
    if(depo_ratio < 0.15 )
        pro_bar_color = 'progress-bar bg-danger active progress-bar-striped';
    else if(depo_ratio < 0.30)
        pro_bar_color = 'progress-bar bg-warning active progress-bar-striped';
    else if(depo_ratio < 0.45)
        pro_bar_color = 'progress-bar bg-success active progress-bar-striped';
    else if(depo_ratio < 0.60)
        pro_bar_color = 'progress-bar bg-info active progress-bar-striped';
    else
        pro_bar_color = 'progress-bar bg-primary active progress-bar-striped';
    return '<div class="progress progress-xs margin-vertical-10 "><div style="position: absolute"><h5 style="color: black; line-height: 20px;">' +
        display_depo_ratio + '%</h5></div><div class="' +
        pro_bar_color + '" style="width:' + display_combine_contrib_ratio +
        '%; height:20px;"></div></div>'
}

function buildContribTable(filter_condict, ordered_dept){
    let whole_contrib_tree = getContributionTree(filter_condict['data_date']),
        frag = document.createDocumentFragment(),
        dept_selector,
        depts_sum = {},
        branch_sum = {},
        req_dept = filter_condict['department'];
    $('#right_sidebar_body').append(dept_selector);
    for(let od in ordered_dept){
        let dept_code = ordered_dept[od],
            dept_sum = buildDeptContribCard(filter_condict, dept_code, whole_contrib_tree[ordered_dept[od]], frag);
        if(!dept_sum)
            continue;
        // {#console.log(dept_sum);#}
        // {# 添加部门选择器中的标签 #}
        // let dept_button = document.createElement('a');
        // dept_button.className = 'btn btn-rounded btn-block btn-outline-info';
        // dept_button.setAttribute('href', '#' + dept_code);
        // dept_button.innerText = dept_sum.cust_name.split('—')[0];
        // dept_selector.appendChild(dept_button);
        // {# end添加部门选择器中的标签 #}
        depts_sum[dept_code] = dept_sum;
        for(let col in dept_sum){
            let sum_operation = TABLE_STRUCTURE[col].value_for_sum_td;
            if(sum_operation === TS_RULE.no_need_sum)
                continue;
            if(sum_operation === TS_RULE.col_accumulation){
                if(!branch_sum[col])
                    branch_sum[col] = 0;
                branch_sum[col] += dept_sum[col];
            }else{
                // {#let sum_operation_type = typeof sum_operation;#}
                // {#switch (sum_operation_type){#}
                // {#    case 'string':#}
                // {#        branch_sum[col] = calculate(sum_operation, branch_sum);#}
                // {#        break;#}
                //}
            }
        }
    }
    document.getElementById('main_content').appendChild(frag);
    // {# 生成分行汇总数 #}
    let branch_sum_ul = document.getElementsByClassName('navbar-nav mr-auto mt-md-0')[0];
    for(let col in TABLE_STRUCTURE){
        if(col === 'cust_name')
            continue;
        let sum_operation = TABLE_STRUCTURE[col].value_for_sum_td,
            li = document.createElement('li');
        // {#li.className = 'nav-item';#}
        li.setAttribute('style', 'width:100px');
        li.innerText = TABLE_STRUCTURE[col].description + '\n';
        if(sum_operation === TS_RULE.col_accumulation && branch_sum[col] && TABLE_STRUCTURE[col].shown_in_dept_sum){
            li.innerText += branch_sum[col];
            branch_sum_ul.appendChild(li);
        }else{
            let sum_operation_type = typeof sum_operation;
            switch (sum_operation_type){
                case 'string':
                    li.innerText += calculate(sum_operation, branch_sum);
                    branch_sum_ul.appendChild(li);
                    break;
                case 'object':
                    let func = sum_operation[0];
                    let func_params = sum_operation.slice(1, sum_operation.length);
                    li.innerHTML += func.apply(func, batchCalculate(func_params, branch_sum));
                    branch_sum_ul.appendChild(li);
                    break;
            }
        }
    }
}

