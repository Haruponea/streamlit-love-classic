import streamlit as st
import random
import numpy as np
from music21 import stream, note, metadata
from PIL import Image
import tempfile
import os

# 사랑 + 클래식 테마에 맞는 색상과 스타일 적용
st.set_page_config(page_title="사랑의 편지 음표", page_icon="💌", layout="centered")

st.markdown("""
    <style>
        body {
            background-color: #fff0f5;
        }
        .stApp {
            background-image: linear-gradient(135deg, #ffe4e1 30%, #fff0f5 100%);
            color: #6a1b9a;
            font-family: 'Georgia', serif;
        }
        h1, h2, h3 {
            color: #d81b60;
            text-align: center;
        }
        .stTextInput, .stTextArea {
            background-color: #ffffffcc;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

NOTES = ['도', '레', '미', '파', '솔', '라', '시', '높은도']
FREQS = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C4 ~ C5

# 로직 함수 정의
def text_to_notes(sender, content, receiver):
    if len(sender) < 2 or len(content) < 4 or len(receiver) < 2:
        return [], []

    selected = random.sample(sender, 2) + random.sample(content, 4) + random.sample(receiver, 2)

    notes = []
    freqs = []
    for char in selected:
        unicode_val = ord(char)
        index = unicode_val % 8
        notes.append(NOTES[index])
        freqs.append(FREQS[index])
    return notes, freqs

def render_sheet_music(note_names):
    s = stream.Stream()
    s.metadata = metadata.Metadata()
    s.metadata.title = "사랑의 음표"
    s.metadata.composer = "AI 편지"

    pitch_map = {
        '도': 'C4', '레': 'D4', '미': 'E4', '파': 'F4',
        '솔': 'G4', '라': 'A4', '시': 'B4', '높은도': 'C5'
    }

    for name in note_names:
        if name in pitch_map:
            s.append(note.Note(pitch_map[name], quarterLength=1))

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "output.png")
        s.write('musicxml.png', fp=filepath)
        image = Image.open(filepath)
        st.image(image, caption="🎼 생성된 악보", use_column_width=True)

# UI 구성
st.title("💌 사랑의 편지에서 울려퍼지는 클래식 선율")

st.write("""
    이 앱은 당신의 사랑이 담긴 편지에서 무작위로 문자를 선택해 
    감미로운 클래식 음표로 변환합니다. 웹에서는 소리가 들리지 않을 수 있으니, 
    로컬에서 직접 실행해보면 더욱 아름답습니다. 🎶
""")

sender = st.text_input("발신인 이름 (2글자 이상)")
content = st.text_area("편지 내용 (4글자 이상)", height=100)
receiver = st.text_input("수신인 이름 (2글자 이상)")

if st.button("🎼 음표 생성"):
    notes, freqs = text_to_notes(sender, content, receiver)
    if not notes:
        st.warning("입력 조건을 다시 확인해주세요 (발신인 2자, 내용 4자, 수신인 2자 이상)")
    else:
        st.success("🎵 생성된 클래식 선율:")
        st.markdown(f"""
            <div style='font-size: 24px; text-align: center; margin: 20px 0;'>
                {' '.join(notes)}
            </div>
        """, unsafe_allow_html=True)
        render_sheet_music(notes)
        st.info("🔇 온라인 환경에서는 소리 재생 기능은 제거되었습니다. 로컬에서 수동으로 테스트해보세요.")
