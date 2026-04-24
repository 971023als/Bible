import requests
import os
import time
import re

API_BASE = "https://bolls.life/get-chapter"

# 신학적 노트 데이터베이스 (확장 가능)
NOTES_DB = {
    "요한복음_14장": {
        "insight": "* **보혜사 성령**: 예수님이 영으로 우리 마음속에 오시는 '참된 부활'의 의미.\n* **내면적 임재**: 재림을 외부적 인물이 아닌 내면의 그리스도 충만으로 보는 해석.",
    },
    "요한계시록_22장": {
        "insight": "* **재림의 완성**: 외부적 사이비 교주를 기다리는 것이 아닌, 내면의 주님이 온 세상을 덮는 우주적 평화의 성취.\n* **부활과 재림의 일치**: 우리 안에 계신 주님의 사랑이 온 피조 세계에 가득하기를 바라는 열망.",
    },
    "창세기_3장": {
        "insight": "* **원복음 (Protoevangelium)**: 여자의 후손이 뱀의 머리를 상하게 할 것이라는 최초의 구원 약속.\n* **가죽옷의 희생**: 인간의 수치를 덮기 위한 하나님의 첫 희생 제물 예표.",
    },
    "여호수아_10장": {
        "insight": "* **아도니세덱 (Adoni-Zedek)**: '의의 주'라는 이름을 가졌으나 평화가 아닌 전쟁을 선택한 예루살렘 왕의 역설.\n* **태양과 달의 멈춤 논쟁**: \n  1) **문자설**: 하나님의 초자연적 개입으로 우주 질서가 일시 정지됨.\n  2) **시적 메타포**: 야살의 책에서 인용된 승리의 극적인 시적 표현.\n  3) **천문학적 해석**: 일식 또는 대기 굴절 현상을 통한 하나님의 섭리.\n  4) **우상 숭배의 척결**: 가나안의 태양/달 신이 여호와 아래 굴복했음을 선포하는 신학적 승리.",
    }
}

def apply_advanced_emphasis(text):
    """
    원어(히브리어/헬라어) 강조 로직 고도화
    1. [], () 등 특수 기호가 포함된 단어는 무조건 볼드
    2. 문장의 핵심 수사학적 포인트(후반부) 볼드
    """
    # 특수 기호 처리
    words = text.split()
    processed_words = []
    
    has_marker = False
    for word in words:
        if any(marker in word for marker in "[]()"):
            processed_words.append(f"**{word}**")
            has_marker = True
        else:
            processed_words.append(word)
    
    # 특수 기호가 없는 경우 기존의 수사학적 강조(후반부 볼드) 적용
    if not has_marker and len(words) > 2:
        mid = len(words) // 2
        return " ".join(words[:mid]) + " **" + " ".join(words[mid:]) + "**"
    
    return " ".join(processed_words)

def process_chapter(book_name, book_id, chapter):
    try:
        # 데이터 가져오기
        krv_data = requests.get(f"{API_BASE}/KRV/{book_id}/{chapter}/").json()
        vulg_data = requests.get(f"{API_BASE}/VULG/{book_id}/{chapter}/").json()
        
        # 구약(히브리어 WLC), 신약(헬라어 TR) 구분
        lang_code = "WLC" if book_id <= 39 else "TR"
        orig_data = requests.get(f"{API_BASE}/{lang_code}/{book_id}/{chapter}/").json()
        
        v_map = {v['verse']: v['text'] for v in vulg_data}
        o_map = {o['verse']: o['text'] for o in orig_data}
        
        lines = [f"# {book_name} {chapter}장\n", "📖 **안내**: 이 파일은 대조 분석용으로 제작되었습니다. 읽기 전 [FAQ.md](../../FAQ.md)를 참고하시면 구조를 이해하는 데 도움이 됩니다.\n"]
        
        for v in krv_data:
            num = v['verse']
            lines.append(f"### {num}절")
            # 한국어 현대화 (가라사대 -> 말씀하시되)
            lines.append(v['text'].replace("가라사대", "말씀하시되"))
            
            # 라틴어 브릿지
            if num in v_map:
                lines.append(f"*{v_map[num]}*")
            
            # 원어 강조 적용
            if num in o_map:
                lines.append(apply_advanced_emphasis(o_map[num]))
            lines.append("")
        
        # 다원적 해석 섹션 삽입
        lines.append("\n---\n## 🌈 다원적 해석 및 심층 분석")
        
        note_key = f"{book_name}_{chapter}장"
        if note_key in NOTES_DB:
            lines.append(f"### 💡 핵심 통찰\n{NOTES_DB[note_key]['insight']}")
        else:
            lines.append("### 💡 핵심 통찰\n* **언약의 연속성**: 이 장에서도 하나님은 자신의 백성과 맺은 사랑의 언약을 성실히 이행하십니다.")
            
        lines.append("\n### 🏛️ 교파별 관점 대조")
        lines.append("* **가톨릭**: 교회의 전통과 성사적 은총을 통한 신앙의 신비를 강조함.")
        lines.append("* **개신교**: 오직 성경과 믿음을 통한 개인의 회심과 하나님과의 관계를 중시함.")
        lines.append("* **동방정교회**: 성화(Theosis)와 신비적 연합을 통한 인간의 신격화를 지향함.")
        lines.append("* **철학적 시선 (니체 등)**: 힘에의 의지와 기존 도덕 체계에 대한 비판적 성찰 배치.")
        
        lines.append("\n♾️ **변치 않는 하나님의 언약**: 이 장에서도 '사랑과 평화(Love and Peace)'의 물줄기는 멈추지 않습니다.")
        
        # 경로 설정 및 저장
        sub_dir = "구약" if book_id <= 39 else "신약"
        path = f"c:/Users/User/OneDrive - usk.ac.kr/문서/Github/Bible/{sub_dir}/{book_name}/{book_name}_{chapter}장.md"
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        return True
    except Exception as e:
        print(f"Error in {book_name} {chapter}: {e}")
        return False

def main():
    # 전체 성경 권 정보 (이름, ID, 장 수)
    # 실제 운영 시에는 모든 권을 리스트업해야 함
    books = [
        ("창세기", 1, 50), ("출애굽기", 2, 40), ("레위기", 3, 27), ("민수기", 4, 36), ("신명기", 5, 34),
        ("여호수아", 6, 24), ("사사기", 7, 21), ("룻기", 8, 4),
        ("요한복음", 43, 21), ("요한계시록", 66, 22)
    ]
    
    for name, bid, chapters in books:
        print(f"Updating {name} with Advanced Emphasis...")
        for ch in range(1, chapters + 1):
            process_chapter(name, bid, ch)
            time.sleep(0.2) # API 부하 방지

if __name__ == "__main__":
    main()
