from app.api.v1.resources.resources import *

def created_routes(api):
    api.add_resource(ChatOpenResource, '/chat/open/')
    api.add_resource(ChatMessageCoreResource, '/chat/message/')
