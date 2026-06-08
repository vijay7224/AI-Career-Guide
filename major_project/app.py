from flask import Flask

app=Flask(__name__)

app.secret_key="secret123"

from routes.auth import register_auth_routes
from routes.recommendation import register_recommend_routes
from routes.chatbot import register_chatbot_routes
from routes.admin import register_admin_routes

register_auth_routes(app)
register_recommend_routes(app)
register_chatbot_routes(app)
register_admin_routes(app)

if __name__=="__main__":
    app.run(debug=True)