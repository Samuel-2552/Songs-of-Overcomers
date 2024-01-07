from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import sqlite3
import os
import hashlib
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room, leave_room
import re

import logging

logging.basicConfig(filename='/home/oilnwine/flaskapp.log', level=logging.DEBUG)
#Then use logging commands throughout your Flask app to log relevant information
logging.debug('Debug message')
logging.info('Informational message')
logging.error('Error message')

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

DATABASE = 'oilnwine.db'

def create_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

def remove_special_characters(input_string):
    # Define a regex pattern to match special characters
    pattern = r'[^a-zA-Z0-9\s]'  # Matches any character that is not a letter, digit, or whitespace

    # Replace special characters with an empty string
    processed_string = re.sub(pattern, '', input_string)
    return processed_string

def create_users_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            otp INTEGER DEFAULT 0,
            verified INTEGER DEFAULT 0,
            permission INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def create_songs_table():
    conn = create_connection()
    cursor = conn.cursor()

    # Create the songs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            alternate_title TEXT,
            lyrics TEXT,
            transliteration TEXT,
            chord TEXT,
            search_title TEXT,
            search_lyrics TEXT,
            youtube_link TEXT,
            create_date TEXT,
            modified_date TEXT,
            username TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def song_view(lyrics, transliteration_lyrics, chord):
    if transliteration_lyrics == "" or transliteration_lyrics == None or transliteration_lyrics == "None":
        paragraphs = re.split(r'\r?\n|\r', lyrics)
        para_count = 1
        if chord == None or chord =="None":
            chord = ''
        else:
            chord = "<span style='font-weight:bold;font-size:larger;'>" + chord + "</span><br>"
        formatted_song = f"<p id={para_count} style='border: 1px solid black;padding: 10px;'>{chord}"
        for paragraph in paragraphs:
            if paragraph == "":
                para_count +=1
                formatted_song += f"</p><p id={para_count} style='border: 1px solid black;padding: 10px;'>"
            else:
                formatted_song += f'{paragraph}<br>'
    else:
        if chord == None or chord =="None":
            chord = ''
        else:
            chord = "<span style='font-weight:bold;font-size:larger;'>" + chord + "</span><br>"
        paragraphs1 = re.split(r'\r?\n|\r', lyrics)
        paragraphs2 = re.split(r'\r?\n|\r', transliteration_lyrics)
        print(paragraphs1)
        print(paragraphs2)
        allow1 = 0
        allow2 = 0
        para_count = 1
        formatted_song = f"<p id={para_count} style='border: 1px solid black;padding: 10px;'>{chord}"
        for i in range(max(len(paragraphs2),len(paragraphs1))):
            if allow1 == 0:
                try:
                    paragraphs1[i]
                except:
                    allow1 = 1
            if allow2 == 0:
                try:
                    paragraphs2[i]
                except:
                    allow2 = 1
            
            if allow1 == 0 and allow2 == 0:
                if paragraphs1[i] == "" or paragraphs2[i] == "":
                    para_count += 1
                    formatted_song += f"</p><p id={para_count} style='border: 1px solid black;padding: 10px;'>"
                else:
                    formatted_song += f"{paragraphs1[i]}<br><span style='color:green;'>{paragraphs2[i]}</span><br>"
            
            if allow1 ==1:
                if paragraphs2[i] == "":
                    para_count += 1
                    formatted_song += f"</p><p id={para_count} style='border: 1px solid black;padding: 10px; color:green;'>"
                else:
                    formatted_song += f'{paragraphs2[i]}<br>'

            if allow2 ==1:
                if paragraphs1[i] == "":
                    para_count += 1
                    formatted_song += f"</p><p id={para_count} style='border: 1px solid black;padding: 10px;'>"
                else:
                    formatted_song += f'{paragraphs1[i]}<br>'

    return formatted_song

# Call the function to create the 'songs' table
create_songs_table()

create_users_table()

@app.route('/download')
def download_db():
    db_file_path = 'oilnwine.db'  # Replace with your SQLite database file path
    
    return send_file(db_file_path, as_attachment=True)

@app.route('/download_logs')
def download_log():
    db_file_path = '/home/oilnwine/flaskapp.log'  # Replace with your SQLite database file path

    return send_file(db_file_path, as_attachment=True)

@app.route('/')
def home():
    conn = sqlite3.connect(DATABASE)
    if 'username' in session:
        login = True
        user = session['username']
        cursor1 = conn.cursor()
        cursor1.execute('SELECT permission FROM users where username = ?', (user,))
        permission = cursor1.fetchone()
        permission = permission[0]
        
    else:
        login = False
        user=""
        permission = 0

    
    
    cursor = conn.cursor()
    

    

    # Execute a query to select data from the 'songs' table
    cursor.execute('SELECT id, title, search_title, search_lyrics FROM songs')
    # Fetch all rows with the specified columns
    rows = cursor.fetchall()

    sorted_rows = sorted(rows, key=lambda x: x[1].lower())


    # print(rows)
    conn.close()

    return render_template("home.html", login=login, user=user, rows=sorted_rows, permission = permission)

@app.route('/tamil')
def tamil():
    conn = sqlite3.connect(DATABASE)
    if 'username' in session:
        login = True
        user = session['username']
        cursor1 = conn.cursor()
        cursor1.execute('SELECT permission FROM users where username = ?', (user,))
        permission = cursor1.fetchone()
        permission = permission[0]
        
    else:
        login = False
        user=""
        permission = 0

    
    
    cursor = conn.cursor()
    

    

    # Execute a SELECT query to fetch all rows
    cursor.execute('SELECT id, title, search_title, search_lyrics FROM songs')

    # Fetch the results
    all_rows = cursor.fetchall()

    # Filter the results based on the search term using Python
    filtered_results = [row for row in all_rows if 'tamil' in row[1] or 'Tamil' in row[1] or 'tamil' in row[2] or 'Tamil' in row[2]]

    # Process the filtered results

    # print(filtered_results)

    sorted_rows = sorted(filtered_results, key=lambda x: x[1].lower())

    # print(sorted_rows)


    # print(rows)
    conn.close()

    return render_template("tamil.html", login=login, user=user, rows=sorted_rows, permission = permission)

@app.route('/telugu')
def telugu():
    conn = sqlite3.connect(DATABASE)
    if 'username' in session:
        login = True
        user = session['username']
        cursor1 = conn.cursor()
        cursor1.execute('SELECT permission FROM users where username = ?', (user,))
        permission = cursor1.fetchone()
        permission = permission[0]
        
    else:
        login = False
        user=""
        permission = 0

    
    
    cursor = conn.cursor()
    

    

    # Execute a SELECT query to fetch all rows
    cursor.execute('SELECT id, title, search_title, search_lyrics FROM songs')

    # Fetch the results
    all_rows = cursor.fetchall()

    # Filter the results based on the search term using Python
    filtered_results = [row for row in all_rows if 'telugu' in row[1] or 'Telugu' in row[1] or 'Telegu' in row[1] or 'telegu' in row[1] or 'telugu' in row[2] or 'Telugu' in row[2] or 'Telegu' in row[2] or 'telegu' in row[2]]

    # Process the filtered results

    # print(filtered_results)

    sorted_rows = sorted(filtered_results, key=lambda x: x[1].lower())

    # print(sorted_rows)


    # print(rows)
    conn.close()

    return render_template("telugu.html", login=login, user=user, rows=sorted_rows, permission = permission)

