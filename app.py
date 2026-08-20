import base64
import os
from datetime import datetime
import pandas as pd
import streamlit as st
from supabase import create_client

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Assessment Deduction — Angels Bud Academy", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- IMAGE ENCODING HELPER ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

crest_b64 = get_base64_image("assets/angels-bud-crest.png")
vok_b64 = get_base64_image("assets/vok-banner.png")

# --- CUSTOM CSS FOR EXACT UI MATCH ---
st.markdown(
    """
    <style>
    /* 1. Global App Background */
    .stApp {
        background-color: #f7f4ec !important;
    }
    
    /* Remove default top padding */
    .block-container {
        padding-top: 2rem !important;
        max-width: 850px !important; 
    }

    /* 2. Top Dark Green Header Card */
    .main-header-card {
        background-color: #033c29;
        border-radius: 16px;
        padding: 40px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .header-top-row {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
    }
    
    .logo-box {
        background-color: white;
        border-radius: 12px;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 5px;
    }
    
    .logo-box img {
        max-width: 100%;
        max-height: 100%;
    }
    
    .academy-badge {
        background-color: #eabf8a;
        color: #033c29;
        font-family: -apple-system, sans-serif;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.5px;
        padding: 6px 14px;
        border-radius: 20px;
        text-transform: uppercase;
    }
    
    .header-title {
        font-family: 'Georgia', serif;
        font-size: 42px;
        font-weight: bold;
        margin: 0 0 5px 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-family: 'Georgia', serif;
        font-size: 24px;
        font-weight: bold;
        margin: 0 0 20px 0;
    }
    
    .header-description {
        font-family: -apple-system, sans-serif;
        font-size: 14px;
        line-height: 1.5;
        margin: 0;
        max-width: 90%;
        opacity: 0.95;
    }

    /* 3. Style Streamlit's native containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 10px 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* 4. Help Instruction Card */
    .help-card {
        background-color: #f1ebd8;
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        margin-top: 25px;
        margin-bottom: 40px;
    }
    
    .help-title {
        font-family: 'Georgia', serif;
        color: #033c29;
        font-size: 20px;
        font-weight: bold;
        margin: 0 0 10px 0;
    }
    
    .help-description {
        font-family: -apple-system, sans-serif;
        color: #4b5563;
        font-size: 14px;
        margin: 0;
        line-height: 1.5;
    }

    /* 5. Footer Styling */
    .footer-divider {
        border: 0;
        border-top: 1px solid #e5e7eb;
        margin: 40px 0 25px 0;
    }
    
    .footer-container {
        text-align: center;
        font-family: -apple-system, sans-serif;
        font-size: 13px;
        color: #4b5563;
        line-height: 1.8;
    }
    
    .footer-container b {
        color: #033c29;
    }
    
    .powered-by-text {
        font-size: 10px;
        color: #6b7280;
        letter-spacing: 2px;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 5px;
    }

    /* Adjust Selectbox label */
    .stSelectbox label p {
        font-family: -apple-system, sans-serif;
        color: #111827;
        font-size: 14px;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SUPABASE CONNECTION SETUP ---
@st.cache_resource
def init_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

# --- CONSTANTS ---
CENTRES = [
    "Aston", "Bayan Lepas", "Kepong", "Light Grey", "Puchong", 
    "Taman Midah", "Gerik", "Ipoh", "Kelana Jaya", "Kajang"
]

CENTRE_CLASSES = {
    "Aston": 2, "Bayan Lepas": 1, "Kepong": 2, "Light Grey": 1, 
    "Puchong": 3, "Taman Midah": 2, "Gerik": 1, "Ipoh": 1, 
    "Kelana Jaya": 2, "Kajang": 1,
}

GRADES = [f"Grade {i}" for i in range(1, 9)]

# --- SUBJECT & N/A CONFIGURATIONS ---
def get_subjects_and_na(grade):
    if grade in ["Grade 1", "Grade 2", "Grade 3"]:
        return [("Maths", True), ("Language Arts", True), ("Science", True), ("LA Extensions", False), ("Social Studies", False)]
    elif grade in ["Grade 4", "Grade 5"]:
        return [("Maths", True), ("Language Arts", True), ("Science", True), ("LA Extensions", False), ("Social Studies", True)]
    elif grade == "Grade 6":
        return [("Math 6", True), ("English 6", True), ("Life Science", True), ("Digital Media Literacy", True), ("Environmental Science", True), ("Ancient World History", True)]
    elif grade == "Grade 7":
        return [("Math 7", True), ("English 7", True), ("Earth & Space Science", True), ("Learning Strategies", True), ("Introduction to Art", True), ("World Culture & Geography", True)]
    elif grade == "Grade 8":
        return [("Math 8", True), ("English 8", True), ("Physical Science", True), ("United States History", True), ("Introduction to Public Speaking & Communications", True)]
    return []

# --- FETCH DATA ---
def fetch_all_profiles():
    try:
        response = supabase.table("profiles").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def fetch_records_for_student(name, centre):
    try:
        response = supabase.table("records").select("*").eq("profile_key", f"{name}_{centre}").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

# --- MAIN UI: HEADER BANNER ---
img_tag = f'<img src="data:image/png;base64,{crest_b64}" alt="Crest">' if crest_b64 else ''

st.markdown(
    f"""
    <div class="main-header-card">
        <div class="header-top-row">
            <div class="logo-box">
                {img_tag}
            </div>
            <div class="academy-badge">ANGELS BUD ACADEMY</div>
        </div>
        <h1 class="header-title">Assessment Deduction</h1>
        <h2 class="header-subtitle">Angels Bud Academy</h2>
        <p class="header-description">Select your centre below to see the student profiles kept there. All centres share one record book, so nothing is ever lost when a student upgrades to the next grade.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- MAIN UI: CENTRE SELECTION CARD ---
with st.container(border=True):
    st.markdown(
        """
        <h2 style="font-family: 'Georgia', serif; color: #033c29; font-size: 24px; font-weight: bold; margin: 5px 0 5px 0;">Choose your centre</h2>
        <p style="font-family: -apple-system, sans-serif; color: #6b7280; font-size: 14px; margin: 0 0 20px 0;">Student profiles appear once a centre is selected.</p>
        """,
        unsafe_allow_html=True
    )
    
    selected_centre = st.selectbox(
        "Centre", 
        ["Select your centre"] + CENTRES,
        label_visibility="visible"
    )

# --- CONDITIONAL VIEW & DASHBOARD LOGIC ---
if selected_centre == "Select your centre":
    # Show the "Help" Card when no centre is selected
    st.markdown(
        """
        <div class="help-card">
            <h3 class="help-title">Need a hand with the next step?</h3>
            <p class="help-description">Choose your centre, open a student profile and record the assessment deduction for the current grade — every previous grade stays saved.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    # Fetch profiles for the selected centre
    all_profiles = fetch_all_profiles()
    centre_profiles = [p for p in all_profiles if p["centre"] == selected_centre]

    # --- SIDEBAR: ACTIONS ---
    st.sidebar.header(f"⚙️ Actions ({selected_centre})")
    action_mode = st.sidebar.radio("Select Operation", ["View Records", "Create Student Profile", "Withdraw Student"])

    # 1. CREATE PROFILE FORM
    if action_mode == "Create Student Profile":
        st.sidebar.subheader("Register New Student")
        max_classes = CENTRE_CLASSES.get(selected_centre, 1)
        class_options = [f"Class {i}" for i in range(1, max_classes + 1)]

        with st.sidebar.form("create_profile"):
            full_name = st.text_input("Student Full Name").strip()
            grade = st.selectbox("Starting Grade", GRADES)
            class_name = st.selectbox("Class", class_options)
            submit_btn = st.form_submit_button("Register & Start")

            if submit_btn:
                if not full_name:
                    st.sidebar.error("Please enter the student's full name.")
                else:
                    existing_names = [p["name"].lower() for p in centre_profiles]
                    if full_name.lower() in existing_names:
                        st.sidebar.warning(f"A student named '{full_name}' already exists in {selected_centre}!")
                    else:
                        profile_key = f"{full_name}_{selected_centre}"
                        try:
                            supabase.table("profiles").insert({
                                "profile_key": profile_key,
                                "name": full_name,
                                "grade": grade,
                                "class": class_name,
                                "centre": selected_centre,
                                "status": "On Progress",
                            }).execute()

                            subj_config = get_subjects_and_na(grade)
                            records_to_insert = []
                            for subj, has_wb in subj_config:
                                records_to_insert.append({
                                    "profile_key": profile_key,
                                    "grade": grade,
                                    "subject": subj,
                                    "workbook": "0/30" if has_wb else "N/A",
                                    "community_service": 0,
                                    "attendance": 0,
                                    "behaviour": 0,
                                    "check_date": datetime.today().strftime("%d/%m/%y"),
                                    "status": "On Progress",
                                })
                            supabase.table("records").insert(records_to_insert).execute()
                            st.sidebar.success(f"Successfully registered {full_name} in {selected_centre}!")
                            st.rerun()
                        except Exception as e:
                            st.sidebar.error(f"Error creating profile: {e}")

    # 2. WITHDRAW PROFILE
    elif action_mode == "Withdraw Student":
        st.sidebar.subheader("Withdraw / Delete Student")
        if not centre_profiles:
            st.sidebar.info("No students registered under this centre yet.")
        else:
            student_names = [p["name"] for p in centre_profiles]
            to_delete = st.sidebar.selectbox("Select Student to Withdraw", student_names)
            if st.sidebar.button("Confirm Withdrawal", type="primary"):
                try:
                    profile_key = f"{to_delete}_{selected_centre}"
                    supabase.table("records").delete().eq("profile_key", profile_key).execute()
                    supabase.table("profiles").delete().eq("profile_key", profile_key).execute()
                    st.sidebar.success(f"Student '{to_delete}' has been successfully withdrawn.")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Error withdrawing student: {e}")

    # --- MAIN VIEW LOGIC ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### 📋 Student Records for {selected_centre}")

    if not centre_profiles:
        st.info("No student profiles found for this centre. Use the sidebar to create a student profile.")
    else:
        student_map = {p["name"]: p for p in centre_profiles}
        selected_student_name = st.selectbox("Select Student Profile", list(student_map.keys()))
        student_info = student_map[selected_student_name]
        records_df = fetch_records_for_student(selected_student_name, selected_centre)

        if records_df.empty:
            st.warning("No assessment records found for this student.")
        else:
            available_grades = sorted(
                records_df["grade"].unique(),
                key=lambda x: int(x.replace("Grade ", "")),
            )

            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**Name:**\n{student_info['name']}")
            with col2:
                st.markdown(f"**Class:**\n{student_info['class']}")
            with col3:
                st.markdown(f"**Centre:**\n{student_info['centre']}")
            with col4:
                st.markdown(f"**Current Grade:**\n{student_info['grade']}")
            st.markdown("---")

            selected_grade_view = st.selectbox("Select Grade Record to View/Edit", available_grades)
            is_current_grade = selected_grade_view == student_info["grade"]

            grade_records = records_df[records_df["grade"] == selected_grade_view].copy()
            display_df = grade_records[
                ["subject", "workbook", "community_service", "attendance", "behaviour", "check_date", "status"]
            ].copy()
            display_df.columns = ["Subject", "Workbook", "Community Service", "Attendance", "Behaviour", "Check Date", "Status"]

            totals = []
            for idx, row in display_df.iterrows():
                wb_val = str(row["Workbook"])
                cs = int(row["Community Service"])
                att = int(row["Attendance"])
                beh = int(row["Behaviour"])

                if wb_val == "N/A":
                    total = cs + att + beh
                    totals.append(f"-{total}/20")
                else:
                    try:
                        wb_num = int(wb_val.split("/")[0].replace("-", ""))
                    except:
                        wb_num = 0
                    total = wb_num + cs + att + beh
                    totals.append(f"-{total}/50")

            display_df["Total (-)"] = totals
            display_df = display_df[
                ["Subject", "Workbook", "Community Service", "Attendance", "Behaviour", "Total (-)", "Check Date", "Status"]
            ]

            if is_current_grade:
                st.markdown(f"#### Active Record — {selected_grade_view}")
                edited_df = st.data_editor(
                    display_df,
                    column_config={
                        "Subject": st.column_config.TextColumn("Subject", disabled=True),
                        "Workbook": st.column_config.TextColumn("Workbook (-) [Format: X/30 or N/A]"),
                        "Community Service": st.column_config.NumberColumn("Community Service", min_value=0, max_value=10, step=1),
                        "Attendance": st.column_config.NumberColumn("Attendance", min_value=0, max_value=5, step=1),
                        "Behaviour": st.column_config.NumberColumn("Behaviour", min_value=0, max_value=5, step=1),
                        "Total (-)": st.column_config.TextColumn("Total (-)", disabled=True),
                        "Check Date": st.column_config.TextColumn("Check Date", disabled=True),
                        "Status": st.column_config.SelectboxColumn("Status", options=["On Progress", "Completed"], required=True),
                    },
                    use_container_width=True,
                    hide_index=True,
                    key=f"active_editor_{selected_student_name}_{selected_grade_view}",
                )

                if not edited_df.equals(display_df):
                    try:
                        for i, row in edited_df.iterrows():
                            orig_row = display_df.loc[i]
                            if (
                                row["Workbook"] != orig_row["Workbook"]
                                or row["Community Service"] != orig_row["Community Service"]
                                or row["Attendance"] != orig_row["Attendance"]
                                or row["Behaviour"] != orig_row["Behaviour"]
                                or row["Status"] != orig_row["Status"]
                            ):
                                new_date = datetime.today().strftime("%d/%m/%y")
                            else:
                                new_date = orig_row["Check Date"]

                            supabase.table("records").update({
                                "workbook": row["Workbook"],
                                "community_service": int(row["Community Service"]),
                                "attendance": int(row["Attendance"]),
                                "behaviour": int(row["Behaviour"]),
                                "check_date": new_date,
                                "status": row["Status"],
                            }).eq("profile_key", f"{selected_student_name}_{selected_centre}").eq("grade", selected_grade_view).eq("subject", row["Subject"]).execute()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating record: {e}")
            else:
                st.markdown(f"#### Historical Record (Locked) — {selected_grade_view}")
                st.dataframe(display_df, use_container_width=True, hide_index=True)

            # --- UPGRADE STUDENT GRADE SECTION ---
            if is_current_grade:
                st.markdown("---")
                st.markdown("### 🚀 Student Grade Upgrade")
                current_grade_num = int(student_info["grade"].replace("Grade ", ""))

                if current_grade_num < 8:
                    next_grade = f"Grade {current_grade_num + 1}"
                    st.write(f"Ready to upgrade **{selected_student_name}** from **{student_info['grade']}** to **{next_grade}**?")
                    confirm_upgrade = st.checkbox(f"I confirm that {selected_student_name} is upgrading to {next_grade}")

                    if st.button("Upgrade Student Grade", type="primary"):
                        if confirm_upgrade:
                            try:
                                profile_key = f"{selected_student_name}_{selected_centre}"
                                supabase.table("profiles").update({"grade": next_grade}).eq("profile_key", profile_key).execute()

                                subj_config = get_subjects_and_na(next_grade)
                                new_records = []
                                for subj, has_wb in subj_config:
                                    new_records.append({
                                        "profile_key": profile_key,
                                        "grade": next_grade,
                                        "subject": subj,
                                        "workbook": "0/30" if has_wb else "N/A",
                                        "community_service": 0,
                                        "attendance": 0,
                                        "behaviour": 0,
                                        "check_date": datetime.today().strftime("%d/%m/%y"),
                                        "status": "On Progress",
                                    })
                                supabase.table("records").insert(new_records).execute()
                                st.success(f"{selected_student_name} successfully upgraded to {next_grade}!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error during upgrade: {e}")
                        else:
                            st.warning("Please check the confirmation box above before clicking upgrade.")
                else:
                    st.info("Student has already reached the maximum grade level (Grade 8).")

# --- FOOTER ---
vok_img_tag = f'<img src="data:image/png;base64,{vok_b64}" alt="VOK Banner" style="width: 140px; border-radius: 4px;">' if vok_b64 else '<div style="font-size:12px; color:#888;">We Love We Care</div>'

st.markdown(
    f"""
    <hr class="footer-divider">
    <div class="footer-container">
        Contact: <b>Angels Bud Academy Management</b><br>
        Email: <b>care@angelsbud.com</b>, <b>abcareline@gmail.com</b>
        <div class="powered-by-text">POWERED BY</div>
        {vok_img_tag}
    </div>
    """,
    unsafe_allow_html=True
)
