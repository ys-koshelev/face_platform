import face_recognition
import cv2
from datetime import datetime, timedelta
import numpy as np
import platform


def save_known_faces():
    with open("known_faces.dat", "wb") as face_data_file:
        face_data = [known_face_encodings, known_face_metadata]
        pickle.dump(face_data, face_data_file)
        print("Known faces backed up to disk.")


def load_known_faces():
    global known_face_encodings, known_face_metadata

    try:
        with open("known_faces.dat", "rb") as face_data_file:
            known_face_encodings, known_face_metadata = pickle.load(face_data_file)
            print("Known faces loaded from disk.")
    except FileNotFoundError as e:
        print("No previous face data found - starting with a blank known face list.")
        pass


def running_on_jetson_nano():
    # To make the same code work on a laptop or on a Jetson Nano, we'll detect when we are running on the Nano
    # so that we can access the camera correctly in that case.
    # On a normal Intel laptop, platform.machine() will be "x86_64" instead of "aarch64"
    return platform.machine() == "aarch64"


def get_jetson_gstreamer_source(capture_width=1920, capture_height=1080, display_width=1280, display_height=720, framerate=30, flip_method=0):
    """
    Return an OpenCV-compatible video source description that uses gstreamer to capture video from the camera on a Jetson Nano
    """
    return (
            f'nvarguscamerasrc ! video/x-raw(memory:NVMM), ' +
            f'width=(int){capture_width}, height=(int){capture_height}, ' +
            f'format=(string)NV12, framerate=(fraction){framerate}/1 ! ' +
            f'nvvidconv flip-method={flip_method} ! ' +
            f'video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! ' +
            'videoconvert ! video/x-raw, format=(string)BGR ! appsink'
            )


def register_new_face(face_encoding, face_image):
    """
    Add a new person to our list of known faces
    """
    # Add the face encoding to the list of known faces
    known_face_encodings.append(face_encoding)
    # Add a matching dictionary entry to our metadata list.
    # We can use this to keep track of how many times a person has visited, when we last saw them, etc.
    known_face_metadata.append({
        "first_seen": datetime.now(),
        "first_seen_this_interaction": datetime.now(),
        "last_seen": datetime.now(),
        "seen_count": 1,
        "seen_frames": 1,
        "face_image": face_image,
    })
    return None
    
def lookup_known_face(face_encoding):
    """
    See if this is a face we already have in our face list
    """
    metadata = None

    # If our known face list is empty, just return nothing since we can't possibly have seen this face.
    if len(known_face_encodings) == 0:
        return metadata

    # Calculate the face distance between the unknown face and every face on in our known face list
    # This will return a floating point number between 0.0 and 1.0 for each known face. The smaller the number,
    # the more similar that face was to the unknown face.
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

    # Get the known face that had the lowest distance (i.e. most similar) from the unknown face.
    best_match_index = np.argmin(face_distances)

    # If the face with the lowest distance had a distance under 0.6, we consider it a face match.
    # 0.6 comes from how the face recognition model was trained. It was trained to make sure pictures
    # of the same person always were less than 0.6 away from each other.
    # Here, we are loosening the threshold a little bit to 0.65 because it is unlikely that two very similar
    # people will come up to the door at the same time.
    if face_distances[best_match_index] < 0.65:
        # If we have a match, look up the metadata we've saved for it (like the first time we saw it, etc)
        metadata = known_face_metadata[best_match_index]

        # Update the metadata for the face so we can keep track of how recently we have seen this face.
        metadata["last_seen"] = datetime.now()
        metadata["seen_frames"] += 1

        # We'll also keep a total "seen count" that tracks how many times this person has come to the door.
        # But we can say that if we have seen this person within the last 5 minutes, it is still the same
        # visit, not a new visit. But if they go away for awhile and come back, that is a new visit.
        if datetime.now() - metadata["first_seen_this_interaction"] > timedelta(minutes=5):
            metadata["first_seen_this_interaction"] = datetime.now()
            metadata["seen_count"] += 1

    return metadata