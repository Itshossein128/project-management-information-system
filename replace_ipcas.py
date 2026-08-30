import requests

BASE_URL = "http://localhost:7875/api"
HEADERS = {
    "Authorization": "Token hEL327l1wBRNqnIxCW47UDwKQIsLKSy0:YICsgyH71f5TQ8qCIgliAXe0wGBJsqJW",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def replace_text(text):
    if not text:
        return text
    # Replace IPCAS with Velora while preserving case if possible
    # We'll just do basic string replacements for the combinations we care about
    # IPCAS -> Velora
    # ipcas -> velora
    # Ipcas -> Velora
    text = text.replace("IPCAS", "Velora")
    text = text.replace("ipcas", "velora")
    text = text.replace("Ipcas", "Velora")
    return text

def main():
    shelf_id = 10
    shelf_data = requests.get(f"{BASE_URL}/shelves/{shelf_id}", headers=HEADERS).json()
    
    # Process books in this shelf
    for book in shelf_data.get("books", []):
        book_id = book["id"]
        book_detail = requests.get(f"{BASE_URL}/books/{book_id}", headers=HEADERS).json()
        
        # update book if needed
        b_name = book_detail["name"]
        b_desc = book_detail.get("description", "")
        new_b_name = replace_text(b_name)
        new_b_desc = replace_text(b_desc)
        
        if new_b_name != b_name or new_b_desc != b_desc:
            print(f"Updating Book {book_id}")
            requests.put(f"{BASE_URL}/books/{book_id}", headers=HEADERS, json={
                "name": new_b_name,
                "description": new_b_desc,
            })
            
        # process pages directly in book or inside chapters
        for item in book_detail.get("contents", []):
            if item["type"] == "chapter":
                chap_id = item["id"]
                chap_detail = requests.get(f"{BASE_URL}/chapters/{chap_id}", headers=HEADERS).json()
                
                c_name = chap_detail["name"]
                c_desc = chap_detail.get("description", "")
                n_c_name = replace_text(c_name)
                n_c_desc = replace_text(c_desc)
                
                if c_name != n_c_name or c_desc != n_c_desc:
                    print(f"Updating Chapter {chap_id}")
                    requests.put(f"{BASE_URL}/chapters/{chap_id}", headers=HEADERS, json={
                        "name": n_c_name,
                        "description": n_c_desc,
                        "book_id": book_id
                    })
                    
                for p in chap_detail.get("pages", []):
                    process_page(p["id"])
            elif item["type"] == "page":
                process_page(item["id"])

def process_page(page_id):
    page_detail = requests.get(f"{BASE_URL}/pages/{page_id}", headers=HEADERS).json()
    p_name = page_detail["name"]
    p_md = page_detail.get("markdown", "")
    n_p_name = replace_text(p_name)
    n_p_md = replace_text(p_md)
    
    if p_name != n_p_name or p_md != n_p_md:
        print(f"Updating Page {page_id}")
        payload = {
            "name": n_p_name,
            "markdown": n_p_md,
            "book_id": page_detail["book_id"]
        }
        if page_detail.get("chapter_id"):
            payload["chapter_id"] = page_detail["chapter_id"]
            
        res = requests.put(f"{BASE_URL}/pages/{page_id}", headers=HEADERS, json=payload)
        if res.status_code != 200:
            print(f"Failed page {page_id} update:", res.text)
        else:
            print(f"Updated Page {page_id} successfully.")

if __name__ == "__main__":
    main()
