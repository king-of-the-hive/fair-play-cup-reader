from calendar_helper import get_service, read_existing_events, insertevent
import requests
import re
from datetime import datetime, timezone, timedelta

print("STARTING")
service = get_service()
tournaments = [117]
tourn_short_name = "[WC24]"


def readtournament(id, existing_matchids):
    print("READING TOURNAMENT {}".format(id))
    page = requests.get(
        f"https://www.boardspace.net/cgi-bin/tournament-signup.cgi?tournamentid={str(id)}"
    )
    p = page.text.replace("\n", "").replace("\r", "")
    players = re.findall("fromname=(.*?)&matchid=|<td>(TBA)<\/td>", p)
    players = list(map(lambda x: x[1] if x[0] == "" else x[0], players))
    players2 = [
        [players[j * 2], players[j * 2 + 1]]
        for j in range(int(len(players) / 2))
        if players[j * 2] != "TBA" or players[j * 2 + 1] != "TBA"
    ]
    players = sum(players2, [])
    tournname = re.findall("return false;'>(.*?) </a>", p)[1]
    cells = re.findall("editmatch.*?</td><td.*?>(.*?)</td><td>", p)
    for i in range(len(cells)):
        matchid = 0
        try:
            shouldinsertevent = False
            dates = re.findall(
                "scheduled ([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2})", cells[i]
            )
            matchid = re.findall("matchid=(.*?)>", cells[i])
            if len(matchid) > 0:
                matchid = matchid[0]
                if len(dates) > 0:
                    d = max(
                        [
                            datetime.strptime(x, "%Y-%m-%d %H:%M").replace(
                                tzinfo=timezone.utc
                            )
                            for x in dates
                        ]
                    )
                    shouldinsertevent = True
                else:
                    d = "Not scheduled formally"
                if shouldinsertevent:
                    de = d + timedelta(hours=1)
                    start = d.strftime("%Y-%m-%dT%H:%M")
                    start_z = d.strftime("%Y-%m-%dT%H:%M:00Z")
                    end = de.strftime("%Y-%m-%dT%H:%M")
                    end_z = de.strftime("%Y-%m-%dT%H:%M:00Z")
                    if matchid in existing_matchids:
                        print(
                            f"MatchID {matchid} already exists, checking if date and time updated"
                        )
                        if (
                            existing_matchids[matchid]["start"] == start_z
                            and existing_matchids[matchid]["end"] == end_z
                        ):
                            print("Start and end time the same, skipping")
                            shouldinsertevent = False
                        else:
                            service.events().delete(
                                calendarId="beekeepertournament@gmail.com",
                                eventId=existing_matchids[matchid]["eventId"],
                            ).execute()
                    if shouldinsertevent:
                        eventdata = {
                            "tournname": tournname,
                            "matchid": matchid,
                            "p1": players[i * 2],
                            "p2": players[i * 2 + 1],
                            "start": start,
                            "end": end,
                            "colorid": int(id) % 11 + 1,
                            "tourn_short_name": tourn_short_name,
                        }
                        insertevent(eventdata, service)
                        print("SUCCESS", eventdata)
        except:
            shouldinsertevent = False


existing_matchids = read_existing_events(service)
for id in tournaments:
    readtournament(id, existing_matchids)
