from datetime import datetime
import pandas as pd
import streamlit as st
from supabase import create_client

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Student Assessment Deduction Tracker (Online)", layout="wide"
)

# --- SUPABASE CONNECTION SETUP ---
@st.cache_resource
def init_supabase():
  url = st.secrets["supabase"]["url"]
  key = st.secrets["supabase"]["key"]
  return create_client(url, key)

supabase = init_supabase()

# --- SUBJECT & N/A CONFIGURATIONS ---
def get_subjects_and_na(grade):
  if grade in ["Grade 1", "Grade 2", "Grade 3"]:
    return [
        ("Maths", True),
        ("Language Arts", True),
        ("Science", True),
        ("LA Extensions", False),
        ("Social Studies", False),
    ]
  elif grade in ["Grade 4", "Grade 5"]:
    return [
        ("Maths", True),
        ("Language Arts", True),
        ("Science", True),
        ("LA Extensions", False),
        ("Social Studies", True),
    ]
  elif grade == "Grade 6":
    return [
        ("Math 6", True),
        ("English 6", True),
        ("Life Science", True),
        ("Digital Media Literacy", True),
        ("Environmental Science", True),
        ("Ancient World History", True),
    ]
  elif grade == "Grade 7":
    return [
        ("Math 7", True),
        ("English 7", True),
        ("Earth & Space Science", True),
        ("Learning Strategies", True),
        ("Introduction to Art", True),
        ("World Culture & Geography", True),
    ]
  elif grade == "Grade 8":
    return [
        ("Math 8", True),
        ("English 8", True),
        ("Physical Science", True),
        ("United States History", True),
        ("Introduction to Public Speaking & Communications", True),
    ]
  return []

# --- FETCH DATA FROM SUPABASE ---
def fetch_profiles():
  try:
    response = supabase.table("profiles").select("*").execute()
    profiles_dict = {}
    for row in response.data:
      profiles_dict[row["profile_key"]] = {
          "Name": row["name"],
          "Grade": row["grade"],
          "Class": row["class"],
          "Centre": row["centre"],
      }
    return profiles_dict
  except Exception as e:
    st.error(f"Error fetching profiles from Supabase: {e}")
    return {}

def fetch_records(profile_key):
  try:
    response = (
        supabase.table("records")
        .select("*")
        .eq("profile_key", profile_key)
        .execute()
    )
    if response.data:
      df = pd.DataFrame(response.data)
      df = df.rename(
          columns={
              "subject": "Subject",
              "workbook": "Workbook",
              "community_service": "Community Service",
              "attendance": "Attendance",
              "behaviour": "Behaviour",
              "check_date": "Check Date",
              "status": "Status",
          }
      )
      return df[["Subject", "Workbook", "Community Service", "Attendance", "Behaviour", "Check Date", "Status"]]
  except Exception as e:
    st.error(f"Error fetching records: {e}")
  return pd.DataFrame()

# --- SIDEBAR: PROFILE MANAGEMENT ---
st.sidebar.header("🎓 Student Profile Management")
menu_action = st.sidebar.radio(
    "Actions", ["View / Edit Records", "Create Profile", "Withdraw / Delete Profile"]
)

grades_list = [f"Grade {i}" for i in range(1, 9)]
profiles = fetch_profiles()

# 1. CREATE PROFILE
if menu_action == "Create Profile":
  st.sidebar.subheader("Add New Student Profile")
  with st.sidebar.form("create_profile_form"):
    full_name = st.text_input("Full Name").strip()
    grade = st.selectbox("Grade", grades_list)
    class_name = st.text_input("Class").strip()
    centre = st.text_input("Centre").strip()
    submit_profile = st.form_submit_button("Create Profile")

    if submit_profile:
      if not full_name:
        st.sidebar.error("Please enter the student's full name.")
      else:
        profile_key = f"{full_name}_{grade}"
        if profile_key in profiles:
          st.sidebar.warning(f"Profile for {full_name} in {grade} already exists!")
        else:
          try:
            # Insert profile metadata
            supabase.table("profiles").insert({
                "profile_key": profile_key,
                "name": full_name,
                "grade": grade,
                "class": class_name,
                "centre": centre,
            }).execute()

            # Initialize subject records
            subj_config = get_subjects_and_na(grade)
            records_to_insert = []
            for subj, has_wb in subj_config:
              records_to_insert.append({
                  "profile_key": profile_key,
                  "subject": subj,
                  "workbook": "0/30" if has_wb else "N/A",
                  "community_service": 0,
                  "attendance": 0,
                  "behaviour": 0,
                  "check_date": datetime.today().strftime("%d/%m/%y"),
                  "status": "On Progress",
              })
            supabase.table("records").insert(records_to_insert).execute()
            st.sidebar.success(f"Successfully created profile for {full_name} ({grade})!")
            st.rerun()
          except Exception as e:
            st.sidebar.error(f"Database error during creation: {e}")

