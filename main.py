import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import telebot
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

token = '2055335624:AAEsw70Dq6p2UKE5nBhMZLcoiKF888tV3_A'
bot = telebot.TeleBot('2055335624:AAEsw70Dq6p2UKE5nBhMZLcoiKF888tV3_A')
capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"
chrome_options = Options()
chrome_options.add_argument("--headless")
id_users = {1: False}


# возвращает инфу о боте
# print(bot.getMe()) # шляпа через telePot
# print(bot.getUpdates())


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    bot.send_message(message.from_user.id, "Запрос принят")
    if message.text == "/start":
        global id_users
        # Если новый пользователь, то запоминаем его
        if (id_users.get(message.from_user.id) == None):
            id_users.update({message.from_user.id: True})
            print(id_users)
            sendToUserInfo(message)
        else:
            # Если пользователь уже пользовался ботом, то проверяем, запущен ли у него уже бот
            if (id_users[message.from_user.id]):
                print(id_users)
                bot.send_message(message.from_user.id, 'Бот уже запущен.')
            else:
                print(id_users)
                id_users[message.from_user.id] = True
                sendToUserInfo(message)

    elif message.text == "/stop":
        if (id_users.get(message.from_user.id) == None):
            id_users.update({message.from_user.id: False})
        else:
            id_users[message.from_user.id] = False

    else:
        bot.send_message(message.from_user.id, 'Неправильная команда, используй /start или /stop')


def sendToUserInfo(message):
    global id_users
    while id_users[message.from_user.id]:
        CREDENTIALS_FILE = 'pythonttcbot-637204aa469e.json'  # Имя файла с закрытым ключом, вы должны подставить свое

        # Читаем ключи из файла
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive'])

        httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
        service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API

        spreadsheetId = "1q46uvPcfhRrwKRzstEqJxrVmdPDxJPbydlL-C1Sd3Vs"  # сохраняем идентификатор файла
        print('https://docs.google.com/spreadsheets/d/' + spreadsheetId)

        ranges = ["Лист номер один!B2:C5"]  #

        results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                           ranges=ranges,
                                                           valueRenderOption='FORMATTED_VALUE',
                                                           dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']
        for i in range(len(sheet_values)):
            sheet_values[i][0] = sheet_values[i][0].replace(' ', '+')
            print(sheet_values[i])
            print("https://eu.tamrieltradecentre.com/pc/Trade/SearchResult?SearchType=Sell&ItemNamePattern=" + sheet_values[i][0] + "&PriceMax=" + sheet_values[i][1] + "&lang=ru-RU")

            driver = webdriver.Chrome(executable_path="C:\chromedriver.exe",options=chrome_options,desired_capabilities=capa)
            driver.get("https://eu.tamrieltradecentre.com/pc/Trade/SearchResult?SearchType=Sell&ItemNamePattern="+sheet_values[i][0]+"&PriceMax="+sheet_values[i][1]+"&lang=ru-RU")
            time.sleep(5)
            wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'trade-list-table')))
            html = driver.page_source
            soup = BeautifulSoup(html, features="lxml")
            print('started')
            locations = soup.findAll("div", {
                "data-bind": "text: StringResource['TraderLocation' + DBData.GuildKioskLocation[GuildKioskLocationID]]"})
            guilds = soup.findAll("div", {"data-bind": "text: GuildName"})
            costs = soup.findAll("span", {"data-bind": "localizedNumber: UnitPrice"})
            time_ago = soup.findAll("td", {"data-bind": "minutesElapsed: DiscoverUnixTime"})

            for i in range(len(locations)):
                bot.send_message(message.from_user.id, 'Локация ' +
                                 locations[i].text + ', гильдия ' +
                                 guilds[i].text + ', цена = ' +
                                 costs[i].text + ', в последний раз видели ' +
                                 time_ago[i].text + '\n')
            # print(locations[i].text)
            # print(guilds[i].text)
            # print(costs[i].text)
            # print(time_ago[i].text + '\n')

            driver.close()

            print('finished')
            time.sleep(10)

bot.infinity_polling()
