import cv2
import tkinter as tk
from tkinter import Message ,Text
import cv2
import os
import shutil
import csv
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import time
import tkinter.ttk as ttk
import tkinter.font as font
window = tk.Tk()
window.title("Face_Recognition_System")

dialog_title = 'QUIT'
dialog_text = 'Are you sure?'

window.configure(background='white')
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

message = tk.Label(window, text="Face_Recognition_Based_Attendance_System" ,bg="brown",fg="white"  ,width=49  ,height=2,font=('arial', 30, 'italic bold'))

message.place(x=100, y=20)

lbl = tk.Label(window, text="Enter ID",width=20  ,height=2  ,fg="brown"  ,bg="pink" ,font=('arial', 15, ' bold ') )
lbl.place(x=200, y=150)

txt = tk.Entry(window,width=20  ,bg="pink" ,fg="brown",font=('arial', 15, ' bold '))
txt.place(x=600, y=165)

lbl2 = tk.Label(window, text="Enter Name",width=20  ,fg="brown"  ,bg="pink"    ,height=2 ,font=('arial', 15, ' bold '))
lbl2.place(x=200, y=250)

txt2 = tk.Entry(window,width=20  ,bg="pink"  ,fg="brown",font=('arial', 15, ' bold ')  )
txt2.place(x=600, y=265)

lbl3 = tk.Label(window, text="ImageLoaded  ",width=20  ,fg="brown"  ,bg="pink"  ,height=2 ,font=('arial', 15, ' bold '))
lbl3.place(x=200, y=350)

message = tk.Label(window, text="" ,bg="pink"  ,fg="brown"  ,width=40  ,height=2, activebackground = "pink" ,font=('arial', 15, ' bold '))
message.place(x=600, y=350)

lbl4 = tk.Label(window, text="Attendance ",width=20  ,fg="brown"  ,bg="pink"  ,height=2 ,font=('arial', 15, ' bold'))
lbl4.place(x=400, y=600)


message2 = tk.Label(window, text="" ,fg="brown"   ,bg="pink",activeforeground = "green",width=30  ,height=2  ,font=('arial', 15, ' bold '))
message2.place(x=700, y=600)

def clear():
    txt.delete(0, 'end')
    res = ""
    message.configure(text= res)

def clear2():
    txt2.delete(0, 'end')
    res = ""
    message.configure(text= res)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

