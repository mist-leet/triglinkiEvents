import os
import json
from datetime import datetime, timedelta

from _calendar import CalendarRequestController
import pytz
from aiohttp import web


class Server:
    def __init__(self):
        self.local_tz = pytz.timezone('Europe/Moscow')
        self.calendarRequestController = CalendarRequestController('https://calendar.google.com/calendar/ical/unng0onmro6g0oieukkpp6mvd0%40group.calendar.google.com/private-246f64586415b7bb871af8af91f94ff3/basic.ics')

    async def get_events(self, request):
        print(request)
        current_time = datetime.now()#.replace(tzinfo=pytz.utc).astimezone(self.local_tz)
        start_date = datetime(
            year=current_time.year,
            month=current_time.month,
            day=current_time.day,
            hour=0,
            minute=0
        )
        end_date = datetime(
            year=(current_time + timedelta(days=7)).year,
            month=(current_time + timedelta(days=7)).month,
            day=(current_time + timedelta(days=7)).day,
            hour=0,
            minute=0
        )

        result = None
        try:
            print(f'try to get data:')
            print(f'from: {start_date}')
            print(f'to: {end_date}')
            result = self.calendarRequestController.get_data(start_date, end_date)
            result = list(map(lambda x: x.to_dict(), result))
            print(f'result count: {len(result)}')
        except Exception as e:
            print(e)
        response = web.json_response(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    def start(self, argv=None):
        app = web.Application()
        app.add_routes([web.get('/get_events', self.get_events)])
        web.run_app(app)
        return app

server = Server()
server.start()