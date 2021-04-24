from flask import Flask, render_template, request
import json
from manage_sql import get_question_paper, add_question_paper, all_old_form_details, add_room, check_type_room_info
from manage_sql import check_type_data, add_respondent, return_res_data, save_response_changes

app = Flask(__name__)


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/Create_Form")
def Create_Form():
    return render_template("question_paper.html")


@app.route("/Create_Room")
def Create_Room():
    return render_template("rooms.html")


@app.route("/Form_Rooms")
def Form_Rooms():
    return render_template("Form_rooms.html")


@app.route("/respond")
def respond():
    return render_template("respond.html")


@app.route("/Form_Responses")
def form_responses():
    return render_template("form_responses.html")


@app.route('/saveFormChanges', methods=['POST'])
def accecpt_new_form():

    data_string = request.get_data(as_text=True)
    dataForSQL = json.loads(data_string)
    print(str(dataForSQL))

    return add_question_paper(dataForSQL)


@app.route('/getEditFormDetails', methods=['POST'])
def send_old_paper():
    data_string = request.get_data(as_text=True)
    data = json.loads(data_string)
    print(str(data))

    return json.dumps(get_question_paper(data))


@app.route('/homepageload', methods=['POST'])
def all_old_forms():
    data_string = request.get_data(as_text=True)
    data = json.loads(data_string)
    print(str(data))

    #all_old_form_details(data)

    return json.dumps(all_old_form_details(data))


@app.route('/accountLoginDetails', methods=['POST'])
def account_details():
    data_string = request.get_data(as_text=True)
    data = json.loads(data_string)
    print(str(data))

    return json.dumps(check_type_data(data))


@app.route('/respondFormDetails', methods=['POST'])
def responses():
    data_string = request.get_data(as_text=True)
    data = json.loads(data_string)
    print(str(data))

    return add_respondent(data)


@app.route('/getRespondentsData', methods=['POST'])
def get_res_table():
    data_string = request.get_data(as_text=True)
    data = json.loads(data_string)
    print(str(data))

    return json.dumps(return_res_data(data))


@app.route('/saveChangesOfResponses', methods=['POST'])
def save_res_table():
    data_string = request.get_data(as_text=True)
    data = json.loads(data_string)
    print(str(data))

    return save_response_changes(data)


@app.route('/roomDataInfo', methods=['POST'])
def room_details():
    data_string = request.get_data(as_text=True)
    data = json.loads(data_string)
    print(str(data))

    return json.dumps(check_type_room_info(data))


@app.route('/saveRoomData', methods=['POST'])
def save_room_details():
    data_string = request.get_data(as_text=True)
    data = json.loads(data_string)
    print(str(data))

    return add_room(data)


if __name__ == '__main__':
    app.run(debug=True)