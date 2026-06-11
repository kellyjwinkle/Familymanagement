import pandas as pd
from pathlib import Path
from datetime import date, datetime
import streamlit as st

st.set_page_config(page_title="Family Priorities", page_icon="✅", layout="wide")

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "priorities.csv"
COLUMNS = ["id","title","type","priority","owner","status","due_date","kid_tag","notes","updated_at"]
DEFAULT_ROWS = [
    {"id":1,"title":"Buy school shoes for twins","type":"Buy","priority":"High","owner":"Both","status":"In progress","due_date":"2026-08-01","kid_tag":"Twins","notes":"Check current sizes before ordering.","updated_at":"2026-06-11 16:00"},
    {"id":2,"title":"Schedule annual checkups","type":"Do","priority":"High","owner":"You","status":"Not started","due_date":"2026-07-15","kid_tag":"All kids","notes":"Call pediatric office and ask for back-to-school forms.","updated_at":"2026-06-11 16:05"},
    {"id":3,"title":"Build weekly family budget review habit","type":"Goal","priority":"Medium","owner":"Both","status":"In progress","due_date":"","kid_tag":"","notes":"Review spending every Sunday evening.","updated_at":"2026-06-11 16:10"},
]

def ensure_data_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        pd.DataFrame(DEFAULT_ROWS, columns=COLUMNS).to_csv(DATA_FILE, index=False)

def load_data() -> pd.DataFrame:
    ensure_data_file()
    df = pd.read_csv(DATA_FILE)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[COLUMNS].fillna("")

def save_data(df: pd.DataFrame):
    df.to_csv(DATA_FILE, index=False)

def next_id(df: pd.DataFrame) -> int:
    if df.empty:
        return 1
    return int(pd.to_numeric(df["id"], errors="coerce").fillna(0).max()) + 1

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")
    owners = ["All"] + sorted([x for x in df["owner"].dropna().unique() if x])
    types = ["All"] + sorted([x for x in df["type"].dropna().unique() if x])
    statuses = ["All"] + sorted([x for x in df["status"].dropna().unique() if x])
    priorities = ["All"] + sorted([x for x in df["priority"].dropna().unique() if x])
    owner_filter = st.sidebar.selectbox("Owner", owners)
    type_filter = st.sidebar.selectbox("Type", types)
    status_filter = st.sidebar.selectbox("Status", statuses)
    priority_filter = st.sidebar.selectbox("Priority", priorities)
    query = st.sidebar.text_input("Search title or notes")
    filtered = df.copy()
    if owner_filter != "All": filtered = filtered[filtered["owner"] == owner_filter]
    if type_filter != "All": filtered = filtered[filtered["type"] == type_filter]
    if status_filter != "All": filtered = filtered[filtered["status"] == status_filter]
    if priority_filter != "All": filtered = filtered[filtered["priority"] == priority_filter]
    if query:
        q = query.lower()
        filtered = filtered[filtered["title"].str.lower().str.contains(q, na=False) | filtered["notes"].str.lower().str.contains(q, na=False)]
    return filtered

def add_item_form(df: pd.DataFrame):
    with st.expander("Add a new item", expanded=True):
        with st.form("add_item_form", clear_on_submit=True):
            title = st.text_input("Title")
            c1, c2 = st.columns(2)
            with c1:
                item_type = st.selectbox("Type", ["Buy", "Do", "Goal"])
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                owner = st.selectbox("Owner", ["You", "Wes", "Both"])
            with c2:
                status = st.selectbox("Status", ["Not started", "In progress", "Waiting", "Done"])
                due_date = st.date_input("Due date", value=None)
                kid_tag = st.text_input("Kid tag", placeholder="Optional")
            notes = st.text_area("Notes", placeholder="Add details, links, or next steps")
            submitted = st.form_submit_button("Save item", use_container_width=True)
            if submitted:
                if not title.strip():
                    st.error("Please enter a title.")
                    return
                new_row = {
                    "id": next_id(df),
                    "title": title.strip(),
                    "type": item_type,
                    "priority": priority,
                    "owner": owner,
                    "status": status,
                    "due_date": due_date.isoformat() if due_date else "",
                    "kid_tag": kid_tag.strip(),
                    "notes": notes.strip(),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                updated = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(updated)
                st.success("Item added.")
                st.rerun()

def quick_update(df: pd.DataFrame):
    st.subheader("Quick update")
    if df.empty:
        st.info("No items to update yet.")
        return
    labels = [f"#{int(row['id'])} - {row['title']}" for _, row in df.iterrows()]
    selected = st.selectbox("Choose an item", labels)
    row_id = int(selected.split(" - ")[0].replace("#", ""))
    row_index = df.index[df["id"] == row_id][0]
    status_options = ["Not started", "In progress", "Waiting", "Done"]
    owner_options = ["You", "Wes", "Both"]
    c1, c2 = st.columns(2)
    with c1:
        new_status = st.selectbox("Status", status_options, index=status_options.index(df.loc[row_index, "status"]))
    with c2:
        new_owner = st.selectbox("Owner", owner_options, index=owner_options.index(df.loc[row_index, "owner"]))
    if st.button("Save update", use_container_width=True):
        df.loc[row_index, "status"] = new_status
        df.loc[row_index, "owner"] = new_owner
        df.loc[row_index, "updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_data(df)
        st.success("Update saved.")
        st.rerun()

def main():
    st.title("Family Priorities")
    st.caption("A simple shared tracker for purchases, tasks, and goals.")
    df = load_data()
    filtered = apply_filters(df)
    open_items = df[df["status"] != "Done"]
    due_this_month = df[df["due_date"].astype(str).str.startswith(str(date.today())[:7])]
    high_priority = df[df["priority"] == "High"]
    done_items = df[df["status"] == "Done"]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Open", len(open_items))
    m2.metric("High priority", len(high_priority))
    m3.metric("Due this month", len(due_this_month))
    m4.metric("Done", len(done_items))
    add_item_form(df)
    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("Shared list")
        if filtered.empty:
            st.info("No items match the current filters.")
        else:
            st.dataframe(filtered[["id", "title", "type", "priority", "owner", "status", "due_date", "kid_tag", "updated_at"]], use_container_width=True, hide_index=True)
    with right:
        quick_update(df)
        st.subheader("This week focus")
        focus = df[(df["priority"] == "High") & (df["status"] != "Done")][["title", "owner", "status", "due_date"]]
        if focus.empty:
            st.info("No high-priority items right now.")
        else:
            st.table(focus.head(5))
    with st.expander("Project notes"):
        st.markdown("- Start with one shared list before adding accounts or notifications.\n- Keep fields simple so updating from a phone stays fast.\n- Upgrade later to a database and authentication when you outgrow CSV storage.")

if __name__ == "__main__":
    main()
