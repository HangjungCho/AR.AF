from sqlalchemy import create_engine

# 거의 핵심 기능들을 import 하는데 밑에서 쓰는 것을 보면 알겠지만 주로 db에 연결하거나 주소 경로 설정할때 많이 쓰인다
from flask import Flask, url_for, render_template, request, redirect, session, jsonify, make_response, abort, g, flash


from flask_sqlalchemy import SQLAlchemy
from pip._vendor.appdirs import user_data_dir
from sqlalchemy import desc

# 우리는 타이머 기능을 사용하기 때문에 필요하기도 하지만 날짜를 계산하기 위해서 필요하다.
from datetime import datetime 
import time

from sqlalchemy.sql.expression import null
from _hashlib import new 
from sqlite3 import dbapi2 as sqlite3
from _dummy_thread import error
from contextlib import closing

# 백자이크 import
from werkzeug.security import check_password_hash, generate_password_hash # 쓰진 않았지만 비밀번호 해쉬값으로 바꿔서 암호화 하려고 했었음
from werkzeug.utils import secure_filename

from pytz import timezone
import atexit
from Cython.Shadow import address


DATABASE = 'araf.db'  # 내가 설정한 DB 이름

app = Flask(__name__) # app 초기화, 밑에 SQLAlchemy에 들어감
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///araf.db'

#파일 업로드 용량 제한
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024

db2 = SQLAlchemy(app)
app.config.from_object(__name__)

def connect_db():
    """DB 연결 후 Connection객체 반환, DB 없으면 내부적으로 새로 생성됨."""
    return sqlite3.connect(app.config['DATABASE'])

#################################### Table Class start #########################################

# ======================================== User ===============================================
#class User(db2.Model):
#    __tablename__ = 'User' # 테이블 이름

#    ID = db2.Column(db2.Integer,  primary_key = True) # 시퀀스 추가
#    user_id = db2.Column(db2.String) 
#    password = db2.Column(db2.String)

#    def __init__(self, user_id, password):
#        self.user_id = user_id
#        self.password = password

#    def __repr__(self):
#        return"<User('%s', '%s')>" % (self.user_id, self.password)
# =============================================================================================

# ====================================== Quantity =============================================
class Quantity(db2.Model):
    __tablename__ = 'Quantity'
    
    ID = db2.Column(db2.Integer, primary_key = True)
    p_type = db2.Column(db2.String)
    cal = db2.Column(db2.String)
    count = db2.Column(db2.Integer)
    date = db2.Column(db2.String)
    time = db2.Column(db2.String)
    img = db2.Column(db2.String)

    def __init__(self, p_type, cal, count, date, time, img):
        self.p_type = ptype
        self.cal = cal
        self.count = count
        self.date = date
        self.time = time
        self.img = img

    def __repr__(self):
        return"<Quantity('%s', '%s', '%d', '%s', '%s', '%s')>" % (self.p_type, self.cal, self.count, self.date, self.time, self.img)
# =============================================================================================

# ======================================== Count ==============================================
#class Count(db2.Model):
#    __tablename__ = 'Count'
    
#    p_type = db2.Column(db2.String, primary_key = True)
#    total = db2.Column(db2.Integer)
 
#    def __init__(self, p_type, total):
#        self.p_type = p_type
#        self.total = total
   
#    def __repr__(self):
#        return"<Count('%s', '%d')>" % (self.p_type, total)
# =============================================================================================       

###################################### Table Class end ###############################################


###################################### Method Tool Start ###############################################
""" 쿼리문을 직접 쓸수 있게 해주는 함수 (minitwit에서 쓰던 방식임) """
def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    """ g는 전역객체, fetchall():조회할때 쓰는 메소드"""
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

""" g.db 전역객체로 DB에 접근하여 query문 적용하기 위한 Method"""
@app.before_request
def before_request():
    """http 요청이 올 때마다 실행 : db연결하고 전역 객체 g에 저장하고 세션에 userid가 저장되어 있는지 체크해서 user 테이블로부터 user 정보 조회 한 후에 전역 객체 g에 저장 """
    g.db=connect_db()
    
# 여기서 말해두지만 g.db와 db2는 엄연히 다른 방식입니다.. 
# g.db는 minitwit에서 끌어다가 쓴 방식이고
# db2 는 박혜정쌤이 게시판 만들때 쓰던 방식입니다 개인적으로 db2 방식이 더 쉬워서 많이썼어요 ㅎㅎ 이 위에있는 두 query_db, before_request 함수는 minitwit에서 쓰는 방식을 가져온 것입니다.

