import requests
from pyquery import PyQuery as pq
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import configparser

config = configparser.ConfigParser()
config.read('settings.ini')

def send_book(file):
    server = smtplib.SMTP(config["e-mail"]["server"], config["e-mail"]["port"])
    server.login(config["e-mail"]["login"], config["e-mail"]["password"])

    msg = MIMEMultipart()
    msg['From'] = config["e-mail"]["login"]
    msg['To'] = config["e-mail"]["to"]
    msg['Subject'] = "New book"
    binary_file = open(file, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(binary_file.read())
    encoders.encode_base64(part)

    part.add_header('Content-Disposition', "attachment; filename= %s" % file)
    msg.attach(part)

    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    print ('Книга отправлена на ', config["e-mail"]["to"])

def get_search_result(book_name, sort):
    payload = {'ab': 'ab1', 't': book_name, 'sort': sort}
    try:
        r = requests.get('http://flibusta.is/makebooklist', params=payload)
    except requests.exceptions.ConnectionError:
        print('не удалось подключиться к серверу flibusta.is')
        return 'Connection error'

    if r.text == 'Не нашлось ни единой книги, удовлетворяющей вашим требованиям.':
        print(f'Не нашлось ни единой книги по запросу {book_name}')
        return 'No result'
    else:
        return r.text
    
def fetch_book_id(search_result):
    doc = pq(search_result)
    titles = doc('div > a')
    print("Найдена книга:", titles[0].text)
    book = doc('div > a').attr.href
    return book

search_query = input('Введите название книги: ')

search_result = get_search_result(search_query, 'rating')
if search_result != 'No result' and search_result != 'Connection error':
    book_id = (fetch_book_id(search_result))
    print (f'http://flibusta.is{book_id}/')

    with open('book.epub', 'wb') as file:
        file.write(requests.get(f'http://flibusta.is{book_id}/epub').content)

    if input('Отправить книгу на почту? (y/n): ') == 'y':
        send_book("book.epub")

