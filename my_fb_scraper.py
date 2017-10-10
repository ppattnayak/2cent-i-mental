import json
import datetime
import csv
import time
import os
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib import urlopen, Request
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


APP_id = "xxxxxxxxxxxxxx"
APP_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # DO NOT SHARE WITH ANYONE!
page_id = "cnn"
#edit the days to weeks or months for date difference and cutoff date generation
cutoff_date = datetime.datetime.now() - datetime.timedelta(hours=1)
cutoff_date = cutoff_date.isoformat()

json_pagedata = []
comment_data = []

def create_url(graph_url, APP_id, APP_secret):
    post_arg = "/posts/?key=value&access_token=" + APP_id + "|" + APP_secret
    post_url = graph_url + post_arg

    return post_url

def render_json(post_url):
    web_response = urlopen(post_url)
    #print(post_url)
    read_page = web_response.read()
    json_pagedata = json.loads(read_page)

    return json_pagedata

def render_no_of_likes(post_id, APP_id, App_secret):
    graph_url = "https://graph.facebook.com/" + str(post_id)
    likes_arg = "/likes?summary=true&key=value&access_token=" + APP_id + "|" + APP_secret
    likes_url = graph_url + likes_arg
    #print(likes_url)
    likes_json = render_json(likes_url)
    count = likes_json["summary"]["total_count"]
    #count no of likes
    #print(count)
    return count
    #render_no_of_likes('5550296508_10157262626676509', APP_id,APP_secret)

    #function to create url to call API to return comment data for posts
def comment_url_creation(post_id, APP_id, APP_secret):
    graph_url = "https://graph.facebook.com/" + str(post_id)
    comments_arg = "/comments/?key=value&access_token=" + APP_id + "|" + APP_secret
    comments_url = graph_url + comments_arg
    # print(likes_url)
    return comments_url

def get_comments_of_post(post_id,post,APP_id, APP_secret, comments_url, post_likes):
    comment = render_json(comments_url)["data"]
    post_total_likes = post_likes
    for msg in comment:
        try:
            current_comments = [post_id, post["message"], msg["from"]["name"], msg["message"], msg["created_time"], post_total_likes]
            comment_data.append(current_comments)
        except:
            current_comments = ["error", "error", "error", "error", "error"]

    try:
        next_page = comment["paging"]["next"]
    except Exception:
        next_page = None

    if next_page is not None:
        get_comments_of_post(post_id, post, APP_id, APP_secret,next_page,post_total_likes)
    else:
        return comment_data


def scrape_posts_multiple_pages_by_date(post_url, date, json_pagedata):
    page_postobj = render_json(post_url)
    next_page = page_postobj["paging"]["next"]
    page_postobj = page_postobj["data"]
    collecting = True
    comments_data=[]
    for post in page_postobj:
        try:
            likes_count = render_no_of_likes(str(post["id"]),APP_id,APP_secret)
            comments_url = comment_url_creation(str(post["id"]), APP_id, APP_secret)
            comments_data = get_comments_of_post(str(post["id"]),post,APP_id,APP_secret,comments_url, likes_count)
            current_post = [post["id"],post["message"],post["created_time"],likes_count]
        except:
            current_post = ["error", "error", "error", "error"]

        if current_post[2] != "error":
            #compare the date range
            if date < current_post[2]:
                json_pagedata.append(current_post)
                print("Collecting from posts")
            elif date > current_post[2]:
                print("Done Collecting")
                collecting = False
                break
    if collecting == True:
        scrape_posts_multiple_pages_by_date(next_page, date, json_pagedata)

    return comments_data



def main():
    graph_url = "https://graph.facebook.com/" + page_id

    #extract post data from a page
    post_url = create_url(graph_url,APP_id,APP_secret)
    json_pagedata = []
    comments_data = []
    #json_pagedata = scrape_posts_multiple_pages_by_date(post_url,cutoff_date,json_pagedata)
    comments_data = scrape_posts_multiple_pages_by_date(post_url,cutoff_date,json_pagedata)

    # with open("fb_post_comment_sentiment_analysis.csv", 'w') as resultFile:
    #     wr = csv.writer(resultFile, dialect='excel')
    #     wr.writerows(comments_data)
    #print(comments_data)
    #iterate through each post made by the page and return id and message for the posts
    with open("fb_post_comment_sentiment_analysis.csv", 'w') as resultFile:
        wr = csv.writer(resultFile, dialect='excel')
        wr.writerow(['post_id','post_message','user_name','comment','comment_date','post_likes','sentiment_score'])
    for post in comments_data:

        try:
            # print(post[0])
            # print(post[1])
            # print(post[2])
            # print(post[3])
            # print(post[4])
            # print(post[5])
            # otpt = post[0]+"|"+post[1]+"|"+post[2]+"|"+post[3]+"|"+post[4]+"|"+post[5]
            #print(post[0], "|", post[1], "|", post[2], "|", post[3], "|", post[4], "|", post[5])
            #print(post)

            #Sentiment Analysis using VADER
            analyser = SentimentIntensityAnalyzer()
            vs = analyser.polarity_scores(post[3])
            post = [post[0],post[1],post[2],post[3],post[4],post[5],str(vs["compound"])]
            #print(post[0], "|", post[1], "|", post[2], "|", post[3], "|", post[4], "|", post[5], "|", post[6])
            print(post)
            with open("fb_post_comment_sentiment_analysis.csv",'a') as resultFile:
                wr = csv.writer(resultFile, dialect='excel')
                wr.writerow(post)
        except:
            print("oops")
    # comment_data = comments_data
    # os.system('get_Sentiment_Score.py')

if __name__ == "__main__":
    main()




