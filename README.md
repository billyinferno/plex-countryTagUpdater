## PLEX - TV Shows Country Label

This python script will update your labels metadata on your TV Shows at PLEX to add country of the TV shows based on the original country returned by TMDB for the shows.

In case tha there are no country configured on TMDB result, it will be skipped, and you can see the list of TV Shows that not being updated once the scan is finished.

## How to use?

1. Copy .example.env to .env
2. Edit .env and add all information needed there
3. ```python3 updateLabel.py```


### Arguments

In case you didn't want to use .env file you can also passing arguments to the script

* ```-force```

    this will force update the TV shows that already have country label

* ```-clearscreen```

    clear the screen before run

* ```-plextoken```

    your PLEX token that will be used to connect to your PLEX server

* ```-tmdbapikey```

    your TMDB API Key that will be used to get information from TMDB

* ```-baseurl```

    your PLEX url (eg. 127.0.0.1:32400)

* ```-library```
    Your TV Shows library name, usually it will be defaulted as "TV Shows"