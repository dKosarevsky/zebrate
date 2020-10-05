import streamlit as st

import requests

import torch

from torchvision import transforms

from resnet import ResNetGenerator
from savedb import truncate, save_to_temp_db, update_prod_db

from PIL import Image
from io import BytesIO

import base64

st.set_option('deprecation.showfileUploaderEncoding', False)
st.title("Zebrate app")
st.header("neural network that turns a horse into a zebra")

FILE_TYPES = ["png", "jpg", "jpeg"]
URL = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Flifeglobe.net%2Fmedia%2Fentry%2F6445%2F1a.jpg"
horse_table = "horse_files"
zebra_table = "zebra_files"


def uploader():
    """function for upload images"""
    file = st.sidebar.file_uploader("Upload your horse image:", type=FILE_TYPES)
    show_file = st.sidebar.empty()
    if not file:
        show_file.info("Upload a file of type: " + ", ".join(FILE_TYPES))
        return

    return file


def prepare_model():
    netG = ResNetGenerator()

    model_path = './horse2zebra_0.4.0.pth'
    model_data = torch.load(model_path)
    netG.load_state_dict(model_data)

    netG.eval()
    # st.code(netG.eval())

    preprocess = transforms.Compose([transforms.Resize(256), transforms.ToTensor()])

    return netG, preprocess


def img_to_bin(im):
    buffered = BytesIO()
    im.save(buffered, format="PNG")
    bin_im = base64.b64encode(buffered.getvalue())
    return bin_im


def generate_zebra(net_G, preprocess, user_img, user_url, base_url):
    if user_img:
        img = Image.open(user_img)
    else:
        response = requests.get(user_url if user_url else base_url)
        img = Image.open(BytesIO(response.content))

    st.write("We take a random horse :racehorse: (you can load your own in the menu on the left)")

    img_bin = img_to_bin(img)
    truncate(horse_table)
    save_to_temp_db(img_bin, horse_table)
    update_prod_db(horse_table)

    # TODO push horse to tg
    st.image(img)

    img_t = preprocess(img)
    batch_t = torch.unsqueeze(img_t, 0)

    batch_out = net_G(batch_t)

    out_t = (batch_out.data.squeeze() + 1.0) / 2.0
    out_img = transforms.ToPILImage()(out_t)

    st.write("We drive the horse into tensor ... it's not a stall :grin:, it's such a multidimensional matrix")
    if st.checkbox("Show me the horse tensor"):
        st.code(img_t)

    st.write("Then there is a battle of generative adversarial networks ...")

    return out_img


def main():
    horse_url = st.sidebar.text_input("Put the link to the horse picture here: ")
    net, preproc = prepare_model()
    img_file = uploader()
    zebra = generate_zebra(net, preproc, img_file, horse_url, URL)
    img_bin = img_to_bin(zebra)
    truncate(zebra_table)
    save_to_temp_db(img_bin, zebra_table)
    update_prod_db(zebra_table)
    # TODO push zebra to tg

    st.write("... and the horse turns into a zebra")

    st.image(zebra)

    st.sidebar.markdown("""
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
    """)


if __name__ == "__main__":
    main()
