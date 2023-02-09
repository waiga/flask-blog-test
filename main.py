from flask import Flask, render_template, request
import requests
import smtplib
from secret import EMAIL, PASSWORDS, SECRET_KEY
from flask_sqlalchemy import SQLAlchemy
import os

# where is project directory?
basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# my blog posts
# POSTS = requests.get("https://api.npoint.io/d66dc8817de42951992f").json()

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///'+ os.path.join(basedir, 'posts.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

@app.route('/')
def get_all_posts():
    # print(POSTS)
    posts = BlogPost.query.all()
    return render_template("index.html", my_posts=posts)

@app.route('/about')
def about():
    return render_template("about.html")

def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(EMAIL, PASSWORDS)
        connection.sendmail(EMAIL, EMAIL, email_message)

@app.route('/contact', methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        data = request.form
        print(data["name"])
        print(data["email"])
        print(data["phonenumber"])
        print(data["message"])
        send_email(data["name"], data["email"], data["phonenumber"], data["message"])
        return render_template('contact.html', msg_sent=True)
    return render_template("contact.html", msg_sent=False)

@app.route('/post/<int:post_id>')
def blog_posts(post_id):
    # request_blog_post = None
    # for post in POSTS:
    #     if post["id"] == index:
    #         request_blog_post = post
    requested_post = BlogPost.query.get(post_id)
    return render_template('post.html', blog_post=requested_post)



if __name__ == "__main__":
    app.run(debug=True)