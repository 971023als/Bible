
import os

base_path = "c:/Users/User/OneDrive - usk.ac.kr/문서/Github/Bible/구약"

NOTES_DB = {
    "시편_23": """
---
## 🌈 다원적 해석 및 심층 분석: 시편 23편
### 💡 핵심 통찰: 목자와 양의 신뢰 관계
* **여호와는 나의 목자**: 고대 근동에서 왕은 백성의 '목자'로 묘사되었습니다. 여기서 시인은 하나님을 자신의 진정한 통치자이자 보호자로 고백합니다.
* **푸른 풀밭과 쉴 만한 물가**: 영혼의 안식과 생명력을 상징합니다.

### 🏛️ 교파별 관점 대조
* **가톨릭**: 선한 목자이신 그리스도와 성체성사의 은총을 통한 영적 영양 공급을 강조합니다.
* **개신교**: 개인과 하나님 사이의 인격적 신뢰와 인도하심에 초점을 맞춥니다.
* **유대교**: 이스라엘 공동체를 돌보시는 하나님의 신실한 언약적 사랑으로 해석합니다.
""",
    "시편_119": """
---
## 🌈 다원적 해석 및 심층 분석: 시편 119편
### 💡 핵심 통찰: 율법(Torah)에 대한 알파벳 찬가
* **답관체(Acrostic) 구조**: 히브리어 알파벳 22자를 순서대로 사용하여, 삶의 모든 영역이 하나님의 말씀 아래 있음을 보여줍니다.
* **말씀의 기능**: 내 발의 등(Lamp)이자 내 길의 빛(Light).

### 🏛️ 교파별 관점 대조
* **동방정교회**: 시편 119편을 장례 예배의 핵심으로 사용하며, 죽음 이후에도 이어지는 하나님의 법에 대한 신비적 순종을 강조합니다.
* **개신교**: '오직 성경(Sola Scriptura)'의 원리를 뒷받침하는 가장 강력한 텍스트로 간주합니다.
""",
    "잠언_8": """
---
## 🌈 다원적 해석 및 심층 분석: 잠언 8장
### 💡 핵심 통찰: 선존하시는 지혜(Chokmah)
* **창조의 설계자**: 지혜는 창조의 도구이자 하나님 곁에 있던 창조의 조력자로 묘사됩니다.
* **기독론적 해석**: 신약의 '로고스(Logos)' 기독론과 연결되어, 그리스도의 선존성을 보여주는 구약적 근거로 쓰입니다.

### 🏛️ 철학적 시선
* **로고스(Logos)와 지혜**: 헬라 철학의 이성적 질서인 로고스와 히브리적 인격적 지혜의 융합을 보여줍니다.
""",
    "잠언_31": """
---
## 🌈 다원적 해석 및 심층 분석: 잠언 31장
### 💡 핵심 통찰: 현숙한 여인(Aishet Chayil)
* **지혜의 완성**: 잠언의 결론은 지혜를 이론이 아닌 삶으로 살아내는 '현숙한 여인'의 모습으로 끝납니다.
* **사회경제적 가치**: 그녀는 단순히 가정 내의 존재가 아니라 경제적 주체이자 공동체의 기둥으로 묘사됩니다.
"""
}

def fix_notes():
    # 1. 시편 명칭 통일 (장 -> 편) 및 노트 주입
    psalm_dir = os.path.join(base_path, "시편")
    for filename in os.listdir(psalm_dir):
        if filename.endswith("장.md"):
            old_path = os.path.join(psalm_dir, filename)
            new_path = os.path.join(psalm_dir, filename.replace("장.md", "편.md"))
            
            with open(old_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 파일 제목 변경 (# 시편 X장 -> # 시편 X편)
            content = content.replace("# 시편", "# 시편").replace("장\n", "편\n", 1)
            
            # 노트 주입
            ch_num = filename.split("_")[1].replace("장.md", "")
            key = f"시편_{ch_num}"
            if key in NOTES_DB and NOTES_DB[key] not in content:
                # 푸터 앞에 삽입
                content = content.replace("\n---\n\n♾️", NOTES_DB[key] + "\n---\n\n♾️")
            
            with open(new_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.remove(old_path)
            print(f"Fixed and Renamed: {filename}")

    # 2. 잠언 노트 재주입
    prov_dir = os.path.join(base_path, "잠언")
    for key, note in NOTES_DB.items():
        if "잠언" in key:
            ch_num = key.split("_")[1]
            file_path = os.path.join(prov_dir, f"잠언_{ch_num}장.md")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if note not in content:
                    content = content.replace("\n---\n\n♾️", note + "\n---\n\n♾️")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Fixed Note: {file_path}")

if __name__ == "__main__":
    fix_notes()
