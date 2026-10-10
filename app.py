from pathlib import Path
from io import BytesIO
from textwrap import dedent

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Cricket Player Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROOT = Path(__file__).resolve().parent

EXCEL_NAME = "Player_Stats_PowerBI_Ready(1).xlsx"


# =====================================================
# HTML HELPER
# HTML ko code ki tarah dikhne se bachane ke liye
# textwrap.dedent() use kiya gaya hai.
# =====================================================

def render_html(content):
    st.markdown(
        dedent(content).strip(),
        unsafe_allow_html=True
    )


# =====================================================
# PLAYER PHOTO SETTINGS
# =====================================================

PLAYER_WIKI = {
    "Virat Kohli": "Virat_Kohli",
    "Rohit Sharma": "Rohit_Sharma",
    "MS Dhoni": "Mahendra_Singh_Dhoni"
}


@st.cache_data(ttl=86400, show_spinner=False)
def get_player_photo(player_name):

    wiki_name = PLAYER_WIKI.get(player_name)

    if not wiki_name:
        return None

    try:
        url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + wiki_name
        )

        response = requests.get(
            url,
            headers={
                "User-Agent": "CricketPlayerAnalytics/1.0"
            },
            timeout=8
        )

        response.raise_for_status()

        result = response.json()

        return result.get(
            "thumbnail", {}
        ).get("source")

    except Exception:
        return None


# =====================================================
# LOAD EXCEL DATA
# Excel file app.py ke same folder mein hogi.
# =====================================================

@st.cache_data
def load_data():

    possible_files = [
        ROOT / EXCEL_NAME,
        ROOT / "Player_Stats_PowerBI_Ready.xlsx",
        ROOT / "data" / EXCEL_NAME,
        ROOT / "data" / "Player_Stats_PowerBI_Ready.xlsx"
    ]

    excel_path = next(
        (
            path for path in possible_files
            if path.is_file()
        ),
        None
    )

    # Agar exact naam na mile toh root folder mein
    # doosri Excel files bhi search karein.

    if excel_path is None:

        excel_files = [
            path for path in ROOT.glob("*.xlsx")
            if not path.name.startswith("~$")
        ]

        if excel_files:
            excel_path = excel_files[0]

    if excel_path is None:

        raise FileNotFoundError(
            f"Excel file nahi mili: {EXCEL_NAME}\n"
            "Excel file ko app.py ke same folder mein rakhein."
        )

    workbook = pd.ExcelFile(excel_path)

    if "Player_Stats_Long" in workbook.sheet_names:
        sheet_name = "Player_Stats_Long"
    else:
        sheet_name = workbook.sheet_names[0]

    data = pd.read_excel(
        excel_path,
        sheet_name=sheet_name
    )

    data.columns = (
        data.columns.astype(str).str.strip()
    )

    required_columns = [
        "Player Name",
        "Format",
        "Year",
        "Innings",
        "Runs",
        "Balls",
        "Outs",
        "Avg",
        "SR",
        "HS",
        "50s",
        "100s",
        "4s",
        "6s",
        "Dot %"
    ]

    missing = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing:

        raise ValueError(
            "Excel mein ye columns missing hain: "
            + ", ".join(missing)
        )

    for column in required_columns:

        if column not in ["Player Name", "Format"]:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    data["Player Name"] = (
        data["Player Name"]
        .astype("string")
        .str.strip()
    )

    data["Format"] = (
        data["Format"]
        .astype("string")
        .str.strip()
    )

    data = data.dropna(
        subset=["Player Name", "Format", "Year"]
    ).copy()

    data = data[
        (data["Player Name"] != "")
        & (data["Format"] != "")
    ].copy()

    data["Year"] = data["Year"].astype(int)

    data = data.sort_values(
        ["Year", "Player Name", "Format"]
    ).reset_index(drop=True)

    return data, excel_path.name, sheet_name


try:

    df, excel_file, sheet_name = load_data()

except Exception as error:

    st.error("Excel data load nahi ho paya.")

    st.code(str(error))

    st.info(
        "Excel filename, worksheet aur column names check karein."
    )

    st.stop()


# =====================================================
# CUSTOM DESIGN
# =====================================================

render_html("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.hero {
    background: linear-gradient(
        120deg,
        #102a43,
        #145374,
        #159a8c
    );
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 18px;
    color: white;
}

.hero h1 {
    color: white;
    font-size: 36px;
    margin: 0;
}

