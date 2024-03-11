import json

# Đọc danh sách động từ bất quy tắc từ một tệp văn bản
with open("irregular_verbs.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# Tạo danh sách động từ từ dữ liệu đọc được
irregular_verbs = []
for line in lines:
    # Tách thông tin về động từ
    verb_info = line.strip().split("\t")

    # Kiểm tra nếu dòng không có đúng 4 giá trị, bỏ qua nó
    if len(verb_info) < 4:
        print(f"Ignoring invalid line: {line}")
        continue

    # Unpack thông tin động từ
    number = verb_info[0]
    infinitive = verb_info[1]
    
    meaning = verb_info[-1]
    past_forms = verb_info[2]
    pass_perfect = verb_info[3]

    # Tạo từ điển cho mỗi động từ
    verb_dict = {
        "number":number,
        "infinitive": infinitive,
        "V2": past_forms,
        "V3": pass_perfect,
        "meaning": meaning
    }

    # Thêm từ điển vào danh sách
    irregular_verbs.append(verb_dict)

# Tạo từ điển chứa danh sách động từ
verbs_dict = {"verbs": irregular_verbs}

# Ghi dữ liệu vào tệp JSON
with open("irregular_verbs.json", "w", encoding="utf-8") as json_file:
    json.dump(verbs_dict, json_file, indent=2, ensure_ascii=False)

print("JSON file created successfully.")
