import re
from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import List, Optional

import icalendar
import recurring_ical_events
import requests
from icalendar import Calendar

import pytz


@dataclass
class Event:
    name: str
    dtstart: datetime
    dtend: datetime
    text: str
    dtstamp: datetime
    rule: str
    picture: str

    is_donation: Optional[bool] = None
    price: Optional[int] = None
    skip: Optional[bool] = None

    def __post_init__(self):
        self.process_additional_fields()

        if self.picture and self.picture.startswith('https://drive.google.com/file/d/'):
            regex_1 = re.compile('https:\/\/drive\.google\.com\/file\/d\/(.+)\/')
            regex_2 = re.compile('https:\/\/drive\.google\.com\/file\/d\/(.+)')
            if regex_1.match(self.picture):
                self.picture = f"https://drive.google.com/u/0/uc?id={regex_1.match(self.picture).group(1)}&export=download"
            elif regex_2.match(self.picture):
                    self.picture = f"https://drive.google.com/u/0/uc?id={regex_2.match(self.picture).group(1)}&export=download"

        if isinstance(self.dtstart, date):
            self.dtstart = datetime(
                year=self.dtstart.year or 1970,
                month=self.dtstart.month or 1,
                day=self.dtstart.day or 1,
                hour=self.dtstart.time().hour,
                minute=self.dtstart.time().minute,
                second=self.dtstart.time().second
            )
        else:
            self.dtstart = datetime(
                year=self.dtstart.year or 1970,
                month=self.dtstart.month or 1,
                day=self.dtstart.day or 1,
                hour=self.dtstart.hour or 0,
                minute=self.dtstart.minute or 0,
                second=self.dtstart.second or 0
            )

        if isinstance(self.dtend, date):
            self.dtend = datetime(
                year=self.dtend.year or 1970,
                month=self.dtend.month or 1,
                day=self.dtend.day or 1,
                hour=self.dtend.time().hour,
                minute=self.dtend.time().minute,
                second=self.dtend.time().second
            )
        else:
            self.dtend = datetime(
                year=self.dtend.year or 1970,
                month=self.dtend.month or 1,
                day=self.dtend.day or 1,
                hour=self.dtend.hour or 0,
                minute=self.dtend.minute or 0,
                second=self.dtend.second or 0
            )
        # from
        # https://drive.google.com/file/d/1uBcwqgV1h7W2WMctN6aZMzVFhFidvD_5/view?usp=drive_web
        # to
        # https://drive.google.com/u/0/uc?id=1uBcwqgV1h7W2WMctN6aZMzVFhFidvD_5&export=download

    regexs = {
        'skip': '#ignore',
        'price': '#price_(\d+)',
        'is_donation': '#donation'
    }

    def process_additional_fields(self):
        self.text = re.sub('<br>|<\/br>|<p>|<\/p>', '', self.text)

        for key, regex in self.regexs.items():
            if key == 'skip':
                matches = re.compile(regex).findall(self.text)
                if any(matches):
                    self.text = re.sub(regex, '', self.text)
                    self.skip = True
                else:
                    self.skip = False
            if key == 'price':
                matches = re.compile(regex).findall(self.text)
                if any(matches):
                    self.text = re.sub(regex, '', self.text)
                    self.price = int(matches[0])
                else:
                    self.price = None
            if key == 'is_donation':
                matches = re.compile(regex).findall(self.text)
                if any(matches):
                    self.text = re.sub(regex, '', self.text)
                    self.is_donation = True
                else:
                    self.is_donation = False


    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'dtstart': str(self.dtstart),
            'dtend': str(self.dtend),
            'dtstamp': str(self.dtstamp),
            'text': self.text,
            'rule': self.rule,
            'picture': self.picture,
            'price': self.price,
            'is_donation': self.is_donation,
        }


class CalendarRequestController:

    @staticmethod
    def utc_to_local(utc_dt: datetime) -> datetime:
        if utc_dt.tzinfo.zone != 'Europe/Moscow':
            local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(CalendarRequestController.local_tz)
            return CalendarRequestController.local_tz.normalize(local_dt)
        else:
            return utc_dt

    local_tz = pytz.timezone('Europe/Moscow')

    def __init__(self, url):
        self.url = url

    def get_data(self, dfrom: datetime = None, dto: datetime = None) -> List[Event]:
        result: List[Event] = []
        response = requests.get(self.url)
        data = response.text
        gcal = Calendar.from_ical(data)

        for component in recurring_ical_events.of(gcal).between(dfrom, dto):
            if component.name == "VEVENT":
                print('process event: ', component.get('summary'), component.get('description'))
                result.append(self.create_from_cal_component(component))

        # result += self._process_rule(result)
        result.sort(key=lambda x: x.dtstart)

        if not dfrom or not dto:
            return result

        in_range = []
        for event in result:
            try:
                if (
                        event.dtstart > dfrom and event.dtend < dto and
                        not event.skip
                ):
                    in_range.append(event)
            except Exception as e:
                print(e)
        return in_range

    def create_from_cal_component(self, component: icalendar.Event) -> Event:
        return Event(
            name=component.get('summary'),
            dtstart=CalendarRequestController.utc_to_local(component.get('dtstart').dt),
            dtend=CalendarRequestController.utc_to_local(component.get('dtend').dt),
            dtstamp=CalendarRequestController.utc_to_local(component.get('dtstamp').dt),
            text=component.get('description'),
            rule=component.get('rrule'),
            picture=component.get('attach')
        )
