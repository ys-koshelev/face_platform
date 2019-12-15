from backend import encode_face, compare_face_with_etalon, watch_face

def process_a():
    clear()
    photo_path = input('Print path to folder with photos stored for encoding')
    return encode_face(photo_path, photo_path + '/encoding')

def process_b():
    clear()
    etalon_path = input('Print path to etalon encoding')
    return compare_face_with_etalon(etalon_path)

def process_c():
    clear()
    etalon_path = input('Print path to etalon encoding')
    duration = input('Specify duration of test in minutes')
    return watch_face(etalon_path, 60*float(duration))

def clear(): 
  
    # for windows 
    if name == 'nt': 
        _ = system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 

func_dict = {'1': process_a, '2': process_b, '3': process_c}

while True:
    val = input("Choose what to test: \n \n 1) Encode face (create etalon to compare), \n 2) Shot one photo and compare it with etalon, \n 3) Contignously watch for person\n")
    func_dict[val]()