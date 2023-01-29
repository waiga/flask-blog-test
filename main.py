from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# my blog posts
POSTS = requests.get("https://api.npoint.io/d66dc8817de42951992f").json()

@app.route('/')
def get_all_posts():
    print(POSTS)
    return render_template("index.html", my_posts=POSTS)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact', methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        data = request.form
        print(data["name"])
        print(data["email"])
        print(data["phonenumber"])
        print(data["message"])
        return f'<h1>Successfully sent your message</h1>'
    return render_template("contact.html")

@app.route('/post/<int:index>')
def blog_posts(index):
    request_blog_post = None
    for post in POSTS:
        if post["id"] == index:
            request_blog_post = post
    return render_template('post.html', blog_post=request_blog_post)



if __name__ == "__main__":
    app.run(debug=True)