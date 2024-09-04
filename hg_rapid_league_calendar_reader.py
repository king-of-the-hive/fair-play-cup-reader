import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait 
from datetime import datetime, timedelta, timezone
from calendar_helper import get_service as gs_cal
from calendar_helper import read_existing_events, insertevent

tournaments_list = [
    # "ACXNa3oJETc",
    "OTYj-NLjrhZ",
    "P0vWY1cCgZo",
    "QTqVShhoDB4",
    "blZc7ZCcDVN",
    "GIN-bVCI_EM",
    "rpkSq2C--Jv",
    "lS5grMvIqU9"
]

tz_string = datetime.now().astimezone().tzinfo
print("STARTING")

calendar_service = gs_cal()

driver_service = Service("C:\\chromedriver.exe")
driver_options = webdriver.ChromeOptions()
driver_options.add_argument('--ignore-certificate-errors')
driver_options.add_argument("--log-level=1")
#driver_options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service=driver_service, options=driver_options)
driver.maximize_window()

existing_matchids = read_existing_events(calendar_service)

for tournament in tournaments_list:
    driver.get(f"https://hivegame.com/tournament/{tournament}")
    dropdown_xpath = '/html/body/main/div/div/div/details/summary'
    while True:
        try:
            _dropdown_wait = WebDriverWait(driver, 300).until(lambda x: x.find_element(webdriver.common.by.By.XPATH, dropdown_xpath))
            break
        except:
            print("Waiting for dropdown to appear")
            time.sleep(10)
    dropdown = driver.find_element(by=webdriver.common.by.By.XPATH, value=dropdown_xpath)
    dropdown.click()
    time.sleep(5)
    scheduled_xpath = '/html/body/main/div[2]/div/div[2]/details/div/div/div[2]'
    scheduled_games = driver.find_elements(by=webdriver.common.by.By.XPATH, value=scheduled_xpath)

    time.sleep(5)
    players_xpath = '/html/body/main/div[2]/div/div[2]/details/div/div/div[1]'
    players = driver.find_elements(by=webdriver.common.by.By.XPATH, value=players_xpath)

    links_xpath = '/html/body/main/div[2]/div/div[2]/details/div/a'
    links_list = driver.find_elements(by=webdriver.common.by.By.XPATH, value=links_xpath)

    tourn_name_xpath = '/html/body/main/div[2]/div/div[1]/h1'
    tourn_name = driver.find_element(by=webdriver.common.by.By.XPATH, value=tourn_name_xpath).text
    tourn_short_name = "[" + "".join([x[0] for x in tourn_name.split(" ")]) + "]"
    for i, schedule_string in enumerate(scheduled_games):
        shouldinsertevent = True
        
        if "Scheduled at" in schedule_string.text:
            print(f"Game {i}: {schedule_string.text}")
            players_list = players[i].text.split("\n")
            player_1 = players_list[0]
            player_2 = players_list[3]
            match_link = links_list[i].get_attribute("href")
            matchid = sum(
                [
                    ord(char) ** 3
                    for char in match_link + player_1 + player_2
                ]
            )
            match_date = schedule_string.text.split("Scheduled at ")[1]
            match_date = datetime.strptime(match_date, "%Y-%m-%d %H:%M")
            match_date = match_date.replace(tzinfo=tz_string).astimezone(timezone.utc)
            match_end = match_date + timedelta(hours=1)

            start = match_date.strftime("%Y-%m-%dT%H:%M")
            start_z = match_date.strftime("%Y-%m-%dT%H:%M:00Z")
            end = match_end.strftime("%Y-%m-%dT%H:%M")
            end_z = match_end.strftime("%Y-%m-%dT%H:%M:00Z")
            eventdata = {
                "tournname": tourn_name,
                "matchid": matchid,
                "p1": player_1,
                "p2": player_2,
                "start": start,
                "end": end,
                "colorid": 3,
                "tourn_short_name": tourn_short_name,
                "link": match_link,
            }
            print(eventdata)
            if str(matchid) in existing_matchids:
                print(f"MatchID {matchid} already exists, checking if date and time updated")
                if (
                    existing_matchids[str(matchid)]["start"] == start_z
                    and existing_matchids[str(matchid)]["end"] == end_z
                ):
                    print("Start and end time the same, skipping")
                    shouldinsertevent = False
                else:
                    calendar_service.events().delete(
                        calendarId="beekeepertournament@gmail.com",
                        eventId=existing_matchids[str(matchid)]["eventId"],
                    ).execute()
            if shouldinsertevent:
                print("Inserting event")
                insertevent(eventdata, calendar_service)

driver.quit()
