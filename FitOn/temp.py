from datetime import datetime, timedelta
import pytz

# Create a datetime object for March 10th, 12:00 AM EST
est = pytz.timezone('Asia/Kolkata')
date_time = est.localize(datetime(2024, 3, 10, 0, 0))

# Convert the datetime object to milliseconds
milliseconds = int(date_time.timestamp() * 1000)

print(milliseconds)