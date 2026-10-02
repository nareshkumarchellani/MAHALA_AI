from agents.intake import run as intake
from agents.understanding import run as understanding
from agents.duplicate import run as duplicate
from agents.clustering import run as clustering
from agents.evidence import run as evidence
from agents.priority import run as priority
from agents.routing import run as routing

def test_all_agents_demo_mode():
    text='There is garbage on the street near the market.'
    assert intake(text)['clean_text']
    u=understanding(text)
    assert u['category'] in ['Garbage / Waste','Roads','Water','Sewerage','Street Lights','Electricity','Parks','Public Spaces','Public Safety','Other']
    d=duplicate(text,u['category'],24.9,67.0,[])
    assert d['similarity']==0
    assert clustering(u['category'],None,None,[])['case'] is None
    assert evidence()['evidence_valid']
    assert 0 <= priority(text,u['category'],u['summary'])['impact_score'] <= 100
    assert routing('Garbage / Waste',text,[{'name':'Waste Management'},{'name':'Municipal Services'}])['department']=='Waste Management'

def test_duplicate_and_cluster():
    existing=[{'id':7,'title':'Garbage on market road','description':'Trash is not being collected','category':'Garbage / Waste','latitude':24.900,'longitude':67.000}]
    d=duplicate('Trash is not collected on market road','Garbage / Waste',24.9005,67.0005,existing)
    assert d['similarity'] > 0
    cases=[{'id':3,'category':'Garbage / Waste','latitude':24.900,'longitude':67.000}]
    assert clustering('Garbage / Waste',24.901,67.001,cases)['case']['id']==3
