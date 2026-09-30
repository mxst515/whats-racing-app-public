import streamlit as st
from datetime import datetime
from core.models import Race
import os

class RaceCardView:
    """
    Visual Component, representing single race card, responsible only for rendering data on screen page
    """

    SERIES_EMOJIS = {
        "F1": "🏎️",
        "F2": "🏎️",
        "F3": "🏎️",
        "WEC": "🥇",
        "INDYCAR": "🏅",
        "WRC": "🚧",
    }

    def __init__(self, race: Race):
        """
        Dependency Injection
        Pass Race date model when the object is created
        """
        self.__race = race

    @property
    def series_emoji(self) -> str:
        return self.SERIES_EMOJIS.get(self.__race.series, "🏁")
    
    @property
    def weekend_date_range(self) -> str:
        """
        Property dynamicaly calculating date range for race weekend about on sessions
        Smart format: '03 - 08 MAR' (same month) or '28 FEB - 02 MAR' (cross-month).
        """
        if not self.__race.sessions:
            return "No dates"
        
        dates = sorted([session.date for session in self.__race.sessions])
        first_str= dates[0]
        last_str = dates[-1]

        if first_str == last_str:
            return datetime.strptime(first_str, "%Y-%m-%d").strftime("%d %b").upper()
        
        try:
            d1 = datetime.strptime(first_str, "%Y-%m-%d")
            d2 = datetime.strptime(last_str, "%Y-%m-%d")

            if d1.month == d2.month and d1.year == d2.year:
                # Format: 03 - 08 MAR
                return f"{d1.strftime('%d')} - {d2.strftime('%d %b').upper()}"
            else:
                # Format: 28 FEB - 02 MAR (cross month)
                return f"{d1.strftime('%d %b').upper()} - {d2.strftime('%d %b').upper()}"
        except ValueError:
            return f"{first_str} - {last_str}"

    @property
    def header_title(self) -> str:
        # property building text for expander bar
        # return f"{self.series_emoji} {self.__race.series} | Round {self.__race.round}: {self.__race.country} | {self.weekend_date_range}"
        return f"Round {self.__race.round} &nbsp;| &nbsp;{self.weekend_date_range}"

    @staticmethod
    def __format_date(date_str: str) -> str:
        """
        Static method
        Formats date from ISO (YYYY-MM-DD) to short format (DD.MM)
        """
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            return d.strftime("%d %b")
        except ValueError:
            return date_str
        
    def __get_calendar_page_date(self) -> tuple[str, str]:
        if not self.__race.sessions:
            return "--", "TBC"
        
        first_date_str = min(session.date for session in self.__race.sessions)

        try:
            d = datetime.strptime(first_date_str, "%Y-%m-%d")
            day = d.strftime("%d")           # Wyciąga dzień (np. 14)
            month = d.strftime("%b").upper() # Wyciąga skrót miesiąca z dużej litery (np. MAR)
            return day, month
        except ValueError:
            return "--", "TBC"
        
    def __render_sessions_list(self):
        # rendering harmonogram inside card
        if not self.__race.sessions:
            st.info("No sessions for this race weekend")
            return        
        
        sorted_sessions = sorted(self.__race.sessions, key=lambda s: (s.date, s.time))

        # for session in sorted_sessions:
        #     formatted_date = self.__format_date(session.date)
        #     st.markdown(f"📅 {formatted_date} | 🕒 **{session.time}** - {session.type}", text_alignment="justify")

        st.markdown(f"**{self.__race.name}**")

        for session in sorted_sessions:
            with st.container(border=True, horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
                formatted_date = self.__format_date(session.date)
                st.markdown(f"**{session.type}**", text_alignment="left")
                st.markdown(f"**📅 {formatted_date} | 🕒 {session.time}**", text_alignment="left")

    def render(self):
        """
        Main rendering method for drawing component
        """

        with st.container(horizontal=True, horizontal_alignment="center"):
            with st.container(border=True, horizontal=True, vertical_alignment="center", horizontal_alignment="center", width="stretch"):
                with st.container(gap="medium", horizontal=False, width="content", horizontal_alignment="center", vertical_alignment="center"):
                    cal_day, cal_month = self.__get_calendar_page_date()
                    st.markdown(
                        f"""
                        <div style="text-align: center; line-height: 1; min-width: 10px;">
                            <span style="font-size: 30px; font-weight: 500;">{cal_day}</span><br>
                            <span style="font-size: 20px; font-weight: 400; color: #ff4b4b;">{cal_month}</span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    try:
                        logo_path_svg = f"Logos/{self.__race.series.lower()}.svg"
                        logo_path_png = f"Logos/{self.__race.series.lower()}.png"
                        
                        if os.path.exists(logo_path_svg):
                            st.image(logo_path_svg, width=60)
                        else:
                            st.image(logo_path_png, width=60)
                    except:
                        st.image(f"Logos/empty.png", width=60)
                
                # main label container
                with st.container(gap="xsmall"):
                    st.subheader(f"**{self.__race.series} | {self.__race.country.strip()}**")
                    # st.subheader(f"**{self.header_title}**")
                    with st.expander(f"**{self.header_title}**"):
                        self.__render_sessions_list()

