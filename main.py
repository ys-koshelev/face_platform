import face_recognition
from utils import running_on_jetson_nano, get_jetson_gstreamer_source
#from numpy import save as npsave
import numpy as np
import cv2
import glob

def encode_face(path_to_photos, path_to_save_encoding):
    photos_list = glob.glob(path_to_photos + '/*.jpg')
    
    gen_encoding = 0
    num_faces = 0
    for photo_path in photos_list:
        frame = cv2.imread(photo_path)
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        if len(face_encodings) == 1:
            gen_encoding += face_encodings[0]
            num_faces += 1
    if num_faces != 0:
        np.save(path_to_save_encoding, gen_encoding/num_faces)
        return True
    else:
        print('Failed to encode faces, nothing was saved')
        return False
    

def compare_face_with_etalon(path_to_etalon_encoding):
    if running_on_jetson_nano():
        # Accessing the camera with OpenCV on a Jetson Nano requires gstreamer with a custom gstreamer source string
        video_capture = cv2.VideoCapture(get_jetson_gstreamer_source(), cv2.CAP_GSTREAMER)
    else:
        # Accessing the camera with OpenCV on a laptop just requires passing in the number of the webcam (usually 0)
        # Note: You can pass in a filename instead if you want to process a video file instead of a live camera stream
        video_capture = cv2.VideoCapture(0)
    
    etalon_face_encoding = np.load(path_to_etalon_encoding)
    
    ret, frame = video_capture.read()
    video_capture.release()
    cv2.destroyAllWindows()
    
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    if len(face_encodings) != 0:
        face_compares = face_recognition.compare_faces(face_encodings, etalon_face_encoding, tolerance=0.65)
        if True in face_compares:
            print(str(len(face_compares)) + ' person/persons on image, one of them is the same, as etalon')
            return True
        else:
            print(str(len(face_compares)) + ' person/persons on image, none of them is the same, as etalon')
            return False
    else:
        print('No faces were detected on camera!')
        return False
    

