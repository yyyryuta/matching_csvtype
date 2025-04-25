"""
CSVファイルから企業データを抽出するモジュール
"""

import os
import csv
from typing import Dict, Any, Optional

def process_csv_file(filepath: str) -> Dict[str, Any]:
    """CSVファイルから企業データを抽出する"""
    try:
        # ファイルが存在するか確認
        if not os.path.exists(filepath):
            return {
                "status": "error",
                "message": "ファイルが見つかりません。"
            }
        
        # ファイルサイズを確認
        file_size = os.path.getsize(filepath)
        if file_size < 10:  # 極端に小さいファイルはエラーとする
            return {
                "status": "error",
                "message": "ファイルの内容が不十分です。有効な企業データを含むCSVファイルをアップロードしてください。"
            }
        
        # CSVからデータを抽出
        with open(filepath, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            # 最初の行を取得
            try:
                first_row = next(csv_reader)
            except StopIteration:
                return {
                    "status": "error",
                    "message": "CSVファイルにデータが含まれていません。"
                }
            
            # 必要なフィールドが存在するか確認
            required_fields = ["company_name", "industry", "business_description"]
            missing_fields = [field for field in required_fields if field not in first_row]
            
            if missing_fields:
                return {
                    "status": "error",
                    "message": f"CSVファイルに必要なフィールドが含まれていません: {', '.join(missing_fields)}"
                }
            
            # データを抽出
            company_data = {
                "company_name": first_row["company_name"],
                "industry": first_row["industry"],
                "business_description": first_row["business_description"]
            }
            
            return {
                "status": "success",
                "data": company_data
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"CSVファイルの処理中にエラーが発生しました: {str(e)}"
        }

def extract_company_data_from_csv(filepath: str) -> Optional[Dict[str, str]]:
    """CSVファイルから企業データを抽出する関数（アプリケーション用インターフェース）"""
    result = process_csv_file(filepath)
    
    if result["status"] == "success":
        return result["data"]
    else:
        # エラーの場合はログに記録し、None を返す
        print(f"Error extracting data from CSV: {result['message']}")
        return None

# テスト用コード
if __name__ == "__main__":
    # テスト用のCSVファイルパス
    test_filepath = "data/test_companies.csv"
    
    # CSVファイルを処理
    result = process_csv_file(test_filepath)
    
    if result["status"] == "success":
        print("抽出されたデータ:")
        for key, value in result["data"].items():
            print(f"{key}: {value}")
    else:
        print(f"エラー: {result['message']}")