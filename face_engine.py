import streamlit as st

def show_verification_screen():
    st.markdown("<h2 style='text-align: center; color: #00d4ff;'>🛡️ BIOMETRIC SCAN</h2>", unsafe_allow_html=True)
    
    # High-Tech Laser Animation
    st.markdown('''
        <style>
        .scanner {
            width: 100%; height: 5px;
            background: #00d4ff;
            box-shadow: 0 0 15px #00d4ff;
            position: relative;
            animation: scan 2s infinite;
        }
        @keyframes scan { 0% { top: 0px; } 50% { top: 200px; } 100% { top: 0px; } }
        </style>
        <div style="height: 210px; border: 2px solid #333; position: relative; overflow: hidden;">
            <div class="scanner"></div>
        </div>
    ''', unsafe_allow_html=True)
    
    return st.camera_input("Verify Face to Unlock Portal")
