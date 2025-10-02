import sqlite3

def get_db():
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None):
    try:
        conn = get_db()
        c = conn.cursor()
        
        if params:
            c.execute(query, params)
        else:
            c.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            results = [dict(row) for row in c.fetchall()]
            conn.close()
            return {'success': True, 'data': results}
        else:
            conn.commit()
            last_id = c.lastrowid
            conn.close()
            return {'success': True, 'last_id': last_id}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}