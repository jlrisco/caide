from datetime import datetime, timedelta, time

from_date_str = "2010-03-20T09:30:00+00:00"
to_date_str = "2010-03-23T17:29:59+00:00"

from_date = datetime.strptime(from_date_str, '%Y-%m-%dT%H:%M:%S%z')
to_date = datetime.strptime(to_date_str, '%Y-%m-%dT%H:%M:%S%z')

ti = from_date.replace(hour=7, minute=30, second=0)
te = from_date.replace(hour=17, minute=29, second=59)

if from_date >= ti and from_date <= te:
    print("si")
else:
    print("no")