# import xml.etree.ElementTree as ET
# import sqlite3

# # Process the XML data
# def process_xml(xml_data):
#     root = ET.fromstring(xml_data)
#     lyrics = []
#     for verse in root.findall('.//verse'):
#         verse_type = verse.get('type')
#         verse_text = verse.text.strip()
#         lyrics.append((verse_type, verse_text))
#     return lyrics

# DATABASE = 'oilnwine.db'

# def create_connection():
#     conn = sqlite3.connect(DATABASE)
#     return conn

# def create_users_table():
#     conn = create_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE,
#             email TEXT UNIQUE,
#             password TEXT,
#             otp INTEGER DEFAULT 0,
#             verified INTEGER DEFAULT 0,
#             permission INTEGER DEFAULT 0
#         )
#     ''')
#     conn.commit()
#     conn.close()

# def create_songs_table():
#     conn = create_connection()
#     cursor = conn.cursor()

#     # Create the songs table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS songs (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             title TEXT,
#             alternate_title TEXT,
#             lyrics TEXT,
#             transliteration TEXT,
#             chord TEXT,
#             search_title TEXT,
#             search_lyrics TEXT,
#             youtube_link TEXT,
#             create_date TEXT,
#             modified_date TEXT,
#             username TEXT,
#             FOREIGN KEY (username) REFERENCES users(username)
#         )
#     ''')
#     conn.commit()
#     conn.close()

# def add_song(title, alternate_title, lyrics, search_title, search_lyrics, create_date, modified_date):
#     conn = create_connection()
#     cursor = conn.cursor()
#     # Insert song data into the songs table
#     cursor.execute('''
#         INSERT INTO songs (title, alternate_title, lyrics, search_title, search_lyrics, create_date, modified_date, username)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#     ''', ( title, alternate_title, lyrics,
#          search_title, search_lyrics, create_date, modified_date, "OpenLP"))

#     conn.commit()
#     conn.close()

# create_users_table()
# create_songs_table()


# for i in range(1,1773):
#     # Connect to the SQLite database
#     db_file = 'songs.sqlite'  # Replace with the path to your SQLite database file
#     conn = sqlite3.connect(db_file)
#     cursor = conn.cursor()

#     # Execute a query to select data from the 'songs' table for the selected ID
#     cursor.execute('SELECT * FROM songs WHERE id = ?', (i,))

#     row = cursor.fetchone()
#     if row!=None and i!=1574:
#         processed=""
#         lyrics = process_xml(row[3])
#         for j in range(len(lyrics)):
#             if j!=len(lyrics)-1:
#                 processed += lyrics[j][1]+"\n\n"
#             else:
#                 processed += lyrics[j][1]
#         print(processed)

#         add_song(row[1],row[2],processed,row[9],row[10],row[11],row[12])

#     # print(row[1],row[2],processed,row[9],row[10],row[11],row[12])

#     # Close the database connection
#     conn.close()

