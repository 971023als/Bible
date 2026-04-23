import os
import re
import json
import urllib.request
import time

# Mapping Korean book names to Bolls Bible API IDs and bible-api.com English names
BOOK_DATA = {
    "창세기": {"id": 1, "en": "genesis", "chapters": 50},
    "출애굽기": {"id": 2, "en": "exodus", "chapters": 40},
    "레위기": {"id": 3, "en": "leviticus", "chapters": 27},
    "민수기": {"id": 4, "en": "numbers", "chapters": 36},
    "신명기": {"id": 5, "en": "deuteronomy", "chapters": 34},
    "여호수아": {"id": 6, "en": "joshua", "chapters": 24},
    "사사기": {"id": 7, "en": "judges", "chapters": 21},
    "룻기": {"id": 8, "en": "ruth", "chapters": 4},
    "사무엘상": {"id": 9, "en": "1-samuel", "chapters": 31},
    "사무엘하": {"id": 10, "en": "2-samuel", "chapters": 24},
    "열왕기상": {"id": 11, "en": "1-kings", "chapters": 22},
    "열왕기하": {"id": 12, "en": "2-kings", "chapters": 25},
    "역대상": {"id": 13, "en": "1-chronicles", "chapters": 29},
    "역대하": {"id": 14, "en": "2-chronicles", "chapters": 36},
    "에스라": {"id": 15, "en": "ezra", "chapters": 10},
    "느헤미야": {"id": 16, "en": "nehemiah", "chapters": 13},
    "에스더": {"id": 17, "en": "esther", "chapters": 10},
    "욥기": {"id": 18, "en": "job", "chapters": 42},
    "시편": {"id": 19, "en": "psalms", "chapters": 150},
    "잠언": {"id": 20, "en": "proverbs", "chapters": 31},
    "전도서": {"id": 21, "en": "ecclesiastes", "chapters": 12},
    "아가": {"id": 22, "en": "song-of-solomon", "chapters": 8},
    "이사야": {"id": 23, "en": "isaiah", "chapters": 66},
    "예레미야": {"id": 24, "en": "jeremiah", "chapters": 52},
    "예레미야에가": {"id": 25, "en": "lamentations", "chapters": 5},
    "에스겔": {"id": 26, "en": "ezekiel", "chapters": 48},
    "다니엘": {"id": 27, "en": "daniel", "chapters": 12},
    "호세아": {"id": 28, "en": "hosea", "chapters": 14},
    "요엘": {"id": 29, "en": "joel", "chapters": 3},
    "아모스": {"id": 30, "en": "amos", "chapters": 9},
    "오바댜": {"id": 31, "en": "obadiah", "chapters": 1},
    "요나": {"id": 32, "en": "jonah", "chapters": 4},
    "미가": {"id": 33, "en": "micah", "chapters": 7},
    "나훔": {"id": 34, "en": "nahum", "chapters": 3},
    "하박국": {"id": 35, "en": "habakkuk", "chapters": 3},
    "스바냐": {"id": 36, "en": "zephaniah", "chapters": 3},
    "학개": {"id": 37, "en": "haggai", "chapters": 2},
    "스가랴": {"id": 38, "en": "zechariah", "chapters": 14},
    "말라기": {"id": 39, "en": "malachi", "chapters": 4},
    "마태복음": {"id": 40, "en": "matthew", "chapters": 28},
    "마가복음": {"id": 41, "en": "mark", "chapters": 16},
    "누가복음": {"id": 42, "en": "luke", "chapters": 24},
    "요한복음": {"id": 43, "en": "john", "chapters": 21},
    "사도행전": {"id": 44, "en": "acts", "chapters": 28},
    "로마서": {"id": 45, "en": "romans", "chapters": 16},
    "고린도전서": {"id": 46, "en": "1-corinthians", "chapters": 16},
    "고린도후서": {"id": 47, "en": "2-corinthians", "chapters": 13},
    "갈라디아서": {"id": 48, "en": "galatians", "chapters": 6},
    "에베소서": {"id": 49, "en": "ephesians", "chapters": 6},
    "빌립보서": {"id": 50, "en": "philippians", "chapters": 4},
    "골로새서": {"id": 51, "en": "colossians", "chapters": 4},
    "데살로니가전서": {"id": 52, "en": "1-thessalonians", "chapters": 5},
    "데살로니가후서": {"id": 53, "en": "2-thessalonians", "chapters": 3},
    "디모데전서": {"id": 54, "en": "1-timothy", "chapters": 6},
    "디모데후서": {"id": 55, "en": "2-timothy", "chapters": 4},
    "디도서": {"id": 56, "en": "titus", "chapters": 3},
    "빌레몬서": {"id": 57, "en": "philemon", "chapters": 1},
    "히브리서": {"id": 58, "en": "hebrews", "chapters": 13},
    "야고보서": {"id": 59, "en": "james", "chapters": 5},
    "베드로전서": {"id": 60, "en": "1-peter", "chapters": 5},
    "베드로후서": {"id": 61, "en": "2-peter", "chapters": 3},
    "요한1서": {"id": 62, "en": "1-john", "chapters": 5},
    "요한2서": {"id": 63, "en": "2-john", "chapters": 1},
    "요한3서": {"id": 64, "en": "3-john", "chapters": 1},
    "유다서": {"id": 65, "en": "jude", "chapters": 1},
    "요한계시록": {"id": 66, "en": "revelation", "chapters": 22}
}

