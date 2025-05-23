from flask import Flask, jsonify, redirect, render_template, session, request, url_for
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
from flask_cors import CORS
import os
import requests #sends requests
import json
from dotenv import load_dotenv  #loads env file
from bson.objectid import ObjectId
import pymongo
from pymongo import MongoClient

# dont know if needed
from dotenv import load_dotenv

# from flask_oidc import OpenIDConnect
# import pymongo
# from pymongo import MongoClient
# from functools import wraps
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
NYT_API_KEY = os.getenv("NYT_API_KEY")      #gets api key from .env


oauth = OAuth(app)

nonce = generate_token()


oauth.register(
    name=os.getenv('OIDC_CLIENT_NAME'),
    client_id=os.getenv('OIDC_CLIENT_ID'),
    client_secret=os.getenv('OIDC_CLIENT_SECRET'),
    #server_metadata_url='http://dex:5556/.well-known/openid-configuration',
    authorization_endpoint="http://localhost:5556/auth",
    token_endpoint="http://dex:5556/token",
    jwks_uri="http://dex:5556/keys",
    userinfo_endpoint="http://dex:5556/userinfo",
    device_authorization_endpoint="http://dex:5556/device/code",
    client_kwargs={'scope': 'openid email profile'}
)

@app.route('/')
def home():
    user = session.get('user')
    return render_template("index.html", user=user)
    #if user:
    #    return f"<h2>Logged in as {user['email']}</h2><a href='/logout'>Logout</a>"
    #return '<a href="/login">Login with Dex</a>'

#@app.route('/api/key')
#def get_key():
#    return jsonify({'apiKey': os.getenv('NYT_API_KEY')})

@app.route('/login')
def login():
    session['nonce'] = nonce
    redirect_uri = 'http://localhost:8000/authorize'
    client = oauth.create_client(os.getenv("OIDC_CLIENT_NAME"))
    return client.authorize_redirect(redirect_uri, nonce=nonce)
    #return oauth.dex.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/authorize')
def authorize():
    # load_dotenv()
    # uri = os.getenv("URI")
    # cluster = MongoClient(uri)
    # db = cluster["users"]
    # reg_user_collection = db["regular"]
    # admin_user_collection = db["admins"]

    client = oauth.create_client(os.getenv("OIDC_CLIENT_NAME"))
    token = client.authorize_access_token()
    nonce = session.get('nonce')

    user_info = client.parse_id_token(token, nonce=nonce)  # or use .get('userinfo').json()
    session['user'] = user_info
    # email = user_info.get("email")

    # if not email:
    #     return "Email not provided"
    
    # is_admin = admin_user_collection.find_one({"email": email})
    # is_reg = reg_user_collection.find_one({"email": email})
    # if not is_admin and not is_reg:
    #     if email.endswith("@moderator.com"):
    #         admin_user_collection.insert_one({
    #             "email": email
    #         })
    #     else:
    #         reg_user_collection.insert_one({
    #             "email": email
    #         })
    # else:
    #     session['user']['role'] = 'admin' if is_admin else 'regular'
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


uri = os.getenv("URI")
cluster = MongoClient(uri)
db = cluster["Comments"]
comments_collection = db["comments"]

@app.route('/api/comments', methods=["POST"])
def add_comment():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"})
    data = request.json
    article_id = data.get("article_id")
    content = data.get("content")
    # if not article_id or not content:
    #     return jsonify({"error": "Missing Data"})
    comment = {
        "article_id": article_id,
        "content": content,
        "user_email": session["user"]["email"]
    }
    comments_collection.insert_one(comment)
    return jsonify({"message": "Comment Posted"})

@app.route("/api/comments", methods=["GET"])
def get_comments():
    article_id = request.args.get("article_id")
    comment_list = list(db["comments"].find({"article_id": article_id}))
    for c in comment_list:
        c["_id"] = str(c["_id"])
    return jsonify(comment_list)

@app.route('/api/comments/<comment_id>', methods=["DELETE"])
def delete_comment(comment_id):
    user = session.get("user", {})
    email = user.get("email")
    if not email:
        return jsonify({"error": "Unauthorized"})
    
    comment = comments_collection.find_one({"_id": ObjectId(comment_id)})
    if not comment:
        return jsonify({"error": "Comment not Found"})
    is_owner = comment["user_email"] == email
    is_mod = email == "moderator@hw3.com"

    if not is_owner and not is_mod:
        return jsonify({"error": "Forbidden"})
    
    result = comments_collection.delete_one({"_id": ObjectId(comment_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Comment deleted"})
    else:
        return jsonify({"error": "Failed to Delete Message"})
    # if email != "moderator@hw3.com":
    #     return jsonify({"error": "Unauthorized"})
    
    # result = comments_collection.delete_one({"_id": ObjectId(comment_id)})
    # if result.deleted_count == 1:
    #     return jsonify({"message": "Comment Deleted"})
    # else:
    #     return jsonify({"error": "Comment not found"})
# https://flask.palletsprojects.com/en/stable/quickstart/
# https://flask.palletsprojects.com/en/stable/api/#flask.jsonify
# https://developer.nytimes.com/docs/articlesearch-product/1/overview

#@app.route('/')                             #Sets up root URL
#def home():
#    return render_template("index.html")    #renders index.html template

@app.route('/api/news')                     #apinews route used by js
def news():
    #Base url for NYT article searchapi
    url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    #Search Paramaters to control article searching 
    searchparams = {
        #Filter query to control location to Davis or Sacramento only 
        "fq": "timesTag.location.contains:(Davis OR Sacramento)",
        #Uses API key we received from env earlier
        "api-key": NYT_API_KEY,
        #Sort by recency
        "sort": "newest"
    }
    #debug
    #respoone = requests.get(url, params=searchparams)
    print("NYT_API_KEY:", NYT_API_KEY)
    #Get request to API with the parameters to get article data
    response = requests.get(url, params=searchparams)
    #Returns jsonified version of data
    return jsonify(response.json())

@app.route('/api/key')
def get_api_key():
    return jsonify({"key": NYT_API_KEY})


# #If main, run flask server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)