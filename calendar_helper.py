from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery
import os.path, re


def read_existing_events(service):
    print("Reading existing events")
    existing_matchids = {}
    page_token = None
    while True:
        events = (
            service.events()
            .list(calendarId="beekeepertournament@gmail.com", pageToken=page_token, timeZone="Etc/GMT-0")
            .execute()
        )
        for event in events["items"]:
            if "description" in event:
                matchid = re.findall("MATCHID: ([0-9]*)", event["description"])
                if len(matchid) > 0:
                    matchid = matchid[0]
                    existing_matchids[matchid] = {
                        "eventId": event["id"],
                        "start": event["start"]["dateTime"],
                        "end": event["end"]["dateTime"],
                    }
        page_token = events.get("nextPageToken")
        if not page_token:
            break
    # print(existing_matchids)
    return existing_matchids

def get_service():
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    if os.path.exists("token_calendar.json"):
        creds = Credentials.from_authorized_user_file("token_calendar.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token_calendar.json", "w") as token:
            token.write(creds.to_json())

    service = discovery.build("calendar", "v3", credentials=creds)
    return service

def insertevent(eventdata, service):
    tourn_short_name = eventdata["tourn_short_name"] if "tourn_short_name" in eventdata else ""
    event = {
        "summary": "{} v {} {}".format(eventdata["p1"], eventdata["p2"], tourn_short_name),
        "description": "TOURNAMENT: {}<br/><br/>Match between {} and {}.<br/><br/>MATCHID: {}.".format(
            eventdata["tournname"],
            eventdata["p1"],
            eventdata["p2"],
            eventdata["matchid"],
            "" if "link" not in eventdata else "<br/><br/>Link: {}".format(eventdata["link"]),
        ),
        "start": {
            "dateTime": "{}:00-00:00".format(eventdata["start"]),
            "timeZone": "Etc/GMT-0",
        },
        "end": {
            "dateTime": "{}:00-00:00".format(eventdata["end"]),
            "timeZone": "Etc/GMT-0",
        },
        "visibility": "public",
        "colorId": eventdata["colorid"],
    }
    event = service.events().insert(calendarId="beekeepertournament@gmail.com", body=event).execute()
