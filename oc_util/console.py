import shutil
import os
import cv2
from collections import deque
import sys
from glob import glob
import re


def put_text(img, up, down, right, left):
    collor = (0, 255, 140)
    if up is not None:
        up = os.path.basename(up)
        cv2.putText(img, f'Up:{up}', (10, 60),cv2.FONT_HERSHEY_PLAIN, 4, collor, 4, cv2.LINE_AA)
    
    if down is not None:
        down = os.path.basename(down)
        cv2.putText(img, f'Right:{down}', (10, 130),cv2.FONT_HERSHEY_PLAIN, 4, collor, 4, cv2.LINE_AA)
    
    if right is not None:
        right = os.path.basename(right)
        cv2.putText(img, f'Down:{right}', (10, 190),cv2.FONT_HERSHEY_PLAIN, 4, collor, 4, cv2.LINE_AA)
    
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
   

