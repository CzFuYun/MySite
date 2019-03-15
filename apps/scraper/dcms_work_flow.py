# from html.parser import HTMLParser
import html

from scraper.dcms_request import DcmsHttpRequest, RegExp
from private_modules.dcms_shovel.page_parser import DcmsWebPage



class DcmsWorkFlow:
    def __init__(self, *args, dcms=None, **kwargs):
        if dcms is None:
            self.dcms = DcmsHttpRequest()
            self.dcms.login()
        else:
            self.dcms = dcms


class LuWorkFlow(DcmsWorkFlow):
    def __init__(self, lu_num, *args, dcms=None, rlk=None, **kwargs):
        super().__init__(self, *args, dcms=dcms, **kwargs)
        dcms_type = self.dcms.DcmsType.cp.value
        if lu_num.startswith('SMELU'):
            dcms_type = self.dcms.DcmsType.sme.value
        elif lu_num.startswith('CSLU'):
            dcms_type = self.dcms.DcmsType.cs.value
        self.dcms.setDcmsType(dcms_type)
        self.rlk = rlk or self.dcms.search_lu(lu_num)
        self.lu_num = lu_num

    def apply_info(self):
        '''
        放款流程“申请信息”标签页
        :return:
        '''
        url_path = self.dcms.UrlPath(
            self.dcms.dcms_type + 'dcma/limit_utilization/application/application.view',
            {'do': 'LoadSummary', 'resultLinkKey': self.rlk}
        )
        r = self.dcms.get(url_path)
        return DcmsWebPage(r.text)


class CpWorkFlow(DcmsWorkFlow):
    def __init__(self, cp_num, *args, dcms=None, rlk=None, **kwargs):
        super().__init__(self, *args, dcms=dcms, **kwargs)
        dcms_type = self.dcms.DcmsType.cp.value
        if cp_num.startswith('SME'):
            dcms_type = self.dcms.DcmsType.sme.value
        elif cp_num.startswith('CS'):
            dcms_type = self.dcms.DcmsType.cs.value
        self.dcms.setDcmsType(dcms_type)
        self.rlk = rlk or self.dcms.search_cp(cp_num)
        self.cp_num = cp_num

    def apply_info(self):
        pass

    def document_generation(self):
        '''
        授信流程中文件生成标签
        :return:
        '''
        # url_path = self.dcms.UrlPath(
        #     self.dcms.dcms_type + 'dcms/corporate/application/document_generation.view',
        #     {'do': 'List', 'taskId': 'false', 'resultLinkKey': self.rlk, 'applicationId': self.rlk}
        # )
        url_path = self.dcms.UrlPath(
            self.dcms.dcms_type + 'dcms/corporate/application/document_generation.view',
            {'do': 'List', 'taskId': 'false', 'resultLinkKey': self.rlk, 'applicationId': self.rlk}
        )
        r = self.dcms.get(url_path)
        return DcmsWebPage(r.text)

    def getReply(self):
        doc_gen = self.document_generation()
        doc_list = doc_gen.list_areas()['文件保存列表']
        for doc in doc_list:
            if '批复' in doc['文件名称'].inner_text:
                reply_rlk = RegExp.rlk.search(str(doc['文件名称'].outer_html)).groups()[0]
                url_path = self.dcms.UrlPath(
                    self.dcms.dcms_type + 'dcms/corporate/application/document_generation.view',
                    {'do': 'SavedDetail', 'id': reply_rlk, 'requestAction': 'save'}
                )
                r = self.dcms.get(url_path)
                content = DcmsWebPage(html.unescape(html.unescape(r.text))).HTML_soup.find('textarea').text.split('审批意见：')[1].strip()
                code = RegExp.reply_code.search(r.text).group()
                return code, content
