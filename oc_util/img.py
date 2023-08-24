from PIL import Image

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
