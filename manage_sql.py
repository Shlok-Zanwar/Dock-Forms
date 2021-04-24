import mysql.connector
from send_mail import send_otp
import json
import os


def sql_connection():
    try:
        mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          password="shlok",
          database="project_forms",
          port='3306'
        )
        return mydb

    except mysql.connector.Error as err:
        print("sql connection error ("+err+")")


def arr_to_str(array):
    i = 0
    string = ''
    while i < len(array):
        string += array[i]+'ø'
        i += 1

    return string


def get_TrueFalse(num):
    if num == '1':
        num = True

    else:
        num = False

    return num


def str_to_arr(string):
    i = 0
    opt = ''
    array = []
    while i < len(string):
        if string[i] == 'ø':
            array.append(opt)
            opt = ''
        else:
            opt += string[i]

        i += 1

    return array


def add_question_paper(data_collected):

    mydb = sql_connection()
    mycursor = mydb.cursor()

    xyz = delete_form(data_collected['QPaper_ID'])

    if data_collected['QPaper_ID'] == 0:
        sql = "INSERT INTO question_papers (User_ID, Show_responce, Accepting_responce, Rooms_accepted, Title, Description, Limit_response) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (data_collected['User_ID'], data_collected['Settings']['Show_correct'], data_collected['Settings']['Accepting_Responce'], 'None', data_collected['Title'], data_collected['Description'], data_collected['Settings']['Restrict_response'])

        json_data = {
            "QPaper_ID": "",
            "Title": "",
            "Questions": [],
            "num_of_res": 0,
            "resData": []
        }

    else:
        sql = "INSERT INTO question_papers (QPaper_ID, User_ID, Show_responce, Accepting_responce, Rooms_accepted, Title, Description, Limit_response) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (data_collected['QPaper_ID'], data_collected['User_ID'], data_collected['Settings']['Show_correct'],
               data_collected['Settings']['Accepting_Responce'], 'None', data_collected['Title'],
               data_collected['Description'], data_collected['Settings']['Restrict_response'])

        if data_collected['num_of_responds'] == "0":
            file = open("./Response_data/resData_"+str(data_collected['QPaper_ID'])+".json", "r+")
            json_data = json.loads(file.read())

            json_data['num_of_res'] = 0
            json_data['resData'] = []

        else:
            file = open("./Response_data/resData_"+str(data_collected['QPaper_ID'])+".json", "r+")
            json_data = json.loads(file.read())

    mycursor.execute(sql, val)
    mydb.commit()

    QPaper_ID = mycursor.lastrowid
    json_data['Title'] = data_collected['Title']
    json_data['QPaper_ID'] = QPaper_ID
    ques_arr = []

    i = 0

    while i < len(data_collected['Questions']):
        if data_collected['Questions'][i]['Question_type'] == 'Multiple Choice':
            sql = "INSERT INTO questions (QPaper_ID, QType, Question, Options, Correct_ans) VALUES (%s, %s, %s, %s, %s)"
            val = (QPaper_ID, data_collected['Questions'][i]['Question_type'], data_collected['Questions'][i]['Question'], arr_to_str(data_collected['Questions'][i]['Options']), data_collected['Questions'][i]['Correct_ans'])
            mycursor.execute(sql, val)
            mydb.commit()

        elif data_collected['Questions'][i]['Question_type'] == 'Text Type':
            sql = "INSERT INTO questions (QPaper_ID, QType, Question) VALUES (%s, %s, %s)"
            val = (QPaper_ID, data_collected['Questions'][i]['Question_type'], data_collected['Questions'][i]['Question'])
            mycursor.execute(sql, val)
            mydb.commit()

        elif data_collected['Questions'][i]['Question_type'] == 'Range Type':
            sql = "INSERT INTO questions (QPaper_ID, QType, Question, MinRange, MaxRange) VALUES (%s, %s, %s, %s, %s)"
            val = (QPaper_ID, data_collected['Questions'][i]['Question_type'], data_collected['Questions'][i]['Question'], str(data_collected['Questions'][i]['min_range']), data_collected['Questions'][i]['max_range'])
            mycursor.execute(sql, val)
            mydb.commit()

        ques_arr.append(data_collected['Questions'][i]['Question'])

        i += 1

    json_data['Questions'] = ques_arr
    #print("json_data = " + str(json_data))
    write_file = open("./Response_data/resData_"+str(QPaper_ID)+".json", "w+")
    write_file.write(json.dumps(json_data))

    return "Form ID = "+str(QPaper_ID)


