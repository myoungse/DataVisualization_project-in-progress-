from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import json
from datetime import datetime
import urllib.parse
import re
from difflib import SequenceMatcher
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Chrome 드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# options.add_argument('--headless')  # 필요시 주석 해제

chrome_driver_path = r"C:\Users\ekbin\.wdm\drivers\chromedriver\win64\136.0.7103.113\chromedriver-win32\chromedriver.exe"
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

def scroll_down():
    """페이지 스크롤"""
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

def is_urgent_acceleration_news(title, content=""):
    """급발진 관련 뉴스인지 확인"""
    keywords = ['급발진', '갑발진', '급가속']
    text_to_check = (title + " " + content).lower()

    # 제외할 단어들
    exclude_words = ['일본', '패소', '소송']  # 원하는 단어 추가
    
    # 제외 단어가 포함된 기사는 제외
    for exclude_word in exclude_words:
        if exclude_word in text_to_check:
            return False
    
    return any(keyword in text_to_check for keyword in keywords)

def calculate_similarity(text1, text2):
    """두 텍스트의 유사도 계산 (0~1)"""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def extract_accident_keywords(title, content):
    """8개 키워드 추출 (정확한 단일 값 추출)"""
    text = title + " " + content
    
    keywords = {
        'gender': None,             # 1. 성별
        'age': None,                # 2. 나이
        'car_model': None,          # 3. 차 모델
        'brake_status': None,       # 4. 브레이크 작동 여부
        'accident_location': None,  # 5. 사고 장소
        'accident_result': None,    # 6. 사고 결과
        'accident_time': None,      # 7. 사고 발생 시점
        'drunk_driving': None       # 8. 음주 운전 여부
    }
    
    # 1. 성별 추출
    gender_patterns = [
        r'([0-9]+대|[0-9]+세)\s*(남성|여성)',
        r'(남성|여성)\s*([0-9]+대|[0-9]+세)',
        r'(남성|여성)\s*운전자',
        r'운전자\s*(남성|여성)',
        r'(남|여)\([0-9]+\)',
        r'([0-9]+대|[0-9]+세)\s*(남|여)',
        r'(남|여)\s*([0-9]+대|[0-9]+세)'
    ]
    for pattern in gender_patterns:
        match = re.search(pattern, text)
        if match:
            gender_text = match.group()
            if '남성' in gender_text or '남' in gender_text:
                keywords['gender'] = '남'
            elif '여성' in gender_text or '여' in gender_text:
                keywords['gender'] = '여'
            break
    
    # 2. 나이 추출
    age_patterns = [
        r'([0-9]+)대',
        r'([0-9]+)세',
        r'([0-9]+)살',
        r'\(([0-9]+)\)'
    ]
    for pattern in age_patterns:
        match = re.search(pattern, text)
        if match:
            age_num = int(match.group(1))
            if age_num > 10 and age_num < 100:  # 나이 범위 체크
                age_decade = (age_num // 10) * 10
                keywords['age'] = f'{age_decade}대'
                break
            elif age_num >= 100:  # 세 자리 수는 연도일 가능성
                continue
    
    # 3. 차 모델 추출
    car_patterns = [
        r'(SUV|승용차|세단|해치백|쿠페|컨버터블|RV|미니밴|왜건)',
        r'(소나타|아반떼|그랜저|싼타페|투싼|스포티지|K[0-9]+|SM[0-9]+)',
        r'(현대|기아|삼성|쌍용|르노|BMW|벤츠|아우디|토요타|혼다)\s*([가-힣A-Za-z0-9]+)',
        r'(제네시스|카니발|모하비|코란도)'
    ]
    for pattern in car_patterns:
        match = re.search(pattern, text)
        if match:
            car_text = match.group()
            # 승용차, SUV 등 차종 우선
            if any(car_type in car_text for car_type in ['SUV', '승용차', '세단', '해치백']):
                keywords['car_model'] = car_text
                break
            else:
                keywords['car_model'] = car_text
    
    # 4. 브레이크 작동 여부
    brake_patterns = [
        r'브레이크\s*(작동|안\s*됨|되지\s*않|고장|실패|밟았지만|안\s*들)',
        r'제동\s*(장치|실패|불가|안\s*됨)',
        r'(브레이크를\s*밟았지만|브레이크가\s*안|제동이\s*안)'
    ]
    for pattern in brake_patterns:
        match = re.search(pattern, text)
        if match:
            brake_text = match.group()
            if any(word in brake_text for word in ['안', '불가', '실패', '고장', '되지않', '밟았지만']):
                keywords['brake_status'] = '작동 안됨'
            else:
                keywords['brake_status'] = '작동됨'
            break
    
    # 5. 사고 장소 추출 (더 정확한 패턴으로)
    location_patterns = [
        # 가장 상세한 주소부터 우선 검색
        # 시-구-동-구체적장소
        r'([가-힣]+시\s+[가-힣]+구\s+[가-힣]+동\s+[가-힣]+\s*(?:삼거리|사거리|교차로|인근|일대))',
        r'([가-힣]+시\s+[가-힣]+구\s+[가-힣]+동\s+[가-힣]+(?:아파트|빌딩|상가|마트|병원|학교|시장|주차장))',
        # 시-구-구체적장소
        r'([가-힣]+시\s+[가-힣]+구\s+[가-힣]+\s*(?:삼거리|사거리|교차로|인근|일대))',
        r'([가-힣]+시\s+[가-힣]+구\s+[가-힣]+(?:아파트|빌딩|상가|마트|병원|학교|시장|주차장))',
        # 구-동-구체적장소
        r'([가-힣]+구\s+[가-힣]+동\s+[가-힣]+\s*(?:삼거리|사거리|교차로|인근|일대))',
        r'([가-힣]+구\s+[가-힣]+동\s+[가-힣]+(?:아파트|빌딩|상가|마트|병원|학교|시장|주차장))',
        # 시-구-동
        r'([가-힣]+시\s+[가-힣]+구\s+[가-힣]+동)',
        # 시-구
        r'([가-힣]+시\s+[가-힣]+구)',
        # 구-동
        r'([가-힣]+구\s+[가-힣]+동)',
        # 완전한 고속도로명 (부분 매칭 방지)
        r'([가-힣]+고속도로)',
        # 완전한 국도명
        r'([0-9]+번\s*국도)',
        # 구체적인 도로명 (단순 "로"는 제외)
        r'([가-힣]{2,}로)\s*[0-9]*번길',
        r'([가-힣]{3,}로)(?!\s*[가-힣])',  # 3글자 이상의 도로명
        # 구체적인 건물명
        r'([가-힣]{2,}(?:아파트|빌딩|상가|마트|병원|학교|시장|주차장|터널|교차로|사거리))',
        # 지하주차장
        r'([가-힣]+(?:아파트|빌딩|상가))\s*지하주차장'
    ]
    
    # 제외할 단어들 (더 포괄적으로)
    exclude_words = [
        '당시', '음주', '운전', '상태', '측정', '검사', '확인', '조사', '발표', '보도', 
        '기자', '뉴스', '사건', '사고', '시속', '속도', '브레이크', '제동', '급발진',
        '차량', '승용차', '운전자', '피해', '부상', '사망'
    ]
    
    # 너무 짧거나 의미없는 결과 제외
    invalid_patterns = [
        r'^[가-힣]{1}$',  # 한 글자
        r'^속도로$',       # "속도로" 직접 제외
        r'^[0-9]+$',       # 숫자만
        r'^[가-힣]로$'     # "X로" 형태 (너무 짧은 도로명)
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text)
        if match:
            location = match.group(1).strip()
            
            # 제외 단어 체크
            if any(exclude_word in location for exclude_word in exclude_words):
                continue
                
            # 무효한 패턴 체크
            if any(re.match(invalid_pattern, location) for invalid_pattern in invalid_patterns):
                continue
                
            # 너무 짧은 단어 제외 (2글자 미만)
            if len(location) < 2:
                continue
                
            keywords['accident_location'] = location
            break
    
    # 만약 위에서 찾지 못했다면, 더 관대한 패턴으로 재시도
    if not keywords['accident_location']:
        fallback_patterns = [
            r'([가-힣]+시)(?:\s|에서|의|,)',
            r'([가-힣]+구)(?:\s|에서|의|,)',
            r'([가-힣]+동)(?:\s|에서|의|,)'
        ]
        
        for pattern in fallback_patterns:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                if len(location) >= 2 and not any(exclude_word in location for exclude_word in exclude_words):
                    keywords['accident_location'] = location
                    break
    
    # 6. 사고 결과 추출 (정확한 형식으로)
    # 먼저 복합적인 사고 결과 찾기
    complex_patterns = [
        r'([0-9]+)명\s*(중상|경상|부상).*?([0-9]+)명\s*(사망)',
        r'([0-9]+)명\s*(사망).*?([0-9]+)명\s*(중상|경상|부상)',
        r'(중상|경상|부상)\s*([0-9]+)명.*?(사망)\s*([0-9]+)명',
        r'(사망)\s*([0-9]+)명.*?(중상|경상|부상)\s*([0-9]+)명'
    ]
    
    for pattern in complex_patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if '사망' in groups and ('중상' in groups or '경상' in groups or '부상' in groups):
                # 사망자와 부상자가 모두 있는 경우
                if groups[1] == '사망':
                    death_count = groups[0]
                    injury_count = groups[2]
                    injury_type = groups[3]
                else:
                    injury_count = groups[0]
                    injury_type = groups[1]
                    death_count = groups[2]
                keywords['accident_result'] = f'{injury_type} {injury_count}명, 사망 {death_count}명'
                break
    
    # 복합 결과가 없으면 단일 결과 찾기
    if not keywords['accident_result']:
        single_patterns = [
            r'([0-9]+)명\s*(사망|숨짐)',
            r'(사망자)\s*([0-9]+)명',
            r'([0-9]+)명\s*(중상)',
            r'([0-9]+)명\s*(경상)',
            r'([0-9]+)명\s*(부상|다쳐)',
            r'(부상자)\s*([0-9]+)명',
            r'(인명피해)\s*(없)',
            r'(물적피해|재산피해)만'
        ]
        
        for pattern in single_patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if '사망' in groups[1] or '숨짐' in groups[1]:
                    keywords['accident_result'] = f'사망 {groups[0]}명'
                elif groups[1] in ['중상', '경상', '부상', '다쳐']:
                    keywords['accident_result'] = f'{groups[1]} {groups[0]}명'
                elif '인명피해' in groups[0] and '없' in groups[1]:
                    keywords['accident_result'] = '인명피해 없음'
                elif '물적피해' in groups[0] or '재산피해' in groups[0]:
                    keywords['accident_result'] = '물적피해만'
                break
    
    # 7. 사고 발생 시점 (정확한 시간으로)
    time_patterns = [
        # 구체적인 시간 (오전/오후 + 시 + 분)
        r'(오전|오후|새벽|밤)\s*([0-9]+)시\s*([0-9]+)분',
        # 시간만 (오전/오후 + 시)
        r'(오전|오후|새벽|밤)\s*([0-9]+)시',
        # 24시간 형식
        r'([0-9]+)시\s*([0-9]+)분',
        r'([0-9]+)시(?!간)',  # '시간'이 아닌 '시'만
        # 날짜 + 시간
        r'([0-9]+)일\s*(오전|오후|새벽|밤)\s*([0-9]+)시',
        # 상대적 시간
        r'(어제|오늘|그제)\s*(오전|오후|새벽|밤)\s*([0-9]+)시'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 3 and groups[2]:  # 분까지 있는 경우
                if groups[2].isdigit():  # 분이 숫자인지 확인
                    keywords['accident_time'] = f'{groups[0]} {groups[1]}시 {groups[2]}분'
                else:  # 시만 있는 경우
                    keywords['accident_time'] = f'{groups[0]} {groups[1]}시'
            elif len(groups) == 2 and groups[1]:
                if groups[1].isdigit():
                    keywords['accident_time'] = f'{groups[0]} {groups[1]}시'
                else:
                    keywords['accident_time'] = f'{groups[0]} {groups[1]}'
            else:
                keywords['accident_time'] = match.group()
            break
    
    # 8. 음주 운전 여부
    drunk_patterns = [
        r'음주\s*(운전|상태|측정)',
        r'술\s*(마시고|취한|먹고)',
        r'혈중\s*알코올\s*농도',
        r'알코올\s*검출'
    ]
    
    sober_patterns = [
        r'음주\s*(아닌|하지\s*않|안\s*한)',
        r'술\s*(마시지\s*않|안\s*마)',
        r'음주\s*상태\s*아님',
        r'알코올\s*검출\s*안'
    ]
    
    # 음주 아님 먼저 체크
    for pattern in sober_patterns:
        match = re.search(pattern, text)
        if match:
            keywords['drunk_driving'] = '아님'
            break
    
    # 음주 의심 체크
    if not keywords['drunk_driving']:
        for pattern in drunk_patterns:
            match = re.search(pattern, text)
            if match:
                keywords['drunk_driving'] = '의심'
                break
    
    return keywords

def extract_core_content(title, content):
    """기사의 핵심 내용 추출"""
    text = title + " " + content
    
    # 사건의 핵심 요소들 추출
    core_elements = []
    
    # 인명 패턴
    name_patterns = [r'[가-힣]{2,3}(?=씨|님|군|양)', r'[가-힣]{2,3}(?=\([0-9]+\))']
    for pattern in name_patterns:
        matches = re.findall(pattern, text)
        core_elements.extend(matches)
    
    # 장소 패턴
    location_patterns = [r'[가-힣]+시', r'[가-힣]+구', r'[가-힣]+동']
    for pattern in location_patterns:
        matches = re.findall(pattern, text)
        core_elements.extend(matches)
    
    # 법원, 판결 관련 키워드
    legal_keywords = ['패소', '승소', '기각', '인용', '판결', '법원', '재판부', '항소', '상고']
    for keyword in legal_keywords:
        if keyword in text:
            core_elements.append(keyword)
    
    # 사고 관련 키워드
    accident_keywords = ['급발진', '사고', '추돌', '충돌']
    for keyword in accident_keywords:
        if keyword in text:
            core_elements.append(keyword)
    
    return ' '.join(core_elements)

def calculate_content_hash(title, content):
    """기사 내용의 해시값 계산"""
    core_content = extract_core_content(title, content)
    return hashlib.md5(core_content.encode()).hexdigest()

def is_duplicate_article_advanced(new_title, new_content, new_keywords, existing_articles, threshold=0.85):
    """고도화된 중복 기사 판단"""
    
    # 1. 핵심 내용 해시 비교
    new_hash = calculate_content_hash(new_title, new_content)
    
    for article in existing_articles:
        existing_hash = calculate_content_hash(article['title'], article.get('content', ''))
        
        if new_hash == existing_hash:
            print(f"    ✗ 해시 중복 감지: 동일한 핵심 내용")
            return True
    
    # 2. TF-IDF 벡터 유사도 계산
    new_text = new_title + " " + new_content
    
    for article in existing_articles:
        existing_text = article['title'] + " " + article.get('content', '')
        
        # TF-IDF 벡터화
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,
            ngram_range=(1, 2)
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform([new_text, existing_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            if similarity >= threshold:
                print(f"    ✗ TF-IDF 유사도 중복 감지: {similarity:.3f}")
                print(f"      기존: {article['title'][:50]}...")
                print(f"      신규: {new_title[:50]}...")
                return True
                
        except Exception as e:
            continue
    
    # 3. 핵심 키워드 조합 비교
    def get_key_combination(title, keywords):
        """핵심 키워드 조합 생성"""
        key_parts = []
        
        # 인명이 있으면 추가
        name_match = re.search(r'[가-힣]{2,3}(?=씨|님|군|양)', title)
        if name_match:
            key_parts.append(name_match.group())
        
        # 키워드에서 핵심 정보 추가
        if keywords.get('accident_location'):
            # 장소에서 시/구만 추출
            location = keywords['accident_location']
            city_match = re.search(r'[가-힣]+시', location)
            district_match = re.search(r'[가-힣]+구', location)
            if city_match:
                key_parts.append(city_match.group())
            if district_match:
                key_parts.append(district_match.group())
        
        if keywords.get('accident_result'):
            # 사고 결과에서 핵심만 추출
            result = keywords['accident_result']
            if '사망' in result:
                key_parts.append('사망')
            if '부상' in result or '중상' in result or '경상' in result:
                key_parts.append('부상')
        
        # 제목에서 핵심 단어 추출
        key_words = ['급발진', '사고', '추돌', '충돌']
        for word in key_words:
            if word in title:
                key_parts.append(word)
        
        return '|'.join(sorted(set(key_parts)))  # 중복 제거 후 정렬
    
    new_combination = get_key_combination(new_title, new_keywords)
    
    for article in existing_articles:
        existing_combination = get_key_combination(article['title'], article['keywords'])
        
        if new_combination and existing_combination and new_combination == existing_combination:
            print(f"    ✗ 키워드 조합 중복 감지")
            print(f"      조합: {new_combination}")
            return True
    
    return False

def get_article_content(url):
    """기사 제목과 본문 추출 (중복 검사용으로 더 많은 내용 추출)"""
    try:
        driver.get(url)
        time.sleep(3)
        
        # 제목 추출
        title = ""
        title_selectors = ['.article_title', '.news_title', 'h1.title', 'h1']
        for selector in title_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                title = element.text.strip()
                if title:
                    break
            except:
                continue
        
        # 본문 추출 (중복 검사를 위해 더 많은 내용)
        content = ""
        content_selectors = ['.article_cont', '.news_cont', '.article_body', '.text_area', '.cont_area']
        for selector in content_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                full_content = element.text.strip()
                # 중복 검사를 위해 3000자까지 추출
                content = full_content[:3000] if full_content else ""
                if len(content) > 200:
                    break
            except:
                continue
        
        # 본문이 없으면 p 태그들에서 추출
        if not content:
            try:
                paragraphs = driver.find_elements(By.TAG_NAME, 'p')
                content_parts = []
                for p in paragraphs[:10]:  # 처음 10개 문단
                    text = p.text.strip()
                    if len(text) > 20:
                        content_parts.append(text)
                content = '\n'.join(content_parts)[:3000]
            except:
                content = ""
        
        return title, content
        
    except Exception as e:
        print(f"본문 추출 오류: {e}")
        return "", ""

def collect_urgent_acceleration_news(max_pages=51):
    """급발진 뉴스 수집 (고도화된 중복 제거)"""
    
    all_articles = []
    search_query = "급발진"
    
    print(f"급발진 뉴스 수집 시작 (최대 {max_pages}페이지)")
    
    for page in range(1, max_pages + 1):
        print(f"\n--- {page}페이지 수집 중 ---")
        
        encoded_query = urllib.parse.quote(search_query)
        search_url = f"https://news.sbs.co.kr/news/search/result.do?query={encoded_query}&tabIdx=2&pageIdx={page}&dateRange=all"
        
        try:
            driver.get(search_url)
            time.sleep(4)
            scroll_down()
            
            links = driver.find_elements(By.TAG_NAME, 'a')
            page_articles = []
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    link_text = link.text.strip()
                    
                    if (href and 'news.sbs.co.kr' in href and 
                        ('newsEndPage' in href or '/news/' in href) and
                        len(link_text) > 10):
                        
                        if is_urgent_acceleration_news(link_text):
                            if href.startswith('//'):
                                href = 'https:' + href
                            elif href.startswith('/'):
                                href = 'https://news.sbs.co.kr' + href
                            
                            # URL 중복 체크
                            if not any(article['url'] == href for article in all_articles):
                                page_articles.append({
                                    'title': link_text,
                                    'url': href
                                })
                                
                except Exception:
                    continue
            
            print(f"{page}페이지에서 {len(page_articles)}개 기사 발견")
            
            # 각 기사에서 키워드 추출
            for i, article_info in enumerate(page_articles, 1):
                print(f"  [{i}/{len(page_articles)}] {article_info['title'][:40]}... 처리중")
                
                title, content = get_article_content(article_info['url'])
                
                if not title:
                    title = article_info['title']
                
                if is_urgent_acceleration_news(title, content):
                    # 키워드 추출
                    keywords = extract_accident_keywords(title, content)
                    
                    # 8개 키워드 중 7개 이상이 null값인지 확인
                    null_count = sum(1 for value in keywords.values() if value is None)
                    if null_count >= 7:
                        print(f"    ✗ 키워드 부족으로 제외 (null값 {null_count}개/8개)")
                        continue
                    
                    # 고도화된 중복 기사 체크
                    if is_duplicate_article_advanced(title, content, keywords, all_articles):
                        print(f"    ✗ 중복 기사로 제외")
                        continue
                    
                    new_article = {
                        'title': title,
                        'url': article_info['url'],
                        'content': content[:500],  # 저장용으로는 500자만
                        'keywords': keywords
                    }
                    
                    all_articles.append(new_article)
                    print(f"    ✓ 키워드 추출 완료 (총 {len(all_articles)}개)")
                else:
                    print(f"    ✗ 급발진 관련성 부족으로 제외")
                
                time.sleep(2)
            
            time.sleep(3)
            
        except Exception as e:
            print(f"{page}페이지 처리 중 오류: {e}")
            continue
    
    return all_articles

def main():
    try:
        print("=== SBS 급발진 뉴스 키워드 크롤러 시작 (고도화된 중복 제거) ===")
        
        articles = collect_urgent_acceleration_news(max_pages=51)
        
        print(f"\n=== 수집 완료 ===")
        print(f"총 {len(articles)}개의 급발진 관련 기사 수집 (중복 제거됨)")
        
        if articles:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"급발진_키워드_{timestamp}.json"
            
            save_data = {
                'collected_at': datetime.now().isoformat(),
                'total_articles': len(articles),
                'articles': articles
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n결과가 '{filename}' 파일로 저장되었습니다.")
            
            # 수집된 기사 키워드 요약 (요청한 형식으로)
            print(f"\n=== 수집된 급발진 사건 키워드 요약 ===")
            for i, article in enumerate(articles, 1):
                keywords = article['keywords']
                print(f"\n{i}. {article['title']}")
                print(f"   URL: {article['url']}")
                print(f"   1. 성별 : {keywords['gender'] or 'None'}")
                print(f"   2. 나이 : {keywords['age'] or 'None'}")
                print(f"   3. 차 모델 : {keywords['car_model'] or 'None'}")
                print(f"   4. 브레이크 작동 여부 : {keywords['brake_status'] or 'None'}")
                print(f"   5. 사고 장소 : {keywords['accident_location'] or 'None'}")
                print(f"   6. 사고 결과 : {keywords['accident_result'] or 'None'}")
                print(f"   7. 사고 발생 시점 : {keywords['accident_time'] or 'None'}")
                print(f"   8. 음주 운전 여부 : {keywords['drunk_driving'] or 'None'}")
                print("-" * 80)
        else:
            print("급발진 관련 기사를 찾을 수 없습니다.")
    
    except Exception as e:
        print(f"크롤링 중 오류: {e}")
    
    finally:
        try:
            driver.quit()
            print("\n브라우저 종료 완료")
        except:
            pass

if __name__ == "__main__":
    main()
