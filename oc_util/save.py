import os
import shutil
import uuid
from glob import glob


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
