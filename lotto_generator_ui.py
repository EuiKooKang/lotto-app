import streamlit as st
import random
import pandas as pd
import datetime
import requests
from pathlib import Path

# 저장할 로또 번호 로그 경로
SAVE_PATH = Path("lotto_saved.csv")

# 번호 추천을 위한 간단한 패턴 기반 추천기
popular_numbers = [1, 7, 11, 17, 22, 27, 33, 38, 42]

def generate_lotto_numbers():
    base = set(random.sample(popular_numbers, 3))
    while len(base) < 6:
        base.add(random.randint(1, 45))
    return sorted(list(base))

def check_similarity(new_set, history_sets):
    results = []
    for round_info in history_sets:
        match = len(new_set & round_info['number_set'])
        if match >= 4:
            results.append({
                'Round': round_info['round'],
                'Match Count': match,
                'Matching Numbers': sorted(list(new_set & round_info['number_set'])),
            })
    return pd.DataFrame(results)

def save_number(generated):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = pd.DataFrame([[now] + generated], columns=['timestamp'] + [f'n{i+1}' for i in range(6)])
    if SAVE_PATH.exists():
        prev = pd.read_csv(SAVE_PATH)
        df = pd.concat([prev, new_entry], ignore_index=True)
    else:
        df = new_entry
    df.to_csv(SAVE_PATH, index=False)

def load_saved():
    if SAVE_PATH.exists():
        return pd.read_csv(SAVE_PATH)
    return pd.DataFrame(columns=['timestamp', 'n1','n2','n3','n4','n5','n6'])

def fetch_lotto_history(latest_round=1121, past_count=260):
    lotto_data = []
    for round_no in range(latest_round - past_count + 1, latest_round + 1):
        url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={round_no}"
        try:
            res = requests.get(url)
            data = res.json()
            if data['returnValue'] == 'success':
                numbers = [data[f'drwtNo{i}'] for i in range(1, 7)]
                lotto_data.append({
                    'round': data['drwNo'],
                    'number_set': set(numbers)
                })
        except:
            continue
    return lotto_data

# Streamlit 앱 시작
st.set_page_config(page_title="로또 번호 추천기", page_icon="🎰", layout="centered")
st.title("🎰 로또 번호 자동 생성 & 중복 분석기")

if st.button("✨ 로또 번호 추천받기"):
    generated = generate_lotto_numbers()
    st.success(f"추천 번호: {generated}")
    save_number(generated)

    st.info("📡 과거 로또 데이터 분석 중...")
    history_sets = fetch_lotto_history()
    result_df = check_similarity(set(generated), history_sets)
    if not result_df.empty:
        st.warning("⚠️ 과거 당첨 번호와 유사한 조합 발견!")
        st.dataframe(result_df)
    else:
        st.success("🎉 유사 조합 없음. 안심하고 도전하세요!")

st.markdown("---")
st.subheader("💾 저장된 추천 기록")
saved_df = load_saved()
st.dataframe(saved_df)

st.caption("ⓒ 초롱이 - 캡틴 전용 로또 분석기")
