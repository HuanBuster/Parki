from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config

def Delete(name):

    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    query = "DELETE FROM vehicle JOIN customer on vehicle.customer_id = customer.customer_id WHERE first_name LIKE {}".format(name)
    cursor.execute(query)
    conn.commit()

    DeleteMes = 'User has been deleted'
    print(DeleteMes)
    cursor.close()
    conn.close()

def GetLP(name):
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    query = "SELECT vehicle_number FROM vehicle JOIN customer ON vehicle.customer_id = customer.customer_id WHERE first_name LIKE {}".format(name)
    cursor.execute(query)

    TupleResult = cursor.fetchall()
    VehicleId = TupleResult[0]
    
    cursor.close()
    conn.close()
    return VehicleId

 
if __name__ == "__main__":
    ConditionQuery = '\'' + '%' + 'Son' + '\''
    print(ConditionQuery)
    # Delete(ConditionQuery)
    # number = GetLP(ConditionQuery)
    # print(number)
    Delete(ConditionQuery)
    