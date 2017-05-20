import flask
from flask.views import View,MethodView



# 基于类的视图

class RegUser(View):
    def dispatch_request(self):
        return flask.render_template('reg.html')

class MyRegUser(MethodView):
    def get(self):
        return flask.render_template('reg.html')

    def post(self):
        # if request.method == 'POST':
        #   pass
        return None




class UserLogin(View):
    def dispatch_request(self):
        pass