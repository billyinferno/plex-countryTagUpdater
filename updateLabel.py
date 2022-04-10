#/usr/bin/python3
'''
updateLabel.py
--------------
created by : Adi Martha
https://github.com/billyinferno
'''

from unittest import skip
from plexapi.server import PlexServer
from tmdbv3api import TMDb, TV
from dotenv import load_dotenv
from pprint import pprint
from tqdm import tqdm
from os import getenv, system, name, path
import pycountry
import sys

# load the environment
TMDB_API_KEY = ''
BASE_URL = ''
PLEX_TOKEN = ''
LIBRARY_NAME = 'TV Shows'
IS_FORCE = False

def clr():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

def loadEnvFile():
    global TMDB_API_KEY
    global BASE_URL
    global PLEX_TOKEN
    global LIBRARY_NAME
    load_dotenv()
    TMDB_API_KEY = getenv('TMDB_API_KEY')
    BASE_URL = getenv('BASE_URL')
    PLEX_TOKEN = getenv('PLEX_TOKEN')
    LIBRARY_NAME = getenv('LIBRARY_NAME')

# connect to TMDB
def connectToTMDB():
    print("🔗 Connect to TMDB")
    tmdb = TMDb()
    tmdb.api_key = TMDB_API_KEY
    return tmdb

# connect to plex
def connect():
    print("🔗 Connect to PLEX Server")
    baseurl = BASE_URL
    token = PLEX_TOKEN
    plex = PlexServer(baseurl, token)
    return plex

def getCountries(countries):
    countryLabel = []
    if len(countries) > 0:
        for country in countries:
            # convert the alpha_2 country to actual country name
            country_name = pycountry.countries.get(alpha_2=country)
            name = country_name.name

            # check if has common name, like South Korea?
            # otherwise we will defaulted to name
            if hasattr(country_name, 'common_name'):
                name = country_name.common_name
            
            # append the country name
            countryLabel.append("🌍 " + name)
    # return the countryLabel
    return countryLabel

def getTvShow(plex, tmdb):
    skipped = 0
    updated = 0
    notFound = 0
    notFoundList = []

    tv = TV()
    tvShows = plex.library.section(LIBRARY_NAME).search(title=None,sort="titleSort:asc")
    # loop thru the tvShows
    pBarShows = tqdm(tvShows)
    icon = ''
    for show in pBarShows:
        # set the tmdbId as blank
        tmdbId = ''
        guids = show.guids
        for guid in guids:
            if guid.id[0:4].lower() == "tmdb":
                tmdbId = guid.id[7:]

        # fetch the item from library
        item = plex.library.fetchItem(show.key)

        isLabelExists = False
        currentLabel = []
        # check if we already tag country to this item or not
        for label in show.labels:
            # check for the tag of the label
            tag = label.tag
            currentLabel.append(tag)
            if tag[0] == '🌍':
                isLabelExists = True

        if isLabelExists and not IS_FORCE:
            icon = "✔️"
            skipped = skipped + 1
        else:
            # show doesn't have country tagged yet, so we can continur
            # first let's remove all the labels
            if len(currentLabel) > 0:
                item.removeLabel(currentLabel)
            
            # initialize the variable
            isFind = False
            countryLabel = []

            # check whether we got tmdbId on the guids or not?
            if len(tmdbId) > 0:
                s = tv.details(tmdbId)
                # if we got tmdbId means we can get exact record
                countryLabel = getCountries(s.origin_country)
                # check whether we got country label or not
                if len(countryLabel) > 0:
                    isFind = True
            else:
                s = tv.search(show.title)
                # if we search we need to parse and see whether the search result has same name or not?
                for result in s:
                    # check if the title is the same or not
                    if(show.title.lower() == result.name.lower()):
                        # same title, means that we can get the original country
                        countryLabel = getCountries(result.origin_country)
                        # check whether we got country label or not
                        if len(countryLabel) > 0:
                            isFind = True
                        # once found break from the loop
                        break
            
            # check if this is FORCE?
            # if FORCE and we don't get countryLabel we need to return it to the current label
            if IS_FORCE:
                if len(countryLabel) <= 0:
                    countryLabel = currentLabel
                    isFind = True
            
            # check whether we find the country that we need to update or not?
            if not isFind:
                # cannot find the show, so we update this with "Not Found"
                icon = "🚫"
                notFound = notFound + 1
                notFoundList.append(show.title)
            else:
                # means we can update the label
                item.addLabel(countryLabel)
                icon = "✏️"
                updated = updated + 1

        pBarShows.set_description('{:50.50}'.format(icon + " " + show.title))
    
    # once finished showed the summary
    print("SUMMARY")
    print("-------")
    print("Skipped   : {}".format(skipped))
    print("Updated   : {}".format(updated))
    print("Not Found : {}".format(notFound))
    for showNotFound in notFoundList:
        print(" 🚫 " + showNotFound)

