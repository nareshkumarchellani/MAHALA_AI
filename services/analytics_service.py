from database import query

def overview():
    c=query('SELECT category,COUNT(*) n FROM complaints GROUP BY category ORDER BY n DESC')
    s=query('SELECT status,COUNT(*) n FROM complaints GROUP BY status')
    p=query('SELECT ai_priority,COUNT(*) n FROM complaints GROUP BY ai_priority')
    return {'categories':c,'statuses':s,'priorities':p}
