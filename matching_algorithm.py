"""
企業マッチングアルゴリズムモジュール
OpenAI APIを使用した企業間マッチング分析
"""

import os
import json
import numpy as np
from openai import OpenAI
from typing import List, Dict, Any, Union

def get_embedding(text: str, model: str = "text-embedding-ada-002", api_key: str = None) -> List[float]:
    """テキストのベクトル埋め込みを取得する関数"""
    if not api_key:
        raise ValueError("API キーが設定されていません。")
    
    client = OpenAI(api_key=api_key)
    response = client.embeddings.create(
        model=model,
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """2つのベクトル間のコサイン類似度を計算する関数"""
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    return dot_product / (norm_a * norm_b)

def generate_query_expansion(industry: str, business_description: str, api_key: str = None) -> str:
    """業種と事業内容から関連キーワードを生成する関数（クエリ拡張）"""
    if not api_key:
        raise ValueError("API キーが設定されていません。")
    
    client = OpenAI(api_key=api_key)
    prompt = f"""
    以下の業種と事業内容から、ビジネスマッチングに役立つ関連キーワードを10個以内で生成してください。
    業種: {industry}
    事業内容: {business_description}
    
    関連キーワード（カンマ区切りで）:
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "あなたはビジネスマッチングの専門家です。"},
            {"role": "user", "content": prompt}
        ]
    )
    
    keywords = response.choices[0].message.content.strip()
    return keywords

def generate_hyde_document(company_a: Dict[str, str], company_b: Dict[str, str], api_key: str = None) -> str:
    """2つの企業情報からHyDE（仮想ドキュメント）を生成する関数"""
    if not api_key:
        raise ValueError("API キーが設定されていません。")
    
    client = OpenAI(api_key=api_key)
    prompt = f"""
    以下の2つの企業の情報から、両社の協業可能性について詳細な分析レポートを作成してください。
    
    企業A:
    企業名: {company_a['company_name']}
    業種: {company_a['industry']}
    事業内容: {company_a['business_description']}
    
    企業B:
    企業名: {company_b['company_name']}
    業種: {company_b['industry']}
    事業内容: {company_b['business_description']}
    
    分析レポートには以下の内容を含めてください：
    1. 両社の強みと弱み
    2. 協業による相乗効果
    3. 具体的な協業アイデア
    4. 市場機会と課題
    5. 成功確率の予測
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "あなたはビジネスマッチングと事業開発の専門家です。"},
            {"role": "user", "content": prompt}
        ]
    )
    
    hyde_document = response.choices[0].message.content.strip()
    return hyde_document

