import numpy as np
import pickle
from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


model = pickle.load(open('heart_disease_model.pkl','rb'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def init(self, username, password):
        self.username = username
        self.password = password


def predict(values,dic):
    values = np.asarray(values)
    return model.predict(values.reshape(1, -1))[0]

#url
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        u = request.form['username']
        p = request.form['password']
        data = User.query.filter_by(username=u, password=p).first()
        if data is not None:
            session['logged_in'] = True
            return redirect(url_for('main'))
        return render_template('login.html', message="Incorrect Details")



@app.route('/main')
def main():
    return render_template("index.html")

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            password=request.form['password']
            cpassword=request.form['cpassword']
            if password==cpassword:
                db.session.add(User(username=request.form['username'], password=request.form['password']))
                db.session.commit()
                return redirect(url_for('login'))
            
            else:
                return redirect(url_for('register'))

            
            
        except:
            return render_template('register.html', message="User Already Exists")
    else:
        return render_template('register.html')
    
@app.route("/predict",methods= ['POST', 'GET'])
def predictPage():
    try:
        if request.method == 'POST':
            to_predict_dict = request.form.to_dict()
            to_predict_list = list(map(float, list(to_predict_dict.values())))
            pred = predict(to_predict_list, to_predict_dict)
    except:
        message = "Please enter valid Data"
        return render_template("index.html", message = message)

    return render_template('predict.html', pred = pred)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))

@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html")





    


if __name__ == '__main__':
    app.secret_key = "ThisIsNotASecret:p"
    with app.app_context():
        db.create_all()
        app.run(debug=True)