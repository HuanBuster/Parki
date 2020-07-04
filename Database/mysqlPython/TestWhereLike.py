from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config

def QueryWhereLike():

    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()
    text = '\'The%\''
    query = "SELECT * FROM books WHERE title LIKE {} ".format(text)
    # value = (text,)
    cursor.execute(query)
    rows = cursor.fetchall()
    # first_name = result[0]
    # only_name = first_name[0].split()
    
    # print('The name is:',only_name[-1])
    # print(name[0].split())
    print('Total Row(s):', cursor.rowcount)
    for row in rows:
        print(row)
    cursor.close()
    conn.close()

if __name__ == "__main__":
    QueryWhereLike()