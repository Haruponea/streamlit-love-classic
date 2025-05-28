import streamlit as st
import random
import numpy as np
from music21 import stream, note, metadata, midi, environment
from PIL import Image
from pdf2image import convert_from_path
import tempfile
import os
import pygame
import subprocess

# MuseScore 4 경로 설정
us = environment.UserSettings()
us['musescoreDirectPNGPath'] = r'C:\Program Files\MuseScore 4\bin\MuseScore4.exe'

st.set_page_config(page_title="Love classic", page_icon="💌", layout="centered")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Gamja+Flower&display=swap');
        input, textarea, .st-emotion-cache-1whx7iy p, .st-emotion-cache-1kyxreq {
            font-family: 'Gamja Flower', cursive !important;
            font-size: 25px !important;
        }
        body {
            background-color: #fff0f5;
        }
        .stApp {
            background-image: linear-gradient(135deg, #ffe4e1 30%, #fff0f5 100%);
            color: #6a1b9a;
            font-family: 'Gamja Flower', cursive;
            font-size: 25px;
        }
        h1, h2, h3 {
            color: #d81b60;
            font-family: 'Gamja Flower', cursive;
            text-align: center;
            font-size: 40px;
        }
        .stTextInput, .stTextArea {
            background-color: #ffffffcc;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

NOTES = ['도', '레', '미', '파', '솔', '라', '시', '높은도']

def text_to_notes(sender, content, receiver):
    if len(sender) < 2 or len(content) < 4 or len(receiver) < 2:
        return []
    selected = random.sample(sender, 2) + random.sample(content, 4) + random.sample(receiver, 2)
    return [NOTES[ord(char) % 8] for char in selected]

def play_notes_midi(note_names):
    s = stream.Score()
    scoreLayout = layout.PageLayout()
    scoreLayout.pageHeight = 400
    scoreLayout.topMargin = 10
    scoreLayout.bottomMargin = 10
    s.insert(0, scoreLayout)
    pitch_map = {
        '도': 'C4', '레': 'D4', '미': 'E4', '파': 'F4',
        '솔': 'G4', '라': 'A4', '시': 'B4', '높은도': 'C5'
    }
    for name in note_names:
        if name in pitch_map:
            n = note.Note(pitch_map[name], quarterLength=1)
        s.append(n)
    mf = midi.translate.streamToMidiFile(s)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as f:
        mf.open(f.name, 'wb')
        mf.write()
        mf.close()
        temp_mid_path = f.name
    try:
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(temp_mid_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    finally:
        os.remove(temp_mid_path)

from music21 import layout

def render_sheet_music(note_names, composer_name):
    s = stream.Stream()
    s.metadata = metadata.Metadata()
    s.metadata.title = composer_name + "의 편지"
    s.metadata.composer = composer_name

    pitch_map = {
        '도': 'C4', '레': 'D4', '미': 'E4', '파': 'F4',
        '솔': 'G4', '라': 'A4', '시': 'B4', '높은도': 'C5'
    }

    for name in note_names:
        pitch = pitch_map.get(name)
        if pitch:
            s.append(note.Note(pitch, quarterLength=1))

    output_dir = os.path.abspath("output")
    os.makedirs(output_dir, exist_ok=True)
    xml_path = os.path.join(output_dir, "output.musicxml")
    mscz_path = os.path.join(output_dir, "intermediate.mscz")
    pdf_path = os.path.join(output_dir, "output.pdf")

    try:
        # 페이지 레이아웃 설정
        scoreLayout = layout.PageLayout()
        scoreLayout.pageHeight = 300
        scoreLayout.topMargin = 10
        scoreLayout.bottomMargin = 10
        s.insert(0, scoreLayout)

        s.write('musicxml', fp=xml_path)
        st.success("✅ musicxml 저장 성공")

        musescore_path = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
        style_path = r"C:\Program Files\MuseScore 4\styles\style.mss"

        subprocess.run([musescore_path, xml_path, "-o", mscz_path], check=True)

        result = subprocess.run([
            musescore_path, mscz_path, "-o", pdf_path, "-S", style_path
        ], capture_output=True, text=True, encoding='utf-8')

        if result.returncode != 0 or not os.path.exists(pdf_path):
            st.error(f"⚠️ MuseScore에서 PDF 파일을 생성하지 못했습니다.\n{result.stderr}")
        else:
            images = convert_from_path(pdf_path)
            image = images[0]
            width, height = image.size
            cropped_image = image.crop((0, 0, width, int(height * 0.3)))
            st.image(cropped_image, caption="🎼 생성된 악보", use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ 악보 이미지 생성 중 오류 발생: {e}")


# UI 구성
st.title("💌 Love letter: 클래식, 사랑을 담다")

st.markdown("""
    <div style='font-family: "Gamja Flower", cursive; font-size: 20px; line-height: 1.6;'>
        이 앱은 당신의 사랑이 담긴 편지를 감미로운 클래식 음표로 변환합니다.<br>
        아래 버튼을 누르면 생성된 음표가 오선지에 표시되고, 선율도 함께 들을 수 있어요. 🎶
    </div>
""", unsafe_allow_html=True)

sender = st.text_input("발신인 이름 (2글자 이상)")
content = st.text_area("편지 내용 (4글자 이상)", height=100)
receiver = st.text_input("수신인 이름 (2글자 이상)")

if st.button("🎼 음표 생성 및 연주"):
    notes = text_to_notes(sender, content, receiver)
    if not notes:
        st.warning("입력 조건을 다시 확인해주세요 (발신인 2자, 내용 4자, 수신인 2자 이상)")
    else:
        st.success("🎵 생성된 나만의 악보")
        render_sheet_music(notes, sender)
        try:
            play_notes_midi(notes)
        except Exception as e:
            st.error(f"🔇 소리 재생 중 오류 발생: {e}")
