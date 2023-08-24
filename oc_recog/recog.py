from PIL import Image
import face_recognition
import os
from glob import glob


def delete_no_person_jpg_files(directory_path):
    """顔認識できないJPEGファイルを削除する
    
    Args:
        directory_path (str): フォルダパス
    Returns:
        None:
    """  
    def _delete_image(file_path):
        os.remove(file_path)
    jpg_filenames = glob(f'{directory_path}/*.jpg')
    num_files = len(jpg_filenames)
    count = 1
    d_count = 0
    for filename in jpg_filenames:
        print(f'\r\r{count} / {num_files},  delete {d_count}', end='')
        count += 1
        try:
            # 顔認識
            image = face_recognition.load_image_file(filename)
            face_locations = face_recognition.face_locations(image)

            if len(face_locations) == 0:        
                _delete_image(filename)
                d_count += 1
                
        except Exception as e:
            print('ERROR')
            print(e)

def recognition(files_path, save_dir):
    """顔画像を抽出して保存する。抽出に成功した画像は削除される
    
    Args:
        files_path (List[str,]): 
        save_dir (str)
    Returns:
        None:
    """
    for file_path in files_path:
        print(f'Image: {file_path}') 
        try:      
            # 顔認識
            image = face_recognition.load_image_file(file_path)
            face_locations = face_recognition.face_locations(image)
            
            # 画像サイズ
            width, height = Image.open(file_path).size
            
            # 顔画像切り抜き
            rn = 1
            for face_location in face_locations:
                top, right, bottom, left = face_location
                
                # 
                t, r, b, l = 30, 30, 30, 30
                while ((top - t) < 0):
                    t -= 1
                while ((bottom + b) > height):
                    b -= 1
                while ((left - l) < 0):
                    l -= 1
                while ((right + r) > width):
                    r -=1
                face_image = image[top-t:bottom+b, left-l:right+r]
                pil_image = Image.fromarray(face_image)
                
                # 保存
                file_name = os.path.join(save_dir, f'r_{str(rn)}.jpg')
                while (os.path.exists(file_name)):
                    rn += 1
                    file_name = os.path.join(save_dir, f'r_{str(rn)}.jpg')
                
                pil_image.save(file_name)
                os.remove(file_path)
        except:
            print(f'ERROR: {file_path}')
            os.remove(file_path)
            continue
