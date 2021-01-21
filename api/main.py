from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)


@app.route('/')
def hello_world():
    return 'Hello, world!'


#class ClassName(Resource):
#   methods

#api.add_resource(ClassName, '/class')

if __name__ == '__main__': #  Check I'm not importing (I think)
    app.run() # Run the app