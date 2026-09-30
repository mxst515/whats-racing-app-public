import streamlit as st
from typing import List
from datetime import datetime
from streamlit_theme import st_theme

from core.globals import APP_LOGOS_PATHS
from core.models import Race
from core.database_facade import FirebaseFacade
from core.filtering_strategies import (
                                       RaceCalendarPipeline, 
                                       UpcomingRacesStrategy, 
                                       SeriesFilterStrategy, 
                                       ChronologicalSortStrategy,
                                       SearchFilterStrategy,
                                       DateRangeStrategy
                                       )
from app.sidebar_view import SidebarView, FilterSelections
from app.race_card_view import RaceCardView

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_cached_races(_db: FirebaseFacade) -> List[Race]:
    """
    fetch race once for 3600s (1 hour) and hold in server ram
    """
    try:
        return _db.get_all_races()
    except Exception as e:
        st.error(f"Failed connecting to database: {e}")
        return []

class CalendarController:
    """
    MAIN CONTROLLER (MVC)
    Retrieves data from the database (Model), receives user decisions from the panel  
    filters them (Strategies), and delegates drawing results to the screen
    """
    def __init__(self):
        # init connection with database and sidebar
        self.db = FirebaseFacade()
        self.sidebar_view = SidebarView()

    def setup_page(self):
        # setup the main page
        st.set_page_config(
            page_title="Motorsport Calendar App",
            page_icon=":checkered_flag:",
            layout="centered",
            initial_sidebar_state="auto"
        )
        st.logo(APP_LOGOS_PATHS["RED"], size="large")

    def render_header(self):
        theme = st_theme()

        logo_path = APP_LOGOS_PATHS["DARK"]

        if theme is not None and theme.get("base") == "dark":
            logo_path = APP_LOGOS_PATHS["LIGHT"]
                    
        st.image(logo_path, width=500)

        st.title("Motorsport Calendar App", text_alignment="left")
        st.markdown("All of your favourite racing series in one place", text_alignment="right")
        st.divider()

        
    # def __fetch_all_races(self) -> List[Race]:
    #     try:
    #         return self.db.get_all_races()
    #     except Exception as e:
    #         st.error(f"Failed connecting to database {e}")
    #         return []

    def __get_race_month(self, race: Race) -> str:
        # helper method, parse month and format it from the first session

        if not race.sessions:
            return "UNKNOWN DATE"
        
        first_date_str = min(session.date for session in race.sessions)

        try:
            d = datetime.strptime(first_date_str, "%Y-%m-%d")
            return d.strftime("%B %Y").upper()
        except ValueError:
            return "UNKNOWN DATE"
    
    def __apply_filters(self, races: List[Race], filters: FilterSelections) -> list[Race]:
        pipeline = RaceCalendarPipeline()

        if filters.search_query:
            pipeline.add_strategy(SearchFilterStrategy(filters.search_query))

        pipeline.add_strategy(SeriesFilterStrategy(filters.selected_series))

        if filters.date_range:
            if len(filters.date_range) == 2:
                pipeline.add_strategy(DateRangeStrategy(filters.date_range[0], filters.date_range[1]))
            elif len(filters.date_range) == 1:
                pipeline.add_strategy(DateRangeStrategy(filters.date_range[0], filters.date_range[0]))

        if filters.show_upcoming_only:
            pipeline.add_strategy(UpcomingRacesStrategy())

        if filters.show_chronological:
            pipeline.add_strategy(ChronologicalSortStrategy())

        return pipeline.execute(races)
        
    def __render_main_content(self, filtered_races: List[Race]):
        # render the main race list
        with st.container(vertical_alignment="center", horizontal_alignment="center", height="stretch"):
            with st.container(vertical_alignment="center", horizontal_alignment="center", width="stretch"): #### content
                with st.container(vertical_alignment="top", horizontal_alignment="center", height="content", gap=None): #title logo
                    self.render_header()
                    
                if not filtered_races:
                    st.warning("No Races Matching Preferences")
                    return
                
                current_month = None

                for race in filtered_races:
                    # render month name in separete
                    race_month = self.__get_race_month(race)

                    if race_month != current_month:
                        st.subheader(f"{race_month}")
                        current_month = race_month

                    card_view = RaceCardView(race)
                    card_view.render()
       
    def run(self):
        self.setup_page()

        with st.spinner("Fetching data from database..."):
            all_races = fetch_cached_races(self.db)

        dynamic_series_list = sorted(list(set(race.series for race in all_races)))

        user_filters = self.sidebar_view.render(available_series=dynamic_series_list)

        final_races = self.__apply_filters(all_races, user_filters)

        self.__render_main_content(final_races)
    