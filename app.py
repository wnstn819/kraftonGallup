from flask import Flask, render_template,jsonify,request,redirect
from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
from flask_jwt_extended import JWTManager, create_access_token,jwt_required,get_jwt_identity
import datetime
import hashlib
import jwt

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.

db = client["kraftonGallup"]
users_collection = db["users"]
list_collection = db["list"]




app = Flask(__name__)
# 로그인 페이지

jwtM = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'testKey'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=10) # define the life span of the token


@app.route('/')
def home():
   return render_template("login.html")


@app.route('/home/login', methods=['POST'])
def login():  
   username = request.form['username']
   password = request.form['password']
   user_from_db = users_collection.find_one({'username': username})
   if user_from_db:
        encrpted_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if encrpted_password == user_from_db['password']:
             access_token = create_access_token({"identity":user_from_db['username'],"password":password})
             print("토큰 생성 테스트")
             print(access_token)
             return jsonify({'token':access_token,'result':'success'}), 200
   return jsonify({'msg' : 'The username or password is incorrect'}), 401

    

# 회원 가입 페이지

@app.route('/join/add', methods=['POST'])
def register():
     new_user_name = request.form['username']
     new_user_pw= request.form['password']
     
     new_user_pw = hashlib.sha256(new_user_pw.encode("utf-8")).hexdigest() # encrpt password
     doc = users_collection.find_one({"username": new_user_name})

     new_user ={
         'username' : new_user_name,
         'password' : new_user_pw
     }
     if not doc:
          users_collection.insert_one(new_user)
          return jsonify({'msg' : 'User created successfully', 'result': 'success'}) , 201
     else:
          return jsonify({'msg' : 'Username already exists'}),409



#protected
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify({"logged_in_as":current_user,"result": "success"}), 200



# 게시글 페이지


@app.route('/list')
def list_main():  
   token_receive = request.cookies.get('mytoken')
   print("-----테스트------")
   print(token_receive)
   return render_template('list.html', a="list")


@app.route('/list/get', methods=['GET'])
def get_list():
    result = list(db.list.find({}))
    return jsonify({'result': 'success', 'list': result})
    


# 새글 생성


@app.route('/new')
def add_page():  
   return 'This is My Page!'


# 상세 페이지



if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)