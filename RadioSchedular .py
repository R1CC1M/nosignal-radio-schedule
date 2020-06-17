import requests
import bs4
import datetime
import time
import webbrowser
import re
from win10toast import ToastNotifier
from datetime import datetime


def OpenRadioWebsite():
    webbrowser.open('https://www.theresnosignal.com/listen')

def webscraper():    # returns 'schedule'
    # Scrapes schedule from no signal website
    res = requests.get('https://www.theresnosignal.com/listen')
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    elems = soup.select(
        '#block-yui_3_17_2_1_1584659443927_6573 > div:nth-child(1)')

    text = elems[0].getText()   # gets all the text from the div tag
    # turns single string of text into separate shows in a list format
    sched = text.split('•')
    del sched[0]

    return sched

def showChecker(showNumber):   # returns 'showNumber'
    # Checks time of each show against the current time to find the correct show in the list

    # Regex to find the time of show and name of show
    regexTime = r"\s(\d\d|\d)(\w\w|\w)\s[-]\s(\d|\w)*"  # finds time of show
    regexName = r"[:]\s.*"   # finds name of show

    showDatbase = {}  # empty dictionary for show timetable this is a nested dictionairy

    # Find how many shows in the schedual and create entries in the dictionary to match
    for n in range(len(showNumber)):

        sN = 'show' + str(n + 1)
        showDatbase[sN] = {}

    counter = 0  # starting position of counter
    num = 0      # starting position of num counter
    # loops through show keys of the database created earlier
    for k in showDatbase.keys():

        e = showNumber[num]  # gets the same show name in dictionary

        mTime = re.search(regexTime, e) # regex object for time of show
        x = mTime.group().strip()

        counter = counter + 1
        show_id = 'show' + str(counter)

        num = num + 1 # keeps track of how many times loops to mirror show number

        mName = re.search(regexName, e)  # regex object for show name
        y = mName.group() # string of regex match
        showDatbase[show_id][x] = y  # places show name into dictionary

        for keys in showDatbase[k].keys():
            # loops through show database keys and finds each nested dictionary key, to find current show playing
            show = e  # show name used later in toaster module to print to notifications

            timeS = keys[:4].strip()   # gets start time of show eg. 10AM
            timeE = keys[6:11].strip() # gets end time of show eg. 12PM

            if timeE == 'Late':  # changes last show end time to 1am so value error does not occur
                timeE = '12AM'
            else:
                pass

            currentTime = datetime.now()  # gets the current time

            tS = datetime.strptime(timeS, '%I%p') # converts string start time to datetime object
            tE = datetime.strptime(timeE, '%I%p') # converts string end time to datetime object

            combtS = datetime.combine(currentTime.date(), tS.time()) # combines current date and start time object
            combtE = datetime.combine(currentTime.date(), tE.time()) # combines current date and end time object

            # checks which show is currently playing and sends a notification
            if currentTime.time() > combtS.time() and currentTime.time() > combtE.time():
                print(keys + ' has ended')
            elif currentTime.time() < combtE.time() and combtS.time() < currentTime.time():
                toaster = ToastNotifier()
                toaster.show_toast('Now Playing - No Signal Radio ⚡ \n' + show, msg='🔊 powered by @rec_ess', icon_path='favicon.ico', duration=20, callback_on_click=OpenRadioWebsite)
                print(keys + ' currently playing')
            else:
                print(keys + ' not started yet')

print('Checking No Signal and retrieving todays schedule...')
sched = webscraper()
showChecker(sched)
