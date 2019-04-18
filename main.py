import asyncio
import datetime
import websockets
import mysql.connector
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config

def connect():
    """ Connect to MySQL database """

    db_config = read_db_config()

    try:
        print('Connecting to MySQL database...')
        conn = MySQLConnection(**db_config)

        if conn.is_connected():
            print('connection established.')
        else:
            print('connection failed.')

    except Error as error:
        print(error)


clients = []
connect()


async def ws(websocket, path):

    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    nickname = await websocket.recv()
    clients.append({"ws": websocket, "nick": nickname})
    current_idx = len(clients) - 1

    print(f"New connection {current_idx}")

    cursor.execute("SELECT * FROM messages")
    row = cursor.fetchone()
    while row is not None:
        to_send_history = f"{row[2]} | {row[0]}: {row[1]}"
        await clients[current_idx].get('ws').send(to_send_history)
        row = cursor.fetchone()

    while True:

        message = await websocket.recv()

        if message == "CLOSE":
            print("CLOSING CONNECTION")
            clients[current_idx].get('ws').close()
            clients.pop(current_idx)
            return

        query = "INSERT INTO messages (Login, m_Text) VALUES (%s,%s)"
        args = (clients[current_idx].get('nick'), message)
        cursor.execute(query, args)
        conn.commit()

        to_send = f"{datetime.datetime.now().strftime('%H:%M:%S')} | {clients[current_idx].get('nick')}: {message}"

        for client in clients:
            await client.get('ws').send(to_send)

        await asyncio.sleep(0)

start_server = websockets.serve(ws, "localhost", 8081)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