""" 날짜함수 Method """
def format_datetime(timestamp):
    """ 정수값에 해당하는 날짜 시간 포맷 형식 변경해서 문자열로 반환하는 함수 """
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d  %H:%M')

app.jinja_env.filters['datetimeformat'] = format_datetime
""" jinja 템플릿 엔진에 filter로 등록 => html페이지에서 필터처리할 때 사용됨"""
# template engine jinja에 이름을 지정(datetimeformat)하고 format_datetime(우리가 위에서 만든 함수)를 넣어준다

###################################### Method Tool End ###############################################



###################################### Route Method ###############################################


'''메인페이지 '''

#@app.route("/")
#def home():
#    product_popular = []
    
#    # 마감일 빠른 순으로 출력하기 위해 product table에서  등록일자 순으로 오름차순 하여 상위 3개 제품을 product_deadline 변수에 list형으로 저장한다.
#    product_deadline=Product.query.filter_by(state=1).order_by(Product.now_date.asc()).limit(3)
    
#    # 최신 등록상품을 출력하기 위해 product table에서 등록일자 순으로 내림차순 하여 상위 4개 제품을 product_newest 변수에 list형으로 젖아한다.
#    product_newest = Product.query.filter_by(state=1).order_by(Product.now_date.desc()).limit(4)
    
#    # 좋아요를 가장 많이 받은 제품을 출력하기 위해 heart 테이블에서 좋아요 개수가 가장 많은 상품부터 상위 4개제품을 heart_data에 저장한다.
#    heart_data = Heart.query.order_by(Heart.heart_cnt.desc()).limit(4)
    
#    # heart_data는 heart table에서 그저 좋아요가 높은 순으로 가져온 데이터기 때문에 메인페이지에 넘겨주기에는 적은 정보를 담고있다
#    # 따라서 heart table이 아닌 product table로 변형해 주기 위해서 for문으로 좋아요가 높은 순으로 4개의 제품을 리스트 형식으로 저장해 준다.
#    for i in range(4):
#        product_popular.append(Product.query.filter_by(id=heart_data[i].product_id, state=1).first())
#    #                                                  id가 heart_data의 아이들만, 낙찰이 되지 않은 제품들만 가져옴
#    # render_template 함수로 리턴을 해주 면 html 파일에 아래와 같은 변수들을 넘겨 줄 수 있음. 예를들면 product_head = product_deadline 의 경우 product_deadline이라는 이클립스에서의 변수를
#    # index.html 에서 product_head라는 변수의 형태로 쓰겠다 라는 의미로 해석하면 된다.
#    return render_template('index.html', product_head=product_deadline,
#                           product_newest=product_newest,
#                           product_popular=product_popular,
#                           now_time = int(time.time()+time_seoul)) # UTC 표준시간 기준 서울은 9시간 이 더 많이 때문에 time_seoul 더해줘야 지금시간이 제대로 출력됩니다



""" index """
@app.route("/", methods=['GET','POST'])
def home():

    if request.method=='POST': 
        product_name = request.form.get('search') 
        product_date = request.form.get('startdate')
        print("search : {}".format(search))
        print("startdate : {}".format(search))

        productlist = db2.session.query(Quantity).filter(Quantity.p_type.like('%'+product_name+'%')).all()
        return render_template("search.html", products=productlist)  
    else:
        return redirect(url_for("home")) 


#""" 로그인 """
#@app.route("/login", methods=['GET','POST'])
#def login():
#    if request.method=='GET': # 만약 login을 login이미지를 클릭해서 들어오든, 링크로 타서 들어오면 GET 방식으로 이동하기 때문에 아래의 내용을 실행합니다.
#        return render_template("login.html", error = None) # error가 없는 상태로 간주한 상태에서 login.html을 열어줍니다.
#    else: # POST방식으로 이동할 경우(우리 프로젝트의 경우 login을 위해 아이디와 비밀번호를 입력 후 Log in 버튼을 누르면 POST 방식으로 요청하게 됩니다.)
#        uname=request.form['username'] # 입력했던 id를 변수로 따로 저장, login.html의 132줄 name="username"를 참고하세요
#        upasswd=request.form['password'] # 입력했던 password를 변수로 따로 저장, login.html의 135줄 name="password"를 참고하세요
#        try:
#            user_data = User.query.filter_by(name=uname, password=upasswd).first()
#            if user_data is not None : # 정상적으로 로그인이 된 경우 실행되는 창
#                session['user_id']=user_data.id # 세션에 user_id 라는 변수로 user_data.id 값을 올려줍니다. 앞으로 무진장 많이쓰니 중요함
#                session['logged_in']=True # 세션에 logged_in 이라는 변수를 True로 지정해 줍니다. 앞으로 무진장 많이쓰니 중요함
#                return redirect(url_for('home')) # 홈으로 이동해줌, home() 뷰함수를 실행하는 것과 같음
#            else: # 정상적으로 로그인이 되지 않는경우(DB에 관련 user_data가 없는경우 None이 되므로..)
#                error = "ID가 존재하지 않거나 비밀번호가 일치하지 않습니다."
#                return render_template("login.html", error=error) # 왜 로그인이 안되었는지 보내줍니다.
#        except :
#            error = "DB조회중에 에러가 발생했습니다." # 예외처리를 해주지 못한 나머지 에러는 그냥 DB조회중 에러라고 책임감없는 짬처리를 해버립니다. 어차피 개발자 아니면 모르니 ㅋㅋㅋ
#                                             # 추가적으로 에러처리를 해주고싶으면 위에 try안에  elif로 추가해줘야겠쥬?
#            return render_template("login.html", error=error)

