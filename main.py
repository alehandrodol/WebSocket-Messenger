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

    cursor.execute("SELECT * FROM messages")
    row = cursor.fetchone()
    while row is not None:
        to_send_history = f"{row[2]} | {row[0]}: {row[1]} {row[3]}"
        await clients[current_idx].get('ws').send(to_send_history)
        row = cursor.fetchone()

    while True:

        message = await websocket.recv()

        if message == "CLOSE":
            print("CLOSING CONNECTION")
            clients[current_idx].get('ws').close()
            clients.pop(current_idx)
            return
        if "UPDATE " in message:
            # Message here is 'UPDATE id "message"'
            data = message.split(" ")
            query = f'UPDATE messages SET m_Text="{" ".join(data[2:])}" WHERE id={data[1]};'
            cursor.execute(query)
            conn.commit()
            await reload(cursor)
            continue
        if "DELETE " in message:
            inId = message.split(" ")[1]
            query = f'DELETE FROM messages WHERE id={inId}'
            print(query)
            cursor.execute(query)
            conn.commit()
            await reload(cursor)
            continue

        query = "INSERT INTO messages (Login, m_Text) VALUES (%s,%s);"
        args = (clients[current_idx].get('nick'), message)
        cursor.execute(query, args)
        conn.commit()

        query = "SELECT ID FROM messages ORDER BY ID DESC LIMIT 1;"
        cursor.execute(query)
        id = cursor.fetchone()

        await sendToAll(message, current_idx, id)

        await asyncio.sleep(0)

async def sendToAll(message, current_idx, id):
    to_send = f"{datetime.datetime.now().strftime('%H:%M:%S')} | {clients[current_idx].get('nick')}: {message} {id[0]}"

    for client in clients:
        await client.get('ws').send(to_send)

async def reload(cursor):
    cursor.execute("SELECT * FROM messages")
    row = cursor.fetchone()

    for client in clients:
        await client.get('ws').send("CLEAR")

    while row is not None:
        to_send_history = f"{row[2]} | {row[0]}: {row[1]} {row[3]}"
        for client in clients:
            await client.get('ws').send(to_send_history)
        row = cursor.fetchone()

start_server = websockets.serve(ws, "localhost", 8081)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
