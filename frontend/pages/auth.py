import streamlit as st
from utils.apis import login_user, register_user

st.markdown("<h2 class='main-header' style='text-align: center;'>🔐 Login or Register</h2>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Create a centered form container
with st.container():
    # Width-limited form in the center
    form_col = st.columns([1, 3, 1])[1]  # center column

    with form_col:
        auth_mode = st.radio("Choose mode", ["Login", "Register"], horizontal=True)
        with st.form("auth_form"):
            if auth_mode == "Login":
                username = st.text_input("Username", key="auth_username")
                password = st.text_input("Password", type="password", key="auth_password")

            if auth_mode == "Register":
                first_name = st.text_input("First Name", key="auth_first_name")
                last_name = st.text_input("Last Name", key="auth_last_name")
                username = st.text_input("Username", key="auth_username")
                password = st.text_input("Password", type="password", key="auth_password")
                confirm_password = st.text_input("Confirm Password", type="password", key="auth_confirm_password")

            submitted = st.form_submit_button("✅ Submit", use_container_width=True)

        # Process form submission
        if submitted:
            if not username or not password:
                st.warning("Please fill in all required fields.")
            elif auth_mode == "Register" and password != confirm_password:
                st.error("Passwords do not match.")
            else:
                with st.spinner("Processing..."):
                    if auth_mode == "Login":
                        success, user_data = login_user(username, password)
                    else:
                        success, user_data = register_user(username, password)

                if success:
                    st.session_state.logged_in = True
                    st.session_state.user = user_data["user"]
                    st.session_state.auth_token = user_data["token"]
                    st.success(f"{auth_mode} successful! Welcome {username}.")
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials or registration failed.")
