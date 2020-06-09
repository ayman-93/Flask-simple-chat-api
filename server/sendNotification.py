# -*- coding: utf-8 -*-
import requests
import json

class sendNotification(object):

    def send(self,a,b,c,d,e):
        # a = type 1= company 2= user
        # b = userid
        # c = tiltle
        # d = message
        # e = relation
        
        try:
            header = {"Content-Type": "application/json; charset=utf-8",
                      "Authorization": "Basic <Yjc0ZTJhZGYtM2YyNi00YjVmLWJiY2QtYTYwNjQ4YmE3ZDRm>"}

            payload = {"app_id": "7299c913-4193-443a-8157-bb86400adfcd",
                        "ios_badgeType": "Increase",
                        "ios_badgeCount": "1",
                        "filters": [
                       		        {"field": "tag", "key": "userId", "relation": e, "value": b}, 
                       	            {"operator": "AND"}, {"field": "tag", "key": "userType", "relation": "=", "value": a}, 
                       	            {"operator": "AND"}, {"field": "tag", "key": "login", "relation": "=", "value": 1}
                       	],
                        "headings": {"en": c},
                        "contents": {"en": d}
                       
                   
                   }
 
            req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
 
            return {'statusCode':req.status_code, 'reason':req.reason}
         
        except Exception as e:
            return str(e)