BASE_DIR = r"c:\Users\User\OneDrive - usk.ac.kr\문서\Github\Bible"

def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}", flush=True)
        return None

def get_latin_text(book_en, chapter):
    url = f"https://bible-api.com/{book_en}+{chapter}?translation=clementine"
    data = fetch_json(url)
    if data and 'verses' in data:
        return {v['verse']: v['text'] for v in data['verses']}
    return {}

def generate_markdown(book_name, chapter, korean_verses, original_verses, latin_map):
    lines = [f"# {book_name} {chapter}장\n\n"]
    
    orig_map = {v['verse']: v['text'] for v in original_verses}
    
    for v in korean_verses:
        verse_num = v['verse']
        korean_text = v['text']
        lines.append(f"### {verse_num}절\n")
        lines.append(f"{korean_text}\n")
        
        # Add Latin if available
        if verse_num in latin_map:
            lines.append(f"*{latin_map[verse_num].strip()}*\n")
            
        # Add Original if available
        if verse_num in orig_map:
            lines.append(f"{orig_map[verse_num]}\n")
            
        lines.append("\n")
    
    return "".join(lines)

def process_book(dir_path, book_name, is_old_testament):
    data = BOOK_DATA.get(book_name)
    if not data:
        return
    
    book_id = data['id']
    book_en = data['en']
    max_chapters = data['chapters']
    book_dir = os.path.join(dir_path, book_name)
    
    translation_orig = "WLC" if is_old_testament else "SBLGNT"
    translation_ko = "KRV"

    for chapter in range(1, max_chapters + 1):
        filename = f"{book_name}_{chapter}장.md"
        file_path = os.path.join(book_dir, filename)
        
        # We RE-DO everything as requested, so no "already updated" check this time
        # but to be safe we can check if it already has Latin AND Original
        # Actually the user said "다시 다 만들어줘" so we overwrite.

        print(f"  Updating {filename} with Latin bridge...", flush=True)
        korean_verses = fetch_json(f"https://bolls.life/get-chapter/{translation_ko}/{book_id}/{chapter}/")
        time.sleep(0.2)
        original_verses = fetch_json(f"https://bolls.life/get-chapter/{translation_orig}/{book_id}/{chapter}/")
        time.sleep(0.2)
        latin_map = get_latin_text(book_en, chapter)
        
        if korean_verses and original_verses:
            md_content = generate_markdown(book_name, chapter, korean_verses, original_verses, latin_map)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            time.sleep(0.3)

if __name__ == "__main__":
    # Process Old Testament
    ot_dir = os.path.join(BASE_DIR, "구약")
    for book in os.listdir(ot_dir):
        if os.path.isdir(os.path.join(ot_dir, book)):
            print(f"Processing OT: {book}...", flush=True)
            process_book(ot_dir, book, True)
            
    # Process New Testament
    nt_dir = os.path.join(BASE_DIR, "신약")
    for book in os.listdir(nt_dir):
        if os.path.isdir(os.path.join(nt_dir, book)):
            print(f"Processing NT: {book}...", flush=True)
            process_book(nt_dir, book, False)
