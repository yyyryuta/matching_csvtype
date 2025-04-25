"""
AIビジネスマッチングエージェントのメインアプリケーション
CSVデータ抽出、HyDE、RAG、クエリ拡張、フィルタリングを統合したマッチングシステム
"""

import os
import json
import csv
import uuid
import tempfile
from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename
from csv_extractor import extract_company_data_from_csv
from matching_algorithm import compare_companies, generate_matching_report

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

# OpenAI APIキーの環境変数設定
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("警告: OPENAI_API_KEYが設定されていません。環境変数を設定してください。")

# セッションデータを保存するディクショナリ
session_data = {}

# アップロードされたファイルの保存先ディレクトリ
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 許可するファイル拡張子
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """メインページを表示"""
    return render_template('index.html')

@app.route('/api/upload_and_match', methods=['POST'])
def upload_and_match():
    """CSVファイルをアップロードしてマッチング分析を開始する"""
    # セッションIDの生成
    session_id = str(uuid.uuid4())
    
    # ファイルの存在確認
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'ファイルが選択されていません。'}), 400
    
    file = request.files['file']
    
    # ファイル名の確認
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'ファイルが選択されていません。'}), 400
    
    # マッチング先企業情報の取得
    target_company_name = request.form.get('target_company_name', '')
    target_industry = request.form.get('target_industry', '')
    target_business_description = request.form.get('target_business_description', '')
    
    # マッチング先企業情報の検証
    if not target_company_name or not target_industry or not target_business_description:
        return jsonify({'status': 'error', 'message': 'マッチング先企業情報が不足しています。'}), 400
    
    # ファイル形式の確認
    if not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': 'CSVファイル形式のみ対応しています。'}), 400
    
    try:
        # ファイルの保存
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"{session_id}_{filename}")
        file.save(filepath)
        
        # CSVファイルからデータを抽出
        company_data = extract_company_data_from_csv(filepath)
        
        if not company_data:
            return jsonify({'status': 'error', 'message': 'CSVファイルからデータを抽出できませんでした。ファイル形式を確認してください。'}), 400
        
        # マッチング先企業データの作成
        target_company_data = {
            'company_name': target_company_name,
            'industry': target_industry,
            'business_description': target_business_description
        }
        
        # セッションデータの保存
        session_data[session_id] = {
            'company_a': company_data,
            'company_b': target_company_data,
            'analysis_results': None,
            'matching_results': None
        }
        
        # 企業情報を返す
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'data': {
                'company_a_name': company_data['company_name'],
                'company_a_industry': company_data['industry'],
                'company_b_name': target_company_data['company_name'],
                'company_b_industry': target_company_data['industry']
            }
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'ファイル処理中にエラーが発生しました: {str(e)}'}), 500

@app.route('/api/analyze_matching', methods=['POST'])
def analyze_matching():
    """マッチング分析を実行する"""
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in session_data:
        return jsonify({'status': 'error', 'message': 'セッションが無効です。もう一度お試しください。'}), 400
    
    try:
        # セッションデータの取得
        session_info = session_data[session_id]
        company_a = session_info['company_a']
        company_b = session_info['company_b']
        
        # 企業間の比較分析（実際のマッチングアルゴリズムを使用）
        analysis_results = compare_companies(company_a, company_b, api_key=OPENAI_API_KEY)
        
        # 分析結果をセッションに保存
        session_data[session_id]['analysis_results'] = analysis_results
        
        return jsonify({
            'status': 'success',
            'data': analysis_results
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'分析中にエラーが発生しました: {str(e)}'}), 500

@app.route('/api/matching_results', methods=['POST'])
def matching_results():
    """マッチング結果を取得する"""
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in session_data:
        return jsonify({'status': 'error', 'message': 'セッションが無効です。もう一度お試しください。'}), 400
    
    try:
        # セッションデータの取得
        session_info = session_data[session_id]
        company_a = session_info['company_a']
        company_b = session_info['company_b']
        
        # マッチング結果の生成（実際のマッチングアルゴリズムを使用）
        matching_results = generate_matching_report(company_a, company_b, api_key=OPENAI_API_KEY)
        
        # マッチング結果をセッションに保存
        session_data[session_id]['matching_results'] = matching_results
        
        return jsonify({
            'status': 'success',
            'results': matching_results
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'結果生成中にエラーが発生しました: {str(e)}'}), 500

# セッションクリーンアップ機能（オプション）
@app.route('/api/cleanup_session', methods=['POST'])
def cleanup_session():
    """不要なセッションデータを削除する"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id and session_id in session_data:
        # セッションデータの削除
        del session_data[session_id]
        
        # 関連ファイルの削除
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.startswith(f"{session_id}_"):
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, filename))
                except Exception as e:
                    print(f"Error removing file: {str(e)}")
                    
        return jsonify({'status': 'success', 'message': 'セッションデータがクリーンアップされました。'})
    
    return jsonify({'status': 'success', 'message': 'セッションデータが見つかりませんでした。'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')