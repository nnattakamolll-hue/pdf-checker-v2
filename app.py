import streamlit as st
import pypdf
import requests
import json

st.set_page_config(page_title="PDF Verifier", layout="wide")

st.title("🔍 ระบบอัปโหลดและตรวจสอบเอกสาร PDF ด้วย AI")
st.write("อัปโหลดไฟล์ PDF 2 ไฟล์เพื่อเปรียบเทียบเนื้อหาและตรวจสอบความถูกต้อง")

col1, col2 = st.columns(2)

with col1:
    st.subheader("ไฟล์ที่ 1 (ต้นฉบับ)")
    file1 = st.file_uploader("เลือกไฟล์ PDF ไฟล์ที่ 1", type=["pdf"], key="file1")

with col2:
    st.subheader("ไฟล์ที่ 2 (เอกสารที่ต้องการตรวจสอบ)")
    file2 = st.file_uploader("เลือกไฟล์ PDF ไฟล์ที่ 2", type=["pdf"], key="file2")

if file1 and file2:
    if st.button("🚀 เริ่มเปรียบเทียบและตรวจสอบข้อมูล", type="primary"):
        with st.spinner("กำลังอ่านและวิเคราะห์เอกสาร..."):
            try:
                reader1 = pypdf.PdfReader(file1)
                text1 = "".join([page.extract_text() for page in reader1.pages])

                reader2 = pypdf.PdfReader(file2)
                text2 = "".join([page.extract_text() for page in reader2.pages])

                api_key = st.secrets.get("GEMINI_API_KEY", "")

                prompt = f"""
คุณเป็นผู้ตรวจสอบเอกสารระดับมืออาชีพ กรุณาเปรียบเทียบข้อมูลในเอกสาร 2 ชุดนี้อย่างละเอียด:
1. สรุปภาพรวมว่าเนื้อหาตรงกัน ขัดแย้ง หรือมีข้อมูลผิดเพี้ยนไปจากเดิมหรือไม่
2. ระบุรายละเอียดจุดที่ตรงกันและจุดที่แตกต่างกันอย่างชัดเจน
3. หากมีข้อมูลตัวเลข ชื่อ หรือเงื่อนไขที่ไม่ตรงกัน ให้แจ้งเตือนทันที

--- เอกสารชุดที่ 1 ---
{text1}

--- เอกสารชุดที่ 2 ---
{text2}
"""

                # เปลี่ยนไปใช้ endpoint แบบ v1alpha เพื่อรองรับ OAuth Token (AQ...) โดยเฉพาะ
                url = "https://generativelanguage.googleapis.com/v1alpha/models/gemini-2.5-flash:generateContent"
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }

                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }

                response = requests.post(url, headers=headers, data=json.dumps(payload))
                res_data = response.json()

                if response.status_code == 200:
                    try:
                        ai_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                        st.success("วิเคราะห์เสร็จเรียบร้อย!")
                        st.markdown("### 📊 ผลการตรวจสอบ:")
                        st.markdown(ai_text)
                    except Exception:
                        st.error(f"รูปแบบข้อมูลตอบกลับไม่ถูกต้อง: {res_data}")
                else:
                    st.error(f"API Error ({response.status_code}): {res_data}")

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {e}")
else:
    st.info("💡 กรุณาอัปโหลดไฟล์ PDF ทั้ง 2 ไฟล์ให้ครบถ้วนเพื่อเริ่มใช้งาน")