result_list = [[1, 1, 1, 'Genesis 1'], [2, 1, 2, 'Genesis 2'], [3, 1, 3, 'Genesis 3'], [4, 1, 4, 'Genesis 4'], [5, 1, 5, 'Genesis 5'], [6, 1, 6, 'Genesis 6'], [7, 1, 7, 'Genesis 7'], [8, 1, 8, 'Genesis 8'], [9, 1, 9, 'Genesis 9'], [10, 1, 10, 'Genesis 10'], [11, 1, 11, 'Genesis 11'], [12, 1, 12, 'Genesis 12'], [13, 1, 13, 'Genesis 13'], [14, 1, 14, 'Genesis 14'], [15, 1, 15, 'Genesis 15'], [16, 1, 16, 'Genesis 16'], [17, 1, 17, 'Genesis 17'], [18, 1, 18, 'Genesis 18'], [19, 1, 19, 'Genesis 19'], [20, 1, 20, 'Genesis 20'], [21, 1, 21, 'Genesis 21'], [22, 1, 22, 'Genesis 22'], [23, 1, 23, 'Genesis 23'], [24, 1, 24, 'Genesis 24'], [25, 1, 25, 'Genesis 25'], [26, 1, 26, 'Genesis 26'], [27, 1, 27, 'Genesis 27'], [28, 1, 28, 'Genesis 28'], [29, 1, 29, 'Genesis 29'], [30, 1, 30, 'Genesis 30'], [31, 1, 31, 'Genesis 31'], [32, 1, 32, 'Genesis 32'], [33, 1, 33, 'Genesis 33'], [34, 1, 34, 'Genesis 34'], [35, 1, 35, 'Genesis 35'], [36, 1, 36, 'Genesis 36'], [37, 1, 37, 'Genesis 37'], [38, 1, 38, 'Genesis 38'], [39, 1, 39, 'Genesis 39'], [40, 1, 40, 'Genesis 40'], [41, 1, 41, 'Genesis 41'], [42, 1, 42, 'Genesis 42'], [43, 1, 43, 'Genesis 43'], [44, 1, 44, 'Genesis 44'], [45, 1, 45, 'Genesis 45'], [46, 1, 46, 'Genesis 46'], [47, 1, 47, 'Genesis 47'], [48, 1, 48, 'Genesis 48'], [49, 1, 49, 'Genesis 49'], [50, 1, 50, 'Genesis 50'], [51, 2, 1, 'Exodus 1'], [52, 2, 2, 'Exodus 2'], [53, 2, 3, 'Exodus 3'], [54, 2, 4, 'Exodus 4'], [55, 2, 5, 'Exodus 5'], [56, 2, 6, 'Exodus 6'], [57, 2, 7, 'Exodus 7'], [58, 2, 8, 'Exodus 8'], [59, 2, 9, 'Exodus 9'], [60, 2, 10, 'Exodus 10'], [61, 2, 11, 'Exodus 11'], [62, 2, 12, 'Exodus 12'], [63, 2, 13, 'Exodus 13'], [64, 2, 14, 'Exodus 14'], [65, 2, 15, 'Exodus 15'], [66, 2, 16, 'Exodus 16'], [67, 2, 17, 'Exodus 17'], [68, 2, 18, 'Exodus 18'], [69, 2, 19, 'Exodus 19'], [70, 2, 20, 'Exodus 20'], [71, 2, 21, 'Exodus 21'], [72, 2, 22, 'Exodus 22'], [73, 2, 23, 'Exodus 23'], [74, 2, 24, 'Exodus 24'], [75, 2, 25, 'Exodus 25'], [76, 2, 26, 'Exodus 26'], [77, 2, 27, 'Exodus 27'], [78, 2, 28, 'Exodus 28'], [79, 2, 29, 'Exodus 29'], [80, 2, 30, 'Exodus 30'], [81, 2, 31, 'Exodus 31'], [82, 2, 32, 'Exodus 32'], [83, 2, 33, 'Exodus 33'], [84, 2, 34, 'Exodus 34'], [85, 2, 35, 'Exodus 35'], [86, 2, 36, 'Exodus 36'], [87, 2, 37, 'Exodus 37'], [88, 2, 38, 'Exodus 38'], [89, 2, 39, 'Exodus 39'], [90, 2, 40, 'Exodus 40'], [91, 3, 1, 'Leviticus 1'], [92, 3, 2, 'Leviticus 2'], [93, 3, 3, 'Leviticus 3'], [94, 3, 4, 'Leviticus 4'], [95, 3, 5, 'Leviticus 5'], [96, 3, 6, 'Leviticus 6'], [97, 3, 7, 'Leviticus 7'], [98, 3, 8, 'Leviticus 8'], [99, 3, 9, 'Leviticus 9'], [100, 3, 10, 'Leviticus 10'], [101, 3, 11, 'Leviticus 11'], [102, 3, 12, 'Leviticus 12'], [103, 3, 13, 'Leviticus 13'], [104, 3, 14, 'Leviticus 14'], [105, 3, 15, 'Leviticus 15'], [106, 3, 16, 'Leviticus 16'], [107, 3, 17, 'Leviticus 17'], [108, 3, 18, 'Leviticus 18'], [109, 3, 19, 'Leviticus 19'], [110, 3, 20, 'Leviticus 20'], [111, 3, 21, 'Leviticus 21'], [112, 3, 22, 'Leviticus 22'], [113, 3, 23, 'Leviticus 23'], [114, 3, 24, 'Leviticus 24'], [115, 3, 25, 'Leviticus 25'], [116, 3, 26, 'Leviticus 26'], [117, 3, 27, 'Leviticus 27'], [118, 4, 1, 'Numbers 1'], [119, 4, 2, 'Numbers 2'], [120, 4, 3, 'Numbers 3'], [121, 4, 4, 'Numbers 4'], [122, 4, 5, 'Numbers 5'], [123, 4, 6, 'Numbers 6'], [124, 4, 7, 'Numbers 7'], [125, 4, 8, 'Numbers 8'], [126, 4, 9, 'Numbers 9'], [127, 4, 10, 'Numbers 10'], [128, 4, 11, 'Numbers 11'], [129, 4, 12, 'Numbers 12'], [130, 4, 13, 'Numbers 13'], [131, 4, 14, 'Numbers 14'], [132, 4, 15, 'Numbers 15'], [133, 4, 16, 'Numbers 16'], [134, 4, 17, 'Numbers 17'], [135, 4, 18, 'Numbers 18'], [136, 4, 19, 'Numbers 19'], [137, 4, 20, 'Numbers 20'], [138, 4, 21, 'Numbers 21'], [139, 4, 22, 'Numbers 22'], [140, 4, 23, 'Numbers 23'], [141, 4, 24, 'Numbers 24'], [142, 4, 25, 'Numbers 25'], [143, 4, 26, 'Numbers 26'], [144, 4, 27, 'Numbers 27'], [145, 4, 28, 'Numbers 28'], [146, 4, 29, 'Numbers 29'], [147, 4, 30, 'Numbers 30'], [148, 4, 31, 'Numbers 31'], [149, 4, 32, 'Numbers 32'], [150, 4, 33, 'Numbers 33'], [151, 4, 34, 'Numbers 34'], [152, 4, 35, 'Numbers 35'], [153, 4, 36, 'Numbers 36'], [154, 5, 1, 'Deuteronomy 1'], [155, 5, 2, 'Deuteronomy 2'], [156, 5, 3, 'Deuteronomy 3'], [157, 5, 4, 'Deuteronomy 4'], [158, 5, 5, 'Deuteronomy 5'], [159, 5, 6, 'Deuteronomy 6'], [160, 5, 7, 'Deuteronomy 7'], [161, 5, 8, 'Deuteronomy 8'], [162, 5, 9, 'Deuteronomy 9'], [163, 5, 10, 'Deuteronomy 10'], [164, 5, 11, 'Deuteronomy 11'], [165, 5, 12, 'Deuteronomy 12'], [166, 5, 13, 'Deuteronomy 13'], [167, 5, 14, 'Deuteronomy 14'], [168, 5, 15, 'Deuteronomy 15'], [169, 5, 16, 'Deuteronomy 16'], [170, 5, 17, 'Deuteronomy 17'], [171, 5, 18, 'Deuteronomy 18'], [172, 5, 19, 'Deuteronomy 19'], [173, 5, 20, 'Deuteronomy 20'], [174, 5, 21, 'Deuteronomy 21'], [175, 5, 22, 'Deuteronomy 22'], [176, 5, 23, 'Deuteronomy 23'], [177, 5, 24, 'Deuteronomy 24'], [178, 5, 25, 'Deuteronomy 25'], [179, 5, 26, 'Deuteronomy 26'], [180, 5, 27, 'Deuteronomy 27'], [181, 5, 28, 'Deuteronomy 28'], [182, 5, 29, 'Deuteronomy 29'], [183, 5, 30, 'Deuteronomy 30'], [184, 5, 31, 'Deuteronomy 31'], [185, 5, 32, 'Deuteronomy 32'], [186, 5, 33, 'Deuteronomy 33'], [187, 5, 34, 'Deuteronomy 34'], [188, 6, 1, 'Joshua 1'], [189, 6, 2, 'Joshua 2'], [190, 6, 3, 'Joshua 3'], [191, 6, 4, 'Joshua 4'], [192, 6, 5, 'Joshua 5'], [193, 6, 6, 'Joshua 6'], [194, 6, 7, 'Joshua 7'], [195, 6, 8, 'Joshua 8'], [196, 6, 9, 'Joshua 9'], [197, 6, 10, 'Joshua 10'], [198, 6, 11, 'Joshua 11'], [199, 6, 12, 'Joshua 12'], [200, 6, 13, 'Joshua 13'], [201, 6, 14, 'Joshua 14'], [202, 6, 15, 'Joshua 15'], [203, 6, 16, 'Joshua 16'], [204, 6, 17, 'Joshua 17'], [205, 6, 18, 'Joshua 18'], [206, 6, 19, 'Joshua 19'], [207, 6, 20, 'Joshua 20'], [208, 6, 21, 'Joshua 21'], [209, 6, 22, 'Joshua 22'], [210, 6, 23, 'Joshua 23'], [211, 6, 24, 'Joshua 24'], [212, 7, 1, 'Judges 1'], [213, 7, 2, 'Judges 2'], [214, 7, 3, 'Judges 3'], [215, 7, 4, 'Judges 4'], [216, 7, 5, 'Judges 5'], [217, 7, 6, 'Judges 6'], [218, 7, 7, 'Judges 7'], [219, 7, 8, 'Judges 8'], [220, 7, 9, 'Judges 9'], [221, 7, 10, 'Judges 10'], [222, 7, 11, 'Judges 11'], [223, 7, 12, 'Judges 12'], [224, 7, 13, 'Judges 13'], [225, 7, 14, 'Judges 14'], [226, 7, 15, 'Judges 15'], [227, 7, 16, 'Judges 16'], [228, 7, 17, 'Judges 17'], [229, 7, 18, 'Judges 18'], [230, 7, 19, 'Judges 19'], [231, 7, 20, 'Judges 20'], [232, 7, 21, 'Judges 21'], [233, 8, 1, 'Ruth 1'], [234, 8, 2, 'Ruth 2'], [235, 8, 3, 'Ruth 3'], [236, 8, 4, 'Ruth 4'], [237, 9, 1, '1 Samuel 1'], [238, 9, 2, '1 Samuel 2'], [239, 9, 3, '1 Samuel 3'], [240, 9, 4, '1 Samuel 4'], [241, 9, 5, '1 Samuel 5'], [242, 9, 6, '1 Samuel 6'], [243, 9, 7, '1 Samuel 7'], [244, 9, 8, '1 Samuel 8'], [245, 9, 9, '1 Samuel 9'], [246, 9, 10, '1 Samuel 10'], [247, 9, 11, '1 Samuel 11'], [248, 9, 12, '1 Samuel 12'], [249, 9, 13, '1 Samuel 13'], [250, 9, 14, '1 Samuel 14'], [251, 9, 15, '1 Samuel 15'], [252, 9, 16, '1 Samuel 16'], [253, 9, 17, '1 Samuel 17'], [254, 9, 18, '1 Samuel 18'], [255, 9, 19, '1 Samuel 19'], [256, 9, 20, '1 Samuel 20'], [257, 9, 21, '1 Samuel 21'], [258, 9, 22, '1 Samuel 22'], [259, 9, 23, '1 Samuel 23'], [260, 9, 24, '1 Samuel 24'], [261, 9, 25, '1 Samuel 25'], [262, 9, 26, '1 Samuel 26'], [263, 9, 27, '1 Samuel 27'], [264, 9, 28, '1 Samuel 28'], [265, 9, 29, '1 Samuel 29'], [266, 9, 30, '1 Samuel 30'], [267, 9, 31, '1 Samuel 31'], [268, 10, 1, '2 Samuel 1'], [269, 10, 2, '2 Samuel 2'], [270, 10, 3, '2 Samuel 3'], [271, 10, 4, '2 Samuel 4'], [272, 10, 5, '2 Samuel 5'], [273, 10, 6, '2 Samuel 6'], [274, 10, 7, '2 Samuel 7'], [275, 10, 8, '2 Samuel 8'], [276, 10, 9, '2 Samuel 9'], [277, 10, 10, '2 Samuel 10'], [278, 10, 11, '2 Samuel 11'], [279, 10, 12, '2 Samuel 12'], [280, 10, 13, '2 Samuel 13'], [281, 10, 14, '2 Samuel 14'], [282, 10, 15, '2 Samuel 15'], [283, 10, 16, '2 Samuel 16'], [284, 10, 17, '2 Samuel 17'], [285, 10, 18, '2 Samuel 18'], [286, 10, 19, '2 Samuel 19'], [287, 10, 20, '2 Samuel 20'], [288, 10, 21, '2 Samuel 21'], [289, 10, 22, '2 Samuel 22'], [290, 10, 23, '2 Samuel 23'], [291, 10, 24, '2 Samuel 24'], [292, 11, 1, '1 Kings 1'], [293, 11, 2, '1 Kings 2'], [294, 11, 3, '1 Kings 3'], [295, 11, 4, '1 Kings 4'], [296, 11, 5, '1 Kings 5'], [297, 11, 6, '1 Kings 6'], [298, 11, 7, '1 Kings 7'], [299, 11, 8, '1 Kings 8'], [300, 11, 9, '1 Kings 9'], [301, 11, 10, '1 Kings 10'], [302, 11, 11, '1 Kings 11'], [303, 11, 12, '1 Kings 12'], [304, 11, 13, '1 Kings 13'], [305, 11, 14, '1 Kings 14'], [306, 11, 15, '1 Kings 15'], [307, 11, 16, '1 Kings 16'], [308, 11, 17, '1 Kings 17'], [309, 11, 18, '1 Kings 18'], [310, 11, 19, '1 Kings 19'], [311, 11, 20, '1 Kings 20'], [312, 11, 21, '1 Kings 21'], [313, 11, 22, '1 Kings 22'], [314, 12, 1, '2 Kings 1'], [315, 12, 2, '2 Kings 2'], [316, 12, 3, '2 Kings 3'], [317, 12, 4, '2 Kings 4'], [318, 12, 5, '2 Kings 5'], [319, 12, 6, '2 Kings 6'], [320, 12, 7, '2 Kings 7'], [321, 12, 8, '2 Kings 8'], [322, 12, 9, '2 Kings 9'], [323, 12, 10, '2 Kings 10'], [324, 12, 11, '2 Kings 11'], [325, 12, 12, '2 Kings 12'], [326, 12, 13, '2 Kings 13'], [327, 12, 14, '2 Kings 14'], [328, 12, 15, '2 Kings 15'], [329, 12, 16, '2 Kings 16'], [330, 12, 17, '2 Kings 17'], [331, 12, 18, '2 Kings 18'], [332, 12, 19, '2 Kings 19'], [333, 12, 20, '2 Kings 20'], [334, 12, 21, '2 Kings 21'], [335, 12, 22, '2 Kings 22'], [336, 12, 23, '2 Kings 23'], [337, 12, 24, '2 Kings 24'], [338, 12, 25, '2 Kings 25'], [339, 13, 1, '1 Chronicles 1'], [340, 13, 2, '1 Chronicles 2'], [341, 13, 3, '1 Chronicles 3'], [342, 13, 4, '1 Chronicles 4'], [343, 13, 5, '1 Chronicles 5'], [344, 13, 6, '1 Chronicles 6'], [345, 13, 7, '1 Chronicles 7'], [346, 13, 8, '1 Chronicles 8'], [347, 13, 9, '1 Chronicles 9'], [348, 13, 10, '1 Chronicles 10'], [349, 13, 11, '1 Chronicles 11'], [350, 13, 12, '1 Chronicles 12'], [351, 13, 13, '1 Chronicles 13'], [352, 13, 14, '1 Chronicles 14'], [353, 13, 15, '1 Chronicles 15'], [354, 13, 16, '1 Chronicles 16'], [355, 13, 17, '1 Chronicles 17'], [356, 13, 18, '1 Chronicles 18'], [357, 13, 19, '1 Chronicles 19'], [358, 13, 20, '1 Chronicles 20'], [359, 13, 21, '1 Chronicles 21'], [360, 13, 22, '1 Chronicles 22'], [361, 13, 23, '1 Chronicles 23'], [362, 13, 24, '1 Chronicles 24'], [363, 13, 25, '1 Chronicles 25'], [364, 13, 26, '1 Chronicles 26'], [365, 13, 27, '1 Chronicles 27'], [366, 13, 28, '1 Chronicles 28'], [367, 13, 29, '1 Chronicles 29'], [368, 14, 1, '2 Chronicles 1'], [369, 14, 2, '2 Chronicles 2'], [370, 14, 3, '2 Chronicles 3'], [371, 14, 4, '2 Chronicles 4'], [372, 14, 5, '2 Chronicles 5'], [373, 14, 6, '2 Chronicles 6'], [374, 14, 7, '2 Chronicles 7'], [375, 14, 8, '2 Chronicles 8'], [376, 14, 9, '2 Chronicles 9'], [377, 14, 10, '2 Chronicles 10'], [378, 14, 11, '2 Chronicles 11'], [379, 14, 12, '2 Chronicles 12'], [380, 14, 13, '2 Chronicles 13'], [381, 14, 14, '2 Chronicles 14'], [382, 14, 15, '2 Chronicles 15'], [383, 14, 16, '2 Chronicles 16'], [384, 14, 17, '2 Chronicles 17'], [385, 14, 18, '2 Chronicles 18'], [386, 14, 19, '2 Chronicles 19'], [387, 14, 20, '2 Chronicles 20'], [388, 14, 21, '2 Chronicles 21'], [389, 14, 22, '2 Chronicles 22'], [390, 14, 23, '2 Chronicles 23'], [391, 14, 24, '2 Chronicles 24'], [392, 14, 25, '2 Chronicles 25'], [393, 14, 26, '2 Chronicles 26'], [394, 14, 27, '2 Chronicles 27'], [395, 14, 28, '2 Chronicles 28'], [396, 14, 29, '2 Chronicles 29'], [397, 14, 30, '2 Chronicles 30'], [398, 14, 31, '2 Chronicles 31'], [399, 14, 32, '2 Chronicles 32'], [400, 14, 33, '2 Chronicles 33'], [401, 14, 34, '2 Chronicles 34'], [402, 14, 35, '2 Chronicles 35'], [403, 14, 36, '2 Chronicles 36'], [404, 15, 1, 'Ezra 1'], [405, 15, 2, 'Ezra 2'], [406, 15, 3, 'Ezra 3'], [407, 15, 4, 'Ezra 4'], [408, 15, 5, 'Ezra 5'], [409, 15, 6, 'Ezra 6'], [410, 15, 7, 'Ezra 7'], [411, 15, 8, 'Ezra 8'], [412, 15, 9, 'Ezra 9'], [413, 15, 10, 'Ezra 10'], [414, 16, 1, 'Nehemiah 1'], [415, 16, 2, 'Nehemiah 2'], [416, 16, 3, 'Nehemiah 3'], [417, 16, 4, 'Nehemiah 4'], [418, 16, 5, 'Nehemiah 5'], [419, 16, 6, 'Nehemiah 6'], [420, 16, 7, 'Nehemiah 7'], [421, 16, 8, 'Nehemiah 8'], [422, 16, 9, 'Nehemiah 9'], [423, 16, 10, 'Nehemiah 10'], [424, 16, 11, 'Nehemiah 11'], [425, 16, 12, 'Nehemiah 12'], [426, 16, 13, 'Nehemiah 13'], [427, 17, 1, 'Esther 1'], [428, 17, 2, 'Esther 2'], [429, 17, 3, 'Esther 3'], [430, 17, 4, 'Esther 4'], [431, 17, 5, 'Esther 5'], [432, 17, 6, 'Esther 6'], [433, 17, 7, 'Esther 7'], [434, 17, 8, 'Esther 8'], [435, 17, 9, 'Esther 9'], [436, 17, 10, 'Esther 10'], [437, 18, 1, 'Job 1'], [438, 18, 2, 'Job 2'], [439, 18, 3, 'Job 3'], [440, 18, 4, 'Job 4'], [441, 18, 5, 'Job 5'], [442, 18, 6, 'Job 6'], [443, 18, 7, 'Job 7'], [444, 18, 8, 'Job 8'], [445, 18, 9, 'Job 9'], [446, 18, 10, 'Job 10'], [447, 18, 11, 'Job 11'], [448, 18, 12, 'Job 12'], [449, 18, 13, 'Job 13'], [450, 18, 14, 'Job 14'], [451, 18, 15, 'Job 15'], [452, 18, 16, 'Job 16'], [453, 18, 17, 'Job 17'], [454, 18, 18, 'Job 18'], [455, 18, 19, 'Job 19'], [456, 18, 20, 'Job 20'], [457, 18, 21, 'Job 21'], [458, 18, 22, 'Job 22'], [459, 18, 23, 'Job 23'], [460, 18, 24, 'Job 24'], [461, 18, 25, 'Job 25'], [462, 18, 26, 'Job 26'], [463, 18, 27, 'Job 27'], [464, 18, 28, 'Job 28'], [465, 18, 29, 'Job 29'], [466, 18, 30, 'Job 30'], [467, 18, 31, 'Job 31'], [468, 18, 32, 'Job 32'], [469, 18, 33, 'Job 33'], [470, 18, 34, 'Job 34'], [471, 18, 35, 'Job 35'], [472, 18, 36, 'Job 36'], [473, 18, 37, 'Job 37'], [474, 18, 38, 'Job 38'], [475, 18, 39, 'Job 39'], [476, 18, 40, 'Job 40'], [477, 18, 41, 'Job 41'], [478, 18, 42, 'Job 42'], [479, 19, 1, 'Psalms 1'], [480, 19, 2, 'Psalms 2'], [481, 19, 3, 'Psalms 3'], [482, 19, 4, 'Psalms 4'], [483, 19, 5, 'Psalms 5'], [484, 19, 6, 'Psalms 6'], [485, 19, 7, 'Psalms 7'], [486, 19, 8, 'Psalms 8'], [487, 19, 9, 'Psalms 9'], [488, 19, 10, 'Psalms 10'], [489, 19, 11, 'Psalms 11'], [490, 19, 12, 'Psalms 12'], [491, 19, 13, 'Psalms 13'], [492, 19, 14, 'Psalms 14'], [493, 19, 15, 'Psalms 15'], [494, 19, 16, 'Psalms 16'], [495, 19, 17, 'Psalms 17'], [496, 19, 18, 'Psalms 18'], [497, 19, 19, 'Psalms 19'], [498, 19, 20, 'Psalms 20'], [499, 19, 21, 'Psalms 21'], [500, 19, 22, 'Psalms 22'], [501, 19, 23, 'Psalms 23'], [502, 19, 24, 'Psalms 24'], [503, 19, 25, 'Psalms 25'], [504, 19, 26, 'Psalms 26'], [505, 19, 27, 'Psalms 27'], [506, 19, 28, 'Psalms 28'], [507, 19, 29, 'Psalms 29'], [508, 19, 30, 'Psalms 30'], [509, 19, 31, 'Psalms 31'], [510, 19, 32, 'Psalms 32'], [511, 19, 33, 'Psalms 33'], [512, 19, 34, 'Psalms 34'], [513, 19, 35, 'Psalms 35'], [514, 19, 36, 'Psalms 36'], [515, 19, 37, 'Psalms 37'], [516, 19, 38, 'Psalms 38'], [517, 19, 39, 'Psalms 39'], [518, 19, 40, 'Psalms 40'], [519, 19, 41, 'Psalms 41'], [520, 19, 42, 'Psalms 42'], [521, 19, 43, 'Psalms 43'], [522, 19, 44, 'Psalms 44'], [523, 19, 45, 'Psalms 45'], [524, 19, 46, 'Psalms 46'], [525, 19, 47, 'Psalms 47'], [526, 19, 48, 'Psalms 48'], [527, 19, 49, 'Psalms 49'], [528, 19, 50, 'Psalms 50'], [529, 19, 51, 'Psalms 51'], [530, 19, 52, 'Psalms 52'], [531, 19, 53, 'Psalms 53'], [532, 19, 54, 'Psalms 54'], [533, 19, 55, 'Psalms 55'], [534, 19, 56, 'Psalms 56'], [535, 19, 57, 'Psalms 57'], [536, 19, 58, 'Psalms 58'], [537, 19, 59, 'Psalms 59'], [538, 19, 60, 'Psalms 60'], [539, 19, 61, 'Psalms 61'], [540, 19, 62, 'Psalms 62'], [541, 19, 63, 'Psalms 63'], [542, 19, 64, 'Psalms 64'], [543, 19, 65, 'Psalms 65'], [544, 19, 66, 'Psalms 66'], [545, 19, 67, 'Psalms 67'], [546, 19, 68, 'Psalms 68'], [547, 19, 69, 'Psalms 69'], [548, 19, 70, 'Psalms 70'], [549, 19, 71, 'Psalms 71'], [550, 19, 72, 'Psalms 72'], [551, 19, 73, 'Psalms 73'], [552, 19, 74, 'Psalms 74'], [553, 19, 75, 'Psalms 75'], [554, 19, 76, 'Psalms 76'], [555, 19, 77, 'Psalms 77'], [556, 19, 78, 'Psalms 78'], [557, 19, 79, 'Psalms 79'], [558, 19, 80, 'Psalms 80'], [559, 19, 81, 'Psalms 81'], [560, 19, 82, 'Psalms 82'], [561, 19, 83, 'Psalms 83'], [562, 19, 84, 'Psalms 84'], [563, 19, 85, 'Psalms 85'], [564, 19, 86, 'Psalms 86'], [565, 19, 87, 'Psalms 87'], [566, 19, 88, 'Psalms 88'], [567, 19, 89, 'Psalms 89'], [568, 19, 90, 'Psalms 90'], [569, 19, 91, 'Psalms 91'], [570, 19, 92, 'Psalms 92'], [571, 19, 93, 'Psalms 93'], [572, 19, 94, 'Psalms 94'], [573, 19, 95, 'Psalms 95'], [574, 19, 96, 'Psalms 96'], [575, 19, 97, 'Psalms 97'], [576, 19, 98, 'Psalms 98'], [577, 19, 99, 'Psalms 99'], [578, 19, 100, 'Psalms 100'], [579, 19, 101, 'Psalms 101'], [580, 19, 102, 'Psalms 102'], [581, 19, 103, 'Psalms 103'], [582, 19, 104, 'Psalms 104'], [583, 19, 105, 'Psalms 105'], [584, 19, 106, 'Psalms 106'], [585, 19, 107, 'Psalms 107'], [586, 19, 108, 'Psalms 108'], [587, 19, 109, 'Psalms 109'], [588, 19, 110, 'Psalms 110'], [589, 19, 111, 'Psalms 111'], [590, 19, 112, 'Psalms 112'], [591, 19, 113, 'Psalms 113'], [592, 19, 114, 'Psalms 114'], [593, 19, 115, 'Psalms 115'], [594, 19, 116, 'Psalms 116'], [595, 19, 117, 'Psalms 117'], [596, 19, 118, 'Psalms 118'], [597, 19, 119, 'Psalms 119'], [598, 19, 120, 'Psalms 120'], [599, 19, 121, 'Psalms 121'], [600, 19, 122, 'Psalms 122'], [601, 19, 123, 'Psalms 123'], [602, 19, 124, 'Psalms 124'], [603, 19, 125, 'Psalms 125'], [604, 19, 126, 'Psalms 126'], [605, 19, 127, 'Psalms 127'], [606, 19, 128, 'Psalms 128'], [607, 19, 129, 'Psalms 129'], [608, 19, 130, 'Psalms 130'], [609, 19, 131, 'Psalms 131'], [610, 19, 132, 'Psalms 132'], [611, 19, 133, 'Psalms 133'], [612, 19, 134, 'Psalms 134'], [613, 19, 135, 'Psalms 135'], [614, 19, 136, 'Psalms 136'], [615, 19, 137, 'Psalms 137'], [616, 19, 138, 'Psalms 138'], [617, 19, 139, 'Psalms 139'], [618, 19, 140, 'Psalms 140'], [619, 19, 141, 'Psalms 141'], [620, 19, 142, 'Psalms 142'], [621, 19, 143, 'Psalms 143'], [622, 19, 144, 'Psalms 144'], [623, 19, 145, 'Psalms 145'], [624, 19, 146, 'Psalms 146'], [625, 19, 147, 'Psalms 147'], [626, 19, 148, 'Psalms 148'], [627, 19, 149, 'Psalms 149'], [628, 19, 150, 'Psalms 150'], [629, 20, 1, 'Proverbs 1'], [630, 20, 2, 'Proverbs 2'], [631, 20, 3, 'Proverbs 3'], [632, 20, 4, 'Proverbs 4'], [633, 20, 5, 'Proverbs 5'], [634, 20, 6, 'Proverbs 6'], [635, 20, 7, 'Proverbs 7'], [636, 20, 8, 'Proverbs 8'], [637, 20, 9, 'Proverbs 9'], [638, 20, 10, 'Proverbs 10'], [639, 20, 11, 'Proverbs 11'], [640, 20, 12, 'Proverbs 12'], [641, 20, 13, 'Proverbs 13'], [642, 20, 14, 'Proverbs 14'], [643, 20, 15, 'Proverbs 15'], [644, 20, 16, 'Proverbs 16'], [645, 20, 17, 'Proverbs 17'], [646, 20, 18, 'Proverbs 18'], [647, 20, 19, 'Proverbs 19'], [648, 20, 20, 'Proverbs 20'], [649, 20, 21, 'Proverbs 21'], [650, 20, 22, 'Proverbs 22'], [651, 20, 23, 'Proverbs 23'], [652, 20, 24, 'Proverbs 24'], [653, 20, 25, 'Proverbs 25'], [654, 20, 26, 'Proverbs 26'], [655, 20, 27, 'Proverbs 27'], [656, 20, 28, 'Proverbs 28'], [657, 20, 29, 'Proverbs 29'], [658, 20, 30, 'Proverbs 30'], [659, 20, 31, 'Proverbs 31'], [660, 21, 1, 'Ecclesiastes 1'], [661, 21, 2, 'Ecclesiastes 2'], [662, 21, 3, 'Ecclesiastes 3'], [663, 21, 4, 'Ecclesiastes 4'], [664, 21, 5, 'Ecclesiastes 5'], [665, 21, 6, 'Ecclesiastes 6'], [666, 21, 7, 'Ecclesiastes 7'], [667, 21, 8, 'Ecclesiastes 8'], [668, 21, 9, 'Ecclesiastes 9'], [669, 21, 10, 'Ecclesiastes 10'], [670, 21, 11, 'Ecclesiastes 11'], [671, 21, 12, 'Ecclesiastes 12'], [672, 22, 1, 'Song of Solomon 1'], [673, 22, 2, 'Song of Solomon 2'], [674, 22, 3, 'Song of Solomon 3'], [675, 22, 4, 'Song of Solomon 4'], [676, 22, 5, 'Song of Solomon 5'], [677, 22, 6, 'Song of Solomon 6'], [678, 22, 7, 'Song of Solomon 7'], [679, 22, 8, 'Song of Solomon 8'], [680, 23, 1, 'Isaiah 1'], [681, 23, 2, 'Isaiah 2'], [682, 23, 3, 'Isaiah 3'], [683, 23, 4, 'Isaiah 4'], [684, 23, 5, 'Isaiah 5'], [685, 23, 6, 'Isaiah 6'], [686, 23, 7, 'Isaiah 7'], [687, 23, 8, 'Isaiah 8'], [688, 23, 9, 'Isaiah 9'], [689, 23, 10, 'Isaiah 10'], [690, 23, 11, 'Isaiah 11'], [691, 23, 12, 'Isaiah 12'], [692, 23, 13, 'Isaiah 13'], [693, 23, 14, 'Isaiah 14'], [694, 23, 15, 'Isaiah 15'], [695, 23, 16, 'Isaiah 16'], [696, 23, 17, 'Isaiah 17'], [697, 23, 18, 'Isaiah 18'], [698, 23, 19, 'Isaiah 19'], [699, 23, 20, 'Isaiah 20'], [700, 23, 21, 'Isaiah 21'], [701, 23, 22, 'Isaiah 22'], [702, 23, 23, 'Isaiah 23'], [703, 23, 24, 'Isaiah 24'], [704, 23, 25, 'Isaiah 25'], [705, 23, 26, 'Isaiah 26'], [706, 23, 27, 'Isaiah 27'], [707, 23, 28, 'Isaiah 28'], [708, 23, 29, 'Isaiah 29'], [709, 23, 30, 'Isaiah 30'], [710, 23, 31, 'Isaiah 31'], [711, 23, 32, 'Isaiah 32'], [712, 23, 33, 'Isaiah 33'], [713, 23, 34, 'Isaiah 34'], [714, 23, 35, 'Isaiah 35'], [715, 23, 36, 'Isaiah 36'], [716, 23, 37, 'Isaiah 37'], [717, 23, 38, 'Isaiah 38'], [718, 23, 39, 'Isaiah 39'], [719, 23, 40, 'Isaiah 40'], [720, 23, 41, 'Isaiah 41'], [721, 23, 42, 'Isaiah 42'], [722, 23, 43, 'Isaiah 43'], [723, 23, 44, 'Isaiah 44'], [724, 23, 45, 'Isaiah 45'], [725, 23, 46, 'Isaiah 46'], [726, 23, 47, 'Isaiah 47'], [727, 23, 48, 'Isaiah 48'], [728, 23, 49, 'Isaiah 49'], [729, 23, 50, 'Isaiah 50'], [730, 23, 51, 'Isaiah 51'], [731, 23, 52, 'Isaiah 52'], [732, 23, 53, 'Isaiah 53'], [733, 23, 54, 'Isaiah 54'], [734, 23, 55, 'Isaiah 55'], [735, 23, 56, 'Isaiah 56'], [736, 23, 57, 'Isaiah 57'], [737, 23, 58, 'Isaiah 58'], [738, 23, 59, 'Isaiah 59'], [739, 23, 60, 'Isaiah 60'], [740, 23, 61, 'Isaiah 61'], [741, 23, 62, 'Isaiah 62'], [742, 23, 63, 'Isaiah 63'], [743, 23, 64, 'Isaiah 64'], [744, 23, 65, 'Isaiah 65'], [745, 23, 66, 'Isaiah 66'], [746, 24, 1, 'Jeremiah 1'], [747, 24, 2, 'Jeremiah 2'], [748, 24, 3, 'Jeremiah 3'], [749, 24, 4, 'Jeremiah 4'], [750, 24, 5, 'Jeremiah 5'], [751, 24, 6, 'Jeremiah 6'], [752, 24, 7, 'Jeremiah 7'], [753, 24, 8, 'Jeremiah 8'], [754, 24, 9, 'Jeremiah 9'], [755, 24, 10, 'Jeremiah 10'], [756, 24, 11, 'Jeremiah 11'], [757, 24, 12, 'Jeremiah 12'], [758, 24, 13, 'Jeremiah 13'], [759, 24, 14, 'Jeremiah 14'], [760, 24, 15, 'Jeremiah 15'], [761, 24, 16, 'Jeremiah 16'], [762, 24, 17, 'Jeremiah 17'], [763, 24, 18, 'Jeremiah 18'], [764, 24, 19, 'Jeremiah 19'], [765, 24, 20, 'Jeremiah 20'], [766, 24, 21, 'Jeremiah 21'], [767, 24, 22, 'Jeremiah 22'], [768, 24, 23, 'Jeremiah 23'], [769, 24, 24, 'Jeremiah 24'], [770, 24, 25, 'Jeremiah 25'], [771, 24, 26, 'Jeremiah 26'], [772, 24, 27, 'Jeremiah 27'], [773, 24, 28, 'Jeremiah 28'], [774, 24, 29, 'Jeremiah 29'], [775, 24, 30, 'Jeremiah 30'], [776, 24, 31, 'Jeremiah 31'], [777, 24, 32, 'Jeremiah 32'], [778, 24, 33, 'Jeremiah 33'], [779, 24, 34, 'Jeremiah 34'], [780, 24, 35, 'Jeremiah 35'], [781, 24, 36, 'Jeremiah 36'], [782, 24, 37, 'Jeremiah 37'], [783, 24, 38, 'Jeremiah 38'], [784, 24, 39, 'Jeremiah 39'], [785, 24, 40, 'Jeremiah 40'], [786, 24, 41, 'Jeremiah 41'], [787, 24, 42, 'Jeremiah 42'], [788, 24, 43, 'Jeremiah 43'], [789, 24, 44, 'Jeremiah 44'], [790, 24, 45, 'Jeremiah 45'], [791, 24, 46, 'Jeremiah 46'], [792, 24, 47, 'Jeremiah 47'], [793, 24, 48, 'Jeremiah 48'], [794, 24, 49, 'Jeremiah 49'], [795, 24, 50, 'Jeremiah 50'], [796, 24, 51, 'Jeremiah 51'], [797, 24, 52, 'Jeremiah 52'], [798, 25, 1, 'Lamentations 1'], [799, 25, 2, 'Lamentations 2'], [800, 25, 3, 'Lamentations 3'], [801, 25, 4, 'Lamentations 4'], [802, 25, 5, 'Lamentations 5'], [803, 26, 1, 'Ezekiel 1'], [804, 26, 2, 'Ezekiel 2'], [805, 26, 3, 'Ezekiel 3'], [806, 26, 4, 'Ezekiel 4'], [807, 26, 5, 'Ezekiel 5'], [808, 26, 6, 'Ezekiel 6'], [809, 26, 7, 'Ezekiel 7'], [810, 26, 8, 'Ezekiel 8'], [811, 26, 9, 'Ezekiel 9'], [812, 26, 10, 'Ezekiel 10'], [813, 26, 11, 'Ezekiel 11'], [814, 26, 12, 'Ezekiel 12'], [815, 26, 13, 'Ezekiel 13'], [816, 26, 14, 'Ezekiel 14'], [817, 26, 15, 'Ezekiel 15'], [818, 26, 16, 'Ezekiel 16'], [819, 26, 17, 'Ezekiel 17'], [820, 26, 18, 'Ezekiel 18'], [821, 26, 19, 'Ezekiel 19'], [822, 26, 20, 'Ezekiel 20'], [823, 26, 21, 'Ezekiel 21'], [824, 26, 22, 'Ezekiel 22'], [825, 26, 23, 'Ezekiel 23'], [826, 26, 24, 'Ezekiel 24'], [827, 26, 25, 'Ezekiel 25'], [828, 26, 26, 'Ezekiel 26'], [829, 26, 27, 'Ezekiel 27'], [830, 26, 28, 'Ezekiel 28'], [831, 26, 29, 'Ezekiel 29'], [832, 26, 30, 'Ezekiel 30'], [833, 26, 31, 'Ezekiel 31'], [834, 26, 32, 'Ezekiel 32'], [835, 26, 33, 'Ezekiel 33'], [836, 26, 34, 'Ezekiel 34'], [837, 26, 35, 'Ezekiel 35'], [838, 26, 36, 'Ezekiel 36'], [839, 26, 37, 'Ezekiel 37'], [840, 26, 38, 'Ezekiel 38'], [841, 26, 39, 'Ezekiel 39'], [842, 26, 40, 'Ezekiel 40'], [843, 26, 41, 'Ezekiel 41'], [844, 26, 42, 'Ezekiel 42'], [845, 26, 43, 'Ezekiel 43'], [846, 26, 44, 'Ezekiel 44'], [847, 26, 45, 'Ezekiel 45'], [848, 26, 46, 'Ezekiel 46'], [849, 26, 47, 'Ezekiel 47'], [850, 26, 48, 'Ezekiel 48'], [851, 27, 1, 'Daniel 1'], [852, 27, 2, 'Daniel 2'], [853, 27, 3, 'Daniel 3'], [854, 27, 4, 'Daniel 4'], [855, 27, 5, 'Daniel 5'], [856, 27, 6, 'Daniel 6'], [857, 27, 7, 'Daniel 7'], [858, 27, 8, 'Daniel 8'], [859, 27, 9, 'Daniel 9'], [860, 27, 10, 'Daniel 10'], [861, 27, 11, 'Daniel 11'], [862, 27, 12, 'Daniel 12'], [863, 28, 1, 'Hosea 1'], [864, 28, 2, 'Hosea 2'], [865, 28, 3, 'Hosea 3'], [866, 28, 4, 'Hosea 4'], [867, 28, 5, 'Hosea 5'], [868, 28, 6, 'Hosea 6'], [869, 28, 7, 'Hosea 7'], [870, 28, 8, 'Hosea 8'], [871, 28, 9, 'Hosea 9'], [872, 28, 10, 'Hosea 10'], [873, 28, 11, 'Hosea 11'], [874, 28, 12, 'Hosea 12'], [875, 28, 13, 'Hosea 13'], [876, 28, 14, 'Hosea 14'], [877, 29, 1, 'Joel 1'], [878, 29, 2, 'Joel 2'], [879, 29, 3, 'Joel 3'], [880, 30, 1, 'Amos 1'], [881, 30, 2, 'Amos 2'], [882, 30, 3, 'Amos 3'], [883, 30, 4, 'Amos 4'], [884, 30, 5, 'Amos 5'], [885, 30, 6, 'Amos 6'], [886, 30, 7, 'Amos 7'], [887, 30, 8, 'Amos 8'], [888, 30, 9, 'Amos 9'], [889, 31, 1, 'Obadiah 1'], [890, 32, 1, 'Jonah 1'], [891, 32, 2, 'Jonah 2'], [892, 32, 3, 'Jonah 3'], [893, 32, 4, 'Jonah 4'], [894, 33, 1, 'Micah 1'], [895, 33, 2, 'Micah 2'], [896, 33, 3, 'Micah 3'], [897, 33, 4, 'Micah 4'], [898, 33, 5, 'Micah 5'], [899, 33, 6, 'Micah 6'], [900, 33, 7, 'Micah 7'], [901, 34, 1, 'Nahum 1'], [902, 34, 2, 'Nahum 2'], [903, 34, 3, 'Nahum 3'], [904, 35, 1, 'Habakkuk 1'], [905, 35, 2, 'Habakkuk 2'], [906, 35, 3, 'Habakkuk 3'], [907, 36, 1, 'Zephaniah 1'], [908, 36, 2, 'Zephaniah 2'], [909, 36, 3, 'Zephaniah 3'], [910, 37, 1, 'Haggai 1'], [911, 37, 2, 'Haggai 2'], [912, 38, 1, 'Zechariah 1'], [913, 38, 2, 'Zechariah 2'], [914, 38, 3, 'Zechariah 3'], [915, 38, 4, 'Zechariah 4'], [916, 38, 5, 'Zechariah 5'], [917, 38, 6, 'Zechariah 6'], [918, 38, 7, 'Zechariah 7'], [919, 38, 8, 'Zechariah 8'], [920, 38, 9, 'Zechariah 9'], [921, 38, 10, 'Zechariah 10'], [922, 38, 11, 'Zechariah 11'], [923, 38, 12, 'Zechariah 12'], [924, 38, 13, 'Zechariah 13'], [925, 38, 14, 'Zechariah 14'], [926, 39, 1, 'Malachi 1'], [927, 39, 2, 'Malachi 2'], [928, 39, 3, 'Malachi 3'], [929, 39, 4, 'Malachi 4'], [930, 40, 1, 'Matthew 1'], [931, 40, 2, 'Matthew 2'], [932, 40, 3, 'Matthew 3'], [933, 40, 4, 'Matthew 4'], [934, 40, 5, 'Matthew 5'], [935, 40, 6, 'Matthew 6'], [936, 40, 7, 'Matthew 7'], [937, 40, 8, 'Matthew 8'], [938, 40, 9, 'Matthew 9'], [939, 40, 10, 'Matthew 10'], [940, 40, 11, 'Matthew 11'], [941, 40, 12, 'Matthew 12'], [942, 40, 13, 'Matthew 13'], [943, 40, 14, 'Matthew 14'], [944, 40, 15, 'Matthew 15'], [945, 40, 16, 'Matthew 16'], [946, 40, 17, 'Matthew 17'], [947, 40, 18, 'Matthew 18'], [948, 40, 19, 'Matthew 19'], [949, 40, 20, 'Matthew 20'], [950, 40, 21, 'Matthew 21'], [951, 40, 22, 'Matthew 22'], [952, 40, 23, 'Matthew 23'], [953, 40, 24, 'Matthew 24'], [954, 40, 25, 'Matthew 25'], [955, 40, 26, 'Matthew 26'], [956, 40, 27, 'Matthew 27'], [957, 40, 28, 'Matthew 28'], [958, 41, 1, 'Mark 1'], [959, 41, 2, 'Mark 2'], [960, 41, 3, 'Mark 3'], [961, 41, 4, 'Mark 4'], [962, 41, 5, 'Mark 5'], [963, 41, 6, 'Mark 6'], [964, 41, 7, 'Mark 7'], [965, 41, 8, 'Mark 8'], [966, 41, 9, 'Mark 9'], [967, 41, 10, 'Mark 10'], [968, 41, 11, 'Mark 11'], [969, 41, 12, 'Mark 12'], [970, 41, 13, 'Mark 13'], [971, 41, 14, 'Mark 14'], [972, 41, 15, 'Mark 15'], [973, 41, 16, 'Mark 16'], [974, 42, 1, 'Luke 1'], [975, 42, 2, 'Luke 2'], [976, 42, 3, 'Luke 3'], [977, 42, 4, 'Luke 4'], [978, 42, 5, 'Luke 5'], [979, 42, 6, 'Luke 6'], [980, 42, 7, 'Luke 7'], [981, 42, 8, 'Luke 8'], [982, 42, 9, 'Luke 9'], [983, 42, 10, 'Luke 10'], [984, 42, 11, 'Luke 11'], [985, 42, 12, 'Luke 12'], [986, 42, 13, 'Luke 13'], [987, 42, 14, 'Luke 14'], [988, 42, 15, 'Luke 15'], [989, 42, 16, 'Luke 16'], [990, 42, 17, 'Luke 17'], [991, 42, 18, 'Luke 18'], [992, 42, 19, 'Luke 19'], [993, 42, 20, 'Luke 20'], [994, 42, 21, 'Luke 21'], [995, 42, 22, 'Luke 22'], [996, 42, 23, 'Luke 23'], [997, 42, 24, 'Luke 24'], [998, 43, 1, 'John 1'], [999, 43, 2, 'John 2'], [1000, 43, 3, 'John 3'], [1001, 43, 4, 'John 4'], [1002, 43, 5, 'John 5'], [1003, 43, 6, 'John 6'], [1004, 43, 7, 'John 7'], [1005, 43, 8, 'John 8'], [1006, 43, 9, 'John 9'], [1007, 43, 10, 'John 10'], [1008, 43, 11, 'John 11'], [1009, 43, 12, 'John 12'], [1010, 43, 13, 'John 13'], [1011, 43, 14, 'John 14'], [1012, 43, 15, 'John 15'], [1013, 43, 16, 'John 16'], [1014, 43, 17, 'John 17'], [1015, 43, 18, 'John 18'], [1016, 43, 19, 'John 19'], [1017, 43, 20, 'John 20'], [1018, 43, 21, 'John 21'], [1019, 44, 1, 'Acts 1'], [1020, 44, 2, 'Acts 2'], [1021, 44, 3, 'Acts 3'], [1022, 44, 4, 'Acts 4'], [1023, 44, 5, 'Acts 5'], [1024, 44, 6, 'Acts 6'], [1025, 44, 7, 'Acts 7'], [1026, 44, 8, 'Acts 8'], [1027, 44, 9, 'Acts 9'], [1028, 44, 10, 'Acts 10'], [1029, 44, 11, 'Acts 11'], [1030, 44, 12, 'Acts 12'], [1031, 44, 13, 'Acts 13'], [1032, 44, 14, 'Acts 14'], [1033, 44, 15, 'Acts 15'], [1034, 44, 16, 'Acts 16'], [1035, 44, 17, 'Acts 17'], [1036, 44, 18, 'Acts 18'], [1037, 44, 19, 'Acts 19'], [1038, 44, 20, 'Acts 20'], [1039, 44, 21, 'Acts 21'], [1040, 44, 22, 'Acts 22'], [1041, 44, 23, 'Acts 23'], [1042, 44, 24, 'Acts 24'], [1043, 44, 25, 'Acts 25'], [1044, 44, 26, 'Acts 26'], [1045, 44, 27, 'Acts 27'], [1046, 44, 28, 'Acts 28'], [1047, 45, 1, 'Romans 1'], [1048, 45, 2, 'Romans 2'], [1049, 45, 3, 'Romans 3'], [1050, 45, 4, 'Romans 4'], [1051, 45, 5, 'Romans 5'], [1052, 45, 6, 'Romans 6'], [1053, 45, 7, 'Romans 7'], [1054, 45, 8, 'Romans 8'], [1055, 45, 9, 'Romans 9'], [1056, 45, 10, 'Romans 10'], [1057, 45, 11, 'Romans 11'], [1058, 45, 12, 'Romans 12'], [1059, 45, 13, 'Romans 13'], [1060, 45, 14, 'Romans 14'], [1061, 45, 15, 'Romans 15'], [1062, 45, 16, 'Romans 16'], [1063, 46, 1, '1 Corinthians 1'], [1064, 46, 2, '1 Corinthians 2'], [1065, 46, 3, '1 Corinthians 3'], [1066, 46, 4, '1 Corinthians 4'], [1067, 46, 5, '1 Corinthians 5'], [1068, 46, 6, '1 Corinthians 6'], [1069, 46, 7, '1 Corinthians 7'], [1070, 46, 8, '1 Corinthians 8'], [1071, 46, 9, '1 Corinthians 9'], [1072, 46, 10, '1 Corinthians 10'], [1073, 46, 11, '1 Corinthians 11'], [1074, 46, 12, '1 Corinthians 12'], [1075, 46, 13, '1 Corinthians 13'], [1076, 46, 14, '1 Corinthians 14'], [1077, 46, 15, '1 Corinthians 15'], [1078, 46, 16, '1 Corinthians 16'], [1079, 47, 1, '2 Corinthians 1'], [1080, 47, 2, '2 Corinthians 2'], [1081, 47, 3, '2 Corinthians 3'], [1082, 47, 4, '2 Corinthians 4'], [1083, 47, 5, '2 Corinthians 5'], [1084, 47, 6, '2 Corinthians 6'], [1085, 47, 7, '2 Corinthians 7'], [1086, 47, 8, '2 Corinthians 8'], [1087, 47, 9, '2 Corinthians 9'], [1088, 47, 10, '2 Corinthians 10'], [1089, 47, 11, '2 Corinthians 11'], [1090, 47, 12, '2 Corinthians 12'], [1091, 47, 13, '2 Corinthians 13'], [1092, 48, 1, 'Galatians 1'], [1093, 48, 2, 'Galatians 2'], [1094, 48, 3, 'Galatians 3'], [1095, 48, 4, 'Galatians 4'], [1096, 48, 5, 'Galatians 5'], [1097, 48, 6, 'Galatians 6'], [1098, 49, 1, 'Ephesians 1'], [1099, 49, 2, 'Ephesians 2'], [1100, 49, 3, 'Ephesians 3'], [1101, 49, 4, 'Ephesians 4'], [1102, 49, 5, 'Ephesians 5'], [1103, 49, 6, 'Ephesians 6'], [1104, 50, 1, 'Philippians 1'], [1105, 50, 2, 'Philippians 2'], [1106, 50, 3, 'Philippians 3'], [1107, 50, 4, 'Philippians 4'], [1108, 51, 1, 'Colossians 1'], [1109, 51, 2, 'Colossians 2'], [1110, 51, 3, 'Colossians 3'], [1111, 51, 4, 'Colossians 4'], [1112, 52, 1, '1 Thessalonians 1'], [1113, 52, 2, '1 Thessalonians 2'], [1114, 52, 3, '1 Thessalonians 3'], [1115, 52, 4, '1 Thessalonians 4'], [1116, 52, 5, '1 Thessalonians 5'], [1117, 53, 1, '2 Thessalonians 1'], [1118, 53, 2, '2 Thessalonians 2'], [1119, 53, 3, '2 Thessalonians 3'], [1120, 54, 1, '1 Timothy 1'], [1121, 54, 2, '1 Timothy 2'], [1122, 54, 3, '1 Timothy 3'], [1123, 54, 4, '1 Timothy 4'], [1124, 54, 5, '1 Timothy 5'], [1125, 54, 6, '1 Timothy 6'], [1126, 55, 1, '2 Timothy 1'], [1127, 55, 2, '2 Timothy 2'], [1128, 55, 3, '2 Timothy 3'], [1129, 55, 4, '2 Timothy 4'], [1130, 56, 1, 'Titus 1'], [1131, 56, 2, 'Titus 2'], [1132, 56, 3, 'Titus 3'], [1133, 57, 1, 'Philemon 1'], [1134, 58, 1, 'Hebrews 1'], [1135, 58, 2, 'Hebrews 2'], [1136, 58, 3, 'Hebrews 3'], [1137, 58, 4, 'Hebrews 4'], [1138, 58, 5, 'Hebrews 5'], [1139, 58, 6, 'Hebrews 6'], [1140, 58, 7, 'Hebrews 7'], [1141, 58, 8, 'Hebrews 8'], [1142, 58, 9, 'Hebrews 9'], [1143, 58, 10, 'Hebrews 10'], [1144, 58, 11, 'Hebrews 11'], [1145, 58, 12, 'Hebrews 12'], [1146, 58, 13, 'Hebrews 13'], [1147, 59, 1, 'James 1'], [1148, 59, 2, 'James 2'], [1149, 59, 3, 'James 3'], [1150, 59, 4, 'James 4'], [1151, 59, 5, 'James 5'], [1152, 60, 1, '1 Peter 1'], [1153, 60, 2, '1 Peter 2'], [1154, 60, 3, '1 Peter 3'], [1155, 60, 4, '1 Peter 4'], [1156, 60, 5, '1 Peter 5'], [1157, 61, 1, '2 Peter 1'], [1158, 61, 2, '2 Peter 2'], [1159, 61, 3, '2 Peter 3'], [1160, 62, 1, '1 John 1'], [1161, 62, 2, '1 John 2'], [1162, 62, 3, '1 John 3'], [1163, 62, 4, '1 John 4'], [1164, 62, 5, '1 John 5'], [1165, 63, 1, '2 John 1'], [1166, 64, 1, '3 John 1'], [1167, 65, 1, 'Jude 1'], [1168, 66, 1, 'Revelation 1'], [1169, 66, 2, 'Revelation 2'], [1170, 66, 3, 'Revelation 3'], [1171, 66, 4, 'Revelation 4'], [1172, 66, 5, 'Revelation 5'], [1173, 66, 6, 'Revelation 6'], [1174, 66, 7, 'Revelation 7'], [1175, 66, 8, 'Revelation 8'], [1176, 66, 9, 'Revelation 9'], [1177, 66, 10, 'Revelation 10'], [1178, 66, 11, 'Revelation 11'], [1179, 66, 12, 'Revelation 12'], [1180, 66, 13, 'Revelation 13'], [1181, 66, 14, 'Revelation 14'], [1182, 66, 15, 'Revelation 15'], [1183, 66, 16, 'Revelation 16'], [1184, 66, 17, 'Revelation 17'], [1185, 66, 18, 'Revelation 18'], [1186, 66, 19, 'Revelation 19'], [1187, 66, 20, 'Revelation 20'], [1188, 66, 21, 'Revelation 21'], [1189, 66, 22, 'Revelation 22']]

