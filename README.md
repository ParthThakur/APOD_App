# APOD GUI App

NASA post an Astronomy picture of the Day, everyday at apod.nasa.gov. I have creates a GUI app which 
lets users select and download the picture on a particular date.

### Getting Started

-----

To get the app on your local machine, make sure you have a working installation of `python 3.6` or 
above.

##### Perquisites

To run the app, you will need to have the following python libraries:

- beautifulsoup4  v4.6.0
- Pillow  v5.1.0
- PyQt5  v5.9.2
- requests  v2.18.4

These libraries are listed in the `requirements.txt` file. Run the following code to get all the 
required libraries.

```
pip install -r requirements.txt
```

### Known Issues

-----

    1. The app can only display one image at a time. To get another image, a restart is required.
    2. The app will freeze while downloading the preview and while downloading the high resolution 
       image.

### License

-----

This project is licensed under the MIT License - see the 
[LICENSE.md](https://gist.github.com/PurpleBooth/LICENSE.md) file for details