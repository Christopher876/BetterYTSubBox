from dateutil.parser import parse as date_parse
from datetime import datetime
from progressbar import progress as pg
from os import path
import json
from time import time

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
    return subs

def save_videos_to_json(videos : {}):
    """Save all of the videos found within the filter criteria to a json file for use later
    """
    json_file = json.dumps(videos,indent=4,sort_keys=True)

    exists = path.isfile('videos.json')
    if exists:
        with open('videos.json','w') as outfile:
            outfile.write(json_file)
    else:
        with open('videos.json','w') as outfile:
            outfile.write(json_file)

def save_uploads_playlist_to_txt(uploads : []):
    """ Save all of the channels upload playlist to the file to save on some quota usage
    """

    exists = path.isfile('uploads.json')
    if exists:
        with open('uploads.txt','w') as outfile:
            outfile.write('Created: ' + str(time()) + '\n')
            for upload in uploads:
                outfile.write(upload + '\n')
    else:
        with open('uploads.txt','w') as outfile:
            outfile.write('Created:' + str(time()) + '\n')
            for upload in uploads:
                outfile.write(upload + '\n')

class SubscriptionsList:
    subscribedChannels = []

    def add_channel_to_list(self, subscriptions):
        """Add any channels found in the user's subscriptions to the subscribedChannels array
        """
        for channel in subscriptions['items']:
            self.subscribedChannels.append(channel['snippet']['resourceId']['channelId'])

    def print_all(self):
        """Function left over from making sure if all the data was there
        """
        for item in self.subscribedChannels:
            print(item)
        print(len(self.subscribedChannels))

class Channel:

    def check_uploads_playlist_refresh(self):
        """Check if the uploads playlist needs to be refreshed by checking if the current time is greater than a day plus the file creation date.
        """
        created = None
        with open('uploads.txt') as infile:
            created = infile.readline()
        file_created_time = float(str(created).split()[1])
        print('Uploads File creation date: ' + str(datetime.utcfromtimestamp(float(file_created_time))))

        if time() > file_created_time + 86400:
            if input('Would you like to fetch a set of uploads?') is 'y':
                return True
            else:
                with open('uploads.txt') as infile:
                    self.uploads = []
                    infile.readline()
                    for line in infile:
                        self.uploads.append(line)
                return False
        else:
            with open('uploads.txt') as infile:
                self.uploads = []
                infile.readline()
                for line in infile:
                    self.uploads.append(line)
            return False
    
    def get_uploads_playlist(self,service,channels):
        """Get the playlist that contains a channel's uploads and then save all of the playlists that it finds to a .txt file
        """
        self.uploads = []
        total = len(channels.subscribedChannels)
        progress = 0
        
        #Get all of the subscription channels and this function takes quite a bit of time...
        for channel in channels.subscribedChannels:
            pg(progress,total,status='Getting the uploads playlist')
            uploads = service.channels().list(
                part='contentDetails',
                id=channel
            ).execute()
            self.uploads.append(uploads['items'][0]['contentDetails']['relatedPlaylists']['uploads'])
            progress += 1
        save_uploads_playlist_to_txt(self.uploads)

    
    def get_channel_videos(self,service,filter_by_date,**kwargs):
        """ Get the videos from the channel based on the date that the video should be greater than or equal to.
        Add all of the videos to a dictionary and then save them to a json file for consumption later.
        """

        i = 0 #Keeps track of the number of videos
        videos = {}

        #Use the playlist that contains all of the uploads and add them to the videos dictionary
        for channel in self.uploads:
            uploads = service.playlistItems().list(
                part='contentDetails,snippet',
                maxResults=5,
                playlistId=channel
            ).execute()
            
            #Filter out videos that are lower than the provided filter date
            for video in uploads['items']:
                if date_parse(video['contentDetails']['videoPublishedAt']).replace(tzinfo=None) >= date_parse(filter_by_date):
                    videos[video['snippet']['title']] = video['contentDetails']['videoId']
                    single_video = (str(i) + ')  ' + video['snippet']['title'] + '  ' + video['contentDetails']['videoId'])
                    print(single_video)
                    i += 1
        save_videos_to_json(videos)
