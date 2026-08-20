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
    initial_sidebar_state="collapsed",
)

# --- IMAGE ENCODING HELPER ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

crest_b64 = get_base64_image("assets/angels-bud-crest.png")
vok_b64 = get_base64_image("assets/vok-banner.png")

# --- CUSTOM CSS — brand palette + fonts (Manrope / Lora) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Lora:wght@400;500;600;700&display=swap');

    :root {
        --abc-background: #f7f4ec;
        --abc-card: #ffffff;
        --abc-brand: #033c29;
        --abc-brand-foreground: #f8f6ec;
        --abc-secondary: #f1ebd8;
        --abc-secondary-foreground: #2b4638;
        --abc-accent: #eabf8a;
        --abc-accent-foreground: #033c29;
        --abc-muted-foreground: #6b7280;
        --abc-border: #e5e7eb;
        --abc-destructive: #ef4444;
        --abc-destructive-dark: #b91c1c;
        --abc-success: #1f9d55;
        --abc-success-bg: #e4f6ea;
        --abc-warning: #b7791f;
        --abc-warning-bg: #fbf0d9;
        --abc-radius: 12px;
    }

    * {
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* 1. Global App Background */
    .stApp {
        background-color: var(--abc-background) !important;
    }

    .block-container {
        padding-top: 2rem !important;
        max-width: 850px !important;
    }

    /* 2. Top Dark Green Header Card */
    .main-header-card {
        background-color: var(--abc-brand);
        border-radius: 16px;
        padding: 40px;
        color: var(--abc-brand-foreground);
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
        background-color: var(--abc-accent);
        color: var(--abc-accent-foreground);
        font-family: 'Manrope', sans-serif;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.5px;
        padding: 6px 14px;
        border-radius: 20px;
        text-transform: uppercase;
    }

    .header-title {
        font-family: 'Lora', Georgia, serif !important;
        font-size: 42px;
        font-weight: 700;
        margin: 0 0 5px 0;
        letter-spacing: -0.5px;
    }

    .header-subtitle {
        font-family: 'Lora', Georgia, serif !important;
        font-size: 24px;
        font-weight: 600;
        margin: 0 0 20px 0;
    }

    .header-description {
        font-family: 'Manrope', sans-serif;
        font-size: 14px;
        line-height: 1.5;
        margin: 0;
        max-width: 90%;
        opacity: 0.95;
    }

    /* 3. Streamlit Native Card Overrides */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--abc-card);
        border: 1px solid var(--abc-border);
        border-radius: var(--abc-radius);
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* 4. Headings styling */
    h2, h3 {
        font-family: 'Lora', Georgia, serif !important;
        color: var(--abc-brand) !important;
        font-weight: 700 !important;
    }

    /* 5. Buttons */
    .stButton > button[kind="primary"] {
        background-color: var(--abc-brand) !important;
        color: var(--abc-brand-foreground) !important;
        border-radius: 8px !important;
        height: 42px !important;
        font-weight: 600 !important;
        border: none !important;
    }
    .stButton > button[kind="secondary"] {
        border-radius: 8px !important;
    }

    /* 6. Empty State Card */
    .empty-state {
        border: 1.5px dashed #cbd5e1;
        border-radius: var(--abc-radius);
        padding: 40px 20px;
        text-align: center;
        background-color: #fafafa;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    .empty-icon {
        font-size: 32px;
        color: var(--abc-muted-foreground);
        margin-bottom: 10px;
    }
    .empty-text {
        color: var(--abc-muted-foreground);
        font-size: 14px;
        font-family: 'Manrope', sans-serif;
    }

    /* 7. Student List Card */
    .student-title {
        color: var(--abc-brand);
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 4px;
    }
    .student-subtitle {
        color: var(--abc-muted-foreground);
        font-size: 13px;
        font-family: 'Manrope', sans-serif;
    }

    /* 7b. Clickable student row (whole card opens the profile) */
    .student-row-wrapper {
        position: relative;
    }
    .student-row-wrapper [data-testid="stVerticalBlockBorderWrapper"] {
        transition: box-shadow 0.15s ease, border-color 0.15s ease;
    }
    .student-row-wrapper:hover [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--abc-brand);
        box-shadow: 0 2px 8px rgba(3, 60, 41, 0.12);
    }
    /* Requires Streamlit 1.36+, which exposes a widget's key as class
       "st-key-<key>" on its wrapping div. We stretch the invisible
       "open profile" button (key="sel_...") over the row so the whole
       card is clickable, minus the trash icon which stays on top. */
    [class*="st-key-sel_"] {
        position: absolute !important;
        top: 0;
        left: 0;
        width: 88%;
        height: 100%;
        z-index: 5;
        margin: 0 !important;
    }
    [class*="st-key-sel_"] button {
        width: 100%;
        height: 100%;
        opacity: 0;
        cursor: pointer;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    [class*="st-key-del_"] {
        position: relative;
        z-index: 10;
    }

    /* Trash button styling */
    [data-testid="stButton"] button[aria-label="Delete"],
    [class*="st-key-del_"] button {
        color: var(--abc-destructive) !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    [data-testid="stButton"] button[aria-label="Delete"]:hover,
    [class*="st-key-del_"] button:hover {
        color: var(--abc-destructive-dark) !important;
        background: #fee2e2 !important;
    }

    /* 7c. Status pill badges (used in the read-only grade view) */
    .status-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        font-family: 'Manrope', sans-serif;
    }
    .status-pill.on-progress {
        background-color: var(--abc-warning-bg);
        color: var(--abc-warning);
    }
    .status-pill.completed {
        background-color: var(--abc-success-bg);
        color: var(--abc-success);
    }
    .status-pill.other {
        background-color: #f1f5f9;
        color: #475569;
    }

    /* 8. Help & Footer */
    .help-card {
        background-color: var(--abc-secondary);
        border-radius: var(--abc-radius);
        padding: 30px;
        text-align: center;
        margin-top: 30px;
        margin-bottom: 40px;
    }
    .help-title {
        font-family: 'Lora', Georgia, serif;
        color: var(--abc-brand);
        font-size: 20px;
        font-weight: 700;
        margin: 0 0 10px 0;
    }
    .help-description {
        font-family: 'Manrope', sans-serif;
        color: var(--abc-secondary-foreground);
        font-size: 14px;
        margin: 0;
        line-height: 1.5;
    }

    .footer-divider {
        border: 0;
        border-top: 1px solid var(--abc-border);
        margin: 40px 0 25px 0;
    }
    .footer-container {
        text-align: center;
        font-family: 'Manrope', sans-serif;
        font-size: 13px;
        color: #4b5563;
        line-height: 1.8;
    }
    .powered-by-text {
        font-size: 10px;
        color: #6b7280;
        letter-spacing: 2px;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 5px;
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

# --- CONSTANTS & CONFIGURATIONS ---
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

STATUS_OPTIONS = ["On Progress", "Completed", "Needs Review"]

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

def status_pill_html(status):
    css_class = "other"
    if status == "On Progress":
        css_class = "on-progress"
    elif status == "Completed":
        css_class = "completed"
    return f'<span class="status-pill {css_class}">{status}</span>'

# --- FETCH DATA ---
def fetch_all_profiles():
    try:
        response = supabase.table("profiles").select("*").execute()
        return response.data if response.data else []
    except Exception:
        return []

def fetch_records_for_student(name, centre):
    try:
        response = supabase.table("records").select("*").eq("profile_key", f"{name}_{centre}").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# --- SESSION STATE INITIALIZATION ---
if 'show_create_form' not in st.session_state:
    st.session_state.show_create_form = False
if 'viewing_student' not in st.session_state:
    st.session_state.viewing_student = None

# --- MAIN UI: HEADER BANNER ---
img_tag = f'<img src="data:image/png;base64,{crest_b64}" alt="Crest">' if crest_b64 else ''
st.markdown(
    f"""
    <div class="main-header-card">
        <div class="header-top-row">
            <div class="logo-box">{img_tag}</div>
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
        <h2 style="margin: 5px 0 5px 0; font-size: 24px;">Choose your centre</h2>
        <p style="color: #6b7280; font-size: 14px; margin: 0 0 15px 0;">Student profiles appear once a centre is selected.</p>
        """,
        unsafe_allow_html=True
    )

    col_sel, col_btn = st.columns([0.75, 0.25], vertical_alignment="bottom")
    with col_sel:
        selected_centre = st.selectbox(
            "Centre",
            ["Select your centre"] + CENTRES,
            label_visibility="visible"
        )
    with col_btn:
        if selected_centre != "Select your centre":
            if st.button("👤 Create profile", type="primary", use_container_width=True):
                st.session_state.show_create_form = not st.session_state.show_create_form
                st.session_state.viewing_student = None

# --- CONDITIONAL VIEWS ---
if selected_centre == "Select your centre":
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
    all_profiles = fetch_all_profiles()
    centre_profiles = [p for p in all_profiles if p["centre"] == selected_centre]

    # --- INLINE CREATE STUDENT FORM ---
    if st.session_state.show_create_form:
        with st.container(border=True):
            st.markdown(f"### Register New Student in {selected_centre}")
            max_classes = CENTRE_CLASSES.get(selected_centre, 1)

            with st.form("create_profile_form"):
                f_name = st.text_input("Student Full Name")
                c1, c2 = st.columns(2)
                f_grade = c1.selectbox("Starting Grade", GRADES)
                f_class = c2.selectbox("Class", [f"Class {i}" for i in range(1, max_classes + 1)])

                submitted = st.form_submit_button("Register Student", type="primary")
                if submitted:
                    if not f_name.strip():
                        st.error("Please enter a name.")
                    elif f_name.strip().lower() in [p["name"].lower() for p in centre_profiles]:
                        st.warning("Student already exists!")
                    else:
                        profile_key = f"{f_name.strip()}_{selected_centre}"
                        try:
                            supabase.table("profiles").insert({
                                "profile_key": profile_key,
                                "name": f_name.strip(),
                                "grade": f_grade,
                                "class": f_class,
                                "centre": selected_centre,
                                "status": "On Progress",
                            }).execute()

                            subj_config = get_subjects_and_na(f_grade)
                            records_to_insert = [{
                                "profile_key": profile_key, "grade": f_grade, "subject": subj,
                                "workbook": "0/30" if has_wb else "N/A", "community_service": 0,
                                "attendance": 0, "behaviour": 0,
                                "check_date": datetime.today().strftime("%d/%m/%y"), "status": "On Progress"
                            } for subj, has_wb in subj_config]

                            supabase.table("records").insert(records_to_insert).execute()
                            st.session_state.show_create_form = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    # --- SEARCH BAR ---
    st.markdown("<br>", unsafe_allow_html=True)
    search_query = st.text_input("Search student", placeholder="🔍 Search student name", label_visibility="collapsed")

    filtered_profiles = [p for p in centre_profiles if search_query.lower() in p["name"].lower()]

    # --- LIST / EMPTY STATE ---
    if not filtered_profiles:
        st.markdown(
            f"""
            <div class="empty-state">
                <div class="empty-icon">🎓</div>
                <div class="empty-text">No student profiles in {selected_centre} yet. Create one to start recording deductions.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        for p in filtered_profiles:
            st.markdown('<div class="student-row-wrapper">', unsafe_allow_html=True)
            with st.container(border=True):
                c_text, c_actions = st.columns([0.9, 0.1], vertical_alignment="center")

                with c_text:
                    is_middle = "Middle School" if int(p['grade'].split(' ')[1]) >= 6 else "Primary School"
                    st.markdown(
                        f"""
                        <div class="student-title">{p['name']}</div>
                        <div class="student-subtitle">{p['grade']} · {is_middle} · {p['class']} · {p['centre']}</div>
                        """,
                        unsafe_allow_html=True
                    )

                with c_actions:
                    if st.button("🗑️", key=f"del_{p['profile_key']}", help="Withdraw Student"):
                        try:
                            supabase.table("records").delete().eq("profile_key", p['profile_key']).execute()
                            supabase.table("profiles").delete().eq("profile_key", p['profile_key']).execute()
                            if st.session_state.viewing_student == p['name']:
                                st.session_state.viewing_student = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting: {e}")

                if st.button("Open profile", key=f"sel_{p['profile_key']}"):
                    st.session_state.viewing_student = p['name']
                    st.session_state.show_create_form = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # --- STUDENT DASHBOARD VIEWER ---
    if st.session_state.viewing_student:
        student_info = next((p for p in centre_profiles if p["name"] == st.session_state.viewing_student), None)
        if student_info:
            st.markdown(f"---")
            st.markdown(f"### 📋 Managing: {student_info['name']}")

            records_df = fetch_records_for_student(student_info['name'], selected_centre)

            if not records_df.empty:
                available_grades = sorted(records_df["grade"].unique(), key=lambda x: int(x.replace("Grade ", "")))
                selected_grade_view = st.selectbox("Select Grade Record", available_grades)
                is_current_grade = selected_grade_view == student_info["grade"]

                grade_records = records_df[records_df["grade"] == selected_grade_view].copy()
                display_df = grade_records[["subject", "workbook", "community_service", "attendance", "behaviour", "check_date", "status"]].copy()
                display_df.columns = ["Subject", "Workbook", "Community Service", "Attendance", "Behaviour", "Check Date", "Status"]

                totals = []
                for idx, row in display_df.iterrows():
                    wb_val = str(row["Workbook"])
                    cs = int(row["Community Service"])
                    att = int(row["Attendance"])
                    beh = int(row["Behaviour"])

                    if wb_val == "N/A":
                        totals.append(f"-{cs + att + beh}/20")
                    else:
                        try:
                            wb_num = int(wb_val.split("/")[0].replace("-", ""))
                        except Exception:
                            wb_num = 0
                        totals.append(f"-{wb_num + cs + att + beh}/50")

                display_df["Total (-)"] = totals
                display_df = display_df[["Subject", "Workbook", "Community Service", "Attendance", "Behaviour", "Total (-)", "Check Date", "Status"]]

                if is_current_grade:
                    edited_df = st.data_editor(
                        display_df,
                        column_config={
                            "Subject": st.column_config.TextColumn("Subject", disabled=True),
                            "Total (-)": st.column_config.TextColumn("Total (-)", disabled=True),
                            "Check Date": st.column_config.TextColumn("Check Date", disabled=True),
                            "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS),
                        },
                        use_container_width=True, hide_index=True,
                        key=f"editor_{student_info['profile_key']}_{selected_grade_view}",
                    )

                    if not edited_df.equals(display_df):
                        try:
                            for i, row in edited_df.iterrows():
                                orig_row = display_df.loc[i]
                                if (row["Workbook"] != orig_row["Workbook"] or row["Community Service"] != orig_row["Community Service"] or row["Attendance"] != orig_row["Attendance"] or row["Behaviour"] != orig_row["Behaviour"] or row["Status"] != orig_row["Status"]):
                                    supabase.table("records").update({
                                        "workbook": row["Workbook"], "community_service": int(row["Community Service"]),
                                        "attendance": int(row["Attendance"]), "behaviour": int(row["Behaviour"]),
                                        "check_date": datetime.today().strftime("%d/%m/%y"), "status": row["Status"],
                                    }).eq("profile_key", student_info['profile_key']).eq("grade", selected_grade_view).eq("subject", row["Subject"]).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating: {e}")
                else:
                    # Read-only past grade — render with a styled status pill to match the design system
                    display_only = display_df.drop(columns=["Status"]).copy()
                    st.dataframe(display_only, use_container_width=True, hide_index=True)
                    st.markdown(
                        "".join(
                            f'<div style="display:flex; justify-content:space-between; padding:4px 2px; font-size:13px;">'
                            f'<span>{row["Subject"]}</span>{status_pill_html(row["Status"])}</div>'
                            for _, row in display_df.iterrows()
                        ),
                        unsafe_allow_html=True,
                    )

    # LOWER HELP CARD
    st.markdown(
        """
        <div class="help-card" style="margin-top: 40px;">
            <h3 class="help-title">Need a hand with the next step?</h3>
            <p class="help-description">Choose your centre, open a student profile and record the assessment deduction for the current grade — every previous grade stays saved.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- FOOTER ---
vok_img_tag = f'<img src="data:image/png;base64,{vok_b64}" alt="VOK Banner" style="width: 140px; border-radius: 4px;">' if vok_b64 else '<div style="font-size:12px; color:#888;">We Love We Care</div>'

st.markdown(
    f"""
    <hr class="footer-divider">
    <div class="footer-container">
        Contact: <b>Angels Bud Academy Management</b><br>
        Email: <b style="color: #033c29;">care@angelsbud.com</b>, <b style="color: #033c29;">abcareline@gmail.com</b>
        <div class="powered-by-text">POWERED BY</div>
        {vok_img_tag}
    </div>
    """,
    unsafe_allow_html=True
)
