

if __name__ == '__main__':
    from deposit_and_credit.models_operation import DateOperation
    imp_date = DateOperation()

    # # ↓每日执行
    # from app_customer_repository.models import ProjectExecution
    # ProjectExecution.takePhoto()

    # from scraper.models import DailyLeiShou
    # last_scrape = imp_date.last_data_date_str(DailyLeiShou, 'add_date')
    # DailyLeiShou.getDailyLeishou('2019-03-06')

    # from scraper.models import CpLedger
    # last_scrape = imp_date.last_data_date_str(CpLedger, 'add_date')
    # print('是否爬取批复日大于等于', last_scrape, '的地区、小微、个贷授信信息？')
    # print('0.否\n1.是')
    # choice = input('>>>')
    # if choice == '1' or choice == '':
    #     CpLedger._bulkCreateCpFromCrp(last_scrape)
    #     CpLedger._bulkCreateSmeCpFromCrp(last_scrape)
    #     CpLedger._bulkCreateCsCpFromCrp(last_scrape)


    # ↓月初执行
    from scraper.models import LuLedger


    # ↓按需执行
    from deposit_and_credit.models import ExpirePrompt
    ExpirePrompt.fill_cp_num()
    ExpirePrompt.updateProgress()