from google.cloud import firestore
import json
import requests
import base64

def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    # pubsub_message = base64.b64decode(event['data']).decode('utf-8')

    # here I should access the newsAPI and get the top 10 articles from the list of ten sources
    url = "https://newsapi.org/v2/top-headlines?" 
    url += "sources=bbc-news,cnn,cbc-news,bloomberg,fox-news,the-washington-post,time,newsweek,abc,independent" 
    url += "&pageSize=100" 
    url += "&apiKey=72d48922d4644d03bcda247a8ba59479"

    response = requests.get(url)

    json_response = response.json()
    print(json_response)

    try:
        
        db = firestore.Client()
        collection_name = "articleGroups"
        
        dic = {
                "title": "test", 
                "source": "test", 
                "url": "test",
                "description": "test",
                "content": "test",
                "date": "test"
                }

        db.collection(collection_name).add(dic)
        
        print("success")

    except Exception as e:
        
        print("error, somehthing was wrong with writting to the firesstore")
        print(e)

    # print(pubsub_message)

# command to run to deploy :
# gcloud functions deploy gatherData --runtime python37
