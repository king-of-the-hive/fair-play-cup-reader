import re
import pandas as pd
from datetime import datetime, timezone, timedelta
from calendar_helper import get_service as gs_cal
from calendar_helper import read_existing_events, insertevent
from helper import get_service as gs
from helper import read_sheet

print("STARTING")

tournname = "Hive Fair Play Cup 2024"
tourn_short_name = "[FP24]"
calendar_service = gs_cal()
sheet_service = gs()
spreadsheet_id = "1UV9LrVmk5e8N_-iLr9IMVW0kdQ9_cmAw6b9Ro89ZBbk"
NUM_ROUNDS = 6

def get_round_fd(val):
    df = pd.DataFrame(val).T
    df = df.reset_index(drop=True)
    return df

rounds = []
for j in range(NUM_ROUNDS):
    _range = f"R. {j+1} - Team Comp.!A:H"
    try:
        response = read_sheet(sheet_service, spreadsheet_id, _range)
        values = response["values"]
        rounds.append(get_round_fd(values))
    except:
        pass

df = pd.concat(rounds, ignore_index=True)

matches = {}
for i, row in df.iterrows():
    if ('white' in row[1] and 'black' in row[5]) or ('black' in row[1] and 'white' in row[5]):
        player1 = row[1]
        player2 = row[5]
        scheduled_date = row[6]
        scheduled_time = row[7]
        matchid = sum([ord(char) ** 3 for char in player1 + player2 + str(i)])
        player1 = player1.replace(" (white)", "").replace(" (black)", "")
        player2 = player2.replace(" (white)", "").replace(" (black)", "")
        matches[matchid] = {
            "player1": player1,
            "player2": player2,
            "scheduled_date": scheduled_date,
            "scheduled_time": scheduled_time,
        }

matches = {
    match: matches[match]
    for match in matches
    if (
        (
            matches[match]["scheduled_date"] != ""
            and not pd.isna(matches[match]["scheduled_date"])
        )
    )
}

existing_matchids = read_existing_events(calendar_service)
for match in matches:
    shouldinsertevent = True
    dates = [
        str(matches[match]["scheduled_date"])
        + " "
        + str(matches[match]["scheduled_time"]),
    ]
    dates = [x for x in dates if re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", x)]
    # print(dates)
    if len(dates) > 0:
        d = max(
            [
                datetime.strptime(x, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
                for x in dates
            ]
        )
        de = d + timedelta(hours=1)
        start = d.strftime("%Y-%m-%dT%H:%M")
        start_z = d.strftime("%Y-%m-%dT%H:%M:00Z")
        end = de.strftime("%Y-%m-%dT%H:%M")
        end_z = de.strftime("%Y-%m-%dT%H:%M:00Z")
        # print(match)
        eventdata = {
            "tournname": tournname,
            "matchid": str(match),
            "p1": matches[match]["player1"],
            "p2": matches[match]["player2"],
            "start": start,
            "end": end,
            "colorid": 2,
            "tourn_short_name": tourn_short_name,
        }
        print(eventdata)
        if str(match) in existing_matchids:
            print(
                "MatchID {} already exists, checking if date and time updated".format(
                    match
                )
            )
            if (
                existing_matchids[str(match)]["start"] == start_z
                and existing_matchids[str(match)]["end"] == end_z
            ):
                print("Start and end time the same, skipping")
                shouldinsertevent = False
            else:
                calendar_service.events().delete(
                    calendarId="beekeepertournament@gmail.com",
                    eventId=existing_matchids[str(match)]["eventId"],
                ).execute()
        if shouldinsertevent:
            insertevent(eventdata, calendar_service)
