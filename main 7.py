import zipfile
import os
import shutil
import re

def extract_ipa(ipa_path, extract_to="extracted"):
    with zipfile.ZipFile(ipa_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted {ipa_path} to {extract_to}/")

def replace_binary_in_app(app_path, new_binary_path):
    original_binary_path = os.path.join(app_path, "TsumTsum")
    
    if os.path.exists(original_binary_path):
        os.remove(original_binary_path)
        print(f"Removed original binary at {original_binary_path}")
    
    shutil.copy(new_binary_path, original_binary_path)
    print(f"Replaced binary with {new_binary_path}")

def create_ipa(extracted_path, output_ipa_path):
    shutil.make_archive(output_ipa_path.replace('.ipa', ''), 'zip', extracted_path)
    os.rename(output_ipa_path.replace('.ipa', '.zip'), output_ipa_path)
    print(f"Created new IPA at {output_ipa_path}")

def modify_binary_at_offset(binary_path, pattern, offset, index, new_value):
    with open(binary_path, "r+b") as f:
        data = f.read()
        pattern_bytes = bytes.fromhex(pattern)
        pattern_index = [m.start() for m in re.finditer(re.escape(pattern_bytes), data)]
        
        if len(pattern_index) <= index:
            print(f"Error: Pattern not found at index {index}")
            return
        
        target_offset = pattern_index[index] + offset
        print(f"Pattern found at index {index}: offset {hex(pattern_index[index])}, target offset {hex(target_offset)}")
        
        f.seek(target_offset)
        original_data = f.read(len(new_value) // 2)
        print(f"Original data at {hex(target_offset)}: {original_data.hex()}")
        
        new_bytes = bytes.fromhex(new_value)
        f.seek(target_offset)
        f.write(new_bytes)
        print(f"Modified binary at offset {hex(target_offset)} with {new_value}")

def select_changes():
    grouped_changes = {}
    for change in changes:
        group = change.get('group', change['name'])
        if group not in grouped_changes:
            grouped_changes[group] = []
        grouped_changes[group].append(change)
    
    print("offset確認（複数選択する場合はカンマで区切って入力）：")
    for i, group_name in enumerate(grouped_changes.keys(), 1):
        print(f"{i}. {group_name}")
    print(f"{len(grouped_changes) + 1}. おすすめセット")  # セット選択を追加
    print(f"{len(grouped_changes) + 2}. offset表示")  # 追加

    selected_numbers = input("適用したい番号を入力してください: ")
    selected_indexes = [int(x.strip()) - 1 for x in selected_numbers.split(",")]
    
    selected_changes = []
    for i in selected_indexes:
        if i == len(grouped_changes):  # おすすめセットが選ばれた場合
            selected_changes.extend(select_set())
        elif i == len(grouped_changes) + 1:  # ターゲットオフセット表示
            display_target_offsets()
        else:
            group_name = list(grouped_changes.keys())[i]
            selected_changes.extend(grouped_changes[group_name])
    
    return selected_changes
def display_target_offsets():
    print("変更内容の名前とターゲットオフセット：")
    for change in changes:
        pattern = change['pattern']
        offset = change['offset']
        index = change['index']
        
        # 実際のバイナリファイル（TsumTsum）を指定
        binary_path = 'temp_extracted/Payload/TsumTsum.app/TsumTsum'
        
        with open(binary_path, 'rb') as f:  # 実際のバイナリで読み込み
            data = f.read()
            pattern_bytes = bytes.fromhex(pattern)
            pattern_index = [m.start() for m in re.finditer(re.escape(pattern_bytes), data)]
            
            if len(pattern_index) > index:
                target_offset = pattern_index[index] + offset
                print(f"{change['name']} ->  offset: {hex(target_offset)}")

def select_set():
    sets = {
        'A': ['コイン1億固定','コイン1億固定2','LIAPP ALERT 回避','落下速度MAX', '倍速MAX' ,'プレイ倍速３倍','リザスキ','ツム消し2秒増加','単発チェーン','1ツム', 'ツム終了','広告削除','利用規約スキップ','検知アラートスキップ','ガチャスキ'],
        'B': ['コイン2億固定','コイン2億固定2','LIAPP ALERT 回避','落下速度MAX', '倍速MAX','プレイ倍速３倍','リザスキ','ツム消し2秒増加','単発チェーン','1ツム','広告削除','利用規約スキップ','検知アラートスキップ', 'ツム終了','ガチャスキ'],
        'C': ['コイン0固定','コイン回避0','LIAPP ALERT 回避','落下速度MAX', '倍速MAX','プレイ倍速３倍','リザスキ','ツム消し2秒増加','単発チェーン','1ツム', 'ツム終了','ガチャスキ','広告削除','利用規約スキップ','検知アラートスキップ','ランクMAX'],
        'D': ['コイン0固定','コイン回避0','LIAPP ALERT 回避', '倍速MAX','落下速度MAX', 'リザスキ','プレイ倍速３倍', 'ボム非生成1', 'ボム非生成2', '試合リザスキ','全ツムチェーン', 'オートチェーン', 'ツム終了','ガチャスキ','広告削除','検知アラートスキップ','利用規約スキップ','ツムEXP']
    }
    set_names = {
        'A': '1億コイン代行',
        'B': '2億コイン代行',
        'C': 'ランク代行',
        'D': 'ツムレベ代行'
    }
    print("選びたいセットを選択してください：")
    for key, name in set_names.items():
        print(f"{key}: {name}")
    
    set_choice = input("A, B, C, Dのいずれかを選択してください: ").strip().upper()
    selected_set = sets.get(set_choice)
    
    if not selected_set:
        print("無効な選択です。1億コイン代行（Aセット）をデフォルトとして適用します。")
        selected_set = sets['A']
    
    return [change for change in changes if change['name'] in selected_set]

def main(original_ipa, output_ipa):
    extract_to = "temp_extracted"
    app_path = os.path.join(extract_to, "Payload", "TsumTsum.app")
    
    extract_ipa(original_ipa, extract_to)
    selected_changes = select_changes()
    binary_path = os.path.join(app_path, "TsumTsum")
    
    for change in selected_changes:
        pattern = change['pattern']
        offset = change['offset']
        index = change['index']
        new_value = change['value']
        modify_binary_at_offset(binary_path, pattern, offset, index, new_value)

    create_ipa(extract_to, output_ipa)
    shutil.rmtree(extract_to)
    print("Cleaned up temporary files.")


# 変更内容をリストで定義
changes = [

    # コイン0
    {'name': 'コイン0固定', 'pattern': '0840201EA8', 'offset':0x1C, 'index': 0, 'value': '01008052', 'group': 'コイン0'},
    {'name': 'コイン回避0', 'pattern': '0840201EA8', 'offset':0x18, 'index': 0, 'value': '01008052', 'group': 'コイン0'},
  
    # コイン100万
    {'name': 'コイン100万固定', 'pattern': '94420091', 'offset':-0x14, 'index': 1, 'value': '01488872', 'group': 'コイン100万'},
    {'name': 'コイン100万固定2', 'pattern': '94420091', 'offset':-0x18, 'index': 1, 'value': 'E101A052', 'group': 'コイン100万'},
   

    # コイン1000万
    {'name': 'コイン1000万固定', 'pattern': '0840201EA8', 'offset':0x1C, 'index': 0, 'value': '01D09272', 'group': 'コイン1000万'},
    {'name': 'コイン1000万固定2', 'pattern': '0840201EA8', 'offset':0x18, 'index': 0, 'value': '0113A052', 'group': 'コイン1000万'},
    
    # コイン1億
    {'name': 'コイン1億固定', 'pattern': '0840201EA8', 'offset':0x1C, 'index': 0, 'value': '01209C72', 'group': 'コイン1億'},
    {'name': 'コイン1億固定2', 'pattern': '0840201EA8', 'offset':0x18, 'index': 0, 'value': 'A1BEA052', 'group': 'コイン1億'},
   
    # コイン2億
    {'name': 'コイン2億固定', 'pattern': '0840201EA8', 'offset': 0x1C, 'index': 0, 'value': '01409872', 'group': 'コイン2億'},
    {'name': 'コイン2億固定2', 'pattern': '0840201EA8', 'offset': 0x18, 'index': 0, 'value': '617DA152', 'group': 'コイン2億'},
   

     # 1ツム1コイン
    {'name': '単発チェーン', 'pattern': '00008052C0035FD6081045B9', 'offset': 0x8, 'index': 0, 'value': 'C0035FD6','group': '1ツム1コイン'},
    {'name': '1ツム', 'pattern': '01310B91', 'offset': 0x8, 'index': 2, 'value': '68008052', 'group': '1ツム1コイン'},


#その他
     {'name': 'ツムEXP', 'pattern': '685A41B91F09007148', 'offset': -0x8, 'index': 0, 'value': '016A9852'},
    {'name': 'スコアMAX', 'pattern': '136868F8', 'offset': -0x18, 'index': 1, 'value': 'C0035FD6'},
    {'name': 'ツム終了', 'pattern': '4A0001271E0028281E', 'offset': 0x5, 'index': 1, 'value': 'E003271E'},
    {'name': 'レベルロックリザルトスキップ', 'pattern': 'C1050035', 'offset': -0x20, 'index': 0, 'value': 'C0035FD6'},
    {'name': 'LIAPP ALERT 回避', 'pattern': '081840f9e81f00f9', 'offset': -0x40, 'index': 0, 'value': 'C0035FD6'},
    {'name': 'ツム消し2秒増加', 'pattern': '68160639', 'offset': 0x20, 'index': 1, 'value': '1F2003D5'},
    {'name': '全ツムチェーン', 'pattern': '0140201E60', 'offset': 0x2C, 'index': 0, 'value': 'C0035FD6'},
    {'name': 'スキル無限', 'pattern': '014140f900102d1e', 'offset': 0x28, 'index': 0, 'value': '22008052'},
    {'name': '倍速MAX', 'pattern': '080080527F', 'offset': 0x8, 'index': 1, 'value': '00F0271E'},
    {'name': 'プレイ倍速３倍', 'pattern': '08440139', 'offset': 0x8, 'index': 1,'value': '08102E1E'},
    {'name': 'リザスキ', 'pattern': 'E8FEFF36600E40F9', 'offset': 0x20, 'index': 3, 'value': 'C0035FD6'},
    {'name': '試合リザスキ', 'pattern': 'C80A00B4', 'offset': -0x8, 'index': 1, 'value': '340080D2'},
    {'name': 'コンボ999', 'pattern': 'c80600b4', 'offset': -0x14, 'index': 4, 'value': 'E17C8052'},
    {'name': '5秒前スタート', 'pattern': '43B8890A40B90801094A', 'offset': 0x6, 'index': 0, 'value': 'A000271E'},
    {'name': 'フィーバーゲージ増加', 'pattern': 'BD0210301E', 'offset': 0x1, 'index': 0, 'value': '00D0271E'},
    {'name': 'ランクMAX', 'pattern': '0101391ed7', 'offset': -0x10, 'index': 0, 'value': 'E17a020B'},
    {'name': 'ガチャスキ', 'pattern': '14FF4301D1F85F01A9F65702A9F44F03A9FD7B04A9FD030191F40301AA15', 'offset': 0x1, 'index': 0, 'value': 'C0035FD6'},
    {'name': 'オートチェーン', 'pattern': '08284639', 'offset': -0x10, 'index': 1, 'value': '016A9852'},
     {'name': '単発チェーン', 'pattern': '0801152A0801', 'offset': -0x8, 'index': 0, 'value': '016a9852'},
    {'name': 'ツムサイズ', 'pattern': '08090091280108CA', 'offset': -0x18, 'index': 5, 'value': '0849A852'},
    {'name': 'ツム一色', 'pattern': '66010F0008', 'offset': 0x3, 'index': 0, 'value': '0008251e'},
    {'name': 'ツム増量', 'pattern': '290500714B000054', 'offset': 0x0, 'index': 0, 'value': '29250071'},
     {'name': '広告削除', 'pattern': '600C0034', 'offset': -0x48, 'index': 1, 'value': 'C0035FD6'},
     {'name': '利用規約スキップ', 'pattern': '1E00009420', 'offset': -0x78, 'index': 0, 'value': '02008052'},
     {'name': '検知アラートスキップ', 'pattern': '3F11007160', 'offset': -0x18, 'index': 0, 'value': 'C0035FD6'},
    {'name': '時間停止', 'pattern': '0101012A', 'offset': 0x38, 'index': 0, 'value': 'C0035FD6'},
    {'name': '即終了', 'pattern': 'C00300347F', 'offset': -0x4, 'index': 0, 'value': '1F2003D5'},
    {'name': '落下速度MAX', 'pattern': 'C100805242', 'offset': -0x8, 'index': 2, 'value': '00F0271E'},
    {'name': 'ボム生成チェーン46', 'pattern': '01310B91', 'offset': 0x8, 'index': 0, 'value': 'C8058052'},
     {'name': 'ボム非生成', 'pattern': '68160639', 'offset': -0x18, 'index': 1, 'value': '010440b9'},

  
]


if __name__ == "__main__":
    original_ipa = "/Users/owner/Desktop/ipa作成機/original.ipa"
    output_ipa = "/Users/owner/Desktop/ipa作成機/output.ipa"
    main(original_ipa, output_ipa)
