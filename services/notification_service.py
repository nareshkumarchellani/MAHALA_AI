from database import execute, query, now
def notify(user_id,title,message): execute('INSERT INTO notifications(user_id,title,message,created_at) VALUES(?,?,?,?)',(user_id,title,message,now()))
def unread(user_id): return len(query('SELECT id FROM notifications WHERE user_id=? AND read=0',(user_id,)))
def list_notifications(user_id): return query('SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC',(user_id,))
def mark_read(user_id): execute('UPDATE notifications SET read=1 WHERE user_id=?',(user_id,))
