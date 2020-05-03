from database.models import Conversation, Message, User
from database.db import initialize_db
from bson import json_util
from flask_socketio import SocketIO, send, emit, join_room, rooms, leave_room
from flask import Flask, render_template, request, Response, jsonify
import json
from datetime import datetime

from utilis.GetConversationId import GetConversationId
from utilis.JSONEncoder import MongoengineEncoder
from mongoengine.document import NotUniqueError
from pymongo.errors import DuplicateKeyError
from mongoengine.queryset.visitor import Q
# import eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

app.config["MONGODB_HOST"] = "mongodb+srv://ayman:753258@aymancluster-ddsk0.mongodb.net/orag?retryWrites=true&w=majority"
initialize_db(app)
# for socketio
# eventlet.monkey_patch()


@app.route('/')
def index():
    return "api is working.."

# Get All Conversations
# @app.route('/conversations')
# def get_conversation():
#     conversation = Conversation.objects().to_json()
#     return Response(conversation, mimetype="application/json", status=200)

# Get user Conversations By userId.
@app.route('/user/<userId>/conversations')
def get_conversationById(userId):
    print(userId)
    conversation = Conversation.objects.filter(
        Q(userOne=userId) | Q(userTwo=userId)).to_json()
    return Response(conversation, mimetype="application/json", status=200)

# Add New Conversation.
# @app.route('/conversations', methods=['POST'])
# def add_conversation():
#     body = request.get_json()
#     conversation = Conversation(**body).save()
#     id = conversation.id
#     return {'id': str(id)}, 200

# # Update Converateion By Id.
# @app.route('/conversations/<id>', methods=['PUT'])
# def update_conversation(id):
#     body = request.get_json()
#     Conversation.objects.get(id=id).update(**body)
#     return 'Converateion {""} updated', 200

# # Delete Conversation By Id.
# @app.route('/conversations/<id>', methods=['DELETE'])
# def delete_conversation(id):
#     Conversation.objects.get(id=id).delete()
#     return '', 200

# Socket Events
# 1: built in event on conncet lisen for users connection
@socketio.on('connect')
def handleConnect():
    print("connected", request.sid)


@socketio.on('startConversation')
def handlStartConversation(data):
    try:
        _userOne = User(userId=str(data['userOne']['userId']), userName=data['userOne']
                        ['userName'], avatar=data['userOne']['avatar'])
        _userTwo = User(userId=str(data['userTwo']['userId']), userName=data['userTwo']
                        ['userName'], avatar=data['userTwo']['avatar'])
        conversation = Conversation(
            userOne=_userOne, userTwo=_userTwo).save()
        print("new conversationId:: " + str(conversation.conversationId))
        join_room(str(conversation.conversationId))
        emit("conversationOpen", {"conversationId": conversation.conversationId, "messages": [{"msg": "This is the bgining of the conversation", "time": datetime.now().ctime()}]},
             room=conversation.conversationId)

    except (NotUniqueError, DuplicateKeyError):
        oldConversationId = GetConversationId(
            str(data['userOne']['userId']), str(data['userOne']['userId']))
        print("they are already In Conversation " + oldConversationId)
        join_room(oldConversationId)
        print("user ", data['userOne']['userName'],
              " joind room", oldConversationId)

        conversation = json.loads(Conversation(
            conversationId=oldConversationId).to_json())
        # for con in conversation:
        # test = MongoengineEncoder(conversation)
        # print("con", test)
        print("Conversations " + str(conversation))

        emit("conversationOpen", {"conversationId": conversation['conversationId'], "messages": conversation['messages']},
             room=oldConversationId)
    except Exception as e:
        print("Something want wrong: ", e)
        # print("request.sid " + request.sid)
        # emit('alreadyInConversation',
        #      "Already In Conversation " + conversationId, room=conversationId)

    # I make this condiatian
    # userOne = data['userId'] if data['userId'] < data['receiverId'] else data['receiverId']
    # userTwo = data['userId'] if data['userId'] > data['receiverId'] else data['receiverId']
    # conversationId = str(userOne) + str(userTwo)

    # conversation = Conversation(**body).save()
    # id = conversation.id
    # join_room(conversationId)
    # # send the conversationId back to the user who s
    # emit("conversationId", data=conversationId, room=data['userId'])
    # print("conversationId ", conversationId)
    # _conversations = Conversation.objects(conversationId=conversationId)
    # if(not _conversations):
    #     Conversation(userOne=userOne, userTwo=userTwo,).save()
    # for u in _conversations:
    #     print("result:: ", u.id, u.userOne, u.userTwo, str(u.startDate))
    # print("op ", str(ob))
    # print("_conversation: ", json_util.dumps(_conversation))
    # emit("test", json_util.dumps(_conversation))
    # sender = data['userId'] if
    # newConversation = {
    #     "userOne": data['userId'],
    #     "userTwo": "2",
    #     "startDate": "2020-04-24",
    #     "lastUdate": "2020-04-24",
    #     "messages": [{ "msg": "hi..", "time": "2020-04-24" }]
    # }
    # Conversation(data.get_json()).save()


@socketio.on('message')
def handleMessage(data):
    data = json.loads(data)
    emit("message", data['message'], room=data['conversationId'])
    conversation = Conversation.objects(
        conversationId=str(data['conversationId']))
    print("conversation in handleMessage ", conversation)
    # conversation.messages.append(Message(
    #     _id=data['message']['_id'], time=data['message']['time'], msg=data['message']['msg']))
    # conversation.save()
    print("new message to conversationId", str(data['conversationId']))


@socketio.on('leaveConversation')
def leaveConversation(conversationId):
    print("user leave conversation ", conversationId)
    leave_room(conversationId)


@socketio.on('disconnect')
def handleConnect():
    # leave_room()
    print("user disconnect")


if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True)
    socketio.run(app, host='0.0.0.0', debug=True)
