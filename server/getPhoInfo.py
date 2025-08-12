import json
def getData():
    with open('document_structure.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data
if __name__ == '__main__':
    getData()
