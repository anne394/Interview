import streamlit as st
import requests

API = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="RAG Chat", layout="wide")
st.title("RAG Chat Demo")

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.username = None

with st.sidebar:
    st.header("Auth")
    username = st.text_input("Username", value=st.session_state.get("username", ""))
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)
    if col1.button("Register"):
        r = requests.post(f"{API}/auth/register", json={"username": username, "password": password})
        if r.ok:
            st.success("Registered — token saved")
            st.session_state.token = r.json()["access_token"]
            st.session_state.username = username
        else:
            st.error(r.text)
    if col2.button("Login"):
        r = requests.post(f"{API}/auth/login", json={"username": username, "password": password})
        if r.ok:
            st.success("Logged in")
            st.session_state.token = r.json()["access_token"]
            st.session_state.username = username
        else:
            st.error(r.text)

st.write("---")

st.header("Upload Document (txt only)")
with st.form("upload"):
    title = st.text_input("Title")
    uploaded = st.file_uploader("Text file (.txt)", type=["txt"])
    submit = st.form_submit_button("Upload")
    if submit:
        if uploaded is None:
            st.error("Choose a text file")
        else:
            files = {"file": (uploaded.name, uploaded.getvalue(), "text/plain")}
            data = {"title": title}
            headers = {}
            if st.session_state.token:
                headers["Authorization"] = f"Bearer {st.session_state.token}"
            resp = requests.post(f"{API}/docs/upload-text", data=data, files=files, headers=headers)
            if resp.ok:
                st.success(f"Uploaded — chunks: {resp.json().get('chunks')}")
            else:
                st.error(resp.text)

st.write("---")
st.header("Chat")

if "conv_id" not in st.session_state:
    st.session_state.conv_id = None

query = st.text_input("Ask a question", key="query")
if st.button("Send"):
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    payload = {"query": query, "conversation_id": st.session_state.get("conv_id")}
    r = requests.post(f"{API}/chat/ask", json=payload, headers=headers)
    if r.ok:
        data = r.json()
        st.session_state.conv_id = data.get("conversation_id")
        st.markdown("**Assistant:**")
        st.write(data.get("answer"))
        st.markdown("**Sources:**")
        st.write(data.get("sources"))
    else:
        st.error(r.text)