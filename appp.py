import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import date
import time

# ==========================================================
# LOGIN VALIDATION
# ==========================================================
if "user" not in st.session_state or "password" not in st.session_state or "role" not in st.session_state:
    st.warning("Please log in first.")
    st.switch_page("login.py")
    
USER = st.session_state.user
PASSWORD = st.session_state.password
ROLE = "Supervisor" if USER == "root" else "Viewer"

# ==========================================================
# ROLE HELPERS
# ==========================================================
def can_edit():
    return ROLE == "Supervisor"  # only root can edit/delete

def view_only_message():
    st.info("🔒 You have view-only access.")

# ==========================================================
# DATABASE CONNECTION
# ==========================================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password':'NAGS@2882',
    'database': 'wildlife_conservation'
}

@st.cache_resource
def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch=True):
    conn = get_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result
        else:
            conn.commit()
            cursor.close()
            return True
    except Error as e:
        if "denied" in str(e).lower():
            st.warning("🚫 You don't have permission to perform this action.")
        else:
            st.error(f"Query execution error: {e}")
        return None

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(page_title="Wildlife Conservation", page_icon="🦁", layout="wide")

# Sidebar user info
st.sidebar.markdown("---")
st.sidebar.success(f"👤 User: **{USER}** \n🎖️ Role: **{ROLE}**")
if USER == "root":
    st.sidebar.warning("⚠️ You are using ROOT (full access).")

if st.sidebar.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("login.py")

st.sidebar.markdown("---")

# ==========================================================
# SIDEBAR NAVIGATION
# ==========================================================
st.sidebar.title("🌿 Navigation")
page = st.sidebar.radio("Go to", [
    "🏠 Home",
    "📊 View All Tables",
    "🦁 Species Management",
    "🌳 Habitat Management",
    "👮 Ranger Management",
    "🐾 Animal Management",
    "🔍 Sighting Management",
    "⚠️ Threat Reports",
    "🏢 Organization Management",
    "🔧 Equipment Management",
    "⚙️ Functions & Procedures",
    "📈 Analytics"
])