@app.route('/bible')
def bible():
    global result_list
    if 'username' in session:
        login = True
        user = session['username']        
    else:
        login = False
        user=""

    


    return render_template("bible.html", login=login, user=user, rows=result_list)

@app.route('/get_verse', methods=['POST'])
def get_verse():
    global result_list
    data = request.get_json()   
    selected_id = int(data['id']) - 1
    print("data", result_list[selected_id])

    conn = sqlite3.connect('kjv.db')
    cursor = conn.cursor()
    bookNum = result_list[selected_id][1]
    chNum = result_list[selected_id][2]
    # Execute a query to select data from the 'songs' table for the selected ID
    cursor.execute('SELECT * FROM words WHERE bookNum = ? AND chNum = ?', (bookNum,chNum,))
    row = cursor.fetchall()
    conn.close()

    conn1 = sqlite3.connect('tamil.db')
    cursor1 = conn1.cursor()
    bookNum1 = result_list[selected_id][1]
    chNum1 = result_list[selected_id][2]
    # Execute a query to select data from the 'songs' table for the selected ID
    cursor1.execute('SELECT * FROM words WHERE bookNum = ? AND chNum = ?', (bookNum1,chNum1,))
    row1 = cursor1.fetchall()
    conn1.close()

    lyrics=""
    if row:
        for i in range(len(row)):
            print(row[i][1])
            lyrics += f"<p id={row[i][4]} style='border: 1px solid black;padding: 10px;'>"+ "<span style='font-weight:bold;font-size:larger;'>" + result_list[selected_id][3] + ":" + str(row[i][4]) + "</span><br>" +row[i][1]+ f"<br><span style='color:green;'>{row1[i][1]}</span></p>"
            
        print(lyrics)
        return jsonify({'lyrics': lyrics, 'title':result_list[selected_id][3]})
    else:
        return jsonify({'lyrics': [], 'title': []})

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session and session['username'] != "Sam":
        return "Not Authorized"
    


    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT * from users')
    rows = cursor.fetchall()

    conn.close()

    return render_template("admin_dashboard.html", users=rows)

