import streamlit as st

if "page" not in st.session_state:
    st.session_state["page"]="main"

def navigate(page):
    st.session_state["page"]=page


#Main Page [Landing page]
if st.session_state["page"] == "main":
    st.title("Welcome to Landing Page")

    st.button("Register",on_click=lambda:navigate("Register"))
    st.button("Login",on_click=lambda:navigate("Login"))

elif st.session_state["page"] == "Register":
    st.title("Welcome to Registeration Page")

    st.button("Back to main page",on_click=lambda:navigate("main"))

elif st.session_state["page"]=="Login":
    st.title("Welcome to Login Page")
    st.button("Back to main page",on_click=lambda:navigate("main"))


elif st.session_state["page"]=="home":
    st.title("Welcome to Home page")