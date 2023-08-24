from glob import glob
import os
from PIL import Image
import numpy as np

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