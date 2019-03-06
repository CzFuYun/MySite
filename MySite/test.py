



if __name__ == '__main__':
    pass
    from app_customer_repository.models import ProjectExecution
    ProjectExecution.takePhoto()

    from deposit_and_credit.models import ExpirePrompt
    ExpirePrompt.fill_cp_num()
    ExpirePrompt.updateProgress()

    from scraper.models import CpLedger
