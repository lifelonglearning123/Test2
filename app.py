import streamlit as st
from st_paywall import add_auth


st.title("30 Day Twitter Content Planner")
add_auth(required=True)
