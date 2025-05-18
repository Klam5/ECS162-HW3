from flask import Flask, jsonify, redirect, render_template, session
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


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
    if user:
        return f"<h2>Logged in as {user['email']}</h2><a href='/logout'>Logout</a>"
    return '<a href="/login">Login with Dex</a>'

@app.route('/api/key')
def get_key():
    return jsonify({'apiKey': os.getenv('NYT_API_KEY')})

@app.route('/login')
def login():
    session['nonce'] = nonce
    redirect_uri = 'http://localhost:8000/authorize'
    return oauth.flask_app.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/authorize')
def authorize():
    token = oauth.flask_app.authorize_access_token()
    nonce = session.get('nonce')

    user_info = oauth.flask_app.parse_id_token(token, nonce=nonce)  # or use .get('userinfo').json()
    session['user'] = user_info
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)




# https://flask.palletsprojects.com/en/stable/quickstart/
# https://flask.palletsprojects.com/en/stable/api/#flask.jsonify
# https://developer.nytimes.com/docs/articlesearch-product/1/overview

# from flask import Flask, render_template, jsonify #Imports flask, render template for HTML file, jsonify to send JSON back and forth
# import os       #used to read env variables
# import requests #sends requests
# import json
# from dotenv import load_dotenv  #loads env file

# load_dotenv()
# app = Flask(__name__)                       #Creates Flask app
# NYT_API_KEY = os.getenv("NYT_API_KEY")      #gets api key from .env

# @app.route('/')                             #Sets up root URL
# def home():
#     return render_template("index.html")    #renders index.html template

# @app.route('/api/news')                     #apinews route used by js
# def news():
#     #Base url for NYT article searchapi
#     url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
#     #Search Paramaters to control article searching 
#     searchparams = {
#         #Filter query to control location to Davis or Sacramento only 
#         "fq": "timesTag.location.contains:(Davis OR Sacramento)",
#         #Uses API key we received from env earlier
#         "api-key": NYT_API_KEY,
#         #Sort by recency
#         "sort": "newest"
#     }
#     #Get request to API with the parameters to get article data
#     response = requests.get(url, params=searchparams)
#     #Returns jsonified version of data
#     return jsonify(response.json())

# @app.route('/api/key')
# def get_api_key():
#     return jsonify({"key": NYT_API_KEY})


# #If main, run flask server
# if __name__ == "__main__":
#     app.run(port=8000, debug=True)