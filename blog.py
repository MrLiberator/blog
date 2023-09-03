import mysql.connector
from functools import wraps
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request

# ----------------- Veritabanı Bağlantısı ----------------- #
con = mysql.connector.connect(
  host="31.186.11.139",
  user="kitc9listecomtr_denemee",
  password="!Deneme123",
  db="kitc9listecomtr_deneme")
# --------------------------------------------------------- #

# --------------------- Form İşlemleri -------------------- #

# Kayıt Olma Formu
class RegisterForm(Form):
    name = StringField("İsim: ",validators=[
        validators.DataRequired("Lütfen İsiminizi Giriniz!"),
        validators.Length(min=3)
    ])
    username = StringField("Kullanıcı Adı: ",validators=[
        validators.DataRequired("Lütfen Kullanıcı Adınızı Giriniz!"),
        validators.Length(min=3)
    ])
    email = StringField("E-Posta: ",validators=[
        validators.Email("Lütfen Geçerli Bir E-Posta Adresi Giriniz!"),
        validators.DataRequired("Lütfen E-Posta Adresinizi Giriniz!")
    ])
    password = PasswordField("Parola: ",validators=[
        validators.Length(min=6),
        validators.EqualTo(fieldname="confirm"),
        validators.DataRequired("Lütfen Bir Parola Belirleyiniz!")
    ])
    confirm = PasswordField("Parola Doğrula: ",validators=[
        validators.DataRequired("Lütfen Parolanızı Tekrar Giriniz!")
    ])

# Giriş Yapma Formu
class LoginForm(Form):
    username = StringField("Kullanıcı Adı: ")
    password = PasswordField("Parola: ")

# Makale Ekleme Formu
class AddArticle(Form):
    title = StringField("Makale Başlığı",validators=[
        validators.DataRequired("Lütfen Makalenize Başlık Giriniz!"),
        validators.Length(min=5)
    ])
    content = TextAreaField("Makale İçeriği",validators=[
        validators.DataRequired("Lütfen Makalenizin İçeriğini Oluşturunuz!"),
        validators.Length(min=180,max=3000)
    ])
# --------------------------------------------------------- #

# Uygulama
app = Flask(__name__)

# Secret Key
app.secret_key = 'wqEqewqe231w21313&+%'

# Kullanıcı Giriş Zorunluluğu
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "loggin" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu Sayfayı Görüntülemek İçin Lütfen Giriş Yapınız!","danger")
            return redirect(url_for("login"))
    return decorated_function

# ------------------- Konum Bağlantısı -------------------- #
# Anasayfa
@app.route("/")
def index():
    return render_template("index.html")

# Hakkımızda
@app.route("/about")
def about():
    return render_template("about.html")

# Kayıt Ol
@app.route("/register", methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = con.cursor()
        sorgu = "SELECT * FROM users WHERE username = %s;"
        cursor.execute(sorgu,(username,))
        data = cursor.fetchone()

        if data == None:
            data = 0
            sorgu = "INSERT INTO users(name,username,email,password) VALUES(%s,%s,%s,%s)"
            cursor.execute(sorgu,(name,username,email,password))
            con.commit()
            cursor.close()
            flash("Kayıt Başarıyla Yapıldı!","success")
            return redirect(url_for("index"))
        else:
            flash("Kullanıcı Adı Kullanılmaktadır. Lütfen Farklı Bir Kullanıcı Adı Belirleyiniz!","warning")
            return(redirect(url_for("register")))
    else:
        return render_template("register.html",form = form)

# Giriş Yap
@app.route("/login", methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        entred_password = form.password.data
        sorgu = "Select * From users where username = %s"
        cursor = con.cursor(dictionary=True)
        cursor.execute(sorgu,(username,))
        data = cursor.fetchone()
        if data == None:
            flash("Kullanıcı Adı Bulunamadı!","warning")
            return(redirect(url_for("login")))
        else:
            real_password = data["password"]
            if sha256_crypt.verify(entred_password,real_password):
                flash("Kullanıcı Girişi Başarılı!","success")
                session["loggin"] = True
                session["username"] = username
                return redirect(url_for("index"))
            else:
                flash("Kullanıcı Adı Veya Parola Hatalı Lütfen Tekrar Giriş Yapınız!","danger")
                return redirect(url_for("login"))
    else:
        return render_template("login.html",form=form)

# Çıkış Yap
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

# Kontrol Paneli
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# Makale Ekleme
@app.route("/addarticle", methods = ["GET","POST"])
@login_required
def addarticle():
    form = AddArticle(request.form)
    if request.method == "POST":
        title = form.title.data
        content = form.content.data

        sorgu = "Insert Into articles(title,author,content) Values(%s,%s,%s)"
        cursor = con.cursor()
        cursor.execute(sorgu,(title,session["username"],content))
        con.commit()
        cursor.close()
        flash("Makale Başarıyla Eklendi!","success")
        return redirect(url_for("dashboard"))
    else:
        return render_template("addarticle.html",form = form)

@app.route("/deneme")
@login_required
def deneme():
    return render_template("deneme.html")
# --------------------------------------------------------- #

# Konsol'da Çalıştırma
if __name__ == "__main__":
    app.run()
