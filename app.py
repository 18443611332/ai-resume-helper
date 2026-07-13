import streamlit as st
from resume_optimizer import optimize_resume

st.set_page_config(
    page_title="AI 简历优化助手 V3",
    page_icon="📝",
    layout="wide"
)

if "job_description" not in st.session_state:
    st.session_state.job_description = ""

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

sample_jobs = {
    "Python 开发": "招聘 Python 开发工程师，要求熟悉 Python、Flask、MySQL，能阅读接口文档，完成基础后端开发，有良好的学习能力和沟通能力。",
    "数据分析": "招聘数据分析师，要求熟悉 Excel、SQL、Python，能进行数据清洗、数据可视化，并输出分析报告。",
    "产品运营": "招聘产品运营专员，要求具备活动策划、数据分析、用户运营能力，沟通表达清晰，能推动项目执行。"
}

sample_resumes = {
    "Python 开发": "我学习过 Python，做过课程项目，了解数据库基础，会写简单的增删改查，也接触过 Flask，能独立完成基础功能开发。",
    "数据分析": "我学习过 Excel 和 Python，做过课程数据分析作业，了解数据清洗、图表制作和基础统计分析。",
    "产品运营": "我参加过校园活动策划，做过社团宣传和用户沟通工作，了解基本的数据整理，执行力较强。"
}

st.title("📝 AI 简历优化助手 V3")
st.write("输入岗位描述和简历内容，AI 会帮你分析匹配度、提取问题、给出建议，并生成优化后的简历。")

with st.sidebar:
    st.header("⚙️ 参数设置")

    job_type = st.selectbox(
        "选择岗位类型",
        ["Python 开发", "数据分析", "产品运营"]
    )

    resume_style = st.selectbox(
        "选择优化风格",
        ["正式专业", "适合校招", "简洁直接"]
    )

    if st.button("一键填入测试样例"):
        st.session_state.job_description = sample_jobs[job_type]
        st.session_state.resume_text = sample_resumes[job_type]

    if st.button("清空输入内容"):
        st.session_state.job_description = ""
        st.session_state.resume_text = ""

    st.markdown("---")
    st.caption("小提示：先用测试样例跑通，再换成你自己的内容。")

col1, col2 = st.columns(2)

with col1:
    job_description = st.text_area(
        "请输入岗位描述：",
        height=260,
        key="job_description",
        placeholder="例如：招聘 Python 开发工程师，要求熟悉 Python、Flask、MySQL..."
    )

with col2:
    resume_text = st.text_area(
        "请输入你的简历内容：",
        height=260,
        key="resume_text",
        placeholder="请把你的简历内容粘贴到这里..."
    )

if st.button("开始分析并优化"):
    if not job_description.strip():
        st.warning("请先输入岗位描述。")
    elif not resume_text.strip():
        st.warning("请先输入简历内容。")
    else:
        with st.spinner("AI 正在分析，请稍等..."):
            try:
                result = optimize_resume(job_description, resume_text, resume_style)

                score = int(result.get("match_score", 0))
                score = max(0, min(score, 100))

                st.success("分析完成！")

                tab1, tab2, tab3 = st.tabs(["总览", "优化后的简历", "原始结果"])

                with tab1:
                    st.subheader("📊 岗位匹配度")
                    st.metric("匹配分数", f"{score} 分")
                    st.progress(score / 100)
                    st.write(result.get("score_reason", "暂无说明"))

                    col_a, col_b = st.columns(2)

                    with col_a:
                        st.subheader("✅ 简历优点")
                        strengths = result.get("strengths", [])
                        if strengths:
                            for item in strengths:
                                st.write(f"- {item}")
                        else:
                            st.write("暂无内容")

                        st.subheader("⚠️ 存在问题")
                        problems = result.get("problems", [])
                        if problems:
                            for item in problems:
                                st.write(f"- {item}")
                        else:
                            st.write("暂无内容")

                    with col_b:
                        st.subheader("💡 修改建议")
                        suggestions = result.get("suggestions", [])
                        if suggestions:
                            for item in suggestions:
                                st.write(f"- {item}")
                        else:
                            st.write("暂无内容")

                        st.subheader("🔍 缺失关键词")
                        missing_keywords = result.get("missing_keywords", [])
                        if missing_keywords:
                            st.write("、".join(missing_keywords))
                        else:
                            st.write("没有明显缺失关键词")

                with tab2:
                    st.subheader("🧾 优化后的简历")
                    optimized_resume = result.get("optimized_resume", "")
                    st.text_area(
                        "优化结果",
                        optimized_resume,
                        height=360
                    )

                    st.download_button(
                        label="下载优化后的简历（txt）",
                        data=optimized_resume,
                        file_name="optimized_resume.txt",
                        mime="text/plain"
                    )

                with tab3:
                    st.subheader("📦 原始结果（调试用）")
                    st.json(result)

            except Exception as e:
                st.error(f"出错了：{e}")