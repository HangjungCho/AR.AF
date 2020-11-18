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
    user_name = db2.Column(db2.String) 
    password = db2.Column(db2.String)

    def __init__(self, user_id, user_name, password):
        self.user_id = user_id
        self.user_name = user_name
        self.password = password

    def __repr__(self):
        return"<User('%s', %s, '%s')>" % (self.user_id, self.user_name, self.password)
 #=============================================================================================

# ====================================== Quantity =============================================
class Quantity(db2.Model):
    __tablename__ = 'Quantity'
    
    ID = db2.Column(db2.Integer, primary_key = True)
    p_type = db2.Column(db2.String)
    cal = db2.Column(db2.String)
    count = db2.Column(db2.Integer)
    error = db2.Column(db2.Integer)
    date = db2.Column(db2.String)
    time = db2.Column(db2.String)
    img = db2.Column(db2.String)

    def __init__(self, p_type, cal, count, error, date, time, img):
        self.p_type = ptype
        self.cal = cal
        self.count = count
        self.error = error
        self.date = date
        self.time = time
        self.img = img

    def __repr__(self):
        return"<Quantity('%s', '%s', '%d', '%d', '%s', '%s', '%s')>" % (self.p_type, self.cal, self.count, self.error, self.date, self.time, self.img)
# =============================================================================================

# ======================================== Count ==============================================
class Count(db2.Model):
    __tablename__ = 'Count'
    
    ID = db2.Column(db2.Integer, primary_key = True)
    p_type = db2.Column(db2.String)
    num = db2.Column(db2.Integer)
    img = db2.Column(db2.String)
 
    def __init__(self, p_type, num, img):
        self.p_type = p_type
        self.num = num
        self.img = img
   
    def __repr__(self):
        return"<Count('%s', '%d', '%s')>" % (self.p_type, self.num, self.img)
# =============================================================================================   

# ======================================== ErrStat ==============================================
class ErrStat(db2.Model):
    __tablename__='ErrStat'

    ID = db2.Column(db2.Integer, primary_key=True)
    p_type = db2.Column(db2.String)
    num = db2.Column(db2.Integer)

    def __init__(self, p_type, num):
        self.p_type = p_type
        self.num = num
    
    def __repr__(self):
        return"<ErrStat('%s', '%d')>" % (self.p_type, self.num)
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
        u_id=request.form['email']
        u_passwd=request.form['password']
#         try:
        user_data = User.query.filter_by(user_id=u_id, password=u_passwd).first()

        if user_data is not None : # 정상적으로 로그인이 된 경우 실행되는 창
            session['user_id']=user_data.ID
            session['logged_in']=True
    
    #           productlist = db2.session.query(Quantity).filter(Quantity.p_type.like('%')).all()
            return redirect(url_for('home'))
#             return render_template("index.html", user=user_data, products = product_data)
        else: # 정상적으로 로그인이 되지 않는경우(DB에 관련 user_data가 없는경우 None이 되므로..)
            error = "ID 혹은 비밀번호가 일치하지 않습니다."
            return render_template("login.html", error=error) # 왜 로그인이 안되었는지 보내줍니다.
#         except :
#             error = "DB조회중에 에러가 발생했습니다." # 예외처리를 해주지 못한 나머지 에러는 그냥 DB조회중 에러라고  짬처리
#             return render_template("login.html", error=error)

@app.route("/main", methods=['GET', 'POST'])
def home():
    if not session['logged_in']: # session['logged_in'] 은 로그인 페이지에서 저장해 뒀던것을 기억하나요? 로그인 되어있다면 이 값은 True로 되어있을 것 입니다.
        return redirect(url_for('login'))
    else:

        user_data=User.query.filter_by(ID=session['user_id']).first()
        product_count_data = Count.query.filter(Count.p_type.isnot('ERR_001')).all()
        product_data = Quantity.query.filter_by(p_type='ERR_001').all()
        error_products = Quantity.query.filter_by(error=1).all()
        error_states = ErrStat.query.filter_by().all()
        product_len = len(error_states)

 
        return render_template("index.html", user=user_data,
                                             products_count = product_count_data,
                                             products = product_data,
                                             error_products = error_products,
                                             error_states = error_states,
                                             product_len=product_len)
    


