# 台股法人成本 / 均線評估工具

## 本機執行

```bash
pip install -r requirements.txt
streamlit run stock_eval_app_topdown_v4.py
```

## 分享方式

### 方式 A：丟給同事本機執行
把這個資料夾整包給同事，同事安裝 Python 後執行上面的指令。

### 方式 B：部署到 Streamlit Community Cloud
1. 建立 GitHub repository
2. 上傳這三個檔案：
   - stock_eval_app_topdown_v4.py
   - requirements.txt
   - README.md
3. 到 Streamlit Community Cloud 登入 GitHub
4. 選擇 repo / branch / main file
5. main file 選 stock_eval_app_topdown_v4.py
6. Deploy 後把 streamlit.app 網址分享給別人
