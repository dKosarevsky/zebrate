import pytest
import pytest_check as check

from zebrate import validate_url, uploader, generate_zebra, prepare_model, URL
from savedb import connect_to_db

from PIL import Image

GOOD_URLS = [
    "https://images.pexels.com/photos/52500/horse-herd-fog-nature-52500.jpeg",  # bad tensor!
    "https://api.time.com/wp-content/uploads/2015/08/horse-smile.jpg?w=1004&quality=85",
    "https://www.avso.org/wp-content/uploads/files/6/0/8/13-beautiful-horses-in-the-wild-nature-7-608.jpg",
    "https://media.gq.com/photos/56e71c0b14cbe0637b261d7f/16:9/w_2560%2Cc_limit/horseinsuit2.jpg",
    "https://images.pexels.com/photos/4204391/pexels-photo-4204391.jpeg",
    "https://i0.wp.com/www.horsetalk.co.nz/wp-content/uploads/2016/08/shiny-coat-stock.jpg?w=800&ssl=1",
    "https://wl-brightside.cf.tsp.li/resize/728x/JPG/113/847/52e3a95feabf4a5187d28ddc66.JPG",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcQY_mtcP5x2O9Xg5KuOywqQQTvCGArNuXoIUA&usqp=CAU",
]

BAD_URLS = [
    "data:image/cXHRgXFxUcSo0pHj2yVDfh2UqX",
    "some/bad/url",
    "some text and not a link at all",
    "zebrate.herapp.com",
    "external-content.duckduckgo.com/iu/?u=%3A%2F%2Ftse4.mm.bing.net%2Fth%3Fid%3DOIP.1fL9kvj1PnPQHaEK%26pid%3DApi&f=1",
    "%3A%2F%2Ftse4.mm.bing.net%2Fth%3Fid%3DOIP.5SGUBFb9su1fL9kvj1PnPQHaEK%26pid%3DApi&f=1",
    "1234567890",
    "qwerty",
    # "https://www.carolinaequinehospital.com/wp-content/uploads/2019/07/26717864661_b25b611eb1_o-768x510.jpg",
    # ^^ UnidentifiedImageError: cannot identify image file <_io.BytesIO object at 0x7f4bf51c3360> ^^
]

EXTENSIONS_URLS = [
    "https://images.pexels.com/photos/52500/horse-herd-fog-nature-52500.{}",  # bad tensor!
    "https://api.time.com/wp-content/uploads/2015/08/horse-smile.{}?w=1004&quality=85",
    "https://www.avso.org/wp-content/uploads/files/6/0/8/13-beautiful-horses-in-the-wild-nature-7-608.{}",
    "https://media.gq.com/photos/56e71c0b14cbe0637b261d7f/16:9/w_2560%2Cc_limit/horseinsuit2.{}",
    "https://images.pexels.com/photos/4204391/pexels-photo-4204391.{}",
    "https://i0.wp.com/www.horsetalk.co.nz/wp-content/uploads/2016/08/shiny-coat-stock.{}?w=800&ssl=1",
    "https://wl-brightside.cf.tsp.li/resize/728x/JPG/113/847/52e3a95feabf4a5187d28ddc66.{}",
    "https://encrypted-tbn0.gstatic.com/images.{}",
]

VALID_EXTENSIONS = ["jpeg", "jpg", "png", "pdf"]

INVALID_EXTENSIONS = ["mpeg4", "txt", "mp3"]

NUMS = [0., 8., 5.5, 100., 999.]


def test_generate_zebra():
    db_connection = connect_to_db()
    net, preprocess = prepare_model()
    zebra = generate_zebra(net, preprocess, None, None, URL, db_connection)

    assert type(zebra) == Image.Image
    assert isinstance(zebra, Image.Image)


def test_uploader():
    check.is_true(uploader("011010010110110101100111"), "True, it's a file")
    check.is_false(uploader(0), "False, NOT file")


def test_url_validator(good_url, bad_url, numbers):
    check.is_true(validate_url(good_url), "True, url is real")
    check.is_false(validate_url(bad_url), "False, NOT url")
    check.is_false(validate_url(""), "False, url is absent")
    check.is_false(validate_url(numbers), "False, AttributeError")


def test_url_http(good_url, bad_url):
    url = "https://media.istockphoto.com/photos/no-better-adventure-buddy-picture-id1265024528"
    validated_url = validate_url(url)
    assert good_url != validated_url
    check.is_in("http", good_url, "Is http in the url")
    check.is_not_in("http", bad_url, "make sure http isn't in url")


def test_valid_extension(valid_extension, extension_url):
    check.is_in(valid_extension, extension_url.format(valid_extension), "Is extension in the url")


def test_invalid_extension(invalid_extension, valid_extension, extension_url):
    check.is_not_in(invalid_extension, extension_url.format(valid_extension), "Is extension NOT in url")


@pytest.fixture(params=GOOD_URLS)
def good_url(request):
    """
    Fixtures with parameters will run once per param
    in params list of good urls
    """
    yield request.param


@pytest.fixture(params=BAD_URLS)
def bad_url(request):
    yield request.param


@pytest.fixture(params=EXTENSIONS_URLS)
def extension_url(request):
    yield request.param


@pytest.fixture(params=VALID_EXTENSIONS)
def valid_extension(request):
    yield request.param


@pytest.fixture(params=INVALID_EXTENSIONS)
def invalid_extension(request):
    yield request.param


@pytest.fixture(params=NUMS)
def numbers(request):
    yield request.param
