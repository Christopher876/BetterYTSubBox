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

class ChannelUploads:
    def __init__(self, videos):
        self.uploads = {}
        for item in videos['items']:
            self.uploads['https://www.youtube.com/watch?v=' + item['contentDetails']['videoId']] = item['contentDetails']['videoPublishedAt']
        
        for key,value in self.uploads.items():
            pass
