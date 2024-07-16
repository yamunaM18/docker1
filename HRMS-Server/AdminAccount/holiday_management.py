from .models import Holiday
from datetime import datetime

def add_holidayy(date_str, name):
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return {"message": "Invalid date format"}, 400

    if Holiday.objects.filter(date=date).exists():
        return {"message": "Holiday with this date already exists"}, 400

    Holiday.objects.create(date=date, name=name)

    return {"message": "Holiday added successfully"}, 201