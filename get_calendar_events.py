

import datetime
import os.path
import zoneinfo
import json

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, you may need to re-run `gcloud auth application-default login`
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def main():
  """Shows basic usage of the Google Calendar API with ADC.
  Prints the full metadata of all events for the current week.
  """
  creds, project = google.auth.default(scopes=SCOPES)

  try:
    service = build("calendar", "v3", credentials=creds)

    # Get the user's calendar's timezone
    calendar_info = service.calendars().get(calendarId='primary').execute()
    timezone_str = calendar_info['timeZone']
    tz = zoneinfo.ZoneInfo(timezone_str)

    # Get the current date and calculate the start and end of the week in the user's timezone
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    start_of_next_week = start_of_week + datetime.timedelta(days=7)

    # Create timezone-aware datetime objects for the beginning of the day
    time_min_local = datetime.datetime.combine(start_of_week, datetime.time.min, tzinfo=tz)
    time_max_local = datetime.datetime.combine(start_of_next_week, datetime.time.min, tzinfo=tz)

    # Convert to RFC3339 format for the API
    time_min = time_min_local.isoformat()
    time_max = time_max_local.isoformat()

    print(f"Getting events from {start_of_week} to {start_of_week + datetime.timedelta(days=6)} in timezone {timezone_str}")

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the full JSON metadata for each event
    for i, event in enumerate(events):
      print(f"\n--- Event {i+1} / {len(events)} ---")
      # Use json.dumps for pretty printing the dictionary
      # ensure_ascii=False to correctly display Japanese characters
      print(json.dumps(event, indent=2, ensure_ascii=False))

  except HttpError as error:
    print(f"An error occurred: {error}")
  except Exception as e:
    print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
  main()
