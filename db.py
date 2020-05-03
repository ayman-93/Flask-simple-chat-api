from pymongo import MongoClient, DESCENDING

client = MongoClient(
    "mongodb+srv://ayman:753258@aymancluster-ddsk0.mongodb.net/orga_db?retryWrites=true&w=majority")

orga_db = client.get_database("orga_db")
conversation_collection = orga_db.get_collection("conversation")


def testInsertUser():
    return conversation_collection.insert_one(
        {
            "userOne": "1",
            "userTwo": "2",
            "startDate": "2020-04-24",
            "messages": [{"msg": "hi..", "time": "2020-04-24"}]
        }
    )

# # Get Conversation By Id.
# def get_conversationById(id):
#     conversation = Conversation.objects.get(id=id).to_json()
#     return Response(conversation, mimetype="application/json", status=200)

# # Add New Conversation.
# def add_conversation():
#     body = request.get_json()
#     conversation = Conversation(**body).save()
#     id = conversation.id
#     return {'id': str(id)}, 200

# # Update Converateion By Id.
# def update_conversation(id):
#     body = request.get_json()
#     Conversation.objects.get(id=id).update(**body)
#     return '', 200

# # Delete Conversation By Id.
# def delete_conversation(id):
#     Conversation.objects.get(id=id).delete()
#     return '', 200
