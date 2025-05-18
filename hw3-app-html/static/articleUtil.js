//Takes article object from API and builds the HTML to place on screen
function renderArticle(article, element) {
    //Grabs headline and snippet and for headline main, ? prevents a crash
    const headline = article.headline?.main || "No title available";
    const snippet = article.snippet || "No summary available";
    //Empty url
    let imageUrl = "";
    //If multimedia, add url
    if(article.multimedia && article.multimedia.length > 0) {
        imageUrl = "https://www.nytimes.com" + article.multimedia[0].url;
    }
    //Sets up article HTML to test with
    const articleHTML = `
        <h2>${headline}</h2>${imageUrl ? `<img src="${imageUrl}" alt="Da Image">` : ""}<p>${snippet}</p>
    `;
    //Saves in innerHTML
    element.innerHTML = articleHTML;
}

if(typeof module !== "undefined") {
    module.exports = {renderArticle}
}