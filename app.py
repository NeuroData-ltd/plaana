#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import argparse
import collections
import ast
import csv
import os
import requests
import json
import time
from collections import OrderedDict
from pathlib import Path
import streamlit as st
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import streamlit.components.v1 as stc

urlapi = "https://naanapay.com/contrapid/infractions.php"

import requests
import streamlit as st
import pandas as pd
from webcam import webcam
import datetime
# Security
# passlib,hashlib,bcrypt,scrypt
import hashlib


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False


# DB Management
import mysql.connector

conn = mysql.connector.connect(host='sql6.freesqldatabase.com',
                                         database='sql6483132',
                                         user='sql6483132',
                                         password='KiuByTAqMe')
c = conn.cursor()


def infractions_non_payees(plate_number):
    c.execute(
        'SELECT nature_infraction, lieu_infraction, date_infraction FROM infractions where immatriculation="{}" and statut=0'.format(
            plate_number))
    data = c.fetchall()
    return data


# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS agents(username TEXT,password TEXT, matricule TEXT)')


def add_userdata(username, password, matricule):
    c.execute('INSERT INTO agents(username,password, matricule) VALUES (%s,%s,%s)', (username, password, matricule))
    conn.commit()


def login_user(username, password):
    c.execute('SELECT * FROM agents WHERE username =%s AND password = %s', (username, password))
    data = c.fetchall()
    return data


def view_all_users():
    c.execute('SELECT * FROM agents')
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


def datasets(plate_number):
    connection = mysql.connector.connect(host='sql6.freesqldatabase.com',
                                         database='sql6483132',
                                         user='sql6483132',
                                         password='KiuByTAqMe')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        cursor = connection.cursor()
        cursor.execute("SELECT immatriculation FROM carte_grise;")

        mats = []
        for e in cursor.fetchall():
            mats.append(e[0])
        print(mats)

        cursor.execute(f'select genre from carte_grise where immatriculation="{plate_number}";')
        genre = cursor.fetchall()[0][0]

        cursor.execute(f'select marque from carte_grise where immatriculation="{plate_number}";')
        marque = cursor.fetchall()[0][0]

        cursor.execute(f'select modele from carte_grise where immatriculation="{plate_number}";')
        modele = cursor.fetchall()[0][0]

        cursor.execute(f'select date_mise_circulation from carte_grise where immatriculation="{plate_number}";')
        date_mise_circulation = cursor.fetchall()[0][0]

        cursor.execute(f'select nom from carte_grise where immatriculation="{plate_number}";')
        nom = cursor.fetchall()[0][0]

        cursor.execute(f'select prenom from carte_grise where immatriculation="{plate_number}";')
        prenom = cursor.fetchall()[0][0]

        cursor.execute(f'select profession from carte_grise where immatriculation="{plate_number}";')
        profession = cursor.fetchall()[0][0]

        cursor.execute(f'select ville from carte_grise where immatriculation="{plate_number}";')
        ville = cursor.fetchall()[0][0]

        cursor.execute(f'select province from carte_grise where immatriculation="{plate_number}";')
        province = cursor.fetchall()[0][0]

        cursor.execute(f'select adresse from carte_grise where immatriculation="{plate_number}";')
        adresse = cursor.fetchall()[0][0]

        cursor.execute(f'select declaration_perte from carte_grise where immatriculation="{plate_number}";')
        declaration_perte = cursor.fetchall()[0][0]

        cursor.execute(f'select date_visite from visite_technique where immatriculation="{plate_number}";')
        date_visite = cursor.fetchall()[0][0]

        cursor.execute(f'select date_expiration from visite_technique where immatriculation="{plate_number}";')
        date_expiration = cursor.fetchall()[0][0]

        cursor.execute(f'select assureur from assurance where immatriculation="{plate_number}";')
        assureur = cursor.fetchall()[0][0]
        cursor.execute(f'select type_assurance from assurance where immatriculation="{plate_number}";')
        type_assurance = cursor.fetchall()[0][0]
        cursor.execute(f'select date_assurance from assurance where immatriculation="{plate_number}";')
        date_assurance = cursor.fetchall()[0][0]
        cursor.execute(f'select date_expiration from assurance where immatriculation="{plate_number}";')
        date_expiration1 = cursor.fetchall()[0][0]

        # cursor.execute(f'select numero_permis from permis_de_conduire where nom="{nom}";')
        numero_permis = "1142548"
        # cursor.execute(f'select date_delivrance from permis_de_conduire where nom="{nom}";')
        date_delivrance = "2022-01-01"
        # cursor.execute(f'select lieu_delivrance from assurance where nom="{nom}";')
        lieu_delivrance = "OUAGADOGO"
        return (
            mats, genre, marque, modele, date_mise_circulation, nom, prenom, assureur, date_visite, date_expiration,
            type_assurance, date_assurance,
            date_expiration1, profession, ville, province, adresse, declaration_perte, date_visite, date_expiration,
            numero_permis, date_delivrance, lieu_delivrance)


