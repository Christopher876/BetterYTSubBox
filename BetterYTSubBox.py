import os
from configparser import ConfigParser
import time
from dateutil.parser import parse as date_parse
from datetime import date,timezone,datetime 
import json

import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

from youtube import SubscriptionsList,Channel,get_subscriptions, load_local_videos
from setup import Setup
from google_chromecast import Chromecast

from PyInquirer import prompt
from examples import custom_style_2

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

#Class for google authentication
class Authentication:
    def __init__(self):
        """Create the authentication object and save load all that is necessary
        """
        exist = os.path.isfile('./user.ini')
        if exist:
            config = ConfigParser()
            config.read('./user.ini')
            self.token = config['YouTube']['token']
            self.refresh_token = config['YouTube']['refresh_token']
            self.id_token = config['YouTube']['id_token']
            self.token_uri = config['YouTube']['token_uri']
            self.client_id = config['YouTube']['client_id']
            self.client_secret = config['YouTube']['client_secret']
        else:
            self.get_authenticated_service()
            
    def get_authenticated_service(self):
        """Get the first authentication from Google if the user.ini file does not exist
        or if something in the user.ini is not working
        """
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_console()
        authentication.save_auth_info(credentials)
        return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)    
    
    #Check if token expired and get a new one
    def check_auth_token(self):
        config = ConfigParser()
        config.read('./user.ini')

        #Setup the credentials
        credentials = google.oauth2.credentials.Credentials(
                token=config['YouTube']['token'],
                refresh_token=config['YouTube']['refresh_token'],
                id_token=config['YouTube']['id_token'],
                token_uri=config['YouTube']['token_uri'],
                client_id=config['YouTube']['client_id'],
                client_secret=config['YouTube']['client_secret'],
                scopes=SCOPES
        )
        
        #Get a new token
        if(time.time() > float(config['YouTube']['token_received']) + 3600):
            #Refresh the token
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)

            #Set all of our new variables
            self.token = credentials.token
            self.refresh_token = credentials.refresh_token
            self.id_token = credentials.id_token
            self.token_uri = credentials.token_uri
            self.client_id = credentials.client_id
            self.client_secret = credentials.client_secret

            #Save the new variables to the file
            self.save_auth_info(credentials)
            return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)
        
        else:
            return build(API_SERVICE_NAME, API_VERSION, credentials = credentials) 

    def save_auth_info(self,credentials : google.oauth2.credentials.Credentials):
        #Check if file exists
        exist = os.path.isfile('./user.ini')

        #This may need to check the user.ini for any problems
        if exist is not True:
            open('./user.ini','a').close()

        config = ConfigParser()
        cfgfile = open('./user.ini','w')

        config.add_section('YouTube')
        config.set('YouTube','token',credentials.token)
        config.set('YouTube','refresh_token',credentials._refresh_token)
        config.set('YouTube','id_token',str(credentials.id_token))
        config.set('YouTube','token_uri',credentials.token_uri)
        config.set('YouTube','client_id',str(credentials.client_id))
        config.set('YouTube','client_secret',credentials.client_secret)
        config.set('YouTube','token_received',str(time.time()))
        config.write(cfgfile)
        cfgfile.close()        

authentication : Authentication

def save_to_json(outfile, jsonfile):
    with open(outfile,'w') as out:
        json.dump(jsonfile,out)

def cmd(videos):
    while(True):
        uInput = input('> ')
        if uInput == 'exit':
            exit(1)
        if uInput == 'help':
            print('"exit" = exit from program\n\
            "new" without args = fetch new videos with defined filter before launching program\n \
            "new" with same way filter is used = fetch new videos with new defined filter arg')
        
        #Get new videos from subscriptions
        if uInput == 'ls':
            try:
                channel.get_channel_videos(service,setup.args.filter.date())
            except AttributeError:
                channel.check_uploads_playlist_refresh()
                channel.get_channel_videos(service,setup.args.filter.date())
            
            i = 0
            for video in videos:
                print(str(i) + ') ' + video)
                i += 1

        #Get a new set of uploads
        if uInput == 'new':
            channel.get_channel_videos(service,setup.args.filter.date())
            videos = load_local_videos()

            i = 0
            for video in videos:
                print(str(i) + ') ' + video)
                i += 1

        if 'new' in uInput and len(uInput) > 1:
            filter_date = datetime.fromtimestamp(time.time() - float(uInput.split()[1]) * 86400).date() 
            print('Getting a new set of uploads with the filter date of ' + str(filter_date))
            channel.get_channel_videos(service,filter_date)

        #Cast to Google Chromecast the video that should be played   
        elif uInput.isdigit():     
            chromecast.play_youtube_video(videos[int(uInput)])

if __name__ == '__main__':
    authentication = Authentication()
    channel = Channel()
    setup = Setup()
    chromecast = Chromecast()
    
    service = authentication.check_auth_token()
    subs = None
    if setup.args.new is True:
        print('Getting new subscription channels')
        subs = get_subscriptions(service=service,maxResults=50)
        channel.get_uploads_playlist(service,subs)
    
    else:
        print("Using local subscription channels")
        subs = channel.get_subscriptions_from_txt()
    
    videos = {}
    if setup.args.list is True:
        channel.check_uploads_playlist_refresh()
        videos = channel.get_channel_videos(service,setup.args.filter.date())
        
        #Get on the new line from when updating the same line-
        print('\n')
        i = 0
        for video in videos.keys():
            print(str(i) + ') ' + str(video))
            i += 1
    else:
        videos = load_local_videos()

        i = 0
        for video in videos:
            print(str(i) + ') ' + video)
            i += 1

    #Video Selection
    upload_videos = [
        {
            'type':'list',
            'name':'videos',
            'message':'Select a video to cast',
            'choices':videos.keys()
        }
    ]

    while(True):
        try : 
            video_choice = prompt(upload_videos,style=custom_style_2)
            os.system('clear')
            chromecast.play_youtube_video(videos[video_choice['videos']])
        
        #When ctrl+c is pressed, prevent chromecast from spewing out this    
        except KeyError: exit(1)