def TakeImages():
    Id=(txt.get())
    name=(txt2.get())
    if(is_number(Id) and name.isalpha()):
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector=cv2.CascadeClassifier(harcascadePath)
        sampleNum=0
        while(True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                #incrementing sample number
                sampleNum=sampleNum+1
                #saving the captured face in the dataset folder TrainingImage
                cv2.imwrite("TrainingImage\ "+name +"."+Id +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
                #display the frame
                cv2.imshow('frame',img)
            #wait for 100 miliseconds
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # break if the sample number is morethan 100
            elif sampleNum>60:
                break
        cam.release()
        cv2.destroyAllWindows()
        res = "Images Saved for ID : " + Id +" Name : "+ name
        row = [Id , name]
        with open('StudentDetails\StudentDetails.csv','a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        message.configure(text= res)
    else:
        if(is_number(Id)):
            res = "Enter Alphabetical Name"
            message.configure(text= res)
        if(name.isalpha()):
            res = "Enter Numeric Id"
            message.configure(text= res)

def TrainImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()#recognizer = cv2.face.LBPHFaceRecognizer_create()#$cv2.createLBPHFaceRecognizer()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector =cv2.CascadeClassifier(harcascadePath)
    faces,Id = getImagesAndLabels("TrainingImage")
    recognizer.train(faces, np.array(Id))
    recognizer.save("TrainingImageLabel")
    res = "Image Trained"#+",".join(str(f) for f in Id)
    message.configure(text= res)

def getImagesAndLabels(path):
    #get the path of all the files in the folder
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)]
    #print(imagePaths)

    #create empth face list
    faces=[]
    #create empty ID list
    Ids=[]
    #now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        #loading the image and converting it to gray scale
        pilImage=Image.open(imagePath).convert('L')
        #Now we are converting the PIL image into numpy array
        imageNp=np.array(pilImage,'uint8')
        #getting the Id from the image
        Id=int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        Ids.append(Id)
    return faces,Ids

def TrackImages():
    recognizer = cv2.face.LBPHFaceRecognizer_create()#cv2.createLBPHFaceRecognizer()
    recognizer.read("TrainingImageLabel")
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath);
    df=pd.read_csv("StudentDetails\StudentDetails.csv")
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names =  ['Id','Name','Date','Time']
    attendance = pd.DataFrame(columns = col_names)
    while True:
        ret, im =cam.read()
        gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        faces=faceCascade.detectMultiScale(gray, 1.2,5)
        for(x,y,w,h) in faces:
            cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
            Id, conf = recognizer.predict(gray[y:y+h,x:x+w])
            if(conf < 40):
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%y')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa=df.loc[df['Id'] == Id]['Name'].values
                tt=str(Id)+"-"+aa
                attendance.loc[len(attendance)] = [Id,aa,date,timeStamp]

            else:
                Id='Unknown'
                tt=str(Id)
            if(conf > 45):
                noOfFile=len(os.listdir("ImagesUnknown"))+1
                cv2.imwrite("ImagesUnknown\Image"+str(noOfFile) + ".jpg", im[y:y+h,x:x+w])
            cv2.putText(im,str(tt),(x,y+h), font, 1,(255,255,255),2)
        attendance=attendance.drop_duplicates(subset=['Id'],keep='first')
        cv2.imshow('im',im)
        if (cv2.waitKey(1)==ord('q')):
            break
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%y')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour,Minute,Second=timeStamp.split(":")
    fileName="Attendance\Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"
    attendance.to_csv(fileName,index=False)
    cam.release()
    cv2.destroyAllWindows()
    #print(attendance)
    res=attendance
    message2.configure(text= res)







clearButton = tk.Button(window, text="Clear", command=clear  ,fg="brown"  ,bg="pink"  ,width=20  ,height=2 ,activebackground = "brown" ,font=('times', 15, ' bold '))
clearButton.place(x=960, y=150)
clearButton2 = tk.Button(window, text="Clear", command=clear2  ,fg="brown"  ,bg="pink"  ,width=20  ,height=2, activebackground = "brown" ,font=('times', 15, ' bold '))
clearButton2.place(x=960, y=250)
takeImg = tk.Button(window, text="Take Images", command=TakeImages  ,fg="brown"  ,bg="pink" ,width=20  ,height=2, activebackground = "brown" ,font=('times', 15, ' bold '))
takeImg.place(x=200, y=450)
trainImg = tk.Button(window, text="Train Images", command=TrainImages  ,fg="brown"  ,bg="pink"  ,width=20  ,height=2, activebackground = "brown" ,font=('times', 15, ' bold '))
trainImg.place(x=500, y=450)
trackImg = tk.Button(window, text="Track Images", command=TrackImages  ,fg="brown"  ,bg="pink"  ,width=20  ,height=2, activebackground = "brown" ,font=('times', 15, ' bold '))
trackImg.place(x=800, y=450)
quitWindow = tk.Button(window, text="Quit", command=window.destroy  ,fg="brown"  ,bg="pink"  ,width=20  ,height=2, activebackground = "brown" ,font=('times', 15, ' bold '))
quitWindow.place(x=1100, y=450)
copyWrite = tk.Text(window, background=window.cget("background"), borderwidth=0,font=('times', 30, 'italic bold underline'))
copyWrite.tag_configure("superscript", offset=10)
copyWrite.insert("insert", "Developed by Ashish","", "TEAM", "superscript")
copyWrite.configure(state="disabled",fg="red"  )
copyWrite.pack(side="left")
copyWrite.place(x=800, y=750)

window.mainloop()
