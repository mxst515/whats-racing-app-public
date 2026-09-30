import streamlit as st
from app.calendar_controller import CalendarController

def run_app():
    app = CalendarController()
    app.run()

if __name__ == "__main__":
    run_app()