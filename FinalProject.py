import tkinter as tk
from tkinter import *
import numpy as np
import tkinter.messagebox
import pyodbc
import face_recognition
from pandas import DataFrame as df

print('start')

# avg vectoer of 50 samples this vector is saved at DB
avgVector = []
for x in range(0, 128):
    avgVector.append(0)


def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title('!')
    label = tk.Label(popup, text=msg)
    label.pack(side='top', fill='x', pady=10)
    b1 = tk.Button(popup, text='Okay', command=popup.destroy)
    b1.pack()
    popup.mainloop()


def RemakeList(lst1):
    """
    this func get list of floats change the data type to string
    :param lst1: list
    :return: string
    """
    print('RemakeList')
    li = str(lst1).replace('\n', '')
    li1 = li.replace(' ', '')
    li2 = li1.split(',')
    str1 = ""
    for ele in li2:
        str1 += ele + ' ,'
    str1 = str1[8:-5]
    return str1


def OpenCamera():
    print('OpenCamera')
    # OpenCV program to detect face in real time
    # import libraries of python OpenCV
    # where its functionality resides
    import cv2

    # load the required trained XML classifiers
    # https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
    # Trained XML classifiers describes some features of some
    # object we want to detect a cascade function is trained
    # from a lot of positive(faces) and negative(non-faces)
    # images.

    # cascPath = 'C:/Users/Gil/PycharmProjects/FinalProject/venv/hde_fe_default.xml'
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
    # Trained XML file for detecting eyes
    # eyePath = 'C:/Users/Gil/PycharmProjects/FinalProject/venv/haarcascade_eye.xml'
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

    # capture frames from a camera
    cap = cv2.VideoCapture(0)
    flag = True
    count = 10
    for i in range(0, 128):
        avgVector[i] = 0

    # loop runs if capturing has been initialized.
    while 1:

        # reads frames from a camera
        ret, img = cap.read()

        # convert to gray scale of each frames
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detects faces of different sizes in the input image
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            # To draw a rectangle in a face.
            # The face data is stored as tuples of coordinates.
            # x and y define the coordinate of the upper-left corner of the face frame,
            # w and h define the width and height of the frame.
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

            # Detects eyes of different sizes in the input image
            eyes = eye_cascade.detectMultiScale(roi_gray)

            # To draw a rectangle in eyes
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 127, 255), 2)

            #
        # Display an image in a window

        cv2.imshow('img', img)

        """
        print('count outside the loop: ', count)
        if flag == True and count > 0:
            count = count - 1
            if count == 0:
                flag = False
        elif flag == False and count < 10:
            if len(eyes) == 2:
                count = count + 1
                print('count inside : ', count)
                print(len(eyes))
                print('add to sumvector')
                encoded_face = face_recognition.api.face_encodings(img, faces, 1, 'large')

                print(encoded_face)
                print('#################################################bla  ', encoded_face[0])
                SumAvgFaces(encoded_face[0])
            else:
                print('count not increase... ', count)
        else:
            for i in range(0, 128):
                avgVector[i] = (avgVector[i] / 10)
            print('avgVector :', avgVector)
        """

        # Wait for Esc key to stop
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

    encoded_face = face_recognition.api.face_encodings(img, None, 1, 'small')
    print(type(encoded_face))
    print(encoded_face)
    # Close the window
    cap.release()

    # De-allocate any associated memory usage
    cv2.destroyAllWindows()
    return encoded_face


def SumAvgFaces(encoded_face):
    for i in range(0, 128):
        avgVector[i] += encoded_face[i]


def ReadFromDB(conn):
    print('ReadFromDB')
    cursor = conn.cursor()
    cursor.execute("select * from Bank.dbo.FaceVectors1")
    for row in cursor:
        print(f'row={row}')
    print()


def SearchIdInDB(conn, id):
    """
    #this func search if a given id is exists in database
    #if exists then return the data about if not return false
    """
    print('SearchIdInDB')
    cursor = conn.cursor()
    cursor.execute("Select * from Bank.dbo.FaceVectors1 where id = ?",
                   (id))  # if found return a list of the mathing row
    row = cursor.fetchmany(4)
    if not row:
        return False  # not exists in database
    else:
        # print(row[0][3])
        row0 = row[0]
        print('row0')
        print(type(row0))
        print(row0)
        print('row3')
        row1 = row0[3]
        print(row1)
        row1 = row1.split(",")
        print(type(row1))
        return row  # exists in database


