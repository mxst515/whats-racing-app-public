import streamlit as st
from dataclasses import dataclass
from typing import List, Tuple
import datetime

from core.globals import GLOBAL_RACING_SERIES

# DTO Data transfer Object
@dataclass
class FilterSelections:
    """
    Transport class. Used for safe transfer client choices from sidebar to controller
    """
    search_query: str
    selected_series: List[str]
    show_upcoming_only: bool
    show_chronological: bool
    date_range: Tuple[datetime.date, ...]

class SidebarView:
    """
    Visual component, representing sidebar with filters.
    Responsible for showing filters and return client choice
    """

    # AVAILABLE_SERIES = ["F1", "F2", "F3", "WEC", "INDYCAR", "INDYNXT", "NASCAR", "OTHER"]
    AVAILABLE_SERIES = GLOBAL_RACING_SERIES

    def __init__(self): 
        """
        Initialize default filter states in session memory ONLY if they don't exist.
        This prevents unnecessary state re-evaluations during UI re-renders.
        """
        if "series_selector" not in st.session_state:
            st.session_state.series_selector = self.AVAILABLE_SERIES
        if "date_picker" not in st.session_state:
            st.session_state.date_picker = []
    
    # --- CALLBACKS ---
    
    def __apply_date_shortcut(self):
        """
        Callback function to handle logic WHEN user clicks a pill for date selection
        """
        today = datetime.date.today()
        choice = st.session_state.shortcut_pills

        if choice == "Today":
            st.session_state.date_picker = (today, today)
        elif choice == "Tommorow":
            st.session_state.date_picker = (today, today + datetime.timedelta(days=1))
        elif choice == "Next Week":
            st.session_state.date_picker = (today, today + datetime.timedelta(days=7))
        elif choice == "Next Month":
            st.session_state.date_picker = (today, today + datetime.timedelta(days=30))
        else:
            st.session_state.date_picker = []

    def __select_all_series(self):
        """Callback to select all series in pills"""
        st.session_state.series_selector = self.AVAILABLE_SERIES

    def __deselect_all_series(self):
        """Callback to clear all series in pills"""
        st.session_state.series_selector = []

    # --- UI COMPONENTS ---

    def __render_search_section(self) -> str:
        """
        Renders the custom text search input
        """
        st.caption("CUSTOM SEARCH")
        return st.text_input(
            label="🔍 Search race or country", 
            placeholder="e.g., Monaco, le mans..."
        )
    
    def __render_series_selection(self) -> str:
        """
        Renders the series selection logic inside an expander.
        """
        st.caption("SELECT SERIES")
        with st.expander("🏎️ Select Racing Series", expanded=False):
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                st.button("Select All", on_click=self.__select_all_series, width="stretch")
            with col2:
                st.button("Clear", on_click=self.__deselect_all_series, width="stretch")

            # Series Pills
            selected_series = st.pills(
                label="Choose racing series",
                options=self.AVAILABLE_SERIES,
                selection_mode="multi",
                key="series_selector",
                label_visibility="visible" 
            )
        
        return selected_series if selected_series is not None else []

    def __render_date_section(self) -> Tuple[datetime.date, ...]:
        """
        Renders the date picker and quick select shortcuts.
        """
        date_range = st.date_input(
            label="📅 Select Date Range",
            # value=[],  # Empty by default
            key="date_picker",
            help="Select a start and end date to filter races within a specific timeframe. You can also set only one day",
            label_visibility="visible"
        )
        
        with st.container(width="content" , vertical_alignment="top", horizontal_alignment="center", border=False):
            st.segmented_control(
                label="Quick Select:",
                options=["Today", "Tommorow", "Next Week", "Next Month"],
                key="shortcut_pills",
                on_change=self.__apply_date_shortcut,
                label_visibility="visible",
                width="stretch"
            )

        return date_range
    
    def __render_view_options_section(self) -> Tuple[bool, bool]:
        """
        Renders the toggles for main view options and advanced settings.
        """
        st.caption("VIEW OPTIONS")
                
        show_upcoming_only = st.toggle(
            label="🚀 Only upcoming races",
            value=True,
            help="Turn off to see past races from this season."
        )
        
        with st.expander("⚙️ Experimental Options", expanded=False):
            show_chronological = st.toggle(
                label="⏱️ Chronological timeline",
                value=True,
                help="Turn off to group races by series rather than exact date."
            )

        return show_upcoming_only, show_chronological
    
    def __render_title_content(self):
        with st.container(gap="xsmall"):
            st.header("🏎️ Calendar Filters")
            st.markdown("Customize your racing schedule")
            st.space("xxsmall")

    def render(self, available_series: List[str]) -> FilterSelections:
        """
        Main render method for sidebar. Closing all UI logic in st.sidebar and return DTO Object
        """

        with st.sidebar:
            self.AVAILABLE_SERIES = available_series
            with st.container(gap="small"):
                self.__render_title_content()
                
                search_query = self.__render_search_section()
                safe_series = self.__render_series_selection()
                st.divider()
                date_range = self.__render_date_section()
                st.divider()
                show_upcoming_only, show_chronological = self.__render_view_options_section()
                st.divider()
                st.info("Changing filters will automatically refresh the list on the main screen")

            # DTO object
            return FilterSelections(search_query=search_query,
                                    selected_series=safe_series,
                                    show_upcoming_only=show_upcoming_only,
                                    show_chronological=show_chronological,
                                    date_range=date_range
            )