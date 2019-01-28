import re, sys, threading, urllib
from collections import namedtuple

import requests, bs4

from .base_request import BaseHttpRequest
from apps.deposit_and_credit.models_operation import DateOperation
from dcms_shovel.page_parser import DcmsWebPage


class CrpHttpRequest(BaseHttpRequest):
    origin_url = 'http://102.104.254.14/crp/'
    Column = namedtuple('Column', ['db_field', 'type'])
    qidai_fields = {
        '报表数据日期': Column('DT_COMMIT', '4'),
        '分行名称（一级）': Column('BR_NM2', '2'),
        '分行名称（二级）': Column('BR_NM', '2'),
        '经办行': Column('JBBR_NM', '2'),
        '客户编号': Column('NO', '9'),
        '客户名称': Column('NM', '9'),
        '公司性质/公司类型': Column('MT_CONSTITUTION_NAME', '2'),
        '企业出资人经济成分': Column('MT_CIF_CAT_NAME', '2'),
        '控股股东': Column('DSCP_MUGS', '9'),
        '控股股东控股比例(百分比)': Column('EQUITY', '9'),
        '地址': Column('GRP_ADDR', '9'),
        '是否我行预警客户': Column('IS_EW', '2'),
        '行业门类（客户）': Column('MT_IND_TYP_NAME', '2'),
        '行业大类（客户）': Column('MT_IND_CAT_NAME', '2'),
        '行业中类（客户）': Column('MT_IND_NAME', '2'),
        '行业小类（客户）': Column('MT_IND_DETAIL_NAME', '2'),
        '企业规模': Column('MT_CORP_TYP_NAME', '2'),
        '客户评级（2015版）': Column('RAITING', '2'),
        '授信参考编号': Column('AAP_REF_NO', '9'),
        '放款参考编号': Column('LU_REF_NO', '9'),
        '业务种类': Column('MT_FAC_NAME', '2'),
        '是否特别授信业务': Column('IS_LOW_RISK', '2'),
        '是否表外业务': Column('IS_OFF_BAL_SHEET', '2'),
        '帐号': Column('ACCT_NO', '9'),
        '合同号': Column('CONTRACT_NO', '9'),
        '发放日期': Column('DT_FIRST_DISB', '4'),
        '业务到期日': Column('DT_MATURITY', '4'),
        '汇率': Column('EXCHG_RATE', '3'),
        '利率': Column('INT_RATE', '3'),
        '计息频率': Column('INT_CALC_MT_REST_TYP_NAME', '2'),
        '利率调整频率': Column('MT_FRQ_ADJ_TYP_NAME', '2'),
        '利率浮动标识': Column('MT_SIGN_NM', '2'),
        '利率浮动比例': Column('MARGIN', '3'),
        '业务费用类型': Column('MT_FEE_NAME', '2'),
        '费率(百分比)': Column('RATE', '3'),
        '保证人名称': Column('COLL_NM', '9'),
        '保证金帐号': Column('DEPOSIT_ACCT_NO', '9'),
        '保证金比例': Column('DEPOSIT_RATIO', '3'),
        '放款金额(元)': Column('DISB_AMT', '1'),
        '业务余额(原币)': Column('OUTSTD_AMT', '1'),
        '业务币种': Column('MT_CUR_NAME', '2'),
        '担保方式': Column('MT_COLL_CLS_TYP_NAME', '2'),
        '押品一级分类': Column('MT_COLL_TYP_NAME', '2'),
        '押品二级分类': Column('ERJI', '2'),
        '押品三级分类': Column('MT_COLL_NAME', '2'),
        '授信连接担保金额': Column('SPLIT_VALUE', '1'),
        '担保品价值': Column('COLL_VALUE', '1'),
        '账户链接担保金额': Column('ACCT_CHARGE_VALUE', '1'),
        '安全系数': Column('SAFETY_FACTOR', '9'),
        '安全担保金额(元)': Column('SAVE_COLL_VALUE', '1'),
        '账户状态': Column('MT_ACCT_STS_NAME', '2'),
        '五级分类': Column('RATING_NM', '2'),
        '是否展期': Column('IS_EXT', '2'),
        '是否借新还旧': Column('IS_JXHJ', '2'),
        '拨备金额(元)': Column('DV_ACCT_AMT', '1'),
        '建档日期': Column('LU_DT', '4'),
        '额度使用建档金额': Column('LU_LMT', '1'),
        '主办客户经理': Column('MGR_NM', '9'),
        '管户客户经理': Column('SEC_NM', '9'),
        '管户客户经理用户代码': Column('SEC_ID', '2'),
        '客户首笔授信批准时间': Column('CDT_DATE', '4'),
        '集团名称': Column('GRP_NM', '9'),
        '集团客户编号': Column('GRP_NO', '9'),
        '集团母公司名称': Column('CORE_CIF_NM', '9'),
        '集团客户分类': Column('MT_GRP_TYP_NAME', '2'),
        '集团客户控制额度到期日': Column('GRP_DT_MATURITY', '4'),
        '主客户经理（集团）': Column('MAIN_ACCT_MGR_NM', '9'),
        '批复编号': Column('GRP_APPROVAL_LETTER_NO', '9'),
        '批复结论': Column('MT_CMT_RESULT_NAME', '2'),
        '批复时间': Column('DT_APPR', '4'),
        '批复金额(元)(原币）': Column('LMT_APPR', '1'),
        '批复期限': Column('GRP_TENURE_MT_TIME_NAME', '9'),
        '是否集团客户': Column('IS_GRP', '2'),
        '是否减值': Column('IS_DV_ACCT', '2'),
        '业务期限代码': Column('TENURE_MT_TIME_CD', '2'),
        '组织机构代码': Column('ID_NO_3', '9'),
        '业务期限': Column('APPR_TENURE', '3'),
        '展期次数': Column('EXT_NO', '3'),
        '借新还旧次数': Column('JXHJ_NO', '3'),
        '是否银团贷款': Column('IS_BANK_GROUP_LOAN', '2'),
        '客户评级': Column('TMP_RATING_GRADE_CD', '2'),
        '评级有效日期（2015版）': Column('DT_VALID', '4'),
        '罚息浮动标识': Column('SUSPENSE_MT_SIGN_NM', '2'),
        '罚息浮动比例': Column('SUSPENSE_MARGIN', '3'),
        '罚息利率': Column('INT_RATE_IN_SUSPENSE', '3'),
        '客户状态': Column('MT_CIF_STS_NAME', '2'),
        '是否大额预警': Column('IS_EW_LARG', '2'),
        '保证金余额': Column('DEPOSIT_AMT', '1'),
        '主营业务收入': Column('MAIN_BUSI_INCOM', '1'),
        '担保品所有者': Column('COLL_OWNER', '9'),
        '业务余额（担保拆分）': Column('OUTSTD_AMT2', '1'),
        '新核心账号': Column('CB_ACCT_NO', '9'),
        '是否主动营销': Column('IS_ACTV_MKTING', '2'),
        '国家': Column('MT_CTRY_NAME', '2'),
        '省': Column('MT_STATE_NAME', '9'),
        '市': Column('MT_CITY_NAME', '2'),
        '县/区': Column('MT_COUNTY_NAME', '2'),
        '行政区划代码': Column('MT_SECTION_CD', '9'),
        '是否政府投融资平台': Column('IS_GOV_INVEST_CUSTOMER', '2'),
        '平台类型': Column('MT_GOV_INVEST_TYP_NAME', '9'),
        '平台等级': Column('MT_GOV_INVEST_LVL_NAME', '9'),
        '行业门类（投向）': Column('INVEST_MT_IND_TYP_NAME', '2'),
        '行业大类（投向）': Column('INVEST_MT_IND_CAT_NAME', '2'),
        '行业中类（投向）': Column('INVEST_MT_IND_NAME', '2'),
        '行业小类（投向）': Column('INVEST_MT_IND_DETAIL_NAME', '2'),
        '可担保授信金额': Column('SPLIT_VALUE2', '1'),
        '可担保账户金额': Column('ACCT_CHARGE_VALUE2', '1'),
        '期限分类(利率)': Column('MT_RATE_TYP_NAME', '2'),
        '核心业务名称': Column('CB_PROD_NM', '2'),
        'PD值': Column('TMP_RATING_PD_VAL', '3'),
        '互保客户代码': Column('ACE_NO', '9'),
        '互保客户名称': Column('ACE_NM', '9'),
        '互保类型': Column('MT_ACE_TYP_NAME', '2'),
        '支付方式': Column('MT_LOAN_DISB_TYP_NAME', '2'),
        '支付金额（本币）': Column('STZF_DISB_AMT', '1'),
        '当日汇率': Column('EXCHG_RATE', '1'),
        '支付金额（人民币）': Column('STZF_DISB_RMB', '1'),
        '收款人名称': Column('STZF_RECEIVER', '9'),
        '已摊利息': Column('INTEREST', '1'),
        '待摊利息': Column('UNEARNED_INT', '1'),
        '净值': Column('NET_BAL', '1'),
        '上次五级分类': Column('APPR_RATING_DSCP', '2'),
        '系统计算五级分类结果': Column('SYS_RATING_DSCP', '2'),
        '五级分类认定原因': Column('APPR_JUSTIFICATION', '9'),
        '是否逾期（监管口径）': Column('OVER_FLAG', '2'),
        '欠本日期（监管口径）': Column('DEB_BAL_DATE', '4'),
        '欠息日期（监管口径）': Column('DEB_TXN_DATE', '4'),
        '逾期本金（监管口径）': Column('UNPD_PRIN_BAL', '1'),
        '逾期期限（监管口径）': Column('OVER_CAT', '9'),
        '是否欠息（监管口径）': Column('DEBT_FLAG', '2'),
        '表内欠息（监管口径）': Column('INNER_TXN', '1'),
        '表外欠息（监管口径）': Column('OUTER_TXN', '1'),
        '计提累计欠息（监管口径）': Column('TOTAL_TXN', '1'),
        '汇率（业务日期）': Column('CUR_RATE', '1'),
        '单户业务余额总额': Column('AMT_CIF', '1'),
        '分行所属省份': Column('BR_MT_STATE_NAME', '2'),
        '统计指标（业务）': Column('ACCT_INDEX', '9'),
        '统计指标（客户）': Column('CIF_INDEX', '9'),
        '是否互保客户': Column('IS_ACE', '2'),
        '互保客户母公司名称': Column('ACE_CORE_CIF_NM', '9'),
        '是否关联方': Column('IS_BANK_RELATED', '2'),
        '原发放日期（借新还旧）': Column('DT_FIRST_DISB_0', '4'),
        '原到期日（借新还旧）': Column('DT_MATURITY_0', '4'),
        '原账号（借新还旧）': Column('ACCT_NO_OLD', '9'),
        '担保币种': Column('COLL_MT_CUR_NAME', '2'),
        '债项评级（2015版）': Column('CREDIT_RATING', '9'),
        '评级日期': Column('DT_RATING', '4'),
        '客户评级类型': Column('TMP_RATING_TYP_DSCP', '9'),
        '最近一期五级分类时间': Column('DT_APPROVED', '4'),
        '信贷计提金额': Column('TAKE_AMT', '1'),
        '环境和社会风险敏感度分类': Column('MT_SOC_ENV_RISK_TYP_CD', '2'),
        '环境和社会表现评价分档': Column('MT_SOC_ENV_PFM_EVAL_TYP_CD', '2'),
        '战略新兴产业产品': Column('ZHANLV_DSCP', '2'),
        '战略新兴产业分类-小类': Column('HYXL', '2'),
        '战略新兴产业分类-中类': Column('HYZL', '2'),
        '战略新兴产业分类-大类': Column('HYDL', '2'),
        '工业转型升级': Column('GONGYE_DSCP', '2'),
        '是否停息': Column('FIL01', '2'),
        '从业人数': Column('CYRS', '2'),
        '资产总额': Column('ZCZE', '1'),
        '负债总额': Column('FZZE', '1'),
        '财务报表日期': Column('CWBB_DT', '4'),
        '平台客户属性': Column('PTKHSX', '2'),
        '还款类型': Column('HKLX', '2'),
        '分期还款方式': Column('FQHKFS', '2'),
        '对应基准利率': Column('DYJZLL', '9'),
        '检查类型': Column('RV_MT_APP_TYP_NM', '2'),
        '检查日期': Column('DT_REVIEW', '4'),
        '检查状态': Column('APP_STS_CD', '2'),
        '是否自动生成': Column('IS_DOWNLOAD', '2'),
        '角色': Column('ROLE_DEF_NAME', '2'),
        '经办人': Column('USER_NAME', '2'),
        '节能减排项目及服务大类': Column('MT_ENG_SER_CAT_NAME', '2'),
        '节能减排项目及服务小类': Column('MT_ENG_SER_DETAIL_NAME', '2'),
        '上月末企业规模': Column('MT_CORP_TYP_NAME_SY', '2'),
        '年初企业规模': Column('MT_CORP_TYP_NAME_NC', '2'),
        '业务期限（天）': Column('YWQX_T', '2'),
        '业务期限（短期、中长期）': Column('YWQX2', '2'),
        '是否同城客户': Column('IS_TC', '2'),
        '逾欠日期': Column('YQRQ', '4'),
        '逾欠天数': Column('YQTS', '3'),
        '上年末五级分类': Column('last_rating2', '2'),
        '是否中小部业务': Column('IS_ZX', '2'),
        '会计科目名称（一级）': Column('KJKM_NM', '2'),
        '首次下调不良日期': Column('SCXTBLRQ', '4'),
        '首次下调不良结果': Column('SCXTBLJG', '2'),
        '放款交易编号': Column('trxn_id', '9'),
        '国际业务编号': Column('oth_intl_biz_no', '9'),
        '账号风险暴露类型二级分类': Column('MT_RISK_EXP_REL_DSCP', '2'),
        '是否小微零售客户': Column('IS_IRB_RATAIL', '2'),
        '是否小企业客户': Column('CUST_APP_TYP_CD', '2'),
        '核心产品名称': Column('CB_CPMC', '3'),
        '核心客户号': Column('CB_CUSTOMER_NO', '9'),
        '信用证付款期限（天）': Column('XYZ_FKQX', '2'),
        '押品编号': Column('GUAR_NO', '9'),
        '是否外部风险预警客户': Column('IS_CIF_RISK', '2'),
        '实地检查频率': Column('MT_SIRV_FRQ_TERM_DESC', '2'),
        '支用检查关闭日期': Column('DT_CLOSED_ZYJC', '4'),
        '实地检查关闭日期': Column('DT_CLOSED_SDJC', '4'),
        '到期前检查关闭日期': Column('DT_CLOSED_DQJC', '4'),
        '预警建档时间': Column('DT_CREATED_YJ', '4'),
        '注册地所在国家': Column('ZCDSZGJ', '2'),
        '企业规模对应销售额': Column('QYXSE', '2'),
        '企业规模对应资产总额(万元)': Column('QYZCZE', '2'),
        '客户经理所属机构': Column('KHJLSSJG', '2'),
        '是否有客户经理(监控)角色': Column('KHJLJKJS', '2'),
        '是否有效用户': Column('SFYXYH', '2'),
        '总账汇率': Column('ZZHL', '2'),
    }
    leishou_fields = {
        '报表数据日期': Column('DT_COMMIT', '4'),
        '分行名称': Column('BR_NM', '2'),
        '经办行': Column('JBBR_NM', '2'),
        '客户编号': Column('CIF_NO', '9'),
        '客户名称': Column('CIF_NM', '9'),
        '行业门类（客户）': Column('MT_IND_TYP_NAME', '2'),
        '行业大类（客户）': Column('MT_IND_CAT_NAME', '2'),
        '行业中类（客户）': Column('MT_IND_NAME', '2'),
        '行业小类（客户）': Column('MT_IND_DETAIL_NAME', '2'),
        '企业规模': Column('MT_CORP_TYP_NAME', '2'),
        '信用等级评定': Column('RATING', '2'),
        '业务种类': Column('MT_FAC_NAME', '2'),
        '是否特别授信业务': Column('IS_LOW_RISK', '2'),
        '是否表外业务': Column('IS_BWAI', '2'),
        '帐号': Column('ACCT_NO', '9'),
        '合同号': Column('CONTRACT_NO', '9'),
        '收回日期': Column('CREDIT_DT_UPDATED', '4'),
        '收回金额(元)': Column('CREDIT', '1'),
        '汇率': Column('EXCHG_RATE', '9'),
        '利率': Column('INT_RATE', '9'),
        '计息频率': Column('MT_REST_TYP_NAME', '2'),
        '业务币种': Column('MT_CUR_NAME', '2'),
        '账户状态': Column('MT_ACCT_STS_NAME', '2'),
        '五级分类': Column('MT_RISK_RATING_TYP_NAME', '2'),
        '行业门类（投向）': Column('INVEST_MT_IND_TYP_NAME', '2'),
        '行业大类（投向）': Column('INVEST_MT_IND_CAT_NAME', '2'),
        '行业中类（投向）': Column('INVEST_MT_IND_NAME', '2'),
        '行业小类（投向）': Column('INVEST_MT_IND_DETAIL_NAME', '2'),
        '发放日期': Column('DT_FIRST_DISB', '4'),
    }

    @staticmethod
    def encode(string):
        return BaseHttpRequest.encode(string).replace('%', '%25')

    def __init__(self):
        super().__init__()
        self.imp_date = DateOperation()
        self.setDataDate()

    def login(self, user_name='czjw'):
        login_params = 'isLogin=EnterFromLogin&task=login&step=login&tran=login'
        self.user_name = user_name
        if user_name == 'czwlh':
            self.connection.get(self.origin_url + 'Login.do?_%24' + login_params + '&logintype=pwd&usrname=czwlh&password=1')
        elif user_name == 'czjw':
            self.connection.get(self.origin_url + 'InnerLogin.do?_$' + login_params + '&name=czjw')

    def setDataDate(self, date_str=None):
        if date_str is None:
            date_str = str(self.imp_date.delta_date(-1))
        self.data_date = date_str

    def getUrlParam(self, fields_dict, strFrom, px, *col_name_cn, task='qry', step='submit', tran='dtcx_list', **filter_condition):
        # ↑以前从未注意到的问题：参数的摆放位置。可选参数要位于*args与**kwargs之间
        '''
        :param fields_dict:
        :param col_name_cn: 企贷表表头的中文列名
        :param filter_condition: 筛选条件，由中文列名及条件字符串组成，例如：'业务余额(原币)': '>0 & <100', '分行名称（一级）': "='CZ'"
        :return:
        '''
        strFilter = ''
        if filter_condition:
            for key, value in filter_condition.items():
                strFilter += ' AND '
                col_name = self.qidai_fields[key].db_field
                condition = value.replace('&', ' OR ' + col_name + ' ').replace('|', ' AND ' + col_name + ' ')
                strFilter += ('(' + col_name + condition)
                strFilter += ')'
        strSelect = ''
        strType = ''
        strMc = ''
        for i in col_name_cn:
            strSelect += (fields_dict[i].db_field + ',')
            strType += (fields_dict[i].type + ',')
            strMc += self.encode(i)
        url_param = {
            'task': task,
            'step': step,
            'tran': tran,
            'strSelect': strSelect[:-1],
            'strFrom': strFrom + self.data_date.replace('-', ''),
            'strWhere': " AND (DT_COMMIT = to_date('" + self.data_date + "','yyyy-mm-dd'))" + strFilter +
                        " AND MT_BR_CD IN (" +
                        "SELECT "
                        "JBBR_CD "
                        "FROM "
                        "TBL_MT_BR_CC "
                        "WHERE "
                        "JBBR_CD=(SELECT MT_BR_CD FROM TBL_SEC_USER WHERE ID='" + self.user_name + "') " +
                        "OR YDBR_CD=(SELECT MT_BR_CD FROM TBL_SEC_USER WHERE ID='" + self.user_name + "') " +
                        "OR BR_CD=(SELECT MT_BR_CD FROM TBL_SEC_USER WHERE ID='" + self.user_name + "') " +
                        "OR CD=(SELECT MT_BR_CD FROM TBL_SEC_USER WHERE ID='" + self.user_name + "')) ",
            'strType': strType[:-1],
            'strMc': strMc,
            'px': px,
            'pageNum': '1'
        }
        # return url_param
        response = self.post('CustZdy.do', **url_param)
        p = DcmsWebPage(response.text)
        max_page = int(p.HTML_soup.find('input', {'id': 'resMaxPages'}).attrs['value'])
        yield p
        for page_num in range(1, max_page):
            url_param['pageNum'] = str(page_num + 1)
            response = self.post('CustZdy.do', **url_param)
            yield DcmsWebPage(response.text)
        raise StopIteration

    def getQiDai(self, *col_name_cn, **filter_condition):
        '''
        爬取企贷表
        '''
        strFrom = 'TBL_CPMX_COLL_'
        px = 'br_nm as c1,no as c2;c1,c2;br_nm,no'
        return self.getUrlParam(self.qidai_fields, strFrom, px, *col_name_cn, **filter_condition)

    def getLeiShou(self, *col_name_cn, **filter_condition):
        strFrom = 'TBL_CPMX_LS_'
        px = 'BR_NM AS C1,ACCT_NO AS C2;C1,C2;BR_NM,ACCT_NO'
        return self.getUrlParam(self.qidai_fields, strFrom, px, *col_name_cn, **filter_condition)