import cv2
import streamlit as st


# def play_videoFile(filePath, mirror=False):
#     cap = cv2.VideoCapture(filePath)
#     cv2.namedWindow("Video Life2Coding", cv2.WINDOW_AUTOSIZE)
#     while True:
#         ret_val, frame = cap.read()
#         if mirror:
#             frame = cv2.flip(frame, 1)
#         cv2.imshow("Video Life2Coding", frame)
#         if cv2.waitKey(1) == 27:
#             break  # esc to quit
#     cv2.destroyAllWindows()

filePath = "cams/cam0.mp4"
st.title("Webcam Live Feed")
run = st.checkbox("Run")
FRAME_WINDOW = st.image([])
camera = cv2.VideoCapture(filePath)

while run:
    _, frame = camera.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(frame)
else:
    st.write("Stopped")


# import cv2
# import streamlit as st

# st.title("Webcam Live Feed")
# run = st.checkbox("Run")
# FRAME_WINDOW = st.image([])
# camera = cv2.VideoCapture(0)

# while run:
#     _, frame = camera.read()
#     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     FRAME_WINDOW.image(frame)
# else:
#     st.write("Stopped")

