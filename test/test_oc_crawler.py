import pytest

from oc_crawler import url_analysis, is_jpg_url, is_png_url

@pytest.mark.parametrize(('img_url', 'url', 'result'),[
    ('https://xyz.com', '//xxxx/', 'https://xyz.com')
])
def test_url_analysis(img_url, url, result):
    r = url_analysis(img_url, url)
    assert r == result

@pytest.mark.parametrize(('url', 'result'), [
    ('https://xyz/20201001001357084.jpg', True),
    ('/img/XXX.gif', False),
    ('/img/XXXX.jpg/#jpg', False),
])
def test_is_jpg_url(url, result):
    assert result == is_jpg_url(url)

@pytest.mark.parametrize(('url', 'result'), [
    ('https://xtyz.com/g/m/8/gm8j46mpp36s/20201001001357084.png', True),
    ('https://xyz.com/blog.html', False),
    ('/img/XXXX.png/#png', False),
])
def test_is_png_url(url, result):
    assert result == is_png_url(url)