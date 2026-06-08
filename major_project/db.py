from pymongo import MongoClient

client = MongoClient("mongodb+srv://vijaysuryawanshi7224_db_user:vijay%402005@cluster0.ckvnjfm.mongodb.net/collegedb?retryWrites=true&w=majority")

db = client["job_portal"]

users_collection = db["users"]
jobs_collection = db["jobs"]
admin_collection = db["admin"]