from flask import Flask, render_template,flash,redirect,url_for,session,logging,request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DateField
from passlib.hash import sha256_crypt
from functools import wraps
import os
from werkzeug.utils import secure_filename
import datetime
from flask_sqlalchemy import SQLAlchemy


app=Flask(__name__)


app.secret_key="ybblog"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////Users/rihanna/Masaüstü/YBBLOG - Kopya/blog.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            
            return f(*args, **kwargs)
        else:
            flash("lütfen giriş yapınız!","danger")
            return redirect(url_for("login"))
    return decorated_function
class BlogUsers(db.Model):
   id = db.Column(db.Integer,primary_key = True)
   name = db.Column(db.String)
   username = db.Column(db.String)
   email = db.Column(db.String)
   location= db.Column(db.String)
   job=db.Column(db.String)
   date=db.Column(db.String)
   password = db.Column(db.String)
   img=db.Column(db.String)

class BlogArticles(db.Model):
   id = db.Column(db.Integer,primary_key=True)
   title = db.Column(db.String)
   author = db.Column(db.String)
   content = db.Column(db.String)
   now = datetime.datetime.now()
   date = datetime.datetime.strftime(now,"%x")

   created_date = db.Column(db.String,default= date)
class BlogComment(db.Model):
   id = db.Column(db.Integer,primary_key=True)
   kod = db.Column(db.String)
   username = db.Column(db.String)
   content = db.Column(db.String)    
   now = datetime.datetime.now()
   date = datetime.datetime.strftime(now,"%x")
   created_date = db.Column(db.String,default= date)
   img = db.Column(db.String)


   
#anasayfa
@app.route("/")
def index():
    return render_template("index.html")

#kontrol paneli
@app.route("/dashboard")
@login_required
def dashboard():
    result = BlogArticles.query.filter_by(author = session["username"])
    
    if result != None:
        articles=result
        return render_template("dashboard.html",articles=articles)
    else:
        flash("Makaleniz bulunmamaktadır!","warning")
        return render_template("dashboard.html")
#hakkımda
@app.route("/about")
def about():
    return render_template("about.html")
class RegisterForm(Form):
    name = StringField("isim soyisim",validators=[validators.Length(min=5,max=30)])
    username = StringField("kullanıcı adı",validators=[validators.Length(min=5,max=30)])
    email = StringField("Email",validators=[validators.Email(message="lütfen geçerli bir email giriniz!")])
    password = PasswordField("parola",validators=[
    validators.data_required(message="lütfen bir parola yazınız"),
    validators.EqualTo(fieldname="confirm",message="parolayı hatalı")    
    ])
    confirm = PasswordField("parola doğrula")
    date=DateField("doğum tarihi",format=r"%d/%m/%Y")
    job = StringField("meslek",validators=[validators.Length(min=1,max=30)])
    location = StringField("yaşadığınız yer",validators=[validators.Length(min=1,max=30)])
#kayıt olma formu
@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method=="POST" and form.validate():
        name = form.name.data.upper()
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.hash(form.password.data)
        date=form.date.data
        job=form.job.data.upper()
        location=form.location.data.upper()
        img=""
        result=BlogUsers.query.filter_by(username=username).first()
        if result == None:
        
            user = BlogUsers(name = name,username = username,email = email,password = password,location=location,job=job,date=date,img=img)
            db.session.add(user)
            db.session.commit()

            flash("başarıyla kayıt oldunuz...","success")
            return redirect(url_for("login"))

        else:
            flash("bu kullanıcı ismi kullanılmış","danger")
            return redirect(url_for("index"))

    

    else:

        return render_template("register.html",form=form)
class LoginForm(Form):
    username=StringField("kullanıcı adı")
    password=PasswordField("parola")
#giriş yapma formu
@app.route("/login", methods=["GET","POST"])
def login():
    form=LoginForm(request.form)
    if request.method=="POST":
        username=form.username.data
        password_endered=form.password.data
        result=BlogUsers.query.filter_by(username=username).first()
        if result != None:
            real_password=result.password
            if sha256_crypt.verify(password_endered,real_password):
                
                session["logged_in"]=True
                session["username"]=username
                flash("başarıyla giriş yaptınız...","success")
                return redirect("/user/"+username)
            else:
                flash("parola yanlış girilmiştir","danger")
                return redirect(url_for("login"))

        else:
            flash("kullanıcı girişi hatalı!","danger")
            return redirect(url_for("login"))
    
    return render_template("login.html",form=form)
