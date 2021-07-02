import streamlit as st
import glob
import os
import cv2
from PIL import Image
import pandas as pd
from dataframeOptimizer import reduce_mem_usage

from math import log
import SessionState

# from videoplayer import play_videoFile

from bokeh.models import ColumnDataSource, CustomJS
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.palettes import Spectral6

import cv2


@st.cache
def load_data(file_name: str) -> pd.DataFrame:
    df = pd.read_csv(file_name, error_bad_lines=False)
    df["y"] = df["y"].apply(lambda y: abs(1080 - y))
    df["frame"] = df["frame"].astype("int64")
    df["global_id"] = df["object_id"].astype(str) + "_" + df["object_class"]
    # return reduce_mem_usage(df)
    to_drop = df["object_id"].value_counts()
    to_drop = list(to_drop[to_drop < 6 * 24].keys())
    df = df.query(f"object_id not in {to_drop}")
    df = df.sort_values("object_id").drop_duplicates(subset=["x", "y"], keep="last")
    df[["x", "y", "w", "h"]] = df[["x", "y", "w", "h"]].astype("int32")
    return df


@st.cache(allow_output_mutation=True)
def select_section(start: int, end: int, fps: int, classes: list) -> pd.DataFrame:
    return df.query(
        f"(frame>= {start*fps} and frame<={end*fps} and object_class in {classes})"
    )


# fig.show()

# st.title("CCTV Analysis")
st.markdown(
    "<h1 style='text-align: center;'>CCTV Analysis</h1>", unsafe_allow_html=True,
)

csv_names = [os.path.basename(x).split(".")[0] for x in glob.glob("processed/*.csv")]
csvs = glob.glob("processed/*.csv")


choice_csvs = st.sidebar.selectbox("Select proccessed datat:", csvs)
uploaded_file = st.sidebar.file_uploader("Choose a file...", type=["csv"])

video_names = [os.path.basename(x).split(".")[0] for x in glob.glob("cams/*.mp4")]
videos = glob.glob("cams/*.mp4")
choice_video = st.sidebar.selectbox("Select Video:", videos)

FRAME_WINDOW = st.image([])
camera = cv2.VideoCapture(choice_video)
preview = st.checkbox(f"Preview Video: {choice_video}")
while preview:
    _, frame = camera.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(frame)

if st.button(f"Run video externally: {choice_video}"):
    os.system(f"vlc {choice_video}")


st.subheader(f"Running results for file {choice_csvs}")

df = load_data(choice_csvs)
counts = df["object_class"].value_counts()

# default_alphas = counts.apply(lambda x: 2 / log(x)).to_dict()

# if st.checkbox("Show Dataset"):
with st.beta_expander("Show Dataset"):
    st.write("### Enter the number of rows to view")
    rows = st.number_input("", min_value=0, value=5)
    if rows > 0:
        st.dataframe(df.head(rows))

# Select columns to display
# if st.checkbox("Show dataset with selected columns"):
with st.beta_expander("Show dataset with selected columns"):
    # get the list of columns
    columns = df.columns.tolist()
    st.write("#### Select the columns to display:")
    selected_cols = st.multiselect("", columns)
    if len(selected_cols) > 0:
        selected_df = df[selected_cols]
        st.dataframe(selected_df)

df_stats = df.describe()
min_frame = int(df_stats["frame"]["min"])
max_frame = int(df_stats["frame"]["max"])
fps = 24

object_classes = df["object_class"].value_counts().to_dict()

# if st.checkbox("Show Dataset statistics"):
with st.beta_expander("Show Dataset statistics"):
    st.subheader("Dataset statistics")
    st.dataframe(df_stats)


session_state = SessionState.get(user_name="", source=None, df_selected=None, plot=None)

with st.form("get section form"):
    st.write("Analyse period")
    start_period = st.number_input(
        "Start period (seconds)", min_value=0, max_value=int(max_frame / fps), value=0
    )

    end_period = st.number_input(
        "End period (seconds)", max_value=int(max_frame / fps), value=100,
    )

    objects_to_display = st.multiselect(
        "Chose objects to display",
        list(object_classes.keys()),
        list(object_classes.keys()),
    )

    submitted = st.form_submit_button("Submit")
    if submitted:

        if start_period <= end_period:

            with st.spinner("Analysing ...."):

                session_state.df_section = select_section(
                    start_period, end_period, fps, objects_to_display
                )

                with st.beta_expander(label="Selected data stats", expanded=False):

                    sub_selected_df = (
                        session_state.df_section.groupby(["object_class", "object_id"])
                        .count()
                        .reset_index()
                    )
                    st.write(sub_selected_df["object_class"].value_counts())
        else:
            st.error("start_period must be smaller than end_period")

try:
    source = ColumnDataSource(session_state.df_section)
    plot = figure(
        output_backend="webgl",
        sizing_mode="stretch_both",
        tools="box_select,lasso_select,pan,wheel_zoom,save,reset",
    )
    factors = list(object_classes.keys())

    plot.circle_dot(
        x="x",
        y="y",
        legend_label="object_class",
        source=source,
        alpha=0.1,
        color=factor_cmap("object_class", palette=Spectral6, factors=factors),
    )

    plot.vbar(
        width=0.9,
        legend_field="object_class",
        source=source,
        fill_color=factor_cmap("object_class", palette=Spectral6, factors=factors),
    )

    source.selected.js_on_change(
        "indices",
        CustomJS(
            args=dict(source=source),
            code="""
                            document.dispatchEvent(
                                new CustomEvent("TestSelectEvent", {detail: {indices: cb_obj.indices}})
                            )
                        """,
        ),
    )
    event_result = streamlit_bokeh_events(
        events="TestSelectEvent",
        bokeh_plot=plot,
        key="foo",
        debounce_time=5000,
        refresh_on_update=True,
    )

    # some event was thrown
    if event_result is not None:
        # TestSelectEvent was thrown
        if "TestSelectEvent" in event_result:
            st.subheader("Selected Points' Stat summary")
            indices = event_result["TestSelectEvent"].get("indices", [])
            sub_selected_df = (
                session_state.df_section.iloc[indices]
                .groupby(["object_class", "object_id"])
                .count()
                .reset_index()
            )

            st.write(sub_selected_df["object_class"].value_counts())
except:
    # raise
    pass
