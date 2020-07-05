from .db import db
from datetime import datetime
from bson.objectid import ObjectId
import uuid
import json

from utilis.GetConversationId import GetConversationId


class User(db.Document):
    # _id = db.ObjectIdField(default=ObjectId,
    #                        unique=True, primary_key=True)
    userId = db.StringField(unique=True, required=True)
    name = db.StringField(required=True)
    avatar = db.StringField(required=True)
    conversations = db.ListField(db.ReferenceField('Conversation'))

    def addConversation(self, conversationId):
        self.conversations.append(ObjectId(conversationId))
        self.save()

    def getUserConversation(self):
        userConversations = []
        for conversation in self.conversations:
            # remove unnecessary fields: _id and conversations from users
            userOne = json.loads(conversation.userOne.to_json())
            userTwo = json.loads(conversation.userTwo.to_json())
            # conversation.pop('messages', None)
            userOne.pop('_id', None)
            userOne.pop('conversations', None)
            userTwo.pop('_id', None)
            userTwo.pop('conversations', None)
            conversation.userOne = userOne
            conversation.userTwo = userTwo
            updatedAt = conversation.updatedAt.__str__()
            # print("conversation.messages::",
            #       conversation['messages'][0].to_json())

            # conversation.pop("messages")
            # msgsClone = []
            # # retrive the messages from the Conversation doc by referance instaded of the referance id.
            # for message in conversation.messages:
            #     # print("message::::::::::before ", message)
            #     msgsClone.append(json.loads(message.to_json()))
            # print("message:::::::::: ", message)

            # print("conversation.messages", msgsClone)
            # print("\n\n\nconversation.messages",
            #       str(json.loads(conversation.messages)), "\n\n\n")
            msgsClone = []
            unreadMesaages = 0
            for message in conversation.messages:
                # print('\n\n\nmessage.user.userId in User getusermessage:',
                #       message.user.userId)
                if(self.userId != message.user.userId):
                    unreadMesaages += message.readStatus
                msgsClone.append({"_id": str(message.messageId), "createdAt": message.createdAt, "text": message.text, "user": {
                    "_id": message.user.userId, "name": message.user.name, "avatar": message.user.avatar}, "readStatus": message.readStatus})
            msgsClone.reverse()
            userConversations.append(
                {"userOne": conversation.userOne, "userTwo": conversation.userTwo, "conversationId": conversation.conversationId,
                 "messages": msgsClone, "unreadMesaages": unreadMesaages, "updatedAt": updatedAt
                 })
        return userConversations

# class Sender(db.EmbeddedDocument):
#     _id = db.StringField(required=True)
#     name = db.StringField(required=True)
#     avatar = db.StringField(required=True)


class Message(db.Document):
    # id = db.ObjectIdField(default=ObjectId,
    #                       unique=True, primary_key=True)
    messageId = db.UUIDField(required=True, binary=False,
                             default=lambda: uuid.uuid4())
    conversationRef = db.ReferenceField('Conversation')
    createdAt = db.StringField(required=True, default=datetime.now().ctime())
    text = db.StringField(required=True)
    user = db.ReferenceField(User)
    image = db.StringField()
    video = db.StringField()
    readStatus = db.BooleanField(default=True)


class Conversation(db.Document):
    userOne = db.ReferenceField(User)
    userTwo = db.ReferenceField(User)
    conversationId = db.StringField(unique=True)
    createdAt = db.DateTimeField()
    updatedAt = db.DateTimeField(default=datetime.now().ctime(), required=True)
    messages = db.ListField(db.ReferenceField(Message))
    # readStatus = db.BooleanField(default=False)

    # def updateReadStatus(self, userId):
    #     lastMessage = json.loads(self.messages[-1].to_json())
    #     lastSenderPk = lastMessage['user']['$oid']
    #     lastSender = json.loads(User.objects(pk=lastSenderPk).to_json())
    #     lastSenderId = lastSender[0]['userId']
    #     print("\n\nlast sender id ",  lastSenderId)
    #     print("\n\nstr(userId) ",  str(userId))
    #     if(str(userId) == str(lastSenderId)):
    #         self.readStatus = False if(self.readStatus == True) else True
    #         # self.update_one(set__messages__readStatus=True)
    #         # self.objects(
    #         #     upsert=True, set__messages__readStatus=True)
    #         self.save()

    def getMessages(self):
        preparedMessages = []
        unreadMesaages = 0
        for message in self.messages:
            # print("\n\n\nGetmessages ", message)
            unreadMesaages += message.readStatus
            preparedMessages.append({"_id": str(message.messageId), "createdAt": message.createdAt, "text": message.text, "user": {
                "_id": message.user.userId, "name": message.user.name, "avatar": message.user.avatar}})
        # test = preparedMessages
        # print("\n\n\ntest before ", test,
        #       "\n\n\ntest after rev ", test.reverse(), "\n\n\n")
        preparedMessages.reverse()
        return {"messages": preparedMessages, "unreadMesaages": unreadMesaages}

    def addMessag(self, messagePk):
        self.messages.append(messagePk)

    def updateReadStatus(self, userId):
        # print("\n\n userId: ", userId)
        for message in self.messages:
            # print("\n\n\nmessage.user.userId: ", message.user.userId)
            if(message.user.userId != userId and message.readStatus):
                Message.objects(pk=message.id).update_one(
                    set__readStatus=False)
                # message.readStatus = True
        self.save()
        # Conversation.objects(
        #     conversationId=str(conversationId)).update_one(set__messages__readStatus=True)

    def save(self, *args, **kwargs):

        if not self.createdAt:
            self.createdAt = datetime.now().ctime()

        self.updatedAt = datetime.now().ctime()

        # if not self.messages:
        #     USER = User(
        #         id="0", name="Bot", avatar="https://image.freepik.com/free-vector/gamer-mascot-geek-boy-esports-logo-avatar-with-headphones-glasses-cartoon-character_8169-228.jpg").save()
        #     self.messages = [Message(createdAt=str(datetime.now().ctime(
        #     )), text="First Message Initial Message Sender Bot who open the conversation " + self.userOne['name'], user=USER)]
        #     print("assign message")

        if not self.conversationId:
            # to make the smaller number always first.
            self.conversationId = GetConversationId(
                self.userOne['userId'], self.userTwo['userId'])

        return super(Conversation, self).save(*args, **kwargs)
