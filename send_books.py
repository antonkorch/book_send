import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import configparser
import os
import tqdm

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
    #print ('Книга отправлена на ', config["e-mail"]["to"])

# send all books from folder
def send_all_books():
    books_dir = os.getcwd() + "/books/"
    dirs = os.listdir(books_dir)
    for file in tqdm.tqdm(dirs):
        if file.endswith(".epub"):
            #print("Отправка книги: " + file)
            send_book(books_dir + file)
            # if input("Удалить книгу? (y/n): ") == "y":
            #     os.remove(file)

print ("Отправка книг на почту: " + config["e-mail"]["to"])
send_all_books()