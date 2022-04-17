import requests
import cv2
import time
import re
from tkinter import *
import datetime

capture = cv2.VideoCapture()
capture.open(1,cv2.CAP_DSHOW)

base = 'https://westcentralus.api.cognitive.microsoft.com/vision/v2.0'
recog_url = f'{base}/recognizeText?mode=Printed'

key = ''
headers = {'Ocp-Apim-Subscription-Key': key}
headers_stream = {'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/octet-stream'}

def get_license(img):
    ml = ''
    img_encode = cv2.imencode('.jpg', img)[1]
    img_bytes = img_encode.tobytes()
    r1 = requests.post(recog_url, headers = headers_stream, data=img_bytes)

    if r1.status_code != 202:
        print(r1.json())
        return 'Fail request'
    result_url = r1.headers['Operation-Location']
  #  print(result_url)
    r2 = requests.get(result_url, headers = headers)

    while r2.status_code == 200 and r2.json()['status'] != 'Succeeded':
        r2 = requests.get(result_url, headers = headers)
        time.sleep(0.5)
        #print('status: ', r2.json()['status'])
    carcard = ''
    lines = r2.json()['recognitionResult']['lines']
    #print(lines)
    for i in range(len(lines)):
        text = lines[i]['text']
        ml = ml + text + " "
        m = re.match(r'^[\w]{1,2}[-. ][\w]{1,4}$', text)

        if m != None:
            carcard = m.group()
            return carcard
    if carcard == '':
        return ml.strip()

if capture.isOpened():
    while True:
        success, img =  capture.read()
        if success:
            cv2.imshow('Press S to enter carpark', img)
        k = cv2.waitKey(100)
        if k == ord('s') or k == ord('S'):
            cv2.imwrite('shot.jpg',img)
            license = get_license(img)
            window = Tk()
            window.title("Carplate Recognition")
            window.geometry("300x600")
            firstLabel = Label(window, text="Car Plate", bg="lightblue", width=30, font="Helvetica 24 bold")
            firstLabel.pack()
            carplateLabel = Label(window, text=license, bg="lightyellow", width=30, font="Helvetica 24")
            carplateLabel.pack()
            secondLabel = Label(window, text="Entry Time", bg="lightblue", width=30, font="Helvetica 24 bold")
            secondLabel.pack()
            t = datetime.datetime.now().strftime("%H:%M:%S")
            timeLabel = Label(window, text=t, bg="lightyellow", width=30, font="Helvetica 24")
            timeLabel.pack()
            thirdLabel = Label(window, text="Payment", bg="lightblue", width=30, font="Helvetica 24 bold")
            thirdLabel.pack()
            if license[0:2] == "AM":
                payLabel = Label(window, text="Free of charge", bg="lightyellow", width=30, font="Helvetica 24")
                payLabel.pack()
            else:
                payLabel = Label(window, text="Octopus", bg="lightyellow", width=30, font="Helvetica 24")
                payLabel.pack()
            btn = Button(window,text="Close", command=window.destroy)
            btn.pack()
            window.mainloop()

        if k == ord('q') or k == ord('Q'):
            print('exit')
            cv2.destroyAllWindows()
            capture.release()
            break
else:
    print('Fail to open camera')

