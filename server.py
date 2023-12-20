from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
import hashlib
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

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
            song_no TEXT,
            title TEXT,
            alternate_title TEXT,
            lyrics TEXT,
            transliteration TEXT,
            verse_order TEXT,
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

def song_view(lyrics, transliteration_lyrics):
    if transliteration_lyrics == "":
        paragraphs = lyrics.split('\r\n')
        para_count = 1
        formatted_song = f"<p id={para_count} style='border: 1px solid black;padding: 10px;'>"
        for paragraph in paragraphs:
            if paragraph == "":
                para_count +=1
                formatted_song += f"</p><p id={para_count} style='border: 1px solid black;padding: 10px;'>"
            else:
                formatted_song += f'{paragraph}<br>'
    else:
        paragraphs1 = lyrics.split('\r\n')
        paragraphs2 = transliteration_lyrics.split('\r\n')
        print(paragraphs1)
        print(paragraphs2)
        allow1 = 0
        allow2 = 0
        para_count = 1
        formatted_song = f"<p id={para_count} style='border: 1px solid black;padding: 10px;'>"
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

@app.route('/')
def home():
    if 'username' in session:
        login = True
        user = session['username']
    else:
        login = False
        user=""
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Execute a query to select data from the 'songs' table
    cursor.execute('SELECT id, song_no, title, search_title, search_lyrics FROM songs')
    # Fetch all rows with the specified columns
    rows = cursor.fetchall()

    # print(rows)
    conn.close()

    return render_template("home.html", login=login, user=user, rows=rows)

@app.route('/get_lyrics', methods=['POST'])
def get_lyrics():
    data = request.get_json()   
    selected_id = data['id']
    # print("ids", selected_id)

    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Execute a query to select data from the 'songs' table for the selected ID
    cursor.execute('SELECT lyrics, transliteration, title FROM songs WHERE id = ?', (selected_id,))
    
    row = cursor.fetchone()
    # print(row)

    # Close the database connection
    conn.close()

    if row:
        lyrics = song_view(row[0], row[1])
        # print(lyrics)
        return jsonify({'lyrics': lyrics, 'title':row[2]})
    else:
        return jsonify({'lyrics': [], 'title': []})
    
@app.route('/song/<id>')
def song(id):
     # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Execute a query to select data from the 'songs' table for the selected ID
    cursor.execute('SELECT lyrics, transliteration, title FROM songs WHERE id = ?', (int(id),))
    
    row = cursor.fetchone()
    # print(row)

    # Close the database connection
    conn.close()

    lyrics = song_view(row[0], row[1])

    # print("HI")

    return render_template("song_viewer.html", lyrics=lyrics, song_title=row[2])

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
        return render_template("dashboard.html", user_name= session['username'])
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
        song_language = request.form['songLanguage']
        other_language = request.form.get('otherLanguageInput')
        transliteration_lyrics = request.form.get('transliterationLyrics')
        song_no = request.form.get('songNumber')
        chord = request.form.get('chord')
        title = request.form['title']
        alternate_title = request.form.get('alternateTitle')
        lyrics = request.form['lyrics']
        verse_order = request.form['verseOrder']
        search_title = title + "@" + alternate_title + "@" + song_language + " " + str(song_no)
        song_no = song_language + " " + str(song_no)
        search_lyrics = lyrics.replace('\r\n', ' ') + " " + transliteration_lyrics.replace('\n', ' ')
        
        conn = create_connection()
        cursor = conn.cursor()

        # Get the current date and time
        current_date = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Insert song data into the songs table
        cursor.execute('''
            INSERT INTO songs (song_no, title, alternate_title, lyrics, transliteration, verse_order, search_title, search_lyrics, create_date, modified_date, username)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (song_no, title, alternate_title, lyrics, transliteration_lyrics,
            verse_order, search_title, search_lyrics, current_date, current_date, session['username']))

        conn.commit()
        conn.close()


        return redirect('/dashboard')
    
    return render_template('add_song.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
