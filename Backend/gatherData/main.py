from google.cloud import firestore
import json
import base64

def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')

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
        
        db.collection(collection_name).doc().set(dic)
        
        print("succes")

    except Exception:
        
        print("error, somehthing was wrong with writting to the firesstore")

    print(pubsub_message)

# command to run to deploy :
# gcloud functions deploy gatherData --runtime python37
