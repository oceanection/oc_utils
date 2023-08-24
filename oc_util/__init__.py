import os
import sys
import uuid
import re
import shutil
import typing
from glob import glob
from  collections import deque

import cv2
import numpy as np
from PIL import Image

def rename_data(dir_path, ext='jpg'):
    """フォルダ内のjpegファイル名を変更する。1から連番で変更する。
    Args:
        dir_path (str) : フォルダパス
        ext (str): 拡張子タイプ
    Returns:
        None
    """
    rn = 1
    ls = glob(f'{dir_path}/*.{ext}')
    for file in ls:
        os.rename(file, f'{dir_path}/{str(rn)}.{ext}')

def delete_duplicate_jpg_files(dir_path:str, r=False):
    """フォルダ内の同一画像を削除する
    Args:
        dir_path (str):
        r (bool): 一つ下の階層フォルダに保存された画像を対象にする
    """
    def _delete(ls):
        num_files = len(ls)

        ls = [(l, os.path.getsize(l)) for l in ls]
        ls = sorted(ls, key=lambda x: x[1])
        
        count = 1
        d_count = 0
        e_count = 0
        try:
            for i in range(len(ls)):
                print(f'\r{count} / {num_files}: delete {d_count}, error {e_count}', end='')
                try:
                    img1 = Image.open(ls[i][0])
                    img2 = Image.open(ls[i+1][0])
                    img1_np = np.array(img1)
                    img2_np = np.array(img2)
                    count += 1
                    if np.array_equal(img1_np, img2_np):
                        os.remove(ls[i][0])
                        d_count += 1
                except:
                    print(f'\r{count} / {num_files}: delete {d_count}, error {e_count}', end='')
                    os.remove(ls[i][0])
                    e_count += 1                
        except IndexError:
            print('')
        
    if r:
        dirs = [d for d in glob(f'{dir_path}/*') if os.path.isdir(d)]
                
        ls = []
        for i in dirs:
            d = glob(f'{i}/*.jpg')
            ls += d
        _delete(ls)

    else:
        ls = glob(f'{dir_path}/*.jpg')
        _delete(ls)
        

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

def img_rotate(path, size=300, direction='v'):
    """
    """
    img = Image.open(path)
    width, height = img.size
    
    print(f'width: {width}, height: {height}')
    
    if direction == 'v':
        if width == size:
            img_r = img.rotate(90)
            img_r.save(path)
        else:
            pass
    elif direction == 'h':
        if width == size:
            pass
        else:
            img_r = img.rotate(90)
            img_r.save(path)
    else:
        pass


def collect_v(dir_path, save_path):
    pass



def save_data(dir_path:str, data, dtype='fp', ext='jpg',filename='', dir_name='data', limit=10000):
    """指定のフォルダ内にJPGファイルなどをコピーする。下位フォルダを作成し、上限ファイル数を超えた場合には新たなフォルダを作成する。

    Arg:
        dir_path (str): 保存先フォルダパス
        data (Any): コピーするデータ
        dtype (str): dataの種類。ファイルパス'fp'、 バイナリデータ'b'、Pllow'plw'.
        ext (str): 拡張子. 初期値はファイルパス'fp'
        filename (str): ファイル名
        dir_name (str): 下位フォルダの名前. 初期値は'data'
        limit (int): 下位フォルダの保存上限数
    Returns:
        detail_dir_path (str): 保存先下位フォルダパス
    """  
    def _save(data, dtype, name, path, ext):
        if dtype == 'plw':
            data.save(f'{path}/{name}.{ext}')
            return path
        elif dtype == 'b':
            with open(f'{path}/{name}.{ext}', 'wb') as f:
                f.write(data)
            return path
        elif dtype == 'fp':
            shutil.copy(data, f'{path}/{name}.{ext}')
            return path

    # 保存先フォルダの検索
    dirs = glob(f'{dir_path}/{dir_name}_*')
    
    # ファイル名
    if filename == '':
        filename = uuid.uuid4()
    
    if len(dirs) == 0:
        os.mkdir(f'{dir_path}/{dir_name}_1')
        detail_dir_path = f'{dir_path}/{dir_name}_1'
        detail_dir_path = _save(data, dtype, filename, detail_dir_path, ext)
        return detail_dir_path
        
    else:
        # 保存先フォルダの並べかえ（昇順）
        dirs = [[int(d.split('_')[-1]), d] for d in glob(f'{dir_path}/{dir_name}_*')]
        dirs = sorted(dirs, key=lambda x: x[0])
        dirs = [d[1] for d in dirs] 
       
        detail_dir_path = dirs[-1]
        files = glob(f'{detail_dir_path}/*.{ext}')
        
        name_count = 1
        if f'{detail_dir_path}/{filename}.{ext}' in files:
            old_filename = filename
            while f'{detail_dir_path}/{filename}.{ext}' in files:
                name_count += 1
                filename = f'{filename}({str(name_count)})'
            filename = f'{old_filename}({str(name_count)})'
        
        if len(files) <= limit:
            detail_dir_path = _save(data, dtype, filename, detail_dir_path, ext)
            return detail_dir_path
        else:
            last_num = int(detail_dir_path.split('_')[-1])
            os.mkdir(f'{dir_path}/{dir_name}_{last_num+1}')
            detail_dir_path = f'{dir_path}/{dir_name}_{last_num+1}'
            detail_dir_path = _save(data, dtype, filename, detail_dir_path, ext)
            return detail_dir_path


