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
time_seoul = 32400
# 서울시간은 UTC 기준 9시간이 많기 때문에 9시간을 초로 환산하여  하루  9시간 * 3600초 => 32400초
# 이 시간이 현재 시간이 된다


app = Flask(__name__) # app 초기화, 밑에 SQLAlchemy에 들어감
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///araf.db'

#파일 업로드 용량 제한
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024

db2 = SQLAlchemy(app)
app.config.from_object(__name__)
# 
def connect_db():
    """DB 연결 후 Connection객체 반환, DB 없으면 내부적으로 새로 생성됨."""
    return sqlite3.connect(app.config['DATABASE'])

#################################### Table Class start #########################################

 #======================================== User ===============================================
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
 #=============================================================================================

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
    
    ID = db2.Column(db2.Integer, primary_key = True)
    p_type = db2.Column(db2.String)
    num = db2.Column(db2.Integer)
 
    def __init__(self, p_type, num):
        self.p_type = p_type
        self.num = num
   
    def __repr__(self):
        return"<Count('%s', '%d')>" % (self.p_type, self.num)
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
# d = datetime.date(2020, 11, 13) 
# d.strftime('%A')  
                                                      
# import locale                                                           
# locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')                    
# d.strftime('%A')                                                       



'''메인페이지 '''
# @app.route()는 무엇이냐? 사이트의 경로랑 연결지어주는 역할을 합니다. "/" 라고 되어있으므로 "http://(사이트도메인)/" 의 경로에 접속하게 되면 실행되게 경로설정을 해주는 것이지요.
# 저의경우는 http://192.168.25.50:5000/ 에 접속하면 실행되네요 이때 get, post 두가지 방식으로 정보를 받아오는데 아무것도 쓰지 않으면 default(기본값)으로 get 방식을 쓰게 됩니다.
# 아무것도 쓰지 않았기 때문에 지금은 get 방식이겠지요?
# 정리를 하면, http://(사이트도메인)/"의 경로에 사용자가 접속하면 뷰 함수를 호출하는데 method를 표시하지 않았으므로 get 방식으로 이 함수를 호출합니다.
    
 
@app.route("/", methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template("login.html", error = None)
    else:
        u_id=request.form['username']
        u_passwd=request.form['password']
        try:
            user_data = User.query.filter_by(user_id=u_id, password=u_passwd).first()
            if user_data is not None : # 정상적으로 로그인이 된 경우 실행되는 창
                session['user_id']=user_data.user_id
                session['logged_in']=True
 
#                 productlist = db2.session.query(Quantity).filter(Quantity.p_type.like('%')).all()
                return redirect(url_for("home"))
            else: # 정상적으로 로그인이 되지 않는경우(DB에 관련 user_data가 없는경우 None이 되므로..)
                error = "ID가 존재하지 않거나 비밀번호가 일치하지 않습니다."
                return render_template("login.html", error=error) # 왜 로그인이 안되었는지 보내줍니다.
        except :
            error = "DB조회중에 에러가 발생했습니다." # 예외처리를 해주지 못한 나머지 에러는 그냥 DB조회중 에러라고  짬처리
            return render_template("login.html", error=error)

@app.route("/main", methods=['GET', 'POST'])
def home():
    if not session['logged_in']: # session['logged_in'] 은 로그인 페이지에서 저장해 뒀던것을 기억하나요? 로그인 되어있다면 이 값은 True로 되어있을 것 입니다.
        return render_template("login.html")
    else:
#         user_data2=[]
#         user_data=User.query.filter_by(id=session['user_id']).first()
#         product_data = Product.query.filter_by(id=productid).first()
#         author_user=User.query.filter_by(id=product_data.author_id).first()
#         heart_data = Heart.query.filter_by(product_id=productid).first()
#         # Table 명과 어떤것을 filter했는지만 주목해 주시면 됩니다~
#         if request.method=='POST':
#             quest_msg = Message(product_id = productid, author_id=user_data.id, text=request.form['text'], pub_date=int(time.time()+time_seoul))
#             # minitwit에 내용을 쓰고 등록하면 해당상품의 id, 등록한 사람 id, 등록한 내용, 등록한 날짜 를 Message table에 저장하고
#             db2.session.add(quest_msg) # 그 내용을 db에 저장한 뒤에,
#             db2.session.commit() # commit을 해줘야 적용됩니다. SQL과 동일한 내용인데 기억나시나요? commit하지 않으면 DB에 저장되지 않습니다.
#             message_data = Message.query.filter_by(product_id=productid).order_by(desc(Message.pub_date)).all() # 이제 minitwit내용을 날짜순으로 내림차순(최신 등록한 날짜가 맨 위에오게)으로 정리해주고
#             sp_long = len(message_data) # 메세지가 몇개 있는지 따로 변수로 저장해주고 (이유는 위에서 한 것과 같다, len함수를 html에서 쓸수 없으므로..)
#             for i in range(sp_long):
#                 user_data2.append(User.query.filter_by(id=message_data[i].author_id).first()) # message_data를 토대로 minitwit 작성한 회원들의 정보를 모두 저장해줍니다.
#             return render_template('single-product.html', product = product_data, now_time = int(time.time()+time_seoul), messages=message_data, user= user_data2, sp_long=sp_long, author_user=author_user, heart=heart_data)
        return render_template("index.html")
            # 모든 변수를 single-product.html에 넘겨줍니다. 이 정보들을 활용하는 것은 single-product.html에서 쓰기 나름인데 html 보시면 어떻게 썼는지 보실수 있습니다. 이해하는데는 별로 어렵지 않으니 한번 보세요 ㅎㅎ
#         else: #get 방식으로 들어온 경우는 347줄에 있는 viewProduct 함수를 실행해 줍니다.
#             return redirect(url_for("viewProduct"))
    








""" 제품상세페이지  """
# @app.route 의 기능을 다음의 주소로 접근했을때 뷰함수를 실행하게 하라는 것은 앞에서 설명했다.
# 여기서 주목해야 할 점은 <int:productid> 이다. 자세하게 설명을 하자면, 우리가 어떤 A상품에 대해 클릭하게되면 상세페이지로 넘어가는 것은 다들 알고 있을텐데 다음의 주소로 접속할 경우 이 뷰함수가 실행이 된다.
# http://(본인의 ip):5000/single-product/5 이런식으로 이동이 될 것이다. 이때 5는 예를 든 것으로 상품의 고유 id인데 이는 상품을 등록할 때 DB에서 product table에 등록하면서 자동으로 id라는 column에서 지정된다 필요하면
# DB를 확인해 볼것, 이때 id는 primary key(기본키)로 제품이 생성될 때 마다 자동으로 매겨진다
# 이때 id값은 integer의 자료형을 가질 수 밖에 없게 우리가 위에서 Class 만들때 설정 해 두었다 (한번 위에서 product Class를 확인 해 보시면 알듯)
# 그렇기 때문에, <> 형태의 괄호 안에 무슨형이고, 이 값을 이 뷰 함수가 어떤 변수명으로 사용할 것인지 사용자가 지정할 수 있는데, 나는 앞에서 주소값의 5값을 앞으로 productid 라고 쓰고 싶어서 productid라고 써둔 것이다.
# 만약 productid가 아니라 임의로 special이라고 쓰고 싶다? 상관없다. 본인이 쓰고싶은 이름으로 지정하면 된다.
# 자 이제 요약하면 http://(본인ip):5000/single-product/(모든 int 형의 값) 의 경로로 접속할때 어떤 상품의 id건 모두 다 productid라는 변수로 우리가 받아주겠다, 라는 의미다.
@app.route("/single-product/<int:productid>")
def viewProduct(productid=None): # 자 이제 본인이 지정한 변수명을 None값으로 초기화 하여 선언 해 주어야 함수 안에서 활용 할 수 있다. 나는 productid라고 지정해 뒀으니 productid=None 으로 써두자
    user_data = []
    product_data = Product.query.filter_by(id=productid).first() # 위에서 productid를 그렇게 강조했는데 어디서 쓰이냐? 바로 여기서 쓰인다. 현재 보고있는 상품의 id값이 저장되어 있으므로 그 상품의 정보를 가져와 준다.
    author_user = User.query.filter_by(id=product_data.author_id).first() # 상품의 id만 있으면 이렇게 제품을 등록한 유저의 정보도 가져올 수 있고,
    message_data = Message.query.filter_by(product_id=productid).order_by(desc(Message.pub_date)).all() # 특정 상세제품의 minitwit에 내용들도 모두 가져올 수 있다.
    heart_data = Heart.query.filter_by(product_id=productid).first() # 당연히 좋아요 관련 데이터도 가져올 수 있다
    sp_long = len(message_data) # 굳이 message_data가 몇개있는지 별도의 변수에 저장한 이유는, html에서는 len함수를 쓸수 없기 때문에 여기서 따로 변수에 저장해 두었다. (html에서 for문을 쓰기 위해서 갯수를 저장해둠)
    for i in range(sp_long): #sp_long은 바로 위에 있으니 참고
        user_data.append(User.query.filter_by(id=message_data[i].author_id).first())
        # user_data에 minitwit을 쓴 사람의 id정보를 담아주는 for문으로 순전히 minitwit에 어떤사람이 썼는지 보여주기 위해 만든 user_data임.
    return render_template("single-product.html", messages=message_data, product = product_data, now_time = int(time.time()+time_seoul), user=user_data, sp_long=sp_long, author_user=author_user, heart=heart_data)
    # render_templat은 위에서 설명했으므로 앞으로는 설명을 생략하도록 하겠다.

""" 검색창 """
# 자, 처음으로 POST 방식을 사용하는 뷰 함수가 나왔는데 아래의 형식으로 사용해야한다. methods 오타 주의!! s안쓰면 에러남
@app.route("/search", methods=['GET','POST'])
def search_product():
    # 개인적으로 이해한 것이니 100% 정답이 아닐 수 있습니다..
    # GET 방식? : 대표적으로 href 태그를 통해서 들어오는 경우, 입력값을 받지않고 들어오면 GET 방식으로 들어오게 됩니다. 입력값을 받는 GET방식도 있는걸로 아는데 쓰진 않았기 때문에 모르므로 패스..
    # POST 방식? : 대표적으로 form 태그 안에서 method="POST" 를 설정 한 경우 form 안의 제출하기 따위의 액션을 취하는 태그가 있으면 POST방식으로 요청하게 됨
    
    if request.method=='POST': # 이와같이 POST 방식을 사용하는 경우는 html 파일에서 대표적으로 form 태그에서 method="POST" 의 속성이 있어야 POST로 받아올 수 있습니다.  search.html의 56번째 줄을 참고해주세요
        productname = request.form.get('search') # 검색하는 값 받아오는데, search.html의 59번째줄 input 태그에서 name="search"의 name속성에 써둔 곳에서 값을 받아오는 것입니다 즉 검색창에 검색한 내용을 받아오겠죠?
        # 참고로 id="search"라고 되어있는데 뷰 함수와는 무관합니다. id="something" 이런식으로 name="search"와 다르게 해도 기능에는 별 문제가 없음..
        productlist = db2.session.query(Product).filter(Product.title.like('%'+productname+'%')).all() # SQL문이 기억나시면 like의 기능을 참고해주세요 %는 모든 문자입니다.
        # 즉 검색창에 입력한 내용을 productname 변수에 저장하고, 그 변수명 앞뒤로 %를 붙임으로써 검색내용 앞뒤로 어떤 내용이든 출력하게끔 리스트형식으로 productlist 변수에 저장합니다.
        # 예를들어 "커피"를 검색했다고 칩시다, 그러면 "[커피]원두", "디카페인[커피]", "드립[커피]머신" 와 같은 product table의 title을 가진 product의 모든 정보들이  productlist에 저장되겠지요 ㅎㅎ
        return render_template("search.html", products=productlist)  # 그 내용을 넘겨줍니다. 출력을 어떻게 할지는 search.html 에서 정해줘야하는데 search.html의 161~177 줄을 참고해주세요
    else:
        return redirect(url_for("home")) # 흠.. 왜 이렇게했는지는 까먹었는데 없어도 될듯싶습니다. GET 방식일 때 위에 home()함수로 이동하게 하는건데 search는 POST방식으로밖에 이동하지 않게 설정했기 때문에 없어도 될것입니다
    


# """ 로그인 """
# @app.route("/login", methods=['GET','POST'])
# def login():
#     if request.method=='GET': # 만약 login을 login이미지를 클릭해서 들어오든, 링크로 타서 들어오면 GET 방식으로 이동하기 때문에 아래의 내용을 실행합니다.
#         return render_template("login.html", error = None) # error가 없는 상태로 간주한 상태에서 login.html을 열어줍니다.
#     else: # POST방식으로 이동할 경우(우리 프로젝트의 경우 login을 위해 아이디와 비밀번호를 입력 후 Log in 버튼을 누르면 POST 방식으로 요청하게 됩니다.)
#         uname=request.form['username'] # 입력했던 id를 변수로 따로 저장, login.html의 132줄 name="username"를 참고하세요
#         upasswd=request.form['password'] # 입력했던 password를 변수로 따로 저장, login.html의 135줄 name="password"를 참고하세요
#         try:
#             user_data = User.query.filter_by(name=uname, password=upasswd).first()
#             if user_data is not None : # 정상적으로 로그인이 된 경우 실행되는 창
#                 session['user_id']=user_data.id # 세션에 user_id 라는 변수로 user_data.id 값을 올려줍니다. 앞으로 무진장 많이쓰니 중요함
#                 session['logged_in']=True # 세션에 logged_in 이라는 변수를 True로 지정해 줍니다. 앞으로 무진장 많이쓰니 중요함
#                 return redirect(url_for('home')) # 홈으로 이동해줌, home() 뷰함수를 실행하는 것과 같음
#             else: # 정상적으로 로그인이 되지 않는경우(DB에 관련 user_data가 없는경우 None이 되므로..)
#                 error = "ID가 존재하지 않거나 비밀번호가 일치하지 않습니다."
#                 return render_template("login.html", error=error) # 왜 로그인이 안되었는지 보내줍니다.
#         except :
#             error = "DB조회중에 에러가 발생했습니다." # 예외처리를 해주지 못한 나머지 에러는 그냥 DB조회중 에러라고 책임감없는 짬처리를 해버립니다. 어차피 개발자 아니면 모르니 ㅋㅋㅋ
#                                              # 추가적으로 에러처리를 해주고싶으면 위에 try안에  elif로 추가해줘야겠쥬?
#             return render_template("login.html", error=error)

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
    
    
    
# -----------------------------------------< 미니트윗 >---------------------------------------------------------------

''' 상품안에 상품문의를 minitwit 형식으로 구현하는 함수 '''
@app.route("/single-product/<int:productid>/add_message", methods=['GET', 'POST']) # <int:productid>는 위에서 설명한 것과 동일합니다!
def single_product_QnA(productid=None):
    if not session['logged_in']: # session['logged_in'] 은 로그인 페이지에서 저장해 뒀던것을 기억하나요? 로그인 되어있다면 이 값은 True로 되어있을 것 입니다.
        return render_template("login.html")
    else:
        user_data2=[]
        user_data=User.query.filter_by(id=session['user_id']).first()
        product_data = Product.query.filter_by(id=productid).first()
        author_user=User.query.filter_by(id=product_data.author_id).first()
        heart_data = Heart.query.filter_by(product_id=productid).first()
        # Table 명과 어떤것을 filter했는지만 주목해 주시면 됩니다~
        if request.method=='POST':
            quest_msg = Message(product_id = productid, author_id=user_data.id, text=request.form['text'], pub_date=int(time.time()+time_seoul))
            # minitwit에 내용을 쓰고 등록하면 해당상품의 id, 등록한 사람 id, 등록한 내용, 등록한 날짜 를 Message table에 저장하고
            db2.session.add(quest_msg) # 그 내용을 db에 저장한 뒤에,
            db2.session.commit() # commit을 해줘야 적용됩니다. SQL과 동일한 내용인데 기억나시나요? commit하지 않으면 DB에 저장되지 않습니다.
            message_data = Message.query.filter_by(product_id=productid).order_by(desc(Message.pub_date)).all() # 이제 minitwit내용을 날짜순으로 내림차순(최신 등록한 날짜가 맨 위에오게)으로 정리해주고
            sp_long = len(message_data) # 메세지가 몇개 있는지 따로 변수로 저장해주고 (이유는 위에서 한 것과 같다, len함수를 html에서 쓸수 없으므로..)
            for i in range(sp_long):
                user_data2.append(User.query.filter_by(id=message_data[i].author_id).first()) # message_data를 토대로 minitwit 작성한 회원들의 정보를 모두 저장해줍니다.
            return render_template('single-product.html', product = product_data, now_time = int(time.time()+time_seoul), messages=message_data, user= user_data2, sp_long=sp_long, author_user=author_user, heart=heart_data)
            # 모든 변수를 single-product.html에 넘겨줍니다. 이 정보들을 활용하는 것은 single-product.html에서 쓰기 나름인데 html 보시면 어떻게 썼는지 보실수 있습니다. 이해하는데는 별로 어렵지 않으니 한번 보세요 ㅎㅎ
        else: #get 방식으로 들어온 경우는 347줄에 있는 viewProduct 함수를 실행해 줍니다.
            return redirect(url_for("viewProduct"))
    
# ------------------------------------------------------------------------------------------------------------------------

#이제 거의 같은 기능들이 반복되므로 특별한 내용이나 새로 추가된 기능이 나온것이 아니면 코멘트 달지 않을게요.. 너무 오래걸려서 ㅜ 모르면 질문해주셔도 됩니다!
''' 경매내역보기 조회페이지 '''  
@app.route("/single-product/<int:prod_bidnum>/viewbidder")
def viewbidder(prod_bidnum=None):
    user_data=[]
    product_data=[]
    bidding_data = Bidding.query.filter_by(product_id=prod_bidnum).all()
    
    b_length = len(bidding_data)
    for i in range(len(bidding_data)):
        user_data.append(User.query.filter_by(id=bidding_data[i].bidder_id).first())

    for i in range(len(bidding_data)):
        product_data.append(Product.query.filter_by(id=bidding_data[i].product_id).first())
           
    return render_template("bidder.html", bidders=bidding_data, users=user_data, products=product_data, b_length=b_length)

    
''' 마이페이지 '''
@app.route("/mypage")
def mypage():
    try:
        if session['logged_in']:
            user_data = User.query.filter_by(id=session['user_id']).first()
            return render_template("mypage.html", user=user_data)
        else:
            return render_template("login.html") 
    except:
        return render_template("login.html") 

########################## 마이페이지 여섯가지 목록 ###########################  
''' 판매내역조회 '''
@app.route("/product_sell_list/<int:user_id>")
def product_sell_list(user_id=None):
    if session['logged_in']:
        user_data = User.query.filter_by(id=session['user_id']).first()
        product_data=Product.query.filter_by(author_id=user_id).all()
        return render_template("product_sell_list.html", products = product_data, user=user_data)
    else:
        return render_template("login.html")
  
    
''' 판매상품등록  '''
@app.route("/pdregister")
def pdregister():
    try:
        if not session['logged_in']:
            return render_template("login.html")
        else:
            user_data = User.query.filter_by(id=session['user_id']).first()
            return render_template("pdregister.html", user=user_data)
    except:
        return render_template("login.html")
    
  
############################## 판매상품 등록 -> 상품등록 이미지 파일 관련 Start ################################
''' 이미지를비롯한상품등록버튼누를시에데이터DB에저장 '''     
@app.route('/pdregister/uploader', methods=['GET', 'POST'])
def pdregister_uploadFile():
    user_data = User.query.filter_by(id=session['user_id']).first()
    if request.method == 'POST':
        # 예외처리 구간
        if request.form['product_name']=='':
            error = "상품명이 입력되지 않았습니다."
            return render_template("pdregister.html", error1=error, user=user_data)
        elif (request.form['initial_price'] and request.form['direct_price'])=='':
            error = "시작가 및 즉구가를 입력해 주세요"
            return render_template("pdregister.html", error3=error, user=user_data)
        elif int(request.form['initial_price'].replace(",",""))>=int(request.form['direct_price'].replace(",","")):
            error = "즉시 구매 가격보다 높거나 같습니다."
            return render_template("pdregister.html", error2=error, user=user_data)
        elif request.form['direct_price']==0:
            error = "즉시 구매가는  적어도 1원 이상이어야 합니다."
            return render_template("pdregister.html", error3=error, user=user_data)
        elif request.form['days']=="":
            error = "게시 기간이 입력되지 않았습니다."
            return render_template("pdregister.html", error4=error, user=user_data)
        # 예외처리 끝
        
        f = request.files['product_img'] # request.files 라는 기능을 보면 pdregister.html의 214줄 에서 name="product_img" 의 내용을 가져오는데
                                         # 이때 html에서 이미 image 파일로 저장해 뒀기 때문에 그 정보를 가져옵니다.
        if f.filename == '' : # 첨부된 이미지가 없는 경우
            picture = "img/no_img.png" # 이미지가없다고 아무것도 안하면 메인화면에서 페이지에 이미지가 없는형태로 띄워주어 텅 비게 됩니다.. 정말 보기 안좋아서 img폴더에 보면 제가 따로 no_img라는 이미지 파일을 저장해 뒀습니다.
                                       # 그 경로로 picture 변수를 저장해줍니다. 꼭 no_img 파일이 있는지 확인해주세요!
        else: # 이미지가 잘 저장된경우
            picture = "./img/product_img/" + str(int(time.time()+time_seoul)) + "_" + secure_filename(f.filename) # 해당 이미지를 저장해주는데 이름을 어떻게 할 것인지 고민해 봤습니다.
                                            # 이미지 파일의 이름이 중복되면 충돌이 있어서 안됩니다. 따라서 충돌이 되지 않도록 현재날짜를 초로 환산한 time.time을 활용했습니다.
                                            # 따라서 파일이름은[현재날짜를초로 환산한 값_기존파일이름] 으로 저장될 것입니다. 위치는 img폴더의 product_img폴더 안에 저장되게 경로를 설정해줍니다.
            f.save("./static"+picture)      # 그 경로에 파일을 저장해 줍시다.
              # 파일명을 보호하기 위한 메소드에 적용시킨 후 save
        # 앞전에 제가 g.db와 db2는 다르다는 것을 기억하시나요? g.db는 flask 책에서 배운 minitwit에서 활용한 방식이고 db2는 박혜정쌤이 게시판 만들때 썼던 방식입니다. 여기서는 g.db를 썼네요 이유는 없습니다 그냥 초기에 잘 몰라서 쓴거같습니다.
        # db2로 바꿔서 적용할 수도 있는데 이는 바로 밑에 따로 적용해 두겠습니다.
        
        # minitwit 에서 g.db방식
        g.db.execute('''insert into   product(author_id, title, picture, start_val, current_val, immediate_val, days, board, now_date, bidders, state)
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (session['user_id'],
                    request.form.get('product_name'), picture, request.form.get('initial_price'),
                    request.form.get('initial_price'), request.form.get('direct_price'),
                    request.form.get('days'), request.form.get('description'), int(time.time()+time_seoul), 0,1))
        g.db.commit()
        
        # 혜정쌤의 게시판만들기에서 db2 방식
        """
        something = Product(author_id=session['user_id'], title=request.form.get('product_name'), picture=picture,
                          start_val=request.form.get('initial_price'), current_val=request.form.get('initial_price'),
                          immediate_val=request.form.get('direct_price'), days=request.form.get('days'),
                          board=request.form.get('description'), now_date=int(time.time()+time_seoul),
                          bidders=0, state=1)
        db2.session.add(something)
        db2.session.commit()
        """
        
        # 두 방식이 똑같다는 것이 이해가 되시나요? 어쨌든 둘다 가능하다는 걸 말하고 싶었습니다. 궁금하시면 주석처리 해제 후 적용해보세요^^ 테스트 완료해 뒀습니다.
        # 순수 SQL문을 써서 하고싶은사람은 minitwit방식을 써도 나쁘지 않을것 같아요
        return redirect(url_for("home"))

''' 상품수정 '''  
# picture 부분은 위에서 상품등록 할때와 같습니다. 나머지는 방식이 똑같아서 딱히 설명을 추가적으로 할 것이 없네요
@app.route("/pdregister_edit/pdnum=<int:product_id>", methods=['GET', 'POST'])
def pdregister_edit(product_id=None):
    user_data = User.query.filter_by(id=session['user_id']).first()
    product_data = Product.query.filter_by(id=product_id).first()
    message_data = Message.query.filter_by(product_id=product_id).order_by(desc(Message.pub_date)).all()
    author_user=User.query.filter_by(id=product_data.author_id).first()
    heart_data = Heart.query.filter_by(product_id=product_data.id).first()
    sp_long = len(message_data)
    if session['logged_in']:
        if request.method == 'GET':
            return render_template("pdregister_edit.html", user= user_data, product= product_data)
        else:
            edit_product = Product.query.filter_by(id=product_id).first()
            edit_product.title = request.form['product_name']
            edit_product.board = request.form['description']
            f = request.files['product_img']
            picture = "./img/product_img/" + str(int(time.time()+time_seoul)) + "_" + secure_filename(f.filename)
            if edit_product.title=='':
                return render_template("pdregister_edit.html", user= user_data, product= product_data, error = "상품이름을 입력하여 주세요")
            if secure_filename(f.filename)=='':
                edit_product.picture = product_data.picture
            else:
                edit_product.picture = picture
            db2.session.add(edit_product)
            db2.session.commit()
            f.save("./static"+picture)
            return render_template("single-product.html", user= user_data, product= product_data, now_time = int(time.time()+time_seoul), sp_long=sp_long, author_user=author_user, heart=heart_data)
    else:
        return render_template("login.html")
    
''' 등록된상품삭제 '''
@app.route('/pdregister_edit/pdnum=<int:product_id>/delete')
def pdregister_delete(product_id=None):
    user_data = User.query.filter_by(id=session['user_id']).first()
    
    products=query_db('''select product.* from product, users where product.author_id = users.id order by product.id desc ''')
    # query_db 또한 SQL문을 써서 만드는 방식입니다.. 지금보니까 왜썼지? 싶네요 지워도 써먹은데가없어서 적용될거같은데.. 일단 놔둘게요 
    
    product_data = Product.query.filter_by(id=product_id).first()
    db2.session.delete(product_data) # 새로나온 기능이네요 delete하면 일치하는 내용을 DB에서 삭제해줍니다. 간단하죠?
    db2.session.commit() # commit을 해야 적용된다는 점 잊지마세요!
    return redirect(url_for("product_sell_list", user_id = user_data.id))
    
    

############################## 판매상품 등록 -> 상품등록 이미지 파일 관련 end ################################
''' 입찰하기 '''
@app.route("/single-product/<int:productid>/getbid", methods=['GET', 'POST'])
def getbid(productid=None):
    if not session['logged_in']:
        return redirect(url_for("login"))
    product = Product.query.filter_by(id=productid).first()
    user_data = User.query.filter_by(id=session['user_id']).first() # userid 가져오기위해
    bid_data = Bidding.query.filter_by(product_id=product.id).all()
    message_data = Message.query.filter_by(product_id=productid).order_by(desc(Message.pub_date)).all()
    author_user=User.query.filter_by(id=product.author_id).first()
    heart_data = Heart.query.filter_by(product_id=productid).first()
    sp_long = len(message_data)
    flag = 0
    for bid in bid_data: # 로그인한 사용자가 이미 입찰을 했는지 여부를 체크하고 이미 입찰한 사용자라면 flag값을 1로 셋팅함
        if bid.bidder_id==user_data.id:
            flag = 1 #이미 입찰한놈임
    if request.method == 'POST':        
        if request.form['my_price']=='':
            error = "입찰 금액을 입력해 주세요"
            return render_template("single-product.html", product=product, now_time = int(time.time()+time_seoul), error = error, sp_long=sp_long, author_user=author_user, heart=heart_data)
        elif int((request.form['my_price']).replace(",",""))<=int((product.current_val).replace(",","")):
            error = "입찰가격이 현재가보다 낮습니다. 올바른 가격을 입력해 주세요"
            return render_template("single-product.html", product=product, now_time = int(time.time()+time_seoul), error = error, sp_long=sp_long, author_user=author_user, heart=heart_data)
        elif int((request.form['my_price']).replace(",",""))>=int((product.immediate_val).replace(",","")):
            error = "입찰가격이 즉시 구매가보다 높습니다. 올바른 가격을 입력해 주세요"
            return render_template("single-product.html", product=product, now_time = int(time.time()+time_seoul), error = error, sp_long=sp_long, author_user=author_user, heart=heart_data)
        else:
            bidding = Bidding(bidder_id=user_data.id, product_id=product.id, now_date=int(time.time()+time_seoul), my_price = request.form['my_price'])
            if flag: #이미 입찰한 사람이라면 입찰가격과 현재 날짜만 수정하고 리턴해줌
                # update set where 문으로 지정된 product의 price를 수정하는 코드 추가
                g.db.execute('''update bidding set my_price = ?, now_date = ? where product_id = ? and bidder_id = ?''',(request.form['my_price'], int(time.time()+time_seoul), product.id, user_data.id))
                g.db.commit()
            else:
                product.bidders+=1
                db2.session.add(bidding)
                db2.session.commit()
            g.db.execute('''update product set current_val = ? where id = ?''', (request.form['my_price'], product.id ))
            g.db.commit() # 입력받은 입찰가를 product의 현재가(currenct_val)에 대입하여 update 시켜준다  
            return redirect(url_for("bid_list"))
    else:
        return redirect(url_for("home"))
    
''' 입찰 내역 '''
@app.route("/bid_list")
def bid_list():
    user_data = User.query.filter_by(id=session['user_id']).first()
    bid_data = Bidding.query.filter_by(bidder_id=user_data.id).all()
    product_data=[]
    for bid in bid_data:
        product_data.append(Product.query.filter_by(id=bid.product_id).first())
    if session['logged_in']:
        return render_template("bid_list.html", user = user_data, bidding = bid_data, product=product_data, p_long = len(product_data))
    else:
        return render_template("login.html")
    
''' 즉시구매하기 '''
@app.route("/single-prodict/<int:product_id>/getitem", methods=['GET', 'POST'])
def getitem(product_id=None):
    if not session['logged_in']:
        return redirect(url_for("login"))
    user_data = User.query.filter_by(id=session['user_id']).first()
    product_data = Product.query.filter_by(id=product_id).first()
    bidding_data = Bidding.query.filter_by(bidder_id=user_data.id, product_id=product_data.id).first()

    if bidding_data==None: #입찰한 적이 없는 사람이었다면
        bidding_date = int(time.time()+time_seoul)
        bidding_myprice = product_data.immediate_val
    else:
        bidding_date = bidding_data.now_date
        bidding_myprice = product_data.immediate_val
    product_data.state = 0 # 낙찰 상태로 바꿔줌
#     product_data.now_date = product_data.now_date-86400*product_data.days #즉시구매시 타이머 종료
    db2.session.commit()
    g.db.execute('''insert into   sbid(product_id, sbidder_id, sbid_price, sbid_date, bidding_date, my_price)
                    values (?, ?, ?, ?, ?, ?)''', ( product_data.id, user_data.id, product_data.immediate_val, int(time.time()+time_seoul), bidding_date, bidding_myprice) )
    g.db.commit()
#     sbid_data = Sbid.query.filter_by(sbidder_id=user_data.id).all()
    return redirect(url_for("sbid_list"))


''' 낙찰내역  '''
@app.route("/sbid_list")
def sbid_list():
    product_data=[]
    author=[]
    user_data = User.query.filter_by(id=session['user_id']).first()
    sbid_data = Sbid.query.filter_by(sbidder_id = user_data.id).all()
    s_long = len(sbid_data)
    for i in range(s_long):     
        product_data.append(Product.query.filter_by(id=sbid_data[i].product_id).first())
    for i in range(s_long):
        author.append(User.query.filter_by(id=product_data[i].author_id).first())
    return render_template("sbid_list.html", user=user_data, sbid=sbid_data, product=product_data, s_long=s_long, author=author)


''' 결제내역  '''
@app.route("/payment_list")
def payment_list():
    product_data = []
    author = []
    user_data = User.query.filter_by(id=session['user_id']).first()
    payment_list = Payment.query.filter_by(bidder_id=user_data.id).all() # 입찰한 사용자 기준으로 모든정보 가져옴
    pl_long = len(payment_list)
    for i in range(pl_long):
        product_data.append(Product.query.filter_by(id=payment_list[i].product_id).first()) #입찰한 제품의 정보를 축적한다.
    for i in range(pl_long):
        author.append(User.query.filter_by(id=product_data[i].author_id).first())
    
    return render_template("payment_list.html", payment = payment_list, user=user_data, product = product_data, author = author ,pl_long=pl_long)

""" 결제하기 누르면 """
@app.route("/pay_for/<int:product_id>")
def pay_for(product_id=None):
    user_data = User.query.filter_by(id=session['user_id']).first()
    product_data=Product.query.filter_by(id=product_id).first()
    return render_template("pay_for.html", user=user_data, product=product_data)
    
''' 결제완료 '''
@app.route("/payment_for/<int:productid>/complete", methods=['GET', 'POST'])
def payment_complete(productid=None):
    user_data = User.query.filter_by(id=session['user_id']).first()
    product_data=Product.query.filter_by(id=productid).first()
    sbid_data = Sbid.query.filter_by(product_id=product_data.id).first()
    new_payment= Payment(product_id = product_data.id,
                            sbid_price = sbid_data.sbid_price,
                            bidder_id = user_data.id,
                            email = user_data.email,
                            phone = user_data.phone,
                            address = user_data.address,
                            pay_date = int(time.time()+time_seoul) )
    post = Sbid.query.filter_by(product_id=product_data.id).first()
    db2.session.delete(post)
    db2.session.add(new_payment)
    db2.session.commit()
    payment_list = Payment.query.filter_by(bidder_id=user_data.id).all() 
    return redirect(url_for("payment_list"))


""" 낙찰 취소 """
@app.route("/sbid_list/sbid_delete/<int:productid>", methods=['GET', 'POST'])
def sbid_delete(productid=None):
    # 낙찰성공 내역 취소하는 내용 추가 필요
    user_data=User.query.filter_by(id=session['user_id']).first()
    sbid_data=Sbid.query.filter_by(product_id=productid).first()
    product_data=Product.query.filter_by(id=productid).first()
    db2.session.delete(sbid_data)
    product_data.state = 1
    db2.session.commit() 
    return redirect(url_for("sbid_list"))

''' 회원정보수정  '''
@app.route("/mchange", methods=['GET', 'POST'])
def mchange():
    try:
        user_data = User.query.filter_by(id=session['user_id']).first()
        if not session['logged_in']:
            return render_template("login.html") #로그인 안되어 있으면 로그인 화면으로
        if request.method == 'GET':
            return render_template("mchange.html", user=user_data)
        else:
            edit_user = User.query.filter_by(id=session['user_id']).first()
            edit_user.password = request.form['password']
            edit_user.email = request.form['emailid']+'@'+request.form['emailadd']
            edit_user.phone = request.form['txtMobile1']+'-'+request.form['txtMobile2']+'-'+request.form['txtMobile3']
            edit_user.address = request.form['address']

            if (request.form['password'] and request.form['emailid'] and request.form['emailadd'] and request.form['txtMobile1'])=='' or (len(request.form['txtMobile2'])<3 or len(request.form['txtMobile3'])<4) :
                if request.form['password'] == '':
                    error = "비밀번호란이 입력되지 않았습니다."
                    return render_template("mchange.html", error=error, user=user_data)
                elif (request.form['emailid'] or request.form['emailadd']) == '' :
                     error = "E-mail란이 입력되지 않았습니다."
                     return render_template("mchange.html", error=error, user=user_data)
                elif (request.form['txtMobile1']==''):
                     return render_template("mchange.html", error = "핸드폰번호 앞자리가 선택되지 않았습니다.", user=user_data)
                elif (len(request.form['txtMobile2'])<3 or len(request.form['txtMobile3'])<4):
                    return render_template("mchange.html", error="핸드폰 번호 양식이 맞지 않습니다.", user=user_data)
            if request.form['password'] == request.form['confirmPassword']:
                db2.session.add(edit_user)
                db2.session.commit()
                return redirect(url_for("home"))
            else:
                error = "입력하신 비밀번호와 비밀번호 확인값이 일치하지 않습니다."
                return render_template("mchange.html", error=error, user=user_data)
    except:
        return render_template("login.html")
        
###############장바구니에 담는 소스 코드 작성 START #########################
""" 카트추가 """
@app.route("/single-product/<int:productid>/addcart")
def add_cart(productid=None):
    if not session['logged_in']:
        return redirect(url_for("login"))
    user_data = User.query.filter_by(id=session['user_id']).first()
    product_data = Product.query.filter_by(id=productid).first()
    message_data = Message.query.filter_by(product_id=productid).order_by(desc(Message.pub_date)).all()
    author_user=User.query.filter_by(id=product_data.author_id).first()
    heart_data = Heart.query.filter_by(product_id=productid).first()
    cart_data = Cart.query.filter_by(productId=product_data.id, userId=user_data.id).first()
    sp_long = len(message_data)
    
    if Heart.query.filter_by(product_id=product_data.id).first() == None: #만약 한번도 찜에 올라온 데이터가 아니라면 행에 추가해준다
        heart = Heart(product_id = product_data.id, heart_cnt=0)
        db2.session.add(heart)
        db2.session.commit()   
    if cart_data==None:
        carts = Cart(productId=product_data.id, userId=session['user_id'])
        heart = Heart.query.filter_by(product_id=product_data.id).first()
        heart.heart_cnt+=1
        db2.session.add(heart)
        db2.session.add(carts)
        db2.session.commit()
        return redirect(url_for('favorite_list'))
    else:
        return render_template("single-product.html", user= user_data, product= product_data, now_time = int(time.time()+time_seoul), error="이미 찜목록에 있는 상품입니다.",sp_long=sp_long, author_user = author_user, heart=heart_data)
        

''' 찜목록 삭제 '''
@app.route("/favorite_list/<int:product_id>/delete")
def delete_cart(product_id=None):
    user_data=User.query.filter_by(id=session['user_id']).first()
    product_data=Product.query.filter_by(id=product_id).first()
    cart_data = Cart.query.filter_by(productId=product_data.id, userId=user_data.id).first()
    heart_data = Heart.query.filter_by(product_id=product_data.id).first()
    heart_data.heart_cnt-=1
    db2.session.delete(cart_data)
    db2.session.commit()
    return redirect(url_for("favorite_list"))

''' 찜목록 '''
@app.route("/favorite_list")
def favorite_list():
    user_data = User.query.filter_by(id=session['user_id']).first()
    cart_data = Cart.query.filter_by(userId=session['user_id']).all()
    product_data = []
    for cart in cart_data:
        product_data.append(Product.query.filter_by(id=cart.productId).first())
    return render_template("favorite_list.html", user=user_data, products=product_data)

###############장바구니에 담는 소스 코드 작성 END ############################ 

''' 내가보낸문의 '''
############################################################################################
@app.route("/myboard", methods=['GET', 'POST'])
def boardlist():
    user_data = User.query.filter_by(id=session['user_id']).first()
    try:
        if session['logged_in']:
            boardlist = Boards.query.order_by(desc(Boards.id)).all()
            return render_template("myboard.html", user=user_data, boards = boardlist)
        else:
            return render_template("login.html")
    except:
        return render_template("login.html")
    
@app.route("/myboard/new")
def boardNew():
    user_data=User.query.filter_by(id=session['user_id']).first()
    return render_template("myboard_form.html", user=user_data)

@app.route("/myboard/add" , methods=['GET', 'POST'])
def addPost():  
    new_post = Boards(writer=request.form['writer'], title = request.form['title'],   content = request.form['content'] , regdate = int(time.time()+time_seoul), reads=0)
    db2.session.add(new_post)
    db2.session.commit()                                           
    return redirect(url_for("boardlist"))   #get요청
#get요청

@app.route("/myboard/view/<int:bbs_id>")
def viewMyboard(bbs_id=None):
    user_data=User.query.filter_by(id=session['user_id']).first()
    post = Boards.query.filter_by(id=bbs_id).first()
    post.reads=post.reads+1
    db2.session.commit()
    return render_template("myboard_view.html", bbs = post, user=user_data)

@app.route("/myboard/edit",methods=['POST', 'GET'])
def editPost():
    user_data=User.query.filter_by(id=session['user_id']).first()
    post = Boards.query.filter_by(id=request.form["bbsid"]).first()
    return render_template("myboard_edit.html",bbs=post, user=user_data)

@app.route("/myboard/save", methods=['POST', 'GET'])
def savePost():
    post = Boards.query.filter_by(id=request.form["bbsid"]).first()
    post.title = request.form["title"]
    post.content = request.form["content"]
    #post.reads=post.reads+1
    db2.session.commit()
    return redirect(url_for("boardlist"))

@app.route("/myboard/delete/<int:bbsid>", methods=['POST','GET'])
def removePost(bbsid=None):
    post = Boards.query.filter_by(id=bbsid).first()
    db2.session.delete(post)
    db2.session.commit()
    return redirect(url_for("boardlist"))         
#################################################################

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
    app.run(host='0.0.0.0') #본인의 ip로 접속할 수 있게 해줍니다.
