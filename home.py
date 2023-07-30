import openai
import streamlit as st
from streamlit_chat import message
import connection


def clear_convo():
    st.session_state['past'] = []
    st.session_state['generated'] = []


def retrieve_inds(key, env):
    conn = connection.PineconeDBConnection('pinecone')
    conn._connect(api_key=key, environment=env)
    inds = conn.fetch_inds()
    return inds


def get_description():
    conn = connection.PineconeDBConnection('pinecone')
    conn._connect()
    dscrpt = conn.describe_inds(st.session_state['manual'])
    return dscrpt


if __name__ == '__main__':
    st.set_page_config(page_title='Pinecone ChatBot', page_icon=':robot_face: ')

    key = st.sidebar.text_input('OPENAI_API_KEY')
    pinecone_key = st.sidebar.text_input('PINECONE_API_KEY')
    pinecone_env = st.sidebar.text_input('PINECONE_ENV')
    openai.api_key = key
    if pinecone_key and pinecone_env:
        st.sidebar.title('Pinecone Indexes:')
        dbs = retrieve_inds(pinecone_key, pinecone_env)
        index = st.sidebar.radio('Please select an index:', dbs, key="init")
        st.session_state['manual'] = index
        st.sidebar.title('Index Description')
        st.sidebar.code(get_description(), language='json')
    else:
        st.toast('Did you forget to set your Pinecone Key and Env?')
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button:
        clear_convo()

    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    if 'manual' not in st.session_state:
        st.session_state['manual'] = []

    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key="input", height=75)
        submit_button = st.form_submit_button(label="Submit")

    if user_input and submit_button:
        conn = connection.PineconeDBConnection('pinecone')
        conn._connect(api_key=pinecone_key, environment=pinecone_env)
        index = st.session_state['manual']
        if key:
            response = conn.query(index, user_input)
            st.session_state.past.append(user_input)
            st.session_state.generated.append(response)
        else:
            st.toast('Did you forget to set your OPENAI_API_KEY?')

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated']) - 1, -1, -1):
            message(st.session_state['generated'][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + "user")
