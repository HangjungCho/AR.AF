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
class User(db2.Model):
    __tablename__ = 'User' # 테이블 이름

    ID = db2.Column(db2.Integer,  primary_key = True) # 시퀀스 추가
    user_id = db2.Column(db2.String) 
    password = db2.Column(db2.String)

    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = password

    def __repr__(self):
        return"<User('%s', '%s')>" % (self.user_id, self.password)
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
class Count(db2.Model):
    __tablename__ = 'Count'
    
    p_type = db2.Column(db2.String, primary_key = True)
    total = db2.Column(db2.Integer)
 
    def __init__(self, p_type, total):
        self.p_type = p_type
        self.total = total
   
    def __repr__(self):
        return"<Count('%s', '%d')>" % (self.p_type, total)
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

""""
자 이제 time 을 Integer로 쓰는 이유를 설명하겠습니다. 협정세계시  UTC 기준으로 날짜를 계산하게 되는데 어떤 방식이냐면, UTC에 대해서 먼저 알아야 합니다.
UTC란? : 1972년 1월 1일부터 시행된 협정세계시에서는 1967년 국제도량형총회가 정한 세슘원자의 진동수에 따른 초의 길이가 그 기준으로 쓰인다.

즉, 1972년 1월 1일부터 1초간 꾸준히 2020년 현재날짜 까지  계속 1초단위를 세어 온 것이죠  time.time()을 출력하는 순간 나오는 숫자들이 바로 1972년 부터 1초씩 쭉 세어온 초 입니다.
근데 이때 출력되는 값은 string 값으로 int로 자료형 변환 해 주어야 합니다. 따라서 제가 앞으로 시간을 쓸 때 int(time.time()) 을 자주 쓸 것입니다. String으로 해도 되는데 굳이 Int로 했던 이유는 python에서는 String도 사칙연산이 가능하지만
JavaScript는 그렇지 않기 때문이죠, 값을 넘겨줄때 string형 날짜를 보내주면 연산을 못하기 때문에 python에서 미리 int로 변환해 주어 보냈습니다.
이 때문에 굳이굳이 초 단위로, 자료형은 굳이굳이  Integer형으로 한것입니다.
"""
###################################### Method Tool End ###############################################



###################################### Route Method ###############################################
"""
밑에 뷰 함수들을 설명하기 전에 앞서 GET 방식과 POST 방식의 차이에 대해서 알아야 합니다.
GET : HTML 에서 정보를  "받아옴". 정보를 보낼수는 있으나 정보들이 도메인에 노출되고(정보의노출) 보내는 정보량에도 제한이 있어서 좋지 않다.
POST " HTML 에서 정보를 받아오고(이는 GET방식이 default기 때문) 다시 HTML에 정보를 보내고 싶을 때 써줍니다. 정보들이 숨겨져서 보내지고 정보량 제한도 없어서 정보를 보낼때 쓰임!
"""



'''메인페이지 '''
# @app.route()는 무엇이냐? 사이트의 경로랑 연결지어주는 역할을 합니다. "/" 라고 되어있으므로 "http://(사이트도메인)/" 의 경로에 접속하게 되면 실행되게 경로설정을 해주는 것이지요.
# 저의경우는 http://192.168.25.50:5000/ 에 접속하면 실행되네요 이때 get, post 두가지 방식으로 정보를 받아오는데 아무것도 쓰지 않으면 default(기본값)으로 get 방식을 쓰게 됩니다.
# 아무것도 쓰지 않았기 때문에 지금은 get 방식이겠지요?
# 정리를 하면, http://(사이트도메인)/"의 경로에 사용자가 접속하면 뷰 함수를 호출하는데 method를 표시하지 않았으므로 get 방식으로 이 함수를 호출합니다.
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



""" 검색창 """

@app.route("/", methods=['GET','POST'])
def search_product():

    if request.method=='POST': # 이와같이 POST 방식을 사용하는 경우는 html 파일에서 대표적으로 form 태그에서 method="POST" 의 속성이 있어야 POST로 받아올 수 있습니다.  search.html의 56번째 줄을 참고해주세요
        productname = request.form.get('search') # 검색하는 값 받아오는데, search.html의 59번째줄 input 태그에서 name="search"의 name속성에 써둔 곳에서 값을 받아오는 것입니다 즉 검색창에 검색한 내용을 받아오겠죠?
        # 참고로 id="search"라고 되어있는데 뷰 함수와는 무관합니다. id="something" 이런식으로 name="search"와 다르게 해도 기능에는 별 문제가 없음..
        productlist = db2.session.query(Product).filter(Product.title.like('%'+productname+'%')).all() # SQL문이 기억나시면 like의 기능을 참고해주세요 %는 모든 문자입니다.
        # 즉 검색창에 입력한 내용을 productname 변수에 저장하고, 그 변수명 앞뒤로 %를 붙임으로써 검색내용 앞뒤로 어떤 내용이든 출력하게끔 리스트형식으로 productlist 변수에 저장합니다.
        # 예를들어 "커피"를 검색했다고 칩시다, 그러면 "[커피]원두", "디카페인[커피]", "드립[커피]머신" 와 같은 product table의 title을 가진 product의 모든 정보들이  productlist에 저장되겠지요 ㅎㅎ
        return render_template("search.html", products=productlist)  # 그 내용을 넘겨줍니다. 출력을 어떻게 할지는 search.html 에서 정해줘야하는데 search.html의 161~177 줄을 참고해주세요
    else:
        return redirect(url_for("home")) # 흠.. 왜 이렇게했는지는 까먹었는데 없어도 될듯싶습니다. GET 방식일 때 위에 home()함수로 이동하게 하는건데 search는 POST방식으로밖에 이동하지 않게 설정했기 때문에 없어도 될것입니다
    


