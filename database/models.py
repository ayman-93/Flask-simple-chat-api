from .db import db
from datetime import datetime
# from bson.objectid import ObjectId
import uuid

from utilis.GetConversationId import GetConversationId


class User(db.EmbeddedDocument):
    id = db.StringField(required=True)
    name = db.StringField(required=True)
    avatar = db.StringField(required=True)


class Sender(db.EmbeddedDocument):
    _id = db.StringField(required=True)
    name = db.StringField(required=True)
    avatar = db.StringField(required=True)


class Message(db.EmbeddedDocument):
    _id = db.UUIDField(required=True, binary=False,
                       default=lambda: uuid.uuid4())
    createdAt = db.StringField(required=True, default=datetime.now().ctime())
    text = db.StringField(required=True)
    user = db.EmbeddedDocumentField(Sender)
    image = db.StringField()
    video = db.StringField()


class Conversation(db.Document):
    userOne = db.EmbeddedDocumentField(User)
    userTwo = db.EmbeddedDocumentField(User)
    conversationId = db.StringField(unique=True)
    createdAt = db.DateTimeField()
    updatedAt = db.DateTimeField(default=datetime.now().ctime(), required=True)
    messages = db.ListField(db.EmbeddedDocumentField(Message))

    def save(self, *args, **kwargs):
        print("inside save in models")
        if not self.createdAt:
            self.createdAt = datetime.now().ctime()

        self.updatedAt = datetime.now().ctime()

        if not self.messages:
            self.messages = [Message(createdAt=str(datetime.now().ctime()), text="First Message Initial Message Sender Bot who open the conversation " + self.userOne['name'], user=Sender(
                _id="0", name="Bot", avatar="https://image.freepik.com/free-vector/gamer-mascot-geek-boy-esports-logo-avatar-with-headphones-glasses-cartoon-character_8169-228.jpg"))]
            print("assign message")

        if not self.conversationId:
            print("assing conversationId")
            # to make the smaller number always first.
            self.conversationId = GetConversationId(
                self.userOne['id'], self.userTwo['id'])
            print("assing conversationId end")

        return super(Conversation, self).save(*args, **kwargs)