@app.route('/productmanagement')
def productManagement():
    if not session['logged_in']:
        return redirect(url_for('login'))
    else:
        user_data = User.query.filter_by(ID = session['user_id']).first()
        product_data = Quantity.query.filter_by(error=0).all()
        categories = Count.query.filter().all()
        # categories = Count.query.filter(Count.p_type.isnot('ERR_001')).all()
        return render_template("product_management.html", user=user_data,
                                                          products = product_data,
                                                          categories = categories)


"""제품 자세히 보기"""4
@app.route("/main/view_detail/<int:productid>", methods=['GET','POST'])
def view_detail(productid=None):
    product_data = Quantity.query.filter_by(ID=productid).first() # 해당 물품정보를 DB에서 가져옴
    return render_template("view.html", product = product_data)


"""제품 출고"""
@app.route("/productmanagement/release", methods=['GET', 'POST'])
def release():
    if not session['logged_in']:
        return redirect(url_for('login'))
    else:
        release_product_info = request.form['release_list']
        for product in release_product_info:
             product_data = Quantity.query.filter_by(p_type = product).first()
             db2.session.delete(product_data)
        return redirect(url_for('productManagement'))

""" 카테코리 삭제 """
@app.route("/productmanagement/<int:category_id>", methods=['GET', 'POST'])
def del_category(category_id=None):
    if not session['logged_in']:
        return redirect(url_for('login'))
    else:
        category_data = Count.query.filter_by(ID=category_id).first()
        product_data = Quantity.query.filter_by(p_type=category_data.p_type).all()
        errstat_data = ErrStat.query.filter_by(p_type=category_data.p_type).first()
        print(product_data)
        print(errstat_data)
        db2.session.delete(category_data)
        for product in product_data:  
            db2.session.delete(product)
        db2.session.delete(errstat_data)
        db2.session.commit()
        
        return redirect(url_for('productManagement'))
        
# """에러 리포트"""
# @app.route("/productmanagement/report", methods=['GET', 'POST'])
# def report():
#     if not session['logged_in']:
#         return redirect(url_for('login'))
#     else:
#         report_product_info = request.form['release_list']
#         for product in report_product_info:
#             product_data = Quantity.query.filter_by(p_type=product).first()
#             product_data.error = 1


""" 회원가입 """
@app.route("/register", methods=['GET', 'POST'])
def register():
    """get방식  요청은 reighter.html 응답 전송 post 방식 요청은 db에 회원 정보 추가하고 login페이지로 redirect시킵니다"""
    if request.method=='POST': #회원가입 페이지에 회원가입 누르면 모든 정보들을 저장해 줍니다. 
        # User Class 기반의 내용들을 이용하여 저장
        new_user = User(user_id= request.form['email'],
                        user_name=request.form['username'],
                        password = request.form['password'])

        if (request.form['username'] and request.form['password'] and request.form['email']) == '':
            if  request.form['username'] == '':
                error = "ID는 필수 입력 사항입니다."
                return render_template("register.html", error=error)
            elif request.form['password'] == '':
                error = "비밀번호는 필수 입력 사항입니다."
                return render_template("register.html", error=error)
            elif (request.form['email']) == '' :
                error = "E-mail은 필수 입력 사항입니다."
                return render_template("register.html", error=error)


        # 각종 에러처리, 회원ID를 입력 안했건, 비밀번호를 입력하지 않았건, email을 입력하지 않았건 회원가입하지 못하게 해줍시다!
        
        if request.form['password']==request.form['confirmpassword']: # 비밀번호 확인이 일치하면 commit 시킨다. 
            db2.session.add(new_user)
            db2.session.commit()
            return redirect(url_for("login"))
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
    return redirect(url_for('login'))

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


# 메인함수
if __name__ == '__main__':
    app.debug=True # Debug 활성화
#     db2.create_all() #테이블이 생성되고 나서는 주석처리해줌
    app.secret_key = '1234567890'
    app.run(debug=False, host='0.0.0.0') #본인의 ip로 접속할 수 있게 해줍니다.
