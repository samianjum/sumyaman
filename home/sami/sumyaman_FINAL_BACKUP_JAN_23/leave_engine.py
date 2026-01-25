import streamlit as st
from leave_apply import render_leave_apply
from leave_approvals import render_leave_approvals

def render_leave_system(u):
    # Agar data mein 'roll' ki key hai, to iska matlab ye student hai
    # Kyunki aapke debug data mein student ke paas 'roll' hai aur teacher ke paas nahi
    if 'roll' in u:
        render_leave_apply(u)
    else:
        render_leave_approvals(u)
