import sys
import os
import requests
import re
import io
import tempfile
import webbrowser
from PIL import Image
from bs4 import BeautifulSoup
from PyQt5 import QtGui, QtWidgets, QtCore


class ApodApp(QtWidgets.QMainWindow):

    def __init__(self):
        self.astro_URL = 'https://apod.nasa.gov/apod/ap[%%].html'
        self.astro_image_URL = 'https://apod.nasa.gov/apod/'
        self.save_path = os.path.expanduser('~\Pictures\APOD')
        self.s = requests.Session()

        super(ApodApp, self).__init__()
        self.setGeometry(50, 150, 700, 500)
        self.setWindowTitle("Astronomy picture of the day")
        self.setWindowIcon(QtGui.QIcon("favicon.jpg"))

        self.welcome_string = "Welcome to the Astronomy Picture of the Day app. \n" \
                              "Please select the date you want to see the picture of."
        self.welcome_text = QtWidgets.QLabel(self)
        self.welcome_text.setText(self.welcome_string)
        self.welcome_text.move(20, 10)
        self.welcome_text.resize(260, 50)

        self.invalid_date = "The date entered is out of range. Please enter a date between"\
                            "June 16, 1995 and today."

        self.home()

    def home(self):
        
        calendar = QtWidgets.QCalendarWidget(self)
        calendar.setGridVisible(True)
        calendar.move(20, 50)
        calendar.resize(320, 200)
        calendar.setMinimumDate(QtCore.QDate(1995, 6, 16))
        calendar.setMaximumDate(QtCore.QDate.currentDate())
        calendar.clicked[QtCore.QDate].connect(self.getApodDate)

        date = calendar.selectedDate()
        a_date = [int(str(date.year())[2:]), date.month(), date.day()]
        self.astro_date = ''.join(list(map(str, a_date)))

        see_button = QtWidgets.QPushButton("See Picture", self)
        see_button.move(20, 280)
        see_button.clicked.connect(self.getPicture)

        self.show()

    def getApodDate(self, date):
        a_date = [int(str(date.year())[2:]), date.month(), date.day()]
        b_date = list(map(str, a_date))
        self.astro_date = ''
        for x in b_date:
            if len(x) < 2:
                self.astro_date = self.astro_date + '0' + x
            else:
                self.astro_date = self.astro_date + x
                
    def getPicture(self):
        
        def get_explanation():
            raw = soup.findAll('p')[2]
            pos = [m.start() for m in re.finditer('<p>', str(raw))]
            raw = str(raw)[:pos[1]]
            soup_ = BeautifulSoup(raw, 'html.parser')
            raw = str(soup_.findAll('p')[0].text)
            return (raw.replace('\n', ' ')).replace('  ', ' ')[1:]

        def get_image():
            print(self.title)

            picture_path = soup.findAll('a')[1]
            image_link_full_res = self.astro_image_URL + picture_path.get('href')

            try:
                picture_path = soup.findAll('img')[0]
                image_link_compressed = self.astro_image_URL + picture_path.get('src')
                return {'compressed': image_link_compressed, 'full-res': image_link_full_res}
            except IndexError:
                popup = QtWidgets.QMessageBox.question(self, "No Image found.",
                                                       "APOD has uploaded a video.\nOpen link in Browser?",
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if popup == QtWidgets.QMessageBox.Yes:
                    webbrowser.open_new_tab(self.image_URL)
                    sys.exit()
                else:
                    sys.exit()

        self.image_URL = self.astro_URL.replace('[%%]', self.astro_date)
        response = self.s.get(self.image_URL)

        if response.status_code != 200:
            print(self.invalid_date)
            self.home()
            date_error = QtWidgets.QLabel(self)
            date_error.setText = self.invalid_date
            self.welcome_text.move(20, 10)
            self.welcome_text.resize(260, 50)
            
        soup = BeautifulSoup(response.text, 'html.parser')
        self.title = soup.findAll('b')[0].text[1:]
        self.image_links = get_image()
        self.image_explanation = get_explanation()
        self.showPicture()

    def showPicture(self):

        def download_image():
            image_raw = self.s.get(self.image_links['full-res'])
            image_bytes = io.BytesIO(image_raw.content)
            image = Image.open(image_bytes).convert("RGB")
            image.save(self.save_path + '\\' + self.title.replace(':', '') + '.jpg', 'JPEG',
                       dpi=[300, 300], quality=100)

        def open_browser():
            webbrowser.open_new_tab(self.image_URL)

        picture_bytes = self.s.get(self.image_links['compressed'])
        img_bytes = io.BytesIO(picture_bytes.content)
        temp_image = Image.open(img_bytes).convert("RGB")
        tf = tempfile.NamedTemporaryFile(delete=True)
        temp_image.save(tf.name + '.jpg', format=None)
        pixmap = QtGui.QPixmap(tf.name + '.jpg')
        tf.close()
        
        pixmap = pixmap.scaledToHeight(500)
        pix_label = QtWidgets.QLabel(self)
        pix_label.setPixmap(pixmap)
        pix_label.resize(pixmap.size())
        pix_label.show()
        self.resize(pixmap.width(), pixmap.height()+200)

        title_text = QtWidgets.QLabel(self)
        title_text.setText(self.title)
        title_text.resize(self.width(), 15)
        title_text.move(20, 505)
        title_text.setFont(QtGui.QFont("Times New Roman", 10, QtGui.QFont.Bold))
        title_text.show()

        explanation_text = QtWidgets.QLabel(self)
        explanation_text.setText(self.image_explanation)
        explanation_text.resize(self.width()-30, 115)
        explanation_text.setWordWrap(True)
        explanation_text.move(20, 515)
        explanation_text.show()

        download_button = QtWidgets.QPushButton("Download", self)
        exit_button = QtWidgets.QPushButton("Exit", self)
        browser_button = QtWidgets.QPushButton("Show in Browser", self)

        download_button.minimumSizeHint()
        exit_button.minimumSizeHint()
        browser_button.minimumSizeHint()
        download_button.move(20, 650)
        browser_button.move(120, 650)
        exit_button.move(220, 650)

        download_button.clicked.connect(download_image)
        exit_button.clicked.connect(sys.exit)
        browser_button.clicked.connect(open_browser)

        download_button.show()
        exit_button.show()
        browser_button.show()
        

def run():
    app = QtWidgets.QApplication(sys.argv)
    gui = ApodApp()
    sys.exit(app.exec_())


run()
