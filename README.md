# api_task

# JSON Web Tokens (or JWTs) provide a means of transmitting information from the client to the server in a stateless, secure way.

The auth workflow works as follows:

    Client provides email and password, which is sent to the server
    Server then verifies that email and password are correct and responds with an auth token
    Client stores the token and sends it along with all subsequent requests to the API
    Server decodes the token and validates it
This cycle repeats until the token expires or is revoked. In the latter case, the server issues a new token.

# HOW TO RUN THE FILE:

1.cd to the directory where requirements.txt is located.

2.pip install -r requirements.txt , in your shell.

3.Run, python api.py.

* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

browse on "http://127.0.0.1:5000/"

browse through following routes,

# / route - Login
# /thumb route - Download and covert the image to thumbnail(50*50)



The given url is requested and image is dwonloaded from the same and saved in the working Directory.


The images from the working directory are searched and converted into thumbnails and again saved into the same directory.
