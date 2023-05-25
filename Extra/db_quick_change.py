import sqlite3
import os
from bcrypt import hashpw, checkpw, gensalt

db_conn = sqlite3.connect('Server/Server.db')
# hashed_password = hashpw('a9@sdf8$98'.encode('utf-8'), gensalt(5)).decode('utf-8')
# db_conn.execute(f'UPDATE Users SET password = "{hashed_password}" WHERE login = "admin"')
db_conn.execute(f'DELETE FROM Users WHERE userId = 2')
# db_conn.execute(f'UPDATE Users SET login = "adminadmin" WHERE login = "admin"')
# db_conn.execute(f'ALTER TABLE Accesses ADD COLUMN creatorId INTEGER')
# db_conn.execute(f'ALTER TABLE Users ADD COLUMN lastLogInTime STRING')
# db_conn.execute(f'INSERT INTO Accesses (path, guestId) VALUES("admin/123.txt", 2)')
db_conn.commit()
db_conn.close()