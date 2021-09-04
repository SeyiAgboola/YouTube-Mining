# YouTube Mining

This repo contains code that will allow you to extract statistics on YouTube Videos by pulling the metadata from the YouTube API via Python.

Before you start you will need YouTube Dev Authentication which you can get via Google Developer Console: https://developers.google.com/youtube/registering_an_application

If you want look at the official documentation of YouTube API using Python, you can go to: https://developers.google.com/youtube/v3/docs/.

There are two main blocks of code:
* YouTube API Extraction Based on a specific Search Query (youtube_search.py)
* YouTube URL Extraction from Reddit Submissions (YouTube Views and Reddit Scores from Text.py)

The second block of code is tailored for pulling YouTube links from submissions on /r/Games so you will need to tailor it to your own purposes. But I am an entry level Python programmer so my code is as basic as it gets.