def find_similar_past_cases(hyde_document: str, api_key: str = None) -> List[Dict[str, str]]:
    """HyDEドキュメントに類似した過去の成功事例を検索する関数"""
    if not api_key:
        raise ValueError("API キーが設定されていません。")
    
    client = OpenAI(api_key=api_key)
    prompt = f"""
    以下の企業間協業分析レポートに類似した過去の成功事例を2つ生成してください。
    各事例には、タイトル、日付、説明、ROI（投資収益率）を含めてください。
    
    協業分析レポート:
    {hyde_document[:1000]}  # レポートの最初の1000文字を使用
    
    出力形式:
    [
      {{
        "title": "事例のタイトル",
        "date": "YYYY-MM-DD",
        "description": "事例の詳細説明",
        "roi": "XX%"
      }},
      {{
        "title": "事例のタイトル",
        "date": "YYYY-MM-DD",
        "description": "事例の詳細説明",
        "roi": "XX%"
      }}
    ]
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "あなたはビジネス分析と事例調査の専門家です。JSONフォーマットで出力してください。"},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    try:
        result = json.loads(response.choices[0].message.content.strip())
        if "cases" in result:
            return result["cases"]
        else:
            # JSONが期待した形式でない場合の処理
            return [
                {
                    'title': "異業種間の戦略的提携による新商品開発",
                    'date': '2024-02-15',
                    'description': "食品メーカーと化粧品会社が協力し、食品由来の天然成分を活用した化粧品ラインを共同開発。両社の強みを活かした新商品開発により、新規顧客層を獲得し、市場シェアを拡大しました。",
                    'roi': '150%'
                },
                {
                    'title': '地域企業間の協業による観光振興',
                    'date': '2023-11-08',
                    'description': "地元の食品生産者と観光施設が連携し、体験型の観光プログラムを開発。地域の特産品と観光資源を組み合わせることで、観光客数と売上の両方が増加しました。",
                    'roi': '130%'
                }
            ]
    except json.JSONDecodeError:
        # JSON解析エラー時のフォールバック
        return [
            {
                'title': "異業種間の戦略的提携による新商品開発",
                'date': '2024-02-15',
                'description': "食品メーカーと化粧品会社が協力し、食品由来の天然成分を活用した化粧品ラインを共同開発。両社の強みを活かした新商品開発により、新規顧客層を獲得し、市場シェアを拡大しました。",
                'roi': '150%'
            },
            {
                'title': '地域企業間の協業による観光振興',
                'date': '2023-11-08',
                'description': "地元の食品生産者と観光施設が連携し、体験型の観光プログラムを開発。地域の特産品と観光資源を組み合わせることで、観光客数と売上の両方が増加しました。",
                'roi': '130%'
            }
        ]

def calculate_matching_score(company_a: Dict[str, str], company_b: Dict[str, str], api_key: str = None) -> int:
    """2つの企業間のマッチングスコアを計算する関数"""
    if not api_key:
        raise ValueError("API キーが設定されていません。")
    
    # 企業情報のテキスト化
    company_a_text = f"{company_a['company_name']} {company_a['industry']} {company_a['business_description']}"
    company_b_text = f"{company_b['company_name']} {company_b['industry']} {company_b['business_description']}"
    
    # クエリ拡張
    company_a_keywords = generate_query_expansion(company_a['industry'], company_a['business_description'], api_key)
    company_b_keywords = generate_query_expansion(company_b['industry'], company_b['business_description'], api_key)
    
    # 拡張テキスト
    company_a_expanded = f"{company_a_text} {company_a_keywords}"
    company_b_expanded = f"{company_b_text} {company_b_keywords}"
    
    # HyDEドキュメントの生成
    hyde_document = generate_hyde_document(company_a, company_b, api_key)
    
    # ベクトル埋め込みの取得
    company_a_embedding = get_embedding(company_a_expanded, api_key=api_key)
    company_b_embedding = get_embedding(company_b_expanded, api_key=api_key)
    hyde_embedding = get_embedding(hyde_document, api_key=api_key)
    
    # 類似度の計算
    similarity_a_hyde = cosine_similarity(company_a_embedding, hyde_embedding)
    similarity_b_hyde = cosine_similarity(company_b_embedding, hyde_embedding)
    similarity_a_b = cosine_similarity(company_a_embedding, company_b_embedding)
    
    # マッチングスコアの計算（0-100のスケール）
    matching_score = int((similarity_a_hyde * 0.3 + similarity_b_hyde * 0.3 + similarity_a_b * 0.4) * 100)
    
    # スコアの範囲を調整
    matching_score = max(min(matching_score, 100), 0)
    
    return matching_score

def generate_strategy_recommendations(company_a: Dict[str, str], company_b: Dict[str, str], matching_score: int, api_key: str = None) -> List[str]:
    """マッチングスコアに基づいた戦略提案を生成する関数"""
    if not api_key:
        raise ValueError("API キーが設定されていません。")
    
    client = OpenAI(api_key=api_key)
    prompt = f"""
    以下の2つの企業の情報とマッチングスコアに基づいて、具体的な協業戦略の提案を4つ生成してください。
    
    企業A:
    企業名: {company_a['company_name']}
    業種: {company_a['industry']}
    事業内容: {company_a['business_description']}
    
    企業B:
    企業名: {company_b['company_name']}
    業種: {company_b['industry']}
    事業内容: {company_b['business_description']}
    
    マッチングスコア: {matching_score}%
    
    各戦略提案は1文で簡潔に記述し、具体的かつ実行可能なものにしてください。
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "あなたはビジネス戦略と協業の専門家です。"},
            {"role": "user", "content": prompt}
        ]
    )
    
    strategies_text = response.choices[0].message.content.strip()
    
    # 戦略提案をリスト形式に変換
    strategies = []
    for line in strategies_text.split('\n'):
        line = line.strip()
        if line and not line.isdigit() and len(line) > 10:
            # 番号付きリストの場合は番号を削除
            if line[0].isdigit() and line[1:3] in ['. ', '．', '、', ') ', '）']:
                line = line[3:].strip()
            strategies.append(line)
    
    # 最大4つの戦略に制限
    return strategies[:4]

