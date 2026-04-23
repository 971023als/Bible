import os
import re
import json
import urllib.request
import time

# Mapping Korean book names to Bolls Bible API IDs and expected chapter counts
# Using the data from https://bolls.life/get-books/YLT/
BOOK_DATA = {
    "창세기": {"id": 1, "chapters": 50}, "출애굽기": {"id": 2, "chapters": 40}, 
    "레위기": {"id": 3, "chapters": 27}, "민수기": {"id": 4, "chapters": 36}, 
    "신명기": {"id": 5, "chapters": 34}, "여호수아": {"id": 6, "chapters": 24}, 
    "사사기": {"id": 7, "chapters": 21}, "룻기": {"id": 8, "chapters": 4},
    "사무엘상": {"id": 9, "chapters": 31}, "사무엘하": {"id": 10, "chapters": 24}, 
    "열왕기상": {"id": 11, "chapters": 22}, "열왕기하": {"id": 12, "chapters": 25}, 
    "역대상": {"id": 13, "chapters": 29}, "역대하": {"id": 14, "chapters": 36}, 
    "에스라": {"id": 15, "chapters": 10}, "느헤미야": {"id": 16, "chapters": 13}, 
    "에스더": {"id": 17, "chapters": 10}, "욥기": {"id": 18, "chapters": 42}, 
    "시편": {"id": 19, "chapters": 150}, "잠언": {"id": 20, "chapters": 31}, 
    "전도서": {"id": 21, "chapters": 12}, "아가": {"id": 22, "chapters": 8}, 
    "이사야": {"id": 23, "chapters": 66}, "예레미야": {"id": 24, "chapters": 52}, 
    "예레미야에가": {"id": 25, "chapters": 5}, "에스겔": {"id": 26, "chapters": 48}, 
    "다니엘": {"id": 27, "chapters": 12}, "호세아": {"id": 28, "chapters": 14}, 
    "요엘": {"id": 29, "chapters": 3}, "아모스": {"id": 30, "chapters": 9},
    "오바댜": {"id": 31, "chapters": 1}, "요나": {"id": 32, "chapters": 4}, 
    "미가": {"id": 33, "chapters": 7}, "나훔": {"id": 34, "chapters": 3}, 
    "하박국": {"id": 35, "chapters": 3}, "스바냐": {"id": 36, "chapters": 3}, 
    "학개": {"id": 37, "chapters": 2}, "스가랴": {"id": 38, "chapters": 14}, 
    "말라기": {"id": 39, "chapters": 4},
    "마태복음": {"id": 40, "chapters": 28}, "마가복음": {"id": 41, "chapters": 16}, 
    "누가복음": {"id": 42, "chapters": 24}, "요한복음": {"id": 43, "chapters": 21}, 
    "사도행전": {"id": 44, "chapters": 28}, "로마서": {"id": 45, "chapters": 16}, 
    "고린도전서": {"id": 46, "chapters": 16}, "고린도후서": {"id": 47, "chapters": 13}, 
    "갈라디아서": {"id": 48, "chapters": 6}, "에베소서": {"id": 49, "chapters": 6}, 
    "빌립보서": {"id": 50, "chapters": 4}, "골로새서": {"id": 51, "chapters": 4}, 
    "데살로니가전서": {"id": 52, "chapters": 5}, "데살로니가후서": {"id": 53, "chapters": 3}, 
    "디모데전서": {"id": 54, "chapters": 6}, "디모데후서": {"id": 55, "chapters": 4}, 
    "디도서": {"id": 56, "chapters": 3}, "빌레몬서": {"id": 57, "chapters": 1}, 
    "히브리서": {"id": 58, "chapters": 13}, "야고보서": {"id": 59, "chapters": 5}, 
    "베드로전서": {"id": 60, "chapters": 5}, "베드로후서": {"id": 61, "chapters": 3}, 
    "요한1서": {"id": 62, "chapters": 5}, "요한2서": {"id": 63, "chapters": 1}, 
    "요한3서": {"id": 64, "chapters": 1}, "유다서": {"id": 65, "chapters": 1}, 
    "요한계시록": {"id": 66, "chapters": 22}
}

BASE_DIR = r"c:\Users\User\OneDrive - usk.ac.kr\문서\Github\Bible"

def get_bible_text(translation, book_id, chapter):
    url = f"https://bolls.life/get-chapter/{translation}/{book_id}/{chapter}/"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {translation} {book_id}:{chapter} - {e}", flush=True)
        return None

def generate_markdown(book_name, chapter, korean_verses, original_verses):
    lines = [f"# {book_name} {chapter}장\n\n"]
    
    verse_map = {v['verse']: v['text'] for v in original_verses}
    
    for v in korean_verses:
        verse_num = v['verse']
        korean_text = v['text']
        lines.append(f"### {verse_num}절\n")
        lines.append(f"{korean_text}\n")
        if verse_num in verse_map:
            lines.append(f"{verse_map[verse_num]}\n")
        lines.append("\n")
    
    return "".join(lines)

def process_book(dir_path, book_name, is_old_testament):
    data = BOOK_DATA.get(book_name)
    if not data:
        print(f"Skipping unknown book: {book_name}", flush=True)
        return
    
    book_id = data['id']
    max_chapters = data['chapters']
    book_dir = os.path.join(dir_path, book_name)
    
    translation_orig = "WLC" if is_old_testament else "SBLGNT"
    translation_ko = "KRV"
    
    # First, clean up wrong files in the directory
    for filename in os.listdir(book_dir):
        if filename.endswith(".md") and not filename.startswith(book_name) and "_묵상" not in filename:
            print(f"  Removing wrong file: {filename} in {book_name}", flush=True)
            os.remove(os.path.join(book_dir, filename))

    for chapter in range(1, max_chapters + 1):
        filename = f"{book_name}_{chapter}장.md"
        file_path = os.path.join(book_dir, filename)
        
        # Check if already updated (simplified check: if file exists and has original characters)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if re.search(r'[\u0590-\u05FF\u0370-\u03FF]', content):
                    print(f"  Skipping {filename} (already updated).", flush=True)
                    continue

        print(f"  Updating {filename}...", flush=True)
        korean_verses = get_bible_text(translation_ko, book_id, chapter)
        time.sleep(0.2)
        original_verses = get_bible_text(translation_orig, book_id, chapter)
        
        if korean_verses and original_verses:
            md_content = generate_markdown(book_name, chapter, korean_verses, original_verses)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            time.sleep(0.3)

if __name__ == "__main__":
    # Process Old Testament
    process_dir_path = os.path.join(BASE_DIR, "구약")
    for book in os.listdir(process_dir_path):
        if os.path.isdir(os.path.join(process_dir_path, book)):
            print(f"Processing {book}...", flush=True)
            process_book(process_dir_path, book, True)
            
    # Process New Testament
    process_dir_path = os.path.join(BASE_DIR, "신약")
    for book in os.listdir(process_dir_path):
        if os.path.isdir(os.path.join(process_dir_path, book)):
            print(f"Processing {book}...", flush=True)
            process_book(process_dir_path, book, False)
