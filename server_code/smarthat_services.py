from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask.ext.mysql import MySQL



mysql = MySQL()
app = Flask(__smarthatservices__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'smarthat'
app.config['MYSQL_DATABASE_PASSWORD'] = 'LiKlCje2ClQ2K_tAIIAG'
app.config['MYSQL_DATABASE_DB'] = 'samrthat_data'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'


mysql.init_app(app)

api = Api(app)

class AuthenticateDevice(Resource):
    def post(self):
        try:
            # Parse the arguments

            parser = reqparse.RequestParser()
            parser.add_argument('email', type=str, help='Email address for Authentication')
            parser.add_argument('password', type=str, help='Password for Authentication')
            args = parser.parse_args()

            _deviceName = args['email']
            _userPassword = args['password']

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_AuthenticateUser',(_deviceName,))
            data = cursor.fetchall()


            if(len(data)>0):
                if(str(data[0][2])==_userPassword):
                    return {'status':200,'UserId':str(data[0][0])}
                else:
                    return {'status':100,'message':'Authentication failure'}

        except Exception as e:
            return {'error': str(e)}


class GetAllItems(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('id', type=str)
            args = parser.parse_args()

            _userId = args['id']

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_GetAllItems',(_userId,))
            data = cursor.fetchall()

            items_list=[];
            for item in data:
                i = {
                    'Id':item[0],
                    'Item':item[1]
                }
                items_list.append(i)

            return {'StatusCode':'200','Items':items_list}

        except Exception as e:
            return {'error': str(e)}

class AddItem(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('id', type=str)
            parser.add_argument('item', type=str)
            args = parser.parse_args()

            _userId = args['id']
            _item = args['item']

            print _userId;

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_AddItems',(_userId,_item))
            data = cursor.fetchall()

            conn.commit()
            return {'StatusCode':'200','Message': 'Success'}

        except Exception as e:
            return {'error': str(e)}

class CreateUser(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, help='Name of SmartHat Unit')
            parser.add_argument('key', type=str, help='Key for device Authentication')
            args = parser.parse_args()

            _deviceName = args['name']
            _deviceKey = args['key']

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('spAddDevice',(_deviceName,_userPassword))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return {'StatusCode':'200','Message': 'Device Added Sucessfully'}
            else:
                return {'StatusCode':'1000','Message': str(data[0])}

        except Exception as e:
            return {'error': str(e)}


# class CreateUser(Resource):
#     def post(self):
#         try:
#             # Parse the arguments
#             parser = reqparse.RequestParser()
#             parser.add_argument('email', type=str, help='Email address to create user')
#             parser.add_argument('password', type=str, help='Password to create user')
#             args = parser.parse_args()
#
#             _deviceName = args['email']
#             _userPassword = args['password']
#
#             conn = mysql.connect()
#             cursor = conn.cursor()
#             cursor.callproc('spCreateUser',(_deviceName,_userPassword))
#             data = cursor.fetchall()
#
#             if len(data) is 0:
#                 conn.commit()
#                 return {'StatusCode':'200','Message': 'User creation success'}
#             else:
#                 return {'StatusCode':'1000','Message': str(data[0])}
#
#         except Exception as e:
#             return {'error': str(e)}



api.add_resource(CreateUser, '/CreateUser')
api.add_resource(AuthenticateUser, '/AuthenticateUser')
api.add_resource(AddItem, '/AddItem')
api.add_resource(GetAllItems, '/GetAllItems')

if __name__ == '__main__':
    app.run(debug=True)