#çıkış işlemi
@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("yine bekleriz...","success")
    return redirect(url_for("index"))

#makale sayfası
@app.route("/articles")
def articles():
    result=BlogArticles.query.all()
    
    if result != []:
        articles=BlogArticles.query.all()
        return render_template("articles.html",articles=articles)

    else:
        print(result)
        flash("makale bulunmamaktır!","warning")
        return render_template("articles.html")
class CommentForm(Form):
    comment=TextAreaField("",validators=[validators.data_required()])
  
#makale detay sayfası
@app.route("/article/<string:id>",methods=["GET","POST"])
def articledetay(id):
    if request.method=="GET":
        article = BlogArticles.query.filter_by(id = id).first()
        comment = BlogComment.query.filter_by(kod = id)
        if article != None:
            if session:
                form=CommentForm(request.form)       
                return render_template("article.html",form=form,article=article,comment=comment)
            else:
                form=""
                return render_template("article.html",form=form,article=article,comment=comment)

        else:
            flash("makale bulunamadı!","danger")
            return render_template("index.html")
    else:
        

        form=CommentForm(request.form)

        comment=form.comment.data
        user = BlogUsers.query.filter_by(username=session["username"]).first()
        img=user.img
        comment=BlogComment(kod=id, username=session["username"], content=comment, img=img)
        db.session.add(comment)
        db.session.commit()
        return redirect("/article/"+str(id))
        

class ArticleForm(Form):
    title=StringField("Makale Başlığı",validators=[validators.data_required()])
    content=TextAreaField("Makale İçeriği",validators=[validators.data_required()])

#makale ekleme
@app.route("/addarticle", methods=["GET","POST"])
@login_required
def addarticle():
    form=ArticleForm(request.form)
    if request.method=="POST" and form.validate():
        title=form.title.data
        content=form.content.data
        article = BlogArticles(title = title,author = session["username"],content = content)
        db.session.add(article)
        db.session.commit()
        flash("Makale başarıyla eklendi...","success")
        return redirect(url_for("dashboard"))

    return render_template("addarticle.html",form=form)
#makale silme
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    result = BlogArticles.query.filter_by(id = id,author = session["username"]).first()
    if result != None :
        db.session.delete(result)
        db.session.commit()

        return redirect(url_for("dashboard"))
    else:
        flash("böyle bir makale yok veya silme yetkiniz bulunmamaktadır!","danger")
        return redirect(url_for("index"))

#makale güncelleme
@app.route("/edit/<string:id>", methods=["GET","POST"])
@login_required
def update(id):
    if request.method=="GET":
        article = BlogArticles.query.filter_by(id = id,author = session["username"]).first()
        if article != None:
            form=ArticleForm()
            form.title.data=article.title
            form.content.data=article.content
            return render_template("update.html",form=form)
        else:
            flash("böyle bir makale bulunmamaktadır, veya güncelleme yetkiniz bulunmamaktadır!","danger")
            return redirect(url_for("index"))
    else:
        form=ArticleForm(request.form)
        newtitle=form.title.data
        newcontent=form.content.data
        article = BlogArticles.query.filter_by(id = id,author = session["username"]).first()
        article.title=newtitle
        article.content=newcontent
        db.session.commit()
        flash("Makaleniz başarıyla güncellendi...","success")
        return redirect(url_for("dashboard"))
#makale arama
@app.route("/search",methods=["GET","POST"])
def search():
    if request.method=="POST":
        keyword=request.form.get("keyword")
        tag = "%{}%".format(keyword)
        result = BlogArticles.query.filter(BlogArticles.title.like(tag)).all()
        if result == []:
            flash("Aradığınız kelimeye uygun sonuç bulunamadı...","danger")
            return redirect(url_for("articles"))
        else:
            articles=result
            return render_template("articles.html",articles = articles)
    else:
        flash("hatalı giriş","danger")
        return redirect(url_for("index"))