def get_question_paper(required_ids):
    send_json = {
        'User_ID': '',
        'num_of_responds': '',
        'Title': '',
        'Description': '',
        'Questions': [],
        'Settings': {
            'Accepting_Responce': '',
            'Show_correct': '',
            'Restrict_response': ''
        },
        'first_create': False
    }

    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "SELECT * FROM question_papers WHERE QPaper_ID = " + str(required_ids['QPaper_ID'])

    mycursor.execute(sql)
    data_from_sql = mycursor.fetchall()
    #print(data_from_sql)

    send_json['User_ID'] = data_from_sql[0][1]
    send_json['Settings']['Show_correct'] = get_TrueFalse(data_from_sql[0][2])
    send_json['Settings']['Accepting_Responce'] = get_TrueFalse(data_from_sql[0][3])

    send_json['Title'] = data_from_sql[0][5]
    send_json['Description'] = data_from_sql[0][6]
    send_json['Settings']['Restrict_response'] = get_TrueFalse(data_from_sql[0][7])

    file = open("./Response_data/resData_"+str(required_ids['QPaper_ID'])+".json", "r+")
    json_data = json.loads(file.read())

    send_json['num_of_responds'] = json_data['num_of_res']

    sql = "SELECT * FROM questions WHERE QPaper_ID = " + str(required_ids['QPaper_ID'])
    mycursor.execute(sql)
    data_from_sql = mycursor.fetchall()
    #print(data_from_sql)


    i = 0

    while i<len(data_from_sql):

        if data_from_sql[i][2] == 'Multiple Choice':
            send_json['Questions'].append({
                "Question_type": data_from_sql[i][2],
                "Question": data_from_sql[i][3],
                "Options":str_to_arr(data_from_sql[i][4]),
                "Correct_ans": data_from_sql[i][5]
            })

        elif data_from_sql[i][2] == 'Text Type':
            send_json['Questions'].append({
                "Question_type":data_from_sql[i][2],
                "Question":data_from_sql[i][3]
            })

        elif data_from_sql[i][2] == 'Range Type':
            send_json['Questions'].append({
                "Question_type":data_from_sql[i][2],
                "Question":data_from_sql[i][3],
                "min_range":float(data_from_sql[i][6]),
                "max_range":float(data_from_sql[i][7])
            })

        i += 1

    return send_json


def all_old_form_details(id_details):
    send_json = {
        'User_ID': '',
        'old_forms': [],
        'old_rooms': []
    }

    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "SELECT QPaper_ID, Title, Accepting_responce FROM question_papers WHERE User_ID = " + str(id_details['User_ID'])

    mycursor.execute(sql)
    data_from_sql = mycursor.fetchall()

    #print(data_from_sql)

    send_json['User_ID'] = id_details['User_ID']

    i = 0

    while i < len(data_from_sql):
        send_json['old_forms'].append({
            'QPaper_ID': data_from_sql[i][0],
            'Title': data_from_sql[i][1],
            'Accepting_responce': get_TrueFalse(data_from_sql[i][2])
        })

        i += 1


    sql = "SELECT Room_ID, Room_Name FROM rooms_info WHERE User_ID = "+str(id_details['User_ID'])
    mycursor.execute(sql)
    data_from_sql = mycursor.fetchall()

    i = 0
    while i < len(data_from_sql):
        send_json['old_rooms'].append({
            'Room_ID': data_from_sql[i][0],
            'Room_Name': data_from_sql[i][1]
        })

        i += 1

    #print(str(send_json))
    #print("Sent Home page data to Id = "+ str(send_json['User_ID']))

    return send_json


def delete_form(QPaper_ID):
    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "DELETE FROM questions WHERE QPaper_id = "+str(QPaper_ID)
    mycursor.execute(sql)
    mydb.commit()

    sql = "DELETE FROM rooms_and_forms WHERE QPaper_ID = "+str(QPaper_ID)
    mycursor.execute(sql)
    mydb.commit()

    sql = "DELETE FROM question_papers WHERE QPaper_ID = "+str(QPaper_ID)
    mycursor.execute(sql)
    mydb.commit()

    return 'QPaper deleted'


