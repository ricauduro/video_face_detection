import cv2
import requests
import time
import json

cam = cv2.VideoCapture(0)

path = "Path where you saved your json file with your key"

credential = json.load(open(path))
KEY = credential['KEY']

while True:
    ret, frame = cam.read()
    # cv2.imshow('frame', frame)

    if cv2.waitKey(1)%256 == 27:
        break

    image = cv2.imencode('.jpg', frame)[1].tobytes()
    
    face_api_url = "https://eastus.api.cognitive.microsoft.com/face/v1.0/detect"
    headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': KEY}
    params = {'detectionModel': 'detection_01', 'returnFaceId': 'true', 'returnFaceRectangle': 'true', 'returnFaceAttributes': 'age, gender, emotion'}

    response = requests.post(face_api_url, params=params, headers=headers, data=image)
    
    response.raise_for_status()
    faces = response.json()
    print(faces)

    for face in faces:
        rect = face['faceRectangle']
        left = rect['left']
        top = rect['top']
        right = int(rect['width']) + int(rect['left'])
        bottom = int(rect['height']) + int(rect['top'])

        draw = cv2.rectangle(frame,(left, top), (right, bottom),(0, 255, 0), 3)

        att = face['faceAttributes']
        age = att['age']

        draw = cv2.putText(draw, 'Age: ' + str(age), (left, bottom + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        
    cv2.imshow('face_rect', draw)
    time.sleep(3)

cam.release()
cv2.destroyAllWindows()