#profil
@app.route("/user/<string:username>",methods=["GET","POST"])
def user(username):
    if "logged_in" in session:
        if username==session["username"]:
            if request.method=="GET":
                articles = BlogArticles.query.filter_by(author = username)
                user = BlogUsers.query.filter_by(username = username).first()           
                return render_template("user.html",user=user,articles=articles)
                        
        else:
            if request.method=="GET":
                articles = BlogArticles.query.filter_by(author = username)
                user = BlogUsers.query.filter_by(username = username).first() 
                print(user) 
                if user != None:
                    return render_template("profile.html",articles=articles,user=user)
                else:
                    flash("böyle bir kullanıcı bulunmamakta","danger")
                    return redirect(url_for("index"))    
    else:
        if request.method=="GET":
            articles = BlogArticles.query.filter_by(author = username)
            user = BlogUsers.query.filter_by(username = username).first()
            print(user)
            if user != None:
                return render_template("profile.html",articles=articles,user=user)
            else:
                flash("böyle bir kullanıcı bulunmamakta","danger")
                return redirect(url_for("index"))   
@app.route("/user/edit/<string:username>",methods=["GET","POST"])
@login_required
def edituser(username):
    if request.method=="GET":
        user = BlogUsers.query.filter_by(username = session["username"]).first()
        print(user)
        if user != None:
            form=RegisterForm()
            form.username.data=user.username
            form.name.data=user.name
            form.job.data=user.job
            form.location.data=user.location
            form.email.data=user.email
            a=(user.date.replace("-",""))
            s=datetime.datetime.strptime(a, r"%Y%m%d")
            form.date.data=s
            return render_template("edit.html",form=form)
        else:
            flash("bu işlem için izniniz bulunmamaktadır","danger")
            return redirect(url_for("index"))
       
    else:
        form=RegisterForm(request.form)
        newname=form.name.data
        newusername=form.username.data
        newlocation=form.location.data
        newjob=form.job.data
        newdate=form.date.data
        newemail=form.email.data
        deneme=BlogUsers.query.filter_by(username = newusername).first()
        print(deneme)
        if deneme == None:
            user = BlogUsers.query.filter_by(username = session["username"]).first()
            user.name=newname
            user.username=newusername
            user.job=newjob
            user.location=newlocation
            user.email=newemail
            user.date=newdate
            db.session.commit()
            session["username"]=newusername
            flash("Makaleniz başarıyla güncellendi...","success")
            return redirect(url_for("index"))
        else:
            flash("bu kullanıcı adı kullanılmış","danger")
            return redirect(url_for("index"))

YUKLEME_KLASORU = 'static/img'
UZANTILAR = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = YUKLEME_KLASORU
app.secret_key = "Flask_Dosya_Yukleme_Ornegi"
def uzanti_kontrol(dosyaadi):
   return '.' in dosyaadi and \
   dosyaadi.rsplit('.', 1)[1].lower() in UZANTILAR

# Form ile dosya yükleme işlemi
@app.route('/dosyayukle', methods=['POST'])
@login_required
def dosyayukle():


   if request.method == 'POST':

        # formdan dosya gelip gelmediğini kontrol edelim
      if 'dosya' not in request.files:
         flash('Dosya seçilmedi')
         return redirect('dosyayukleme')         

        # kullanıcı dosya seçmemiş ve tarayıcı boş isim göndermiş mi
      dosya = request.files['dosya']                    
      if dosya.filename == '':
         flash('Dosya seçilmedi')
         return redirect('dosyayukleme')

        # gelen dosyayı güvenlik önlemlerinden geçir
      if dosya and uzanti_kontrol(dosya.filename):
         dosyaadi = secure_filename(dosya.filename)
         dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], dosyaadi))
         #return redirect(url_for('dosyayukleme',dosya=dosyaadi))
         update = BlogUsers.query.filter_by(username= session["username"]).first()
         
         if user != []:
            
            update.img = dosyaadi
            db.session.commit()
            
            username=session["username"]
            updateimg = BlogComment.query.filter_by(username= session["username"])
            for i in updateimg:
                i.img=dosyaadi
                db.session.commit()
            
            flash("profil fotoğrafınız başarıyla güncellendi...","success")
            return redirect('user/' + username)
         updateimg = BlogComment.query.filter_by(username= session["username"])
         print(updateimg)
         if updateimg != []:
             updateimg.img = dosyaadi
             db.session.commit()
      else:
         flash('İzin verilmeyen dosya uzantısı')
         return redirect('dosyayukleme')

  
# Form ile dosya yükleme sayfası
@app.route('/dosyayukleme')
@login_required
def dosyayukleme():
   return render_template("dosyayukleme.html")




if __name__=="__main__":
    db.create_all()
    app.run(debug=True)

