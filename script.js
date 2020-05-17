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
        // to quick for this
        //document.getElementById("loadingText").innerHtml = 'Displaying articles <img id="loadingImg" src="Assets/loading.gif"></img>'
        display(data.groupArr)
    });

function display(data){

    var newHtml = ""

    console.log(data)

    if(data.length == 0){
        newHtml = "<p style='text-align: center;'>There is no content in the database</p>"
    }

    // this is each group of similar articles
    for(i in data){

        var group = JSON.parse(data[i])

        // now populate ui with articles in group
        newHtml += "<h3 id='articleCount' onclick='minimise(" + i + ")'>" + group.length + " similar articles</h3>"
        newHtml += "<div class='articleGroup'>"

        // this is each article in the group
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
                // get the content of the article and remove the +x chars at the end
                var cont = group[p].content
                for(var i=5 ; i<20 ; i++){
                    if(cont.charAt(cont.length-i)=='+' && cont.charAt(cont.length-i-1)=='['){
                        cont = cont.substring(0, cont.length-i-1)
                        break
                    }
                }
                // newHtml += `
                // <div id="content">
                //     <p>` + cont + `</p>
                // </div>
                // `
                if(group[p].hasOwnProperty('sentiment')){
                    polarity = group[p].sentiment[0]
                    console.log(polarity)
                    subjectivity = group[p].sentiment[1]
                    console.log(subjectivity)
                    // <label>Polarity : ` + (polarity*100).toFixed(2) + `%</label>
                    //     <div id="polarityBar">
                    //     <div id="negPolarityOuter"><div id="negPolarityInner" style="width:` + (polarity<0 ? (-polarity*100) : "0") + `%"></div></div>
                    //     <div id="posPolarityOuter"><div id="posPolarityInner" style="width:` + (polarity>0 ? polarity*100 : "0") + `%"></div></div>
                    // </div>
                    newHtml += `
                    <div id="content">
                    <label>Subjectivity : ` + (subjectivity*100).toFixed(2) + `%</label>
                    <div id="subjOuter"><div id="subjInner" style="width: ` + subjectivity*100 + `%"></div></div>
                    </div>
                    `
                }
            } else {
                // this is for articles that don't have content
                // newHtml += `
                // <div id="content">
                //     <p>Click to view the article</p>
                // </div>
                // `
            }
            newHtml += "</div>"
        }
        newHtml += "</div>"
    }
    document.getElementById("bodyContainer").innerHTML = newHtml

}

function minimise(index){
    groups = document.getElementsByClassName("articleGroup")
    console.log(groups[index].style.height)
    if(groups[index].style.height != "0px"){
        groups[index].style.height = "0px"
        groups[index].style.padding = "0px 20px 0px 20px"
    } else {
        groups[index].style.height = "auto"
        groups[index].style.padding = "30px 20px 20px 20px"
    }
}