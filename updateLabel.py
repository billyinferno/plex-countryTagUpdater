#/usr/bin/python3
from unittest import skip
from plexapi.server import PlexServer
from tmdbv3api import TMDb, TV
from dotenv import load_dotenv
from pprint import pprint
from tqdm import tqdm
from os import getenv, system, name
from time import sleep
import pycountry

# load the environment
TMDB_API_KEY = ''
BASE_URL = ''
PLEX_TOKEN = ''

def clr():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

def loadEnvFile():
    global TMDB_API_KEY
    global BASE_URL
    global PLEX_TOKEN
    load_dotenv()
    TMDB_API_KEY = getenv('TMDB_API_KEY')
    BASE_URL = getenv('BASE_URL')
    PLEX_TOKEN = getenv('PLEX_TOKEN')

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
    tvShows = plex.library.section('TV Shows').search(title=None,sort="titleSort:asc")
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

        if isLabelExists:
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
                
if __name__ == '__main__':
    loadEnvFile()
    plex = connect()
    tmdb = connectToTMDB()
    getTvShow(plex, tmdb)
