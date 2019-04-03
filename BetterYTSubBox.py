import os
from configparser import ConfigParser
import time
from dateutil.parser import parse as date_parse
from datetime import date 
import json

import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

from youtube import SubscriptionsList,ChannelUploads

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
            pass    
    
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

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    authentication.save_auth_info(credentials)
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def get_channel_videos(service,**kwargs):
    response = service.channels().list(**kwargs).execute()
    playlist = service.playlistItems().list(
        part='contentDetails',
        maxResults=25,
        playlistId='PLOU2XLYxmsIKiWaPpfAT60S86NDTa5oAC'
    ).execute()
    uploads = ChannelUploads(playlist)

    return response

def get_subscriptions(service,**kwargs):
    """Get all of the user's subscriptions
        Creates a new subscriptions list object and then adds all of the channel ids to it
    """

    subscriptions = service.subscriptions().list(
        part='snippet',
        mine=True,
        order='alphabetical',
        **kwargs
    ).execute()

    subs = SubscriptionsList()
    subs.add_channel_to_list(subscriptions)
    
    while True:    
        subscriptions = service.subscriptions().list(
            part='snippet',
            mine=True,
            order='alphabetical',
            pageToken=subscriptions['nextPageToken'],
            **kwargs
        ).execute()
        subs.add_channel_to_list(subscriptions)

        if 'nextPageToken' not in subscriptions:
            subs.add_channel_to_list(subscriptions)
            break
    subs.print_all()
    
    return subs

if __name__ == '__main__':
    authentication = Authentication()

  # When running locally, disable OAuthlib's HTTPs verification. When
  # running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service = authentication.check_auth_token()
    #get_channel_videos(service,part='contentDetails',id='UC_x5XG1OV2P6uZZ5FSM9Ttw')
    get_subscriptions(service=service,maxResults=50)
    #v = date_parse('2019-03-27T00:02:58.000Z')
    #print(v.date())
    #print(date.today())