def check_type_data(data_json):

    if data_json['Type'] == 'SignIn-Username':
        result = username_pass(data_json['Username'], data_json['Password'])

    elif data_json['Type'] == 'SignIn-Email':
        result = email_pass(data_json['Email'], data_json['Password'])

    elif data_json['Type'] == 'SignUp-Check':
        result = check_signup(data_json['Username'], data_json['Email'])

    elif data_json['Type'] == 'SignUp-Verified':
        result = add_new_user(data_json['Fullname'], data_json['Email'], data_json['Username'], data_json['Password'], "USER")

    elif data_json['Type'] == 'Accepting-responces':
        result = change_acc_response(data_json['QPaper_ID'], data_json['Accepting_responce'])

    elif data_json['Type'] == 'Delete-Form':
        delete_jsonFile(data_json['QPaper_ID'])
        result = delete_form(data_json['QPaper_ID'])

    elif data_json['Type'] == 'Respond-Form':
        result = respond_form_validation(data_json['User_ID'], data_json['QPaper_ID'])

    return result


def delete_jsonFile(QPaper_ID):
    filename = "./Response_data/resData_"+str(QPaper_ID)+".json"
    os.remove(filename)


#for giving a form
def respond_form_validation(User_ID, QPaper_ID):
    send_json = {
        'Status':'',
        'User_ID': '',
        'Title': '',
        'Description': '',
        'Questions': [],
        'Settings': {
            'Show_correct': ''
        },
    }

    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "SELECT * FROM question_papers WHERE QPaper_ID = "+str(QPaper_ID)
    mycursor.execute(sql)

    data_form_sql = mycursor.fetchall()
    print(data_form_sql)

    if len(data_form_sql) == 0:
        send_data = {
            'Status': "Form id - "+str(QPaper_ID)+" does not exist !"
        }
        return send_data

    if data_form_sql[0][3] == '1':

        if data_form_sql[0][7] == '1':
            limit = limit_res_check(QPaper_ID, User_ID)

            if limit == 'Already Responded':
                send_data = {
                    'Status': "You have already responded"
                }
                return send_data

            else:
                a = "Accepting cause not responded"

        else:
            a = "Accepting cause no limit"

        room_check = check_room_acceptance(QPaper_ID, User_ID)
        if room_check == 'Accepted':
            a = "accepted cause present in room or no rooms"

        else:
            send_data = {
                'Status': "This form is restricted to limited users !"
            }
            return send_data


    else:
        send_data = {
            'Status': "Form response is turned off !"
        }
        return send_data

    #print('allowing')

    send_json['Status'] = 'Accepted-data'
    send_json['User_ID'] = data_form_sql[0][1]
    send_json['Settings']['Show_correct'] = get_TrueFalse(data_form_sql[0][2])
    send_json['Title'] = data_form_sql[0][5]
    send_json['Description'] = data_form_sql[0][6]

    sql = "SELECT * FROM questions WHERE QPaper_ID = " + str(QPaper_ID)
    mycursor.execute(sql)
    data_from_sql = mycursor.fetchall()
    # print(data_from_sql)

    i = 0

    while i < len(data_from_sql):

        if data_from_sql[i][2] == 'Multiple Choice':
            send_json['Questions'].append({
                "Question_type": data_from_sql[i][2],
                "Question": data_from_sql[i][3],
                "Options": str_to_arr(data_from_sql[i][4]),
                "Correct_ans": data_from_sql[i][5]
            })

        elif data_from_sql[i][2] == 'Text Type':
            send_json['Questions'].append({
                "Question_type": data_from_sql[i][2],
                "Question": data_from_sql[i][3]
            })

        elif data_from_sql[i][2] == 'Range Type':
            send_json['Questions'].append({
                "Question_type": data_from_sql[i][2],
                "Question": data_from_sql[i][3],
                "min_range": float(data_from_sql[i][6]),
                "max_range": float(data_from_sql[i][7])
            })

        i += 1

    return send_json


