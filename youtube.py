from dateutil.parser import parse as date_parse
from progressbar import progress as pg

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

class SubscriptionsList:
    subscribedChannels = []

    def __init__(self):
        pass
    def add_channel_to_list(self, subscriptions):
        for channel in subscriptions['items']:
            self.subscribedChannels.append(channel['snippet']['resourceId']['channelId'])
    def print_all(self):
        for item in self.subscribedChannels:
            print(item)
        print(len(self.subscribedChannels))

class Channel:
    
    def get_uploads_playlist(self,service,channels):
        self.uploads = []
        total = len(channels.subscribedChannels)
        progress = 0

        for channel in channels.subscribedChannels:
            pg(progress,total,status='Getting the uploads playlist')
            uploads = service.channels().list(
                part='contentDetails',
                id=channel
            ).execute()
            self.uploads.append(uploads['items'][0]['contentDetails']['relatedPlaylists']['uploads'])
            progress += 1

    
    def get_channel_videos(self,service,filter_by_date,**kwargs):
        for channel in self.uploads:
            uploads = service.playlistItems().list(
                part='contentDetails',
                maxResults=5,
                playlistId=channel
            ).execute()
            for video in uploads['items']:
                if date_parse(video['contentDetails']['videoPublishedAt']) >= date_parse(filter_by_date):
                    print(video['contentDetails']['videoId'])
            input('Press enter to continue....')

        return None
