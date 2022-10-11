import os
import json

import requests
import pandas as pd

from dotenv import load_dotenv

from consts import EVENT_ID


REQUEST_URL = "https://api.us-east-1.prod.events.aws.a2z.com/attendee/graphql"
REQUEST_DATA_FORMAT = '{{"operationName":"RequestSeat","variables":{{"input":{{"eventId":"{event_id}","sessionId":"{session_id}"}}}},"query":"mutation RequestSeat($input: RequestSeatInput!) {{\\n  requestSeat(input: $input) {{\\n    id\\n    __typename\\n  }}\\n}}\\n"}}'


def reserve_favorites() -> None:
    authz = os.environ["AWS_EVENTS_ACCESS_TOKEN"]
    df = pd.read_excel("favorites.xlsx")
    df = df[df["reserve"] == True]
    for _, session in df.iterrows():
        session_id = session["session_id"]
        session_code = session["alias"]
        request_data = REQUEST_DATA_FORMAT.format(event_id=EVENT_ID, session_id=session_id)
        response = requests.post(url=REQUEST_URL, data=request_data, headers={"authorization": authz, "Content-Type": "application/json"}, timeout=30)
        if not response.ok:
            print(f"Failed to reserve session [{session_code}]")
        else:
            body = json.loads(response.text)
            if "errors" in body and body["errors"]:
                print(f"Failed to reserve session [{session_code}]")


def main() -> None:
    load_dotenv()
    reserve_favorites()


if __name__ == "__main__":
    main()
