import streamlit as st
import pandas as pd
import numpy as np
import requests
import base64
import torch
import os

from torchvision import transforms
from resnet import ResNetGenerator
from savedb import truncate, save_to_temp_db, update_prod_db, connect_to_db
from urllib.parse import urlparse
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from pdf2image import convert_from_bytes

st.set_option('deprecation.showfileUploaderEncoding', False)
st.title("Zebrate app")
st.header("neural network that turns a horse into a zebra")

FILE_TYPES = ["png", "jpg", "jpeg", "pdf"]
URL = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Flifeglobe.net%2Fmedia%2Fentry%2F6445%2F1a.jpg"
horse_table = "horse_files"
zebra_table = "zebra_files"

author = """
    ---
    made with:
    * [Streamlit](https://www.streamlit.io/)
    * [Book](https://pytorch.org/assets/deep-learning/Deep-Learning-with-PyTorch.pdf)
    * [PyTorch](https://pytorch.org/)
    * [CycleGAN](https://github.com/keras-team/keras-io/blob/master/examples/generative/cyclegan.py)
    * [ResNet](https://www.res.net/)
    * [weights for model](https://github.com/deep-learning-with-pytorch/dlwpt-code/blob/master/data/p1ch2/horse2zebra_0.4.0.pth)
    * [and this dataset](http://mng.bz/8pKP)
    
    by [Dmitry Kosarevsky](https://github.com/dKosarevsky) for [TaDS labs](https://networking-labs.ru/) in [BMSTU](https://bmstu.ru)
"""


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def get_table_download_link(tensor):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    tensor_np = tensor.numpy()
    df = pd.concat([pd.DataFrame(x) for x in tensor_np], keys=np.arange(tensor_np.shape[2]))
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="horse_tensor.xlsx">Download tensor</a>' # decode b'abc' => abc


def get_image_download_link(img, is_zebra=False):
    """Generates a link allowing the PIL image to be downloaded
    in:  PIL image
    out: href string
    """
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    subgenus = "zebra" if is_zebra else "horse"
    href = f'<a href="data:file/jpg;base64,{img_str}">Download {subgenus}</a>'
    return href


def uploader(file):
    """
    function for upload image from user
    return file object
    """
    show_file = st.empty()
    if not file:
        show_file.info("valid file extension: " + ", ".join(FILE_TYPES))
        return False

    return file


def prepare_model():
    """
    function for prepare generative model
    return model and preprocess
    """
    netG = ResNetGenerator()

    model_path = './horse2zebra_0.4.0.pth'
    model_data = torch.load(model_path)
    netG.load_state_dict(model_data)

    netG.eval()
    # st.code(netG.eval())

    preprocess = transforms.Compose([transforms.Resize(256), transforms.ToTensor()])

    return netG, preprocess


def img_to_bin(im):
    """
    function for encode image ti binary
    return binary object
    """
    buffered = BytesIO()
    im.save(buffered, format="PNG")
    bin_im = base64.b64encode(buffered.getvalue())
    return bin_im


def generate_zebra(net_G, preprocess, user_img, user_url, base_url, db_conn):
    """
    function for generate zebra from horse-tensor
    return image of zebra
    """
    if user_img:
        try:
            img = Image.open(user_img)
        except UnidentifiedImageError:
            img = convert_from_bytes(user_img.read(), fmt='jpeg')[0]
    else:
        response = requests.get(user_url if user_url else base_url)
        try:
            img = Image.open(BytesIO(response.content))
        except UnidentifiedImageError:
            st.write('Something went wrong ... Try another link, or upload an image from your local device')
            st.stop()

    st.write("We take a random horse :racehorse: ")

    img_bin = img_to_bin(img)
    truncate(horse_table, db_conn)
    save_to_temp_db(img_bin, horse_table, db_conn)
    update_prod_db(horse_table, db_conn)

    # TODO push horse to tg
    st.image(img)
    st.markdown(get_image_download_link(img), unsafe_allow_html=True)

    img_t = preprocess(img)
    batch_t = torch.unsqueeze(img_t, 0)

    batch_out = net_G(batch_t)

    out_t = (batch_out.data.squeeze() + 1.0) / 2.0
    out_img = transforms.ToPILImage()(out_t)

    st.write("We drive the horse into tensor ... it's not a stall :grin:, it's such a multidimensional matrix")
    if st.checkbox("Show me the horse tensor"):
        st.code(img_t)
        st.markdown(get_table_download_link(img_t), unsafe_allow_html=True)

    st.write("Then there is a battle of generative adversarial networks ...")

    return out_img


def validate_url(url):
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            return url
        elif not url:
            return False
        else:
            st.sidebar.markdown("<font color='red'>it doesn't look like a picture link</font>", unsafe_allow_html=True)
            return False
    except AttributeError:
        return False


def main():
    horse_url = validate_url(st.text_input("Put the link to the horse picture here: "))
    net, preproc = prepare_model()
    img_file = uploader(st.file_uploader("Upload your horse image:", type=FILE_TYPES))
    db_connection = connect_to_db()
    zebra = generate_zebra(net, preproc, img_file, horse_url, URL, db_connection)
    img_bin = img_to_bin(zebra)
    truncate(zebra_table, db_connection)
    save_to_temp_db(img_bin, zebra_table, db_connection)
    update_prod_db(zebra_table, db_connection)
    # TODO push zebra to tg

    st.write("... and the horse turns into a zebra")

    st.image(zebra)
    st.markdown(get_image_download_link(zebra, is_zebra=True), unsafe_allow_html=True)

    st.sidebar.markdown("# Zebrate")
    st.sidebar.markdown(author)


if __name__ == "__main__":
    main()
