import os
import json
from pathlib import Path
def scan_document_structure(root_dir):
    """
    扫描符合特定结构的文档目录
    结构: {root_dir}/{first_uid}/{second_uid}/index_files/
    过滤条件: 排除文件名包含'wizicon'或'audio'（不区分大小写）的文件
    输出结构: {first_uid: {second_uid: [file1, file2, ...]}}
    特殊要求: 即使index_files为空也保留second_uid条目
    """
    result = {}
    root_path = Path(root_dir)

    for first_uid_dir in root_path.iterdir():
        if not first_uid_dir.is_dir():
            continue

        first_uid = first_uid_dir.name
        result[first_uid] = {}  # 改为字典结构

        for second_uid_dir in first_uid_dir.iterdir():
            if not second_uid_dir.is_dir():
                continue

            second_uid = second_uid_dir.name
            index_files_path = second_uid_dir / "index_files"

            # 初始化该second_uid的条目
            result[first_uid][second_uid] = []

            if index_files_path.exists() and index_files_path.is_dir():
                # 过滤掉文件名包含'wizicon'或'audio'的文件
                file_names = [
                    f.name for f in index_files_path.iterdir()
                    if (f.is_file() and
                        'wizicon' not in f.name.lower() and
                        'audio' not in f.name.lower())
                ]
                result[first_uid][second_uid] = file_names

    return result


if __name__ == "__main__":
    target_dir = input("请输入根目录路径(eg. /home/wiz/data_root/document2): ").strip()
    if not os.path.isdir(target_dir):
        print("错误: 指定的路径不是有效的目录")
    else:
        try:
            structure = scan_document_structure(target_dir)
            print(json.dumps(structure, indent=2, ensure_ascii=False))
            with open("document_structure.json", "w", encoding="utf-8") as f:
                json.dump(structure, f, indent=2, ensure_ascii=False)
            print("结果已保存到 document_structure.json")
        except Exception as e:
            print(f"处理过程中发生错误: {str(e)}")