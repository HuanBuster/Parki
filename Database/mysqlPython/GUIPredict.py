from mysql.connector import MySQLConnection, Error
from PiDBConfig import read_db_config

import tkinter as tk
DisplayRow = 5
# Create a window
window = tk.Tk()
window.title("Database Status")
window.config(bg='white')

# Connect to database
def GetStatusFromDatabase():
	dbconfig = read_db_config()
	conn = MySQLConnection(**dbconfig)
	cursor = conn.cursor()
	cursor.execute("SELECT status FROM parking_lot")
	Statuses = cursor.fetchall()

	cursor.close()
	conn.close()
	return Statuses

def GetActiveUser():
	dbconfig = read_db_config()
	conn = MySQLConnection(**dbconfig)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM vehicle")
	Data = cursor.fetchall()
	
	cursor.close()
	conn.close()
	return Data
	
def ConvertToMatrix(ListStatus):
    CreateMatrix = []
    CreateListInMatrix = []
    RowMatrix = 5
    ColMatrix = 3
    #CreateMatrix.append(['*']*ColMatrix)
    for NumberInRow in range(RowMatrix):
        for NumberInCol in range(ColMatrix):
            CreateListInMatrix.append(ListStatus[NumberInRow + NumberInCol * RowMatrix][0])
        CreateMatrix.append(CreateListInMatrix)
        CreateListInMatrix = []
    #CreateMatrix.append(['*']*ColMatrix)
    return CreateMatrix

ParkingFrame = tk.Frame(window, bg='white')
UserFrame = tk.Frame(window,bg='white')

ParkingFrame.grid(row=0, column=0)
UserFrame.grid(row=0, column=1)

window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
# All the text is here
ParkingText = tk.Label(ParkingFrame, text="Green is vacancy \nRed is occupied", fg='black', bg='white')
ParkingText.grid(row=0, column=0, columnspan=3)
UserText = tk.Label(UserFrame, text="Active user", fg='black', bg='white')
UserText.grid(row=0, column=0)
# All the button is here
ListUser = tk.Listbox(UserFrame,fg='black', bg='white', width=len("CustomerID" + ' | ' +"Vehicle number"))
UserScroll = tk.Scrollbar(UserFrame,orient='vertical', command=ListUser.yview)
UserScroll.grid(row=0,column=1)
ListUser.config(yscrollcommand=UserScroll.set)
#----MAIN----
def AutoRun():
	AllStatus = GetStatusFromDatabase()
	#print(AllStatus)
	Matrix = ConvertToMatrix(AllStatus)
	#print(Matrix)
	A_User = GetActiveUser()
	#print(A_User)

	RowMatrix = 5
	ColMatrix = 3
	for NumberInRow in range(RowMatrix):
		for NumberInCol in range(ColMatrix):
			ButtonCol = tk.Button(ParkingFrame, text=str((NumberInRow + NumberInCol * RowMatrix)+1), width=4)
			if Matrix[NumberInRow][NumberInCol] == 1:
				ButtonCol.config(bg='green')
			else:
				ButtonCol.config(bg='red')
			ButtonCol.grid(row=NumberInRow+1, column=NumberInCol)
	ListUser.insert(0, "CustomerID" + ' | ' +"Vehicle number")
	ListUser.delete(first=1, last=(len(A_User)+2))
	for user in range(len(A_User)):
		Content = str(A_User[user][0]) + '  '*len('CustomerID') + str(A_User[user][1])
		# //DisplayCustomerID = tk.Entry(window, bg='white',fg='black')
		# //DisplayVehicle = tk.Entry(window, bg='white',fg='black')
		
		# //DisplayCustomerID.grid_remove(row=len(A_User)+1)
		# //DisplayVehicle.grid_remove(row=len(A_User)+1)
		
		# //DisplayCustomerID.grid(row=user+1,column=3)
		# //DisplayVehicle.grid(row=user+1,column=4)
		
		# //DisplayCustomerID.insert(1,str(A_User[user][0]))
		# //DisplayVehicle.insert(1,str(A_User[user][1]) )	
		# Using List box
		
		ListUser.insert(user+1,Content)
		ListUser.grid(row=1,column=0)
		
		
	window.after(1000, AutoRun)
			
	# //RegisterButton = tk.Button(text='Login Parking', fg='white', bg='orange')
	# //RegisterButton.grid(row=3, column=0)


AutoRun()
window.mainloop()
	
	
	