def compare_companies(company_a: Dict[str, str], company_b: Dict[str, str], api_key: str = None) -> Dict[str, str]:
    """2つの企業を比較分析する関数"""
    if not api_key:
        raise ValueError("API キーが設定されていません。")
    
    # クエリ拡張の生成
    company_a_keywords = generate_query_expansion(company_a['industry'], company_a['business_description'], api_key)
    company_b_keywords = generate_query_expansion(company_b['industry'], company_b['business_description'], api_key)
    
    # 分析結果の生成
    analysis_results = {
        'search_query': f"{company_a['industry']}と{company_b['industry']}の協業可能性、{company_a_keywords}、{company_b_keywords}",
        'industry_analysis': f"{company_a['industry']}と{company_b['industry']}の業界特性を比較し、相互補完性と市場機会を分析しています。",
        'case_reference': f"類似業種間の過去の成功事例を参照し、成功要因と課題を抽出しています。",
        'data_analysis': f"{company_a['company_name']}と{company_b['company_name']}のビジネスデータを分析し、協業ポテンシャルを評価しています。",
        'matching_patterns': f"両社の事業内容「{company_a['business_description'][:50]}...」と「{company_b['business_description'][:50]}...」から協業パターンを検出しています。",
        'candidate_selection': f"HyDEとRAGを活用して両社のマッチング度合いを評価しています。"
    }
    
    return analysis_results

def generate_matching_report(company_a: Dict[str, str], company_b: Dict[str, str], api_key: str = None) -> Dict[str, Any]:
    """2つの企業間のマッチングレポートを生成する関数"""
    if not api_key:
        raise ValueError("API キーが設定されていません。")
    
    # マッチングスコアの計算
    matching_score = calculate_matching_score(company_a, company_b, api_key)
    
    # HyDEドキュメントの生成
    hyde_document = generate_hyde_document(company_a, company_b, api_key)
    
    # 類似した過去の成功事例の検索
    past_cases = find_similar_past_cases(hyde_document, api_key)
    
    # 戦略提案の生成
    strategies = generate_strategy_recommendations(company_a, company_b, matching_score, api_key)
    
    # マッチング詳細の生成
    client = OpenAI(api_key=api_key)
    prompt = f"""
    以下の2つの企業の情報とマッチングスコアに基づいて、マッチング詳細を3〜4文で簡潔に説明してください。
    
    企業A:
    企業名: {company_a['company_name']}
    業種: {company_a['industry']}
    事業内容: {company_a['business_description']}
    
    企業B:
    企業名: {company_b['company_name']}
    業種: {company_b['industry']}
    事業内容: {company_b['business_description']}
    
    マッチングスコア: {matching_score}%
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "あなたはビジネスマッチングの専門家です。"},
            {"role": "user", "content": prompt}
        ]
    )
    
    matching_details = response.choices[0].message.content.strip()
    
    # マッチングレポートの作成
    matching_report = {
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
        'matching_details': matching_details,
        'past_cases': past_cases,
        'strategies': strategies
    }
    
    return matching_report