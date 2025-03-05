import streamlit as st

# 대시보드 레이아웃
st.set_page_config(layout="wide")

# 🔒 `secrets.toml`에서 비밀번호 가져오기
PASSWORD = st.secrets["general"]["password"]

# ✅ 세션 상태 초기화 (처음 접속할 때 한 번만 실행)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False  # 인증 상태 저장

def check_password():
    """비밀번호 입력이 올바른지 확인"""
    if not st.session_state.authenticated:
        password_container = st.empty()  # 비밀번호 입력 필드를 감싸는 컨테이너 생성
        password = password_container.text_input("🔑 비밀번호를 입력하세요:", type="password")

        if password:
            if password == PASSWORD:
                st.session_state.authenticated = True  # 인증 완료
                password_container.empty()  # ✅ 인증 후 입력 필드 삭제
                st.rerun()  # ✅ 페이지를 다시 실행하여 입력 필드가 완전히 사라지게 함
            else:
                st.error("❌ 비밀번호가 틀렸습니다. 다시 시도하세요.")

    return st.session_state.authenticated

if not check_password():
    st.stop()  # ❌ 비밀번호가 틀리면 코드 실행 중단

# ✅ 비밀번호 인증 후 실행되는 코드 (아래 원래 작성한 코드 유지)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import os
import gdown
import chardet

# 회사 로고 URL 또는 로컬 파일 경로 설정
logo_url = "https://cdn.worldvectorlogo.com/logos/publicis-groupe-vector-logo.svg" 

