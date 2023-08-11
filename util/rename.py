import os

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
            
        
if __name__ == '__main__':
    dir_path = os.path.join(os.getenv("HOME"), 'Pictures', 'sample')
    rename()