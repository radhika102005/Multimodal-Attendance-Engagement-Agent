import streamlit as st
import requests

st.set_page_config(
    page_title="Multimodal Attendance & Engagement Agent",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Multimodal Attendance & Engagement Agent")
st.write("AI-powered classroom attendance and engagement analysis.")

st.info(
    "This demo connects to the project's existing FastAPI backend. "
    "Video processing uses the original YOLO, FaceNet and head-pose pipeline."
)

API_URL = st.sidebar.text_input(
    "Backend API URL",
    value="http://127.0.0.1:8000"
).rstrip("/")

st.subheader("1. Backend Connection")

if st.button("Check Backend"):
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        response.raise_for_status()
        st.success("Backend connected successfully!")
        st.json(response.json())
    except requests.RequestException as e:
        st.error(f"Backend connection failed: {e}")

st.divider()
st.subheader("2. Upload Classroom Video")

session_id = st.number_input(
    "Session ID",
    min_value=1,
    step=1
)

video = st.file_uploader(
    "Choose a classroom video",
    type=["mp4", "avi", "mov", "mkv", "webm"]
)

if st.button("Upload and Process Video", type="primary"):
    if video is None:
        st.warning("Please upload a video first.")
    else:
        try:
            with st.spinner("Uploading video..."):
                response = requests.post(
                    f"{API_URL}/api/v1/video/upload-and-process",
                    data={"session_id": int(session_id)},
                    files={
                        "file": (
                            video.name,
                            video.getvalue(),
                            video.type
                        )
                    },
                    timeout=120
                )
                response.raise_for_status()
                result = response.json()

            st.session_state["job_id"] = result["job_id"]
            st.success("Video uploaded successfully!")
            st.json(result)

        except requests.RequestException as e:
            st.error(f"Upload failed: {e}")

st.divider()
st.subheader("3. Processing Status")

job_id = st.session_state.get("job_id")

if job_id:
    if st.button("Refresh Processing Status"):
        try:
            response = requests.get(
                f"{API_URL}/api/v1/video/status/{job_id}",
                timeout=15
            )
            response.raise_for_status()
            result = response.json()

            st.write("Status:", result.get("status"))
            st.progress(float(result.get("progress", 0)))
            st.write(result.get("message", ""))

            if result.get("status") == "COMPLETED":
                st.success("Video processing completed!")
                st.json(result.get("result", {}))
            elif result.get("status") == "FAILED":
                st.error(result.get("message", "Processing failed."))

        except requests.RequestException as e:
            st.error(f"Could not fetch status: {e}")
else:
    st.caption("Upload a video to receive a processing job ID.")