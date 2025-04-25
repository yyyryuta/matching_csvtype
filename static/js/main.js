// AIビジネスマッチングエージェント JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM要素の取得
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.getElementById('upload-area');
    const stepOneContainer = document.getElementById('step-one-container');
    const stepTwoContainer = document.getElementById('step-two-container');
    const resultsContainer = document.getElementById('results-container');
    const progressFill = document.getElementById('progress-fill');
    const resetButton = document.getElementById('reset-button');
    const errorMessageElement = document.getElementById('error-message');
    
    // 企業情報表示要素
    const companyANameDisplay = document.getElementById('company-a-name-display');
    const companyAIndustryDisplay = document.getElementById('company-a-industry-display');
    const companyBNameDisplay = document.getElementById('company-b-name-display');
    const companyBIndustryDisplay = document.getElementById('company-b-industry-display');
    
    // マッチング先企業情報入力フォーム要素
    const targetCompanyName = document.getElementById('target-company-name');
    const targetIndustry = document.getElementById('target-industry');
    const targetBusinessDescription = document.getElementById('target-business-description');
    
    // ファイル選択ボタンのイベントリスナー
    const fileSelectButton = document.querySelector('.file-select-button');
    if (fileSelectButton) {
        fileSelectButton.addEventListener('click', function() {
            fileInput.click();
        });
    } else {
        console.error('ファイル選択ボタンが見つかりません');
    }
    
    // セッション情報
    let sessionId = null;
    
    // 分析結果コンテナの要素
    const searchQueryElement = document.getElementById('search-query');
    const industryAnalysisElement = document.getElementById('industry-analysis');
    const caseReferenceElement = document.getElementById('case-reference');
    const dataAnalysisElement = document.getElementById('data-analysis');
    const matchingPatternsElement = document.getElementById('matching-patterns');
    const candidateSelectionElement = document.getElementById('candidate-selection');
    
    // ドラッグ&ドロップ機能
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        uploadArea.classList.add('highlight');
    }
    
    function unhighlight() {
        uploadArea.classList.remove('highlight');
    }
    
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        handleFiles(files);
    }
    
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });
    
    function handleFiles(files) {
        if (files.length > 0) {
            // エラーメッセージをクリア
            hideErrorMessage();
            
            // 選択されたファイル名を表示
            const fileName = files[0].name;
            const fileIcon = uploadArea.querySelector('.file-icon');
            const paragraphs = uploadArea.querySelectorAll('p');
            const fileSelectButton = uploadArea.querySelector('.file-select-button');
            
            // 元のコンテンツを非表示にする
            if (fileIcon) fileIcon.style.display = 'none';
            paragraphs.forEach(p => p.style.display = 'none');
            if (fileSelectButton) fileSelectButton.style.display = 'none';
            
            // ファイル名表示要素を作成
            const fileNameDisplay = document.createElement('div');
            fileNameDisplay.className = 'selected-file';
            fileNameDisplay.innerHTML = `
                <i class="fas fa-file-csv"></i>
                <span>${fileName}</span>
                <button type="button" class="change-file-button">変更</button>
            `;
            uploadArea.appendChild(fileNameDisplay);
            
            // 変更ボタンのイベントリスナー
            const changeFileButton = fileNameDisplay.querySelector('.change-file-button');
            if (changeFileButton) {
                changeFileButton.addEventListener('click', function(e) {
                    e.stopPropagation();
                    // 元のコンテンツを再表示
                    if (fileIcon) fileIcon.style.display = 'block';
                    paragraphs.forEach(p => p.style.display = 'block');
                    if (fileSelectButton) fileSelectButton.style.display = 'inline-block';
                    
                    // ファイル名表示を削除
                    fileNameDisplay.remove();
                    
                    // ファイル入力をリセット
                    fileInput.value = '';
                });
            }
        }
    }
    
    // エラーメッセージを表示する関数
    function showErrorMessage(message) {
        errorMessageElement.textContent = message;
        errorMessageElement.style.display = 'block';
        
        // アップロードエリアを赤枠で強調
        uploadArea.style.borderColor = '#e53935';
        
        // 3秒後に赤枠を元に戻す
        setTimeout(() => {
            uploadArea.style.borderColor = '';
        }, 3000);
        
        // アップロードエリアまでスクロール
        uploadArea.scrollIntoView({ behavior: 'smooth' });
    }
    
    // エラーメッセージを非表示にする関数
    function hideErrorMessage() {
        errorMessageElement.style.display = 'none';
        uploadArea.style.borderColor = '';
    }
    
    // マッチング先企業情報の検証
    function validateTargetCompanyInfo() {
        if (!targetCompanyName.value.trim()) {
            showErrorMessage('マッチング先企業名を入力してください。');
            return false;
        }
        
        if (!targetIndustry.value.trim()) {
            showErrorMessage('マッチング先企業の業種を入力してください。');
            return false;
        }
        
        if (!targetBusinessDescription.value.trim()) {
            showErrorMessage('マッチング先企業の事業内容を入力してください。');
            return false;
        }
        
        return true;
    }
    
    // ファイルアップロードとマッチング分析開始
    function uploadFileAndStartMatching(file) {
        // マッチング先企業情報の検証
        if (!validateTargetCompanyInfo()) {
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('target_company_name', targetCompanyName.value.trim());
        formData.append('target_industry', targetIndustry.value.trim());
        formData.append('target_business_description', targetBusinessDescription.value.trim());
        
        // ファイル形式を確認（フロントエンドでも検証）
        const fileExtension = file.name.split('.').pop().toLowerCase();
        if (fileExtension !== 'csv') {
            showErrorMessage('CSVファイル形式のみ対応しています。別のファイルを選択してください。');
            return;
        }
        
        // ファイルサイズを確認
        if (file.size === 0) {
            showErrorMessage('ファイルが空です。有効なCSVファイルを選択してください。');
            return;
        }
        
        fetch('/api/upload_and_match', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // エラーメッセージを非表示
                hideErrorMessage();
                
                // セッションIDを保存
                sessionId = data.session_id;
                
                // 企業情報を表示
                companyANameDisplay.textContent = data.data.company_a_name;
                companyAIndustryDisplay.textContent = data.data.company_a_industry;
                companyBNameDisplay.textContent = data.data.company_b_name;
                companyBIndustryDisplay.textContent = data.data.company_b_industry;
                
                // ステップ1からステップ2へ移行
                stepOneContainer.style.display = 'none';
                stepTwoContainer.style.display = 'block';
                
                // 分析プロセスを開始
                startAnalysis();
            } else if (data.status === 'error') {
                // エラーメッセージを表示
                showErrorMessage(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('ファイルのアップロード中にエラーが発生しました。もう一度お試しください。');
        });
    }
    
    // フォーム送信イベント
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (fileInput.files.length > 0) {
            uploadFileAndStartMatching(fileInput.files[0]);
        } else {
            showErrorMessage('CSVファイルを選択してください。');
        }
    });
    
    // 分析プロセスの開始
    function startAnalysis() {
        // 進捗バーのアニメーション
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 1;
            progressFill.style.width = `${progress}%`;
            
            // 進捗に応じて分析結果を順次表示
            if (progress === 20) {
                document.getElementById('search-query-container').style.display = 'flex';
            } else if (progress === 35) {
                document.getElementById('industry-analysis-container').style.display = 'flex';
            } else if (progress === 50) {
                document.getElementById('case-reference-container').style.display = 'flex';
            } else if (progress === 65) {
                document.getElementById('data-analysis-container').style.display = 'flex';
            } else if (progress === 80) {
                document.getElementById('matching-patterns-container').style.display = 'flex';
            } else if (progress === 90) {
                document.getElementById('candidate-selection-container').style.display = 'flex';
            } else if (progress >= 100) {
                clearInterval(progressInterval);
                // 分析完了後、結果を表示
                setTimeout(showResults, 1000);
            }
        }, 100);
        
        // APIから分析データを取得
        fetch('/api/analyze_matching', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: sessionId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 分析結果を表示
                searchQueryElement.textContent = data.data.search_query;
                industryAnalysisElement.textContent = data.data.industry_analysis;
                caseReferenceElement.textContent = data.data.case_reference;
                dataAnalysisElement.textContent = data.data.data_analysis;
                matchingPatternsElement.textContent = data.data.matching_patterns;
                candidateSelectionElement.textContent = data.data.candidate_selection;
            } else {
                showErrorMessage(data.message);
                // エラーの場合はステップ1に戻る
                stepTwoContainer.style.display = 'none';
                stepOneContainer.style.display = 'block';
                clearInterval(progressInterval);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('分析プロセス中にエラーが発生しました。もう一度お試しください。');
            // エラーの場合はステップ1に戻る
            stepTwoContainer.style.display = 'none';
            stepOneContainer.style.display = 'block';
            clearInterval(progressInterval);
        });
    }
    
    // 結果表示
    function showResults() {
        fetch('/api/matching_results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: sessionId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // ステップ2から結果表示へ移行
                stepTwoContainer.style.display = 'none';
                resultsContainer.style.display = 'block';
                
                // 企業A情報の表示
                document.getElementById('company-a-name').textContent = data.results.company_a.name;
                document.getElementById('company-a-category').textContent = data.results.company_a.industry;
                document.getElementById('company-a-description').textContent = data.results.company_a.description;
                
                // 企業B情報の表示
                document.getElementById('company-b-name').textContent = data.results.company_b.name;
                document.getElementById('company-b-category').textContent = data.results.company_b.industry;
                document.getElementById('company-b-description').textContent = data.results.company_b.description;
                
                // マッチングスコアの表示
                document.getElementById('matching-score-value').textContent = data.results.matching_score;
                document.getElementById('matching-details-text').textContent = data.results.matching_details;
                
                // 過去の成功事例の表示
                const pastCases = data.results.past_cases;
                if (pastCases.length > 0 && pastCases[0]) {
                    const case1 = pastCases[0];
                    document.getElementById('case1-title').textContent = case1.title;
                    document.getElementById('case1-date').textContent = case1.date;
                    document.getElementById('case1-description').textContent = case1.description;
                    document.getElementById('case1-roi').textContent = `ROI: ${case1.roi}`;
                }
                
                if (pastCases.length > 1 && pastCases[1]) {
                    const case2 = pastCases[1];
                    document.getElementById('case2-title').textContent = case2.title;
                    document.getElementById('case2-date').textContent = case2.date;
                    document.getElementById('case2-description').textContent = case2.description;
                    document.getElementById('case2-roi').textContent = `ROI: ${case2.roi}`;
                }
                
                // 戦略提案の表示
                const strategies = data.results.strategies;
                const strategyList = document.getElementById('strategy-list');
                strategyList.innerHTML = '';
                
                strategies.forEach(strategy => {
                    const strategyItem = document.createElement('div');
                    strategyItem.className = 'strategy-item';
                    strategyItem.innerHTML = `
                        <div class="strategy-icon">
                            <i class="fas fa-lightbulb"></i>
                        </div>
                        <div class="strategy-text">${strategy}</div>
                    `;
                    strategyList.appendChild(strategyItem);
                });
            } else {
                showErrorMessage(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('結果の取得中にエラーが発生しました。もう一度お試しください。');
        });
    }
    
    // リセットボタン
    resetButton.addEventListener('click', function() {
        // ページをリロード
        window.location.reload();
    });
    
    // アップロードエリアのクリックイベント
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });
    
    // デバッグ用コンソールログ
    console.log('DOM fully loaded');
    console.log('File select button:', fileSelectButton);
    console.log('File input:', fileInput);
    console.log('Target company form fields:', targetCompanyName, targetIndustry, targetBusinessDescription);
});
