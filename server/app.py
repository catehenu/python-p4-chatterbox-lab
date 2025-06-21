from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# GET /messages: returns all messages, ordered by created_at in ascending order
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([message.to_dict() for message in messages])

# POST /messages: creates a new message with the body and username, and returns the created message as JSON
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()  # Get the JSON data from the request
    body = data.get('body')
    username = data.get('username')

    if not body or not username:
        return jsonify({"error": "Missing 'body' or 'username'"}), 400

    message = Message(body=body, username=username)  # Create a new Message object
    db.session.add(message)  # Add it to the session
    db.session.commit()  # Commit the transaction to the database

    return jsonify(message.to_dict()), 201  # Return the new message as JSON

# PATCH /messages/<int:id>: updates a message's body and returns the updated message as JSON
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)

    if not message:
        return jsonify({"error": "Message not found"}), 404

    data = request.get_json()
    body = data.get('body')

    if not body:
        return jsonify({"error": "Missing 'body'"}), 400

    message.body = body  # Update the message body
    message.updated_at = datetime.utcnow()  # Update the updated_at timestamp
    db.session.commit()  # Commit the changes

    return jsonify(message.to_dict())

# DELETE /messages/<int:id>: deletes the message by its ID
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)

    if not message:
        return jsonify({"error": "Message not found"}), 404

    db.session.delete(message)  # Delete the message from the session
    db.session.commit()  # Commit the deletion to the database

    return '', 204  # Return a 204 No Content status

if __name__ == '__main__':
    app.run(port=5555)