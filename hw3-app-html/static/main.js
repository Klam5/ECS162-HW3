// https://developer.nytimes.com/docs/articlesearch-product/1/overview
// https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector


fetch("/api/news")
    .then(res => res.json())                                //Turns response into json format
    .then(data => {                                     //If data then...
        const articles = data.response.docs.slice(0,3); //Only takes 3 articles
        const cols = [
            document.querySelector(".left-col"),    //Selects mediaquery left col->rightcolumn
            document.querySelector(".mid-col"),
            document.querySelector(".right-col")
        ];

        articles.forEach((article, index) => {
            const col = cols[index];                //Set column to respective column
            const headline = article.headline.main; //Collects headline from current article object
            const snippet = article.snippet         //Collects snippet from current article object

            let imageUrl = null                     //Nulls imageurl just in case of no image
            //If multimedia object, if default, and if the default url, then there is an image available to process and put on our site 
            if(article.multimedia && article.multimedia.default && article.multimedia.default.url) {
                //Uses image url to attach to respective column and checks if default url starts with http
                imageUrl = article.multimedia.default.url.startsWith("http") ? article.multimedia.default.url: "https://nytimes.com/" + article.multimedia.default.url;
            }
            //Adds article into html format via imageurl, headline, and the snippet
            const articleHTML = `
                <h2>${headline}</h2>
                ${imageUrl ? `<img src="${imageUrl}" alt= "Da Image">` : ""}
                <p>${snippet}</p>
            `;
            //Puts the info from articleHTML into the HTML columns
            col.innerHTML = articleHTML;
        });
    })
    //IF there is an error display it
    .catch(error => {
        console.error('Error fetching data:', error);
    });

//Adds date via event listener
document.addEventListener("DOMContentLoaded", () => {
    //Grabs date info from document
    const date = document.getElementById("date");
    //today variable holds new date
    const today = new Date();
    //Formats the data
    const data = {
        weekday:    "long",
        year:       "numeric",
        month:      "long",
        day:        "numeric"
    }
    //formattedData holds locale date with numbers formatted by data
    const formattedDate = today.toLocaleDateString(undefined, data);
    //sets the textcontent
    date.textContent = `${formattedDate}`
})