# mats, genre, marque, nom, prenom, assureur, date_visite, date_expiration, type_assurance, date_assurance, date_expiration1, profession, ville, province, adresse, declaration_perte, date_visite, date_expiration, numero_permis, date_delivrance, lieu_delivrance = datasets("9563D403")


def main():
    global plate_number

    # st.title("reconnaissance de plaque d'immatriculation 🇧🇫")

    a = st.selectbox("Source de l'image : ", ["Téléverser l'image", "Prendre une photo"])
    if a == "Téléverser l'image":
        img_file_buffer = st.file_uploader("Sélectionnez une image", type=["png", "jpg", "jpeg"])
        if img_file_buffer is not None:
            file_details = {"FileName": img_file_buffer.name, "FileType": img_file_buffer.type}

            with open(os.path.join("./tempDir", "input.png"), "wb") as f:
                f.write(img_file_buffer.getbuffer())
        c = st.columns(10)
        test = c[4].button("Vérification")

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
                    c[1].subheader("Numéro De Matricule:")
                    c[1].text(plate_number.upper())

                    c[1].subheader("Numéro D'Ordre:")
                    c[1].text(plate_number[:4].upper())

                    c[1].subheader("Code Alpha:")
                    c[1].text(plate_number[4:6].upper())

                    c[1].subheader("Code Région:")
                    c[1].text(plate_number[6:].upper())
                    plate_number = plate_number.upper()


                    mats, genre, marque, modele, date_mise_circulation, nom, prenom, assureur, date_visite, date_expiration, type_assurance, date_assurance, date_expiration1, profession, ville, province, adresse, declaration_perte, date_visite, date_expiration, numero_permis, date_delivrance, lieu_delivrance = datasets(
                        plate_number)

                    f = open("tmpp.txt", "w")
                    f.write(str(plate_number.upper()))
                    f.close()
                    if plate_number in mats:
                        print("ok")

                    with st.expander("Information Propriétaire"):
                        if plate_number in mats:
                            print("ok")

                            st.markdown('___')
                            c = st.columns(2)
                            c[0].markdown("<h3>Informations Vehicules</h3>", unsafe_allow_html=True)
                            c[0].markdown(f"**Genre**: {genre}")
                            c[0].markdown(f"**Marque**: {marque}")
                            c[0].markdown(f"**Modele**: {modele}")
                            c[0].markdown(f"**Date de mise en circulation**: {date_mise_circulation}")

                            c[1].markdown("<h3>Informations Proprietaire</h3>", unsafe_allow_html=True)
                            c[1].markdown(f"**Nom**: {nom}")
                            c[1].markdown(f"**Prenom**: {prenom}")
                            c[1].markdown(f"**Profession**: {profession}")
                            c[1].markdown(f"**Ville**: {ville}")
                            c[1].markdown(f"**Province**: {province}")
                            c[1].markdown(f"**Adresse**: {adresse}")

                            st.subheader("")
                            c = st.columns(3)
                            c[1].markdown("Declarée Predu:")
                            if declaration_perte == "OUI":
                                c[2].markdown("❌")
                            else:
                                c[2].markdown("✔️")
                            st.markdown('___')
                            c = st.columns(3)
                            c[0].markdown("<h5>Infos Visite Technique</h5>", unsafe_allow_html=True)
                            c[0].markdown(f"**Date Visite**: {date_visite}")
                            c[0].markdown(f"**Date Expiration**: {date_expiration}")

                            c[1].markdown("<h5>Infos Assurance</h5>", unsafe_allow_html=True)
                            c[1].markdown(f"**Assureur**: {assureur}")
                            c[1].markdown(f"**Type Assurance**: {type_assurance}")
                            c[1].markdown(f"**Date Assurance**: {date_assurance}")
                            c[1].markdown(f"**Date Expiration**: {date_expiration1}")

                            c[2].markdown("<h5>Infos Permis de Conduite</h5>", unsafe_allow_html=True)
                            c[2].markdown(f"**Numéro Permis**: {numero_permis}")
                            c[2].markdown(f"**Date Delivrance**: {date_delivrance}")
                            c[2].markdown(f"**Lieu Delivrance**: {lieu_delivrance}")
                        else:
                            st.warning("Ce véhicule n'est pas enregistré!")

            except:
                st.warning("Rééssayer...")
                with st.expander("Infractions non payées"):
                    # df = pd.DataFrame(result)
                    # st.dataframe(df, 200, 100)
                    df = pd.DataFrame(infractions_non_payees(plate_number),
                                      columns=['nature_infraction', 'lieu_infraction', 'date_infraction'])
                    st.dataframe(df)



    else:
        captured_image = webcam()
        if captured_image is None:
            st.write("En attente de la capture...")
        else:
            st.write("Image obtenue de la webcam:")
            captured_image.save("./tempDir/input.png")
            c = st.columns(10)
            test = c[4].button("Vérification")
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
                        c[1].subheader("Numéro De Matricule:")
                        c[1].text(plate_number.upper())

                        c[1].subheader("Numéro D'Ordre:")
                        c[1].text(plate_number[:4].upper())

                        c[1].subheader("Code Alpha:")
                        c[1].text(plate_number[4:6].upper())

                        c[1].subheader("Code Région:")
                        c[1].text(plate_number[6:].upper())
                        plate_number = plate_number.upper()
                        mats, genre, marque, nom, prenom, assureur, date_visite, date_expiration, type_assurance, date_assurance, date_expiration1, profession, ville, province, adresse, declaration_perte, date_visite, date_expiration, numero_permis, date_delivrance, lieu_delivrance = \
                            datasets(plate_number)

                        f = open("tmpp.txt", "w")
                        f.write(str(plate_number.upper()))
                        f.close()

                        with st.expander("Informations Propriétaire"):
                            if plate_number in mats:

                                st.markdown('___')
                                c = st.columns(2)
                                c[0].markdown("<h3>Informations Vehicules</h3>", unsafe_allow_html=True)
                                c[0].markdown(f"**Genre**: {genre}")
                                c[0].markdown(f"**Marque**: {marque}")

                                c[1].markdown("<h3>Informations Proprietaire</h3>", unsafe_allow_html=True)
                                c[1].markdown(f"**Nom**: {nom}")
                                c[1].markdown(f"**Prenom**: {prenom}")
                                c[1].markdown(f"**Profession**: {profession}")
                                c[1].markdown(f"**Ville**: {ville}")
                                c[1].markdown(f"**Province**: {province}")
                                c[1].markdown(f"**Adresse**: {adresse}")

                                st.subheader("")
                                c = st.columns(3)
                                c[1].markdown("Declarée Predu:")
                                if declaration_perte == "OUI":
                                    c[2].markdown("❌")
                                else:
                                    c[2].markdown("✔️")
                                st.markdown('___')
                                c = st.columns(3)
                                c[0].markdown("<h5>Infos Visite Technique</h5>", unsafe_allow_html=True)
                                c[0].markdown(f"**Date Visite**: {date_visite}")
                                c[0].markdown(f"**Date Expiration**: {date_expiration}")

                                c[1].markdown("<h5>Infos Assurance</h5>", unsafe_allow_html=True)
                                c[1].markdown(f"**Assureur**: {assureur}")
                                c[1].markdown(f"**Type Assurance**: {type_assurance}")
                                c[1].markdown(f"**Date Assurance**: {date_assurance}")
                                c[1].markdown(f"**Date Expiration**: {date_expiration1}")

                                c[2].markdown("<h5>Infos Permis de Conduite</h5>", unsafe_allow_html=True)
                                c[2].markdown(f"**Numéro Permis**: {numero_permis}")
                                c[2].markdown(f"**Date Delivrance**: {date_delivrance}")
                                c[2].markdown(f"**Lieu Delivrance**: {lieu_delivrance}")
                            else:
                                st.warning("Ce Vehicule n'existe pas dans la Base de Données!")




                except:
                    st.warning("Désolé, pas d'immatriculation trouvée sur l'image")


