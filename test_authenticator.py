import streamlit as st
import streamlit_authenticator as stauth

st.title("🔐 Authentication Test")

passwords = ["admin123", "view123"]
hashed_pw = stauth.Hasher(passwords).generate()

st.write("✅ Passwords hashed successfully!")
st.write(hashed_pw)