# 로고와 타이틀을 가로로 정렬하는 HTML + CSS 적용
st.markdown(
    f"""
    <div style="display: flex; align-items: center; margin-bottom: 30px;">
        <img src="{logo_url}" height="80" width="80" style="margin-right: 10px;">
        <h1 style="margin: 0; padding: 0;">Publicis Groupe Korea Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# 채널별 컬러 매핑
channel_colors = {
    "X(트위터)": "#9b1b1b",  # 어두운 버건디 레드 (강한 빨강 톤다운)
    "커뮤니티": "#8c4a33",  # 브라운 계열 (차분한 느낌)
    "네이버 카페": "#14532d",  # 다크 그린 (채도를 줄여 어두운 느낌)
    "다음 카페": "#8b0000",  # 어두운 레드 (톤 다운된 강한 색상)
    "인스타그램": "#702963",  # 다크 퍼플 (인스타 색상에서 채도 낮춤)
    "유튜브": "#8b1a1a",  # 유튜브 레드지만 다크톤 적용
    "블로그": "#20554e",  # 어두운 블루-그린 계열
    "티스토리": "#5c4033",  # 차분한 다크 브라운
    "네이버 뉴스": "#1e3a3a",  # 어두운 청록색
    "다음 뉴스": "#1e3799",  # 다크 네이비 블루
    "언론사 뉴스": "#2c3e50"  # 차분한 다크 블루그레이
}

# 브랜드 로고 URL
brand_logos = {
    "맥도날드": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/McDonald%27s_Golden_Arches.svg/1280px-McDonald%27s_Golden_Arches.svg.png",
    "버거킹": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Burger_King_2020.svg/330px-Burger_King_2020.svg.png",
    "롯데리아": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Lotteria_logo.svg/1920px-Lotteria_logo.svg.png"
}

# ✅ Google Drive 파일 ID 매핑
file_links = {
    "01.Social_Buzz_Monthly.csv": "1-2fNHis_rQvrOqrhvGUFqXL64OcGPvbn",
    "02.SearchVolume_Monthly.csv": "1r8LpCvwb-FvQvKnMqimE7xOnrMkr4hCf",
    "04.Sentiment_Buzz_Monthly.csv": "19mmYdWEbDdh0D2okPMFDqPjo0IkqdHl7",
    "05.Keyword_Monthly.csv": "1HutFBwcKVkDs_IR2vRlD3a7q-RzRwVLF",
    "06.Search_Keyword_Monthly.csv": "1U7iZU2iqnezsB_HGhYuH9akKD3h675jf",
    "07.Sentiment_Keyword_Monthly.csv": "1UbGxKX81iBJqbQB62IFDbVAOta5vcXko",
    "08.Search_Keyword_Gender_Monthly.csv": "1KzlKvy76zoQtc-Kx_xz1OauFHqO4cyrR",
    "09.Search_Keyword_Age_Monthly.csv": "1mooWsfx-YnqbGeyHFs4tinDb_70VIzt1"
}

# ✅ 데이터 저장 폴더 생성
data_dir = "Data"
os.makedirs(data_dir, exist_ok=True)

# ✅ Google Drive에서 파일 다운로드
def download_from_drive(file_name, file_id):
    file_path = os.path.join(data_dir, file_name)
    if not os.path.exists(file_path):  # 이미 존재하면 다운로드 생략
        file_url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(file_url, file_path, quiet=False)
    return file_path

# ✅ 인코딩 감지 함수
def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
    return result["encoding"]

# ✅ CSV 파일 로드 함수 (자동 인코딩 감지)
def load_csv_with_encoding(file_name):
    file_path = download_from_drive(file_name, file_links[file_name])
    encoding = detect_encoding(file_path)  # 자동 인코딩 감지
    try:
        return pd.read_csv(file_path, encoding=encoding)
    except Exception as e:
        st.error(f"⚠️ {file_name} 로드 중 오류 발생: {e}")
        return None

# ✅ 데이터 로드 실행
dataframes = {file_name: load_csv_with_encoding(file_name) for file_name in file_links.keys()}

# ✅ 날짜 형식 지정
date_formats = {
    "01.Social_Buzz_Monthly.csv": "%Y-%m",
    "02.SearchVolume_Monthly.csv": "%Y-%m",
    "04.Sentiment_Buzz_Monthly.csv": "%Y-%m",
    "05.Keyword_Monthly.csv": "%Y-%m-%d",
    "06.Search_Keyword_Monthly.csv": "%Y-%m",
    "07.Sentiment_Keyword_Monthly.csv": "%Y-%m-%d",
}

# ✅ 날짜 변환 적용
for file_name, date_format in date_formats.items():
    df = dataframes.get(file_name)
    if df is not None and "날짜" in df.columns:
        df["날짜"] = pd.to_datetime(df["날짜"], format=date_format, errors="coerce")
        df["연도-월"] = df["날짜"].dt.strftime("%Y-%m")

# ✅ 최종 데이터프레임 반환
df_buzz = dataframes.get("01.Social_Buzz_Monthly.csv")
df_search = dataframes.get("02.SearchVolume_Monthly.csv")
df_sentiment = dataframes.get("04.Sentiment_Buzz_Monthly.csv")
df_keywords = dataframes.get("05.Keyword_Monthly.csv")
df_search_keywords = dataframes.get("06.Search_Keyword_Monthly.csv")
df_sentiment_keyword = dataframes.get("07.Sentiment_Keyword_Monthly.csv")
df_search_keyword_gender = dataframes.get("08.Search_Keyword_Gender_Monthly.csv")
df_search_keyword_age = dataframes.get("09.Search_Keyword_Age_Monthly.csv")

if df_buzz is not None:
    max_date = df_buzz['날짜'].max()
    period_options = {
        "최근 3개월": max_date - pd.DateOffset(months=2),
        "최근 6개월": max_date - pd.DateOffset(months=5),
        "최근 12개월": max_date - pd.DateOffset(months=11),
        "최근 24개월": max_date - pd.DateOffset(months=23)
    }
    
    # 사이드바 옵션 구성
    with st.sidebar:
        st.header("🔍 필터링 옵션")
        selected_brand = st.selectbox("📌 브랜드 선택", df_buzz['브랜드'].unique())
        default_channels = ["X(트위터)", "커뮤니티", "네이버 카페", "인스타그램", "블로그"]
        dist_channels = [ch for ch in df_buzz['채널'].unique() if ch != "전체"]
        selected_channels = st.multiselect("📌 소셜미디어 채널 선택", dist_channels, default=[ch for ch in default_channels if ch in dist_channels])
        selected_period = st.selectbox("📆 기간 선택", list(period_options.keys()), index=3)
        
    # 1번 탭 데이터 (소셜 미디어)
    # 소셜 버즈 카드 데이터 필터링
    df_buzz_card = df_buzz[(df_buzz['브랜드'].isin(["맥도날드", "버거킹", "롯데리아"])) & 
                           (df_buzz['날짜'] >= period_options[selected_period]) & 
                           (df_buzz['채널'].isin(selected_channels))]
    
    # 소셜 버즈 추이 데이터 필터링
    df_filtered = df_buzz[(df_buzz['브랜드'] == selected_brand) & 
                          (df_buzz['채널'].isin(selected_channels)) & 
                          (df_buzz['날짜'] >= period_options[selected_period])]
    
    # 소셜 감성 비중 데이터 필터링
    df_sentiment_filtered = df_sentiment[(df_sentiment['브랜드'] == selected_brand) & 
                                         (df_sentiment['채널'].isin(selected_channels)) & 
                                         (df_sentiment['날짜'] >= period_options[selected_period])]
    
    # 소셜 연관어 데이터 필터링
    df_keywords_filtered = df_keywords[(df_keywords['브랜드'] == selected_brand) & 
                                       (df_keywords['채널'].isin(selected_channels)) &
                                       (df_keywords['날짜'] >= period_options[selected_period])]
    
    # 소셜 감성 연관어 데이터 필터링
    df_sentiment_keyword_filtered = df_sentiment_keyword[(df_sentiment_keyword['브랜드'] == selected_brand) & 
                                                    (df_sentiment_keyword['채널'].isin(selected_channels)) & 
                                                    (df_sentiment_keyword['날짜'] >= period_options[selected_period])]
    # 2번 탭 데이터 (검색 데이터)
    # 검색량 카드 데이터 필터링
    df_search_card = df_search[(df_search['브랜드'].isin(["맥도날드", "버거킹", "롯데리아"])) & 
                               (df_search['날짜'] >= period_options[selected_period])]
    
    # 검색량 추이 데이터 필터링
    df_search_filtered = df_search[(df_search['날짜'] >= period_options[selected_period]) & 
                                   (df_search['브랜드'] == selected_brand)]
    
    # 검색 키워드 데이터 필터링
    df_search_keywords_filtered = df_search_keywords[(df_search_keywords['브랜드'] == selected_brand) & 
                                                     (df_search_keywords['날짜'] >= period_options[selected_period])]
    
    # 검색 키워드 성별 데이터 필터링
    df_search_keyword_gender['브랜드'] = df_search_keyword_gender['브랜드'].astype(str)
    df_search_keyword_gender['기간'] = df_search_keyword_gender['기간'].astype(str)
    df_search_keyword_gender_filtered = df_search_keyword_gender[(df_search_keyword_gender['브랜드'] == selected_brand)]
    
    # 검색 키워드 연령 데이터 필터링
    df_search_keyword_age['브랜드'] = df_search_keyword_age['브랜드'].astype(str)
    df_search_keyword_age['기간'] = df_search_keyword_age['기간'].astype(str)
    df_search_keyword_age_filtered = df_search_keyword_age[(df_search_keyword_age['브랜드'] == selected_brand)]

    # 데이터 추가 필터링  
    # 월별 언급량 및 검색량 집계 - 추이 그래프
    df_buzz_monthly = df_filtered.groupby(['연도-월', '채널'])['언급량'].sum().reset_index()
    df_search_monthly = df_search_filtered.groupby(['연도-월'])['검색량'].sum().reset_index()
    
    # 월별 언급량 및 검색량 집계 - 카드 데이터
    df_buzz_card_monthly = df_buzz_card.groupby(['연도-월', '브랜드'])['언급량'].sum().reset_index()
    df_search_card_monthly = df_search_card.groupby(['연도-월', '브랜드'])['검색량'].sum().reset_index()

    # 카드 데이터(소셜 미디어) - 브랜드별 언급량 및 검색량 합계 계산
    total_mentions = df_buzz_card['언급량'].sum()
    total_searches = df_search_card['검색량'].sum()

    # 카드 데이터(검색 데이터) - 브랜드별 검색량 및 검색량 합계 계산
    brand_mentions = df_buzz_card.groupby('브랜드')['언급량'].sum().to_dict()
    brand_search = df_search_card.groupby('브랜드')['검색량'].sum().to_dict()

    # 탭 추가
    tab1, tab2, tab3 = st.tabs(["📊 소셜 미디어 분석", "🔎 검색 데이터 분석", "📈 키워드 분석"])
    
    with tab1:
        st.markdown(f"**{selected_period} 브랜드 소셜미디어 언급량 비교**")

        # 컬럼 크기는 일정하게 유지
        col1, col2, col3 = st.columns(3)

        # 브랜드별 로고 크기 설정 (width, height)
        logo_sizes = {
            "맥도날드": (100, 100),
            "버거킹": (100, 100),
            "롯데리아": (300, 100)
        }

        for col, brand in zip([col1, col2, col3], ["맥도날드", "버거킹", "롯데리아"]):
            width, height = logo_sizes[brand]  # 브랜드별 이미지 크기 가져오기
            percentage = (brand_mentions.get(brand, 0) / total_mentions * 100) if total_mentions else 0
            
            col.markdown(
                f"""
                <div style="text-align: center;">
                    <img src="{brand_logos[brand]}" width="{width}" height="{height}"><br>
                    <span style="font-size: 40px; font-weight: bold;">{brand_mentions.get(brand, 0):,}</span>
                    <span style="font-size: 30px;">({percentage:.1f}%)</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    
        # 언급량 추이 그래프
        fig_buzz = px.bar(
            df_buzz_monthly,
            x='연도-월',
            y='언급량',
            color='채널',
            barmode='stack',
            title=f"{selected_brand} {selected_period} 월별 소셜미디어 언급량 변화",
            color_discrete_map=channel_colors
        )
        fig_buzz.update_layout(
            xaxis_title=None, 
            yaxis_title=None, 
            xaxis=dict(type='category', tickangle=0), 
            showlegend=False
        )
        fig_buzz.update_traces(marker=dict(line=dict(width=0)))
        st.plotly_chart(fig_buzz, use_container_width=True)
        
        # 감성 언급량 추이 그래프
        df_sentiment_monthly = df_sentiment_filtered.groupby(['연도-월', '채널', '감성'])['언급량'].sum().reset_index()
        df_sentiment_monthly['총합'] = df_sentiment_monthly.groupby('연도-월')['언급량'].transform('sum')
        df_sentiment_monthly['비율'] = df_sentiment_monthly['언급량'] / df_sentiment_monthly['총합'] * 100
    
        fig_sentiment = px.bar(
        df_sentiment_monthly,
        x='연도-월',
        y='비율',
        color='감성',
        barmode='stack',
        title=f"{selected_brand} {selected_period} 감성별 비율 변화",
        color_discrete_map = { "긍정": "#00008B", "부정": "#8B0000", "중립": "#4E4E50"}
        )
        
        fig_sentiment.update_layout(
            xaxis_title=None, 
            yaxis_title=None, 
            xaxis=dict(type='category', tickangle=0), 
            showlegend=False
        )
        
        fig_sentiment.update_traces(marker=dict(line=dict(width=0)))
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
        # 소셜미디어 연관어 데이터 월별 언급량  
        df_top_keywords = df_keywords_filtered.groupby(['연도-월', '연관어'])['언급량'].sum().reset_index()
        df_top_keywords = df_top_keywords.sort_values(by=['연도-월', '언급량'], ascending=[True, False])
        df_top_keywords = df_top_keywords.groupby('연도-월').head(100)
    
        # 소셜미디어 연관어 데이터 와이드 형태 변환 함수 선언
        def transform_to_merged_header_format(df):
            df_pivot = df.pivot(index="연관어", columns="연도-월", values="언급량").fillna(0).astype(int)
            df_pivot = df_pivot.reindex(sorted(df_pivot.columns), axis=1)
            column_tuples = [(month, "연관어") for month in df_pivot.columns] + [(month, "언급량") for month in df_pivot.columns]
        
            df_final = pd.DataFrame(columns=pd.MultiIndex.from_tuples(column_tuples))

            for month in df_pivot.columns:
                sorted_keywords = df[df['연도-월'] == month][['연관어', '언급량']].reset_index(drop=True)
                df_final[(month, "연관어")] = sorted_keywords["연관어"]
                df_final[(month, "언급량")] = sorted_keywords["언급량"]
        
            return df_final

        # 소셜미디어 연관어 데이터 와이드 형태 변환 함수 적용
        df_keywords_table = transform_to_merged_header_format(df_top_keywords)

        # 멀티인덱스 컬럼 정렬 (연도-월 순서 유지하면서 '연관어' → '언급량' 반복)
        sorted_columns = sorted(df_keywords_table.columns.levels[0])  # 연도-월 정렬
        new_column_order = [(month, sub_col) for month in sorted_columns for sub_col in ["연관어", "언급량"]]

        # 새로운 컬럼 순서 적용
        df_keywords_table = df_keywords_table[new_column_order]
        
        # 연관어 테이블 출력
        st.markdown(f"**{selected_brand} {selected_period} 소셜미디어 월별 연관어 변화**")
        st.dataframe(df_keywords_table, use_container_width=True, hide_index=True)
        
        #-----------------------------------------------
        # 감성어 데이터 변환 함수 (월별 언급량 내림차순 정렬 추가)
        def transform_to_sentiment_keyword_format(df, selected_sentiment):
            if df.empty:
                return pd.DataFrame()  # 데이터가 없으면 빈 DataFrame 반환
            
            # ✅ 중복 데이터 합산 처리 (연관어, 감성, 연도-월 기준으로 언급량 합산)
            df_grouped = df.groupby(['연관어', '감성', '연도-월'])['언급량'].sum().reset_index()

            # ✅ 감성 필터링
            df_filtered = df_grouped[df_grouped["감성"] == selected_sentiment]

            # ✅ 월별로 언급량 기준 내림차순 정렬 후 상위 100개 유지
            df_sorted = df_filtered.sort_values(by=['연도-월', '언급량'], ascending=[True, False])
            df_sorted = df_sorted.groupby('연도-월').head(100)  # 각 월별 상위 100개 감성어 유지

            # ✅ 피벗 변환 (이제 중복 없음)
            df_pivot = df_sorted.pivot(index="연관어", columns="연도-월", values="언급량").fillna(0).astype(int)

            # ✅ 멀티인덱스 컬럼명 생성
            column_tuples = [(month, "연관어") for month in df_pivot.columns] + [(month, "언급량") for month in df_pivot.columns]
            df_final = pd.DataFrame(columns=pd.MultiIndex.from_tuples(column_tuples))

            # ✅ 월별 정렬 반영하여 감성어 데이터 채우기
            for month in df_pivot.columns:
                sorted_keywords = df_sorted[df_sorted['연도-월'] == month][['연관어', '언급량']].reset_index(drop=True)
                if not sorted_keywords.empty:  # ✅ 빈 데이터 예외 처리
                    df_final[(month, "연관어")] = sorted_keywords["연관어"]
                    df_final[(month, "언급량")] = sorted_keywords["언급량"]

            return df_final

        # ✅ UI에 감성어 데이터 테이블 표시
        col_title, col_select = st.columns([8, 2])
        with col_title:
            st.markdown(f"**{selected_brand} {selected_period} 소셜미디어 월별 감성어 변화**")
        with col_select:
            selected_sentiment = st.selectbox("감성 선택", ["긍정", "부정", "중립"], key="sentiment_select1")

        # ✅ 감성어 필터링 (브랜드, 채널, 날짜 필터 유지)
        df_sentiment_keyword_filtered_selected = df_sentiment_keyword_filtered[
            df_sentiment_keyword_filtered["감성"] == selected_sentiment
        ]

        # ✅ 변환 함수 적용하여 감성어 데이터 가공 (월별 내림차순 정렬 추가)
        df_sentiment_table = transform_to_sentiment_keyword_format(df_sentiment_keyword_filtered_selected, selected_sentiment)

        # ✅ 테이블이 비어있지 않다면 표시
        if not df_sentiment_table.empty:
            sorted_columns = sorted(df_sentiment_table.columns.levels[0])
            new_column_order = [(month, sub_col) for month in sorted_columns for sub_col in ["연관어", "언급량"]]
            df_sentiment_table = df_sentiment_table[new_column_order]

            st.dataframe(df_sentiment_table, use_container_width=True, hide_index=True)
        else:
            st.info("데이터가 없습니다.")

        #-----------------------------------------------

    with tab2:
        st.markdown(f"**{selected_period} 브랜드 검색량 비교**")

        # 컬럼 크기는 일정하게 유지
        col1, col2, col3 = st.columns(3)

        # 브랜드별 로고 크기 설정 (width, height)
        logo_sizes = {
            "맥도날드": (100, 100),
            "버거킹": (100, 100),
            "롯데리아": (300, 100)
        }
        
        for col, brand in zip([col1, col2, col3], ["맥도날드", "버거킹", "롯데리아"]):
            width, height = logo_sizes[brand]  # 브랜드별 이미지 크기 가져오기
            percentage = (brand_search.get(brand, 0) / total_searches * 100) if total_searches else 0

            col.markdown(
                f"""
                <div style="text-align: center;">
                    <img src="{brand_logos[brand]}" width="{width}" height="{height}"><br>
                    <span style="font-size: 40px; font-weight: bold;">{brand_search.get(brand, 0):,}</span>
                    <span style="font-size: 30px;">({percentage:.1f}%)</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        # 검색량 추이 그래프
        fig_search = px.bar(
            df_search_monthly,
            x='연도-월',
            y='검색량',
            barmode='group',
            title=f"{selected_brand} {selected_period} 월별 검색량 변화",
            color_discrete_sequence=["#4B0082"]
        )
        fig_search.update_layout(
            xaxis_title=None, 
            yaxis_title=None, 
            xaxis=dict(type='category', tickangle=0)
        )
        fig_search.update_traces(marker=dict(line=dict(width=0)))
        st.plotly_chart(fig_search, use_container_width=True)
            
        # 검색 키워드 데이터 와이드 형태 변환 함수 선언
        def transform_to_merged_header_format(df, column_name, value_column):
            df_top_keywords = df.groupby(['연도-월', column_name])[value_column].sum().reset_index()
            df_top_keywords = df_top_keywords.sort_values(by=['연도-월', value_column], ascending=[True, False])
            df_top_keywords = df_top_keywords.groupby('연도-월').head(100)
        
            df_pivot = df_top_keywords.pivot(index=column_name, columns="연도-월", values=value_column).fillna(0).astype(int)
            df_pivot = df_pivot.reindex(sorted(df_pivot.columns), axis=1)
            column_tuples = [(month, column_name) for month in df_pivot.columns] + [(month, value_column) for month in df_pivot.columns]
        
            df_final = pd.DataFrame(columns=pd.MultiIndex.from_tuples(column_tuples))
            for month in df_pivot.columns:
                sorted_keywords = df_top_keywords[df_top_keywords['연도-월'] == month][[column_name, value_column]].reset_index(drop=True)
                df_final[(month, column_name)] = sorted_keywords[column_name]
                df_final[(month, value_column)] = sorted_keywords[value_column]
        
            return df_final

        # 검색 키워드 데이터 와이드 형태 변환 함수 적용   
        df_search_keywords_table = transform_to_merged_header_format(df_search_keywords_filtered, "키워드", "검색량")

        # 멀티인덱스 컬럼 정렬 (연도-월 순서 유지하면서 '키워드' → '검색량' 반복)
        sorted_columns = sorted(df_search_keywords_table.columns.levels[0])  # 연도-월 정렬
        new_column_order = [(month, sub_col) for month in sorted_columns for sub_col in ["키워드", "검색량"]]

        # 새로운 컬럼 순서 적용
        df_search_keywords_table = df_search_keywords_table[new_column_order]    
        st.markdown(f"**{selected_brand} {selected_period} 월별 검색 키워드 변화**")
        st.dataframe(df_search_keywords_table, use_container_width=True, hide_index=True)

        # 두 개의 컬럼 생성
        col1, col2 = st.columns([1, 2])

        # 검색 키워드 성별 비율 데이터
        with col1:  # ✅ 왼쪽 컬럼에 배치
            search_period = df_search_keyword_gender_filtered['기간'].iloc[0]
            df_gender_keywords_filtered = df_search_keyword_gender_filtered[['키워드', '검색량', '남성(%)', '여성(%)']]
            df_gender_keywords_filtered = df_gender_keywords_filtered.sort_values(by='검색량', ascending=False)

            # 🔄 검색 키워드 성별 비율 데이터 프레임 출력
            st.markdown(f"**{selected_brand} 검색 키워드 성별 비율 (기간: {search_period})**")
            st.dataframe(df_gender_keywords_filtered, use_container_width=True, hide_index=True)

        # 오른쪽 `col2`에는 다른 콘텐츠 추가 가능
        with col2:
            search_period = df_search_keyword_age_filtered['기간'].iloc[0]
            df_search_keyword_age_filtered = df_search_keyword_age_filtered[['키워드', '검색량', 
                                                                             '12세 이하(%)', '13~19세(%)', '20~24세(%)', '25~29세(%)',
                                                                             '30~39세(%)', '40~49세(%)', '50세 이상(%)']]
            df_search_keyword_age_filtered = df_search_keyword_age_filtered.sort_values(by='검색량', ascending=False)
            st.markdown(f"**{selected_brand} 검색 키워드 연령 비율 (기간: {search_period})**")
            st.dataframe(df_search_keyword_age_filtered, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown(f"**{selected_brand} {selected_period} 키워드 분석**")

        # 세 개의 컬럼 생성 (키워드 유형 선택, 감성 선택, 순위 선택)
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            keyword_type = st.selectbox("키워드 유형 선택", ["연관어", "감성어", "검색어"])  # ✅ 검색어 추가
        
        with col2:
            rank_range_options = {
                "1위~12위": (1, 12),
                "13위~24위": (13, 24),
                "25위~36위": (25, 36),
                "37위~48위": (37, 48),
                "49위~60위": (49, 60)
            }
            selected_range = st.selectbox("키워드 순위 선택", options=list(rank_range_options.keys()))
            start_rank, end_rank = rank_range_options[selected_range]
        
        with col3:
            if keyword_type == "감성어":
                selected_sentiment = st.selectbox("감성 선택", ["긍정", "부정", "중립"], key="sentiment_select")
            else:
                selected_sentiment = "해당 없음"
                st.selectbox("감성 선택", ["해당 없음"], disabled=True)

        # ✅ 선택된 키워드 유형에 따라 데이터 필터링
        if keyword_type == "연관어":
            df_selected = df_keywords_filtered
            keyword_column = "연관어"
        elif keyword_type == "감성어":
            df_selected = df_sentiment_keyword_filtered[df_sentiment_keyword_filtered["감성"] == selected_sentiment]
            keyword_column = "연관어"
        elif keyword_type == "검색어":
            df_selected = df_search_keywords_filtered  # ✅ 검색어 데이터 적용
            keyword_column = "키워드"

        if not df_selected.empty:
            # ✅ 채널 구분 없이 전체 합산하여 데이터 정리
            df_selected = df_selected.groupby([keyword_column, "연도-월"])["검색량" if keyword_type == "검색어" else "언급량"].sum().reset_index()
            df_selected = df_selected.sort_values(by="연도-월")

            def get_top_keywords(df, start_rank, end_rank):
                return df.groupby(keyword_column)["검색량" if keyword_type == "검색어" else "언급량"].sum().nlargest(end_rank).iloc[start_rank-1:end_rank].index

            top_keywords = get_top_keywords(df_selected, start_rank, end_rank)
            df_selected = df_selected[df_selected[keyword_column].isin(top_keywords)]

            rows, cols = 4, 3
            fig = sp.make_subplots(
                rows=rows, cols=cols,
                subplot_titles=[f"<b>{keyword}</b>" for keyword in top_keywords[:rows*cols]]
            )

            # ✅ 원래 사용했던 컬러 매핑 적용
            color_map = {
                "연관어": "#4B0082",  # Dark Purple
                "긍정": "#00008B",  # Dark Blue
                "부정": "#8B0000",  # Dark Red
                "중립": "#4E4E50",  # Gray
                "검색어": "#008B8B"  # Dark Cyan
            }
            bar_color = color_map[keyword_type] if keyword_type in color_map else color_map[selected_sentiment]

            r, c = 1, 1
            for keyword in top_keywords[:rows * cols]:
                keyword_data = df_selected[df_selected[keyword_column] == keyword]
                x_values = pd.to_datetime(keyword_data["연도-월"] + "-01")

                # ✅ 채널별 구분 없이 하나의 막대그래프 유지
                fig.add_trace(
                    go.Bar(
                        x=x_values,
                        y=keyword_data["검색량" if keyword_type == "검색어" else "언급량"],
                        name=keyword,
                        marker_color=bar_color
                    ),
                    row=r, col=c
                )

                c += 1
                if c > cols:
                    c = 1
                    r += 1

            fig.update_layout(
                height=800,
                width=1800,
                title_text="",
                title_x=0.5,
                showlegend=False,
                plot_bgcolor="#0e1117",
                paper_bgcolor="#0e1117",
                font=dict(color="white"),
                margin=dict(l=40, r=40, t=60, b=40)
            )

            for i in range(1, rows * cols + 1):
                fig.update_yaxes(
                    showgrid=False,
                    gridcolor='#d3d3d3',
                    gridwidth=0.1,
                    row=(i - 1) // cols + 1,
                    col=(i - 1) % cols + 1,
                    tickfont=dict(color="white"),
                    tickformat="~s"
                )
                fig.update_xaxes(
                    type="date",
                    dtick="M1",
                    tickformat="%y-%m",
                    showgrid=False,
                    row=(i - 1) // cols + 1,
                    col=(i - 1) % cols + 1,
                    tickangle=-45 if selected_period in ["최근 24개월", "최근 12개월"] else 0,
                    tickfont=dict(color="white", size=10 if selected_period == "최근 24개월" else 13)
                )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")