def is_png(b: bytes) -> bool:
    """バイナリの先頭部分からPNGファイルかどうかを判定する。"""
    return bool(re.match(b"^\x89\x50\x4e\x47\x0d\x0a\x1a\x0a", b[:8]))

def is_jpg(b: bytes) -> bool:
    """バイナリの先頭部分からJPEGファイルかどうかを判定する。"""
    return bool(re.match(b"^\xff\xd8", b[:2]))

def is_gif(b: bytes) -> bool:
    """バイナリの先頭部分からGIFファイルかどうかを判定する。"""
    return bool(re.match(b"^\x47\x49\x46\x38", b[:4]))

def is_pdf(b: bytes) -> bool:
    """バイナリの先頭部分からPDFファイルかどうかを判定する。"""
    return bool(re.match(b"^%PDF", b[:4]))

def is_bmp(b: bytes) -> bool:
    """バイナリの先頭部分からWindows Bitmapファイルかどうかを判定する。"""
    return bool(re.match(b"^\x42\x4d", b[:2]))

def put_text(img, up, down, right, left):
    collor = (0, 255, 140)
    if up is not None:
        up = os.path.basename(up)
        cv2.putText(img, f'Up:{up}', (10, 60),cv2.FONT_HERSHEY_PLAIN, 4, collor, 4, cv2.LINE_AA)
    
    if down is not None:
        down = os.path.basename(down)
        cv2.putText(img, f'Right:{right}', (10, 130),cv2.FONT_HERSHEY_PLAIN, 4, collor, 4, cv2.LINE_AA)
    
    if right is not None:
        right = os.path.basename(right)
        cv2.putText(img, f'Down:{down}', (10, 190),cv2.FONT_HERSHEY_PLAIN, 4, collor, 4, cv2.LINE_AA)
    
    if left is not None:
        left = os.path.basename(left)
        cv2.putText(img, f'Down:{left}', (10, 250),cv2.FONT_HERSHEY_PLAIN, 4, collor, 4, cv2.LINE_AA)


def img_console(dir_path:str, up_key=None, down_key=None, left_key=None, right_key=None):
    """フォルダ内の画像を１枚ずつ表示して、不要な画像を削除。
    ↑↓→←のキーで指定のフォルダに画像をコピーする。
    Enterで次の画像、Bキーで戻る。
    Dキー、バックスペースキーで画像を削除
    Qキーで終了
    
    Args:
        dir_path (str):
        up_key (str):
        down_key (str):
        left_key (str):
        right_key (str):
        copy (bool):
    Returns:
    """
    if not os.path.exists(dir_path):
        return

    filelist  = deque([d for d in glob(f'{dir_path}/*') if os.path.isfile(d) and re.search('\.(jpg|png)$', d)])
    done_filelist = deque()
    while len(filelist) > 0:
        filepath = filelist.popleft()
      
        print('now: ', filepath)
        
        img = cv2.imread(filepath)
        put_text(img, up_key, down_key, right_key, left_key)
        cv2.imshow('image', img)
        
        key = cv2.waitKey(0)
        if key == ord('q'):
            # 'q' key
            cv2.destroyAllWindows()
            sys.exit()
        elif key == 13:
            # Enter key
            done_filelist.append(filepath)
        elif key == ord('b'):
            # 'b' key
            if len(done_filelist) > 0:
                filelist.appendleft(filepath)
                previous_filepath = done_filelist.pop()
                filelist.appendleft(previous_filepath)
                continue
            else:
                filelist.appendleft(filepath)
        elif key == ord('d') or key == 127:
            # 'd' key
            os.remove(filepath)
            continue
        elif key == 0:
            # Up key
            if up_key is not None:
                shutil.copy2(filepath, up_key)
                done_filelist.append(filepath) 
            continue
        elif key == 1:
            # Down Key
            if down_key is not None:
                shutil.copy2(filepath, down_key)
                done_filelist.append(filepath)
            continue
        elif key == 2:
            # Left Key
            if left_key is not None:
                shutil.copy2(filepath, left_key)
                done_filelist.append(filepath)
            continue
        elif key == 3:
            # Right key
            if right_key is not None:
                shutil.copy2(filepath, right_key)
                done_filelist.append(filepath)
            continue
        else:
            # Other
            filelist.appendleft(filepath)
            continue
    
    cv2.destroyAllWindows()
   

