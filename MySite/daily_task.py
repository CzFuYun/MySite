# from MySite import daily_task

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
    print('是否爬取批复日大于等于', last_scrape, '的地区、小微、个贷授信信息？')
    print('0.否\n1.是')
    choice = input('>>>')
    if choice == '1' or choice == '':
        reply_date_gte = last_scrape
    else:
        print('批复日大于等于：')
        reply_date_gte = input('>>>')
    CpLedger._bulkCreateCpFromCrp(reply_date_gte)
    CpLedger._bulkCreateSmeCpFromCrp(reply_date_gte)
    CpLedger._bulkCreateCsCpFromCrp(reply_date_gte)
    print('success')


# ↓每日执行，除月初，月初无法爬取上月的累收数
def c_scrapeLeiShou():
    from deposit_and_credit.models_operation import DateOperation
    from scraper.models import DailyLeiShou
    imp_date = DateOperation()
    last_scrape = imp_date.last_data_date_str(DailyLeiShou, 'add_date')
    DailyLeiShou.getDailyLeishou(last_scrape)


# ↓每日执行
def d_fillLu():
    from scraper.models import LuLedger
    LuLedger.fillCpSmeDetail()
    LuLedger.fillCsDetail()
    print('success')


def e_updateEp():
    from deposit_and_credit.models import ExpirePrompt
    print('是否填充授信参考号？\n0.否\n1.是')
    need_fill_cp_num = input('>>>')
    if need_fill_cp_num == '1' or need_fill_cp_num == '':
        ExpirePrompt.fillCpNum()
    ExpirePrompt.updateProgress()