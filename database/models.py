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
            for message in conversation.messages:
                msgsClone.append({"_id": str(message._id), "createdAt": message.createdAt, "text": message.text, "user": {
                    "_id": message.user.userId, "name": message.user.name, "avatar": message.user.avatar}})
            msgsClone.reverse()
            userConversations.append(
                {"userOne": conversation.userOne, "userTwo": conversation.userTwo, "conversationId": conversation.conversationId, "messages": msgsClone
                 })
        return userConversations

# class Sender(db.EmbeddedDocument):
#     _id = db.StringField(required=True)
#     name = db.StringField(required=True)
#     avatar = db.StringField(required=True)


class Message(db.EmbeddedDocument):
    _id = db.UUIDField(required=True, binary=False,
                       default=lambda: uuid.uuid4())
    createdAt = db.StringField(required=True, default=datetime.now().ctime())
    text = db.StringField(required=True)
    user = db.ReferenceField(User)
    image = db.StringField()
    video = db.StringField()


class Conversation(db.Document):
    userOne = db.ReferenceField(User)
    userTwo = db.ReferenceField(User)
    conversationId = db.StringField(unique=True)
    createdAt = db.DateTimeField()
    updatedAt = db.DateTimeField(default=datetime.now().ctime(), required=True)
    messages = db.ListField(db.EmbeddedDocumentField(Message))

    def getMessages(self):
        preparedMessages = []
        for message in self.messages:
            preparedMessages.append({"_id": str(message._id), "createdAt": message.createdAt, "text": message.text, "user": {
                "_id": message.user.userId, "name": message.user.name, "avatar": message.user.avatar}})
        # test = preparedMessages
        # print("\n\n\ntest before ", test,
        #       "\n\n\ntest after rev ", test.reverse(), "\n\n\n")
        preparedMessages.reverse()
        return preparedMessages

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
