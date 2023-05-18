from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    g
)
import boto3
from backend import AWS_Args


class User:
    def __init__(self,  id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


users = []
users.append(User(id=1, username='Ratibah', password='IT485CAPSTONE1!'))
users.append(User(id=2, username='Raphael', password='IT485CAPSTONE4$'))
users.append(User(id=3, username='Frantz', password='IT485CAPSTONE3#'))
users.append(User(id=4, username='Husnain', password='IT485CAPSTONE2@'))

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'


@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user = next((x for x in users if x.username == username), None)
        if user and user.password == password:
            session['user_id'] = user.id
            print('redirecting to index')
            return redirect(url_for('index'))

        return redirect(url_for('login'))

    return render_template('login.html')


@app.route("/index", methods=['GET', 'POST'])
def index():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['Username']
        eventname = request.form['Event']
        start_date = request.form['Start']
        end_date = request.form['End']
        events = AWS_Args(start_date, end_date, username, eventname)
        events.get_events() 
        graph_url = events.plot_data()
        return render_template('result.html', graph_url="data:image/png;base64," + graph_url)

    else:
        return render_template('index.html')


@app.route("/result")
def result():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('result.html')


if __name__ == '__main__':
    app.run(debug=True)
