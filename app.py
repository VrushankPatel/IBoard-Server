from flask import Flask, send_file, request, Response, jsonify, make_response
from flask_cors import CORS
import json
from sqlalchemy import update
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

CORS(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})

db = SQLAlchemy(app)


class IBoard(db.Model):
    id = db.Column('board_id', db.String(100), primary_key=True)
    text = db.Column(db.String(4294000000))

    def __init__(self, id, text):
        self.id = id
        self.text = text


@app.route("/api/iBoardInsertPayLoad", methods=['POST'])
def DEBoardInsertPayLoad():
    requestData = request.get_json()
    uniqueId = requestData["uniqueId"]
    payLoad = requestData["payLoad"]
    value = IBoard.query.filter(IBoard.id == str(
        uniqueId)).first()
    if value:
        value.text = str(payLoad)
        db.session.flush()
        db.session.commit()
        return "OK", 202
    db.session.add(IBoard(uniqueId, payLoad))
    db.session.commit()
    return "OK", 201


@app.route("/api/iBoardGet", methods=['POST'])
def DEBoardGet():
    requestData = request.get_json()
    uniqueId = requestData["uniqueId"]
    value = IBoard.query.filter(IBoard.id == str(
        uniqueId)).first()
    if value:
        return value.text, 201
    return "", 204


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
