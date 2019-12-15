from utils import face_recognition
from numpy import save as npsave
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
        npsave(gen_encoding/len(num_faces))
        return True
    else:
        print('Failed to encode faces, nothing was saved')
        return False
    

