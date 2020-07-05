from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config

ROW = 5
COL = 3

def GetAllVacancyLot(ListStatus):
    # 0 is occupied, 1 is avaliable 
    # Create a list to save positions of all avaliable parking lot
    SaveList = []  
    for row in range(ROW):
        RowList = ListStatus[row]
        for col in range(COL):
            if RowList[col] == 1:
                TuplePostion = (row,col)
                SaveList.append(TuplePostion)
    return SaveList

def CalcDistance(ListVacancy, StartPoint):
    SaveList = []
    for OneVacancy in ListVacancy:
        RowDistance = abs(OneVacancy[0] - StartPoint[0])
        ColDistance = abs(OneVacancy[1] - StartPoint[1])
        TotalDistance = RowDistance + ColDistance
        SaveList.append(TotalDistance)
    return SaveList

def FindShortestLot(ListOfDistanceAndPosition):
    for TupleInfo in range(len(ListOfDistanceAndPosition)):
        if ListOfDistanceAndPosition[TupleInfo][2] == min(ListOfDistanceAndPosition)[2]:
            MinLocation = ListOfDistanceAndPosition[TupleInfo]
    return MinLocation

def GetAllParkingLot():
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM parking_lot")
    Lots = cursor.fetchall()

    cursor.close()
    conn.close()
    return Lots

def ConvertToMatrix(ListStatus):
    CreateMatrix = []
    CreateListInMatrix = []
    RowMatrix = 5
    ColMatrix = 3
    CreateMatrix.append(['*']*ColMatrix)
    for NumberInRow in range(RowMatrix):
        for NumberInCol in range(ColMatrix):
            CreateListInMatrix.append(ListStatus[NumberInRow + NumberInCol * RowMatrix][0])
        CreateMatrix.append(CreateListInMatrix)
        CreateListInMatrix = []
    CreateMatrix.append(['*']*ColMatrix)
    return CreateMatrix

def ConvertToOrder(ShortestLocation):
    Order = ShortestLocation[0] + ShortestLocation[1] * 5
    return Order 

def WriteLPToParking(LicenceNumber, Order):
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    Statement = "UPDATE parking_lot SET vehicle_number = %s WHERE slot_number = %s "
    Value = (LicenceNumber, Order)
    
    cursor.execute(Statement, Value)
    conn.commit()
    print('Saved {} into position {}'.format(LicenceNumber, Order))

    cursor.close()
    conn.close()

def DeleteLPFromParking(LicenceNumber):
    dbconfig = read_db_config()
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()

    Statement = "UPDATE parking_lot SET vehicle_number = NULL WHERE vehicle_number = %s "
    Value = (LicenceNumber, )
    
    cursor.execute(Statement, Value)
    conn.commit()
    print('Deleted {} from parking'.format(LicenceNumber))

    cursor.close()
    conn.close()

# o = ConvertToOrder((1, 0, 1))
# print(o)
# InputMatrix =  [[ 0, 0, 0, 0, 0],  
#                 [ 0, 0, 0, 0, 0],  
#                 [ 0, 0, 1, 0, 0],  
#                 [ 0, 1, 1, 1, 1],  
#                 [ 0, 1, 1, 0, 0],  
#                 [ 0, 0, 0, 0, 0],  
#                 [ 0, 1, 1, 0, 1],  
#                 [ 0, 0, 0, 0, 0]]
#  --------------------------------
def MasterSearch():
    ParkingStatus = GetAllParkingLot()
    TestMatrix = ConvertToMatrix(ParkingStatus)
    Source = (0,0)
    ListVacancy = GetAllVacancyLot(TestMatrix)
    if len(ListVacancy) != 0:
        ListResult = CalcDistance(ListVacancy,Source)
        ProcessResult = []
        for vacancy in range(len(ListResult)):
            PosAndDis = (ListVacancy[vacancy][0], ListVacancy[vacancy][1], ListResult[vacancy])
            ProcessResult.append(PosAndDis)
        ShortestLocation = FindShortestLot(ProcessResult)
        FoundShortestLocation = True
        return FoundShortestLocation, ShortestLocation
    else:
        FoundShortestLocation = False
        return FoundShortestLocation

        