@app.route('/modify_user/<int:user_id>')
def modify_user(user_id):
    if 'username' not in session and session['username'] != "Sam":
        return "Not Authorized"

    # Fetch user data by user_id and perform modification logic here
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # For instance, you might want to update user permissions
    cursor.execute('UPDATE users SET permission = 1 WHERE id = ?', (user_id,))
    conn.commit()

    conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'username' not in session and session['username'] != "Sam":
        return "Not Authorized"
    


    # Logic to delete user
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()

    conn.close()

    return redirect(url_for('admin_dashboard'))


@app.route('/get_lyrics', methods=['POST'])
def get_lyrics():
    data = request.get_json()   
    selected_id = data['id']
    # print("ids", selected_id)

    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Execute a query to select data from the 'songs' table for the selected ID
    cursor.execute('SELECT lyrics, transliteration, chord, title FROM songs WHERE id = ?', (selected_id,))
    
    row = cursor.fetchone()
    # print(row)

    # Close the database connection
    conn.close()

    if row:
        lyrics = song_view(row[0], row[1], row[2])
        # print(lyrics)
        return jsonify({'lyrics': lyrics, 'title':row[3]})
    else:
        return jsonify({'lyrics': [], 'title': []})
    
@app.route('/song/<id>')
def song(id):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Execute a query to select data from the 'songs' table for the selected ID
        cursor.execute('SELECT lyrics, transliteration, chord, title, youtube_link FROM songs WHERE id = ?', (int(id),))
        
        row = cursor.fetchone()
        # print(row)

        # Close the database connection
        conn.close()

        lyrics = song_view(row[0], row[1], row[2])
    except:
        conn.close()
        return "Song Not Available!"

    # print("HI")

    return render_template("song_viewer.html", lyrics=lyrics, song_title=row[3], link = row[4])

