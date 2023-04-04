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
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1) # define the life span of the token

if 'user_counters' in db.list_collection_names():
    print(db.list_collection_names())
else :
    db.userCounters.insert_one({"seq" : 0})

if 'list_counters' in db.list_collection_names():
    print(db.list_collection_names())
else :
    db.listCounters.insert_one({"seq" : 0})

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
     seq = db.userCounters.find({})[0]['seq']
     new_user ={
         '_id': seq,
         'username' : new_user_name,
         'password' : request.form['password'],
         'token' : new_user_pw
     }
     if not doc:
          users_collection.insert_one(new_user)
          db.userCounters.update_one({'seq': seq},{'$set':{'seq' : (seq+1)}})
          return jsonify({'msg' : 'User created successfully', 'result': 'success'}) , 201
     else:
          return jsonify({'msg' : 'Username already exists'}),409



#protected - 토큰 있는지 체크
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify({"logged_in_as":current_user,"result": "success"}), 200



# 게시글 페이지


@app.route('/list')
def list_main():  
   # token_receive = request.cookies.get('mytoken')
   return render_template('list.html', a="list")


@app.route('/list/get', methods=['GET'])
def get_list():
    result = list(db.list.find({}))
    return jsonify({'result': 'success', 'list': result})
    


# 새글 생성
@app.route('/list/create')
def contents():  
   # token_receive = request.cookies.get('mytoken')
   return render_template('contents.html', a="list")

@app.route('/list/create/post', methods=["POST"])
def add_contents():  
   title = request.form['title']
   details= request.form['details']
   multi = request.form['multi']
   room = request.form['room']
   voteContents = request.form['voteContents']

   print("---------")
   print(multi)
   print(details)

   print("---------@@@@@@@@@@@@@@@@")
   new_contents = {
       "title": title,
       "details" : details,
       "multi" : multi,
       "room" : room,
       "voteContents" : voteContents
   }
   print("------")
   print(new_contents)
   print("------")
   list_collection.insert_one(new_contents)
   return 'This is My Page!'


# 상세 페이지



if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)