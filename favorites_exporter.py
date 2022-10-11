#!/usr/bin/env python


import json
import os

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

import requests
import pandas as pd
import pytz

from dotenv import load_dotenv

EVENT_ID = "53b5de8d-7b9d-4fcc-a178-6433641075fe"


@dataclass
class Session:
    alias: str
    name: str
    description: str
    type: str
    level: str
    date: Optional[str] = ""
    start_time: Optional[str] = ""
    end_time: Optional[str] = ""
    location: Optional[str] = ""
    room: Optional[str] = ""


def export_favorites() -> None:
    favorites = get_favorites()
    df = pd.DataFrame(favorites)
    df.to_excel("favorites.xlsx")


def get_favorites() -> List[Session]:

    favorite_sessions: List[Session] = []

    next_token = ""
    favorites_page, next_token = _get_favorites_page(next_token)
    favorite_sessions.extend(favorites_page)
    while next_token:
        favorites_page, next_token = _get_favorites_page(next_token)
        favorite_sessions.extend(favorites_page)
    return favorite_sessions


def _get_favorites_page(next_token: str) -> tuple[list[Session], str]:
    favorite_sessions: List[Session] = []
    query_endpoint = "https://api.us-east-1.prod.events.aws.a2z.com/attendee/graphql"
    query_template = '{{"operationName":"MyFavorites","variables":{{"eventId":"{event_id}","limit":25,"nextToken":"{next_token}"}},"query":"query MyFavorites($eventId: ID!, $limit: Int, $nextToken: String) {{\\n  event(id: $eventId) {{\\n    eventId\\n    name\\n    myFavorites(limit: $limit, nextToken: $nextToken) {{\\n      items {{\\n        ...SessionFieldFragment\\n        __typename\\n      }}\\n      nextToken\\n      __typename\\n    }}\\n    __typename\\n  }}\\n}}\\n\\nfragment SessionFieldFragment on Session {{\\n  action\\n  alias\\n  createdAt\\n  description\\n  duration\\n  endTime\\n  eventId\\n  isConflicting {{\\n    reserved {{\\n      alias\\n      createdAt\\n      eventId\\n      name\\n      sessionId\\n      type\\n      __typename\\n    }}\\n    waitlisted {{\\n      alias\\n      createdAt\\n      eventId\\n      name\\n      sessionId\\n      type\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  isEmbargoed\\n  isFavoritedByMe\\n  isPaidSession\\n  level\\n  location\\n  myReservationStatus\\n  name\\n  sessionId\\n  startTime\\n  status\\n  type\\n  capacities {{\\n    reservableRemaining\\n    waitlistRemaining\\n    __typename\\n  }}\\n  customFieldDetails {{\\n    name\\n    type\\n    visibility\\n    fieldId\\n    ... on CustomFieldValueFlag {{\\n      enabled\\n      __typename\\n    }}\\n    ... on CustomFieldValueSingleSelect {{\\n      value {{\\n        fieldOptionId\\n        name\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    ... on CustomFieldValueMultiSelect {{\\n      values {{\\n        fieldOptionId\\n        name\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    ... on CustomFieldValueHyperlink {{\\n      text\\n      url\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  package {{\\n    itemId\\n    __typename\\n  }}\\n  price {{\\n    currency\\n    value\\n    __typename\\n  }}\\n  venue {{\\n    name\\n    __typename\\n  }}\\n  room {{\\n    name\\n    __typename\\n  }}\\n  sessionType {{\\n    name\\n    __typename\\n  }}\\n  speakers {{\\n    speakerId\\n    jobTitle\\n    companyName\\n    user {{\\n      firstName\\n      lastName\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  tracks {{\\n    name\\n    __typename\\n  }}\\n  __typename\\n}}\\n"}}'
    authz = os.environ["AWS_EVENTS_ACCESS_TOKEN"]
    query_data = query_template.format(event_id=EVENT_ID, next_token=next_token)
    response = requests.post(url=query_endpoint, data=query_data, headers={"authorization": authz, "Content-Type": "application/json"}, timeout=30)
    if response.ok:
        next_token = _parse_sessions(favorite_sessions, response)
    else:
        raise Exception(f"Failed to get favorites, error: {response.reason}")

    return favorite_sessions, next_token


def _parse_sessions(favorite_sessions, response):
    body = json.loads(response.text)
    favorites = body["data"]["event"]["myFavorites"]
    favorite_items = favorites["items"]
    next_token = favorites["nextToken"]
    for item in favorite_items:
        session = Session(
            alias=item["alias"],
            name=item["name"],
            description=item["description"],
            type=item["sessionType"]["name"],
            level=item["level"],
        )
        if "startTime" in item and item["startTime"]:
            time = datetime.fromtimestamp(item["startTime"] / 1000, tz=timezone.utc).astimezone(pytz.timezone("US/Pacific"))
            session.date = time.strftime("%d/%m/%Y")
            session.start_time = time.strftime("%H:%M")
        if "endTime" in item and item["endTime"]:
            time = datetime.fromtimestamp(item["endTime"] / 1000, tz=timezone.utc).astimezone(pytz.timezone("US/Pacific"))
            session.end_time = time.strftime("%H:%M")
        if "venue" in item and item["venue"]:
            session.location = item["venue"]["name"]
        if "room" in item and item["room"]:
            session.room = item["room"]["name"]
        favorite_sessions.append(session)
    return next_token


def main() -> None:
    load_dotenv()
    export_favorites()


if __name__ == "__main__":
    main()
