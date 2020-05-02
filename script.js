// get sources from :
// bbc-news
// cnn
// fox-news
// abc
// cbc-news
// fox-news
// google-news
// independent
// msnbc
// newsweek
// the-washington-post
// time

var articles = []

var stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", 
"yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", 
"their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", 
"was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", 
"and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", 
"into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", 
"over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", 
"each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", 
"very", "'", "s", "t", "can", "will", "just", "don", "should", "now", "cnn", "bbc", "-"]

var url = "https://newsapi.org/v2/top-headlines?" 
    + "sources=bbc-news,cnn,cbc-news,bloomberg,fox-news,the-washington-post,time,newsweek,abc,independent" 
    + "&pageSize=100" 
    + "&apiKey=72d48922d4644d03bcda247a8ba59479";

var request = new XMLHttpRequest()

fetch(url, {
    mode: 'cors',
    method: "GET"
})
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        console.log(data)
        articles = data.articles
        compare_articles(articles)
    });



function compare_articles(data){

    var sources = []
    var contents = []
    var indexes = []
    var filteredContents = []

    for (article in data){

        var id = data[article].source.id
        var content = data[article].title + data[article].description + data[article].content

        if (sources.includes(id) == false){
            sources.push(id)
        }
        if (contents.length != sources.length){
            contents.push([])
            indexes.push([])
            filteredContents.push([])

            contents[sources.indexOf(id)].push(content)
            indexes[sources.indexOf(id)].push(article)
        } else {
            contents[sources.indexOf(id)].push(content)
            indexes[sources.indexOf(id)].push(article)
        }
    }

    // make a new list of contents with filters applyed
    for (titleGroup in contents){
        for (titleInd in contents[titleGroup]){
            
            // first make title lower case
            var newTitle = contents[titleGroup][titleInd].toLowerCase()
            // then remove stop words
            newTitle = removeStopWords(newTitle)

            filteredContents[titleGroup].push(newTitle)

        }
    }

    console.log(filteredContents)

    // now look at each combination of article and see if they are similar

    var articlePairs = []
    var dataPairs = []

    for(var source=0 ; source<(sources.length-1) ; source+=1){
        for (title in filteredContents){
            var out = compareArticles(filteredContents[source][title], filteredContents.slice(source+1, sources.length))
            if(out.length > 0){
                var index = []
                for(pair in out){
                    // articlePairs.push(out[pair])
                    // find the index of the second article
                    for(group in filteredContents){
                        console.log(filteredContents[group].indexOf(out[pair][1]))
                        if(filteredContents[group].indexOf(out[pair][1]) != -1){
                            index = [group, filteredContents[group].indexOf(out[pair][1])]
                        }
                    }
                    dataPairs.push( [ data[indexes[source][title]], data[indexes[index[0]][index[1]]] ] )
                }
            }
        }
    }

    console.log(dataPairs)

    var newHtml = ""
    // now populate ui
    for(pair in dataPairs){
        newHtml += "<div id='wrapper'>"
        for(element in dataPairs[pair]){
            newHtml += "<div id='wrapper2'><h2>" + dataPairs[pair][element].title + "<br><a>" + dataPairs[pair][element].source.name + "</a>" + "</h2>"
            if(dataPairs[pair][element].content != null){
                newHtml += "<p>" + dataPairs[pair][element].content + "</p></div>"
            } else {
                newHtml += "</div>"
            }
        }
        newHtml += "</div>"
    }

    document.getElementById("pairContainer").innerHTML = newHtml

}


// function just removes list of stop words from string passed in
function removeStopWords(txt){
    var expStr = stop_words.join("|");
	return txt.replace(new RegExp('\\b(' + expStr + ')\\b', 'gi'), '')
                    .replace(/\s{2,}/g, ' ');
}


// function compares an article with a stack of other articles, and returns a list of articles it is similar to
function compareArticles(article, stack){

    var pairs = []

    // stop article from being null
    article = ""+article

    for (group in stack){
        for (article2 in stack[group]){
            // console.log(stack[group][article2])
            var score = comparePhrases(article, stack[group][article2])
            var minLen = Math.min(article.split(" ").length, stack[group][article2].split(" ").length)

            if(score > minLen){
                console.log("these two articles are similar, with a score of " + score)
                console.log(article)
                console.log(stack[group][article2])
                console.log()
                pairs.push([article, stack[group][article2]])
            }
        }
    }

    return pairs

}


// returns similarity of two strings
function comparePhrases(str1, str2){

    str1 = ""+str1
    str2 = ""+str2

    score = 0

    // split the phrases into lists containing words
    strlists = [str1.split(" "), str2.split(" ")]
    listLengs = [strlists[0].length, strlists[1].length]
    // work out smallest and biggest list
    minIndex = listLengs.indexOf(Math.min.apply(null, listLengs))
    maxIndex = 1-minIndex

    for(var i1=0 ; i1<strlists[minIndex].length ; i1+=1){
        for(var i2=0 ; i2<strlists[maxIndex].length ; i2+=1){
            // if a word is very similar/identical to another then add to similarity score
            if(compareStr(strlists[minIndex][i1], strlists[maxIndex][i2])){
                score += 1
            }
        }
    }

    return score

}


function compareStr(str1, str2){
    // if both words are longer than 2 characters
    // see if the words are identical, or one contains the other

    if(str1.length > 2 && str2.length > 2){
        if(str1.includes(str2) || str2.includes(str1)){
            // console.log("comparing " + str1 + " and " + str2 + " returning True")
            return true
        }
    } 
    // console.log("comparing " + str1 + " and " + str2 + " returning False")
    return false
}