from application.application import Application

if __name__ == '__main__':

    application = Application(account_id=1143535072)

    application.get_info_by_match_id(match_id='6849009127')
