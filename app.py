#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import argparse
import collections
import ast
import csv
import os
import json
import time
from collections import OrderedDict
from pathlib import Path
import streamlit as st
from PIL import Image, ImageFont, ImageDraw, ImageEnhance



import requests
import streamlit as st
import pandas as pd
from webcam import webcam

# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
# DB Management
import sqlite3
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data










def parse_arguments(args_hook=lambda _: _):
    parser = argparse.ArgumentParser(
        description=
        'Read license plates from images and output the result as JSON or CSV.',
        epilog="""Examples:'
Process images from a folder: python plate_recognition.py -a MY_API_KEY /path/to/vehicle-*.jpg
Use the Snapshot SDK instead of the Cloud Api: python plate_recognition.py -s http://localhost:8080 /path/to/vehicle-*.jpg
Specify Camera ID and/or two Regions: plate_recognition.py -a MY_API_KEY --camera-id Camera1 -r us-ca -r th-37 /path/to/vehicle-*.jpg""",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-a', '--api-key', help='Your API key.', required=False)
    parser.add_argument(
        '-r',
        '--regions',
        help='Match the license plate pattern of a specific region',
        required=False,
        action="append")
    parser.add_argument(
        '-s',
        '--sdk-url',
        help="Url to self hosted sdk  For example, http://localhost:8080",
        required=False)
    parser.add_argument('--camera-id',
                        help="Name of the source camera.",
                        required=False)
    parser.add_argument('files', nargs='+', help='Path to vehicle images')
    args_hook(parser)
    args = parser.parse_args()
    if not args.sdk_url and not args.api_key:
        raise Exception('api-key is required')
    return args


_session = None


def recognition_api(fp,
                    regions=[],
                    api_key="e2a60c10d2155f1df725c594c5605d6d63a2764c",
                    sdk_url=None,
                    config={},
                    camera_id=None,
                    timestamp=None,
                    mmc=None,
                    exit_on_error=True):
    global _session
    data = dict(regions=regions, config=json.dumps(config))
    if camera_id:
        data['camera_id'] = camera_id
    if mmc:
        data['mmc'] = mmc
    if timestamp:
        data['timestamp'] = timestamp
    response = None
    if sdk_url:
        fp.seek(0)
        response = requests.post(sdk_url + '/v1/plate-reader/',
                                 files=dict(upload=fp),
                                 data=data)
    else:
        if not _session:
            _session = requests.Session()
            _session.headers.update({'Authorization': 'Token ' + api_key})
        for _ in range(3):
            fp.seek(0)
            response = _session.post(
                'https://api.platerecognizer.com/v1/plate-reader/',
                files=dict(upload=fp),
                data=data)
            if response.status_code == 429:  # Max calls per second reached
                time.sleep(1)
            else:
                break

    if response is None:
        return {}
    if response.status_code < 200 or response.status_code > 300:
        print(response.text)
        if exit_on_error:
            exit(1)
    return response.json(object_pairs_hook=OrderedDict)


def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            if isinstance(v, list):
                items.append((new_key, json.dumps(v)))
            else:
                items.append((new_key, v))
    return dict(items)


def flatten(result):
    plates = result['results']
    del result['results']
    del result['usage']
    if not plates:
        return result
    for plate in plates:
        data = result.copy()
        data.update(flatten_dict(plate))
    return data


def save_results(results, args):
    path = Path(args.output_file)
    if not path.parent.exists():
        print('%s does not exist' % path)
        return
    if not results:
        return
    if args.format == 'json':
        with open(path, 'w') as fp:
            json.dump(results, fp)
    elif args.format == 'csv':
        fieldnames = []
        for result in results[:10]:
            candidate = flatten(result.copy()).keys()
            if len(fieldnames) < len(candidate):
                fieldnames = candidate
        with open(path, 'w') as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(flatten(result))


def custom_args(parser):
    parser.epilog += """
Specify additional engine configuration: plate_recognition.py -a MY_API_KEY --engine-config \'{"region":"strict"}\' /path/to/vehicle-*.jpg
Specify an output file and format for the results: plate_recognition.py -a MY_API_KEY -o data.csv --format csv /path/to/vehicle-*.jpg
Enable Make Model and Color prediction: plate_recognition.py -a MY_API_KEY --mmc /path/to/vehicle-*.jpg"""

    parser.add_argument('--engine-config', help='Engine configuration.')
    parser.add_argument('-o', '--output-file', help='Save result to file.')
    parser.add_argument('--format',
                        help='Format of the result.',
                        default='json',
                        choices='json csv'.split())
    parser.add_argument(
        '--mmc',
        action='store_true',
        help='Predict vehicle make and model. Only available to paying users.')


def main():



    st.title("reconnaissance de plaque d'immatriculation 🇧🇫")
    a = st.selectbox("Select : ",["Upload Image","Real Time Picture"])
    if a =="Upload Image":
        img_file_buffer = st.file_uploader("Image de véhicule", type=["png", "jpg", "jpeg"])
        if img_file_buffer is not None:
            file_details = {"FileName": img_file_buffer.name, "FileType": img_file_buffer.type}

            with open(os.path.join("./tempDir", "input.png"), "wb") as f:
                f.write(img_file_buffer.getbuffer())
        c = st.columns(10)
        test = c[4].button("Detecter")

        if test:
            try:

                paths = ["./tempDir/input.png"]

                results = []
                engine_config = {}


                for path in paths:
                    with open(path, 'rb') as fp:
                        api_res = recognition_api(fp,api_key="e2a60c10d2155f1df725c594c5605d6d63a2764c")

                    results.append(api_res)
                    time_exec = json.dumps(results[0]["processing_time"], indent=2)
                    plate_number = json.dumps(results[0]["results"][0]["plate"], indent=2)
                    boxes = json.dumps(results[0]["results"][0]["box"], indent=2)
                    boxes = ast.literal_eval(boxes)
                    c = st.columns(2)
                    xmin,ymin,xmax,ymax = boxes["xmin"],boxes["ymin"],boxes["xmax"],boxes["ymax"]
                    source_img = Image.open("./tempDir/input.png").convert("RGBA")
                    # font_type = ImageFont.truetype("Arial.ttf", 18)
                    draw = ImageDraw.Draw(source_img)
                    draw.rectangle(((xmin, ymin), (xmax, ymax)), outline=(0, 255, 0), width=3)
                    draw.text((xmin - 5, ymin - 10), "Matricule", fill=(0, 255, 0))

                    source_img.save("./tempDir/input.png", "PNG")
                    im = Image.open("tempDir/input.png")
                    im = im.resize((300,400))
                    c[0].image(im)

                    plate_number = plate_number.replace('"',"")
                    c[1].subheader("Numero De Matricule:")
                    c[1].text(plate_number.upper())

                    c[1].subheader("Numero D'Ordre:")
                    c[1].text(plate_number[:4].upper())

                    c[1].subheader("Code Alpha:")
                    c[1].text(plate_number[4:6].upper())

                    c[1].subheader("Code Région:")
                    c[1].text(plate_number[6:].upper())
                    db = pd.read_csv("data.csv")
                    mats = db["immatriculation"].values
                    plate_number = plate_number.upper()




                    with st.expander("Additional Informations"):
                        if plate_number in mats:

                            st.markdown('___')
                            c = st.columns(2)
                            c[0].markdown("<h3>Informations Vehicules</h3>",unsafe_allow_html=True)
                            c[0].markdown(f"**Genre**: {db[db['immatriculation']==plate_number]['genre'].values[0]}")
                            c[0].markdown(f"**Marque**: {db[db['immatriculation']==plate_number]['marque'].values[0]}")
                            c[0].markdown(f"**Color**: {db[db['immatriculation']==plate_number]['color'].values[0]}")


                            c[1].markdown("<h3>Informations Proprietaire</h3>",unsafe_allow_html=True)
                            c[1].markdown(f"**Nom**: {db[db['immatriculation'] == plate_number]['nom'].values[0]}")
                            c[1].markdown(f"**Prenom**: {db[db['immatriculation'] == plate_number]['prenom'].values[0]}")
                            c[1].markdown(f"**Profession**: {db[db['immatriculation'] == plate_number]['profession'].values[0]}")
                            c[1].markdown(f"**Ville**: {db[db['immatriculation'] == plate_number]['ville'].values[0]}")
                            c[1].markdown(f"**Province**: {db[db['immatriculation'] == plate_number]['province'].values[0]}")
                            c[1].markdown(f"**Adresse**: {db[db['immatriculation'] == plate_number]['adresse'].values[0]}")

                            st.subheader("")
                            c = st.columns(3)
                            c[1].markdown("Declarée Predu:")
                            if db[db['immatriculation'] == plate_number]['declaration_perte'].values[0]=="OUI":
                                c[2].markdown("❌")
                            else:
                                c[2].markdown("✔️")
                            st.markdown('___')
                            c = st.columns(3)
                            c[0].markdown("<h5>Infos Visite Technique</h5>", unsafe_allow_html=True)
                            c[0].markdown(f"**Date Visite**: {db[db['immatriculation'] == plate_number]['date_visite'].values[0]}")
                            c[0].markdown(f"**Date Expiration**: {db[db['immatriculation'] == plate_number]['date_expiration'].values[0]}")


                            c[1].markdown("<h5>Infos Assurance</h5>", unsafe_allow_html=True)
                            c[1].markdown(f"**Assureur**: {db[db['immatriculation'] == plate_number]['assureur'].values[0]}")
                            c[1].markdown(f"**Type Assurance**: {db[db['immatriculation'] == plate_number]['type_assurance'].values[0]}")
                            c[1].markdown(f"**Date Assurance**: {db[db['immatriculation'] == plate_number]['date_assurance'].values[0]}")
                            c[1].markdown(f"**Date Expiration**: {db[db['immatriculation'] == plate_number]['date_exp_a'].values[0]}")

                            c[2].markdown("<h5>Infos Permis de Conduite</h5>", unsafe_allow_html=True)
                            c[2].markdown(f"**Numero Permis**: {db[db['immatriculation'] == plate_number]['numero_permis'].values[0]}")
                            c[2].markdown(f"**Type Permis**: {db[db['immatriculation'] == plate_number]['type_permis'].values[0]}")
                            c[2].markdown(f"**Date Delivrance**: {db[db['immatriculation'] == plate_number]['date_delivrance'].values[0]}")
                            c[2].markdown(f"**Lieu Delivrance**: {db[db['immatriculation'] == plate_number]['lieu_delivrance'].values[0]}")
                        else:
                            st.warning("This Vehicule Not registred!")
            except:
                st.warning("Retry...")
    else:
        captured_image = webcam()
        if captured_image is None:
            st.write("Waiting for capture...")
        else:
            st.write("Got an image from the webcam:")
            captured_image.save("./tempDir/input.png")
            c = st.columns(10)
            test = c[4].button("Detecter")
            if test:
                try:

                        paths = ["./tempDir/input.png"]

                        results = []
                        engine_config = {}

                        for path in paths:
                            with open(path, 'rb') as fp:
                                api_res = recognition_api(fp, api_key="e2a60c10d2155f1df725c594c5605d6d63a2764c")

                            results.append(api_res)

                            time_exec = json.dumps(results[0]["processing_time"], indent=2)
                            plate_number = json.dumps(results[0]["results"][0]["plate"], indent=2)
                            boxes = json.dumps(results[0]["results"][0]["box"], indent=2)
                            boxes = ast.literal_eval(boxes)
                            c = st.columns(2)
                            xmin, ymin, xmax, ymax = boxes["xmin"], boxes["ymin"], boxes["xmax"], boxes["ymax"]
                            source_img = Image.open("./tempDir/input.png").convert("RGBA")
                            # font_type = ImageFont.truetype("Arial.ttf", 18)
                            draw = ImageDraw.Draw(source_img)
                            draw.rectangle(((xmin, ymin), (xmax, ymax)), outline=(0, 255, 0), width=3)
                            draw.text((xmin - 5, ymin - 10), "Matricule", fill=(0, 255, 0))

                            source_img.save("./tempDir/input.png", "PNG")
                            im = Image.open("tempDir/input.png")
                            im = im.resize((300, 400))
                            c[0].image(im)

                            plate_number = plate_number.replace('"', "")
                            c[1].subheader("Numero De Matricule:")
                            c[1].text(plate_number.upper())

                            c[1].subheader("Numero D'Ordre:")
                            c[1].text(plate_number[:4].upper())

                            c[1].subheader("Code Alpha:")
                            c[1].text(plate_number[4:6].upper())

                            c[1].subheader("Code Région:")
                            c[1].text(plate_number[6:].upper())
                            db = pd.read_csv("datasets.csv")
                            mats = db["immatriculation"].values
                            plate_number = plate_number.upper()

                            with st.expander("Additional Informations"):
                                if plate_number in mats:

                                    st.markdown('___')
                                    c = st.columns(2)
                                    c[0].markdown("<h3>Informations Vehicules</h3>", unsafe_allow_html=True)
                                    c[0].markdown(f"**Genre**: {db[db['immatriculation'] == plate_number]['genre'].values[0]}")
                                    c[0].markdown(
                                        f"**Marque**: {db[db['immatriculation'] == plate_number]['marque'].values[0]}")

                                    c[1].markdown("<h3>Informations Proprietaire</h3>", unsafe_allow_html=True)
                                    c[1].markdown(f"**Nom**: {db[db['immatriculation'] == plate_number]['nom'].values[0]}")
                                    c[1].markdown(
                                        f"**Prenom**: {db[db['immatriculation'] == plate_number]['prenom'].values[0]}")
                                    c[1].markdown(
                                        f"**Profession**: {db[db['immatriculation'] == plate_number]['profession'].values[0]}")
                                    c[1].markdown(f"**Ville**: {db[db['immatriculation'] == plate_number]['ville'].values[0]}")
                                    c[1].markdown(
                                        f"**Province**: {db[db['immatriculation'] == plate_number]['province'].values[0]}")
                                    c[1].markdown(
                                        f"**Adresse**: {db[db['immatriculation'] == plate_number]['adresse'].values[0]}")

                                    st.subheader("")
                                    c = st.columns(3)
                                    c[1].markdown("Declarée Predu:")
                                    if db[db['immatriculation'] == plate_number]['declaration_perte'].values[0] == "OUI":
                                        c[2].markdown("❌")
                                    else:
                                        c[2].markdown("✔️")
                                    st.markdown('___')
                                    c = st.columns(3)
                                    c[0].markdown("<h5>Infos Visite Technique</h5>", unsafe_allow_html=True)
                                    c[0].markdown(
                                        f"**Puissance**: {db[db['immatriculation'] == plate_number]['puissance_administrative'].values[0]}")
                                    c[0].markdown(
                                        f"**Charge Utile**: {db[db['immatriculation'] == plate_number]['charge_utile'].values[0]}")
                                    c[0].markdown(f"**PTAC**: {db[db['immatriculation'] == plate_number]['ptac'].values[0]}")
                                    c[0].markdown(f"**PTRA**: {db[db['immatriculation'] == plate_number]['ptra'].values[0]}")
                                    c[0].markdown(
                                        f"**Capacite**: {db[db['immatriculation'] == plate_number]['capacite'].values[0]}")

                                    c[1].markdown("<h5>Infos Assurance</h5>", unsafe_allow_html=True)
                                    c[1].markdown(
                                        f"**N° Serie**: {db[db['immatriculation'] == plate_number]['numero_serie'].values[0]}")
                                    c[1].markdown(
                                        f"**Carosserie**: {db[db['immatriculation'] == plate_number]['carrosserie'].values[0]}")
                                    c[1].markdown(f"**Type**: {db[db['immatriculation'] == plate_number]['type'].values[0]}")
                                    c[1].markdown(
                                        f"**Modele**: {db[db['immatriculation'] == plate_number]['modele'].values[0]}")
                                    c[1].markdown(
                                        f"**Energie**: {db[db['immatriculation'] == plate_number]['energie'].values[0]}")

                                    c[2].markdown("<h5>Infos Permis de Conduite</h5>", unsafe_allow_html=True)
                                    c[2].markdown(
                                        f"**Nombre Place**: {db[db['immatriculation'] == plate_number]['nombre_places'].values[0]}")
                                    c[2].markdown(
                                        f"**Date M° Circulation**: {db[db['immatriculation'] == plate_number]['date_mise_circulation'].values[0]}")
                                else:
                                    st.warning("This Vehicule Not registred!")
                except:
                    st.warning("No Car in the Image")
def log():
    """Simple Login App"""
    menu = ["Login", "SignUp"]
    st.sidebar.image("./logos/logo_naana.png")
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login"):
            # if password == '12345':
            create_usertable()
            hashed_pswd = make_hashes(password)

            result = login_user(username, check_hashes(password, hashed_pswd))
            if result:
                main()
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')

        if st.button("Signup"):
            create_usertable()
            add_userdata(new_user, make_hashes(new_password))
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")


if __name__ == '__main__':
    log()
