from streamlit_flow import streamlit_flow
from src.treeparser import Tree
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import ForceLayout, RadialLayout, TreeLayout, LayeredLayout, StressLayout
import streamlit as st
from src.LLM import LLM
from src.utils import clone
import os

st.set_page_config("GitPlexity", 
                   page_icon='assets/favicon.png',
                   layout="wide")

st.image('assets/logo.png', width=250)

@st.dialog("Input you link")
def getLink():
    repoUrl = st.text_input("GitHub Repository URL")
    if st.button("Submit"):
        if clone(repoUrl):
            st.session_state.repository = repoUrl
            st.rerun()
        else:
            st.error("Invalid Git URL.")


if 'repository' not in st.session_state:
    getLink()

else:
    if 'codeTree' not in st.session_state:
        # clone(st.session_state.repository)
        st.session_state.codeTree = Tree('root')
        st.session_state.state = StreamlitFlowState(st.session_state.codeTree.nodes, 
                                                    st.session_state.codeTree.edges)

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.model = LLM(
            codeTree=st.session_state.codeTree)

    if "node" not in st.session_state:
        st.session_state.node = None

    # col1, col2 = st.columns(2)
    tab1, tab2 = st.tabs(["Code Map", "Chat"])
    

    # with col1:
    with tab1:
        updated_state = streamlit_flow('codebase', 
                        st.session_state.state, 
                        layout=TreeLayout(
                            direction='right',
                            node_node_spacing=40,
                            # node_layer_spacing=20
                        ), 
                        fit_view=True, 
                        height=680, 
                        enable_node_menu=False,
                        show_controls=True,
                        enable_edge_menu=False,
                        enable_pane_menu=False,
                        get_edge_on_click=True,
                        get_node_on_click=True, 
                        hide_watermark=True, 
                        allow_new_edges=False,
                        pan_on_drag=True,
                        allow_zoom=True,
                        min_zoom=0.5)
        
        if st.session_state.node!=updated_state.selected_id and updated_state.selected_id and os.path.isfile(updated_state.selected_id):

            st.session_state.node = updated_state.selected_id
            
            st.session_state.messages = []
            st.session_state.model = LLM(
            codeTree=st.session_state.codeTree)

            user_message = f"Fetch {st.session_state.node}..."
            st.session_state.messages.append({"role": "user", "content": user_message})

            response = st.session_state.model.call(filepath=st.session_state.node)
            
            st.session_state.messages.append({"role": "assistant", "content": response})

    # with col2:
    with tab2:
        messages = st.container(height=600)
        for message in st.session_state.messages:
            with messages.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Say something"):

            messages.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            response = st.session_state.model.call(prompt=prompt)

            messages.chat_message("assistant").markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})