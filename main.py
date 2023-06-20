import telebot
import uuid
import time
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler

bot = telebot.TeleBot(TOKEN) # import your own token
scheduler = BackgroundScheduler()

# Our Database
birthdays = {}
id, zone, name, month, day = "", "", "", "", ""

# Check that month is number from 1 to 12


def monthChecker(text):
    res = True
    try:
        res = bool(int(text) in range(1, 13))
    except ValueError:
        return False
    return res

# Check that the day is normal
# UPDATE: Add functionality to check the number that doesn't go beyond month expected range


def dayChecker(text):
    res = True
    try:
        res = bool(int(text) in range(1, 32))  # Add Checker
    except ValueError:
        return False
    return res

# Check that the zone if between -12 and 14


def zoneChecker(text):
    res = True
    try:
        res = bool(int(text) in range(-12, 15))
    except ValueError:
        return False
    return res


def checkBirthday():
    for id in birthdays:
        zone = birthdays[id][1]
        # Adjusting our time to compare time of person who has birthday
        today = [datetime.now(tz=timezone(timedelta(hours=int(zone)))).month, datetime.now(
            tz=timezone(timedelta(hours=int(zone)))).day]
        if birthdays[id][4:] == today:
            if birthdays[id][3] == False:
                bot.send_message(
                    birthdays[id][0], f"Today is the birthday of {birthdays[id][2]}")
            birthdays[id][3] = True
        else:
            birthdays[id][3] = False


scheduler.add_job(checkBirthday, 'interval', minutes=30)

# Main functionality of adding birthday through conversation


@bot.message_handler(commands=['Add'])
def addBirthday(message):
    global id
    id = str(uuid.uuid4()).replace('-', '')
    bot.send_message(
        message.chat.id, "Hello! Let's register a new person's birthday! Enter their name:")
    bot.register_next_step_handler(message, getName)


def getName(message):
    global name
    name = message.text
    bot.send_message(
        message.chat.id, "Now, what's the month of this peron's birthday? Enter number from 1 (January) to 12 (December)")
    bot.register_next_step_handler(message, getMonth)


def getMonth(message):
    global month
    month = message.text
    if monthChecker(month) == False:
        bot.reply_to(
            message, "Error! Enter valid number from 1 (January) to 12 (December)")
        bot.register_next_step_handler(message, getMonth)
    else:
        bot.send_message(
            message.chat.id, "Now, enter a valid day (Ensure that the day didn't go beyond what is expected in certain month (e.g. there is no 31 in September). Otherwise, I will crash ;)")
        bot.register_next_step_handler(message, getDay)


def getDay(message):
    global day
    day = message.text
    if dayChecker(day) == False:
        bot.reply_to(
            message, "Error! Enter valid number from 1 to 31 with caution!")
        bot.register_next_step_handler(message, getDay)
    else:
        bot.send_message(
            message.chat.id, "Now, enter valid Time Zone that this person has currently (e.g. if he lives in Aktobe, which is UTC +5, then just type 5)")
        bot.register_next_step_handler(message, getTimezone)


def getTimezone(message):
    global zone
    zone = message.text
    if zoneChecker(zone) == False:
        bot.reply_to(
            message, "Error! Enter valid Time Zone (number) from -12 to 14")
        bot.register_next_step_handler(message, getTimezone)
    else:
        birthdays[id] = []
        birthdays[id].extend([message.chat.id, zone, name,
                             False, int(month), int(day)])
        bot.send_message(
            message.chat.id, f"Well Done! {name} is recordered. I can't forget, I will remind you, trust) To add another person, type /Add command")


@bot.message_handler(commands=["Check"])
def printPeople(message):
    for id in birthdays:
        print(id, birthdays[id])


@bot.message_handler(commands=["start"])
def greet(message):
    bot.send_message(message.chat.id, "Welcome Birthday Reminder I! You can store here people's birthdays without forgeting who has today a birthday! Start with /Add command to add a new person!")


def main():
    scheduler.start()

    bot.polling()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
    checkBirthday()
