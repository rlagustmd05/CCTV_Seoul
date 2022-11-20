import folium
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import sqlite3
import pandas as pd
import json

con = sqlite3.connect('db.db')
cur = con.cursor()

def login_user(id, pwd):
    cur.execute(f"SELECT * FROM users WHERE id='{id}' and pw='{pwd}'")
    return cur.fetchone()

menu = st.sidebar.selectbox('MENU', options=['회원가입','로그인','회원목록','서울 지키미'])

if menu == '회원가입':
    with st.form('my_form', clear_on_submit=True):
        id = st.text_input('아이디', placeholder='아이디를 입력하세요.', max_chars=10)
        pw = st.text_input('비밀번호', placeholder='비밀번호를 입력하세요.', type='password')
        pw_ck = st.text_input('비밀번호 확인', placeholder='비밀번호를 확인하세요.', type='password')
        name = st.text_input('이름', placeholder='ex) 방민예')
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.text_input('나이', placeholder='ex) 18')
        with col2:
            gender = st.radio('성별', ['남자', '여자'], horizontal=True)
        number = st.text_input('전화번호', placeholder='ex) 010-8071-9071')
        register = st.form_submit_button('회원가입')

        if register:
            if pw == pw_ck:
                cur.execute(f"INSERT INTO users(id, pw, name, age, gender, number) "
                            f"VALUES("
                            f"'{id}', '{pw}', '{name}', {age}, '{gender}', '{number}')")
                con.commit()
                st.success('회원가입이 완료되었습니다.')
            else:
                st.warning('비밀번호를 확인해주세요.')

if menu =='로그인':
    login_id = st.sidebar.text_input('아이디')
    login_pw = st.sidebar.text_input('비밀번호', type='password')
    login_btn = st.sidebar.button('로그인')
    if login_btn:
        user_info = login_user(login_id, login_pw)
        if user_info:
            st.subheader(user_info[2]+'님 환영합니다.')
            st.image(user_info[0]+'.jpg',width=500)
        else:
            st.subheader('다시 로그인하세요')

if menu == '회원목록':
    st.subheader('회원목록')
    df = pd.read_sql("SELECT name, age, gender FROM users", con)
    st.dataframe(df, 500,280)

if menu == '서울 지키미':
    df = pd.read_csv('Project(Seoul).csv',encoding='cp949')
    df_area = df['자치구']
    df_area = df[['위도','경도']]
    ####################### If loading takes a long time
    # count = []
    # for i in range(0, 61540, 30):
    #     count.append(i)
    # df_area = df_area.loc[count, :]
    #######################

    r = ['서울', '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구',
         '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구',
         '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구']

    C = ['black', 'darkred', 'orange', 'green', 'cadetblue', 'lightgray', 'beige']

    st.title('서울 지키미!')

    region = st.selectbox(
        'OO구 CCTV',
        r)

    color = st.selectbox(
        'CCTV 색상',
        C)

    st.subheader('서울시 '+region+' CCTV 현황!!')

    if region == '서울':
        zoom = 11
    elif region == '강남구':
        zoom = 13.3
    else:
        zoom = 14

    def l(x):
        return {r[0]: (37.5539471, 127.0051205), r[1]: (37.494422408892, 127.06315179125),
                r[2]: (37.547926, 127.143313), r[10]: (37.6687738, 127.0470706), r[18]: (37.5102663, 127.1121525),
                r[3]: (37.6350214, 127.0235954), r[11]: (37.5743682, 127.0600189), r[19]: (37.5177055, 126.867815),
                r[4]: (37.5530053, 126.8498756), r[12]: (37.5035179, 126.9478812), r[20]: (37.5263715, 126.9062283),
                r[5]: (37.4706002, 126.9433087), r[13]: (37.5573404, 126.9167535), r[21]: (37.5284272, 126.9904442),
                r[6]: (37.5384843, 127.0822938), r[14]: (37.5738942, 126.935254), r[22]: (37.606123, 126.922791),
                r[7]: (37.4968195, 126.8858694), r[15]: (37.4898354, 127.0152749), r[23]: (37.5789503, 126.9793579),
                r[8]: (37.4609402, 126.8984804), r[16]: (37.5633415, 127.0371025), r[24]: (37.5540907, 126.9979403),
                r[9]: (37.6541917, 127.069793), r[17]: (37.5952422, 127.0188196), r[25]: (37.5945602, 127.0926519),}.get(x, (37.5539471, 127.0051205))

    m = folium.Map(location=l(region), zoom_start=zoom)

    with open("boundary.txt", "r",encoding='UTF-8') as file:
        data = file.read()
    seoul_geo = json.loads(data)

    folium.GeoJson(
        seoul_geo,
        name="지역구"
    ).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)

    for lat, long in zip(df_area['위도'], df_area['경도']):
        folium.Marker([lat, long],
                      popup="방범용",
                      tooltip="방범용",
                      icon=folium.Icon(icon = 'facetime-video', color = color)).add_to(marker_cluster)

    st_data = st_folium(m, width = 725)