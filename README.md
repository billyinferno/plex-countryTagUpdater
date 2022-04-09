## PLEX - TV Shows Country Label

This python script will update your labels metadata on your TV Shows at PLEX to add country of the TV shows based on the original country returned by TMDB for the shows.

In case tha there are no country configured on TMDB result, it will be skipped, and you can see the list of TV Shows that not being updated once the scan is finished.

## How to use?

1. Copy .example.env to .env
2. Edit .env and add all information needed there
3. ```python3 updateLabel.py```
