import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pandas as pd

scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

keys_file = r'./keys/lunchboxtelegram-014f6ca1f214.json'

'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'
def save_orders_data(data):
    credentials = Credentials.from_service_account_file(keys_file, scopes=scopes)
    gc = gspread.authorize(credentials)
    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)
    sheet_id = '1TXri49EUnU2a4S5xLfwu1jEEeMSi7b7u_z7y_En_L14'
    gs = gc.open_by_key(sheet_id)
    worksheet1 = gs.worksheet('Лист1')
    # dataframe (create or import it)
    df = pd.DataFrame(data)
    # write to dataframe
    worksheet1.clear()
    set_with_dataframe(worksheet=worksheet1, dataframe=df, include_index=False,
                       include_column_header=True, resize=True)


