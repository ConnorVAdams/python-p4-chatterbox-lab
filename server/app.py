from flask import Flask, request, make_response, jsonify, abort
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

from sqlalchemy.exc import IntegrityError
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1> INDEX </h1>'

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        msgs = [msg.to_dict() for msg in Message.query.all()]
        return msgs, 200
    else:
        try:
            data = request.get_json()
            msg = Message(**data)
            db.session.add(msg)
            db.session.commit()
            return msg.to_dict(), 201
        except IntegrityError as e:
            db.session.rollback()
            return {"error": str(e)}, 400
        except AttributeError as e:
            db.session.rollback()
            return {"error": str(e)}, 400

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()

    if request.method == 'PATCH':
        data = request.get_json()
        for attr in data:
            setattr(message, attr, data[attr])
            
        db.session.add(message)
        db.session.commit()

        return make_response(message.to_dict(),200 )

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()

        return make_response( {'deleted': True} , 200)


if __name__ == '__main__':
    app.run(port=5555)
