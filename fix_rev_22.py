import requests
import os

API_BASE = "https://bolls.life/get-chapter"

def apply_emphasis(text):
    words = text.split()
    if len(words) <= 2: return f"**{text}**"
    mid = len(words) // 2
    return " ".join(words[:mid]) + " **" + " ".join(words[mid:]) + "**"

def update_rev_22():
    book_name = "요한계시록"
    bid = 66
    ch = 22
    
    krv = requests.get(f"{API_BASE}/KRV/{bid}/{ch}/").json()
    vulg = requests.get(f"{API_BASE}/VULG/{bid}/{ch}/").json()
    tr = requests.get(f"{API_BASE}/TR/{bid}/{ch}/").json()
    
    v_map = {v['verse']: v['text'] for v in vulg}
    t_map = {t['verse']: t['text'] for t in tr}
    
    lines = [f"# {book_name} {ch}장\n", "📖 **안내**: 이 파일은 대조 분석용으로 제작되었습니다. 읽기 전 [FAQ.md](../../FAQ.md)를 참고하시면 구조를 이해하는 데 도움이 됩니다.\n"]
    
    for v in krv:
        num = v['verse']
        lines.append(f"### {num}절")
        lines.append(v['text'].replace("가라사대", "말씀하시되"))
        if num in v_map: lines.append(f"*{v_map[num]}*")
        if num in t_map: lines.append(apply_emphasis(t_map[num]))
        lines.append("")
    
    lines.append("\n---\n## 🌈 다원적 해석 및 심층 분석")
    lines.append("### 💡 핵심 통찰")
    lines.append("* **재림의 완성**: 외부적 사이비 교주를 기다리는 것이 아닌, 내면의 주님이 온 세상을 덮는 우주적 평화의 성취.")
    lines.append("* **부활과 재림의 일치**: 이미 우리 안에 계신 주님의 사랑이 온 피조 세계에 가득하기를 바라는 열망이 곧 재림의 본질입니다.")
    
    lines.append("\n### 🏛️ 교파별 관점 대조")
    lines.append("* **가톨릭**: 그리스도의 영광스러운 재림과 최후 심판, 새 하늘과 새 땅의 완성을 믿음.")
    lines.append("* **개신교**: 개인의 종말과 우주적 종말을 동시에 강조하며, 깨어 있는 신앙을 독려함.")
    lines.append("* **동방정교회**: 성화(Theosis)의 완성이자 만물이 하나님 안에서 하나 되는 종말론적 희망.")
    lines.append("* **철학적 시선 (니체 등)**: 미래의 보상에 매몰되기보다 '현재의 삶'을 긍정하는 실존적 태도와의 대조.")
    
    lines.append("\n♾️ **변치 않는 하나님의 언약**: 이 장에서도 '사랑과 평화(Love and Peace)'의 물줄기는 멈추지 않습니다.")
    
    path = "c:\\Users\\User\\OneDrive - usk.ac.kr\\문서\\Github\\Bible\\신약\\요한계시록\\요한계시록_22장.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Revelation 22 Fixed!")

if __name__ == "__main__":
    update_rev_22()
