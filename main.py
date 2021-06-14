from flask import *
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from flask_mongoengine import MongoEngine
from colorama import init, Fore
init()
from form import LoginForm
from werkzeug.urls import url_parse

def cprint(color,obj):
    colors = {
        "r": Fore.RED,
        "g": Fore.GREEN,
        "b": Fore.BLUE,
    }

    print(colors[color],obj,Fore.RESET)

app = Flask(__name__, template_folder='templates')
app.config['MONGODB_SETTINGS'] = {
    'db': 'observers_log',
    'host': 'localhost',
    'port': 27017,
}
app.secret_key = 'some key'

db = MongoEngine()
db.init_app(app)

login  = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()

class User(UserMixin,db.Document):
    meta = {"collection":"users"}
    username = db.StringField()
    password = db.StringField()
    email = db.StringField()

    # def to_json(self):
    #     return {"username": self.username,
    #             "email": self.email}
    
    # def is_authenticated(self):
    #     return True
    
    # def is_active(self):
    #     return True
    
    # def is_anonymous(self):
    #     return False
    
    # def get_id(self):
    #     return str(self.id)



# ============================================================
#                           Routes
# ============================================================
@app.route("/index")
@login_required
def index():
    return render_template("index.html")
# -------------------------------------------------------------

@app.route("/")
@app.route('/login', methods=['POST',"GET"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        cprint("r",form.username.data)
        cprint("r",form.password.data)
        
        user = User.objects(username=form.username.data).first()
        cprint("r",user)

        if user is None:# or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        
        login_user(user,remember=form.remember_me.data)
        cprint("r",form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
            
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)
# -------------------------------------------------------------

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
# -------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="80")