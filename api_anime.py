from ast import Try
import io
from urllib.request import urlopen
from asyncio.windows_events import NULL
from concurrent.futures import thread
from pickle import TRUE
from pprint import pprint
from re import search
import time
import datetime as DT
from datetime import datetime
from turtle import st
from pyshikiapi import API
import json
import pyodbc
from PIL import Image
import requests
from io import BytesIO

def getDatetime(date):
    try:
        date_time_obj = DT.datetime.fromisoformat(date)
        date_time_obj = date_time_obj.strftime('%Y-%m-%d %H:%M:%S')
        return date
    except Exception as e:
        print('next_episode_at == NONE, returning NONE...')
        return None 
        # print(f"{e}")
    
def get_release(date):
    try:
        result = datetime.strptime(date, '%m/%d/%y')
        return result
    except:
        print('released_on == NONE, returning NONE...')
        return None
def get_franchise(name):
    cursor.execute("SELECT * FROM \"Franchize\"")
    for fr in cursor.fetchall():
        if(fr.name == name):
            return fr.id
    

def token_file_saver(token):  # A function which accepts 1 dict-like argument
    with open('token.json', 'w') as f:
        json.dump(token, f)

conn_str="https://kawai.shikimori.one"

database_str = (
    'Driver={PostgreSQL UNICODE};Server=localhost;Port=5432;Database=AniGO;Uid=admin;Pwd=a;'
    )
connection = pyodbc.connect(database_str)

if connection:
    print("connection is true")
cursor = connection.cursor()


disallowed_chars = ",._ !^&?:"
app_name = 'Api Test'
client_id = 'bce7ad35b631293ff006be882496b29171792c8839b5094115268da7a97ca34c'
client_secret = '811459eada36b14ff0cf0cc353f8162e72a7d6e6c7930b647a5c587d1beffe68'


api = API(app_name, client_id, client_secret, token_update_callback=token_file_saver)



# studios = api._send_request("GET", f"/studios")
# for item in studios:
#     stud_poster = None
#     if(item['image'] != None): 
#         stud_poster = requests.get(f"{conn_str}{item['image']}")
#         stud_poster = stud_poster.content
#     cursor.execute(f"insert into \"Studio\" (shiki_id, name, real, image) values(?,?,?,?)", item['id'], item['name'], item['real'], stud_poster)

# # genres = api._send_request("GET",f"/genres")
# # for item in genres:
# #     if item['kind'] == 'manga':
# #         continue
# #     cursor.execute(f"insert into \"Genre\" (shiki_id, name_eng, name_rus) values(?,?,?)", item['id'], item['name'], item['russian'])

# connection.commit()


i=1
while True:
    ong = 0
    time.sleep(0.125)
    next_ep = ""
    
    try:
        is_franchise = 1
        selected_fr_id = 0

        is_type = 1
        selected_tp_id=0


        anime = api._send_request("GET", f"/animes/{i}")

        cursor.execute("SELECT * FROM \"Franchize\"")
        for row in cursor.fetchall():
            if(row.name != anime['franchise'] or is_franchise == None):
                is_franchise=1
            else:
                is_franchise=0
                break

        if is_franchise == 1:
            print(anime['franchise'])
            cursor.execute(f"insert into \"Franchize\" (name) values(?)", anime['franchise']) 
            connection.commit() 

        cursor.execute("SELECT * FROM \"Franchize\"")
        for row in cursor.fetchall():
            if(row.name == anime['franchise']):
                selected_fr_id = row.id
        #############################################
        cursor.execute("SELECT * FROM \"Type\"")
        for row in cursor.fetchall():
            if(row.name != anime['kind'] or is_type == None):
                is_type=1
            else:
                is_type=0
                break

        if is_type == 1:
            print(anime['kind'])
            cursor.execute(f"insert into \"Type\" (name) values(?)", anime['kind']) 
            connection.commit() 

        cursor.execute("SELECT * FROM \"Type\"")
        for row in cursor.fetchall():
            if(row.name == anime['kind']):
                selected_tp_id = row.id
                
        


        cursor.execute(f"insert into \"Anime\" (name_eng,name_rus, score_shiki, description, ongoing, next_episode_at,shiki_id,released_on, franchize_id, type_id) values(?, ? ,?,?,?,?,?,?,?,?)",anime['name'],anime['russian'],float(anime['score']), anime['description'], anime['ongoing'],getDatetime(anime['next_episode_at']),anime['id'],get_release(anime['released_on']), selected_fr_id, selected_tp_id)

       
        resp_orig = requests.get(f"{conn_str}{anime['image']['original']}")
        resp_prew = requests.get(f"{conn_str}{anime['image']['preview']}")
        cursor.execute(f"insert into \"Image\"(anime_id, original, preview) values(?, ?, ?)", anime['id'], resp_orig.content, resp_prew.content)
        
        for item in anime['japanese']:
                cursor.execute(f"insert into \"Japanese\"(name, anime_id) values(?,?)", item, anime['id'])
        for item in anime['genres']:
                cursor.execute(f"insert into \"GenreAnime\"(anime_id, genre_id) values(?,?)", anime['id'],  item['id'])
        for item in anime['studios']:
                cursor.execute(f"insert into \"StudioAnime\"(anime_id, studio_id) values(?,?)", anime['id'],  item['id'])
        for item in anime['screenshots']:
                if(item['original'] != None):
                    resp_orig = requests.get(f"{conn_str}{item['original']}")
                    resp_orig = resp_orig.content
                cursor.execute(f"insert into \"Screenshot\"(anime_id, image) values(?,?)", anime['id'],  resp_orig)
                        

        
    except Exception as e:
        print(f'{i}   {e}')
        if("429" in str(e)):
            continue
        i=i+1
        continue
    #print(f"insert into Anime(name_eng,name_rus, score_shiki, description, ongoing, nex_episode_at) values('{anime_name}', '{anime['russian']}' ,{float(anime['score'])},'{anime['description']}',{ong},{formatted})")
    i=i+1
    connection.commit()
    print('good')
   
