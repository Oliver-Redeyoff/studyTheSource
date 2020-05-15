from google.cloud import firestore
import json
import requests
import base64
from textblob import TextBlob
from bs4 import BeautifulSoup
import re


def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """

    min_word_length = 2
    stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", 
    "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", 
    "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", 
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", 
    "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", 
    "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", 
    "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", 
    "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", 
    "very", "'", "s", "t", "can", "will", "just", "don", "should", "now", "cnn", "bbc", "-"]

    def compareStrings(str1, str2):
        str1Words = str1.split(" ")
        str2Words = str2.split(" ")
        score = 0

        for word in str1Words:
            for word2 in str2Words:
                if len(word) > min_word_length and len(word2) > min_word_length:
                    if (word in word2) or (word2 in word):
                        score += 1
        
        return score

    url = "https://newsapi.org/v2/top-headlines?" 
    url += "sources=bbc-news,cnn,cbc-news,fox-news,the-washington-post,time,newsweek,abc,independent,msnbc"
    url += "&pageSize=100" 
    url += "&apiKey=72d48922d4644d03bcda247a8ba59479"

    # pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    

    # 1 - here I should access the newsAPI and get the top 10 articles from the list of ten sources
    print("getting data")
    response = requests.get(url)
    print("got data")
    data = response.json()

    articleGroups = []
    contentGroups = []

    sources = []
    sourceGroups = []
    filteredContent = []


    print("start of sorting article by source")
    # 2 - sort articles by their source and populate filteredContent
    for article in data['articles']:
        id = article['source']['id']
        temp = (str(article['title']) + " " + str(article['description']) + " " + str(article['content'])).lower()
        if id in sources:
            sourceGroups[sources.index(id)].append(article)
            filteredContent[sources.index(id)].append(temp)
        else:
            sources.append(id)
            sourceGroups.append([article])
            filteredContent.append([temp])
    print("end of sorting article by source")


    print("start of cleaning data")
    # 3 - iterate through filteredContent and remove stop words and clean data
    groupCounter = -1
    for group in filteredContent:
        groupCounter += 1
        index = -1
        for content in group:
            index += 1
            wordList = content.split()

            wordList  = [word for word in wordList if word.lower() not in stop_words]

            filteredContent[groupCounter][index] = " ".join(wordList)
    print("end of cleaning data")


    print("start of comparing articles")
    # 4 - compare articles with different sources to get pairs of similar articles
    for group1 in range(0, len(filteredContent)-1):
        # print("looking at the following list\n" + str(filteredContent[group1]))
        for content in filteredContent[group1]:

            for group2 in range(group1+1, len(filteredContent)):
                # print("comparing the following string\n" + content + "\nwith the following list\n" + str(filteredContent[group2]))
                for content2 in filteredContent[group2]:

                    score = compareStrings(content, content2)
                    minScore = min([len(content.split(" ")), len(content2.split(" "))])
                    lenDif = abs(len(content.split(" ")) - len(content2.split(" ")))
                    
                    # print(content)
                    # print(content2)
                    # print()

                    #and (minScore>8 and lenDif<20)
                    # I had this to check that two articles weren't very different lengths
                    if score > minScore and minScore > 8:
                        print("Found a pair, with score of " + str(score) + " and min score of " + str(minScore))
                        # print(content)
                        # print(content2)
                        # print()
                        contentGroups.append([content, content2])
                        articleGroups.append([
                            sourceGroups[group1][filteredContent[group1].index(content)],
                            sourceGroups[group2][filteredContent[group2].index(content2)]
                        ])
    print("end of comparing articles")


    print("start of joining database groups with articleGroups")
    # 6 - join groups in database with those in articleGroups
    try:
        db = firestore.Client()
        doc_ref = db.collection(u'articleGroups').document(u'groups')

        doc = doc_ref.get()
        dic = doc.to_dict()

        storedGroups = dic['groupArr']

        for groupStr in storedGroups:
            group = json.loads(groupStr)
            # print(group)
            articleGroups.append(group)
        
    except Exception as e:
        print("error with accessing the database groups")
    print("end of joining database groups with articleGroups")

    
    print("start of joining groups")
    # 7 - join groups that have common elements in articleGroups
    # new version checks if source id and title are same instead of whole json
    for group1 in range(0, len(articleGroups)):
        for group2 in range(0, len(articleGroups)):
            
            # don't join the same group with itself
            if group1 != group2:

                # compare each article from group1 to each one from group2
                for article1 in articleGroups[group1]:
                    for article2 in articleGroups[group2]:

                        # if they have a common source id and title, join
                        if (article1['source']['id']==article2['source']['id'] and article1['title']==article2['title']):

                            print("found common element")
                            # copy all elements from group1 that aren't in group2 and delete group1
                            for elementCopy in articleGroups[group1]:
                                if (elementCopy['source']['id']==article2['source']['id'] and elementCopy['title']==article2['title'])==False:
                                    articleGroups[group2].append(elementCopy)

                            articleGroups[group1] = []
                            break
    # old version checks whole json which would lead to duplications
    # for group1 in range(0, len(articleGroups)):
    #     for group2 in range(0, len(articleGroups)):
    #         # print("comparing group " + str(group1) + " and group " + str(group2))
    #         # don't join the same group with itself
    #         if group1 != group2:
    #             # if they have a common element, join
    #             for element in articleGroups[group1]:
    #                 if element in articleGroups[group2]:
    #                     print("found common element")
    #                     # copy all elements from group1 that aren't in group2 and delete group1
    #                     for elementCopy in articleGroups[group1]:
    #                         if (elementCopy in articleGroups[group2])==False:
    #                             articleGroups[group2].append(elementCopy)
    #                     # print(articleGroups[group1])
    #                     articleGroups[group1] = []
    #                     # print(articleGroups[group1])
    #                     break

    # remove any empty list that would remain
    articleGroups = [x for x in articleGroups if x!=[]]
    print("end of joining groups")


    print("start of sentiment analysis")
    # 8 - now that we know which articles we want, let's get the full content by scrapping the given url
    # then we perform a sentiment analysis using textBlob to get polarity and subjectivity if this hasn't been calculated already
    sentimentsCount = 0
    for group in articleGroups:
        for article in group:
            # if the sentiment of the article has not alerady been calculated, do that
            if "sentiment" not in article.keys():
                url = article['url']
                page = requests.get(url)
                print("got page")
                content = ""

                soup = BeautifulSoup(page.content, 'html.parser')
                parts = soup.find_all("p")
                for part in parts:
                    content += part.text
                print("got full content")

                blob = TextBlob(content)
                article["sentiment"] = [blob.sentiment.polarity, blob.sentiment.subjectivity]
                print("got sentiment")
                print("finished one article")
                sentimentsCount += 1
                break

        # this defines how many sentiment analysises to perform per call of the function since it takes much time    
        if sentimentsCount == 1:
            break

    print("end of sentiment analysis")

    # 9 - update database with new article groups
    if articleGroups!=[]:
        try:
            
            db = firestore.Client()

            doc_ref = db.collection('articleGroups').document('groups')
            doc = doc_ref.get()
            dic = doc.to_dict()

            groups = dic['groupArr']
            
            # now add all new elements to the database
            groups = []
            for group in articleGroups:
                groups.append(json.dumps(group))

            # if the list contains more than 20 articles then drop the old articles
            # at the end of the list
            if(len(groups) > 20):
                groups = groups[0:19]

            dic['groupArr'] = groups

            doc_ref.set(dic)

            # doc.update({u'list': firestore.ArrayUnion([u''+out])})
            
            print("success")

        except Exception as e:
            
            print("error, somehthing was wrong with writting to the firesstore")
            print(e)

    # print(pubsub_message)

# command to run to deploy :
# gcloud functions deploy gatherData --runtime python37
