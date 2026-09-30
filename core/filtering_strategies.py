from abc import ABC, abstractmethod
from datetime import date
from typing import List
from core.models import Race

# main interface strategy
class FilterStrategy(ABC):
    @abstractmethod
    def filter(self, races: List[Race]) -> List[Race]:
        pass

# pass only races which do not ended
class UpcomingRacesStrategy(FilterStrategy):
    def filter(self, races: List[Race]) -> List[Race]:
        today_str = date.today().isoformat()

        upcoming_races = []

        for race in races:
            if not race.sessions:
                continue

            last_session_date = max(session.date for session in race.sessions) # return oldest date from all sessions in race weekend

            if last_session_date >= today_str:
                upcoming_races.append(race)

        return upcoming_races

# pass only races from checked series
class SeriesFilterStrategy(FilterStrategy):
    def __init__(self, selected_series: List[str]):
        self.selected_series = selected_series

    def filter(self, races: List[Race]) -> List[Race]:
        if not self.selected_series:
            return []
        
        return [race for race in races if race.series in self.selected_series]

# sort races chronologically by the date of their first session
class ChronologicalSortStrategy(FilterStrategy):
    def _get_race_start_date(self, race: Race) -> str:
        if not race.sessions:
            # Fallback for races without any sessions yet
            return "9999-12-31"
        # Return the earliest date from all sessions in the weekend
        return min(session.date for session in race.sessions)

    def filter(self, races: List[Race]) -> List[Race]:
        return sorted(races, key=self._get_race_start_date)
    
class SearchFilterStrategy(FilterStrategy):
    def __init__(self, query: str):
        self.query = query.lower().strip()

    def filter(self, races: List[Race]) -> List[Race]:
        if not self.query:
            return races
        
        return [
            race for race in races if (self.query in race.name.lower() or self.query in race.country.lower())
        ]
        
class DateRangeStrategy(FilterStrategy):
    def __init__(self, start_date: date, end_date: date):
        self.start_date_str = start_date.isoformat()
        self.end_date_str = end_date.isoformat()

    def filter(self, races: List[Race]) -> List[Race]:
        filtered_races = []

        for race in races:
            if not race.sessions:
                continue
            
            # Extract all session dates for the current race
            session_dates = [session.date for session in race.sessions]

            if any(self.start_date_str <= s_date <= self.end_date_str for s_date in session_dates):
                filtered_races.append(race)

        return filtered_races
    
# pipeline, get races and filter for all added strategies
class RaceCalendarPipeline:
    def __init__(self):
        self.strategies: List[FilterStrategy] = []

    def add_strategy(self, strategy: FilterStrategy):
        self.strategies.append(strategy)

    def execute(self, races: List[Race]) -> List[Race]:
        filtered_races = races
        for strategy in self.strategies:
            filtered_races = strategy.filter(filtered_races)

        return filtered_races



