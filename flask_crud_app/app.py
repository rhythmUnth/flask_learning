from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask import request, jsonify
from flask_login import login_user, login_required


app = Flask(__name__)
app.config['SECRET_KEY'] = 'flask--_7og*zirj4fn!wch6ezk*65+=*g+e!w7@9)fy7%+)g4y7g&e4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_crud.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'


@login.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'Please login to access this page'}), 401


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print("Data : ", data)
    user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify({'message': 'User is registered and logged in succefully'})


@app.route('/login', methods=['POST'])
def login_usr():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        login_user(user)
        return jsonify({'message': 'User is logged in successfully'})
    return jsonify({'message': 'invalid username or password'}), 400


@app.route('/template_create', methods=['POST'])
@login_required
def create_template():
    data = request.get_json()
    mail_template = Template(id=data['id'], title=data['title'], body=data['body'], image_url=data['image_url'])
    db.session.add(mail_template)
    db.session.commit()
    return jsonify(mail_template), 200


@app.route('/template/<id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def template(id):
    print(id)
    mail_template = Template.query.get(id)
    if mail_template is None:
        return jsonify({'message': 'No such mail template exist'}), 404
    if request.method == 'GET':
        data = {}
        data["template_id"] = mail_template.id
        data["title"] = mail_template.title
        data["body"] = mail_template.body
        data["image_url"] = mail_template.body
        return jsonify(data)
    elif request.method == 'PUT':
        data = request.get_json()
        mail_template.title = data['title']
        mail_template.body = data['body']
        mail_template.image_url = data['image_url']
        db.session.commit()
        data = {}
        data["template_id"] = mail_template.id
        data["title"] = mail_template.title
        data["body"] = mail_template.body
        data["image_url"] = mail_template.body
        return jsonify(data), 200
    elif request.method == 'DELETE':
        db.session.delete(mail_template)
        db.session.commit()
        return jsonify({'message': 'Mail template deleted'}), 200


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Template(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    image_url = db.Column(db.String(120))


if __name__ == '__main__':
    app.run()

with app.app_context():
    db.create_all()
