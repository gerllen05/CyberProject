import sqlite3
import os

db_conn = sqlite3.connect('Server/Server.db')
# db_conn.execute(f'UPDATE Users SET openedFilePath = NULL')
# # # db_conn.execute(f'ALTER TABLE Users ADD COLUMN openedFilePath STRING')
db_conn.execute(f'INSERT INTO Accesses (path, guestId) VALUES("admin/123.txt", 2)')
db_conn.commit()