@app.route('/control/<user>')
def control(user):
    if 'username' not in session:
        return render_template('login.html', error_message="Kindly Login to access controls Page!", error_color='red')
    login=True

    return render_template("control.html", login=login, user=session['username'])

@app.route('/display/<user>')
def display(user):

    return render_template("display.html")


@socketio.on('join')
def handle_join(user):
    room = user
    join_room(room)
    print(f"User {user} joined room {room}")

@socketio.on('send_data_event')
def send_data(data):
    room = data.get('user')
    emitted_data = data.get('data')
    if room and emitted_data:
        emit('update_data', emitted_data, room=room)
        print(f"Data sent to room {room}: {emitted_data}")

@socketio.on('send_para')
def send_para(data):
    room = data.get('user')
    emitted_data = data.get('data')
    if room and emitted_data:
        emit('update_para', emitted_data, room=room)
        print(f"Data sent to room {room}: {emitted_data}")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = create_connection()
        cursor = conn.cursor()

        # Check if username or email already exists
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            error_message = "Username or email already exists!"
            conn.close()
            return render_template('signup.html', error_message=error_message, error_color='red')

        # Hash the password before storing it
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Insert new user into the database
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, hashed_password))
        conn.commit()
        conn.close()

        session['username'] = username
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check if the username or email exists in the database
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username_or_email, username_or_email))
        user = cursor.fetchone()

        if user:
            stored_password = user[3]  # Assuming the password is stored in the fourth column (index 3)
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            if hashed_password == stored_password:
                # Authentication successful, set session and redirect to a dashboard or profile page
                session['username'] = user[1]  # Assuming the username is stored in the second column (index 1)
                conn.close()
                return redirect(url_for('dashboard'))  # Replace 'dashboard' with your desired route
            else:
                error_message = "Incorrect password"
                conn.close()
                return render_template('login.html', error_message=error_message, error_color='red')
        else:
            error_message = "User not found"
            conn.close()
            return render_template('login.html', error_message=error_message, error_color='red')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        conn = sqlite3.connect(DATABASE)
        user = session['username']
        cursor1 = conn.cursor()
        cursor1.execute('SELECT permission FROM users where username = ?', (user,))
        permission = cursor1.fetchone()
        permission = permission[0]
        conn.close()
        
        if session['username'] == "Sam":
            return redirect('/admin_dashboard')
        return render_template("dashboard.html", user_name= session['username'], permission=permission)
    return render_template('login.html', error_message="Kindly Login to access your dashboard!", error_color='red')

