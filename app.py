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

if 'userCounters' in db.list_collection_names():
    print(db.list_collection_names())
else :
    db.userCounters.insert_one({"seq" : 0})

if 'listCounters' in db.list_collection_names():
    print(db.list_collection_names())
else :
    db.listCounters.insert_one({"seq" : 0})

@app.route('/')
def home():
   return render_template("login.html")


@app.route('/home/login', methods=['POST'])
def login():  
   id = request.form['id']
   print(id)
   password = request.form['password']
   user_from_db = users_collection.find_one({'id': id})
   if user_from_db:
        encrpted_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if encrpted_password == user_from_db['token']:
             access_token = create_access_token({"identity":user_from_db['id'],"password":password})
             print("토큰 생성 테스트")
            #print(access_token)
             return jsonify({'token':access_token,'result':'success'}), 200
   return jsonify({'msg' : 'The username or password is incorrect','result' : 'fail'})

    

# 회원 가입 페이지

@app.route('/join/add', methods=['POST'])
def register():
     new_user_name = request.form['name']
     new_user_id = request.form['id']
     new_user_pw= request.form['password']
     new_user_age= request.form['age']
     new_user_gender = request.form['gender']
     new_user_room = request.form['room']

     token = hashlib.sha256(new_user_pw.encode("utf-8")).hexdigest() # encrpt password
     doc = users_collection.find_one({"username": new_user_name})
     seq = db.userCounters.find({})[0]['seq']
     new_user ={
         '_id': seq,
         'id' : new_user_id,
         'password' : new_user_pw,
         'name' : new_user_name,
         'age' : new_user_age, 
         'gender' : new_user_gender,
         'room' : new_user_room,
         'token' : token
     }
     if not doc:
          users_collection.insert_one(new_user)
          db.userCounters.update_one({'seq': seq},{'$set':{'seq' : (seq+1)}})
          return jsonify({'msg' : 'User created successfully', 'result': 'success'}) , 201
     else:
          return jsonify({'msg' : 'Username already exists'}),409
     

   
@app.route('/join/double', methods=['POST'])
def dobuleCheck():
    id = request.form['id']
    doc = users_collection.find_one({"id": id})
    if not doc:
        return jsonify({'msg': "사용 가능한 ID입니다.",'result':'success'})
    else:
        return jsonify({'msg': "중복된 ID입니다.", 'reuslt':'fail'})




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


@app.route('/list/get', methods=['POST'])
def get_list():
    sort = request.form['sort']
    vaild = request.form['vaild']
    print(vaild)
    result = list(db.list.find({'vaild':vaild}).sort([(sort,-1), ('date',-1)]))
    return jsonify({'result': 'success', 'list': result})
    


# 새글 생성
@app.route('/list/create')
def contents():  
   # token_receive = request.cookies.get('mytoken')
   return render_template('create.html', a="list")

@app.route('/list/create/post', methods=["POST"])
def add_contents():  
   title = request.form['title']
   details= request.form['details']
   multi = request.form['multi']
   room = request.form['room']
   voteContents = request.form['voteContents']
   createId = request.form['createId']
   vaild = request.form['valid']

   seq = db.listCounters.find({})[0]['seq']
   new_contents = {
       "_id":seq,
       "title": title,
       "details" : details,
       "multi" : multi,
       "room" : room,
       "voteContents" : voteContents,
       "date" : datetime.datetime.now(),
       "createId": createId,
       "vaild" : vaild,
   }

 

   list_collection.insert_one(new_contents)
   db.listCounters.update_one({'seq': seq},{'$set':{'seq' : (seq+1)}})
   return jsonify({'msg':'등록되었습니다.','result': 'success'})

# 상세 페이지



if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)