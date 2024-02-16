Unfortunally this service is no longer available for personal users in Azure... only for managed partners

# video face detection
Using Azure cognitive services and Python, perform face recogition / detection in real time videos.

  I always like to watch TV series, the ones related to police investigations were the best for me... and I was watching some old episodes (the date of the episodes was very close to the year 2000) and back there they already did face recognition. Then I asked myself, how can someone know how to do face recognition 20 years ago and I still don´t know how to do it? Now I´ve changed this. Using Azure congnitive services API (Free BTW) I´m training models to perform face detection  in live videos. In the next lines I´ll try to explain how to access the Azure API, create and train models. 
  
  So, let´s start.

## video face detection
  Before begining, make sure you already provisioned the face API inside your Azure account.

  Most part of the logic I got from the quick start of the MS Face Recognition service <https://learn.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts-sdk/identity-client-library?tabs=visual-studio&pivots=programming-language-python> and for Face Detection <https://westus.dev.cognitive.microsoft.com/docs/services/563879b61984550e40cbbe8d/operations/563879b61984550f30395236>. This second link is not detailed as the first one, but basically we´re going to do a POST request of the image, GET the landmarks and then draw in the screen with OpenCV.

  Let´s start with the face detection. To detect faces in real time videos, we´re going to use OpenCV (pip install opencv-python) to access our Webcam with the code

```Python
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
```

  With this code we´re initializating our camera, getting each frame and showing the results. You can learn more here <http://docs.opencv.org/modules/contrib/doc/facerec/facerec_tutorial.html>. The line "if cv2.waitKey(1)%256 == 27:" means -> Press esc to stop the loop.

  Now we´re going to transform this video into something that we can send to Azure. With CV2, we´re encoding the image into the varible image to build our POST request.

```Python

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

cam.release()
cv2.destroyAllWindows()
```

The KEY variable you can find in your Azure subscription, inside the face API

![image](https://user-images.githubusercontent.com/58055908/210178831-edfafa89-d46c-4953-81d8-5c83fb2e631e.png)

  I don´t like to let my key exposed, so create a JSON file with the value 
  
  ![image](https://user-images.githubusercontent.com/58055908/210180123-bb752be0-64b0-455e-82a2-8528e7fd0ad9.png)

  and then I´m using json.load to get the value
  
```Python
path = "Path where you saved your json file with your key"

credential = json.load(open(path))
KEY = credential['KEY']
```


  This request was built based on the documentation mentioned earlier. I´m using detection model 01 because it returns main face attributes (head pose, age, emotion, and so on) and also returns the face landmarks that I choose. In this case, I´m only retrieving age, gender and emotion, but there are a lot of options in the documentation that you can choose.
  
  The response should look like this 
  
  ![image](https://user-images.githubusercontent.com/58055908/210121144-79fed0e5-252c-4653-b635-884fd0fc1271.png)
  
  With this response we can see that our script to detect faces in live videos is working. 
  
  Now we can use these coordinates, with OpenCV, to draw the rectangle in our video.
  
  First, we´re going to comment the cv.imshow, once we want to see the video with the rectangle, not the original one. Then we can create a loop for faces variable, once we can have more than 1 face per video, and then start to set variables with the coordinates we´re receiving in the response. After we´re using cv2.rectangle method to draw the rectangle and then cv2.imshow to display the results. 
  
```Python
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
       
    cv2.imshow('face_rect', draw)
    time.sleep(3)

cam.release()
cv2.destroyAllWindows()
```
  
The result is something similar to this

![image](https://user-images.githubusercontent.com/58055908/210179678-e1292eb7-5f37-46a1-888a-ff17caf45f35.png)

I´m also using a library (time) to create a delay between the requests. As I said before, we can call the API for free, but there is a limit, as we can see below

![image](https://user-images.githubusercontent.com/58055908/210179862-d440102d-26c4-45aa-b70e-912f914e1957.png)

We can also draw the other attributes of our response, let´s get the age. Now we´re using the putText function from CV2 to insert a text in our image, you can find more about cv2.putText here (https://docs.opencv.org/4.x/d6/d6e/group__imgproc__draw.html#ga5126f47f883d730f633d74f07456c576) 

```Python
att = face['faceAttributes']
age = att['age']

draw = cv2.putText(draw, 'Age: ' + str(age), (left, bottom + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
 ```


This is  the result

![image](https://user-images.githubusercontent.com/58055908/211224038-852038b3-8270-40a3-bd6a-4536a19d3606.png)

Here the code with the age

```Python
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
```

Until here you can find the code in the face_detection.py .