@app.route('/logout')
def logout():
    # Clear the user's session data
    session.pop('username', None)  # Replace 'username' with your session variable name

    # Redirect to the home page or login page after logout
    return redirect(url_for('home'))


@app.route('/add_songs', methods=['GET', 'POST'])
def add_songs():
    if 'username' not in session:
        return render_template('login.html', error_message="Kindly Login to add Songs!", error_color='red')
    
    if request.method == 'POST':
        transliteration_lyrics = request.form.get('transliterationLyrics')
        chord = request.form.get('chord')
        title = request.form['title']
        alternate_title = request.form.get('alternateTitle')
        lyrics = request.form['lyrics']
        youtube_link = request.form['youtube_link']
        search_title = remove_special_characters(title) + " " + remove_special_characters(alternate_title)
        search_lyrics = lyrics.replace('\r\n', ' ') + " " + transliteration_lyrics.replace('\n', ' ')
        search_lyrics = remove_special_characters(search_lyrics)
        
        conn = create_connection()
        cursor = conn.cursor()

        # Get the current date and time
        current_date = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Insert song data into the songs table
        cursor.execute('''
            INSERT INTO songs (title, alternate_title, lyrics, transliteration, youtube_link, chord, search_title, search_lyrics, create_date, modified_date, username)
            VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, alternate_title, lyrics, transliteration_lyrics,
            youtube_link, chord, search_title, search_lyrics, current_date, current_date, session['username']))

        conn.commit()
        conn.close()


        return redirect('/dashboard')
    
    return render_template('add_song.html')


@app.route('/delete_song/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    if 'username' not in session:
        return jsonify({'message': 'Not authorized'}), 401  # Unauthorized status code
    
    conn = create_connection()
    cursor = conn.cursor()

    # Delete the song based on the provided song_id
    cursor.execute('DELETE FROM songs WHERE id = ?', (song_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Song deleted successfully'}), 200  # OK status code


@app.route('/edit_songs/<int:id>', methods=['GET', 'POST'])
def edit_songs(id):
    if 'username' in session:
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            # Execute a query to select data from the 'songs' table for the selected ID
            cursor.execute('SELECT * FROM songs WHERE id = ?', (id,))
            default_values = cursor.fetchone()

            conn.close()

            if request.method == 'POST':
                transliteration_lyrics = request.form.get('transliterationLyrics')
                chord = request.form.get('chord')
                title = request.form['title']
                alternate_title = request.form.get('alternateTitle')
                lyrics = request.form['lyrics']
                youtube_link = request.form['youtube_link']
                search_title = remove_special_characters(title) + " " + remove_special_characters(alternate_title)
                search_lyrics = lyrics.replace('\r\n', ' ') + " " + transliteration_lyrics.replace('\n', ' ')
                search_lyrics = remove_special_characters(search_lyrics)
                
                conn = create_connection()
                cursor = conn.cursor()

                # Get the current date and time
                current_date = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                cursor.execute('''
                                UPDATE songs 
                                SET title = ?, alternate_title = ?, lyrics = ?, 
                                    transliteration = ?, youtube_link = ?, chord = ?, search_title = ?, 
                                    search_lyrics = ?, modified_date = ?, username = ?
                                WHERE id = ?
                            ''', (title, alternate_title, lyrics, transliteration_lyrics,
                                youtube_link, chord, search_title, search_lyrics, current_date,
                                session['username'], id))
                
                print(title, alternate_title, lyrics, transliteration_lyrics,
                                youtube_link, chord, search_title, search_lyrics, current_date,
                                session['username'], id)

                conn.commit()
                conn.close()


                return redirect('/dashboard')
        except:
            conn.close()
            return "Selected Song Does not Exist."
        
        id=default_values[0]
        title=default_values[1]
        alternate_title=default_values[2]
        lyrics=default_values[3]
        transliteration_lyrics=default_values[4]
        chord=default_values[5]
        link = default_values[8]

        
        return render_template("edit_song.html", id=id, title=title, alternate_title=alternate_title, link=link, chord=chord, lyrics=lyrics, transliteration_lyrics=transliteration_lyrics)
    
    return render_template('login.html', error_message="Kindly Login to edit Songs!", error_color='red')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
