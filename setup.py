from argparse import ArgumentParser
import time
import datetime

class Setup:
    def __init__(self):
        """Setup for command line options
        """
        parser = ArgumentParser()
        parser.add_argument("-n",'--new',help="Fetches a new subscriptions list.",action="store_true")
        parser.add_argument('-f','--filter',type=float,help="Filter the videos this number behind today's date.\
        For example, setting to 2 would be getting videos from (today's date - 2 days) \
        Default = 1 day.")
        parser.add_argument('-l','--list',action='store_true',help='List all of the videos stored locally.')
        self.args = parser.parse_args()

        if self.args.filter is None:
            self.args.filter = time.time() - 86400
        else:
            self.args.filter = time.time() - 86400 * self.args.filter
        
        self.args.filter = datetime.datetime.fromtimestamp(self.args.filter)
        print("Filter set: " + str(self.args.filter.date())) 