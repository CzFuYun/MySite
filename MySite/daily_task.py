# from MySite import daily_task
from MySite.utilities import makeChoice

# ↓每日执行
def a_takePrPhoto():
    from app_customer_repository.models import ProjectExecution
    ProjectExecution.takePhoto()


# ↓每日执行
def b_scrapeCp():
    from deposit_and_credit.models_operation import DateOperation
    imp_date = DateOperation()
    from scraper.models import CpLedger
    last_scrape = imp_date.last_data_date_str(CpLedger, 'add_date')
    if makeChoice(('是否爬取批复日大于等于', last_scrape, '的地区、小微、个贷授信信息？')):
        reply_date_gte = last_scrape
    else:
        print('批复日大于等于：')
        reply_date_gte = input('>>>')
    CpLedger.createCpFromCrp(reply_date_gte)
    CpLedger.createSmeCpFromCrp(reply_date_gte)
    CpLedger.createCsCpFromCrp(reply_date_gte)
    if makeChoice('是否获取批复内容？'):
        CpLedger.fillReplyContentFromDcms()
    print('success')


# ↓一定要先爬累收，再爬放款台账。每日执行，除月初，月初无法爬取上月的累收数
def c_scrapeLeiShou():
    from scraper.models import DailyLeiShou
    DailyLeiShou.getDailyLeishou()


# ↓每日执行
def d_fillLu():
    from scraper.models import LuLedger
    LuLedger.fillCpSmeDetail()
    LuLedger.fillCsDetail()
    print('success')







def f_updateEp():
    from deposit_and_credit.models import ExpirePrompt
    if makeChoice('是否填充授信参考号？'):
        ExpirePrompt.fillCpNum()
    ExpirePrompt.updateProgress()