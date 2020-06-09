import json
from collections import Iterable
from bson import ObjectId
from datetime import datetime
from flask_mongoengine.wtf.fields import unicode


class MongoengineEncoder(json.JSONEncoder):
    """
    The default JSON encoder that ships with Mongoengine (the to_json method
    exposed on Document instances) makes some odd choices. Datetime objects 
    are nested on a $date property, ObjectIds are nested on an $oid property, 
    etc. It makes for a confusing interface when you're serializing obejcts for, 
    say, a JavaScript application. 

    This borrows heavily from an abandoned Flask extension called Flask-Views
    https://github.com/brocaar/flask-views/blob/master/flask_views/db/mongoengine/json.py
    """

    def default(self, obj):
        if isinstance(obj, Iterable):
            out = {}
            for key in obj:
                out[key] = getattr(obj, key)
            return out

        if isinstance(obj, ObjectId):
            return unicode(obj)

        if isinstance(obj, datetime):
            return str(obj)

        return json.JSONEncoder.default(self, obj)
