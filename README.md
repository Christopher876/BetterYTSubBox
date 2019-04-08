# BetterYTSubBox

BetterYTSubBox is a project that has a simple goal of providing people with a way to use YouTube and get the latest videos from their favorite content creators without having the YouTube Sub box deciding what to show you.

A little background is that I have almost near 400 subscriptions to channels and I have to keep visiting many of them to ever see any of their videos and it has gotten to the point where it is just straight up annoying having to do that each and every time I want to see a video. I would jump onto YouTube and the only videos I would see are from what the algorithm deemed I should see.

# Licenses

This project uses third party libraries and as such there are [licenses](THIRD-PARTY-LICENSES.txt) included with an overview file as well as individual licenses. The individual licenses can be found within the "Licenses."

# Usage

* Setup a new Youtube Api Project on https://console.developers.google.com/
* Download the file and rename it to "client_secret.json" and put it in the root directory of the project
* Launch the project with these commands: **NOTE: Just relaunch if it does not start the first time**
  * -l = fetches a new set of uploads
  * -n = fetches a new set of subscriptions
  * -f = Used with -l and it filter videos by setting the minimum date that the program should look at, for example, you would put 2 to filter by today's date - 2
* Select a video and enjoy watch it casting to your tv

# TO DO

- Select 1 from multiple Chromecasts if there are many
- Select using VLC or casting to a Chromecast or opening in browser
- A GUI needs to be added - PyQT will be used or rewriting in C++ so that the code running everything can be cross platform
- Selecting and Queuing videos to play back to back **This will not be added to the Command line program and instead will be added to the version using the GUI**
- ~~Command line options to change different things~~ **Has been added**
