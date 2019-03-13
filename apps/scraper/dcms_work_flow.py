from scraper.dcms_request import DcmsHttpRequest
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
    pass