def GetConversationId(userOne, userTwo):
    one = userOne if userOne < userTwo else userTwo
    two = userOne if userOne > userTwo else userTwo
    # newConversationId = str(one) + str(two)
    return (str(one) + str(two))
