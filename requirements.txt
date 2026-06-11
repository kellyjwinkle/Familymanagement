# Family Priorities Starter App

A simple Streamlit starter app for two adults to track purchases, tasks, and goals from their phones.

## Features
- Shared list of priorities
- Add item form
- Quick update panel
- Filters for owner, type, status, and priority
- Starter CSV data for testing

## Run locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository.
2. Upload these files.
3. Sign in to Streamlit Community Cloud with GitHub.
4. Choose your repo, branch, and `streamlit_app.py`.
5. Click Deploy.

## Suggested next upgrades
- Replace CSV with SQLite or Supabase
- Add login/authentication
- Add edit and delete item actions
- Add comments and activity history
- Add separate views for You, Wes, and Weekly planning