def check_room_acceptance(QPaper_Id, User_ID):
    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "SELECT Room_ID FROM rooms_and_forms WHERE QPaper_ID = "+str(QPaper_Id)
    mycursor.execute(sql)
    data_from_sql = mycursor.fetchall()

    if len(data_from_sql) == 0:
        return 'Accepted'

    room_no = 0
    while room_no < len(data_from_sql):
        file = open("./Rooms_data/room_"+str(data_from_sql[room_no][0])+".json", "r+")
        json_data = json.loads(file.read())

        i = 0
        while i < len(json_data['People']):
            if str(User_ID) == json_data['People'][i][0]:
                return 'Accepted'

            i += 1
        room_no += 1

    return 'Denied'


def limit_res_check(QPaper_ID, User_ID):
    file = open("./Response_data/resData_"+str(QPaper_ID)+".json", "r+")
    json_data = json.loads(file.read())

    i = 0
    while i < len(json_data['resData']):

        if json_data['resData'][i]['User_ID'] == User_ID:
            return "Already Responded"

        i += 1

    return "Allowed"


def change_acc_response(QPaper_ID, accepting):
    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "UPDATE question_papers SET Accepting_responce = "+str(accepting)+" WHERE QPaper_ID = "+str(QPaper_ID)
    mycursor.execute(sql)
    mydb.commit()

    return "Accepting Response changed"


def add_new_user(name, email, username, password, account_type):
    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "INSERT INTO user_data (Full_name, Email_address, Username, Password, Account_type) VALUES (%s, %s, %s, %s, %s)"
    val = (name, email, username, password, account_type)
    mycursor.execute(sql, val)
    mydb.commit()

    User_ID = mycursor.lastrowid

    data_status = {
        "Status":"User added",
        "User_ID":User_ID
    }

    return data_status


def check_signup(username, email):
    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "SELECT Username FROM user_data where Username = '"+username+"'"
    mycursor.execute(sql)
    data_from_sql = mycursor.fetchall()

    if len(data_from_sql) > 0:
        data_status = {
            "Status": "Username already exists, Try another username.",
        }
        return data_status
        exit()

    sql = "SELECT Email_address FROM user_data where Email_address = '" + email + "'"
    mycursor.execute(sql)
    data_from_sql = mycursor.fetchall()

    if len(data_from_sql) > 0:
        data_status = {
            "Status": "Email Id already registered. Try another Email"
        }
        return data_status
        exit()

    data_status = {
        "Status": "Accept Login",
        "Otp": send_otp(email)
    }

    return data_status


def username_pass(username, password):
    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "SELECT Password, User_ID FROM user_data where Username = '"+username+"'"
    mycursor.execute(sql)
    correct_pass = mycursor.fetchall()

    if len(correct_pass) == 0:
        login_status = {
            "Status": "Invalid Username"
        }
        return login_status

    else:
        if password == correct_pass[0][0]:
            login_status = {
                "Status": "Login Successful",
                "User_ID": correct_pass[0][1]
            }
            return login_status


        else:
            login_status = {
                "Status": "Incorrect password"
            }
            return login_status


def email_pass(email, password):
    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "SELECT Password, User_ID FROM user_data where Email_address = '"+email+"'"
    mycursor.execute(sql)
    correct_pass = mycursor.fetchall()

    if len(correct_pass) == 0:
        login_status = {
            "Status": "Invalid Email ID"
        }
        return login_status

    else:
        if password == correct_pass[0][0]:
            login_status = {
                "Status": "Login Successful",
                "User_ID":correct_pass[0][1]
            }
            return login_status

        else:
            login_status = {
                "Status": "Incorrect password"
            }
            return login_status


def add_respondent(res_data):
    file = open("./Response_data/resData_"+str(res_data['QPaper_ID'])+".json", "r+")
    json_data = json.loads(file.read())
    json_data['num_of_res'] += 1

    res_data['Response_num'] = json_data['num_of_res']
    print(str(res_data))

    json_data['resData'].append(res_data)

    file = open("./Response_data/resData_" + str(res_data['QPaper_ID']) + ".json", "w+")
    file.write(json.dumps(json_data))

    return "Response collected"


def return_res_data(id_data):
    file = open("./Response_data/resData_" + str(id_data['QPaper_ID']) + ".json", "r+")
    json_data = json.loads(file.read())

    return json_data


