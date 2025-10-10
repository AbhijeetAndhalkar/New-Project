from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def front_page():
    return render_template('index.html')
#render html for more complex content
#"<p>Hello, World!</p>"

@app.route('/products/')#define the path for the function
def products():
    return "<p>Hello, This is product page!</p>"

@app.route('/about/')
def about():
    return 'Prathamesh gore'

@app.route('/login')
def login():
    return 'login'


if  __name__ == "__main__":
    app.run(debug=True)