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

db = SQLAlchemy(app)

cache = {}

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
    request_data = request.get_json()
    unique_id, payload = str(request_data["uniqueId"]).upper(), request_data["payLoad"]    
    value = IBoard.query.filter(IBoard.id == unique_id).first()
    db.engine.execute(
        "delete from i_board where created_at < now() - interval '1 days'")
    if value:
        if value.text == payload:
            return "NO Update", 200
        value.text = str(payload)
        value.created_at = func.now()
        db.session.flush()
        db.session.commit()
        return "OK", 202
    db.session.add(IBoard(unique_id, payload, func.now()))
    db.session.commit()
    return "OK", 201


@app.route("/api/iBoardGet", methods=['POST'])
def DEBoardGet():
    request_data = request.get_json()
    unique_id = str(request_data["uniqueId"]).upper()
    value = IBoard.query.filter(IBoard.id == unique_id).first()

    if value:
        return value.text, 201
    return "", 204


@app.route("/api", methods=['GET'])
def healthCheck():
    return jsonify({"message": "Server is up and running"}), 200    


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
