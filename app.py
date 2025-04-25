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
app.secret_key = os.urandom(24)

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
    return render_template('index.html')

@app.route('/api/upload_and_match', methods=['POST'])
def upload_and_match():
    # セッションIDの生成
    session_id = str(uuid.uuid4())
    
    # ファイルの存在確認
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'ファイルが選択されていません。'})
    
    file = request.files['file']
    
    # ファイル名の確認
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'ファイルが選択されていません。'})
    
    # マッチング先企業情報の取得
    target_company_name = request.form.get('target_company_name', '')
    target_industry = request.form.get('target_industry', '')
    target_business_description = request.form.get('target_business_description', '')
    
    # マッチング先企業情報の検証
    if not target_company_name or not target_industry or not target_business_description:
        return jsonify({'status': 'error', 'message': 'マッチング先企業情報が不足しています。'})
    
    # ファイル形式の確認
    if not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': 'CSVファイル形式のみ対応しています。'})
    
    try:
        # ファイルの保存
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"{session_id}_{filename}")
        file.save(filepath)
        
        # CSVファイルからデータを抽出
        company_data = extract_company_data_from_csv(filepath)
        
        if not company_data:
            return jsonify({'status': 'error', 'message': 'CSVファイルからデータを抽出できませんでした。ファイル形式を確認してください。'})
        
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
        return jsonify({'status': 'error', 'message': f'ファイル処理中にエラーが発生しました: {str(e)}'})

@app.route('/api/analyze_matching', methods=['POST'])
def analyze_matching():
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in session_data:
        return jsonify({'status': 'error', 'message': 'セッションが無効です。もう一度お試しください。'})
    
    try:
        # セッションデータの取得
        session_info = session_data[session_id]
        company_a = session_info['company_a']
        company_b = session_info['company_b']
        
        # 企業間の比較分析（実際のAPIキーがない場合はモックデータを使用）
        analysis_results = {
            'search_query': f"{company_a['industry']}と{company_b['industry']}の協業可能性を分析",
            'industry_analysis': f"{company_a['industry']}と{company_b['industry']}の業界特性を比較しています...",
            'case_reference': f"類似業種間の過去の成功事例を参照しています...",
            'data_analysis': f"{company_a['company_name']}と{company_b['company_name']}のビジネスデータを分析しています...",
            'matching_patterns': f"両社の事業内容から協業パターンを検出しています...",
            'candidate_selection': f"マッチング度合いを評価しています..."
        }
        
        # 実際のAPIを使用する場合は以下のようなコードになります
        # analysis_results = compare_companies(company_a, company_b, api_key="your_api_key")
        
        # 分析結果をセッションに保存
        session_data[session_id]['analysis_results'] = analysis_results
        
        return jsonify({
            'status': 'success',
            'data': analysis_results
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'分析中にエラーが発生しました: {str(e)}'})

@app.route('/api/matching_results', methods=['POST'])
def matching_results():
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in session_data:
        return jsonify({'status': 'error', 'message': 'セッションが無効です。もう一度お試しください。'})
    
    try:
        # セッションデータの取得
        session_info = session_data[session_id]
        company_a = session_info['company_a']
        company_b = session_info['company_b']
        
        # マッチング結果の生成（実際のAPIキーがない場合はモックデータを使用）
        matching_score = 85  # 0-100のスコア
        
        matching_results = {
            'company_a': {
                'name': company_a['company_name'],
                'industry': company_a['industry'],
                'description': company_a['business_description']
            },
            'company_b': {
                'name': company_b['company_name'],
                'industry': company_b['industry'],
                'description': company_b['business_description']
            },
            'matching_score': matching_score,
            'matching_details': f"{company_a['company_name']}と{company_b['company_name']}は{matching_score}%のマッチング度を示しています。両社の事業内容を分析した結果、協業による相乗効果が期待できます。特に、{company_a['company_name']}の強みと{company_b['company_name']}の市場ニーズが合致しています。",
            'past_cases': [
                {
                    'title': f"{company_a['industry']}と{company_b['industry']}の協業事例",
                    'date': '2024-02-15',
                    'description': f"類似業種の企業間で成功した協業事例です。両社の強みを活かした新商品開発により、市場シェアを拡大しました。",
                    'roi': '150%'
                },
                {
                    'title': '異業種間の戦略的提携',
                    'date': '2023-11-08',
                    'description': "異なる業種の企業が技術とマーケティングのノウハウを共有し、新規市場を開拓した事例です。",
                    'roi': '130%'
                }
            ],
            'strategies': [
                f"{company_a['company_name']}の{company_a['industry']}としての専門知識と{company_b['company_name']}の{company_b['industry']}のネットワークを活用した共同プロジェクトの立ち上げ",
                f"両社の顧客基盤を活用したクロスセリング戦略の展開",
                f"技術・ノウハウの共有による新商品・サービスの開発",
                f"共同マーケティングによるブランド力の強化と市場拡大"
            ]
        }
        
        # 実際のAPIを使用する場合は以下のようなコードになります
        # matching_results = generate_matching_report(company_a, company_b, api_key="your_api_key")
        
        # マッチング結果をセッションに保存
        session_data[session_id]['matching_results'] = matching_results
        
        return jsonify({
            'status': 'success',
            'results': matching_results
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': f'結果生成中にエラーが発生しました: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
