import requests
import sqlite3
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
    global id_users
    if message.text == "/set_average":
        # Если новый пользователь, то запоминаем его
        if (id_users.get(message.from_user.id) == None):
            id_users.update({message.from_user.id: True})
            print(id_users)
            setAveragePrices(message)
        else:
            # Если пользователь уже пользовался ботом, то проверяем, запущен ли у него уже бот
            if (id_users[message.from_user.id]):
                print(id_users)
                bot.send_message(message.from_user.id, 'Бот уже запущен.')
            else:
                print(id_users)
                id_users[message.from_user.id] = True
                setAveragePrices(message)
    else:
        if message.text == "/start":
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
            bot.send_message(message.from_user.id, 'Неправильная команда, используй /start , /stop или /set_average')


def setAveragePrices(message):
    global id_users
    conn = sqlite3.connect('table1.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Предложения ")
    k = 0
    while id_users[message.from_user.id]:

        k += 1
        cursor.execute("SELECT * FROM Товары")
        resulttable = cursor.fetchall()
        for i in range(len(resulttable)):

            print("https://eu.tamrieltradecentre.com/pc/Trade/SearchResult?SearchType=Sell&ItemNamePattern=" +
                  resulttable[i][1].replace(' ', '+') + "&lang=ru-RU&page="+str(k))
            print(resulttable[i])

            driver = webdriver.Chrome(executable_path="C:\chromedriver.exe", options=chrome_options,
                                      desired_capabilities=capa)
            driver.get("https://eu.tamrieltradecentre.com/pc/Trade/SearchResult?SearchType=Sell&ItemNamePattern=" +
                       resulttable[i][1].replace(' ', '+') + "&lang=ru-RU&page="+str(k))
            bot.send_message(message.from_user.id, resulttable[i][1])
            time.sleep(5)
            # wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'trade-list-table')))
            html = driver.page_source
            soup = BeautifulSoup(html, features="lxml")
            print('started')

            costs = soup.findAll("span", {"data-bind": "localizedNumber: UnitPrice"})

            for j in range(len(costs)):
                cursor.execute("INSERT INTO Предложения(stuff_id, price) VALUES (:stuffID,:price)",
                               {"stuffID": i + 1, "price": "".join(costs[j].text.split())})

                conn.commit()
                bot.send_message(message.from_user.id, "".join(costs[j].text.split()) + '\n')


            driver.close()

            print('finished')
            time.sleep(5)
            cursor.execute(
                "UPDATE Товары SET avg_price = (SELECT avg(price)*0.85 FROM Предложения WHERE stuff_id == :stuffID) WHERE Товары.id == :stuffID",
                {"stuffID": i + 1})
            conn.commit()
    conn.close()


def sendToUserInfo(message):
    global id_users
    conn = sqlite3.connect('table1.db')
    cursor = conn.cursor()
    while id_users[message.from_user.id]:
        cursor.execute("SELECT * FROM Товары")
        resulttable = cursor.fetchall()
        for i in range(len(resulttable)):

            print("https://eu.tamrieltradecentre.com/pc/Trade/SearchResult?SearchType=Sell&ItemNamePattern=" +
                  resulttable[i][1].replace(' ', '+') + '&PriceMax=' + str(resulttable[i][2]) + "&lang=ru-RU")
            print(resulttable[i])

            driver = webdriver.Chrome(executable_path="C:\chromedriver.exe", options=chrome_options,
                                      desired_capabilities=capa)
            driver.get("https://eu.tamrieltradecentre.com/pc/Trade/SearchResult?SearchType=Sell&ItemNamePattern=" +
                       resulttable[i][1].replace(' ', '+') + '&PriceMax=' + str(resulttable[i][2]) + "&lang=ru-RU")
            bot.send_message(message.from_user.id, resulttable[i][1])
            time.sleep(5)
            # wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'trade-list-table')))
            html = driver.page_source
            soup = BeautifulSoup(html, features="lxml")
            print('started')

            locations = soup.findAll("div", {
                "data-bind": "text: StringResource['TraderLocation' + DBData.GuildKioskLocation[GuildKioskLocationID]]"})
            guilds = soup.findAll("div", {"data-bind": "text: GuildName"})
            costs = soup.findAll("span", {"data-bind": "localizedNumber: UnitPrice"})
            time_ago = soup.findAll("td", {"data-bind": "minutesElapsed: DiscoverUnixTime"})

            for j in range(len(locations)):
                bot.send_message(message.from_user.id, 'Локация ' +
                                 locations[j].text + ', гильдия ' +
                                 guilds[j].text + ', цена = ' +
                                 costs[j].text + ', в последний раз видели ' +
                                 time_ago[j].text + '\n')

            driver.close()

            print('finished')
            time.sleep(5)
    conn.close()

bot.infinity_polling()
