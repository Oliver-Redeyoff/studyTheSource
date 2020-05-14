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

    # here I should access the newsAPI and get the top 10 articles from the list of ten sources
    print("getting data")
    response = requests.get(url)
    print("got data")
    print()
    data = response.json()

    articleGroups = []
    contentGroups = []

    sources = []
    sourceGroups = []
    filteredContent = []

    # first sort articles by there source and populate filteredContent with initial content
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

    # print(filteredContent[0])

    # for debugging to limit amount of data processed
    # filteredContent = filteredContent[0:2]


    # now iterate through filteredContent and remove stop words to clean data
    groupCounter = -1
    for group in filteredContent:
        groupCounter += 1
        index = -1
        for content in group:
            index += 1
            wordList = content.split()

            wordList  = [word for word in wordList if word.lower() not in stop_words]

            filteredContent[groupCounter][index] = " ".join(wordList)


    # now compare articles to get pairs of similar articles

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
                    if score > minScore and minScore > 6:
                        print("Found a pair, with score of " + str(score) + " and min score of " + str(minScore))
                        # print(content)
                        # print(content2)
                        # print()
                        contentGroups.append([content, content2])
                        articleGroups.append([
                            sourceGroups[group1][filteredContent[group1].index(content)],
                            sourceGroups[group2][filteredContent[group2].index(content2)]
                        ])


    # for debugging merging section
    # articleGroups = [[{'source': {'id': 'fox-news', 'name': 'Fox News'}, 'author': 'Fox News', 'title': 'Georgia grand jury review recommended in fatal shooting of Ahmaud Arbery, Biden weighs in', 'description': 'A Georgia\xa0prosecutor on Tuesday recommended that a grand jury review\xa0the fatal shooting of a black man who friends say was out for a jog at the time he was killed.', 'url': 'https://www.foxnews.com/us/georgia-grand-jury-review-recommended-in-fatal-shooting-of-ahmaud-arbery', 'urlToImage': 'https://static.foxnews.com/foxnews.com/content/uploads/2020/04/Police-Tape-Line-iStock.jpg', 'publishedAt': '2020-05-06T08:07:20.6409854Z', 'content': 'A Georgia\xa0prosecutor on Tuesday recommended that a grand jury review\xa0the fatal shooting of a black man who friends say was out for a jog at the time he was killed.\r\nThe investigation into the fatal shooting of\xa0Ahmaud Arbery, 25, in February\xa0has been criticize… [+3178 chars]'}, {'source': {'id': 'bbc-news', 'name': 'BBC News'}, 'author': 'BBC News', 'title': "Biden demands justice for black jogger's killing", 'description': 'Ahmaud Arbery, a 25-year-old black man, was confronted by an ex-policeman and his son while jogging.', 'url': 'http://www.bbc.co.uk/news/world-us-canada-52557609', 'urlToImage': 'https://ichef.bbci.co.uk/news/1024/branded_news/4304/production/_112165171_061006061-1.jpg', 'publishedAt': '2020-05-06T10:28:18Z', 'content': 'Image copyrightReutersImage caption\r\n Joe Biden: "The video is clear: Ahmaud Arbery was killed in cold blood"\r\nThe Democrats\' likely presidential candidate Joe Biden has demanded justice over the killing of an unarmed black man in the US state of Georgia.\r\nMr… [+3728 chars]'}], [{'source': {'id': 'bbc-news', 'name': 'BBC News'}, 'author': 'BBC News', 'title': "Biden demands justice for black jogger's killing", 'description': 'Ahmaud Arbery, a 25-year-old black man, was confronted by an ex-policeman and his son while jogging.', 'url': 'http://www.bbc.co.uk/news/world-us-canada-52557609', 'urlToImage': 'https://ichef.bbci.co.uk/news/1024/branded_news/4304/production/_112165171_061006061-1.jpg', 'publishedAt': '2020-05-06T10:28:18Z', 'content': 'Image copyrightReutersImage caption\r\n Joe Biden: "The video is clear: Ahmaud Arbery was killed in cold blood"\r\nThe Democrats\' likely presidential candidate Joe Biden has demanded justice over the killing of an unarmed black man in the US state of Georgia.\r\nMr… [+3728 chars]'}, {'source': {'id': 'fox-news', 'name': 'Fox News'}, 'author': 'Fox News', 'title': 'Georgia grand jury review recommended in fatal shooting of Ahmaud Arbery, Biden weighs in', 'description': 'A Georgia\xa0prosecutor on Tuesday recommended that a grand jury review\xa0the fatal shooting of a black man who friends say was out for a jog at the time he was killed.', 'url': 'https://www.foxnews.com/us/georgia-grand-jury-review-recommended-in-fatal-shooting-of-ahmaud-arbery', 'urlToImage': 'https://static.foxnews.com/foxnews.com/content/uploads/2020/04/Police-Tape-Line-iStock.jpg', 'publishedAt': '2020-05-06T08:07:20.6409854Z', 'content': 'A Georgia\xa0prosecutor on Tuesday recommended that a grand jury review\xa0the fatal shooting of a black man who friends say was out for a jog at the time he was killed.\r\nThe investigation into the fatal shooting of\xa0Ahmaud Arbery, 25, in February\xa0has been criticize… [+3178 chars]'}]]


    # Here join groups in database with those in articleGroups
    try:
        db = firestore.Client()
        doc_ref = db.collection(u'articleGroups').document(u'groups')

        doc = doc_ref.get()
        dic = doc.to_dict()

        storedGroups = dic['groupArr']

        for groupStr in storedGroups:
            group = json.loads(groupStr)
            print(group)
            articleGroups.append(group)
        
    except Exception as e:
        print("error with accessing the database groups")

    # print(articleGroups)
        
    # Join pairs that have common elements, should also add current groups that are in the database
    for group1 in range(0, len(articleGroups)):
        for group2 in range(0, len(articleGroups)):
            # print("comparing group " + str(group1) + " and group " + str(group2))
            # don't join the same group with itself
            if group1 != group2:
                # if they have a common element, join
                for element in articleGroups[group1]:
                    if element in articleGroups[group2]:
                        print("found common element")
                        # copy all elements from group1 that aren't in group2 and delete group1
                        for elementCopy in articleGroups[group1]:
                            if (elementCopy in articleGroups[group2])==False:
                                articleGroups[group2].append(elementCopy)
                        # print(articleGroups[group1])
                        articleGroups[group1] = []
                        # print(articleGroups[group1])
                        break

    # finally remove any empty list that would remain
    articleGroups = [x for x in articleGroups if x!=[]]

    # print(articleGroups)
    # out = json.dumps(articleGroups)
    # print()
    # print(type(out))

    # print(articleGroups)

    if articleGroups!=[]:
        try:
            
            db = firestore.Client()

            doc_ref = db.collection('articleGroups').document('groups')
            doc = doc_ref.get()
            dic = doc.to_dict()

            groups = dic['groupArr']

            # dic['stringGroups'] = out

            # remove any element from the new list that is already in the database
            # for groupInDatab in groups:
            #     group = json.loads(groupInDatab)
            #     if(group in articleGroups):
            #         articleGroups.remove(group)
            
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