def save_response_changes(json_data):
    file = open("./Response_data/resData_"+str(json_data['QPaper_ID'])+".json", "w+")
    file.write(json.dumps(json_data))

    return "Changes Saved"


def add_room(data_collected):
    mydb = sql_connection()
    mycursor = mydb.cursor()

    if data_collected['Room_ID'] == 0:
        sql = "INSERT INTO rooms_info (User_ID, Room_Name) VALUES (%s, %s)"
        val = (data_collected['User_ID'], data_collected['Room_Name'])

        mycursor.execute(sql, val)
        mydb.commit()

        Room_ID = mycursor.lastrowid
        data_collected['Room_ID'] = Room_ID

    else:
        sql = "UPDATE rooms_info SET Room_Name = '"+data_collected['Room_Name']+"' WHERE Room_ID = "+str(data_collected['Room_ID'])
        mycursor.execute(sql)
        mydb.commit()

        sql = "UPDATE rooms_and_forms SET Room_Name = '" + data_collected['Room_Name'] + "' WHERE Room_ID = " + str(data_collected['Room_ID'])
        mycursor.execute(sql)
        mydb.commit()

    write_file = open("./Rooms_data/room_"+str(data_collected['Room_ID'])+".json", "w+")
    write_file.write(json.dumps(data_collected))

    return "Room Updated"


def check_type_room_info(data_json):
    if data_json['Status'] == 'Get Room data':
        return get_room_data(data_json['Room_ID'])

    elif data_json['Status'] == 'Get Add User data':
        return get_add_user_to_room(data_json['User_ID'])

    elif data_json['Status'] == 'Delete Room':
        delete_roomJson(data_json['Room_ID'])
        return delete_room(data_json['Room_ID'])

    elif data_json['Status'] == 'Get rooms connected':
        return send_rooms_connected(data_json['QPaper_ID'])

    elif data_json['Status'] == 'Save Connect Changes':
        return save_room_conn_changes(data_json)


def get_room_data(Room_ID):
    filename = "./Rooms_data/room_"+str(Room_ID)+".json"
    file = open(filename, "r+")
    room_data = json.loads(file.read())

    return room_data


def get_add_user_to_room(User_ID):
    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "SELECT Full_name FROM user_data where User_Id = "+str(User_ID)

    mycursor.execute(sql)
    data_from_sql = mycursor.fetchall()

    if len(data_from_sql) == 0:
        send_json = {
            "Status":"No User with User-id "+str(User_ID)+" ."
        }

    else:
        send_json = {
            "Status": "Successful",
            "User_name": data_from_sql[0][0],
            "User_ID": User_ID
        }

    return send_json


def delete_room(Room_ID):
    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "DELETE FROM rooms_and_forms WHERE Room_ID = "+str(Room_ID)
    mycursor.execute(sql)
    mydb.commit()
    sql = "DELETE FROM rooms_info WHERE Room_ID = "+str(Room_ID)
    mycursor.execute(sql)
    mydb.commit()

    return "Room Deleted"


def delete_roomJson(Room_ID):
    filename = "./Rooms_data/room_"+str(Room_ID)+".json"
    os.remove(filename)


def send_rooms_connected(QPaper_ID):
    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "SELECT Room_ID, Room_Name FROM rooms_and_forms WHERE QPaper_ID = "+str(QPaper_ID)
    mycursor.execute(sql)
    data_from_sql = mycursor.fetchall()

    send_data = {
        'QPaper_ID': QPaper_ID,
        'rooms': data_from_sql
    }

    return send_data


def save_room_conn_changes(json_data):
    mydb = sql_connection()
    mycursor = mydb.cursor()

    sql = "DELETE FROM rooms_and_forms where QPaper_ID = "+str(json_data['QPaper_ID'])
    mycursor.execute(sql)
    mydb.commit()

    i = 0
    while i < len(json_data['rooms']):
        sql = "INSERT INTO rooms_and_forms (QPaper_ID, Room_ID, Room_Name) VALUES (%s, %s, %s)"
        val = (json_data['QPaper_ID'], json_data['rooms'][i][0], json_data['rooms'][i][1])

        mycursor.execute(sql, val)
        mydb.commit()

        i += 1

    return "done"

