#/usr/bin/python3
'''
checkTVShow.py
--------------
created by : Adi Martha
https://github.com/billyinferno
'''

from plexapi.server import PlexServer
from tmdbv3api import TMDb, TV
from dotenv import load_dotenv
from pprint import pprint
from tqdm import tqdm
from os import getenv, path
from prettytable import PrettyTable
import sys

# global variable
TMDB_API_KEY = ''
BASE_URL = ''
PLEX_TOKEN = ''
LIBRARY_NAME = 'TV Shows'
SHOW_AVAILABLE = False
SHOW_EXCEPTION = False
plex = None
tmdb = None

# load environment file
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
    global tmdb
    print("🔗 Connect to TMDB")
    tmdb = TMDb()
    tmdb.api_key = TMDB_API_KEY

# connect to plex
def connectToPLEX():
    global plex
    print("🔗 Connect to PLEX Server (" + BASE_URL + ")")
    baseurl = BASE_URL
    token = PLEX_TOKEN
    plex = PlexServer(baseurl, token)

# fetch TV Shows and check how many season do we have
def getTvShow():
    # initialize result variable
    resultList = PrettyTable()
    resultList.field_names = ["Show", "Season", "Status"]
    resultList.align["Show"] = "l"
    resultList.align["Season"] = "l"
    resultList.align["Status"] = "c"

    # create TMDB TV Show instance
    tv = TV()

    # get all TV Shows from PLEX
    tvShows = plex.library.section(LIBRARY_NAME).search(title=None,sort="titleSort:asc")

    # loop thru the tvShows
    pBarShows = tqdm(tvShows)
    for show in pBarShows:
        pBarShows.set_description('{:50.50}'.format(show.title))
        seasonList = []
        tmdbId = ''

        # get the tmdbId
        guids = show.guids
        for guid in guids:
            if guid.id[0:4].lower() == "tmdb":
                tmdbId = guid.id[7:]

        item = plex.library.fetchItem(show.key)
        for season in item.seasons():
            seasonList.append(season.title)
        
        s = None
        if len(tmdbId) > 0:
            # we got actual TMDB ID so we can directly fetch the detail from TMDB
            s = tv.details(tmdbId)
        else:
            showSearch = tv.search(show.title)
            # if we search we need to parse and see whether the search result has same name or not?
            for result in showSearch:
                # check if the title is the same or not
                if(show.title.lower() == result.name.lower()):
                    # same title means that this is the show
                    s = result
                    # once found break from the loop
                    break
        
        if not s == None:
            # loop and check for season
            if hasattr(s, 'seasons'):
                for season in s.seasons:
                    # skip special season, and ensure there are episodes there
                    if season.season_number > 0 and season.episode_count > 0:
                        isSeasonFound = False
                        for currentSeason in seasonList:
                            if season.name.lower() == currentSeason.lower():
                                isSeasonFound = True
                        
                        if not isSeasonFound:
                            # we don't have this season print this
                            resultList.add_row([show.title, season.name, "🚫"])
                        else:
                            if SHOW_AVAILABLE:
                                resultList.add_row([show.title, season.name, "✔️"])
            else:
                if SHOW_EXCEPTION:
                    resultList.add_row([show.title, season.name, "⚠️"])
        else:
            if SHOW_EXCEPTION:
                resultList.add_row([show.title, season.name, "❗"])
    
    print(resultList)

def printHelp():
    helpString = """
    Plex - TV Show Season Checker
    -----------------------------
    This script will perform scan on your PLEX TV Shows library, and search on
    TMDB based on ID (if exists), or show name on TMDB.

    Once result from TMDB found, it will parse the number of Season of the TV
    Shows have and compare with the one on your library, and put the result
    which Season is missing from your TV Shows library.

    NOTE: Before you run the script, ensure to create .env file to run script
    without any arguments, or you can override the .env with arguments.

    Supported Arguments:
    (*) -showavailable
         This will add the Season that already available in your TV Shows
         library to the result
    (*) -showexception
         This will show the TV Shows that not found in TMDB (❗) or don't have
         any season information (⚠️) on TMDB
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

if __name__ == "__main__":
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
        elif arg.lower() == "-showavailable":
            SHOW_AVAILABLE = True
        elif arg.lower() == "-showexception":
            SHOW_EXCEPTION = True
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
    
    if not isError:
        # connect to PLEX and TMDB
        if len(PLEX_TOKEN) > 0 and len(TMDB_API_KEY) > 0 and len(BASE_URL) > 0 and len(LIBRARY_NAME) > 0:
            connectToPLEX()
            connectToTMDB()
            getTvShow()
        else:
            print("ERROR: Environment variables is not complete")