# bible_books = {
#     1: {"name": "Genesis", "chapters": 50},
#     2: {"name": "Exodus", "chapters": 40},
#     3: {"name": "Leviticus", "chapters": 27},
#     4: {"name": "Numbers", "chapters": 36},
#     5: {"name": "Deuteronomy", "chapters": 34},
#     6: {"name": "Joshua", "chapters": 24},
#     7: {"name": "Judges", "chapters": 21},
#     8: {"name": "Ruth", "chapters": 4},
#     9: {"name": "1 Samuel", "chapters": 31},
#     10: {"name": "2 Samuel", "chapters": 24},
#     11: {"name": "1 Kings", "chapters": 22},
#     12: {"name": "2 Kings", "chapters": 25},
#     13: {"name": "1 Chronicles", "chapters": 29},
#     14: {"name": "2 Chronicles", "chapters": 36},
#     15: {"name": "Ezra", "chapters": 10},
#     16: {"name": "Nehemiah", "chapters": 13},
#     17: {"name": "Esther", "chapters": 10},
#     18: {"name": "Job", "chapters": 42},
#     19: {"name": "Psalms", "chapters": 150},
#     20: {"name": "Proverbs", "chapters": 31},
#     21: {"name": "Ecclesiastes", "chapters": 12},
#     22: {"name": "Song of Solomon", "chapters": 8},
#     23: {"name": "Isaiah", "chapters": 66},
#     24: {"name": "Jeremiah", "chapters": 52},
#     25: {"name": "Lamentations", "chapters": 5},
#     26: {"name": "Ezekiel", "chapters": 48},
#     27: {"name": "Daniel", "chapters": 12},
#     28: {"name": "Hosea", "chapters": 14},
#     29: {"name": "Joel", "chapters": 3},
#     30: {"name": "Amos", "chapters": 9},
#     31: {"name": "Obadiah", "chapters": 1},
#     32: {"name": "Jonah", "chapters": 4},
#     33: {"name": "Micah", "chapters": 7},
#     34: {"name": "Nahum", "chapters": 3},
#     35: {"name": "Habakkuk", "chapters": 3},
#     36: {"name": "Zephaniah", "chapters": 3},
#     37: {"name": "Haggai", "chapters": 2},
#     38: {"name": "Zechariah", "chapters": 14},
#     39: {"name": "Malachi", "chapters": 4},
#     40: {"name": "Matthew", "chapters": 28},
#     41: {"name": "Mark", "chapters": 16},
#     42: {"name": "Luke", "chapters": 24},
#     43: {"name": "John", "chapters": 21},
#     44: {"name": "Acts", "chapters": 28},
#     45: {"name": "Romans", "chapters": 16},
#     46: {"name": "1 Corinthians", "chapters": 16},
#     47: {"name": "2 Corinthians", "chapters": 13},
#     48: {"name": "Galatians", "chapters": 6},
#     49: {"name": "Ephesians", "chapters": 6},
#     50: {"name": "Philippians", "chapters": 4},
#     51: {"name": "Colossians", "chapters": 4},
#     52: {"name": "1 Thessalonians", "chapters": 5},
#     53: {"name": "2 Thessalonians", "chapters": 3},
#     54: {"name": "1 Timothy", "chapters": 6},
#     55: {"name": "2 Timothy", "chapters": 4},
#     56: {"name": "Titus", "chapters": 3},
#     57: {"name": "Philemon", "chapters": 1},
#     58: {"name": "Hebrews", "chapters": 13},
#     59: {"name": "James", "chapters": 5},
#     60: {"name": "1 Peter", "chapters": 5},
#     61: {"name": "2 Peter", "chapters": 3},
#     62: {"name": "1 John", "chapters": 5},
#     63: {"name": "2 John", "chapters": 1},
#     64: {"name": "3 John", "chapters": 1},
#     65: {"name": "Jude", "chapters": 1},
#     66: {"name": "Revelation", "chapters": 22}
# }

# result_list = []

# for book_id, book_info in bible_books.items():
#     book_name = book_info["name"]
#     chapters = book_info["chapters"]

#     for chapter in range(1, chapters + 1):
#         book_chapter_name = f"{book_name} {chapter}"
#         result_list.append([len(result_list) + 1, book_id, chapter, book_chapter_name])

# print(result_list)


