from glob import glob
import os

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