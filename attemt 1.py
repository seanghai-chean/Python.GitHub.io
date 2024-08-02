import requests
import calendar
from datetime import datetime

# Replace 'YOUR_BOT_TOKEN' with your actual bot token obtained from BotFather
BOT_TOKEN = '7016907895:AAFFNFiHOH07NXTyVsvF2q7FGT44KhpdMZw'
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"


def send_message(chat_id, text, reply_markup=None):
    url = URL + 'sendMessage'
    params = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown',
    }
    if reply_markup:
        params['reply_markup'] = reply_markup
    response = requests.post(url, json=params)
    return response.json()


def create_web_app_button(url):
    return {
        'text': 'Open Web App',
        'web_app': {
            'url': url
        }
    }


def generate_month_calendar(year, month):
    cal = calendar.TextCalendar(calendar.SUNDAY)
    month_calendar = cal.monthdayscalendar(year, month)
    keyboard = []

    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append({'text': ' ', 'callback_data': 'ignore'})
            else:
                date_str = f'{year}-{month:02}-{day:02}'
                shift_info = get_shifts_for_date(date_str)
                row.append({
                    'text': f'{day}\n{shift_info}',
                    'callback_data': date_str
                })
        keyboard.append(row)

    # Add a button to launch the web app
    keyboard.append([create_web_app_button('https://seanghai-chean.github.io/test2.github.io/')])

    reply_markup = {'inline_keyboard': keyboard}
    return reply_markup


def get_shifts_for_date(date):
    shifts = ["O", "O", "E", "E", "L", "L", "N", "N"]
    day_of_month = int(date.split('-')[2])
    shift = shifts[(day_of_month - 1) % len(shifts)]
    return shift


def handle_update(update):
    if 'message' in update and 'text' in update['message']:
        chat_id = update['message']['chat']['id']
        message_text = update['message']['text'].lower()

        if message_text == 'hi':
            send_message(chat_id, 'Hi there! I\'m your bot.😎')
        elif message_text == 'how are you':
            send_message(chat_id, 'I\'m fine! Thank you.😘')
        elif message_text == 'shifts':
            now = datetime.now()
            reply_markup = generate_month_calendar(now.year, now.month)
            send_message(chat_id, f"{calendar.month_name[now.month]} {now.year}", reply_markup)
        elif message_text == 'help':
            send_message(chat_id, 'Type "Shifts" to see the calendar or use the button below to open the web app.')
        else:
            send_message(chat_id, 'I didn\'t understand that. Type "Help" for options.')

    elif 'callback_query' in update:
        query = update['callback_query']
        chat_id = query['message']['chat']['id']
        data = query['data']

        if data != 'ignore':
            try:
                date_selected = datetime.strptime(data, '%Y-%m-%d')
                shift_info = get_shifts_for_date(data)
                send_message(chat_id, f'You selected {date_selected.strftime("%A, %d %B %Y")}. Shift: {shift_info}')
            except ValueError:
                send_message(chat_id, 'Invalid date selected.')
        else:
            send_message(chat_id, 'This date is not available.')


def main():
    offset = None
    while True:
        try:
            response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates',
                                    params={'offset': offset, 'timeout': 100})
            response.raise_for_status()  # Raise an error for bad responses
            updates = response.json().get('result', [])

            for update in updates:
                handle_update(update)
                offset = update['update_id'] + 1 if 'update_id' in update else offset

        except requests.RequestException as e:
            print(f'Error: {e}')  # Log the error message
        except Exception as e:
            print(f'Unexpected error: {e}')  # Log unexpected errors


if __name__ == '__main__':
    main()
