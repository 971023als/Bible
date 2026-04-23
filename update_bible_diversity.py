import os
import requests
import json
import re
import time

# --- 설정 및 데이터베이스 ---
API_BASE = "https://bolls.life/get-chapter"
MODERN_REPLACEMENTS = {
    "가라사대": "말씀하시되",
    "가라사되": "말씀하시되",
}

# 1. 특수 장별 상세 분석 노트 (사용자 요청 기반)
SPECIFIC_NOTES = {
    "창세기_3장": "* **아룸(עָר֔וּם)**: 뱀의 지혜가 타락하여 간교함이 된 양면성 분석.\n* **니체**: 인간의 자율적 가치 창조를 향한 첫 시도로 보는 전복적 해석.",
    "창세기_4장": "* **77배의 복수 vs 용서**: 라멕의 복수를 예수님의 77번 용서(마태 18:22)와 대조.",
    "출애굽기_4장": "* **십보라의 피 남편**: 언약의 엄중함과 모세의 중보자적 자격에 대한 교파별 논쟁.",
    "레위기_16장": "* **아자젤**: 세상 죄를 지고 가는 그리스도(개신교) vs 죄를 근원으로 돌려보내는 정결(정교회).",
    "신명기_14장": "* **십일조의 본질**: 세금이 아닌 '가족 축제와 외식비'로서의 사랑의 정신 강조.",
    "사무엘하_13장": "* **암논의 병**: 정욕이 인간을 파괴하는 심리적 기제 분석.\n* **비판적 시각**: 다윗의 방관과 가부장적 권력 구조에 대한 사회적 비판.",
    "요한복음_2장": "* **성전과 몸**: 장소의 종교에서 인격의 종교로의 대전환. 서기 70년 예언적 배경.",
    "요한복음_14장": "* **보혜사 성령**: 예수님이 영으로 우리 마음속에 오시는 '참된 부활'의 의미.\n* **내면적 임재**: 재림을 외부적 인물이 아닌 내면의 그리스도 충만으로 보는 해석.",
    "마태복음_9장": "* **세리 마태**: 직업적 꼼꼼함이 복음서의 정교한 구조(5대 설교)로 승화됨.",
    "마태복음_16장": "* **반석**: 베드로(가톨릭) vs 신앙고백(개신교) vs 올바른 전통(정교회).",
    "마태복음_25장": "* **지극히 작은 자**: 배고픈 이웃을 대하는 것이 곧 주님을 대하는 것이라는 실천적 사랑.",
    "요한계시록_22장": "* **재림의 완성**: 외부적 사이비 교주를 기다리는 것이 아닌, 내면의 주님이 온 세상을 덮는 우주적 평화의 성취."
}

# 2. 권(Book)별 공통 교파 관점 템플릿
BOOK_TEMPLATES = {
    "모세오경": {
        "가톨릭": "율법은 구약의 성사적 기초이며, 그리스도를 향한 점진적 계시로 이해함.",
        "개신교": "율법은 죄를 깨닫게 하며, 오직 은혜로 말미암는 구원의 필요성을 역설함.",
        "정교회": "율법은 하나님의 거룩함에 참여하는 '성화(Theosis)'의 초기 단계로 해석함.",
        "철학(니체)": "율법을 강자가 약자를 다스리거나, 혹은 약자가 도덕을 통해 강자를 억압하는 수단으로 비판함."
    },
    "역사서": {
        "가톨릭": "왕권과 성전의 계승을 통해 하나님의 가시적 통치 체제를 중시함.",
        "개신교": "인간 왕들의 실패를 통해 참된 왕이신 그리스도의 필요성을 강조함.",
        "정교회": "역사를 하나님의 섭리가 흐르는 거대한 성화의 과정으로 이해함."
    },
    "복음서": {
        "가톨릭": "그리스도의 인격과 성사적 현존, 교회의 가시적 일치를 중시함.",
        "개신교": "그리스도의 대속 사역과 개인의 신앙적 고백을 핵심으로 봄.",
        "정교회": "로고스의 성육신을 통한 우주적 회복과 신성한 빛의 현현을 강조함.",
        "철학(니체)": "예수를 '마지막 기독교인'으로 평가하거나, 기독교 도덕의 기원을 비판적으로 탐구함."
    }
}

