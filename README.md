# Router

Router is a web app that will display a map of venues from Foursquare closest to the user.
Users can see a quick overview of the venues, with information such as location (from the map),
number of users at a particular venue, and number of tips left by the other users for the location.
Users can also specify a search term to look for specific venues, e.g. 'cupcake'.

From the map, users can select an arbitrary number of points and the app will find a route to travel
through all the selected points (starting from the user's location). The app will try to optimise the path
to minimize travel distances.
Paths are minified, i.e. only points in which user has to change direction are returned.

The app also exposes a RESTful API that other clients can use. The included Android client uses this to (mostly) replicate
the website's functionality.

# Setup

## Server
### Install Python v2.7.6
https://www.python.org/downloads/

### Install pip
Save https://raw.github.com/pypa/pip/master/contrib/get-pip.py
Run `python get-pip.py`

### Create a Virtual Environment
This is optional, but recommended.
`virtualenv venv`
`source venv/bin/activate`

### Install depdencies
`pip install -r requirements.txt`

### Start server
`python server.py`

For future invocations, just execute the bundled `run.sh` file

### Deploy to heroku
From the root of the project, run `git subtree push --prefix server heroku master`
With my credentials, the app is accessible at https://vast-lowlands-8551.herokuapp.com

## Android Client

### Install JDK
http://www.oracle.com/technetwork/java/javase/downloads/index-jsp-138363.html

### Install Android SDK and dependencies
https://developer.android.com/tools/index.html

### Setup Android Map SDK
Speicifically, setup the signing key for maps
https://developers.google.com/maps/documentation/android/

### Build and Install
run `./gradlew clean build installDebug`
