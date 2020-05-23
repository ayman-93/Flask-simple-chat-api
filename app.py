from database.models import Conversation, Message, User
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
    userConversations = User.objects(
        userId=userId).first().getUserConversation()
    # conversation = Conversation.objects.filter(
    #     Q(userOne__id=userId) | Q(userTwo__id=userId)).to_json()
    # test = json.loads(userConversations)
    print("\n\nconversation", userConversations, "\n\n\n")
    # return "test"
    return Response(json.dumps(userConversations), mimetype="application/json", status=200)

# update user
@app.route("/userUpdateInfo", methods=['POST'])
def edit_conversiton():
    # get user data from the body as json.
    userData = request.json
    userId = userData['id']
    userName = userData['name']
    userAvatar = userData['avatar']

    try:
        User.objects(userId=userId).update(name=userName, avatar=userAvatar)
        return {"success": True, "msg": "User Updated.."}

    except Exception as e:
        return {"success": False, "msg": "Something Wron.."}
        print("update user info something wrong, ", e)


# Socket Events
# 1: built in event on conncet lisen for users connection
@socketio.on('connect')
def handleConnect():
    print("connected", request.sid)


@socketio.on('startConversation')
def handlStartConversation(data):

    try:
        USER_ONE = User(userId=data['userOne']['id'], name=data['userOne']
                        ['name'], avatar=data['userOne']['avatar']).save()
    except (NotUniqueError, DuplicateKeyError):
        # print("user one exist in db")
        USER_ONE = User.objects.get(userId=data['userOne']['id'])
    try:
        USER_TWO = User(userId=data['userTwo']['id'], name=data['userTwo']
                        ['name'], avatar=data['userTwo']['avatar']).save()
    except (NotUniqueError, DuplicateKeyError):
        # print("user two exist in db")
        USER_TWO = User.objects.get(userId=data['userTwo']['id'])

        # try to create new conversation.
    try:
        # create the conversation.
        conversation = Conversation(userOne=USER_ONE, userTwo=USER_TWO)
        conversation.save()

        # add conversation reference to userOne
        USER_ONE.addConversation(conversation.pk)
        # add conversation reference to userTwo
        USER_TWO.addConversation(conversation.pk)

        # convert the conversation to Python Dictionary.
        conversation = json.loads(conversation.to_json())

        # join conversation
        join_room(str(conversation['conversationId']))
        print('join new conversationId ', str(conversation['conversationId']))
        # send the conversationId and the messages array
        emit("conversationOpen", {"conversationId": conversation['conversationId'], "messages": conversation['messages']},
             room=conversation['conversationId'])

    # if the conversation already exist.
    except (NotUniqueError, DuplicateKeyError):
        # get the old conversationId
        oldConversationId = GetConversationId(
            data['userOne']['id'], data['userTwo']['id'])

        # print("they are already In Conversation " + oldConversationId)
        # join the old conversation
        join_room(oldConversationId)

        print("join oldConversationId ", oldConversationId)

        # getMessages will return the messages with user(sender) details _id, name and avatart.
        messages = Conversation.objects(
            conversationId=oldConversationId).first().getMessages()

        # convert the old conversation to Python Dictionary.
        conversation = json.loads(Conversation.objects.get(
            conversationId=oldConversationId).to_json())
        conversation['messages'].reverse()
        # send the conversationId and the old messages array
        emit("conversationOpen", {"conversationId": conversation['conversationId'], "messages": messages},
             room=oldConversationId)

    except Exception as e:
        print("Something want wrong: ", e)


@socketio.on('message')
def handleMessage(data):
    # data: contain {  message: { _id: uuid4, text: "", user: {_id: "", name: "", avatar: ""}, createdAt: "" }, conversationId: "1", receiverId: "" }
    # convert the data to python Dictionary
    data = json.loads(data)
    # print("data['receiverId'] ", data['receiverId'])
    # send the new message to conversation
    print("message ", data['message'],
          " conversationId ", data['conversationId'])
    emit("message", data['message'], room=data['conversationId'])

    # set the sender
    # try to get user from db.
    try:
        sender = User.objects.get(userId=data['message']['user']['_id'])
        print("User in message from db", json.loads(sender.to_json()))
    # if user does not exist.
    except User.DoesNotExist:
        sender = User(userId=data['message']['user']['_id'], name=data['message']
                      ['user']['name'], avatar=data['message']['user']['avatar']).save()
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
