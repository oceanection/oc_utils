import pytest

from oc_crawler import url_analysis, is_jpg_url, is_png_url

@pytest.mark.parametrize(('img_url', 'url', 'result'),[
    ('/img/titlemini.gif', 'https://5chan.jp/r18camera/', 'https://5chan.jp/img/titlemini.gif'),
    ('//5chan.jp/r18camera/qrcode', 'https://5chan.jp/r18camera/', 'https://5chan.jp/r18camera/qrcode'),
    ('//analyzer54.fc2.com/ana/icon.php?uid=2857848&ref=&href=&wid=0&hei=0&col=0', 'https://mabui-onna.com/blog-entry-9.html', 'https://analyzer54.fc2.com/ana/icon.php?uid=2857848&ref=&href=&wid=0&hei=0&col=0'),
    ('https://blog-imgs-143.fc2.com/g/m/8/gm8j46mpp36s/20201001001357084.jpg', 'https://mabui-onna.com/blog-entry-9.html', 'https://blog-imgs-143.fc2.com/g/m/8/gm8j46mpp36s/20201001001357084.jpg'),
])
def test_url_analysis(img_url, url, result):
    r = url_analysis(img_url, url)
    assert r == result

@pytest.mark.parametrize(('url', 'result'), [
    ('https://blog-imgs-143.fc2.com/g/m/8/gm8j46mpp36s/20201001001357084.jpg', True),
    ('/img/titlemini.gif', False),
    ('/img/titlemini.jpg/#jpg', False),
])
def test_is_jpg_url(url, result):
    assert result == is_jpg_url(url)

@pytest.mark.parametrize(('url', 'result'), [
    ('https://blog-imgs-143.fc2.com/g/m/8/gm8j46mpp36s/20201001001357084.png', True),
    ('https://mabui-onna.com/blog-entry-9.html', False),
    ('/img/titlemini.png/#png', False),
])
def test_is_png_url(url, result):
    assert result == is_png_url(url)