from .db import db
from datetime import datetime
from bson.objectid import ObjectId

from utilis.GetConversationId import GetConversationId


class Message(db.EmbeddedDocument):
    _id = db.ObjectIdField(required=True, default=lambda: ObjectId())
    time = db.DateTimeField(required=True)
    msg = db.StringField(required=True)


class User(db.EmbeddedDocument):
    userId = db.StringField(required=True)
    userName = db.StringField(required=True)
    avatar = db.StringField(required=True)


class Conversation(db.Document):
    userOne = db.EmbeddedDocumentField(User)
    userTwo = db.EmbeddedDocumentField(User)
    conversationId = db.StringField(unique=True)
    startDate = db.DateTimeField()
    lastUdate = db.DateTimeField(default=datetime.now().ctime(), required=True)
    messages = db.ListField(db.EmbeddedDocumentField(Message))

    # def __repr__(self):
    #     return {"conversationId": self.conversationId,  "messages": self.messages, "startDate": self.startDate, "lastUdate": self.lastUdate}
    # return '<Conversation %r>' % (self.conversationId)

    def save(self, *args, **kwargs):

        if not self.startDate:
            self.startDate = datetime.now().ctime()

        self.lastUdate = datetime.now().ctime()

        if not self.messages:
            self.messages = [Message(time=datetime.now(
            ), msg="First Message Initial Message Sender " + self.userOne['userName'])]

        if not self.conversationId:
            # to make the smaller number always first.

            self.conversationId = GetConversationId(
                self.userOne['userId'], self.userTwo['userId'])
            print("self.userOne['userId']", self.userOne['userId'],
                  "self.userTwo['userId']", self.userTwo['userId'])

        return super(Conversation, self).save(*args, **kwargs)
