import sqlite3
conn = sqlite3.connect('mindlens.db')
conn.execute("DELETE FROM entries WHERE user_id = 'local_user'")
conn.commit()
conn.close()
print("Deleted.")
