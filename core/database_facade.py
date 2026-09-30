import streamlit as st
import firebase_admin
import os
from firebase_admin import credentials, firestore
from core.models import Race

@st.cache_resource
def get_db_client():
    try:
        if not firebase_admin._apps:
            local_key_path = "motorsport-calendar-app-firebase-key.json"

            if os.path.exists(local_key_path):
                cred = credentials.Certificate(local_key_path)
            else:
                cred_dict = dict(st.secrets["firebase"])
                cred = credentials.Certificate(cred_dict)
            
            firebase_admin.initialize_app(cred)
        
        return firestore.client()
    
    except Exception as e:
        st.error(f"Critical Database Error: {e}")
        return None

class FirebaseFacade:
    def __init__(self):
        self.db = get_db_client()
        self.collection_name = "Races"

    def get_all_races(self) -> list[Race]:
        if self.db is None:
            st.warning(f"Database connection is currently unavailable.")
            return []

        races_list = []

        try:
            docs = self.db.collection(self.collection_name).stream()

            for doc in docs:
                data = doc.to_dict()
                doc_id = doc.id

                race_obj = Race.from_dict(data, doc_id=doc_id)
                races_list.append(race_obj)

            return races_list
        except Exception as e:
            st.error(f"Failed to fetch races from database: {e}")
            return []
    
    def add_new_race(self, race: Race, custom_id: str = None) -> str:
        if self.db is None:
            st.error(f"Cannot add race. Database is down")
            return ""

        race_dict = race.to_dict()

        try:
            if custom_id:
                self.db.collection(self.collection_name).document(custom_id).set(race_dict)
                return custom_id
            else:
                update_time, doc_ref = self.db.collection(self.collection_name).add(race_dict)
                return doc_ref.id
        except Exception as e:
            st.error(f"Failed to add new race: {e}")
            return ""