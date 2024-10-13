import sqlite3

DATABASE = "audit_history.db"

# Initialize the database and create the table
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database at the start
init_db()

# Function to save the prompt and response to the database
def save_to_db(prompt: str, response: str):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO audit_log (prompt, response) VALUES (?, ?)", (prompt, response))
        conn.commit()
        print(f"Saved prompt and response to DB: {prompt[:30]}... -> {response[:30]}...")  # Print to check saving
    except Exception as e:
        print(f"Error saving to DB: {e}")
    finally:
        conn.close()


# Function to retrieve the last N interactions from the database
def get_history(context_window: int = 5):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT prompt, response FROM audit_log ORDER BY timestamp DESC LIMIT ?", (context_window,))
    rows = cursor.fetchall()
    conn.close()
    return rows
