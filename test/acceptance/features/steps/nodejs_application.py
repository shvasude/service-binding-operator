
class NodeJSApp(object):

    name = ""
    namespace = ""

    def __init__(self, name, namespace):
        self.name = name
        self.namespace = namespace

    def is_running(self):
        return False

    def install(self, name, namespace):
        return False

    def get_db_name_from_api(self):
        return ""
