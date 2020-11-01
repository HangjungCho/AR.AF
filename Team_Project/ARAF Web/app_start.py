from sqlalchemy import create_engine

# 거의 핵심 기능들을 import 하는데 밑에서 쓰는 것을 보면 알겠지만 주로 db에 연결하거나 주소 경로 설정할때 많이 쓰인다
from flask import Flask, url_for, render_template, request, redirect, session, jsonify, make_response, abort, g, flash


from flask_sqlalchemy import SQLAlchemy
from pip._vendor.appdirs import user_data_dir
from sqlalchemy import desc

# 날짜를 계산을 위한 라이브러리
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

""" 홈(로그인) """
@app.route("/", methods=['GET','POST'])
def home():
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

                productlist = db2.session.query(Quantity).filter(Quantity.p_type.like('%')).all()
                return redirect(url_for("search_product"))
            else: # 정상적으로 로그인이 되지 않는경우(DB에 관련 user_data가 없는경우 None이 되므로..)
                error = "ID가 존재하지 않거나 비밀번호가 일치하지 않습니다."
                return render_template("login.html", error=error) # 왜 로그인이 안되었는지 보내줍니다.
        except :
            error = "DB조회중에 에러가 발생했습니다." # 예외처리를 해주지 못한 나머지 에러는 그냥 DB조회중 에러라고  짬처리
            return render_template("login.html", error=error)



""" 검색페이지 """
@app.route("/search", methods=['GET','POST'])
def search_product():
    if session['logged_in']==True:
        if request.method=='POST': 
            # 받아온 날짜 값
            product_name = request.form.get('search') 
            product_startdate = request.form.get('startdate')
            product_enddate = request.form.get('enddate')

            if product_startdate and product_enddate == '':
                error = "날짜를 입력해주세요"
                return render_template("search.html", error = error)
            # string(a) -> timestamp(b) -> datetime(c) -> string(d)
            #예시
            a = '2020-10-10' # string
            b = time.mktime(datetime.strptime(a, '%Y-%m-%d').timetuple()) # timestamp
            c = datetime.fromtimestamp(b) # datetime
            d = datetime.strftime(c, '%Y-%m-%d') # string

            # datetime 변환 값
            #strp_startdate = time.mktime(datetime.strptime(product_startdate, '%Y-%m-%d').timetuple())
            #strp_enddate = time.mktime(datetime.strptime(product_enddate, '%Y-%m-%d').timetuple())
            #print("p_name : {}".format(product_name))
            #print("startdate : {}".format(strp_startdate))
            #print("enddate : {}".format(strp_enddate))

            productlist = db2.session.query(Quantity).filter(Quantity.p_type.like('%'+product_name+'%')).all()
            return render_template("search.html", products=productlist)  
        else: # GET한 순간 모든 상품을 보여줌
            productlist = db2.session.query(Quantity).filter(Quantity.p_type.like('%')).all()
            return render_template("search.html", products=productlist)
    else:
        return redirect(url_for('home'))



""" 로그아웃 """    
@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['user_id'] = None
    return redirect(url_for('home'))


# 메인함수
if __name__ == '__main__':
    app.debug=True # Debug 활성화
#     db2.create_all() #테이블이 생성되고 나서는 주석처리해줌
    app.secret_key = '1234567890'
    app.run(debug=False, host='0.0.0.0') #본인의 ip로 접속할 수 있게 해줍니다.
