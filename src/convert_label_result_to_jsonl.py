import json

def convert_label_result_to_jsonl(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in data:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')

    print(f"✅ 转换完成，生成文件: {output_path}")


