from database.models import Conversation, Message, User, Sender
from database.db import initialize_db
from flask_socketio import SocketIO, emit, join_room, rooms, leave_room
from flask import Flask, request, Response
import json

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
    # conversation = Conversation.objects.get().filter().to_json()

    conversation = Conversation.objects.filter(
        Q(userOne__id=userId) | Q(userTwo__id=userId)).to_json()
    print("conversation", conversation)
    return Response(conversation, mimetype="application/json", status=200)


# Socket Events
# 1: built in event on conncet lisen for users connection
@socketio.on('connect')
def handleConnect():
    print("connected", request.sid)


@socketio.on('startConversation')
def handlStartConversation(data):
    print("data in startconver ", data)
    try:
        # try to create new conversation.
        conversation = Conversation(
            userOne=User(id=data['userOne']['id'], name=data['userOne']['name'], avatar=data['userOne']['avatar']), userTwo=User(id=data['userTwo']['id'], name=data['userTwo']['name'], avatar=data['userTwo']['avatar'])).save()
        # convert the conversation to Python Dictionary.
        conversation = json.loads(conversation.to_json())

        print("new conversationId:: " + conversation['conversationId'])
        # join conversation
        join_room(str(conversation['conversationId']))
        # send the conversationId and the messages array
        emit("conversationOpen", {"conversationId": conversation['conversationId'], "messages": conversation['messages']},
             room=conversation['conversationId'])
        print("try end")
    # if the conversation already exist.
    except (NotUniqueError, DuplicateKeyError):
        # get the old conversationId
        oldConversationId = GetConversationId(
            data['userOne']['id'], data['userTwo']['id'])

        print("they are already In Conversation " + oldConversationId)
        # join the old conversation
        join_room(oldConversationId)

        print("oldConversationId ", oldConversationId)

        # convert the old conversation to Python Dictionary.
        conversation = json.loads(Conversation.objects.get(
            conversationId=oldConversationId).to_json())

        # send the conversationId and the old messages array
        emit("conversationOpen", {"conversationId": conversation['conversationId'], "messages": conversation['messages']},
             room=oldConversationId)

    except Exception as e:
        print("Something want wrong: ", e)


@socketio.on('message')
def handleMessage(data):
    # data: contain {  message: { _id: uuid4, text: "", user: {_id: "", name: "", avatar: ""}, createdAt: "" }, conversationId: "1", receiverId: "" }
    # convert the data to python Dictionary
    data = json.loads(data)
    print("data['receiverId'] ", data['receiverId'])
    # send the new message to conversation
    emit("message", data['message'], room=data['conversationId'])

    # set the sender
    sender = Sender(_id=data['message']['user']['_id'], name=data['message']
                    ['user']['name'], avatar=data['message']['user']['avatar'])
    # set the new message
    newMessage = Message(
        _id=data['message']['_id'], createdAt=str(data['message']['createdAt']), text=data['message']['text'], user=sender)

    # get the conversation
    conversation = Conversation.objects.get(
        conversationId=str(data['conversationId']))

    # add the new message to messages in the conversation
    conversation.messages.append(newMessage)
    # save the chages on the database
    conversation.save()
    print("new message to conversationId ", str(data['conversationId']))


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
