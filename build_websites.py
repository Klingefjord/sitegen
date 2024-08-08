import json
import re


def make_safe_filename(name):
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Remove any characters that are not alphanumeric, underscores, or hyphens
    name = re.sub(r'[^\w\-_]', '', name)
    return name.lower()

def format_opening_hours(opening_hours):
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    def format_time(time_str):
        hour = int(time_str[:2])
        minute = time_str[2:]
        period = "AM" if hour < 12 else "PM"
        hour = hour % 12 or 12
        return f"{hour}:{minute} {period}"

    periods = opening_hours['periods']
    grouped_hours = {}

    for period in periods:
        open_time = format_time(period['open']['time'])
        close_time = format_time(period['close']['time'])
        hours = f"{open_time} - {close_time}"
        if hours not in grouped_hours:
            grouped_hours[hours] = []
        grouped_hours[hours].append(days_of_week[period['open']['day']])

    formatted_hours = []

    for hours, days in grouped_hours.items():
        days.sort(key=lambda day: days_of_week.index(day))
        if len(days) == 7:
            formatted_hours.append(f"Every day: {hours}")
        elif len(days) == 5 and set(days) == set(days_of_week[:5]):
            formatted_hours.append(f"Weekdays: {hours}")
        elif len(days) == 2 and set(days) == set(days_of_week[-2:]):
            formatted_hours.append(f"Weekends: {hours}")
        else:
            ranges = []
            temp_range = [days[0]]
            for i in range(1, len(days)):
                if days_of_week.index(days[i]) == days_of_week.index(days[i-1]) + 1:
                    temp_range.append(days[i])
                else:
                    ranges.append(temp_range)
                    temp_range = [days[i]]
            ranges.append(temp_range)

            for r in ranges:
                if len(r) > 1:
                    formatted_hours.append(f"{r[0]} – {r[-1]}: {hours}")
                else:
                    formatted_hours.append(f"{r[0]}: {hours}")

    # Ensure Sunday comes last if it is part of the output
    def sort_key(x):
        if "Every day" in x:
            return -1
        elif "Weekdays" in x:
            return 0
        elif "Weekends" in x:
            return 1
        else:
            day = x.split(":")[0].split(" ")[0]
            return days_of_week.index(day)

    formatted_hours.sort(key=sort_key)

    return "\n".join(["<p>" + h + "</p>" for h in formatted_hours])

def build_websites():
    # Load the places.json info
    with open('places.json', 'r') as f:
        places = json.load(f)

    # Load the template html
    with open('template.html', 'r') as f:
        template = f.read()

    for place in places:
        opening_hours = place['opening_hours']
        name = place['name']
        address = place['address']
        phone_number = place['phone_number']
        formatted_hours = format_opening_hours(opening_hours)

        # Replace the placeholders in the template with the actual data
        website = template.replace('{{name}}', name)\
                        .replace('{{title}}', name)\
                        .replace('{{address}}', address)\
                        .replace('{{phone_number}}', phone_number)\
                        .replace('{{opening_hours}}', formatted_hours)
        
        # Save the website to a file
        with open(f'sites/{make_safe_filename(name)}.html', 'w') as f:
            f.write(website)

if __name__ == '__main__':
    build_websites()