"""
A python GUI App that pulls the Astronomy Picture of the Day (APOD) from
apod.nasa.gov

The app uses a calender to take user input of date and then displays the image 
on that date, with it's title and
explanation below.
"""

# Import all required libraries.
import sys
import os
import re
import io
import tempfile
import webbrowser

import requests
from PIL import Image
from bs4 import BeautifulSoup
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import QMessageBox, QLabel, QCalendarWidget, QPushButton


# Create ApodApp class for the GUI
class ApodApp(QMainWindow):

    def __init__(self):

        # The URL for the APOD is of the format ~/apod/apYYMMDD.html
        # [%%] will be replaced my the date chosen by user.
        self.astro_URL = 'https://apod.nasa.gov/apod/ap[%%].html'

        # Prefix for hi-res image.
        self.astro_image_URL = 'https://apod.nasa.gov/apod/'

        # Local directory to save image.
        self.save_path = os.path.expanduser('~\Pictures\APOD')

        # Start requests session.
        self.apod_session = requests.Session()

        super(ApodApp, self).__init__()

        # Set properties of of GUI window.
        self.setGeometry(50, 150, 700, 500)
        self.setWindowTitle("Astronomy picture of the day")
        self.setWindowIcon(QtGui.QIcon("favicon.jpg"))

        self.welcome_string = "Welcome to the Astronomy Picture of the Day " \
                              "app.\n" \
                              "Please select the date you want to see the " \
                              "picture of."
        self.welcome_text = QLabel(self)
        self.welcome_text.setText(self.welcome_string)
        self.welcome_text.move(20, 10)
        self.welcome_text.resize(260, 50)

        self.invalid_date = "The date entered is out of range. Please enter a "\
                            "date between" \
                            "June 16, 1995 and today."

        self.home()

    def home(self):
        """
        Home page of the App. 
        """

        # Create and display calendar object.
        calendar = QCalendarWidget(self)
        calendar.setGridVisible(True)
        calendar.move(20, 50)
        calendar.resize(320, 200)
        calendar.setMinimumDate(QtCore.QDate(1995, 6, 16))
        calendar.setMaximumDate(QtCore.QDate.currentDate())
        calendar.clicked[QtCore.QDate].connect(self.get_apod_date)

        # Get date selected by calendar object and change date to desired 
        # format. (YYMMDD)
        date = calendar.selectedDate()
        a_date = [int(str(date.year())[2:]), date.month(), date.day()]
        self.astro_date = ''.join(list(map(str, a_date)))

        # Create "See Picture" button. Connect it to get_picture function.
        see_button = QPushButton("See Picture", self)
        see_button.move(20, 280)
        see_button.clicked.connect(self.get_picture)

        # Display all objects in the window.
        self.show()

    def get_apod_date(self, date):
        """
        Function to clean date string from calendar object and return desired
        format. (YYMMDD)
        """

        a_date = [int(str(date.year())[2:]), date.month(), date.day()]
        b_date = list(map(str, a_date))
        self.astro_date = ''
        for x in b_date:
            if len(x) < 2:
                self.astro_date = self.astro_date + '0' + x
            else:
                self.astro_date = self.astro_date + x

    def get_picture(self):
        """
        Downloads the image and other attributes about the image.
        :return:
        """

        def get_explanation():
            """
            Extracts the explanation provided for the image.
            :return:
            """
            raw = soup.findAll('p')[2]
            pos = []
            for m in re.finditer("<p>", str(raw)):
                pos.append(m.start())
            raw = str(raw)[:pos[1]]
            soup_ = BeautifulSoup(raw, 'html.parser')
            raw = str(soup_.findAll('p')[0].text)
            return (raw.replace('\n', ' ')).replace('  ', ' ')[1:]

        def get_image():
            """
            Gets the actual image.

            The image used for display purposes is a low resolution version.
            This keeps the download time low for otherwise HD images.
            :return:
            """
            print(self.title)

            picture_path = soup.findAll('a')[1]
            image_link_full_res = self.astro_image_URL + picture_path.get('href')

            try:
                picture_path = soup.findAll('img')[0]
                image_link_compressed = self.astro_image_URL + picture_path.get('src')
                return {'compressed': image_link_compressed,
                        'full-res': image_link_full_res}

            # Certain days, apod uploads a video. Give user the option to view
            # it in their web browser.
            except IndexError:
                error_string = "APOD has uploaded a video.\n" \
                               "Open link in Browser?"
                popup = QMessageBox.question(self, "No Image found.",
                                             error_string,
                                             QMessageBox.Yes | QMessageBox.No)
                if popup == QMessageBox.Yes:
                    webbrowser.open_new_tab(self.image_URL)
                    sys.exit()
                else:
                    sys.exit()

        self.image_URL = self.astro_URL.replace('[%%]', self.astro_date)
        response = self.apod_session.get(self.image_URL)

        if response.status_code != 200:
            print(self.invalid_date)
            self.home()
            date_error = QLabel(self)
            date_error.setText = self.invalid_date
            self.welcome_text.move(20, 10)
            self.welcome_text.resize(260, 50)

        # Create BeautifulSoup object, and extract important attributes.
        soup = BeautifulSoup(response.text, 'html.parser')
        self.title = soup.findAll('b')[0].text[1:]  # Title
        self.image_links = get_image()  # Image links.
        self.image_explanation = get_explanation()  # Explanation
        self.showPicture()  # Display downloaded picture.

    def showPicture(self):
        """
        This function displays the downloaded image for selected date.

        The function draws over the home screen with all the attributes
        extracted previously. It also let's the user download a high resolution
        copy of the displayed image.

        The downloaded image is saved in <User Profile>\Pictures\APOD
        The images are named by their title.
        :return:
        """

        def download_image():
            """
            Downloads a high resolution version of the displayed image as JPEG.
            :return:
            """

            image_raw = self.s.get(self.image_links['full-res'])
            image_bytes = io.BytesIO(image_raw.content)
            image = Image.open(image_bytes).convert("RGB")
            image.save(self.save_path + '\\' + self.title.replace(':', '') +
                       '.jpg', 'JPEG',
                       dpi=[300, 300], quality=100)

        def open_browser():
            """
            Function opens image URL in user's default web browser.
            :return:
            """

            webbrowser.open_new_tab(self.image_URL)

        # Create a temporary file with the low-res version of image.
        # The temporary file is deleted when the program exits.
        picture_bytes = self.s.get(self.image_links['compressed'])
        img_bytes = io.BytesIO(picture_bytes.content)
        temp_image = Image.open(img_bytes).convert("RGB")
        tf = tempfile.NamedTemporaryFile(delete=True)
        print(tf.name)  # Print title to console.
        temp_image.save(tf.name + '.jpg', format=None)
        pixmap = QtGui.QPixmap(tf.name + '.jpg')
        tf.close()

        # Create a pixel map of the image. Scale the image such that image
        # height is 500 pixels. Also resize GUI window to fit the image and
        # explanation.
        pixmap = pixmap.scaledToHeight(500)
        pix_label = QLabel(self)
        pix_label.setPixmap(pixmap)
        pix_label.resize(pixmap.size())
        pix_label.show()
        self.resize(pixmap.width(), pixmap.height() + 200)

        # Display title of Image.
        title_text = QLabel(self)
        title_text.setText(self.title)
        title_text.resize(self.width(), 15)
        title_text.move(20, 505)
        title_text.setFont(QtGui.QFont("Times New Roman", 10, QtGui.QFont.Bold))
        title_text.show()

        # Display explanation of image.
        explanation_text = QLabel(self)
        explanation_text.setText(self.image_explanation)
        explanation_text.resize(self.width() - 30, 115)
        explanation_text.setWordWrap(True)
        explanation_text.move(20, 515)
        explanation_text.show()

        # Create three buttons.
        download_button = QPushButton("Download", self)
        exit_button = QPushButton("Exit", self)
        browser_button = QPushButton("Show in Browser", self)

        # Set dimensions of the three buttons.
        download_button.minimumSizeHint()
        exit_button.minimumSizeHint()
        browser_button.minimumSizeHint()
        download_button.move(20, 650)
        browser_button.move(120, 650)
        exit_button.move(220, 650)

        # Assign functions to the buttons.
        download_button.clicked.connect(download_image)
        exit_button.clicked.connect(sys.exit)
        browser_button.clicked.connect(open_browser)

        # Show the buttons.
        download_button.show()
        exit_button.show()
        browser_button.show()


def run():
    app = QApplication(sys.argv)
    gui = ApodApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
