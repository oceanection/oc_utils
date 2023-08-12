import os
from glob import glob

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
    ls = glob(f'{dir_path}/*.jpg')
    for file in ls:
        os.rename(file, f'{dir_path}/{str(rn)}.jpg')


def delete_duplicate_jpg_files(dir_path):
    """フォルダ内の同一画像を削除する
    """
    ls = glob(f'{dir_path}/*.jpg')
    num_files = len(ls)
    
    ls = [(l, os.path.getsize(l)) for l in ls]
    ls = sorted(ls, key=lambda x: x[1])
    
    count = 1
    d_count = 0
    try:
        for i in range(len(ls)):
            print(f'\r{count} / {num_files}: delete {d_count}', end='')
            img1 = Image.open(ls[i][0])
            img2 = Image.open(ls[i+1][0])
            img1_np = np.array(img1)
            img2_np = np.array(img2)
            count += 1
            if np.array_equal(img1_np, img2_np):
                os.remove(ls[i][0])
                d_count += 1
                
    except IndexError:
        pass

def img_resize(path, size=300):
    """画像のリサイズ. 縦横比を維持する.
    
    Args:
        path (str): 画像ファイルのパス
        size (int): 指定サイズ
    """
    img = Image.open(path)
    
    # 比率計算
    w_ratio = size / img.width
    h_ratio = size / img.height

    if w_ratio < h_ratio:
        resize_size = (size, round(img.height * w_ratio))
    else:
        resize_size = (round(img.width * h_ratio), size)

    img_r = img.resize(resize_size)
    return img_r