def CalculateVectorsSimilarity(vectorfromcam, vectorfromdb):
    """
    this func get list from cam of 128-d that represent the person we are capturing now
    and vectorfromdb is string from DB that we check the similarty of.
    :param vectorfromcam:class 'list'
    :param vectorfromdb:class 'str'
    :return:
    """
    print('CalculateVectorsSimilarity')
    print('vectorfromdb:', type(vectorfromdb), vectorfromdb)
    print('vectorfromcam:', type(vectorfromcam), vectorfromcam)
    known_face_encodings = vectorfromdb[1:-1]  # vectorfromdb come as str with "[]" here we remove those signs
    face_encoding_to_check = vectorfromcam
    bla = face_recognition.compare_faces(known_face_encodings, face_encoding_to_check, 0.6)
    print('after compare_faces')
    print(bla)


def UpdateFromDB(conn):
    print('UpdateFromDB')
    cursor = conn.cursor()
    cursor.execute('insert into Bank.dbo.FaceVectors1() ')
    conn.commit()
    ReadFromDB(conn)


def InsertDB(conn, Eid, EfName, ElName, eVectors1, eVectors2, eVectors3, eVectors4, eVectors5):  # insert new data to DB
    print('InsertDB')
    id = Eid
    fName = EfName
    lName = ElName
    vector1 = eVectors1
    vector2 = eVectors2
    vector3 = eVectors3
    vector4 = eVectors4
    vector5 = eVectors5
    print('v 5')
    print(type(vector5))
    print(vector5)
    cursor = conn.cursor()
    cursor.execute(
        "insert into Bank.dbo.FaceVectors1(id,first_name,last_name,vector1,vector2,vector3,vector4,vector5) values(?,?,?,?,?,?,?,?);",
        (id, fName, lName, vector1, vector2, vector3, vector4, vector5))
    conn.commit()
    row = SearchIdInDB(conn, id)
    return row


def DeleteFromDB(conn, id):
    print('DeleteFromDB')
    cursor = conn.cursor()
    cursor.execute('delete from Bank.dbo.FaceVectors1 where id = ?', (id))
    conn.commit()
    ReadFromDB(conn)


def face_distance(face_encodings, face_to_compare):
    """
    Given a list of face encodings, compare them to a known face encoding and get a euclidean distance
    for each comparison face. The distance tells you how similar the faces are.

    :param faces: List of face encodings to compare
    :param face_to_compare: A face encoding to compare against
    :return: A numpy ndarray with the distance for each face in the same order as the 'faces' array
    """
    print('face_distance')
    if len(face_encodings) == 0:
        return np.empty((0))

    bla = 0
    for i in range(0, 128):
        bla += (face_encodings[i] - face_to_compare[i]) ** 2
    bla = abs((bla) ** 0.5)
    print('bla')
    print(bla)

    print('before bla ')
    bla = np.linalg.norm([face_encodings] - face_to_compare, ord='other', axis=1)
    print('bla')
    print(type(bla))
    print(bla)
    return bla
    # return np.linalg.norm([face_encodings] - face_to_compare, axis=1)


def Convert(known_face_encodings):  # , face_to_compare):
    """
    get string of strings(known_face_encodings) and list of numpy.float64 (face_to_compare) and return 2 lists of floats.
    :param known_face_encodings: a string of known_face_encodings (from DB) type of string: <class 'str'>, type of string[1]:<class 'str'> .
    :param face_to_compare: a list of face_encoding_to_check (from cam) type of str: <class 'list'> type of str[1]: <class 'numpy.float64'> .
    :return: 2 different 'numpy.ndarray' with the same type : class 'numpy.float64' .
    """
    print('Convert')
    lst = ''
    lst = known_face_encodings.split(',')
    arr = np.array([], dtype='float64')
    for word in lst:
        n = float(word)
        arr = np.append(arr, n)
    print(arr)
    return arr


def compare_faces(known_face_encodings, face_encoding_to_check, tolerance=0.6):
    """
    Compare a list of face encodings against a candidate encoding to see if they match.

    :param known_face_encodings: A list of known face encodings
    :param face_encoding_to_check: A single face encoding to compare against the list
    :param tolerance: How much distance between faces to consider it a match. Lower is more strict. 0.6 is typical best performance.
    :return: A list of True/False values indicating which known_face_encodings match the face encoding to check
    """
    print('compare_faces')
    # convert known_face_encodings, face_encoding_to_check to numpt.ndarray
    known_face_encodings, face_encoding_to_check = Convert(known_face_encodings, face_encoding_to_check)
    return list(face_distance(known_face_encodings, face_encoding_to_check) <= tolerance)