# ==========================================================
# HOME PAGE
# ==========================================================
if page == "🏠 Home":
    st.markdown("<h1 style='text-align:center;color:#2E7D32;'>🦁 Wildlife Conservation Management System</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    species_count = execute_query("SELECT COUNT(*) as c FROM Species")
    animal_count = execute_query("SELECT COUNT(*) as c FROM Animal")
    ranger_count = execute_query("SELECT COUNT(*) as c FROM Ranger")
    
    with col1: st.metric("Total Species", species_count[0]['c'] if species_count else 0)
    with col2: st.metric("Tracked Animals", animal_count[0]['c'] if animal_count else 0)
    with col3: st.metric("Active Rangers", ranger_count[0]['c'] if ranger_count else 0)
    
    st.write("---")
    st.write("### Recent Threat Reports")
    recent = execute_query("""
        SELECT tr.Report_Date, h.habitat_type, h.region, tr.Threat_Level, tr.Description
        FROM Threat_Report tr JOIN Habitat h ON tr.Habitat_ID = h.Habitat_ID
        ORDER BY tr.Report_Date DESC LIMIT 5
    """)
    if recent:
        st.dataframe(pd.DataFrame(recent), use_container_width=True)

# ==========================================================
# VIEW ALL TABLES
# ==========================================================
elif page == "📊 View All Tables":
    st.header("📊 View All Database Tables")
    table = st.selectbox("Select Table", [
        "Species", "Alt_Names", "Habitat", "Inhabits", "Ranger", 
        "Assigned_To", "Animal", "Threat_Report", "Organization", 
        "Equipment", "Uses", "Sighting", "Sighting_Details"
    ])
    if st.button("Load Table"):
        data = execute_query(f"SELECT * FROM {table}")
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
            st.success(f"Loaded {len(data)} records from {table}")

# ==========================================================
# SPECIES MANAGEMENT
# ==========================================================
elif page == "🦁 Species Management":
    st.header("🦁 Species Management")

    if ROLE == "Viewer":
        tab_labels = ["View Species"]
    else:
        tab_labels = ["View Species", "Add Species", "Update Species", "Delete Species"]

    tabs = st.tabs(tab_labels)

    # View
    with tabs[0]:
        species = execute_query("SELECT * FROM Species")
        if species:
            st.dataframe(pd.DataFrame(species), use_container_width=True)
            st.write("### Alternative Names")
            alt = execute_query("SELECT s.common_name, a.Alt_Name FROM Species s JOIN Alt_Names a ON s.Sp_ID = a.Sp_ID")
            if alt:
                st.dataframe(pd.DataFrame(alt), use_container_width=True)

    # Add
    if can_edit() and len(tabs) > 1:
        with tabs[1]:
            with st.form("add_species"):
                common = st.text_input("Common Name")
                sci = st.text_input("Scientific Name")
                status = st.selectbox("Conservation Status", ["Least Concern", "Near Threatened", "Vulnerable", "Endangered", "Critically Endangered"])
                life = st.number_input("Average Lifespan (years)", min_value=1, max_value=200)
                alt_name = st.text_input("Alternative Name (optional)")
                if st.form_submit_button("Add"):
                    q = """INSERT INTO Species (common_name, Scientific_name, conservation_status, Avg_lifespan)
                           VALUES (%s,%s,%s,%s)"""
                    ok = execute_query(q, (common, sci, status, life), fetch=False)
                    if ok and alt_name:
                        spid = execute_query("SELECT LAST_INSERT_ID() as id")[0]['id']
                        execute_query("INSERT INTO Alt_Names (Sp_ID, Alt_Name) VALUES (%s,%s)", (spid, alt_name), fetch=False)
                    if ok:
                        st.success("✅ Species added successfully!")
                        time.sleep(1)
                        st.rerun()
    elif ROLE == "Viewer":
        view_only_message()

    # Update
    if can_edit() and len(tabs) > 2:
        with tabs[2]:
            species_list = execute_query("SELECT Sp_ID, common_name FROM Species")
            if species_list:
                spec_dict = {f"{s['common_name']} (ID:{s['Sp_ID']})": s['Sp_ID'] for s in species_list}
                sel = st.selectbox("Select Species", list(spec_dict.keys()))
                spid = spec_dict[sel]
                cur = execute_query("SELECT * FROM Species WHERE Sp_ID=%s", (spid,))[0]
                with st.form("update_species"):
                    c = st.text_input("Common Name", cur['common_name'])
                    sname = st.text_input("Scientific Name", cur['Scientific_name'])
                    stt = st.selectbox("Status",
                        ["Least Concern","Near Threatened","Vulnerable","Endangered","Critically Endangered"],
                        index=["Least Concern","Near Threatened","Vulnerable","Endangered","Critically Endangered"].index(cur['conservation_status']))
                    life = st.number_input("Lifespan", value=cur['Avg_lifespan'])
                    if st.form_submit_button("Update"):
                        execute_query("""UPDATE Species SET common_name=%s, Scientific_name=%s,
                                      conservation_status=%s, Avg_lifespan=%s WHERE Sp_ID=%s""",
                                      (c,sname,stt,life,spid), fetch=False)
                        st.success("✅ Updated successfully!")
                        time.sleep(1)
                        st.rerun()
    elif ROLE == "Viewer":
        # avoid repeating view_only_message many times; keep quiet if already shown above
        pass

    # Delete
    if can_edit() and len(tabs) > 3:
        with tabs[3]:
            sp_list = execute_query("SELECT Sp_ID, common_name FROM Species")
            if sp_list:
                sp_map = {f"{s['common_name']} (ID:{s['Sp_ID']})": s['Sp_ID'] for s in sp_list}
                sel = st.selectbox("Select to Delete", list(sp_map.keys()))
                spid = sp_map[sel]
                st.warning("⚠️ This will delete the species and related records.")
                if st.button("Delete"):
                    # NOTE: Deletion from Species should cascade to Alt_Names and Inhabits if ON DELETE CASCADE is set.
                    # Otherwise, you need to delete from child tables first. Assuming CASCADE for simplicity.
                    execute_query("DELETE FROM Species WHERE Sp_ID=%s", (spid,), fetch=False)
                    st.success("Deleted successfully!")
                    time.sleep(1)
                    st.rerun()

# ==========================================================
# HABITAT MANAGEMENT
# ==========================================================
elif page == "🌳 Habitat Management":
    st.header("🌳 Habitat Management")

    if ROLE == "Viewer":
        tab_labels = ["View Habitats"]
    else:
        tab_labels = ["View Habitats", "Add Habitat", "Update Habitat", "Delete Habitat"]

    tabs = st.tabs(tab_labels)

    # View
    with tabs[0]:
        habitat_data = execute_query("SELECT * FROM Habitat")
        if habitat_data:
            st.dataframe(pd.DataFrame(habitat_data), use_container_width=True)
            st.write("### Species in Habitats")
            species_habitat = execute_query("""
                SELECT h.habitat_type, h.region, s.common_name
                FROM Habitat h
                JOIN Inhabits i ON h.Habitat_ID = i.Habitat_ID
                JOIN Species s ON i.Sp_ID = s.Sp_ID
                ORDER BY h.habitat_type
            """)
            if species_habitat:
                st.dataframe(pd.DataFrame(species_habitat), use_container_width=True)

    # Add
    if can_edit() and len(tabs) > 1:
        with tabs[1]:
            with st.form("add_habitat"):
                habitat_type = st.text_input("Habitat Type")
                climate = st.selectbox("Climate", ["Tropical", "Humid", "Cool", "Arid"])
                region = st.text_input("Region")
                area_size = st.number_input("Area Size (sq km)", min_value=0.0, step=0.01)
                if st.form_submit_button("Add Habitat"):
                    query = """INSERT INTO Habitat (habitat_type, climate, region, area_size) 
                               VALUES (%s, %s, %s, %s)"""
                    result = execute_query(query, (habitat_type, climate, region, area_size), fetch=False)
                    if result:
                        st.success("Habitat added successfully!")
                        time.sleep(1)
                        st.rerun()
    elif ROLE == "Viewer":
        view_only_message()

    # Update
    if can_edit() and len(tabs) > 2:
        with tabs[2]:
            habitat_list = execute_query("SELECT Habitat_ID, habitat_type, region FROM Habitat")
            if habitat_list:
                habitat_dict = {f"{h['habitat_type']} - {h['region']} (ID: {h['Habitat_ID']})": h['Habitat_ID'] for h in habitat_list}
                selected = st.selectbox("Select Habitat to Update", list(habitat_dict.keys()))
                habitat_id = habitat_dict[selected]
                current = execute_query("SELECT * FROM Habitat WHERE Habitat_ID = %s", (habitat_id,))[0]
                with st.form("update_habitat"):
                    habitat_type = st.text_input("Habitat Type", value=current['habitat_type'])
                    climate = st.selectbox("Climate", ["Tropical", "Humid", "Cool", "Arid"],
                        index=["Tropical", "Humid", "Cool", "Arid"].index(current['climate']))
                    region = st.text_input("Region", value=current['region'])
                    area_size = st.number_input("Area Size", value=float(current['area_size']))
                    if st.form_submit_button("Update Habitat"):
                        query = """UPDATE Habitat SET habitat_type=%s, climate=%s, region=%s, area_size=%s 
                                   WHERE Habitat_ID=%s"""
                        result = execute_query(query, (habitat_type, climate, region, area_size, habitat_id), fetch=False)
                        if result:
                            st.success("Habitat updated successfully!")
                            time.sleep(1)
                            st.rerun()
    elif ROLE == "Viewer":
        pass

    # Delete
    if can_edit() and len(tabs) > 3:
        with tabs[3]:
            habitat_list = execute_query("SELECT Habitat_ID, habitat_type, region FROM Habitat")
            if habitat_list:
                habitat_dict = {f"{h['habitat_type']} - {h['region']} (ID: {h['Habitat_ID']})": h['Habitat_ID'] for h in habitat_list}
                selected = st.selectbox("Select Habitat to Delete", list(habitat_dict.keys()))
                habitat_id = habitat_dict[selected]
                st.warning("⚠️ This will delete the habitat and all related records!")
                if st.button("Delete Habitat"):
                    # NOTE: Assuming CASCADE delete is set on Inhabits, Assigned_To, and Threat_Report
                    result = execute_query("DELETE FROM Habitat WHERE Habitat_ID = %s", (habitat_id,), fetch=False)
                    if result:
                        st.success("Habitat deleted successfully!")
                        time.sleep(1)
                        st.rerun()

# ==========================================================
# RANGER MANAGEMENT
# ==========================================================
elif page == "👮 Ranger Management":
    st.header("👮 Ranger Management")

    if ROLE == "Viewer":
        tab_labels = ["View Rangers"]
    else:
        tab_labels = ["View Rangers", "Add Ranger", "Update Ranger", "Delete Ranger"]

    tabs = st.tabs(tab_labels)

    # View
    with tabs[0]:
        ranger_data = execute_query("SELECT * FROM Ranger")
        if ranger_data:
            st.dataframe(pd.DataFrame(ranger_data), use_container_width=True)
            st.write("### Ranger Habitat Assignments")
            assignments = execute_query("""
                SELECT r.fname, r.raankOfRanger, h.habitat_type, h.region, a.Assigned_Date
                FROM Ranger r
                JOIN Assigned_To a ON r.Ranger_ID = a.Ranger_ID
                JOIN Habitat h ON a.Habitat_ID = h.Habitat_ID
                ORDER BY r.fname
            """)
            if assignments:
                st.dataframe(pd.DataFrame(assignments), use_container_width=True)

    # Add
    if can_edit() and len(tabs) > 1:
        with tabs[1]:
            with st.form("add_ranger"):
                fname = st.text_input("Full Name")
                rank = st.selectbox("Rank", ["Junior Ranger", "Field Ranger", "Senior Ranger", "Wildlife Officer"])
                date_joined = st.date_input("Date Joined")
                phone = st.text_input("Phone")
                email = st.text_input("Email")
                if st.form_submit_button("Add Ranger"):
                    query = """INSERT INTO Ranger (fname, raankOfRanger, date_joined, Phone, email) 
                               VALUES (%s, %s, %s, %s, %s)"""
                    result = execute_query(query, (fname, rank, date_joined, phone, email), fetch=False)
                    if result:
                        st.success("Ranger added successfully!")
                        time.sleep(1)
                        st.rerun()
    elif ROLE == "Viewer":
        view_only_message()

    # Update
    if can_edit() and len(tabs) > 2:
        with tabs[2]:
            ranger_list = execute_query("SELECT Ranger_ID, fname FROM Ranger")
            if ranger_list:
                ranger_dict = {f"{r['fname']} (ID: {r['Ranger_ID']})": r['Ranger_ID'] for r in ranger_list}
                selected = st.selectbox("Select Ranger to Update", list(ranger_dict.keys()))
                ranger_id = ranger_dict[selected]
                current = execute_query("SELECT * FROM Ranger WHERE Ranger_ID = %s", (ranger_id,))[0]
                with st.form("update_ranger"):
                    fname = st.text_input("Full Name", value=current['fname'])
                    rank = st.selectbox("Rank", ["Junior Ranger", "Field Ranger", "Senior Ranger", "Wildlife Officer"],
                        index=["Junior Ranger", "Field Ranger", "Senior Ranger", "Wildlife Officer"].index(current['raankOfRanger']))
                    phone = st.text_input("Phone", value=current['Phone'])
                    email = st.text_input("Email", value=current['email'])
                    if st.form_submit_button("Update Ranger"):
                        query = """UPDATE Ranger SET fname=%s, raankOfRanger=%s, Phone=%s, email=%s 
                                   WHERE Ranger_ID=%s"""
                        result = execute_query(query, (fname, rank, phone, email, ranger_id), fetch=False)
                        if result:
                            st.success("Ranger updated successfully!")
                            time.sleep(1)
                            st.rerun()
    elif ROLE == "Viewer":
        pass

    # Delete
    if can_edit() and len(tabs) > 3:
        with tabs[3]:
            ranger_list = execute_query("SELECT Ranger_ID, fname FROM Ranger")
            if ranger_list:
                ranger_dict = {f"{r['fname']} (ID: {r['Ranger_ID']})": r['Ranger_ID'] for r in ranger_list}
                selected = st.selectbox("Select Ranger to Delete", list(ranger_dict.keys()))
                ranger_id = ranger_dict[selected]
                st.warning("⚠️ This will delete the ranger and all related records!")
                if st.button("Delete Ranger"):
                    # NOTE: Assuming CASCADE delete is set on Assigned_To, Uses, Threat_Report, Sighting, Sighting_Details, and Super_Ranger_ID is nullable or handled.
                    result = execute_query("DELETE FROM Ranger WHERE Ranger_ID = %s", (ranger_id,), fetch=False)
                    if result:
                        st.success("Ranger deleted successfully!")
                        time.sleep(1)
                        st.rerun()

# ==========================================================
# ANIMAL MANAGEMENT
# ==========================================================
elif page == "🐾 Animal Management":
    st.header("🐾 Animal Management")

    if ROLE == "Viewer":
        tab_labels = ["View Animals"]
    else:
        tab_labels = ["View Animals", "Add Animal", "Update Animal", "Delete Animal"]

    tabs = st.tabs(tab_labels)

    # View
    with tabs[0]:
        animal_data = execute_query("""
            SELECT a.Animal_ID, s.common_name, a.Tracking_ID, a.DOB, a.Gender, a.Health_status
            FROM Animal a
            JOIN Species s ON a.Sp_ID = s.Sp_ID
        """)
        if animal_data:
            st.dataframe(pd.DataFrame(animal_data), use_container_width=True)

    # Add
    if can_edit() and len(tabs) > 1:
        with tabs[1]:
            species_list = execute_query("SELECT Sp_ID, common_name FROM Species")
            if species_list:
                result = None
                with st.form("add_animal"):
                    animal_id = st.number_input("Animal ID", min_value=1, step=1)
                    species_dict = {s['common_name']: s['Sp_ID'] for s in species_list}
                    selected_species = st.selectbox("Species", list(species_dict.keys()))
                    sp_id = species_dict[selected_species]
                    tracking_id = st.text_input("Tracking ID")
                    dob = st.date_input("Date of Birth")
                    gender = st.selectbox("Gender", ["Male", "Female"])
                    health_status = st.selectbox("Health Status", ["Healthy", "Sick", "Injured", "Under Treatment"])
                    if st.form_submit_button("Add Animal"):
                        query = """INSERT INTO Animal (Animal_ID, Sp_ID, Tracking_ID, DOB, Gender, Health_status) 
                                   VALUES (%s, %s, %s, %s, %s, %s)"""
                        result = execute_query(query, (animal_id, sp_id, tracking_id, dob, gender, health_status), fetch=False)
                if result:
                    st.success("Animal added successfully!")
                    time.sleep(5)
                    st.rerun()
    elif ROLE == "Viewer":
        view_only_message()

    # Update
    if can_edit() and len(tabs) > 2:
        with tabs[2]:
            animal_list = execute_query("""
                SELECT a.Animal_ID, a.Sp_ID, s.common_name, a.Tracking_ID 
                FROM Animal a JOIN Species s ON a.Sp_ID = s.Sp_ID
            """)
            if animal_list:
                animal_dict = {f"{a['common_name']} - {a['Tracking_ID']}": (a['Animal_ID'], a['Sp_ID']) for a in animal_list}
                selected = st.selectbox("Select Animal to Update", list(animal_dict.keys()))
                animal_id, sp_id = animal_dict[selected]
                current = execute_query("SELECT * FROM Animal WHERE Animal_ID = %s AND Sp_ID = %s", (animal_id, sp_id))[0]
                with st.form("update_animal"):
                    tracking_id = st.text_input("Tracking ID", value=current['Tracking_ID'])
                    gender = st.selectbox("Gender", ["Male", "Female"], index=0 if current['Gender'] == 'Male' else 1)

                    # Fix: Corrected quotation and added robust fallback
                    health_options = ["Healthy", "Sick", "Injured", "Under Treatment"]
                    try:
                        selected_index = health_options.index(current['Health_status'])
                    except ValueError:
                        selected_index = 0  # default if somehow invalid value

                    health_status = st.selectbox("Health Status", health_options, index=selected_index)

                    if st.form_submit_button("Update Animal"):
                        query = """UPDATE Animal SET Tracking_ID=%s, Gender=%s, Health_status=%s 
                        WHERE Animal_ID=%s AND Sp_ID=%s"""
                        result = execute_query(query, (tracking_id, gender, health_status, animal_id, sp_id), fetch=False)
                if result:
                    st.success("Animal added successfully!")
                    time.sleep(1)
                    st.rerun()
                   
    elif ROLE == "Viewer":
        pass

    # Delete
    if can_edit() and len(tabs) > 3:
        with tabs[3]:
            animal_list = execute_query("""
                SELECT a.Animal_ID, a.Sp_ID, s.common_name, a.Tracking_ID 
                FROM Animal a JOIN Species s ON a.Sp_ID = s.Sp_ID
            """)
            if animal_list:
                animal_dict = {f"{a['common_name']} - {a['Tracking_ID']}": (a['Animal_ID'], a['Sp_ID']) for a in animal_list}
                selected = st.selectbox("Select Animal to Delete", list(animal_dict.keys()))
                animal_id, sp_id = animal_dict[selected]
                st.warning("⚠️ This will delete the animal and all related records!")
                if st.button("Delete Animal"):
                    # NOTE: Assuming CASCADE delete is set on Sighting_Details
                    result = execute_query("DELETE FROM Animal WHERE Animal_ID = %s AND Sp_ID = %s", (animal_id, sp_id), fetch=False)
                    if result:
                        st.success("Animal deleted successfully!")
                        time.sleep(1)
                        st.rerun()

# ==========================================================
# SIGHTING MANAGEMENT
# ==========================================================
elif page == "🔍 Sighting Management":
    st.header("🔍 Sighting Management")

    if ROLE == "Viewer":
        tab_labels = ["View Sightings"]
    else:
        tab_labels = ["View Sightings", "Add Sighting", "Add Sighting Detail"]

    tabs = st.tabs(tab_labels)

    # View
    with tabs[0]:
        sighting_data = execute_query("""
            SELECT s.Sighting_ID, r.fname as ranger_name, s.Sighting_Date, 
                s.Sighting_Time, s.Location
            FROM Sighting s
            JOIN Ranger r ON s.Ranger_ID = r.Ranger_ID
            ORDER BY s.Sighting_Date DESC
        """)
        if sighting_data:
            st.dataframe(pd.DataFrame(sighting_data), use_container_width=True)
            st.write("### Sighting Details (Animals Observed)")
            details = execute_query("""
                SELECT sd.sighting_ID, s.Location, sp.common_name, a.Tracking_ID, r.fname
                FROM Sighting_Details sd
                JOIN Sighting s ON sd.sighting_ID = s.Sighting_ID
                JOIN Animal a ON sd.Animal_ID = a.Animal_ID
                JOIN Species sp ON a.Sp_ID = sp.Sp_ID
                JOIN Ranger r ON sd.Ranger_ID = r.Ranger_ID
            """)
            if details:
                st.dataframe(pd.DataFrame(details), use_container_width=True)

    # Add Sighting
    if can_edit() and len(tabs) > 1:
        with tabs[1]:
            ranger_list = execute_query("SELECT Ranger_ID, fname FROM Ranger")
            if ranger_list:
                with st.form("add_sighting"):
                    ranger_dict = {r['fname']: r['Ranger_ID'] for r in ranger_list}
                    selected_ranger = st.selectbox("Ranger", list(ranger_dict.keys()))
                    ranger_id = ranger_dict[selected_ranger]
                    sighting_date = st.date_input("Sighting Date")
                    sighting_time = st.time_input("Sighting Time")
                    location = st.text_input("Location")
                    if st.form_submit_button("Add Sighting"):
                        query = """INSERT INTO Sighting (Ranger_ID, Sighting_Date, Sighting_Time, Location) 
                                VALUES (%s, %s, %s, %s)"""
                        result = execute_query(query, (ranger_id, sighting_date, sighting_time, location), fetch=False)
                        if result:
                            st.success("Sighting added successfully!")
                            time.sleep(1)
                            st.rerun()
    elif ROLE == "Viewer":
        view_only_message()

    # Add Sighting Detail (Link Animal to Sighting)
    if can_edit() and len(tabs) > 2:
        with tabs[2]:
            sighting_list = execute_query("SELECT Sighting_ID, Sighting_Date, Location FROM Sighting ORDER BY Sighting_ID DESC")
            animal_list = execute_query("SELECT Animal_ID, Sp_ID, Tracking_ID FROM Animal WHERE Health_status != 'Sick'")
            ranger_list = execute_query("SELECT Ranger_ID, fname FROM Ranger")
            
            if sighting_list and animal_list and ranger_list:
                st.info("Note: The 'trg_no_sick_sighting' trigger prevents adding sick animals here.")
                with st.form("add_sighting_detail"):
                    # Sighting Selection
                    sighting_map = {f"ID: {s['Sighting_ID']} ({s['Location']} on {s['Sighting_Date']})": s['Sighting_ID'] for s in sighting_list}
                    selected_sighting = st.selectbox("Select Sighting Event", list(sighting_map.keys()))
                    sighting_id = sighting_map[selected_sighting]
                    
                    # Animal Selection
                    animal_map = {f"ID: {a['Animal_ID']} (Track: {a['Tracking_ID']})": a['Animal_ID'] for a in animal_list}
                    selected_animal = st.selectbox("Select Animal Observed", list(animal_map.keys()))
                    animal_id = animal_map[selected_animal]
                    
                    # Ranger Selection (Ranger who observed this specific detail)
                    ranger_map = {r['fname']: r['Ranger_ID'] for r in ranger_list}
                    selected_ranger_detail = st.selectbox("Ranger Confirming Detail", list(ranger_map.keys()))
                    ranger_id_detail = ranger_map[selected_ranger_detail]

                    if st.form_submit_button("Link Animal to Sighting"):
                        # NOTE: Since Animal PK is composite (Animal_ID, Sp_ID), this insert assumes Sighting_Details only uses Animal_ID as FK, 
                        # which is an assumption based on the original DDL structure.
                        query = """INSERT INTO Sighting_Details (sighting_ID, Animal_ID, Ranger_ID) 
                                   VALUES (%s, %s, %s)"""
                        result = execute_query(query, (sighting_id, animal_id, ranger_id_detail), fetch=False)
                        if result:
                            st.success(f"Animal {animal_id} linked to Sighting {sighting_id} successfully!")
                            time.sleep(1)
                            st.rerun()
            else:
                st.warning("Ensure Habitats, Animals (not sick), and Rangers are added before linking sightings.")


# ==========================================================
# THREAT REPORTS
# ==========================================================
elif page == "⚠️ Threat Reports":
    st.header("⚠️ Threat Report Management")

    if ROLE == "Viewer":
        tab_labels = ["View Threats"]
    else:
        tab_labels = ["View Threats", "Log New Threat"]

    tabs = st.tabs(tab_labels)

    # View
    with tabs[0]:
        threat_data = execute_query("""
            SELECT tr.Report_ID, h.habitat_type, h.region, r.fname as ranger_name,
                tr.Report_Date, tr.Threat_Level, tr.Description
            FROM Threat_Report tr
            JOIN Habitat h ON tr.Habitat_ID = h.Habitat_ID
            JOIN Ranger r ON tr.Ranger_ID = r.Ranger_ID
            ORDER BY tr.Report_Date DESC
        """)
        if threat_data:
            df = pd.DataFrame(threat_data)
            def color_threat(val):
                if val == 'High':
                    return 'background-color: #ffcccc'
                elif val == 'Medium':
                    return 'background-color: #ffffcc'
                else:
                    return 'background-color: #ccffcc'
            styled_df = df.style.applymap(color_threat, subset=['Threat_Level'])
            st.dataframe(styled_df, use_container_width=True)

    # Log New Threat
    if can_edit() and len(tabs) > 1:
        with tabs[1]:
            st.write("### Log New Threat (Using Procedure)")
            habitat_list = execute_query("SELECT Habitat_ID, habitat_type, region FROM Habitat")
            ranger_list = execute_query("SELECT Ranger_ID, fname FROM Ranger")
            if habitat_list and ranger_list:
                with st.form("log_threat"):
                    habitat_dict = {f"{h['habitat_type']} - {h['region']}": h['Habitat_ID'] for h in habitat_list}
                    selected_habitat = st.selectbox("Habitat", list(habitat_dict.keys()))
                    habitat_id = habitat_dict[selected_habitat]
                    ranger_dict = {r['fname']: r['Ranger_ID'] for r in ranger_list}
                    selected_ranger = st.selectbox("Reporting Ranger", list(ranger_dict.keys()))
                    ranger_id = ranger_dict[selected_ranger]
                    threat_level = st.selectbox("Threat Level", ["Low", "Medium", "High"])
                    description = st.text_area("Description")
                    if st.form_submit_button("Log Threat Report"):
                        query = "CALL LogThreatReport(%s, %s, %s, %s)"
                        result = execute_query(query, (habitat_id, ranger_id, threat_level, description), fetch=False)
                        if result:
                            st.success("Threat report logged successfully!")
                            time.sleep(5)
                            st.rerun()
    elif ROLE == "Viewer":
        view_only_message()

# ==========================================================
# ORGANIZATION MANAGEMENT
# ==========================================================
elif page == "🏢 Organization Management":
    st.header("🏢 Organization Management")

    if ROLE == "Viewer":
        tab_labels = ["View Organizations"]
    else:
        tab_labels = ["View Organizations", "Add Organization", "Update Organization", "Delete Organization"]

    tabs = st.tabs(tab_labels)

    # View
    with tabs[0]:
        org_data = execute_query("SELECT * FROM Organization")
        if org_data:
            st.dataframe(pd.DataFrame(org_data), use_container_width=True)

    # Add
    if can_edit() and len(tabs) > 1:
        with tabs[1]:
            with st.form("add_org"):
                fi_name = st.text_input("Organization Name")
                type_org = st.selectbox("Type", ["NGO", "Government", "Private"])
                phone = st.text_input("Phone")
                email = st.text_input("Email")
                contact = st.text_input("Contact Person")
                if st.form_submit_button("Add Organization"):
                    query = """INSERT INTO Organization (fi_name, typeOrg, phone, email, contact) 
                            VALUES (%s, %s, %s, %s, %s)"""
                    result = execute_query(query, (fi_name, type_org, phone, email, contact), fetch=False)
                    if result:
                        st.success("Organization added successfully!")
                        time.sleep(1)
                        st.rerun()
    elif ROLE == "Viewer":
        view_only_message()

    # Update
    if can_edit() and len(tabs) > 2:
        with tabs[2]:
            org_list = execute_query("SELECT Org_ID, fi_name FROM Organization")
            if org_list:
                org_dict = {f"{o['fi_name']} (ID: {o['Org_ID']})": o['Org_ID'] for o in org_list}
                selected = st.selectbox("Select Organization to Update", list(org_dict.keys()))
                org_id = org_dict[selected]
                current = execute_query("SELECT * FROM Organization WHERE Org_ID = %s", (org_id,))[0]
                with st.form("update_org"):
                    fi_name = st.text_input("Organization Name", value=current['fi_name'])
                    type_org = st.selectbox("Type", ["NGO", "Government", "Private"],
                        index=["NGO", "Government", "Private"].index(current['typeOrg']))
                    phone = st.text_input("Phone", value=current['phone'])
                    email = st.text_input("Email", value=current['email'])
                    contact = st.text_input("Contact Person", value=current['contact'])
                    if st.form_submit_button("Update Organization"):
                        query = """UPDATE Organization SET fi_name=%s, typeOrg=%s, phone=%s, email=%s, contact=%s 
                            WHERE Org_ID=%s"""
                        result = execute_query(query, (fi_name, type_org, phone, email, contact, org_id), fetch=False)
                        if result:
                            st.success("Organization updated successfully!")
                            time.sleep(1)
                            st.rerun()
    elif ROLE == "Viewer":
        pass

    # Delete
    if can_edit() and len(tabs) > 3:
        with tabs[3]:
            org_list = execute_query("SELECT Org_ID, fi_name FROM Organization")
            if org_list:
                org_dict = {f"{o['fi_name']} (ID: {o['Org_ID']})": o['Org_ID'] for o in org_list}
                selected = st.selectbox("Select Organization to Delete", list(org_dict.keys()))
                org_id = org_dict[selected]
                st.warning("⚠️ Deleting an organization will fail if equipment is still linked to it.")
                if st.button("Delete Organization"):
                    # NOTE: Deletion will be restricted by the FK constraint on the Equipment table.
                    delete_query = "DELETE FROM Organization WHERE Org_ID = %s"
                    result = execute_query(delete_query, (org_id,), fetch=False)
                    if result:
                        st.success(f"✅ Organization ID {org_id} deleted successfully.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete organization. Check if all associated equipment has been removed first.")


# ==========================================================
# EQUIPMENT MANAGEMENT
# ==========================================================
elif page == "🔧 Equipment Management":
    st.header("🔧 Equipment Management")

    if ROLE == "Viewer":
        tab_labels = ["View Equipment"]
    else:
        tab_labels = ["View Equipment", "Add Equipment", "Update Equipment", "Assign Equipment", "Delete Equipment"]

    tabs = st.tabs(tab_labels)

    # View
    with tabs[0]:
        equipment_data = execute_query("""
            SELECT e.Equipment_ID, e.equip_type, e.StatusEqui, e.purchase_date, o.fi_name as organization
            FROM Equipment e
            JOIN Organization o ON e.Org_ID = o.Org_ID
        """)
        if equipment_data:
            st.dataframe(pd.DataFrame(equipment_data), use_container_width=True)
            st.write("### Equipment Usage")
            usage_data = execute_query("""
                SELECT r.fname as ranger_name, e.equip_type, u.Date_Issued, e.StatusEqui
                FROM Uses u
                JOIN Ranger r ON u.Ranger_ID = r.Ranger_ID
                JOIN Equipment e ON u.Equipment_ID = e.Equipment_ID
            """)
            if usage_data:
                st.dataframe(pd.DataFrame(usage_data), use_container_width=True)

    # Add
    if can_edit() and len(tabs) > 1:
        with tabs[1]:
            org_list = execute_query("SELECT Org_ID, fi_name FROM Organization")
            if org_list:
                with st.form("add_equipment"):
                    equip_type = st.text_input("Equipment Type")
                    status = st.selectbox("Status", ["Available", "In Use", "Maintenance"])
                    purchase_date = st.date_input("Purchase Date")
                    org_dict = {o['fi_name']: o['Org_ID'] for o in org_list}
                    selected_org = st.selectbox("Providing Organization", list(org_dict.keys()))
                    org_id = org_dict[selected_org]
                    if st.form_submit_button("Add Equipment"):
                        query = """INSERT INTO Equipment (StatusEqui, purchase_date, equip_type, Org_ID) 
                                VALUES (%s, %s, %s, %s)"""
                        result = execute_query(query, (status, purchase_date, equip_type, org_id), fetch=False)
                        if result:
                            st.success("Equipment added successfully!")
                            time.sleep(1)
                            st.rerun()
    elif ROLE == "Viewer":
        view_only_message()

    # Update
    if can_edit() and len(tabs) > 2:
        with tabs[2]:
            org_list = execute_query("SELECT Org_ID, fi_name FROM Organization")
            equip_list = execute_query("SELECT Equipment_ID, equip_type FROM Equipment")
            if equip_list and org_list:
                equip_map = {f"ID: {e['Equipment_ID']} - {e['equip_type']}": e['Equipment_ID'] for e in equip_list}
                selected_equip_id = st.selectbox("Select Equipment to Update", list(equip_map.keys()))
                equip_id = equip_map[selected_equip_id]
                current = execute_query("SELECT * FROM Equipment WHERE Equipment_ID = %s", (equip_id,))[0]
                
                org_dict = {o['fi_name']: o['Org_ID'] for o in org_list}
                org_names = list(org_dict.keys())
                current_org = execute_query("SELECT fi_name FROM Organization WHERE Org_ID = %s", (current['Org_ID'],))[0]['fi_name']
                
                with st.form("update_equipment"):
                    equip_type = st.text_input("Equipment Type", value=current['equip_type'])
                    status = st.selectbox("Status", ["Available", "In Use", "Maintenance"],
                        index=["Available", "In Use", "Maintenance"].index(current['StatusEqui']))
                    purchase_date = st.date_input("Purchase Date", value=current['purchase_date'])
                    selected_org_name = st.selectbox("Providing Organization", org_names, 
                        index=org_names.index(current_org))
                    org_id = org_dict[selected_org_name]
                    
                    if st.form_submit_button("Update Equipment"):
                        query = """UPDATE Equipment SET StatusEqui=%s, purchase_date=%s, equip_type=%s, Org_ID=%s 
                                   WHERE Equipment_ID=%s"""
                        result = execute_query(query, (status, purchase_date, equip_type, org_id, equip_id), fetch=False)
                        if result:
                            st.success("Equipment updated successfully!")
                            time.sleep(1)
                            st.rerun()
            else:
                st.warning("Please ensure organizations and equipment exist before updating.")


    # Assign
    if can_edit() and len(tabs) > 3:
        with tabs[3]:
            st.write("### Assign Equipment to Ranger")
            st.info("⚙️ This uses the trigger 'trg_equipment_inuse' to automatically update equipment status!")
            ranger_list = execute_query("SELECT Ranger_ID, fname FROM Ranger")
            equipment_list = execute_query("SELECT Equipment_ID, equip_type, StatusEqui FROM Equipment WHERE StatusEqui = 'Available'")
            if ranger_list and equipment_list:
                with st.form("assign_equipment"):
                    ranger_dict = {r['fname']: r['Ranger_ID'] for r in ranger_list}
                    selected_ranger = st.selectbox("Ranger", list(ranger_dict.keys()))
                    ranger_id = ranger_dict[selected_ranger]
                    equip_dict = {f"{e['equip_type']} (ID: {e['Equipment_ID']})": e['Equipment_ID'] for e in equipment_list}
                    selected_equip = st.selectbox("Equipment", list(equip_dict.keys()))
                    equipment_id = equip_dict[selected_equip]
                    date_issued = st.date_input("Date Issued", value=date.today())
                    if st.form_submit_button("Assign Equipment"):
                        query = """INSERT INTO Uses (Ranger_ID, Equipment_ID, Date_Issued) 
                                VALUES (%s, %s, %s)"""
                        result = execute_query(query, (ranger_id, equipment_id, date_issued), fetch=False)
                        if result:
                            st.success("Equipment assigned successfully! Status automatically updated to 'In Use' by trigger.")
                            time.sleep(2)
                            st.rerun()
            else:
                st.warning("No available equipment to assign.")

    # Delete
    if can_edit() and len(tabs) > 4:
        with tabs[4]:
            st.write("### Delete Equipment")
            equip_list = execute_query("SELECT Equipment_ID, equip_type, StatusEqui FROM Equipment")
            if equip_list:
                equip_map = {f"ID: {e['Equipment_ID']} - {e['equip_type']} (Status: {e['StatusEqui']})": e['Equipment_ID'] for e in equip_list}
                selected_equip_id = st.selectbox("Select Equipment to Delete", list(equip_map.keys()))
                equip_id = equip_map[selected_equip_id]
                
                st.warning("⚠️ Equipment must NOT be currently assigned to a Ranger to be deleted.")
                if st.button("Delete Selected Equipment"):
                    # Check for dependencies (if equipment is currently in use)
                    in_use_check = execute_query("SELECT * FROM Uses WHERE Equipment_ID = %s", (equip_id,), fetch=True)
                    
                    if in_use_check:
                        st.error("Cannot delete equipment: It is currently assigned to a Ranger (check the 'Uses' table). Please remove the assignment first.")
                    else:
                        # Attempt to execute DELETE DML statement
                        delete_query = "DELETE FROM Equipment WHERE Equipment_ID = %s"
                        result = execute_query(delete_query, (equip_id,), fetch=False)
                        
                        if result:
                            st.success(f"✅ Equipment ID {equip_id} deleted successfully.")
                            time.sleep(5)
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete Equipment. Check database permissions.")

# ==========================================================
# FUNCTIONS & PROCEDURES
# ==========================================================
elif page == "⚙️ Functions & Procedures":
    st.header("⚙️ Database Functions & Procedures")

    tab1, tab2, tab3, tab4 = st.tabs(["Animal Age", "Ranger Experience", "Threat Score", "Update Animal Health"])

    # 1️⃣ Animal Age
    with tab1:
        st.info("Uses function: age_of_animal(animal_id, sp_id)")
        animals = execute_query("""
            SELECT a.Animal_ID, a.Sp_ID, s.common_name, a.Tracking_ID 
            FROM Animal a JOIN Species s ON a.Sp_ID = s.Sp_ID
        """)
        if animals:
            amap = {f"{a['common_name']} - {a['Tracking_ID']}": (a['Animal_ID'], a['Sp_ID']) for a in animals}
            sel = st.selectbox("Select Animal", list(amap.keys()))
            aid, spid = amap[sel]
            if st.button("Calculate Age"):
                res = execute_query(f"SELECT age_of_animal({aid}, {spid}) as age")
                if res:
                    st.success(f"🎂 Animal Age: {res[0]['age']} years")

    # 2️⃣ Ranger Experience
    with tab2:
        st.info("Uses function: ranger_experience(ranger_id)")
        rangers = execute_query("SELECT Ranger_ID, fname FROM Ranger")
        if rangers:
            rmap = {r['fname']: r['Ranger_ID'] for r in rangers}
            sel = st.selectbox("Select Ranger", list(rmap.keys()))
            rid = rmap[sel]
            if st.button("Calculate Experience"):
                res = execute_query(f"SELECT ranger_experience({rid}) as exp")
                if res:
                    st.success(f"👮 Experience: {res[0]['exp']} years")

    # 3️⃣ Threat Score
    with tab3:
        st.info("Uses function: threat_severity_score(report_id)")
        threats = execute_query("""
            SELECT tr.Report_ID, h.habitat_type, tr.Threat_Level, tr.Report_Date
            FROM Threat_Report tr
            JOIN Habitat h ON tr.Habitat_ID = h.Habitat_ID
            ORDER BY tr.Report_Date DESC
        """)
        if threats:
            tmap = {f"Report {t['Report_ID']} - {t['habitat_type']} ({t['Threat_Level']})": t['Report_ID'] for t in threats}
            sel = st.selectbox("Select Threat Report", list(tmap.keys()))
            rid = tmap[sel]
            if st.button("Calculate Score"):
                res = execute_query(f"SELECT threat_severity_score({rid}) as score")
                if res:
                    score = res[0]['score']
                    text = {0: "Unknown", 1: "Low", 2: "Medium", 3: "High"}
                    st.success(f"⚠️ Threat Score: {score} ({text.get(score,'N/A')})")

    # 4️⃣ Update Animal Health
    with tab4:
        st.info("Uses procedure: UpdateAnimalHealth(tracking_id, new_status)")
        if can_edit():
            animals = execute_query("""
                SELECT a.Tracking_ID, s.common_name, a.Health_status
                FROM Animal a JOIN Species s ON a.Sp_ID = s.Sp_ID
            """)
            if animals:
                with st.form("update_health"):
                    amap = {f"{a['common_name']} - {a['Tracking_ID']} (Current: {a['Health_status']})": a['Tracking_ID'] for a in animals}
                    sel = st.selectbox("Select Animal", list(amap.keys()))
                    tid = amap[sel]
                    new = st.selectbox("New Health Status", ["Healthy", "Sick", "Injured", "Under Treatment"])
                    if st.form_submit_button("Update Health"):
                        execute_query("CALL UpdateAnimalHealth(%s, %s)", (tid, new), fetch=False)
                        st.success(f"✅ Updated health to {new}")
                        time.sleep(5)
                        st.rerun()
        else:
            view_only_message()

# ==========================================================
# ANALYTICS
# ==========================================================
elif page == "📈 Analytics":
    st.header("📈 Wildlife Analytics Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        st.write("### Conservation Status Distribution")
        data = execute_query("SELECT conservation_status, COUNT(*) as c FROM Species GROUP BY conservation_status")
        if data:
            df = pd.DataFrame(data)
            st.bar_chart(df.set_index("conservation_status"))

    with col2:
        st.write("### Animals by Health Status")
        data = execute_query("SELECT Health_status, COUNT(*) as c FROM Animal GROUP BY Health_status")
        if data:
            df = pd.DataFrame(data)
            st.bar_chart(df.set_index("Health_status"))

    st.write("---")

    col3, col4 = st.columns(2)
    with col3:
        st.write("### Threat Reports by Level")
        data = execute_query("SELECT Threat_Level, COUNT(*) as c FROM Threat_Report GROUP BY Threat_Level")
        if data:
            df = pd.DataFrame(data)
            st.bar_chart(df.set_index("Threat_Level"))

    with col4:
        st.write("### Equipment Status Overview")
        data = execute_query("SELECT StatusEqui, COUNT(*) as c FROM Equipment GROUP BY StatusEqui")
        if data:
            df = pd.DataFrame(data)
            st.bar_chart(df.set_index("StatusEqui"))

    st.write("---")
    st.write("### Species Count by Habitat")
    data = execute_query("""
        SELECT h.habitat_type, h.region, COUNT(DISTINCT i.Sp_ID) as species_count
        FROM Habitat h LEFT JOIN Inhabits i ON h.Habitat_ID = i.Habitat_ID
        GROUP BY h.Habitat_ID, h.habitat_type, h.region
        ORDER BY species_count DESC
    """)
    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True)

    st.write("---")
    st.write("### Ranger Assignment Summary")
    data = execute_query("""
        SELECT r.fname, r.raankOfRanger, COUNT(a.Habitat_ID) as habitats_assigned,
               TIMESTAMPDIFF(YEAR, r.date_joined, CURDATE()) as years_experience
        FROM Ranger r
        LEFT JOIN Assigned_To a ON r.Ranger_ID = a.Ranger_ID
        GROUP BY r.Ranger_ID, r.fname, r.raankOfRanger, r.date_joined
        ORDER BY years_experience DESC
    """)
    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True)

    st.write("---")
    st.write("### Recent Sightings Summary")
    data = execute_query("""
        SELECT DATE(s.Sighting_Date) as date,
               COUNT(DISTINCT s.Sighting_ID) as total_sightings,
               COUNT(DISTINCT sd.Animal_ID) as animals_spotted
        FROM Sighting s
        LEFT JOIN Sighting_Details sd ON s.Sighting_ID = sd.sighting_ID
        GROUP BY DATE(s.Sighting_Date)
        ORDER BY date DESC
        LIMIT 10
    """)
    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True)

# ==========================================================
# FOOTER + DB TEST
# ==========================================================
st.sidebar.markdown("---")
st.sidebar.info("""
**Wildlife Conservation System**
Version 1.0  
Developed for Sanctuary Management  
✅ Complete CRUD  
✅ Stored Procedures & Triggers  
✅ Real-time Analytics
""")

if st.sidebar.button("🔌 Test Database Connection"):
    conn = get_connection()
    if conn:
        st.sidebar.success("✅ Database Connected!")
        conn.close()
    else:
        st.sidebar.error("❌ Connection Failed.")