# bible_books = {
#     1: {"name": "Genesis", "chapters": 50},
#     2: {"name": "Exodus", "chapters": 40},
#     3: {"name": "Leviticus", "chapters": 27},
#     4: {"name": "Numbers", "chapters": 36},
#     5: {"name": "Deuteronomy", "chapters": 34},
#     6: {"name": "Joshua", "chapters": 24},
#     7: {"name": "Judges", "chapters": 21},
#     8: {"name": "Ruth", "chapters": 4},
#     9: {"name": "1 Samuel", "chapters": 31},
#     10: {"name": "2 Samuel", "chapters": 24},
#     11: {"name": "1 Kings", "chapters": 22},
#     12: {"name": "2 Kings", "chapters": 25},
#     13: {"name": "1 Chronicles", "chapters": 29},
#     14: {"name": "2 Chronicles", "chapters": 36},
#     15: {"name": "Ezra", "chapters": 10},
#     16: {"name": "Nehemiah", "chapters": 13},
#     17: {"name": "Esther", "chapters": 10},
#     18: {"name": "Job", "chapters": 42},
#     19: {"name": "Psalms", "chapters": 150},
#     20: {"name": "Proverbs", "chapters": 31},
#     21: {"name": "Ecclesiastes", "chapters": 12},
#     22: {"name": "Song of Solomon", "chapters": 8},
#     23: {"name": "Isaiah", "chapters": 66},
#     24: {"name": "Jeremiah", "chapters": 52},
#     25: {"name": "Lamentations", "chapters": 5},
#     26: {"name": "Ezekiel", "chapters": 48},
#     27: {"name": "Daniel", "chapters": 12},
#     28: {"name": "Hosea", "chapters": 14},
#     29: {"name": "Joel", "chapters": 3},
#     30: {"name": "Amos", "chapters": 9},
#     31: {"name": "Obadiah", "chapters": 1},
#     32: {"name": "Jonah", "chapters": 4},
#     33: {"name": "Micah", "chapters": 7},
#     34: {"name": "Nahum", "chapters": 3},
#     35: {"name": "Habakkuk", "chapters": 3},
#     36: {"name": "Zephaniah", "chapters": 3},
#     37: {"name": "Haggai", "chapters": 2},
#     38: {"name": "Zechariah", "chapters": 14},
#     39: {"name": "Malachi", "chapters": 4},
#     40: {"name": "Matthew", "chapters": 28},
#     41: {"name": "Mark", "chapters": 16},
#     42: {"name": "Luke", "chapters": 24},
#     43: {"name": "John", "chapters": 21},
#     44: {"name": "Acts", "chapters": 28},
#     45: {"name": "Romans", "chapters": 16},
#     46: {"name": "1 Corinthians", "chapters": 16},
#     47: {"name": "2 Corinthians", "chapters": 13},
#     48: {"name": "Galatians", "chapters": 6},
#     49: {"name": "Ephesians", "chapters": 6},
#     50: {"name": "Philippians", "chapters": 4},
#     51: {"name": "Colossians", "chapters": 4},
#     52: {"name": "1 Thessalonians", "chapters": 5},
#     53: {"name": "2 Thessalonians", "chapters": 3},
#     54: {"name": "1 Timothy", "chapters": 6},
#     55: {"name": "2 Timothy", "chapters": 4},
#     56: {"name": "Titus", "chapters": 3},
#     57: {"name": "Philemon", "chapters": 1},
#     58: {"name": "Hebrews", "chapters": 13},
#     59: {"name": "James", "chapters": 5},
#     60: {"name": "1 Peter", "chapters": 5},
#     61: {"name": "2 Peter", "chapters": 3},
#     62: {"name": "1 John", "chapters": 5},
#     63: {"name": "2 John", "chapters": 1},
#     64: {"name": "3 John", "chapters": 1},
#     65: {"name": "Jude", "chapters": 1},
#     66: {"name": "Revelation", "chapters": 22}
# }

# result_list = []

# for book_id, book_info in bible_books.items():
#     book_name = book_info["name"]
#     chapters = book_info["chapters"]

#     for chapter in range(1, chapters + 1):
#         book_chapter_name = f"{book_name} {chapter}"
#         if book_name[0].isdigit():
#             words = book_name.split()
#             short_name = f"{words[0]} {words[1][:3]} {chapter}"
#         else:
#             short_name = f"{book_name[:3].ljust(3, ' ')} {chapter}"
#         # print(short_name)

#         result_list.append([len(result_list) + 1, book_id, chapter, book_chapter_name, short_name])

# print(result_list)


# import sqlite3

# # Connect to SQLite database (will create it if it doesn't exist)
# conn = sqlite3.connect('logs.db')

# # Create a cursor object to execute SQL commands
# cursor = conn.cursor()

# # Create table log_details
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS log_details (
#         id INTEGER PRIMARY KEY,
#         user TEXT NOT NULL,
#         time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
# ''')

# # Create table details
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS details (
#         id INTEGER PRIMARY KEY,
#         user TEXT NOT NULL,
#         time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         data TEXT
#     )
# ''')

# # Commit changes and close connection
# conn.commit()
# conn.close()

# print("Database 'logs.db' created successfully with tables 'log_details' and 'details'.")


import sqlite3

# Connect to SQLite database (creates a new database if not exists)
conn = sqlite3.connect('logs.db')

# Create a cursor object to execute SQL commands
cur = conn.cursor()

# Create add_logs table
cur.execute('''
CREATE TABLE IF NOT EXISTS add_logs (
    id INTEGER PRIMARY KEY,
    user TEXT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    link TEXT
)
''')

# Create edit_logs table
cur.execute('''
CREATE TABLE IF NOT EXISTS edit_logs (
    id INTEGER PRIMARY KEY,
    edit_id INTEGER,
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
    username TEXT
)
''')

# Create delete_logs table
cur.execute('''
CREATE TABLE IF NOT EXISTS delete_logs (
    id INTEGER PRIMARY KEY,
    delete_id INTEGER,
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
    username TEXT
)
''')

# Commit changes and close connection
conn.commit()
conn.close()

print("Tables created successfully.")