# conn is the connection to the DB
conn = pyodbc.connect("DRIVER={SQL Server Native Client 11.0};"
                      "Server=;גיל"
                      "Database=Bank;"
                      "Trusted_Connection=yes;")


#DeleteFromDB(conn,'123456123')


# InsertDB(conn, '321321321', 'gil', 'sharon', '1', '2', '3', '4', '5')


# GUI
class SeaofBTCapp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, ExsitsingUser, AddNewUser):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page")
        label.pack(pady=10, padx=10)

        button = tk.Button(self, text="Exsitsing user",
                           command=lambda: controller.show_frame(ExsitsingUser))
        button.pack()

        button2 = tk.Button(self, text="Add New User",
                            command=lambda: controller.show_frame(AddNewUser))
        button2.pack()


class ExsitsingUser(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        def enterId(event):
            id = idEntry.get()
            if id == '' or id.isnumeric() == False or len(id) != 9:
                tk.messagebox.showinfo('Error', "Please enter your id.\nit must be a number with 9 digits!")
            else:
                vectorfromdb = SearchIdInDB(conn, id)
                if vectorfromdb == False:
                    tk.messagebox.showinfo('Error', "ID not exsits!\ntry again....")
                else:

                    vectorfromdbonlyvector1 = Convert(vectorfromdb[0][3])
                    vectorfromdbonlyvector2 = Convert(vectorfromdb[0][4])
                    vectorfromdbonlyvector3 = Convert(vectorfromdb[0][5])
                    vectorfromdbonlyvector4 = Convert(vectorfromdb[0][6])
                    vectorfromdbonlyvector5 = Convert(vectorfromdb[0][7])

                    vectorfromcam = OpenCamera()

                    if len(vectorfromcam) == 0:
                        print('vectorfromcam', vectorfromcam, ' type: ', type(vectorfromcam))
                        popupmsg('The cam didnt get your face please try again')
                    else:
                        answer1 = face_recognition.api.face_distance(vectorfromcam, vectorfromdbonlyvector1)
                        answer2 = face_recognition.api.face_distance(vectorfromcam, vectorfromdbonlyvector2)
                        answer3 = face_recognition.api.face_distance(vectorfromcam, vectorfromdbonlyvector3)
                        answer4 = face_recognition.api.face_distance(vectorfromcam, vectorfromdbonlyvector4)
                        answer5 = face_recognition.api.face_distance(vectorfromcam, vectorfromdbonlyvector5)
                        print(answer1)
                        print(answer2)
                        print(answer3)
                        print(answer4)
                        print(answer5)
                        if answer1.size == 0:
                            popupmsg("the cam didnt capture your face please try again")
                        elif answer2.size == 0:
                            popupmsg("the cam didnt capture your face please try again")
                        elif answer3.size == 0:
                            popupmsg("the cam didnt capture your face please try again")
                        elif answer4.size == 0:
                            popupmsg("the cam didnt capture your face please try again")
                        elif answer5.size == 0:
                            popupmsg("the cam didnt capture your face please try again")
                        else:
                            avg = answer1
                            avg += answer2
                            avg += answer3
                            avg += answer4
                            avg += answer5
                            avg /= 5
                            print('avg:', avg)
                            if avg <= 0.45:
                                msg = 'welcome '
                                msg += vectorfromdb[0][1]
                                msg += ' '
                                msg += vectorfromdb[0][2]
                                popupmsg(msg)
                            else:
                                popupmsg('You have no permission to this account!')

                        print('the check was against :', vectorfromdb[0][1], vectorfromdb[0][2], 'id :',
                              vectorfromdb[0][0])

            idEntry.delete(0, 'end')

        labelExistsID = tk.Label(self, text="Enter Exists id")
        labelExistsID.pack(anchor=NW, padx=5, pady=5)
        idEntry = tk.Entry(self)
        idEntry.pack(anchor=NW, padx=5, pady=5)
        buttonEnter = tk.Button(self, text="Enter", fg="black")
        buttonEnter.pack(side=LEFT, anchor='s', padx=5, pady=5)
        buttonEnter.bind("<Button-1>", enterId)

        buttonBackHome = tk.Button(self, text="Back to Home",
                                   command=lambda: controller.show_frame(StartPage))

        buttonAddNewUser = tk.Button(self, text="Add New User",
                                     command=lambda: controller.show_frame(AddNewUser))

        buttonBackHome.pack(side=RIGHT, anchor='s', padx=5, pady=5)
        buttonAddNewUser.pack(side=RIGHT, anchor='s', padx=5, pady=5)


class AddNewUser(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        labelTitle = tk.Label(self, text="Add New User", )
        labelTitle.pack(pady=10, padx=10)

        def NewUser(event):
            eFName = entryFirstName.get()
            eLName = entryLastName.get()
            eID = entryID.get()
            if eFName.isalpha() and eLName.isalpha() and eID.isnumeric():
                res = SearchIdInDB(conn, eID)
                if res == False:  # there is no object with the same id, so we can insert our data to the DB
                    print('ok123')

                    flag1 = 0
                    while flag1 == 0:
                        print('vec 1')
                        vectorToInsert1 = OpenCamera()
                        print(vectorToInsert1)

                        if vectorToInsert1 != []:
                            flag1 = 1
                    while flag1 == 1:
                        print('vec 2')
                        vectorToInsert2 = OpenCamera()
                        if vectorToInsert2 != []:
                            flag1 = 0
                    while flag1 == 0:
                        print('vec 3')
                        vectorToInsert3 = OpenCamera()
                        if vectorToInsert3 != []:
                            flag1 = 1
                    while flag1 == 1:
                        print('vec 4')
                        vectorToInsert4 = OpenCamera()
                        if vectorToInsert4 != []:
                            flag1 = 0
                    while flag1 == 0:
                        print('vec 5')
                        vectorToInsert5 = OpenCamera()
                        if vectorToInsert5 != []:
                            flag1 = 1

                    vectorToInsert1 = RemakeList(vectorToInsert1)
                    vectorToInsert2 = RemakeList(vectorToInsert2)
                    vectorToInsert3 = RemakeList(vectorToInsert3)
                    vectorToInsert4 = RemakeList(vectorToInsert4)
                    vectorToInsert5 = RemakeList(vectorToInsert5)

                    print('v 5')
                    print(type(vectorToInsert5))
                    print(vectorToInsert5)

                    try:
                        answer = InsertDB(conn, eID, eFName, eLName, vectorToInsert1, vectorToInsert2, vectorToInsert3,
                                          vectorToInsert4, vectorToInsert5)

                    except SystemError as e:
                        if "Previous SQL was not a query." in str(e):
                            pass
                        else:
                            raise e
                    if answer == False:
                        tk.messagebox.showinfo('Error', "Problem to add new user,\nPlease try again")
                    else:
                        tk.messagebox.showinfo('Success',
                                               eFName + ' ' + eLName + ' with id ' + eID + ' added successfully to the system')

                else:  # there is a object with the same id, so we can't insert our data to the DB
                    print('your id already exsits, please enter your id')
            else:
                print('name must contain only character')

        labelFirstName = tk.Label(self, text='First Name: ')
        labelLastName = tk.Label(self, text='Last Name: ')
        labelID = tk.Label(self, text='ID: ')
        entryFirstName = tk.Entry(self)
        entryLastName = tk.Entry(self)
        entryID = tk.Entry(self)
        labelFirstName.pack(anchor=NW, padx=5, pady=5)
        entryFirstName.pack(anchor=NW, expand=1)

        labelLastName.pack(anchor=W, padx=5, pady=5)
        entryLastName.pack(anchor=W, expand=1)

        labelID.pack(anchor=SW, padx=5, pady=5)
        entryID.pack(anchor=SW, expand=1)

        buttonBackHome = tk.Button(self, text="Back to Home",
                                   command=lambda: controller.show_frame(StartPage))

        buttonExsitsingUser = tk.Button(self, text="Exsitsing User",
                                        command=lambda: controller.show_frame(ExsitsingUser))

        buttonEnterNewUser = tk.Button(self, text="Enter New User", fg="black")
        buttonEnterNewUser.pack(side=LEFT, padx=5, pady=5)
        buttonEnterNewUser.bind("<Button-1>", NewUser)
        buttonExsitsingUser.pack(side=RIGHT, anchor='s', padx=5, pady=5)
        buttonBackHome.pack(side=RIGHT, anchor='s', padx=5, pady=5)


app = SeaofBTCapp()
app.mainloop()
conn.close()
