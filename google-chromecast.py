import pychromecast
from pychromecast.controllers.youtube import YouTubeController
from configparser import ConfigParser
import os
import time

class Chromecast:
    def __init__(self):
        """Creates a new Chromecast by checking the user.ini for the device or creating a new entry in the config file
        """

        exists = os.path.isfile('./user.ini')
        if exists:

            #Set up the config parser and get the info from the config file
            self.config = ConfigParser()
            self.config.read('./user.ini')
            self.get_chromecast()

            #Create the chromecast object
            self.chromecast = pychromecast.Chromecast(host=self.chromecast_info['main_chromecast_host'],port=int(self.chromecast_info['main_chromecast_port']))
            self.chromecast.wait()

            self.yt_controller = YouTubeController()
            self.chromecast.register_handler(self.yt_controller)            
            
        else:
            print("The user.ini does not exist. The program probably does not work then...")
            exit(1)
    
    def get_chromecast(self):
        """Try and get the chromecast from using the config or get a chromecast from the network
        """
        if self.config.has_option('Chromecast','main_chromecast'):
                try:
                    self.chromecast_info = self.config['Chromecast']
                except:
                    print("It appears a section is missing from your config file")
        else:
            chromecasts = pychromecast.get_chromecasts()
            if len(chromecasts) is not 1:
                print(chromecasts)
            else:
                print(f"Selected {chromecasts[0]}")
                self.config.add_section('Chromecast')
                self.config.set('Chromecast','main_chromecast',chromecasts[0].name)
                self.config.set('Chromecast','main_chromecast_host',chromecasts[0].host)
                self.config.set('Chromecast','main_chromecast_port',str(chromecasts[0].port))
                self.config.set('Chromecast','main_chromecast_device',str(chromecasts[0].device))

                with open('./user.ini','w') as cfgfile:
                    self.config.write(cfgfile)
    
    def play_youtube_video(self,youtube_video_url):
        self.yt_controller.play_video(youtube_video_url) 