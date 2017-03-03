from SimpleXMLRPCServer import SimpleXMLRPCServer
import logging
import os
import mysql.connector

try:
    conn = mysql.connector.connect(user='gpslogger', password='O*YGb&iqweruY7u654*', host='127.0.0.1', database='gpslog')
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  conn.close()


# Set up logging
logging.basicConfig(level=logging.INFO)

server = SimpleXMLRPCServer(
    ('localhost', 9000),
    logRequests=True,
)


# Expose a function
def list_contents(dir_name):
    logging.info('list_contents(%s)', dir_name)
    return os.listdir(dir_name)
server.register_function(list_contents)

#def save_coordinates(unit_id, lat, lon, timestamp):
# Start the server
try:
    print('Use Control-C to exit')
    server.serve_forever()
except KeyboardInterrupt:
    print('Exiting')
