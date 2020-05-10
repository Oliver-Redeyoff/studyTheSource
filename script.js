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

        newHtml += "<h3 id='articleCount'>" + group.length + " similar articles</h3>"

        newHtml += "<div id='articleGroup'>"

        // this is each article in the group .urlToImage
        for(p in group){
            newHtml += '<div id="article" onclick="window.open(\'' + group[p].url + '\')">'
            newHtml += `
            <div id="title" style=\'background-image: url("` + group[p].urlToImage + `")\'>
                <div id="TopHalf">
                    <img src="Assets/` + group[p].source.id + `.png"></img>
                </div>
                <div id="BottomHalf">
                    <h2>` + group[p].title + `</h2>
                </div>
            </div>
            `

            if(group[p].content != null){
                newHtml += `
                <div id="content">
                    <p>` + group[p].content + `</p>
                </div>
                `
            } else {
                newHtml += `
                <div id="content">
                    <p>Click to view the article</p>
                </div>
                `
            }
            
            newHtml += "</div>"

        }

        newHtml += "</div>"


    }

    document.getElementById("bodyContainer").innerHTML = newHtml

}