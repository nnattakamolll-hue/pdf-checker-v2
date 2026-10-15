import streamlit as st
import pypdf
from google import genai

st.set_page_config(page_title="PDF Verifier", layout="wide")

st.title("🔍 ระบบเปรียบเทียบรายละเอียดสินค้า PDF ด้วย AI")
st.write("อัปโหลดไฟล์ PDF 2 ไฟล์เพื่อเปรียบเทียบข้อมูลสินค้าว่าตรงกันหรือไม่")

# ช่องกรอก API Key ด้านข้าง เพื่อให้ยืดหยุ่นในการใช้งาน
st.sidebar.header("⚙️ ตั้งค่าระบบ")
api_key_input = st.sidebar.text_input("ใส่ Gemini API Key", type="password", value="")

# ถ้าไม่ได้กรอกใน sidebar ให้ไปดึงมาจาก st.secrets
api_key = api_key_input if api_key_input else st.secrets.get("GEMINI_API_KEY", "")

col1, col2 = st.columns(2)

with col1:
    st.subheader("ไฟล์ที่ 1 (ต้นฉบับ)")
    file1 = st.file_uploader("เลือกไฟล์ PDF ที่ 1", type=["pdf"], key="file1")

with col2:
    st.subheader("ไฟล์ที่ 2 (ตรวจสอบ)")
    file2 = st.file_uploader("เลือกไฟล์ PDF ที่ 2", type=["pdf"], key="file2")

if file1 and file2:
    if st.button("🚀 เริ่มเปรียบเทียบรายละเอียด", type="primary"):
        if not api_key:
            st.error("⚠️ กรุณาใส่ API Key ที่แถบด้านซ้าย หรือตั้งค่าใน Secrets ก่อนใช้งาน")
        else:
            with st.spinner("กำลังประมวลผล..."):
                try:
                    reader1 = pypdf.PdfReader(file1)
                    text1 = "".join([page.extract_text() for page in reader1.pages])

                    reader2 = pypdf.PdfReader(file2)
                    text2 = "".join([page.extract_text() for page in reader2.pages])

                    client = genai.Client(api_key=api_key)

                    prompt = f"""
คุณเป็นผู้ตรวจสอบเอกสารสินค้ามืออาชีพ กรุณาเปรียบเทียบข้อมูลในเอกสาร 2 ชุดนี้อย่างละเอียด:
1. ตรวจสอบว่ารายละเอียดสินค้า รหัสรุ่น สเปค และเงื่อนไขต่างๆ ตรงกันหรือไม่
2. จัดทำตารางสรุปจุดที่ตรงกันและจุดที่แตกต่างกันให้ชัดเจน
3. หากมีข้อมูลที่ขัดแย้งกัน ให้แจ้งเตือนทันที

--- เอกสารชุดที่ 1 ---
{text1}

--- เอกสารชุดที่ 2 ---
{text2}
"""

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )

                    st.success("เปรียบเทียบสำเร็จ!")
                    st.markdown("### 📊 ผลการตรวจสอบ:")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.info("💡 กรุณาอัปโหลดไฟล์ PDF ทั้ง 2 ไฟล์เพื่อเริ่มใช้งาน")