def get_template(book_id):
    if book_id <= 5: return BOOK_TEMPLATES["모세오경"]
    if book_id <= 17: return BOOK_TEMPLATES["역사서"]
    if book_id >= 40: return BOOK_TEMPLATES["복음서"]
    return None

def apply_original_emphasis(text):
    words = text.split()
    if len(words) <= 2: return f"**{text}**"
    split_point = len(words) // 2
    return " ".join(words[:split_point]) + " **" + " ".join(words[split_point:]) + "**"

def modernize_korean(text):
    for old, new in MODERN_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text

def process_chapter(book_name, book_id, chapter):
    krv_data = requests.get(f"{API_BASE}/KRV/{book_id}/{chapter}/").json()
    vulg_data = requests.get(f"{API_BASE}/VULG/{book_id}/{chapter}/").json()
    orig_trans = "WLC" if book_id <= 39 else "TR"
    orig_data = requests.get(f"{API_BASE}/{orig_trans}/{book_id}/{chapter}/").json()

    vulg_map = {v['verse']: v['text'] for v in vulg_data}
    orig_map = {o['verse']: o['text'] for o in orig_data}

    lines = [f"# {book_name} {chapter}장", "\n", "📖 **안내**: 이 파일은 대조 분석용으로 제작되었습니다. 읽기 전 [FAQ.md](../../FAQ.md)를 참고하시면 구조를 이해하는 데 도움이 됩니다.\n"]
    
    for v in krv_data:
        v_num = v['verse']
        lines.append(f"### {v_num}절")
        lines.append(modernize_korean(v['text']))
        if v_num in vulg_map: lines.append(f"*{vulg_map[v_num]}*")
        if v_num in orig_map: lines.append(apply_original_emphasis(orig_map[v_num]))
        lines.append("")

    # --- 다원적 해석 섹션 ---
    lines.append("\n---\n")
    lines.append("## 🌈 다원적 해석 및 심층 분석")
    
    key = f"{book_name}_{chapter}장"
    if key in SPECIFIC_NOTES:
        lines.append(f"### 💡 핵심 통찰\n{SPECIFIC_NOTES[key]}\n")
    
    tpl = get_template(book_id)
    if tpl:
        lines.append("### 🏛️ 교파별 관점 대조")
        lines.append(f"* **가톨릭**: {tpl['가톨릭']}")
        lines.append(f"* **개신교**: {tpl['개신교']}")
        lines.append(f"* **동방정교회**: {tpl['동방정교회']}")
        lines.append(f"* **철학적 시선 (니체 등)**: {tpl['철학(니체)']}")
    
    lines.append("\n♾️ **변치 않는 하나님의 언약**: 이 장에서도 '사랑과 평화(Love and Peace)'의 물줄기는 멈추지 않습니다.")
    return "\n".join(lines)

# 실행 로직 (예시로 몇 장만 우선 확실히 보여드림)
# 실제로는 루프를 돌아야 함
def main():
    root = "c:\\Users\\User\\OneDrive - usk.ac.kr\\문서\\Github\\Bible"
    # 시연을 위해 요한복음 14장과 요한계시록 22장 등 핵심 장을 먼저 갱신
    target_books = [("요한복음", 43, 21), ("요한계시록", 66, 22), ("창세기", 1, 50), ("신명기", 5, 34)]
    for name, bid, chapters in target_books:
        subdir = "구약" if bid <= 39 else "신약"
        for ch in range(1, chapters + 1):
            content = process_chapter(name, bid, ch)
            path = os.path.join(root, subdir, name, f"{name}_{ch}장.md")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated: {name} {ch}")
            time.sleep(0.5)

if __name__ == "__main__":
    main()