""" 로그인 """
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method=='GET': # 만약 login을 login이미지를 클릭해서 들어오든, 링크로 타서 들어오면 GET 방식으로 이동하기 때문에 아래의 내용을 실행합니다.
        return render_template("login.html", error = None) # error가 없는 상태로 간주한 상태에서 login.html을 열어줍니다.
    else: # POST방식으로 이동할 경우(우리 프로젝트의 경우 login을 위해 아이디와 비밀번호를 입력 후 Log in 버튼을 누르면 POST 방식으로 요청하게 됩니다.)
        uname=request.form['username'] # 입력했던 id를 변수로 따로 저장, login.html의 132줄 name="username"를 참고하세요
        upasswd=request.form['password'] # 입력했던 password를 변수로 따로 저장, login.html의 135줄 name="password"를 참고하세요
        try:
            user_data = User.query.filter_by(name=uname, password=upasswd).first()
            if user_data is not None : # 정상적으로 로그인이 된 경우 실행되는 창
                session['user_id']=user_data.id # 세션에 user_id 라는 변수로 user_data.id 값을 올려줍니다. 앞으로 무진장 많이쓰니 중요함
                session['logged_in']=True # 세션에 logged_in 이라는 변수를 True로 지정해 줍니다. 앞으로 무진장 많이쓰니 중요함
                return redirect(url_for('home')) # 홈으로 이동해줌, home() 뷰함수를 실행하는 것과 같음
            else: # 정상적으로 로그인이 되지 않는경우(DB에 관련 user_data가 없는경우 None이 되므로..)
                error = "ID가 존재하지 않거나 비밀번호가 일치하지 않습니다."
                return render_template("login.html", error=error) # 왜 로그인이 안되었는지 보내줍니다.
        except :
            error = "DB조회중에 에러가 발생했습니다." # 예외처리를 해주지 못한 나머지 에러는 그냥 DB조회중 에러라고 책임감없는 짬처리를 해버립니다. 어차피 개발자 아니면 모르니 ㅋㅋㅋ
                                             # 추가적으로 에러처리를 해주고싶으면 위에 try안에  elif로 추가해줘야겠쥬?
            return render_template("login.html", error=error)

""" 회원가입 """
@app.route("/register", methods=['GET', 'POST'])
def register():
    """get방식  요청은 reighter.html 응답 전송 post 방식 요청은 db에 회원 정보 추가하고 login페이지로 redirect시킵니다"""
    if request.method=='POST': #회원가입 페이지에 회원가입 누르면 모든 정보들을 저장해 줍니다. 
        # User Class 기반의 내용들을 이용하여 저장
        new_user = User(name=request.form['username'],
                        email= request.form['emailid']+'@'+request.form['emailadd'],
                        password = request.form['password'],
                        phone = request.form['txtMobile1']+'-'+request.form['txtMobile2']+'-'+request.form['txtMobile3'],
                        address = '')
        if (request.form['username'] and request.form['password'] and request.form['emailid'] and request.form['emailadd']) == '':
            if  request.form['username'] == '':
                error = "ID는 필수 입력 사항입니다."
                return render_template("register.html", error=error)
            elif request.form['password'] == '':
                error = "비밀번호는 필수 입력 사항입니다."
                return render_template("register.html", error=error)
            elif (request.form['emailid'] or request.form['emailadd']) == '' :
                error = "E-mail은 필수 입력 사항입니다."
                return render_template("register.html", error=error)
        # 각종 에러처리, 회원ID를 입력 안했건, 비밀번호를 입력하지 않았건, email을 입력하지 않았건 회원가입하지 못하게 해줍시다!
        
        if request.form['password']==request.form['confirmPassword']: # 비밀번호 확인이 일치하면 commit 시킨다. 
            db2.session.add(new_user)
            db2.session.commit()
            return render_template("login.html", error = None)
        else: # 비밀번호 확인과 비밀번호가 일치하지 않으면 에러
            error = "입력하신 비밀번호와 비밀번호 확인값이 일치하지 않습니다."
            return render_template("register.html", error=error)
    else:# GET 방식의 경우는 register 창을 띄워줌
        return render_template("register.html", error = None)
    
    
 

""" 로그아웃 """    
@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['user_id'] = None
    return redirect(url_for('home'))

""" 회원탈퇴 """
#################################################################
@app.route("/unjoin")
def unjoin():
    user_data = User.query.filter_by(id=session['user_id']).first()
    return render_template("unjoin.html", user=user_data)

@app.route("/unjoin/complete", methods=['GET', 'POST'])
def unjoin_complete():
    user_data = User.query.filter_by(id=session['user_id']).first()
    if request.method == 'POST':
        if request.form['password']==user_data.password:
            db2.session.delete(user_data)
            db2.session.commit()
            session['logged_in'] = False
            session['user_id'] = None 
            return redirect(url_for("home"))
        else:
            error = "회원정보의 비밀번호와 일치하지 않습니다."
            return render_template("unjoin.html", user = user_data, error=error)
    else:
        return redirect(url_for("home"))
#################################################################        

@app.route("/sell_product")
def sell_product():
    return render_template("sell_product.html")

# 메인함수
if __name__ == '__main__':
    app.debug=True # Debug 활성화
#     db2.create_all() #테이블이 생성되고 나서는 주석처리해줌
    app.secret_key = '1234567890'
    app.run(debug=False, host='0.0.0.0') #본인의 ip로 접속할 수 있게 해줍니다.
