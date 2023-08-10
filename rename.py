import os

def rename(dir_path):
    # フォルダ内のファイル名変更
    
    rn = 1
    for file in os.listdir(dir_path):
        os.rename(os.path.join(dir_path,file), os.path.join(dir_path, str(rn)+'.jpg'))
        rn += 1
        
if __name__ == '__main__':
    dir_path = os.path.join(os.getenv("HOME"),'Pictures', 'sample')
    rename()