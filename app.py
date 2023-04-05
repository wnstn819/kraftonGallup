from flask import Flask, render_template,jsonify,request,redirect
from pymongo import MongoClient           # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
from flask_jwt_extended import JWTManager, create_access_token,jwt_required,get_jwt_identity
import datetime
import hashlib
import json
import math

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.

db = client["kraftonGallup"]
users_collection = db["users"]
list_collection = db["list"]





app = Flask(__name__)
################################## 로그인 페이지 ##################################

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

    

################################## 회원 가입 페이지 ##################################

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




################################## protected - 토큰 있는지 체크 ##################################
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify({"logged_in_as":current_user,"result": "success"}), 200



# 게시글 페이지
# 페이징 ing
@app.route('/list')
def list_main():  
    # token_receive = request.cookies.get('mytoken')
    # 최초 호출, 임시 고정값
    sort = 'date'   # request.form['sort']
    vaild = '1'       #request.form['vaild']
  

    result = list(db.list.find({'vaild':'1'}).sort([(sort,-1), ('date',-1)]))    
    result2 = list(db.list.find({'vaild':'0'}).sort([(sort,-1), ('date',-1)]))

    # 페이징 값
    page = request.args.get("page", 1, type=int)
    # print(request.args.get("page", 1, type=int))
    # page = 1
    limit=10
    # datas = list(db.list.find({'valid':'1'}).sort([(sort,-1),('date',-1)]).skip((page - 1) * limit).limit(limit))
    datas = list(db.list.find({'vaild':'1'}).sort([(sort,-1), ('date',-1)]).skip((page - 1) * limit).limit(limit))
    tot_count = len(result)
    last_page_num = math.ceil(tot_count / limit)
    block_size=5
    block_num = int((page - 1) / block_size)
    block_start = (block_size * block_num) + 1
    block_end = block_start + (block_size - 1)
    

    return render_template(
            'table.html', 
            validList=result, 
            invalidList=result2, 
            datas=datas,
            limit=limit,
            page=page,
            block_start=block_start,
            block_end=block_end,
            tot_count = tot_count,
            last_page_num=last_page_num
        )



@app.route('/list/get', methods=['POST'])
def get_list():
    sort = request.form['sort']
    vaild = request.form['vaild']
    result = list(db.list.find({'vaild':vaild}).sort([(sort,-1), ('date',-1)]))
    return jsonify({'result': 'success', 'list': result})

################################## 새글 생성 ##################################
@app.route('/list/create')
def contents():  
   # token_receive = request.cookies.get('mytoken')
   return render_template('create.html', a="list")

@app.route('/list/create/post', methods=["POST"])
def add_contents():  
   title = request.form['title']
   details= request.form['details']
   room = request.form['room']
   expired = request.form['expired']
   convert_date = datetime.datetime.strptime(expired, "%Y-%m-%d"),
   voteContents = request.form['voteContents']
   createId = request.form['createId']
   vaild = request.form['valid']

   seq = db.listCounters.find({})[0]['seq']

   new_contents = {
       "_id":seq,
       "title": title,
       "details" : details,
       "room" : room,
       "expired" : convert_date[0],
       "voteContents" : voteContents,
       "date" : datetime.datetime.now().strftime("%Y-%m-%d"),
       "createId": createId,
       "vaild" : vaild,
   }

 

   list_collection.insert_one(new_contents)
   db.listCounters.update_one({'seq': seq},{'$set':{'seq' : (seq+1)}})
   return jsonify({'msg':'등록되었습니다.','result': 'success'})


################################## 상세 페이지 ##################################
@app.route('/list/vote/<number>', methods=["GET"])
def vote(number):  
   result = list(db.list.find({'_id':int(number)}))
    
   print(result[0]['voteContents'])
   parse = {
       '_id' : result[0]['_id'],
       'title' : result[0]['title'],
       'details' : result[0]['details'],
       'room' : result[0]['room'],
       'voteContents' : json.loads(result[0]['voteContents']),
       'expired': result[0]['expired'],
       'date' : result[0]['date'],
       'createId' : result[0]['createId'],
       'vaild' : result[0]['vaild']
   } 

   # token_receive = request.cookies.get('mytoken')
   return render_template('vote.html', data=parse)

@app.route('/list/vote/detail', methods=["POST"])
def voteDetails():
      id = request.form['id']
      print(id + "ddddddid")
      result = list(db.list.find({'_id':int(id)}))
      return jsonify({'result':'success', 'details':result})

@app.route('/list/vote/update', methods=["POST"])
def vote_update():
    #투표하려면 필요 한 것 투표 id, user id, 투표항목
   
    id = request.form['id']
    select = request.form['select']
    userId = request.form['userId']
    result = list(db.list.find({'_id':int(id)}))
    parse = json.loads(result[0]['voteContents'])
    value=[]

    for key in parse.keys():
        if key == select:
            if userId not in parse[key]:
                value = parse[key]
                value.append(userId)
                parse.update({key :value})   
        else :
            if userId in parse[key]:
                value = parse[key]
                value.remove(userId)
                parse.update({key :value})
   

    parse = json.dumps(parse)
    db.list.update_one({'_id' :int(id)} ,{'$set':{ 'voteContents': str(parse)}})
    return jsonify({"result": "success"})



if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)