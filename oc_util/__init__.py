import os

import numpy as np
from PIL import Image

def rename_jpg(dir_path):
    """フォルダ内のjpegファイル名を変更する。1から連番で変更する。
    Args:
        dir_path (str) :
    Returns:
        None
    """
    rn = 1
    for file in os.listdir(dir_path):
        if (file.find(('.jpg')) != -1):
            os.rename(os.path.join(dir_path,file), os.path.join(dir_path, str(rn)+'.jpg'))
            rn += 1
        else:
            os.rename(os.path.join(dir_path,file), os.path.join(dir_path, file))

def delete_duplicate_jpg_files(dir_path):
    """フォルダ内の同一画像を削除する
    """
    ls = [(os.path.join(dir_path, l), os.path.getsize(os.path.join(dir_path, l))) for l in os.listdir(dir_path) if l.find('.jpg') != -1]
    ls = sorted(ls, key=lambda x: x[1])
    
    num_files = len(ls)
    count = 1
    d_count = 0
    try:
        for i in range(len(ls)):
            print(f'\r {count} / {num_files}: delete {d_count}', end='')
            img1 = Image.open(ls[i][0])
            img2 = Image.open(ls[i+1][0])
            img1_np = np.array(img1)
            img2_np = np.array(img2)
            if np.array_equal(img1_np, img2_np):
                os.remove(ls[i][0])
                d_count += 1
                
    except IndexError:
        pass
    
    print("================================================================")
    print(f'{count} / {num_files}')
    print(f'Delete {d_count} files.')
    print("================================================================")