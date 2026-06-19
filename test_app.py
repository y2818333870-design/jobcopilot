import streamlit as st

st.set_page_config(page_title="Test", page_icon="🚀")

st.title("Test App")

if st.button("Click me"):
    st.write("Button clicked!")
    st.balloons()

name = st.text_input("Name", key="name")
st.write(f"Hello {name}")
