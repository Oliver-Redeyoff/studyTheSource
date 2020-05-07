// get sources from :
// bbc-news
// cnn
// fox-news
// abc
// cbc-news
// independent
// msnbc
// newsweek
// the-washington-post
// time

var articles = []

var url = "https://us-central1-comparethenews.cloudfunctions.net/articleGroups"

// var request = new XMLHttpRequest();
// request.open('GET', url, true);

// request.onload = function() {
//     console.log(this.response)
//     var data = JSON.parse(this.response);
//   }
// request.send();

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
        display(data.groupArr)
    });

function display(data){

    var newHtml = ""

    console.log(data)

    if(data.length == 0){
        console.log("no content")
        newHtml = "<p style='text-align: center;'>There is no content in the database</p>"
    }

    // this is each group of similar articles
    for(i in data){
        var group = JSON.parse(data[i])

        // now populate ui with 

        newHtml += "<div id='wrapper'>"

        // this is each article in the group
        for(p in group){
            newHtml += "<div id='wrapper2' onclick='window.open(\"" + group[p].url + "\")'>" 
            + "<img src='Assets/" + group[p].source.id + ".png'></img>"
            + "<h2>" + group[p].title + "</h2>"
            if(group[p].content != null){
                newHtml += "<p>" + group[p].content + "</p></div>"
            } else {
                newHtml += "</div>"
            }
        }

        newHtml += "</div>"


    }

    document.getElementById("pairContainer").innerHTML = newHtml

}