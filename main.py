from flask import Flask, render_template, request, redirect, url_for
import requests
import smtplib
from secret import EMAIL, PASSWORDS, SECRET_KEY
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL

from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
import os

# where is project directory?
basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap(app)
ckeditor = CKEditor(app)

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


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])

    # Notice body's StringField changed to CKEditorField
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    # print(POSTS)
    posts = BlogPost.query.all()
    return render_template("index.html", my_posts=posts)


@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=form.author.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("blog_posts", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


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

@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

if __name__ == "__main__":
    app.run(debug=True)