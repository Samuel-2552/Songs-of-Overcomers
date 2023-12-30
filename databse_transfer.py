import xml.etree.ElementTree as ET
import sqlite3

# Process the XML data
def process_xml(xml_data):
    root = ET.fromstring(xml_data)
    lyrics = []
    for verse in root.findall('.//verse'):
        verse_type = verse.get('type')
        verse_text = verse.text.strip()
        lyrics.append((verse_type, verse_text))
    return lyrics

DATABASE = 'oilnwine.db'

def create_connection():
    conn = sqlite3.connect(DATABASE)
    return conn

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

def add_song(title, alternate_title, lyrics, search_title, search_lyrics, create_date, modified_date):
    conn = create_connection()
    cursor = conn.cursor()
    # Insert song data into the songs table
    cursor.execute('''
        INSERT INTO songs (title, alternate_title, lyrics, search_title, search_lyrics, create_date, modified_date, username)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ( title, alternate_title, lyrics, 
         search_title, search_lyrics, create_date, modified_date, "OpenLP"))
    
    conn.commit()
    conn.close()

create_users_table()
create_songs_table()


for i in range(1,1773):
    # Connect to the SQLite database
    db_file = 'songs.sqlite'  # Replace with the path to your SQLite database file
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Execute a query to select data from the 'songs' table for the selected ID
    cursor.execute('SELECT * FROM songs WHERE id = ?', (i,))

    row = cursor.fetchone()
    if row!=None and i!=1574:
        processed=""
        lyrics = process_xml(row[3])
        for j in range(len(lyrics)):
            if j!=len(lyrics)-1:
                processed += lyrics[j][1]+"\n\n"
            else:
                processed += lyrics[j][1]
        print(processed)

        add_song(row[1],row[2],processed,row[9],row[10],row[11],row[12])

    # print(row[1],row[2],processed,row[9],row[10],row[11],row[12])

    # Close the database connection
    conn.close()