HTML_BANNER = """
    <div style="background-color:#F0F2F6;padding:1px;border-radius:10px">
        <h1 style="color:#4C4D58; font-family:roboto;text-align:center;">CONTRAPID 🇧🇫</h1>
        <p style="color:#4C4D58;text-align:center;font-size:18px;">Contrôle Rapide de l'Authenticité des Plaques d'Immatriculation et des Documents</p>
        <p style="color:#4C4D58;text-align:center;">By NaanaTech</p>
    </div>
    """


def log():
    """Simple Login App"""
    menu = ["Connexion", "Inscription"]
    st.sidebar.image("./logos/logo_naana.png")
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Connexion":
        username = st.sidebar.text_input("Nom d'utilisateur")
        password = st.sidebar.text_input("Mot de passe", type='password')

        st.image("./logos/logo_naana.png")
        stc.html(HTML_BANNER)
        # st.title('CONTRAPID')
        # st.write("Contrôle Rapide de l'Authenticité des Plaques d'Immatriculation et des Documents")
        # st.subheader("By NaanaTech")
        st.subheader("")
        st.subheader("")
        if st.sidebar.checkbox("Connexion"):
            # if password == '12345':
            create_usertable()
            hashed_pswd = make_hashes(password)

            result = login_user(username, check_hashes(password, hashed_pswd))
            if result:
                main()
                f = open("tmpp.txt", "r")
                try:
                    p = f.readlines()[0]
                    f.close()
                except:
                    p = "D787547"
                with st.expander("E-Verbalisation"):
                    form = st.form(key="E-Verbalisation")
                    plaque = form.text_input("Plaque d'immatriculation", p)
                    namef = form.text_input("Nom fautif")
                    prf = form.text_input("Prenom fautif")
                    phone = form.text_input("Numéro tél (ex: 70xxxxxx)")
                    nature = form.text_input("Nature infraction")
                    lieu = form.text_input("Lieu infraction")
                    now = datetime.date.today()
                    date = form.date_input("Date", now)
                    lieur = form.text_input("Lieu de récupération engin")
                    namea = form.text_input("Matricule agent")
                    submit = form.form_submit_button(label='Soumettre')
                    if submit:
                        d = {
                            "immatriculation": plaque,
                            "nom_fautif": namef,
                            "phone": phone,
                            "prenom_fautif": prf,
                            "nature_infraction": nature,
                            "lieu_infraction": lieu,
                            "date_infraction": str(date),
                            "lieu_recuperation": lieur,
                            "nom_agent": namea
                        }

                        payload = json.dumps(d)
                        headers = {
                            'Content-Type': 'application/json'
                        }
                        response = requests.post(url="https://naanapay.com/contrapid/infractions.php",
                                                 headers=headers, data=payload)
                        print(response.text)
                        print(d)







            else:
                st.warning("Nom d'utilisateur/mot de passe incorrect")

    elif choice == "Inscription":
        st.subheader("Créer un Compte CONTRAPID")
        new_matricule = st.text_input("Matricule")
        new_user = st.text_input("Nom d'utilisateur")
        new_password = st.text_input("Mot de passe", type='password')

        if st.button("Inscription"):
            # create_usertable()
            add_userdata(new_user, make_hashes(new_password), new_matricule)
            st.success("Nouveau compte crée avec succès!")
            st.info("Allez au menu de connexion pour vous connecter")


if __name__ == '__main__':
    log()
