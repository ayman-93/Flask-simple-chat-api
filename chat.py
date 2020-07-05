from database.models import Conversation, Message, User
from database.db import initialize_db
from flask_socketio import SocketIO, emit, join_room, rooms, leave_room
from flask import Flask, request, Response
import json

from utilis.GetConversationId import GetConversationId
from mongoengine.document import NotUniqueError
from pymongo.errors import DuplicateKeyError
from mongoengine.queryset.visitor import Q


app = Flask(__name__)
# app.config['SECRET_KEY'] = 'mysecret'

socketio = SocketIO(app, cors_allowed_origins="*",
                    async_mode='eventlet')  # ,manage_session=False)

app.config["MONGODB_HOST"] = "mongodb+srv://ayman:753258@aymancluster-ddsk0.mongodb.net/orag2?retryWrites=true&w=majority"
initialize_db(app)


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
    user = User.objects(
        userId=userId).first()
    print("\n\n\nuserConversations ", user)
    if user is None:
        return Response(json.dumps({"msg": "no user found.."}))
    userConversations = user.getUserConversation()
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
        emit("conversationOpen", {"conversationId": conversation['conversationId'], "messages": conversation['messages'], "unreadMesaages": 0},
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
        emit("conversationOpen", {"conversationId": conversation['conversationId'], "messages": messages['messages'], "unreadMesaages": messages['unreadMesaages']},
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
        print("\n\n\nsender: ", sender, "\nchat.py L:156")

    # get the conversation
    conversation = Conversation.objects.get(
        conversationId=str(data['conversationId']))

    # set the new message
    newMessage = Message(
        messageId=data['message']['_id'], createdAt=str(data['message']['createdAt']), text=data['message']['text'], user=sender, conversationRef=conversation)
    print("\n\n\nnewMessage: ", newMessage.to_json(), "\nchat.py L:160")

    print("\n\n\nnewMessage: ", newMessage, "\nchat.py L:162")

    # save the chages on the database
    newMessage.save()
    # add the new message to messages in the conversation
    conversation.addMessag(newMessage.pk)
    # set readStatus
    # conversation.updateReadStatus(userId=sender.userId)

    conversation.save()
    print("new message to conversationId ", str(data['conversationId']))


@socketio.on("updateReadStatus")
def updateReadStatus(data):
    conversationId = data['conversationId']
    userId = data['id']
    print("\n\n\nmessage in updateReadStatus \nF:chat,L:180\n\n ")
    # Conversation(conversationId=conversationId).updateReadStatus()

    conversation = Conversation.objects.get(
        conversationId=str(data['conversationId']))
    conversation.updateReadStatus(userId=userId)
    conversation.save()
    # conversation = Conversation.objects(
    #     conversationId=str(conversationId)).update_one(set__messages__readStatus=True)


@socketio.on('leaveConversation')
def leaveConversation(conversationId):
    print("user leave conversation ", conversationId)
    leave_room(conversationId)


@socketio.on('disconnect')
def handleConnect():
    # leave_room()
    print("user disconnect")


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
