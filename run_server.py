"""
サーバー起動スクリプト
HTMLファイルを静的ファイルとして提供するシンプルなFlaskサーバー
"""

from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
import sys

# 現在のディレクトリをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from matching_algorithm import generate_query_expansion, generate_hyde_document, calculate_matching_score, generate_strategy_recommendations, generate_matching_report

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    """メインページを表示"""
    return send_from_directory('.', 'newindex.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """CSVファイルをアップロードして処理する"""
    # ファイルが存在するか確認
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "ファイルが選択されていません。CSVファイルを選択してください。"}), 400
    
    file = request.files['file']
    
    # ファイル名が空でないか確認
    if file.filename == '':
        return jsonify({"status": "error", "message": "ファイルが選択されていません。CSVファイルを選択してください。"}), 400
    
    # ファイル形式が正しいか確認
    if not file.filename.lower().endswith('.csv'):
        return jsonify({"status": "error", "message": "CSVファイル形式のみ対応しています。別のファイルを選択してください。"}), 400
    
    try:
        # 成功レスポンスを返す（実際の処理は省略）
        return jsonify({
            "status": "success", 
            "message": "ファイルが正常にアップロードされました",
            "session_id": "12345"  # 仮のセッションID
        })
    
    except Exception as e:
        # 例外が発生した場合
        return jsonify({"status": "error", "message": f"ファイル処理中にエラーが発生しました: {str(e)}"}), 500

@app.route('/api/upload_and_match', methods=['POST'])
def upload_and_match():
    """CSVファイルをアップロードしてマッチング分析を開始する"""
    # ファイルが存在するか確認
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "ファイルが選択されていません。CSVファイルを選択してください。"}), 400
    
    file = request.files['file']
    
    # ファイル名が空でないか確認
    if file.filename == '':
        return jsonify({"status": "error", "message": "ファイルが選択されていません。CSVファイルを選択してください。"}), 400
    
    # ファイル形式が正しいか確認
    if not file.filename.lower().endswith('.csv'):
        return jsonify({"status": "error", "message": "CSVファイル形式のみ対応しています。別のファイルを選択してください。"}), 400
    
    # マッチング先企業情報の取得
    target_company_name = request.form.get('target_company_name', '')
    target_industry = request.form.get('target_industry', '')
    target_business_description = request.form.get('target_business_description', '')
    
    # マッチング先企業情報の検証
    if not target_company_name or not target_industry or not target_business_description:
        return jsonify({"status": "error", "message": "マッチング先企業情報が不足しています。"}), 400
    
    try:
        # セッションIDの生成
        session_id = str(uuid.uuid4())
        
        # 成功レスポンスを返す（実際の処理は省略）
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "data": {
                "company_a_name": "A社",
                "company_a_industry": "養蜂業",
                "company_b_name": target_company_name,
                "company_b_industry": target_industry
            }
        })
    
    except Exception as e:
        # 例外が発生した場合
        return jsonify({"status": "error", "message": f"ファイル処理中にエラーが発生しました: {str(e)}"}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """分析リクエストを処理する"""
    try:
        # リクエストからセッションIDを取得
        data = request.get_json()
        
        # モックデータの返却
        analysis_data = {
            "company_name": "A社",
            "search_query": "養蜂業, はちみつ, 国産, 卸売",
            "industry_analysis": "養蜂業界の市場規模は年率5.8%で成長中。主な取引先は食品加工業、化粧品業界、健康食品メーカーなど。高付加価値商品の需要増加傾向にあり。",
            "case_reference": "類似企業のマッチング事例を検索しています。3件の事例を発見。成功率の高いパターンを分析中...",
            "data_analysis": "A社の強み：高品質な製品生産、安定した生産体制、弱み：販路の多様性不足、季節変動リスク。",
            "matching_patterns": "候補となる業種: 化粧品メーカー, 健康食品メーカー, 高級食品店",
            "candidate_selection": "各業種から適合度の高い企業をリストアップしています。財務健全性、事業規模、地理的要因、事業シナジーを考慮して最終候補を選定中..."
        }
        
        return jsonify({"status": "success", "data": analysis_data})
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"分析中にエラーが発生しました: {str(e)}"}), 500

@app.route('/api/analyze_matching', methods=['POST'])
def analyze_matching():
    """マッチング分析を実行する"""
    try:
        # リクエストからセッションIDを取得
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"status": "error", "message": "セッションIDが見つかりません。"}), 400
        
        # モックデータの代わりに実際の分析を行う
        company_a = {
            'company_name': 'A社',
            'industry': '養蜂業',
            'business_description': '国産はちみつの生産・卸売'
        }
        
        company_b = {
            'company_name': '札幌コスメティック',
            'industry': '化粧品メーカー',
            'business_description': '天然素材を使用した製品開発に強み。蜂蜜エキスを含む化粧品ラインが人気。'
        }
        
        # クエリ拡張の生成
        company_a_keywords = generate_query_expansion(company_a['industry'], company_a['business_description'])
        
        # 分析データの生成
        analysis_data = {
            "search_query": f"{company_a['industry']}と{company_b['industry']}の協業可能性、{company_a_keywords}",
            "industry_analysis": f"{company_a['industry']}と{company_b['industry']}の業界特性を比較し、相互補完性と市場機会を分析しています。",
            "case_reference": f"類似業種間の過去の成功事例を参照し、成功要因と課題を抽出しています。",
            "data_analysis": f"{company_a['company_name']}と{company_b['company_name']}のビジネスデータを分析し、協業ポテンシャルを評価しています。",
            "matching_patterns": f"両社の事業内容「{company_a['business_description'][:50]}...」と「{company_b['business_description'][:50]}...」から協業パターンを検出しています。",
            "candidate_selection": f"HyDEとRAGを活用して両社のマッチング度合いを評価しています。"
        }
        
        return jsonify({"status": "success", "data": analysis_data})
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"分析中にエラーが発生しました: {str(e)}"}), 500

@app.route('/api/matching_results', methods=['POST'])
def matching_results():
    """マッチング結果を取得する"""
    try:
        # リクエストからセッションIDを取得
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"status": "error", "message": "セッションIDが見つかりません。"}), 400
        
        # テスト用の企業データ
        company_a = {
            'company_name': 'A社',
            'industry': '養蜂業',
            'business_description': '国産はちみつの生産・卸売'
        }
        
        company_b = {
            'company_name': '札幌コスメティック',
            'industry': '化粧品メーカー',
            'business_description': '天然素材を使用した製品開発に強み。蜂蜜エキスを含む化粧品ラインが人気。'
        }
        
        # 実際のマッチングレポートを生成
        results = generate_matching_report(company_a, company_b)
        
        return jsonify({"status": "success", "results": results})
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"結果の取得中にエラーが発生しました: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False) 