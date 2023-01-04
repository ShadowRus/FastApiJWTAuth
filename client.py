import streamlit as st
import requests
import socket
def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

def check_password():
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
                st.session_state["username"] in st.secrets["passwords"]
                and st.session_state["password"]
                == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False


    if 'password_correct' not in st.session_state:
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state['password_correct']:
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        return True

HOST = extract_ip()
PORT = 8084
url ='http://'+ HOST+ ':' + str(PORT)

with st.form('Auth'):
    username = st.text_input('Login')
    password = st.text_input('Password', type= 'password')
    data = {
        "username": str(username),
        "password": str(password)
    }
    if st.form_submit_button('Login'):
        r1 = requests.post(str(url + '/login'),json = data)
        if r1.status_code == 200:
            j1 = r1.json()
            st.write(j1["access_token"])
            st.session_state['access_token']= j1["access_token"]

st.write('Get secrets')
if st.button('Get'):
    payload = {'Authorization': str('Bearer ' + st.session_state['access_token'])}
    r1 = requests.post(str(url + '/secret'),headers= payload)
    st.write(r1.text)