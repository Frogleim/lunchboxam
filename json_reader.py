import json
import glob
import cv2 as cv
import gspread


#
def users_order(sh, username):
    dsh = gc.open('My worksheet')
    worksheet = sh.get_worksheet(0)
    worksheet.update_title(username)



def drinks(sh):
    drinks_sheet = sh.worksheet("Drinks")
    print("Rows", drinks_sheet.get_all_values()[1:])
    data = drinks_sheet.get_all_values()[1:]
    return data


def hot_dishes(sh):
    drinks_sheet = sh.worksheet("Hot Dishes")
    print("Rows", drinks_sheet.get_all_values()[1:])
    data = drinks_sheet.get_all_values()[1:]
    return data


def hot_dishes_2(sh):
    drinks_sheet = sh.worksheet("Hot Dishes 2")
    print("Rows", drinks_sheet.get_all_values()[1:])
    data = drinks_sheet.get_all_values()[1:]
    return data


def hot_dishes_3(sh):
    drinks_sheet = sh.worksheet("Hot Dishes 3")
    print("Rows", drinks_sheet.get_all_values()[1:])
    data = drinks_sheet.get_all_values()[1:]
    return data


def salads(sh):
    drinks_sheet = sh.worksheet("Salads")
    print("Rows", drinks_sheet.get_all_values()[1:])
    data = drinks_sheet.get_all_values()[1:]
    return data


def soups(sh):
    drinks_sheet = sh.worksheet("Soups")
    print("Rows", drinks_sheet.get_all_values()[1:])
    data = drinks_sheet.get_all_values()[1:]
    return data


if __name__ == '__main__':
    sa = gspread.service_account(filename='lunchboxtelegram-a72d88f7f9dc.json')

    sh = sa.open('Menus')
    print(sh)
