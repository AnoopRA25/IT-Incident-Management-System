import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from database import (
    create_table,
    create_incident,
    get_all_incidents,
    get_incident_by_id,
    update_incident
)

from utils import (
    calculate_priority,
    calculate_sla_deadline,
    get_sla_status
)


# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------

st.set_page_config(
    page_title="IT Incident Command Center",
    page_icon="🚨",
    layout="wide"
)


# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------

st.markdown("""
<style>

/* ================================
   MAIN APPLICATION
================================ */

.stApp {
    background: linear-gradient(
        135deg,
        #0b1020 0%,
        #111827 50%,
        #0f172a 100%
    );
}

/* ================================
   MAIN CONTENT
================================ */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* ================================
   MAIN TITLE
================================ */

.main-title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(
        90deg,
        #60a5fa,
        #a78bfa,
        #f472b6
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;

    margin-bottom: 5px;

    transition: 0.3s ease;
}

.main-title:hover {
    transform: scale(1.01);
}

.subtitle {
    color: #94a3b8;
    font-size: 17px;
    margin-bottom: 30px;
}

/* ================================
   SIDEBAR
================================ */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #161b2b,
        #1e293b
    );
    border-right: 1px solid #334155;
}

section[data-testid="stSidebar"] * {
    transition: all 0.25s ease;
}

/* ================================
   SIDEBAR NAVIGATION HOVER
================================ */

section[data-testid="stSidebar"] label {
    border-radius: 10px;
    padding: 7px;
}

section[data-testid="stSidebar"] label:hover {
    background-color: rgba(96, 165, 250, 0.15);
    transform: translateX(5px);
}

/* ================================
   METRIC CARDS
================================ */

div[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        #1e293b,
        #0f172a
    );

    border: 1px solid #334155;

    border-radius: 16px;

    padding: 18px;

    box-shadow:
        0 4px 15px rgba(0, 0, 0, 0.25);

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease,
        border 0.25s ease;
}

div[data-testid="stMetric"]:hover {

    transform: translateY(-6px);

    border: 1px solid #60a5fa;

    box-shadow:
        0 10px 25px rgba(
            96,
            165,
            250,
            0.20
        );
}

/* ================================
   BUTTONS
================================ */

.stButton > button {

    border-radius: 10px;

    border: 1px solid #3b82f6;

    background: linear-gradient(
        135deg,
        #2563eb,
        #7c3aed
    );

    color: white;

    font-weight: 600;

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

.stButton > button:hover {

    transform: translateY(-3px);

    box-shadow:
        0 8px 20px rgba(
            59,
            130,
            246,
            0.4
        );
}

/* ================================
   DATAFRAME
================================ */

div[data-testid="stDataFrame"] {

    border-radius: 12px;

    overflow: hidden;

    border: 1px solid #334155;

    transition: 0.3s ease;
}

div[data-testid="stDataFrame"]:hover {

    box-shadow:
        0 10px 30px rgba(
            0,
            0,
            0,
            0.3
        );
}

/* ================================
   INPUT FIELDS
================================ */

.stTextInput input,
.stTextArea textarea {

    border-radius: 10px !important;

    border: 1px solid #475569 !important;

    transition: all 0.25s ease;
}

.stTextInput input:focus,
.stTextArea textarea:focus {

    border: 1px solid #60a5fa !important;

    box-shadow:
        0 0 0 2px rgba(
            96,
            165,
            250,
            0.2
        ) !important;
}

/* ================================
   SELECT BOX
================================ */

div[data-baseweb="select"] {

    border-radius: 10px;

    transition: 0.25s ease;
}

div[data-baseweb="select"]:hover {

    transform: scale(1.01);
}

/* ================================
   ALERT BOX
================================ */

.alert-card {

    background: linear-gradient(
        135deg,
        rgba(239, 68, 68, 0.12),
        rgba(127, 29, 29, 0.10)
    );

    border-left: 5px solid #ef4444;

    padding: 16px;

    border-radius: 12px;

    margin-bottom: 12px;

    transition: 0.25s ease;
}

.alert-card:hover {

    transform: translateX(6px);

    box-shadow:
        0 8px 20px rgba(
            239,
            68,
            68,
            0.15
        );
}

/* ================================
   STATUS BADGES
================================ */

.status-open {

    color: #f87171;

    font-weight: 700;

    padding: 6px 12px;

    border-radius: 20px;

    background: rgba(
        239,
        68,
        68,
        0.15
    );
}

.status-progress {

    color: #fbbf24;

    font-weight: 700;

    padding: 6px 12px;

    border-radius: 20px;

    background: rgba(
        245,
        158,
        11,
        0.15
    );
}

.status-resolved {

    color: #4ade80;

    font-weight: 700;

    padding: 6px 12px;

    border-radius: 20px;

    background: rgba(
        34,
        197,
        94,
        0.15
    );
}

/* ================================
   DIVIDER
================================ */

hr {

    border-color: #334155;

    margin-top: 25px;

    margin-bottom: 25px;
}

/* ================================
   SMOOTH ANIMATION
================================ */

@keyframes fadeIn {

    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.main .block-container {

    animation:
        fadeIn 0.5s ease-in-out;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# DATABASE INITIALIZATION
# -------------------------------------------------

create_table()


# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.title("🚨 IT Command Center")

st.sidebar.caption(
    "Real-Time Incident Monitoring System"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "➕ Create Incident",
        "📋 Incident Explorer",
        "🔧 Update Incident"
    ]
)

st.sidebar.divider()

st.sidebar.success("● System Online")


# -------------------------------------------------
# HELPER FUNCTION
# -------------------------------------------------

def add_sla_status(df):

    if df.empty:
        return df

    df = df.copy()

    df["sla_status"] = df.apply(
        lambda row: get_sla_status(
            row["sla_deadline"],
            row["status"]
        ),
        axis=1
    )

    return df

def get_sla_countdown(sla_deadline, status):

    if status == "Resolved":
        return "Resolved"

    try:
        deadline = datetime.fromisoformat(str(sla_deadline))
        remaining = deadline - datetime.now()

        if remaining.total_seconds() <= 0:
            return "🚨 SLA Breached"

        total_seconds = int(remaining.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        return f"⏱️ {hours}h {minutes}m remaining"

    except Exception:
        return "Unknown"


def get_incident_age(created_at):

    try:
        created = datetime.fromisoformat(str(created_at))
        age = datetime.now() - created

        total_minutes = int(age.total_seconds() / 60)

        if total_minutes < 60:
            return f"{total_minutes} min"

        hours = total_minutes // 60

        if hours < 24:
            return f"{hours}h"

        days = hours // 24

        return f"{days}d"

    except Exception:
        return "Unknown"


# =================================================
# DASHBOARD
# =================================================

if page == "📊 Dashboard":

    incidents = get_all_incidents()

    st.markdown(
        '<p class="main-title">🚨 IT Incident Command Center</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="subtitle">Real-time monitoring and incident operations dashboard</p>',
        unsafe_allow_html=True
    )
incidents = get_all_incidents()

active_count = 0

if incidents:

    temp_df = pd.DataFrame(incidents)

    active_count = len(
        temp_df[
            temp_df["status"] != "Resolved"
        ]
    )

if active_count == 0:

    st.success(
        "🟢 LIVE SYSTEM STATUS: All systems operational"
    )

else:

    st.warning(
        f"⚡ LIVE SYSTEM STATUS: {active_count} active incident(s) detected"
    )
    

    if not incidents:

        st.info(
            "No incidents available yet. Create your first incident."
        )

    else:

        df = pd.DataFrame(incidents)

        df = add_sla_status(df)

        # ------------------------------
        # METRICS
        # ------------------------------

        total = len(df)

        open_count = len(
            df[df["status"] == "Open"]
        )

        progress_count = len(
            df[df["status"] == "In Progress"]
        )

        critical_count = len(
            df[
                (df["priority"] == "Critical")
                &
                (df["status"] != "Resolved")
            ]
        )

        breached_count = len(
            df[
                df["sla_status"] == "Breached"
            ]
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            "📋 Total Incidents",
            total
        )

        col2.metric(
            "🔴 Open",
            open_count
        )

        col3.metric(
            "🟠 In Progress",
            progress_count
        )

        col4.metric(
            "🚨 Critical",
            critical_count
        )

        col5.metric(
            "⚠️ SLA Breached",
            breached_count
        )

        st.divider()

        # ------------------------------
        # ALERTS
        # ------------------------------

        st.subheader("🚨 Active Alerts")

        critical_incidents = df[
            (df["priority"] == "Critical")
            &
            (df["status"] != "Resolved")
        ]

        breached_incidents = df[
            df["sla_status"] == "Breached"
        ]

        if (
            critical_incidents.empty
            and breached_incidents.empty
        ):

            st.success(
                "✅ No critical or breached incidents detected."
            )

        else:

            for _, incident in critical_incidents.iterrows():

                st.error(
                    f"🚨 CRITICAL INCIDENT: "
                    f"{incident['incident_id']} | "
                    f"{incident['title']}"
                )

            for _, incident in breached_incidents.iterrows():

                if incident["status"] != "Resolved":

                    st.warning(
                        f"⚠️ SLA BREACHED: "
                        f"{incident['incident_id']} | "
                        f"{incident['title']}"
                    )

        st.divider()

        # ------------------------------
        # INTERACTIVE ANALYTICS
        # ------------------------------

        st.subheader("📊 Incident Analytics")

        chart1, chart2 = st.columns(2)

        with chart1:

            priority_data = (
                df["priority"]
                .value_counts()
                .reset_index()
            )

            priority_data.columns = [
                "Priority",
                "Count"
            ]

            fig_priority = px.pie(
                priority_data,
                names="Priority",
                values="Count",
                title="Incidents by Priority",
                hole=0.45
            )

            st.plotly_chart(
                fig_priority,
                use_container_width=True
            )

        with chart2:

            status_data = (
                df["status"]
                .value_counts()
                .reset_index()
            )

            status_data.columns = [
                "Status",
                "Count"
            ]

            fig_status = px.bar(
                status_data,
                x="Status",
                y="Count",
                title="Incidents by Status",
                text="Count"
            )

            st.plotly_chart(
                fig_status,
                use_container_width=True
            )

        # ------------------------------
        # CATEGORY ANALYTICS
        # ------------------------------

        category_data = (
            df["category"]
            .value_counts()
            .reset_index()
        )

        category_data.columns = [
            "Category",
            "Count"
        ]

        fig_category = px.bar(
            category_data,
            x="Category",
            y="Count",
            title="Incidents by Category",
            text="Count"
        )

        st.plotly_chart(
            fig_category,
            use_container_width=True
        )

        st.divider()

        # ------------------------------
# LIVE OPERATIONS PANEL
# ------------------------------

st.divider()

st.subheader("⚡ Live Operations Panel")

if st.button(
    "🔄 Refresh Live Data",
    use_container_width=False
):
    st.rerun()

incidents = get_all_incidents()

if not incidents:

    st.info(
        "No incident data available yet."
    )

else:

    df = pd.DataFrame(incidents)

    df = add_sla_status(df)

    live_df = df.copy()

    live_df["sla_countdown"] = live_df.apply(
        lambda row: get_sla_countdown(
            row["sla_deadline"],
            row["status"]
        ),
        axis=1
    )

    live_df["incident_age"] = live_df.apply(
        lambda row: get_incident_age(
            row["created_at"]
        ),
        axis=1
    )

    active_incidents = live_df[
        live_df["status"] != "Resolved"
    ].copy()

    if active_incidents.empty:

        st.success(
            "🟢 No active incidents. All systems are operating normally."
        )

    else:

        priority_order = {
            "Critical": 1,
            "High": 2,
            "Medium": 3,
            "Low": 4
        }

        active_incidents["priority_order"] = (
            active_incidents["priority"]
            .map(priority_order)
            .fillna(5)
        )

        active_incidents = active_incidents.sort_values(
            "priority_order"
        )

        for _, incident in active_incidents.head(5).iterrows():

            priority = incident["priority"]

            if priority == "Critical":
                icon = "🔴"

            elif priority == "High":
                icon = "🟠"

            elif priority == "Medium":
                icon = "🟡"

            else:
                icon = "🟢"

            with st.container(border=True):

                col1, col2, col3, col4 = st.columns(
                    [3, 2, 2, 2]
                )

                with col1:

                    st.markdown(
                        f"### {icon} {incident['incident_id']}"
                    )

                    st.caption(
                        incident["title"]
                    )

                with col2:

                    st.write(
                        f"**Priority:** {priority}"
                    )

                    st.write(
                        f"**Status:** {incident['status']}"
                    )

                with col3:

                    st.write("**SLA**")

                    st.write(
                        incident["sla_countdown"]
                    )

                with col4:

                    st.write("**Incident Age**")

                    st.write(
                        incident["incident_age"]
                    )

live_df["sla_countdown"] = live_df.apply(
    lambda row: get_sla_countdown(
        row["sla_deadline"],
        row["status"]
    ),
    axis=1
)

live_df["incident_age"] = live_df.apply(
    lambda row: get_incident_age(
        row["created_at"]
    ),
    axis=1
)

active_incidents = live_df[
    live_df["status"] != "Resolved"
].copy()

if active_incidents.empty:

    st.success(
        "🟢 No active incidents. All systems are operating normally."
    )

else:

    priority_order = {
        "Critical": 1,
        "High": 2,
        "Medium": 3,
        "Low": 4
    }

    active_incidents["priority_order"] = (
        active_incidents["priority"]
        .map(priority_order)
        .fillna(5)
    )

    active_incidents = active_incidents.sort_values(
        "priority_order"
    )

    for _, incident in active_incidents.head(5).iterrows():

        priority = incident["priority"]

        if priority == "Critical":
            icon = "🔴"

        elif priority == "High":
            icon = "🟠"

        elif priority == "Medium":
            icon = "🟡"

        else:
            icon = "🟢"

        with st.container(border=True):

            col1, col2, col3, col4 = st.columns(
                [3, 2, 2, 2]
            )

            with col1:

                st.markdown(
                    f"### {icon} {incident['incident_id']}"
                )

                st.caption(
                    incident["title"]
                )

            with col2:

                st.write(
                    f"**Priority:** {priority}"
                )

                st.write(
                    f"**Status:** {incident['status']}"
                )

            with col3:

                st.write("**SLA**")

                st.write(
                    incident["sla_countdown"]
                )

            with col4:

                st.write("**Incident Age**")

                st.write(
                    incident["incident_age"]
                )

        # ------------------------------
        # RECENT INCIDENTS
        # ------------------------------

        st.subheader("📋 Recent Incidents")

        display_columns = [
            "incident_id",
            "title",
            "priority",
            "status",
            "assigned_team",
            "sla_status"
        ]

        st.dataframe(
            df[display_columns].head(10),
            use_container_width=True,
            hide_index=True
        )


# =================================================
# CREATE INCIDENT
# =================================================

if page == "➕ Create Incident":

    st.title("➕ Create New Incident")

    st.caption(
        "Create and automatically prioritize a new IT incident."
    )

    with st.form("create_incident_form"):

        title = st.text_input(
            "Incident Title"
        )

        description = st.text_area(
            "Incident Description"
        )

        category = st.selectbox(
            "Category",
            [
                "Application",
                "Database",
                "Network",
                "Hardware",
                "Software",
                "Security",
                "Other"
            ]
        )

        col1, col2 = st.columns(2)

        with col1:

            impact = st.selectbox(
                "Impact",
                ["Low", "Medium", "High"]
            )

        with col2:

            urgency = st.selectbox(
                "Urgency",
                ["Low", "Medium", "High"]
            )

        assigned_team = st.selectbox(
            "Assigned Team",
            [
                "Application Support",
                "Database Support",
                "Network Support",
                "IT Operations",
                "Security Team"
            ]
        )

        submitted = st.form_submit_button(
            "🚀 Create Incident",
            use_container_width=True
        )

    if submitted:

        if not title.strip():

            st.error(
                "Please enter an incident title."
            )

        else:

            priority = calculate_priority(
                impact,
                urgency
            )

            sla_deadline = calculate_sla_deadline(
                priority
            )

            incident_id = create_incident(
                title,
                description,
                category,
                impact,
                urgency,
                priority,
                assigned_team,
                sla_deadline
            )

            st.success(
                f"🎉 Incident {incident_id} created successfully!"
            )

            col1, col2 = st.columns(2)

            col1.metric(
                "Calculated Priority",
                priority
            )

            col2.metric(
                "SLA Deadline",
                sla_deadline.strftime(
                    "%d-%m-%Y %I:%M %p"
                )
            )


# =================================================
# INCIDENT EXPLORER
# =================================================

elif page == "📋 Incident Explorer":

    st.title("📋 Incident Explorer")

incidents = get_all_incidents()

if not incidents:

    st.info(
        "No incidents available."
    )

else:

    df = pd.DataFrame(incidents)

    df = add_sla_status(df)

    # ==========================================
    # SEARCH AND FILTERS
    # ==========================================

    st.subheader("🔎 Search & Filter Incidents")

    search = st.text_input(
        "Search by Incident ID, Title or Description",
        placeholder="Example: database, login failure, INC0001..."
    )

    col1, col2, col3, col4 = st.columns(4)

    # ------------------------------------------
    # STATUS FILTER
    # ------------------------------------------

    with col1:

        status_filter = st.selectbox(
            "Status",
            [
                "All",
                "Open",
                "In Progress",
                "Resolved"
            ]
        )

    # ------------------------------------------
    # PRIORITY FILTER
    # ------------------------------------------

    with col2:

        priority_filter = st.selectbox(
            "Priority",
            [
                "All",
                "Critical",
                "High",
                "Medium",
                "Low"
            ]
        )

    # ------------------------------------------
    # CATEGORY FILTER
    # ------------------------------------------

    with col3:

        categories = [
            "All"
        ] + sorted(
            df["category"]
            .dropna()
            .unique()
            .tolist()
        )

        category_filter = st.selectbox(
            "Category",
            categories
        )

    # ------------------------------------------
    # ASSIGNED TEAM FILTER
    # ------------------------------------------

    with col4:

        teams = [
            "All"
        ] + sorted(
            df["assigned_team"]
            .dropna()
            .unique()
            .tolist()
        )

        team_filter = st.selectbox(
            "Assigned Team",
            teams
        )

    # ==========================================
    # APPLY FILTERS
    # ==========================================

    filtered_df = df.copy()

    # Search by ID, title or description
    if search:

        search_lower = search.lower()

        filtered_df = filtered_df[
            filtered_df["incident_id"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_lower,
                na=False
            )
            |
            filtered_df["title"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_lower,
                na=False
            )
            |
            filtered_df["description"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_lower,
                na=False
            )
        ]

    # Status filter
    if status_filter != "All":

        filtered_df = filtered_df[
            filtered_df["status"]
            == status_filter
        ]

    # Priority filter
    if priority_filter != "All":

        filtered_df = filtered_df[
            filtered_df["priority"]
            == priority_filter
        ]

    # Category filter
    if category_filter != "All":

        filtered_df = filtered_df[
            filtered_df["category"]
            == category_filter
        ]

    # Assigned Team filter
    if team_filter != "All":

        filtered_df = filtered_df[
            filtered_df["assigned_team"]
            == team_filter
        ]

    # ==========================================
    # RESULT COUNT
    # ==========================================

    st.caption(
        f"Showing {len(filtered_df)} of {len(df)} incident(s)"
    )

    # ==========================================
    # DISPLAY INCIDENTS
    # ==========================================

    display_columns = [
        "incident_id",
        "title",
        "category",
        "priority",
        "status",
        "assigned_team",
        "sla_status"
    ]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

        # ------------------------------
        # INCIDENT DETAILS
        # ------------------------------

    if not filtered_df.empty:

            st.subheader("🔎 Incident Details")

            selected_id = st.selectbox(
                "Select an incident to inspect",
                filtered_df["incident_id"].tolist()
            )

            incident = get_incident_by_id(
                selected_id
            )

            if incident:

                detail_col1, detail_col2 = st.columns(2)

                with detail_col1:

                    st.write(
                        f"**Incident ID:** "
                        f"{incident['incident_id']}"
                    )

                    st.write(
                        f"**Priority:** "
                        f"{incident['priority']}"
                    )

                    st.write(
                        f"**Status:** "
                        f"{incident['status']}"
                    )

                    st.write(
                        f"**Category:** "
                        f"{incident['category']}"
                    )

                with detail_col2:

                    st.write(
                        f"**Assigned Team:** "
                        f"{incident['assigned_team']}"
                    )

                    st.write(
                        f"**Created At:** "
                        f"{incident['created_at']}"
                    )

                    st.write(
                        f"**SLA Deadline:** "
                        f"{incident['sla_deadline']}"
                    )

                st.info(
                    f"**Description:** "
                    f"{incident['description']}"
                )

                if incident["root_cause"]:

                    st.warning(
                        f"**Root Cause:** "
                        f"{incident['root_cause']}"
                    )

                if incident["resolution"]:

                    st.success(
                        f"**Resolution:** "
                        f"{incident['resolution']}"
                    )


# =================================================
# UPDATE INCIDENT
# =================================================

if page == "🔧 Update Incident":

    st.title("🔧 Update / Resolve Incident")

    incidents = get_all_incidents()

    if not incidents:

        st.info(
            "No incidents available to update."
        )

    else:

        incident_ids = [
            incident["incident_id"]
            for incident in incidents
        ]

        selected_id = st.selectbox(
            "Select Incident",
            incident_ids
        )

        incident = get_incident_by_id(
            selected_id
        )

        st.subheader(
            f"{incident['incident_id']} — "
            f"{incident['title']}"
        )

        info_col1, info_col2, info_col3 = st.columns(3)

        info_col1.metric(
            "Priority",
            incident["priority"]
        )

        info_col2.metric(
            "Current Status",
            incident["status"]
        )

        info_col3.metric(
            "Assigned Team",
            incident["assigned_team"]
        )

        with st.form("update_incident_form"):

            status_options = [
                "Open",
                "In Progress",
                "Resolved"
            ]

            status = st.selectbox(
                "Update Status",
                status_options,
                index=status_options.index(
                    incident["status"]
                )
            )

            root_cause = st.text_area(
                "Root Cause Analysis",
                value=incident["root_cause"] or ""
            )

            resolution = st.text_area(
                "Resolution Details",
                value=incident["resolution"] or ""
            )

            submitted = st.form_submit_button(
                "💾 Save Incident Update",
                use_container_width=True
            )

        if submitted:

            update_incident(
                selected_id,
                status,
                root_cause,
                resolution
            )

            st.success(
                f"✅ Incident {selected_id} "
                f"updated successfully!"
            )

            st.rerun()