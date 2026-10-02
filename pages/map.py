import json
import streamlit as st
import folium
from streamlit_folium import st_folium
from database import query
from config import GOOGLE_MAPS_API_KEY

def render():
    st.subheader('🗺️ Civic Intelligence Map')
    complaints = query('''SELECT id,title,category,latitude,longitude,ai_priority,status
                          FROM complaints WHERE latitude IS NOT NULL AND longitude IS NOT NULL''')
    cases = query('''SELECT id,title,category,latitude,longitude,priority,status,complaint_count
                      FROM community_cases WHERE latitude IS NOT NULL AND longitude IS NOT NULL''')
    center = [24.9000, 67.0700]
    if complaints:
        center = [complaints[0]['latitude'], complaints[0]['longitude']]
    elif cases:
        center = [cases[0]['latitude'], cases[0]['longitude']]

    if GOOGLE_MAPS_API_KEY:
        markers = [
            {'lat': r['latitude'], 'lng': r['longitude'],
             'title': f"#{r['id']} {r['title']} • {r['category']} • {r['ai_priority']}"}
            for r in complaints
        ]
        case_markers = [
            {'lat': r['latitude'], 'lng': r['longitude'],
             'title': f"Community #{r['id']} {r['title']} • {r['complaint_count']} reports"}
            for r in cases
        ]
        payload = json.dumps(markers + case_markers).replace('</', '<\\/')
        html = f'''<!doctype html><html><body style="margin:0">
        <div id="map" style="height:520px;width:100%;border-radius:18px"></div>
        <script>
        const markers={payload};
        function initMap(){{
          const map=new google.maps.Map(document.getElementById('map'),{{
            center:{{lat:{center[0]},lng:{center[1]}}},zoom:11
          }});
          markers.forEach(x=>new google.maps.Marker({{
            position:{{lat:x.lat,lng:x.lng}},map,title:x.title
          }}));
        }}
        </script>
        <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_MAPS_API_KEY}&callback=initMap" async defer></script>
        </body></html>'''
        st.components.v1.html(html, height=540, scrolling=False)
        st.caption('Google Maps is enabled. Restrict the browser API key to your deployment domains in Google Cloud.')
        return

    m = folium.Map(location=center, zoom_start=11, tiles='OpenStreetMap')
    for r in complaints:
        folium.CircleMarker(
            [r['latitude'], r['longitude']], radius=7,
            popup=f"Complaint #{r['id']} — {r['title']} — {r['category']} — {r['ai_priority']}",
            tooltip='Complaint', fill=True
        ).add_to(m)
    for r in cases:
        folium.CircleMarker(
            [r['latitude'], r['longitude']], radius=12,
            popup=f"Community #{r['id']} — {r['title']} — {r['complaint_count']} complaints",
            tooltip='Community issue', fill=False
        ).add_to(m)
    st_folium(m, use_container_width=True, height=520)
    st.caption('OpenStreetMap fallback is used when Google Maps is not configured.')
