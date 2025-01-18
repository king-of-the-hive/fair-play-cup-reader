# python -m pip install helium 

import os, yaml
import helium as he
from selenium.webdriver.common.keys import Keys

he.Config.implicit_wait_secs = 20

def login_to_hg():
    driver = he.start_chrome()
    driver.maximize_window()
    he.go_to('https://hivegame.com/')
    he.click('Login')
    username, password = get_credentials_for_hg()
    he.write(username, into='Email')
    he.write(password, into='Password')
    he.click('Sign in')
    return driver

def get_credentials_for_hg():
    if os.path.exists("hg_login.yml"):
        with open("hg_login.yml", 'r') as secrets:
            login = yaml.safe_load(secrets)
            username = login["username"]
            password = login["password"]
    else:
        username = input("Type your username: ")
        password = input("Type your password (unsafe! on your own risk!): ")
    return username, password

def create_tournament(driver, groupname, **params):
    TNAME = params.get("TOURNAMENT_NAME", "TEST 2025")
    SEASON_NAME = params.get("SEASON_NAME")
    if SEASON_NAME:
        TOURNAMENT_NAME = f"{TNAME} ⬡ {SEASON_NAME} ⬡ {'GROUP ' if TNAME == 'KotH' else ''}{groupname}"
    else:
        TOURNAMENT_NAME = f"{TNAME} ⬡ {groupname}"
    TOURNAMENT_DESCRIPTION = params.get("TOURNAMENT_DESCRIPTION", "TEST DESCRIPTION\n\TEST DESCRIPTION\n\nTEST DESCRIPTION")
    TOURNAMENT_MODE = params.get("TOURNAMENT_MODE", "Correspondence")
    MIN_PLAYERS = params.get("MIN_PLAYERS", 2)
    MAX_PLAYERS = params.get("MAX_PLAYERS", 10)
    INVITES_MODE = params.get("INVITES_MODE", "Invite Only")
    TIME_DISTRIBUTION = params.get("TIME_DISTRIBUTION", "Total time each")
    DAYS_PER_PLAYER = params.get("DAYS_PER_PLAYER", 1)
    START_MODE = params.get("START_MODE", "Manual")
    START_DATE = params.get("START_DATE", "2025-01-01")
    START_HOUR = params.get("START_HOUR", 4)
    AMPM = params.get("AMPM", "A")
    FIXED_ROUND_DURATION = params.get("FIXED_ROUND_DURATION")

    he.click('Tournaments')
    he.click('Create Tournament')
    he.click(TOURNAMENT_MODE)
    he.write(TOURNAMENT_NAME, into='Tournament Name')
    he.write(TOURNAMENT_DESCRIPTION, into='Description')

    sliders = he.find_all(he.S("//*[@role='slider']"))

    min_players_slider = sliders[0]
    he.click(min_players_slider)
    while int(min_players_slider.web_element.get_attribute("aria-valuenow")) > MIN_PLAYERS:
        he.press(he.LEFT)

    max_players_slider = sliders[1]
    he.click(max_players_slider)
    while int(max_players_slider.web_element.get_attribute("aria-valuenow")) < MAX_PLAYERS:
        he.press(he.RIGHT)

    if INVITES_MODE == 'Invite Only':
        if(he.Button(to_left_of='Invite Only').exists()):
            he.click(he.Button(to_left_of='Invite Only'))

    if TOURNAMENT_MODE == 'Correspondence':
        if TIME_DISTRIBUTION == 'Total time each':
            he.click('Total time each')
            time_slider = sliders[2]
            he.click(time_slider)
            while int(time_slider.web_element.get_attribute("aria-valuenow")) < DAYS_PER_PLAYER:
                he.press(he.RIGHT)
    if TOURNAMENT_MODE == 'Real time':
        td = TIME_DISTRIBUTION.split("+")
        minutes = int(td[0])
        seconds = int(td[1])
        minutes_slider = sliders[2]
        seconds_slider = sliders[3]
        he.click(minutes_slider)
        if int(minutes_slider.web_element.get_attribute("aria-valuenow")) > minutes:
            while int(minutes_slider.web_element.get_attribute("aria-valuenow")) > minutes:
                he.press(he.LEFT)
        if int(minutes_slider.web_element.get_attribute("aria-valuenow")) < minutes:
            while int(minutes_slider.web_element.get_attribute("aria-valuenow")) < minutes:
                he.press(he.RIGHT)
        he.click(seconds_slider)
        if int(seconds_slider.web_element.get_attribute("aria-valuenow")) > seconds:
            while int(seconds_slider.web_element.get_attribute("aria-valuenow")) > seconds:
                he.press(he.LEFT)
        if int(seconds_slider.web_element.get_attribute("aria-valuenow")) < seconds:
            while int(seconds_slider.web_element.get_attribute("aria-valuenow")) < seconds:
                he.press(he.RIGHT)
        

    if START_MODE == 'Non Manual':
        if(he.Button(to_left_of='Manual start').exists()):
            he.click(he.Button(to_left_of='Manual start'))
            start_date_element = he.S('#start-time')
            calendar_start = start_date_element.web_element
            calendar_start.click()
            month = START_DATE.split("-")[1]
            if month[0] == "0":
                calendar_start.send_keys(month[1])
                #if month[1] == "1":
                #    calendar_start.send_keys(Keys.RIGHT)
            else:
                calendar_start.send_keys(month[0])
                calendar_start.send_keys(month[1])
            day = START_DATE.split("-")[2]
            if day[0] == "0":
                calendar_start.send_keys(day[1])
                calendar_start.send_keys(Keys.RIGHT)
            else:
                calendar_start.send_keys(day[0])
                calendar_start.send_keys(day[1])

            if START_HOUR == 1:
                calendar_start.send_keys(START_HOUR)
                calendar_start.send_keys(Keys.RIGHT)
            elif START_HOUR < 10:
                calendar_start.send_keys(START_HOUR)
            else:
                calendar_start.send_keys(str(START_HOUR)[0])
                calendar_start.send_keys(str(START_HOUR)[1])
            calendar_start.send_keys("0")
            calendar_start.send_keys(Keys.RIGHT)
            calendar_start.send_keys(AMPM)
    if FIXED_ROUND_DURATION:
        if(he.Button(to_left_of='Fixed round duration').exists()):
            he.click(he.Button(to_left_of='Fixed round duration'))
            sliders = he.find_all(he.S("//*[@role='slider']"))
            frd_slider = sliders[2]
            he.click(frd_slider)
            while int(frd_slider.web_element.get_attribute("aria-valuenow")) < FIXED_ROUND_DURATION:
                he.press(he.RIGHT)
            while int(frd_slider.web_element.get_attribute("aria-valuenow")) > FIXED_ROUND_DURATION:
                he.press(he.LEFT)                

    input(f"Press Enter to confirm the tournament creation: {TOURNAMENT_NAME}")
    he.click('Create Tournament')
    return TOURNAMENT_NAME

def find_tournament_link(driver, tournament_name):
    he.go_to('https://hivegame.com/tournaments')
    he.click('Future')
    he.click(tournament_name)
    tournament_link = driver.current_url
    return tournament_link

def send_invites_to_players(driver, tournament_link, player_names, **params):
    INVITE_EXCEPTION = params.get('INVITE_EXCEPTION')
    if driver.current_url != tournament_link:
        he.go_to(tournament_link)
    for p, player in enumerate(player_names):
        if player != INVITE_EXCEPTION:
            he.write(player, into='Invite player')
            button = he.S("//html/body/main/div/div/div/div/div/div/div/div/button")
            he.click(button)
            he.go_to(tournament_link)
        else:
            he.click("Join")
            he.go_to(tournament_link)
