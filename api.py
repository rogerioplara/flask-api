from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

# Modelo de User
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"User(username = {self.name}, email = {self.email})"

# Argumentos para validação de username e email
user_args = reqparse.RequestParser()
user_args.add_argument('username', type=str, required=True, help="Username cannot be blank")
user_args.add_argument('email', type=str, required=True, help="Email cannot be blank")

# Definições de serialização para User
userFields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
}

# Endpoint de consulta 
class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all()
        return users

    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(username=args["username"], email=args["email"])
        db.session.add(user)
        db.session.commit()
        
        users = UserModel.query.all()
        
        return users, 201

class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        
        if not user:
            abort(404, "User not found")
        
        return user
    
    @marshal_with(userFields)
    def patch(self, id):
        args = user_args.parse_args()
        # recebe o json
        user = UserModel.query.filter_by(id=id).first()
        
        if not user:
            abort(404, "User not found")

        # update do user
        user.username = args["username"]
        user.email = args["email"]
        db.session.commit()
        
        return user
    
    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        
        if not user:
            abort(404, "User not found")

        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users

api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>') # passando parâmetro de url

# Rota
@app.route('/')
def home():
    return '<h1>Flask REST API</h1>'

if __name__ == '__main__':
    app.run(debug=True)