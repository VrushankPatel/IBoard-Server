from flask import Flask, send_file, request, Response, jsonify, make_response
from flask_cors import CORS
import json
from sqlalchemy import update
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})
cache = {}
db = SQLAlchemy(app)

class IBoard(db.Model):
    id = db.Column('board_id', db.String(100), primary_key=True)
    text = db.Column('board_text', db.String(10485760))
    created_at = db.Column("created_at", db.DateTime(
        timezone=True), default=func.now())

    def __init__(self, id, text, created_at):
        self.id = id
        self.text = text
        self.created_at = created_at


@app.route("/api/iBoardInsertPayLoad", methods=['POST'])
def DEBoardInsertPayLoad():
    requestData = request.get_json()
    uniqueId, payLoad = requestData["uniqueId"], requestData["payLoad"]
    value = IBoard.query.filter(IBoard.id == str(
        uniqueId)).first()
    db.engine.execute(
        "delete from i_board where created_at < now() - interval '1 days'")
    cache[uniqueId] = payLoad
    if value:
        if value.text == payLoad:
            return "NO Update", 200
        value.text = str(payLoad)
        value.created_at = func.now()
        db.session.flush()
        db.session.commit()
        return "OK", 202
    db.session.add(IBoard(uniqueId, payLoad, func.now()))
    db.session.commit()
    return "OK", 201


@app.route("/api/iBoardGet", methods=['POST'])
def DEBoardGet():
    requestData = request.get_json()
    uniqueId = requestData["uniqueId"]
    if cache[uniqueId]:
        return cache[uniqueId], 201
    value = IBoard.query.filter(IBoard.id == str(uniqueId)).first()

    if value:
        cache[uniqueId] = value.text
        return value.text, 201
    return "", 204


@app.route("/api", methods=['GET'])
def healthCheck():
    return "I am alive!", 200


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
