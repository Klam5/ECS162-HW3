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

            const rawId = article._id;
            const articleId = rawId.replace(/"/g, "&quot;").replace(/\//g, "-");


            let imageUrl = null                     //Nulls imageurl just in case of no image
            //If multimedia object, if default, and if the default url, then there is an image available to process and put on our site 
            if(article.multimedia && article.multimedia.default && article.multimedia.default.url) {
                //Uses image url to attach to respective column and checks if default url starts with http
                imageUrl = article.multimedia.default.url.startsWith("http") ? article.multimedia.default.url: "https://nytimes.com/" + article.multimedia.default.url;
            }
            //Adds article into html format via imageurl, headline, and the snippet
            const articleHTML = `
                <div class="articlewrap" data-article-id=${articleId}>
                    <h2>${headline}</h2>
                    ${imageUrl ? `<img src="${imageUrl}" alt= "Da Image">` : ""}
                    <p>${snippet}</p>
                    <button class='commentbuttn'>
                        <span class="comment-count">Comments</span>
                    </button>
                </div>
            `;
            console.log("rendering: ", articleId)
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
    //Gets elements for sidebars ands buttons
    const sidebar = document.getElementById("account-sidebar");
    const accountBtn = document.getElementById("account-btn");
    const closeBtn = document.getElementById("close-sidebar");
    const commentSidebar = document.getElementById("comment-sb");
    const closeCommentSidebar = document.getElementById("close-commentsb");
    //If account button pressed, show it 
    if(accountBtn) {
        accountBtn.addEventListener("click", () => {
            sidebar.classList.remove("hidden");
        });
    }
    //If close button pressed, hide sidebar 
    if(closeBtn) {
        closeBtn.addEventListener("click", () => {
            sidebar.classList.add("hidden");
        })
    }
    //Shows the sidebar when comment buttons are clicked
    document.body.addEventListener("click", function (event) {
        if(event.target.closest(".commentbuttn")) {
            commentSidebar.classList.remove("hidden");
        }
    });
    //Closes comment sidebar when clicked x
    if(closeCommentSidebar) {
        closeCommentSidebar.addEventListener("click", () => {
            commentSidebar.classList.add("hidden");
        });
    }
});
//Asyncronously loads comments given articleID
async function loadComments(articleId) {
    //Awaits for fetching comments 
    const res = await fetch(`/api/comments?article_id=${encodeURIComponent(articleId)}`);
    const comments = await res.json();
    const commentList = document.querySelector(".comments-list"); //Lists comments
    commentList.innerHTML = ""; //Clearscomment list
    
    // if (!Array.isArray(comments)) {
    //     commentList.innerHTML = "<p>Error Loading Comments</p>"
    //     return
    // }
    //If no comments, displays no comments
    if(comments.length === 0) {
        commentList.innerHTML = "<p>No Comments Yet</p>";
        return;
    }
    //Renders all the comments by creating and displaying
    comments.forEach(comment => {
        const p = document.createElement("p");
        //If owner or mod, set to email or moderator@hw3.com
        const isOwner = comment.user_email === window.CURRENT_USER.email;
        const isMod = window.CURRENT_USER.email === "moderator@hw3.com";
        //Comment HTML
        p.innerHTML = `
            <span>
                <strong>${comment.user_email || "anonymous"}:</strong>
            </span>
            <span class="comment-text">${comment.content}</span>
            ${(isOwner || isMod) ? `<button class = "delete-comment" data-comment-id="${comment._id}">Delete</button>`: ""}
        `;
        //Adds comment to the list
        commentList.appendChild(p);
    })
    //Delete comment functionality
    document.querySelectorAll(".delete-comment").forEach(button => {
        button.addEventListener("click", async () => {
            const commentId = button.getAttribute("data-comment-id");
            const confirmDelete = confirm("Delete this comment?");
            if (!confirmDelete) return;
    
            const res = await fetch(`/api/comments/${commentId}`, {
                method: "DELETE"
            });

            const result = await res.json();
            alert(result.message || result.error);

            if (res.ok) loadComments(articleId);
        });
    });
}
//Click on any document bodies
document.body.addEventListener("click", function(event){
    const commentButton = event.target.closest(".commentbuttn");
    //If comment button pressed
    if(commentButton) {
        const commentSidebar = document.getElementById("comment-sb");
        commentSidebar.classList.remove("hidden"); //Removes hidden to show comment sidebar
        //Gets article respective to comments
        const articleId = commentButton.closest(".articlewrap").getAttribute("data-article-id");
        document.getElementById("article-id").value = articleId;
        //loads comments for article
        loadComments(articleId)
    }
})
//Adds a new comment
document.getElementById("comment-form").addEventListener("submit", async(e) => {
    e.preventDefault(); //Stops default form submit behavior
    const articleId = document.getElementById("article-id").value;  //Gets respective article id
    const commentText = document.getElementById("comment-text").value;  //Gets comment content
    //Sends comment data to backend
    const res = await fetch("/api/comments", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            article_id: articleId,
            content: commentText
        })
    });
    const result = await res.json();
    alert(result.message || result.error);  //Shows response method
    if(res.ok) {
        document.getElementById("comment-text").value = "";
        loadComments(articleId)
    }
});