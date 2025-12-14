import sqlite3, os
db='database.db'
if os.path.exists(db):
    print('database.db already exists')
else:
    conn=sqlite3.connect(db)
    c=conn.cursor()
    c.execute('''CREATE TABLE jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, type TEXT, description TEXT)''')
    c.execute('''CREATE TABLE applications (id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER, name TEXT, email TEXT, resume_file TEXT, timestamp TEXT, match_score INTEGER)''')
    jobs=[
        ('Python Developer','Full-time','Backend developer with Python, Flask, REST APIs.'),
        ('AWS Engineer','Full-time','Cloud engineer experienced with AWS services.'),
        ('Full Stack Developer','Contract','Frontend + Backend experience required.')
    ]
    c.executemany('INSERT INTO jobs (title,type,description) VALUES (?,?,?)', jobs)
    conn.commit()
    conn.close()
    print('database.db created and seeded')
