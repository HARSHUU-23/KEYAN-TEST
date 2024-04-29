from flask import Flask, request
import requests
from PIL import Image
from io import BytesIO
import easyocr
import cv2

import face_recognition
import cv2
import numpy as np
import random
import pickle
import shutil
import os
from deepface import DeepFace
import json
import pandas as pd
import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = credentials.Certificate("project-sightkraft-firebase-adminsdk-l1yxj-1cac28b00f.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def get_id_count():
  d = db.collection("ID").document("doc")
  ref = d.get().to_dict()
  print(ref["count"])
  return ref["count"]

def get_name(id):
  d = db.collection("Registration").document("dummy@gmail.com")
  ref = d.get().to_dict()
  print(ref[id]["name"])
  return str(ref[ref[id]["name"]])

app = Flask(__name__)

@app.route('/data', methods = ["POST", "GET"])
def data():
    data = request.json

    print('Received data:', data)
    folder = list(data.keys())[0]

    if not os.path.exists("image/"+folder):
        os.makedirs("image/"+folder)

    for index, url in enumerate(list(data.values())[0]):
        # url = requests.get(url).content 
        # with open(f"image/{folder}/{folder}_{index}.jpg", 'wb') as f:
        #     f.write(url) 
        response = requests.get(url).content
        image = Image.open(BytesIO(response))
        image.thumbnail((1000, 1000))

        image.save(f"image/{folder}/{folder}_{datetime.datetime.now().microsecond}.png")
    
    print("done")
    # Process the received data as needed
    return 'Data received successfully'

@app.route('/new_images', methods = ["POST", "GET"])
def new_images():
    data = request.json

    print('Received data:', data)
    folder = list(data.keys())[0]

    if not os.path.exists("image/"+folder):
        os.makedirs("image/"+folder)

    for index, url in enumerate(list(data.values())[0]):
        # url = requests.get(url).content 
        # with open(f"image/{folder}/{folder}_{index}.jpg", 'wb') as f:
        #     f.write(url) 
        response = requests.get(url).content
        image = Image.open(BytesIO(response))
        image.thumbnail((1000, 1000))

        image.save(f"image/{folder}/{folder}_{datetime.datetime.now().microsecond}.png")
    
    print("done")
    # Process the received data as needed
    return 'Data received successfully'


@app.route('/url', methods = ["POST", "GET"])
def url():
    if request.method == "POST": #if we make a post request to the endpoint, look for the image in the request body
        image_raw_bytes = request.get_data()  #get the whole body

        save_location = ("test.jpg") #save to the same folder as the flask app live in 

        f = open(save_location, 'wb') # wb for write byte data in the file instead of string
        f.write(image_raw_bytes) #write the bytes from the request body to the file
        f.close()

        print("Image saved")
        print("hii")

        return "image saved"
    
save_location = "face.jpg"
save_location_text = "text.jpg"

@app.route('/recognize', methods = ["POST", "GET"])
def recognize():
  if request.method == "POST": #if we make a post request to the endpoint, look for the image in the request body
        image_raw_bytes = request.get_data()  #get the whole body
        f = open(save_location, 'wb') # wb for write byte data in the file instead of string
        f.write(image_raw_bytes) #write the bytes from the request body to the file
        f.close()

        print("Image saved")
        try:
          result = DeepFace.find(img_path=save_location, db_path="image/")
          try:
            id = result[0]['identity'][0].split("/")[1].split("\\")[0]
            print(id)
            d = db.collection("Registration").document("dummy@gmail.com")
            ref = d.get().to_dict()
            name = ref[id]["name"]
            print(name)
            return name
          except :
            print("no match")
            return "No match found"
        except ValueError as e:
            print("Error while processing images:", e)
            return "Error while processing... Try again..."
        except Exception as e:
            print("An unexpected error occurred:", e)
            return "Error while processing... Try again..."

@app.route('/check_f', methods = ["POST", "GET"])
def check_f():
  if request.method == "POST":
         #if we make a post request to the endpoint, look for the image in the request body
        image_raw_bytes = request.get_data()  #get the whole body
        f = open(save_location, 'wb') # wb for write byte data in the file instead of string
        f.write(image_raw_bytes) #write the bytes from the request body to the file
        f.close()

        print("Image saved")
        try:
          result = DeepFace.find(img_path=save_location, db_path="image/")
          print(result)
          try:
            id = result[0]['identity'][0].split("/")[1].split("\\")[0]
            print(id)
            f_save_location = f"{id}_{datetime.datetime.now().microsecond}.png"
            os.rename(save_location,f_save_location)
            source_path = os.path.join(f_save_location)
            destination_path = os.path.join(f"image/{id}",  f_save_location)
            shutil.move(source_path, destination_path)
            return id
          except :
            print("no match")
            return "no"
        except ValueError as e:
            print("Error while processing images:", e)
            return "Error while processing... Try again..."
        except Exception as e:
            print("An unexpected error occurred:", e)
            return "Error while processing... Try again..."
        
@app.route('/read_text', methods = ["POST", "GET"])
def read_text():
    if request.method == "POST": #if we make a post request to the endpoint, look for the image in the request body
        image_raw_bytes = request.get_data()  #get the whole body
        f = open(save_location_text, 'wb') # wb for write byte data in the file instead of string
        f.write(image_raw_bytes) #write the bytes from the request body to the file
        f.close()
        print("Image saved")

        img = cv2.imread(save_location_text)
        reader = easyocr.Reader(['en'])
        result = reader.readtext(img)
        result.sort(key=lambda x: (x[0][2][1] - x[0][0][1]) * (x[0][2][0] - x[0][0][0]), reverse=True)
        threshold_area = (result[0][0][2][1] - result[0][0][0][1]) * (result[0][0][2][0] - result[0][0][0][0]) * 0.8
        large_boxes = [bbox for bbox, _, _ in result if (bbox[2][1] - bbox[0][1]) * (bbox[2][0] - bbox[0][0]) > threshold_area]
        extracted_text = ""
        for bbox in large_boxes:
            for item in result:
                if item[0] == bbox:
                    extracted_text += item[1] + " "
                    break

        print("Extracted Text:", extracted_text)
        return extracted_text

app.run(host='0.0.0.0', port= 8090)

# keys = fetch_data()
# # delete_entry(known_encodings_path, keys)

# s = "https://firebasestorage.googleapis.com/v0/b/project-sightkraft.appspot.com/o/WhatsApp%20Image%202024-04-14%20at%2012.59.02%20PM.jpeg?alt=media&token=fa729e9f-aa75-4985-93ed-638b1220b263"
# url = requests.get(s).content 
# f = open(image_name,'wb') 
# f.write(url) 
# f.close()
# # name = recognize_with_keys(known_encodings_path, image_name, keys)
# # print(name)
# result = enroll(known_encodings_path, "unknown", image_name, s)
# print(result)

# data = {'1': ['https://firebasestorage.googleapis.com/v0/b/project-sightkraft.appspot.com/o/1%2F1000026975.jpg?alt=media&token=982b366c-611b-4cd8-aff6-6e71647df851', 
#               'https://firebasestorage.googleapis.com/v0/b/project-sightkraft.appspot.com/o/1%2F1000026974.jpg?alt=media&token=d9f7a76b-6c2a-4fa7-9a84-31f8d28481a2', 
#               'https://firebasestorage.googleapis.com/v0/b/project-sightkraft.appspot.com/o/1%2F1000026973.jpg?alt=media&token=5d1cf202-1d0e-4026-8585-6a4a467e5b89', 
#               'https://firebasestorage.googleapis.com/v0/b/project-sightkraft.appspot.com/o/1%2F1000026970.jpg?alt=media&token=d9180c03-9340-4050-83d7-e2a2a42122d8', 
#               'https://firebasestorage.googleapis.com/v0/b/project-sightkraft.appspot.com/o/1%2F1000026967.jpg?alt=media&token=5d1380ad-74ec-428f-9eb8-ff590f8df766']}

# try:
#   result = DeepFace.find(img_path="face.jpg", db_path="image/")
#   try:
#     id = result[0]['identity'][0].split("/")[1].split("\\")[0]
#     print(id)
#     d = db.collection("Registration").document("dummy@gmail.com")
#     ref = d.get().to_dict()
#     print(ref[id]["name"])
#   except Exception as e:
#     print("no match", e)
# except ValueError as e:
#     print("Error while processing images:", e)
# except Exception as e:
#     print("An unexpected error occurred:", e)

# print(datetime.datetime.now().microsecond)