#""" 회원가입 """
#@app.route("/register", methods=['GET', 'POST'])
#def register():
#    """get방식  요청은 reighter.html 응답 전송 post 방식 요청은 db에 회원 정보 추가하고 login페이지로 redirect시킵니다"""
#    if request.method=='POST': #회원가입 페이지에 회원가입 누르면 모든 정보들을 저장해 줍니다. 
#        # User Class 기반의 내용들을 이용하여 저장
#        new_user = User(name=request.form['username'],
#                        email= request.form['emailid']+'@'+request.form['emailadd'],
#                        password = request.form['password'],
#                        phone = request.form['txtMobile1']+'-'+request.form['txtMobile2']+'-'+request.form['txtMobile3'],
#                        address = '')
#        if (request.form['username'] and request.form['password'] and request.form['emailid'] and request.form['emailadd']) == '':
#            if  request.form['username'] == '':
#                error = "ID는 필수 입력 사항입니다."
#                return render_template("register.html", error=error)
#            elif request.form['password'] == '':
#                error = "비밀번호는 필수 입력 사항입니다."
#                return render_template("register.html", error=error)
#            elif (request.form['emailid'] or request.form['emailadd']) == '' :
#                error = "E-mail은 필수 입력 사항입니다."
#                return render_template("register.html", error=error)
#        # 각종 에러처리, 회원ID를 입력 안했건, 비밀번호를 입력하지 않았건, email을 입력하지 않았건 회원가입하지 못하게 해줍시다!
        
#        if request.form['password']==request.form['confirmPassword']: # 비밀번호 확인이 일치하면 commit 시킨다. 
#            db2.session.add(new_user)
#            db2.session.commit()
#            return render_template("login.html", error = None)
#        else: # 비밀번호 확인과 비밀번호가 일치하지 않으면 에러
#            error = "입력하신 비밀번호와 비밀번호 확인값이 일치하지 않습니다."
#            return render_template("register.html", error=error)
#    else:# GET 방식의 경우는 register 창을 띄워줌
#        return render_template("register.html", error = None)
    
    
 

#""" 로그아웃 """    
#@app.route("/logout")
#def logout():
#    session['logged_in'] = False
#    session['user_id'] = None
#    return redirect(url_for('home'))

#""" 회원탈퇴 """
##################################################################
#@app.route("/unjoin")
#def unjoin():
#    user_data = User.query.filter_by(id=session['user_id']).first()
#    return render_template("unjoin.html", user=user_data)

#@app.route("/unjoin/complete", methods=['GET', 'POST'])
#def unjoin_complete():
#    user_data = User.query.filter_by(id=session['user_id']).first()
#    if request.method == 'POST':
#        if request.form['password']==user_data.password:
#            db2.session.delete(user_data)
#            db2.session.commit()
#            session['logged_in'] = False
#            session['user_id'] = None 
#            return redirect(url_for("home"))
#        else:
#            error = "회원정보의 비밀번호와 일치하지 않습니다."
#            return render_template("unjoin.html", user = user_data, error=error)
#    else:
#        return redirect(url_for("home"))
##################################################################        

#@app.route("/sell_product")
#def sell_product():
#    return render_template("sell_product.html")



# 메인함수
if __name__ == '__main__':
    app.debug=True # Debug 활성화
#     db2.create_all() #테이블이 생성되고 나서는 주석처리해줌
    app.secret_key = '1234567890'
    app.run(debug=False, host='0.0.0.0') #본인의 ip로 접속할 수 있게 해줍니다.
