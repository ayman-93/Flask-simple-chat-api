import config
from server.sendNotification import sendNotification


class sendChatMessage(object):
    def send(self, conversion_id, sender_id, sender_name, receiver_id, receiver_name, message):
        try:
            
            n = sendNotification()
            # send notification
            n.send('individual', receiver_id, sender_name, message, '=')
            
            conn = config.mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('add_Notification', [sender_name, sender_name, message, message, '8', 2, receiver_id, sender_id])
            data = cursor.fetchall()
            conn.commit()
            
            return data

        except Exception as e:
            return e