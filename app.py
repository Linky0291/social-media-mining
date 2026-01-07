import streamlit as st
import whisper
import os
import tempfile
# 把这一行加在 import 下面，手动把 ffmpeg 的路径加进来
# 注意：大部分 choco 安装都在这个位置，如果不在，我再教你找
os.environ["PATH"] += os.pathsep + r"C:\ProgramData\chocolatey\bin"
# --- 页面基础设置 ---
st.set_page_config(page_title="Vibe 转录神器", page_icon="🎙️", layout="centered")

# --- 加载 Whisper 模型 (加了缓存，不用每次都重新加载) ---
@st.cache_resource
def load_model():
    # 这里默认用 base 模型，速度和精度的平衡点
    # 如果觉得慢，改成 "tiny"；如果觉得不准，改成 "small" 或 "medium"
    return whisper.load_model("small")

st.title("🎙️ 语音转文字 Vibe Transcriber")
st.write("上传你的音频，让 AI 帮你写稿。")

# ---上传文件区域 ---
uploaded_file = st.file_uploader("支持 mp3, wav, m4a, mp4 等格式", type=["mp3", "wav", "m4a", "mp4"])

if uploaded_file is not None:
    # 播放一下确认文件没问题
    st.audio(uploaded_file)
    
    if st.button("🚀 开始转录"):
        model = load_model()
        
        with st.spinner("AI 正在疯狂听写中... (根据音频长度，可能需要几分钟)"):
            # 创建临时文件来处理音频
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name

            try:
                # 调用 Whisper 进行转录
                result = model.transcribe(tmp_file_path)
                text = result["text"]
                
                # 显示结果
                st.success("搞定！")
                st.text_area("转录结果：", text, height=300)
                
                # 下载按钮
                st.download_button("💾 下载成 TXT", text, file_name="output.txt")
                
            except Exception as e:
                st.error(f"出错了: {e}")
            finally:
                # 清理垃圾文件
                os.remove(tmp_file_path)