.hero p {
    color: white;
    font-size: 16px;
    margin-top: 10px;
}

div[data-testid="stMetric"] {
    background: rgba(49, 130, 206, 0.08);
    padding: 14px;
    border-radius: 14px;
    border: 1px solid rgba(49, 130, 206, 0.18);
}

.mascot-card {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 22px;
    margin: 18px 0;
    border-radius: 18px;
    background: linear-gradient(
        120deg,
        #e0f2fe,
        #ecfdf5
    );
    border: 1px solid #bae6fd;
    color: #102a43;
}

.mascot {
    font-size: 68px;
    animation: cricketbounce 1.4s infinite ease-in-out;
}

@keyframes cricketbounce {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-12px);
    }
}

.mascot-title {
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 8px;
}

.mascot-description {
    font-size: 16px;
    line-height: 1.8;
}
</style>
""")

render_html("""
<div class="hero">
    <h1>🏏 Cricket Player Analytics</h1>
    <p>
        Player Photos | Animated Cricket Buddy |
        Performance Analysis | Animated Charts
    </p>
</div>
""")

st.caption(
    f"📁 Excel: {excel_file} | "
    f"Sheet: {sheet_name} | "
    f"Records: {len(df)}"
)


# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.title("🎛️ Dashboard Filters")

formats = sorted(
    df["Format"].dropna().unique().tolist()
)

selected_formats = st.sidebar.multiselect(
    "Select Match Format",
    formats,
    default=formats
)

format_data = df[
    df["Format"].isin(selected_formats)
].copy()

players = sorted(
    format_data["Player Name"].dropna().unique().tolist()
)

selected_players = st.sidebar.multiselect(
    "Select Players",
    players,
    default=players
)

filtered = format_data[
    format_data["Player Name"].isin(selected_players)
].copy()

if filtered.empty:

    st.warning(
        "Sidebar mein kam se kam ek format aur player select karein."
    )

    st.stop()


min_year = int(filtered["Year"].min())
max_year = int(filtered["Year"].max())

if min_year < max_year:

    start_year, end_year = st.sidebar.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

else:

    start_year = min_year
    end_year = max_year

    st.sidebar.info(f"Available year: {min_year}")


view = filtered[
    filtered["Year"].between(start_year, end_year)
].copy()

if view.empty:

    st.warning("Selected years mein data nahi hai.")

    st.stop()


# =====================================================
# OVERALL SUMMARY
# =====================================================

total_runs = int(
    view["Runs"].fillna(0).sum()
)

total_innings = int(
    view["Innings"].fillna(0).sum()
)

total_fifties = int(
    view["50s"].fillna(0).sum()
)

total_hundreds = int(
    view["100s"].fillna(0).sum()
)

total_players = view["Player Name"].nunique()

sr_values = view["SR"].dropna()

avg_sr = (
    sr_values.mean()
    if not sr_values.empty
    else None
)

st.subheader("📌 Overall Performance")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("🏏 Total Runs", f"{total_runs:,}")
c2.metric("🎯 Innings", f"{total_innings:,}")
c3.metric("💯 Centuries", f"{total_hundreds:,}")
c4.metric("🔥 Half-centuries", f"{total_fifties:,}")
c5.metric("👥 Players", str(total_players))

if avg_sr is not None:
    st.metric("Average Recorded Strike Rate", f"{avg_sr:.2f}")


# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "👤 Player Profile",
    "🎞️ Animated Charts",
    "📋 Data & Download"
])


# =====================================================
# TAB 1: OVERVIEW
# =====================================================

with tab1:

    st.subheader("📊 Player Performance Overview")

    left, right = st.columns(2)

    with left:

        player_runs = (
            view.groupby("Player Name", as_index=False)
            ["Runs"]
            .sum()
            .sort_values("Runs", ascending=False)
        )

        fig = px.bar(
            player_runs,
            x="Player Name",
            y="Runs",
            color="Player Name",
            text="Runs",
            title="🏏 Player-wise Total Runs",
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

    with right:

        yearly_runs = (
            view.groupby(
                ["Year", "Player Name"],
                as_index=False
            )["Runs"].sum()
        )

        fig = px.line(
            yearly_runs,
            x="Year",
            y="Runs",
            color="Player Name",
            markers=True,
            title="📈 Year-wise Runs Trend"
        )

        fig.update_layout(hovermode="x unified")

        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:

        format_runs = (
            view.groupby("Format", as_index=False)
            ["Runs"].sum()
        )

        fig = px.pie(
            format_runs,
            names="Format",
            values="Runs",
            hole=0.45,
            title="🏆 Runs by Format"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        milestones = (
            view.groupby("Player Name", as_index=False)
            .agg(
                Fifties=("50s", "sum"),
                Centuries=("100s", "sum")
            )
        )

        fig = go.Figure()

        fig.add_bar(
            name="Half-centuries",
            x=milestones["Player Name"],
            y=milestones["Fifties"]
        )

        fig.add_bar(
            name="Centuries",
            x=milestones["Player Name"],
            y=milestones["Centuries"]
        )

        fig.update_layout(
            title="💯 Half-centuries vs Centuries",
            barmode="group"
        )

        st.plotly_chart(fig, use_container_width=True)


# =====================================================
# TAB 2: PLAYER PHOTO + ANALYSIS BUDDY
# =====================================================

with tab2:

    st.subheader("👤 Player Profile")

    player_list = sorted(
        view["Player Name"].unique().tolist()
    )

    chosen_player = st.selectbox(
        "Select a Player",
        player_list
    )

    player_data = view[
        view["Player Name"] == chosen_player
    ].copy()

    photo_col, info_col = st.columns([1, 2])

    with photo_col:

        photo_url = get_player_photo(chosen_player)

        if photo_url:

            st.image(
                photo_url,
                caption=chosen_player,
                use_container_width=True
            )

        else:

            st.markdown(
                f"### 🏏 {chosen_player}"
            )

            st.info(
                "Online photo nahi mili. Neeche photo upload kar sakte hain."
            )

        uploaded_photo = st.file_uploader(
            "Upload Player Photo",
            type=["jpg", "jpeg", "png"],
            key=f"photo_{chosen_player}"
        )

        if uploaded_photo is not None:

            st.image(
                uploaded_photo,
                caption=f"{chosen_player} - Uploaded Photo",
                use_container_width=True
            )

    total_player_runs = int(
        player_data["Runs"].fillna(0).sum()
    )

    total_player_fifties = int(
        player_data["50s"].fillna(0).sum()
    )

    total_player_hundreds = int(
        player_data["100s"].fillna(0).sum()
    )

    highest_score = player_data["HS"].max()

    avg_values = player_data["Avg"].dropna()
    player_sr = player_data["SR"].dropna()

    with info_col:

        st.markdown(f"## 🏏 {chosen_player}")

        a, b = st.columns(2)

        a.metric("Total Runs", f"{total_player_runs:,}")

        b.metric(
            "Highest Score",
            f"{highest_score:g}"
            if pd.notna(highest_score)
            else "N/A"
        )

        a, b = st.columns(2)

        a.metric(
            "Recorded Batting Average",
            f"{avg_values.mean():.2f}"
            if not avg_values.empty
            else "N/A"
        )

        b.metric(
            "Recorded Strike Rate",
            f"{player_sr.mean():.2f}"
            if not player_sr.empty
            else "N/A"
        )

        st.write(
            f"💯 Centuries: {total_player_hundreds} | "
            f"🔥 Half-centuries: {total_player_fifties}"
        )

    # Player-wise yearly analysis

    player_yearly = (
        player_data.groupby("Year", as_index=False)
        .agg(
            Runs=("Runs", "sum"),
            Innings=("Innings", "sum"),
            Fifties=("50s", "sum"),
            Centuries=("100s", "sum")
        )
    )

    if not player_yearly.empty:

        fig = px.area(
            player_yearly,
            x="Year",
            y="Runs",
            markers=True,
            title=f"📈 {chosen_player}: Year-wise Runs"
        )

        st.plotly_chart(fig, use_container_width=True)

        best_row = player_yearly.loc[
            player_yearly["Runs"].idxmax()
        ]

        best_year = int(best_row["Year"])
        best_runs = int(best_row["Runs"])

        # Hindi analysis text

        description = (
            f"Selected data ke hisaab se {chosen_player} ne "
            f"{total_player_runs:,} runs banaye. "
            f"Sabse zyada runs wala saal {best_year} raha, "
            f"jisme {best_runs:,} runs bane. "
            f"Is selection mein {total_player_hundreds} centuries "
            f"aur {total_player_fifties} half-centuries hain."
        )

        # Cricket Analysis Buddy

        render_html(f"""
        <div class="mascot-card">
            <div class="mascot">🧑🏻‍💻🏏</div>
            <div>
                <div class="mascot-title">
                    🤖 Cricket Analysis Buddy
                </div>
                <div class="mascot-description">
                    <b>{chosen_player} ki performance:</b><br>
                    {description}
                </div>
            </div>
        </div>
        """)

    st.subheader("🏆 Format-wise Performance")

    breakdown = (
        player_data.groupby("Format", as_index=False)
        .agg(
            Runs=("Runs", "sum"),
            Innings=("Innings", "sum"),
            Fifties=("50s", "sum"),
            Centuries=("100s", "sum"),
            Fours=("4s", "sum"),
            Sixes=("6s", "sum")
        )
    )

    st.dataframe(
        breakdown,
        use_container_width=True,
        hide_index=True
    )


# =====================================================
# TAB 3: ANIMATED CHARTS
# =====================================================

with tab3:

    st.subheader("🎞️ Animated Year-wise Runs Race")

    st.write(
        "Play button ka use karke year-wise player comparison dekhein."
    )

    animated = (
        view.groupby(
            ["Year", "Player Name"],
            as_index=False
        )["Runs"].sum()
    )

    years = sorted(animated["Year"].unique().tolist())

    names = sorted(
        animated["Player Name"].unique().tolist()
    )

    if len(years) >= 2:

        grid = pd.MultiIndex.from_product(
            [years, names],
            names=["Year", "Player Name"]
        ).to_frame(index=False)

        animated = grid.merge(
            animated,
            on=["Year", "Player Name"],
            how="left"
        )

        animated["Runs"] = animated["Runs"].fillna(0)

        max_runs = max(
            1,
            float(animated["Runs"].max()) * 1.2
        )

        fig = px.bar(
            animated,
            x="Player Name",
            y="Runs",
            color="Player Name",
            animation_frame="Year",
            animation_group="Player Name",
            range_y=[0, max_runs],
            title="🏏 Animated Player Runs by Year"
        )

        fig.update_layout(showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

    else:

        st.info(
            "Animation ke liye kam se kam 2 years select karein."
        )

    st.subheader("⚡ Animated Runs vs Strike Rate")

    scatter = view.dropna(
        subset=["Runs", "SR"]
    ).copy()

    if scatter["Year"].nunique() >= 2:

        scatter["Innings"] = (
            scatter["Innings"].fillna(1).clip(lower=1)
        )

        fig = px.scatter(
            scatter,
            x="SR",
            y="Runs",
            size="Innings",
            color="Player Name",
            animation_frame="Year",
            hover_name="Player Name",
            hover_data=["Format", "HS", "50s", "100s"],
            title="📈 Runs vs Strike Rate"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:

        st.info(
            "Is chart ke liye multiple years ka data chahiye."
        )


# =====================================================
# TAB 4: DATA TABLE + DOWNLOAD
# =====================================================

with tab4:

    st.subheader("📋 Cricket Player Statistics")

    columns = [
        "Player Name",
        "Format",
        "Year",
        "Innings",
        "Runs",
        "Balls",
        "Outs",
        "Avg",
        "SR",
        "HS",
        "50s",
        "100s",
        "4s",
        "6s",
        "Dot %"
    ]

    st.dataframe(
        view[columns],
        use_container_width=True,
        hide_index=True
    )

    csv_data = view[columns].to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "⬇️ Download CSV",
        data=csv_data,
        file_name="cricket_player_stats.csv",
        mime="text/csv"
    )

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        view[columns].to_excel(
            writer,
            index=False,
            sheet_name="Player Stats"
        )

    st.download_button(
        "⬇️ Download Excel",
        data=excel_buffer.getvalue(),
        file_name="cricket_player_stats.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()

render_html("""
<div style="text-align:center; padding:15px;">
    <h3>🏏 Cricket Player Analytics Dashboard</h3>
    <p>Built with Python, Streamlit, Pandas and Plotly</p>
    <p>Player Statistics | Animated Charts | Hindi Insights</p>
</div>
""")

with st.expander("ℹ️ About Dashboard"):

    st.write(
        "Dashboard Excel ke Player_Stats_Long worksheet se "
        "data read karta hai. Player photo online Wikipedia "
        "thumbnail se load karne ki koshish hoti hai. "
        "Online photo unavailable ho toh local image upload "
        "kar sakte hain. Cricket Analysis Buddy selected data "
        "ke basis par Hindi mein performance description deta hai."
    )