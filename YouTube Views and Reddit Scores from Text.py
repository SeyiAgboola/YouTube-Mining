import praw
import redcreds as creds
import time
import sys
import ytcreds

#Set up YouTube credentials
DEVELOPER_KEY = ytcreds.dev
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

import datetime
from apiclient.discovery import build

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)

#Set up Reddit Credentials
r = praw.Reddit(username = creds.username,
            password = creds.password,
            client_id = creds.client_id,
            client_secret = creds.client_secret,
            user_agent = creds.user_agent)

#
def get_conference(x):
    # x = row in publisher_threads['Post ID']
    post = r.submission(id=x)
    body = post.selftext
    title = post.title
    lines = body.split("\n\n") #split body of text into a list of individual lines
    
    #Assign variables to store links and ids
    youtube_links = []
    youtube_ids = []
    reddit_links = []
    reddit_ids = []
    
    #Each line in the Reddit post that has been split into a list of lines
    for line in lines:
        search_youtube = re.search(".+youtube.+", line)
        search_reddit = re.search(".+reddit.+", line)
        #If a YouTube Url append to youtube_links 
        if search_youtube:
                youtube_group = search_youtube.group(0)
                youtube_links.append(youtube_group)
                #append IDs from youtube_links to youtube_ids
                for link in youtube_links:
                    search_ytid = re.search("v=.{11}", link)
                    group_ytid = search_ytid.group(0)
                    group_ytid = group_ytid.replace("v=","")
                    youtube_ids.append(group_ytid)
        #Same but for reddit IDs            
        elif search_reddit:
            reddit_group = search_reddit.group(0)
            reddit_links.append(reddit_group)
            for link in reddit_links:
                search_rdid = re.search("\/.{6}\/", link)
                try:
                    group_rdid = search_rdid.group(0)
                    group_rdid = group_rdid.replace("/","")
                    reddit_ids.append(group_rdid)
                except AttributeError:
                    pass
    #Return the Reddit Post ID, it's reddit ids and youtube ids found in the body of post submission            
    return title, reddit_ids, youtube_ids

reds_yts_conf = []

#turn publisher_threads into list
publisher_postids = publisher_threads['Post ID'].tolist() #list of post ids
publisher_conf_titles = publisher_threads['Title'].tolist() #list of post titles
#for publisher post in list, return relevant_reddits, relevant_youtubes

#----------------------------------------------
#Function takes each Reddit Post ID from list of Publisher Threads and creates a dictionary of Reddit/YouTube IDs found in each Thread
#Each Dictionary is appended to list for ALL Publisher Threads link dictionaries
for post in publisher_postids:
    try:
        #create a new dictionary
        entry = {}
        #add the values
        entry['Conf_Title'], entry['Conf_Reddits'], entry['Conf_YouTubes'] = get_conference(post)
        #append to list
        reds_yts_conf.append(entry)
    except TypeError:
        print("TypeError with " + str(post))
        pass
    

#-------------------------------- The Juicy part--------------------------------------#
#-------------Build YouTube Search------------#
    #Function uses YouTube Video ID to return no. of views
def get_views(postid):
    fixed_id = str(postid).replace("v=","")
    search_response = youtube.videos().list(
        id=fixed_id,
        part="snippet,statistics").execute()
    if search_response != None:#if video id search doesn't return a Nonetype
        try:
            items = search_response['items'] #50 results
            title = items[0]['snippet']['title']
            views_count = int(items[0]['statistics']['viewCount']) #Incase it returns a float, we make sure all results are integers
        except IndexError:
            views_count = 0
    else:
        views_count = 0
    #Test Function
    return title, views_count #, like_sum

#For each publisher thread's dictionary
for entry in reds_yts_conf:
    #Use reddits to add up upvotes
    total_score = 0 #Total Reddit Score
    reddit_pielist = []
    #For each reddit ID in that Publisher Dictionary
    for reddit_post in entry['Conf_Reddits']:
        reddit_pieDict = {} 
        try:
            post = r.submission(id=reddit_post)
            title = post.title
            score = int(post.score)
            reddit_pieDict['Title'] = title
            reddit_pieDict['Score'] = score #Store score separately
            reddit_pielist.append(reddit_pieDict)
            total_score+=score #Add to overall score for that Publisher Thread
        except:
            time.sleep(120)
            try:
                post = r.submission(id=reddit_post)
                title = post.title
                score = int(post.score)
                reddit_pieDict['Title'] = title
                reddit_pieDict['Score'] = score
                reddit_pielist.append(reddit_pieDict)
                total_score+=score
            except:
                reddit_pieDict['Title'] = "failed"
                reddit_pieDict['Score'] = "failed"
                reddit_pielist.append(reddit_pieDict)
                
    #Update that publisher dictionary's total scores and score breakdowns
    entry['Total Score'] = total_score
    entry['Score Breakdown'] = reddit_pielist
    
    #Use YouTube search to calculate total views
    total_views = 0
    youtube_pielist = []
    for vid in entry['Conf_YouTubes']:
        try:
            youtube_pieDict = {}
            title, views = get_views(vid)
            youtube_pieDict['Views'] = views
            youtube_pieDict['Video Title'] = title
            youtube_pielist.append(youtube_pieDict)
            total_views+=views
        except ConnectionAbortedError:
            time.sleep(120)
            try:
                youtube_pieDict = {}
                title, views = get_views(vid)
                youtube_pieDict['Views'] = views
                youtube_pieDict['Video Title'] = title
                youtube_pielist.append(youtube_pieDict)
                total_views+=views
            except ConnectionAbortedError:
                time.sleep(120)
                try:
                    youtube_pieDict = {}
                    title, views = get_views(vid)
                    youtube_pieDict['Views'] = views
                    youtube_pieDict['Video Title'] = title
                    youtube_pielist.append(youtube_pieDict)
                    total_views+=views
                except ConnectionAbortedError:
                    views = 0
                    total_views = "Failed"
                    
    entry['Total Views'] = total_views
    entry['Views Breakdown'] = youtube_pielist

#Turn our list of Dictionaries into a Dataframe        
related_posts = pd.DataFrame(reds_yts_conf)
#Combine our original publisher threads with their combined views and scores
new_publishers_data = pd.concat([publisher_threads, related_posts], axis=1)
