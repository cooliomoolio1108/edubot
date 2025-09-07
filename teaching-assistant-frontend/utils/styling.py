import streamlit as st

def inject_custom_css():
    css = """
    <style>
    h2 {
        margin-left:10px;
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
    }
    [data-testid="stTab"] {
        font-size:50px
    }
    section[data-testid="stSidebar"] [data-testid="stHeading"] {
        padding-left: 10px;
    }
    [data-testid="stPageLink-NavLink"] {
        border-left: 1px solid rgba(250, 250, 250, 0.2);
        border-bottom: 1px solid rgba(250, 250, 250, 0.2);
        
    }
    [data-testid="stPopoverBody"] {
        max-width: 50% !important;   /* adjust width */
        padding: 8px !important;   /* optional: reduce padding */
    }
    [data-testid="stPopoverButton"] {
        border: 0px;
        background: rgb(0, 0, 0, 0);
    }
    [data-testid="stPopoverBody"] [class*="st-key-delete_"] [data-testid="stButton"] button {
        border: none !important;
        background: rgb(0, 0, 0, 0);
        color: red;
    }
    [data-testid="stPopoverBody"] [data-testid="stButton"] button {
        border: none !important;
        background: rgb(0, 0, 0, 0);
        color: #818589;
    }
    div[data-testid="stSidebarHeader"] > img, div[data-testid="collapsedControl"] > img {
        display: flex;
        justify-content: center;  /* center horizontally */
        align-items: center;
        height: 8rem;
        width: auto;
    }
    div[data-testid="stSidebarContent"] {
        padding-top: 2rem;
    }
    div[data-testid="stSidebarHeader"], div[data-testid="stSidebarHeader"] > *,
    div[data-testid="collapsedControl"], div[data-testid="collapsedControl"] > * {
        display: flex;
        align-items: center;
    }
    [data-testid="stSidebarNavItems"] {
        padding-top: 2rem;
    }
    # [data-testid="stSidebar"] {
    #     display: flex;
    # }
    [data-testid="stVerticalBlock"] {
        gap: 0.6rem;
    }
    [data-testid="stHeader"] {
        background: rgb(0, 0, 0, 0);
    }

    [data-testid="stBaseButton-primary"] {
        background: rgb(255, 255, 255, 1);
        border: 1px solid rgba(255, 255, 255, 1);
        transition: all 0.4s ease; /* slower and smooth */
        color: rgb(0, 0, 0, 1);
    }
    [data-testid="stBaseButton-primary"]:hover {
        background: rgb(24 29 155);
        border: 1px solid rgb(24 29 155);
        color: rgb(255, 255, 255, 1);
    }
    data-testid="stBaseButton-primary"]:active {
        color: white !important;
        background: rgb(24 29 155);
        border: 1px solid rgb(24 29 155);
    }
    data-testid="stBaseButton-primary"]:click {
        color: white !important;
        background: rgb(24 29 155);
        border: 1px solid rgb(24 29 155);
    }
    data-testid="stBaseButton-primary"]:focus {
        color: white !important;
        background: rgb(24 29 155);
        border: 1px solid rgb(24 29 155);
    }
    section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
        text-align: left;
        transition: all 0.4s ease;  /* slower and smooth */
        background: rgb(0, 0, 0, 0);
        border: 0;
        padding: 0.2rem !important;  /* override inline style */
        justify-content: flex-start;  /* align text left */
        width: inherit !important;       /* make full-width */
        box-sizing: border-box;       /* include padding in width */
        display: flex;                /* required to align text with justify-content */
    }
    section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
        color: back !important;
        background: rgba(0, 0, 0, 0.2);
        border: 0px solid rgb(24 29 155);
        width: inherit;
    }
    # section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:active {
    #     color: white !important;
    #     background: rgba(24, 29, 155, 0.6);a
    #     border: 1px solid rgb(24 29 155);
    # }
    # section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:focus {
    #     color: white !important;
    #     background: rgba(24, 29, 155, 0.8);
    #     border: 1px solid rgb(24 29 155);
    #     width: inherit;
    # }
    # section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] button:hover {
    #     color: white !important;
    #     background: rgba(24, 29, 155, 0.8);
    #     border: 1px solid rgb(24 29 155);
    # }
    [data-testid="stFileUploaderDropzone"] {
        display: flex;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] {
        display: flex;
    }
    iframe {
        border: none;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        width: 100%;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    st.logo("assets/chatbot.png", size='large')