# 2. DELETE / WITHDRAW PROFILE
elif menu_action == "Withdraw / Delete Profile":
  st.sidebar.subheader("Remove Student Profile")
  if not profiles:
    st.sidebar.info("No profiles available to delete.")
  else:
    profile_keys = list(profiles.keys())
    selected_to_delete = st.sidebar.selectbox("Select Profile to Withdraw", profile_keys)
    if st.sidebar.button("Delete Profile", type="primary", use_container_width=True):
      try:
        supabase.table("records").delete().eq("profile_key", selected_to_delete).execute()
        supabase.table("profiles").delete().eq("profile_key", selected_to_delete).execute()
        st.sidebar.success(f"Profile '{selected_to_delete}' deleted successfully.")
        st.rerun()
      except Exception as e:
        st.sidebar.error(f"Error deleting profile: {e}")

# --- MAIN DASHBOARD: VIEW & EDIT RECORDS ---
st.title("📋 Student Assessment Deduction Record (Cloud)")

if not profiles:
  st.info("No student profiles found. Please use the sidebar to **Create Profile** first.")
else:
  profile_keys = list(profiles.keys())
  selected_profile_key = st.selectbox(
      "Select Student Profile",
      profile_keys,
      format_func=lambda x: f"{profiles[x]['Name']} — {profiles[x]['Grade']}",
  )

  profile_info = profiles[selected_profile_key]
  df_records = fetch_records(selected_profile_key)

  st.markdown("---")
  col1, col2, col3 = st.columns(3)
  with col1:
    st.markdown(f"**Name:** {profile_info['Name']}")
  with col2:
    st.markdown(f"**Class:** {profile_info['Class']}")
  with col3:
    st.markdown(f"**Centre:** {profile_info['Centre']}")
  st.markdown(f"**Grade Level:** {profile_info['Grade']}")
  st.markdown("---")

  if df_records.empty:
    st.warning("No records found for this profile. Try recreating the profile.")
  else:
    display_df = df_records.copy()
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
    column_order = [
        "Subject",
        "Workbook",
        "Community Service",
        "Attendance",
        "Behaviour",
        "Total (-)",
        "Check Date",
        "Status",
    ]
    display_df = display_df[column_order]

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
        key=f"editor_{selected_profile_key}",
    )

    if not edited_df.equals(display_df):
      try:
        for i, row in edited_df.iterrows():
          if (
              row["Workbook"] != df_records.loc[i, "Workbook"]
              or row["Community Service"] != df_records.loc[i, "Community Service"]
              or row["Attendance"] != df_records.loc[i, "Attendance"]
              or row["Behaviour"] != df_records.loc[i, "Behaviour"]
              or row["Status"] != df_records.loc[i, "Status"]
          ):
            new_date = datetime.today().strftime("%d/%m/%y")
          else:
            new_date = df_records.loc[i, "Check Date"]

          supabase.table("records").update({
              "workbook": row["Workbook"],
              "community_service": int(row["Community Service"]),
              "attendance": int(row["Attendance"]),
              "behaviour": int(row["Behaviour"]),
              "check_date": new_date,
              "status": row["Status"],
          }).eq("profile_key", selected_profile_key).eq("subject", row["Subject"]).execute()

        st.rerun()
      except Exception as e:
        st.error(f"Error updating records: {e}")