def printHelp():
    helpString = """
    Plex - TV Show Country Label Update Script
    ------------------------------------------
    This script will perform scan on your PLEX TV Shows library, and search on
    TMDB based on ID (if exists), os show name on TMDB.

    Once result from TMDB found, it will look for the origin country being put
    on the TMDB information, and update the corresponding TV Shows with the
    origin country being put on the TMDB information.

    NOTE: Before you run the script, ensure to create .env file to run script
    without any arguments, or you can override the .env with arguments.

    Supported Arguments:
    (*) -force
         this will force update the TV shows that already have country label
    (*) -clearscreen
         clear the screen before run
    (*) -plextoken
         your PLEX token that will be used to connect to your PLEX server
    (*) -tmdbapikey
         your TMDB API Key that will be used to get information from TMDB
    (*) -baseurl
         your PLEX url (eg. 127.0.0.1:32400)
    (*) -library
         Your TV Shows library name, usually it will be defaulted as
         "TV Shows"
    """
    print(helpString)
                
if __name__ == '__main__':
    if path.exists('.env'):
        # load environment file
        loadEnvFile()

    # get argument
    args = []
    if len(sys.argv) > 1:
        args = sys.argv[1:]
    
    # assuming that there are no error
    isError = False
    isNextValue = False
    isNextValueID = -1
    # loop thru argument
    for arg in args:
        if arg.lower() == "-help":
            isError = True
            printHelp()
        elif arg.lower() == "-force":
            print("🪠 Run as Force update")
            IS_FORCE = True
        elif arg.lower() == "-clearscreen":
            clr()
        elif arg.lower() == "-plextoken":
            if not isNextValue:
                isNextValue = True
                isNextValueID = 1
            else:
                print("ERROR: Invalid value for previous argument before " + arg)
                isError = True
                break
        elif arg.lower() == "-tmdbapikey":
            if not isNextValue:
                isNextValue = True
                isNextValueID = 2
            else:
                print("ERROR: Invalid value for previous argument before " + arg)
                isError = True
                break
        elif arg.lower() == "-baseurl":
            if not isNextValue:
                isNextValue = True
                isNextValueID = 3
            else:
                print("ERROR: Invalid value for previous argument before " + arg)
                isError = True
                break
        elif arg.lower() == "-library":
            if not isNextValue:
                isNextValue = True
                isNextValueID = 4
            else:
                print("ERROR: Invalid value for previous argument before " + arg)
                isError = True
                break
        else:
            if isNextValue:
                if isNextValueID == 1:
                    isNextValue = False
                    isNextValueID = -1
                    PLEX_TOKEN = arg
                elif isNextValueID == 2:
                    isNextValue = False
                    isNextValueID = -1
                    TMDB_API_KEY = arg
                elif isNextValueID == 3:
                    isNextValue = False
                    isNextValueID = -1
                    BASE_URL = arg
                elif isNextValueID == 4:
                    isNextValue = False
                    isNextValueID = -1
                    LIBRARY_NAME = arg
                else:
                    isError = True
                    print("ERROR: Unknown value {} ID on arguments".format(str, isNextValueID))
                    break
            else:
                isError = True
                print("ERROR: " + arg + " is unknown parameter ")
                break
    
    # only run if there are no error, help will be treated as error also
    # as we will only print help and not going to run the script        
    if not isError:
        # ensure that all the global variable is already filled before we run
        if len(PLEX_TOKEN) > 0 and len(TMDB_API_KEY) > 0 and len(BASE_URL) > 0 and len(LIBRARY_NAME) > 0:
            plex = connect()
            tmdb = connectToTMDB()
            getTvShow(plex, tmdb)
        else:
            print("ERROR: Please create .env files before run, or override using arguments")
