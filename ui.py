import streamlit as st
import pandas as pd
import plotly.express as px
from importlib import reload

import configs
import prompts

reload(prompts)
from prompts import get_links_prompt, system_message_base, system_message1, system_message2, \
    system_prompt_web_comparison
from tools.tools import *
from configs import default_variables
from llm.llm import *
# Import all the message part classes
from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    UserPromptPart,
)
from auth_middleware import auth_required

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', None)

# Set page configuration
st.set_page_config(page_title="Medication Analysis Dashboard", layout="wide")


def display_message_part(part):
    """
    Display a single part of a message in the Streamlit UI.
    Customize how you display system prompts, user prompts,
    tool calls, tool returns, etc.
    """
    # system-prompt
    if part.part_kind == 'system-prompt':
        with st.chat_message("system"):
            st.markdown(f"**System**: {part.content}")
    # user-prompt
    elif part.part_kind == 'user-prompt':
        with st.chat_message("user"):
            st.markdown(part.content)
    # text
    elif part.part_kind == 'text':
        with st.chat_message("assistant"):
            st.markdown(part.content)


@auth_required
def main():
    # Sidebar Filters
    st.sidebar.header("Filter Medications")

    if 'base_info' not in st.session_state:
        st.session_state.base_info = default_variables.base_info
    if 'list_similar_medications' not in st.session_state:
        st.session_state.list_similar_medications = default_variables.list_similar_medications
    if 'detailed_info_df' not in st.session_state:
        st.session_state.detailed_info_df = get_default_detailed_info(path=default_variables.default_detailed_info_path)
    if 'med_name_input' not in st.session_state:
        st.session_state.med_name_input = default_variables.med_name_input
        st.session_state.med_name_input2 = default_variables.med_name_input
    if 'llm_model_input' not in st.session_state:
        st.session_state.available_models = default_variables.available_llm_models
        st.session_state.llm_model_input = default_variables.llm_model

    st.markdown("""
        <style>
        /* Sidebar button styling */
        .stButton > button {
            width: 100%;
            border: none;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
            background: linear-gradient(to right, #ff7e5f, #feb47b); /* Shiny Gradient */
            color: white;
            box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.3); /* 3D Effect */
            transition: all 0.3s ease-in-out;
        }

        /* Hover Effect */
        .stButton > button:hover {
            background: linear-gradient(to right, #ff7e5f, #7B7CFE);
            transform: translateY(-2px); /* Lifts the button on hover */
            box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.4);
        }

        /* Active Click Effect */
        .stButton > button:active {
            transform: translateY(2px); /* Pressed Effect */
            box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.2);
        }

        /* Improve sidebar spacing */
        .css-1lcbmhc {
            padding: 10px 5px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar Sections
    sections = {
        "🚀 Medication overview. Find similar.": "find_similar_medication",
        "🛠 Medications Comparison": "comparing_webpages",
        "ℹ️ Help Information": 'help_info',
    }

    ### Init LLM model
    llm = LLM_model(model_id=st.session_state.llm_model_input)

    for label, action in sections.items():
        if st.sidebar.button(label):
            st.session_state["action"] = action

    if "action" not in st.session_state:
        st.info("👈 Select an option from the sidebar to proceed.")

    elif st.session_state["action"] == "find_similar_medication":
        med_inputs_form = st.sidebar.form('my_medication')
        med_name_input = med_inputs_form.text_input("Enter Medication Name:", st.session_state.med_name_input)
        llm_model_input = med_inputs_form.selectbox('LLM model:', (st.session_state.available_models), index=0)
        st.session_state.llm_model_input = llm_model_input
        submit_button = med_inputs_form.form_submit_button(label='Submit')

        st.info("👈 Select an option from the sidebar to proceed.")

        # Main Page Title
        st.title("💊 Medication Analysis Dashboard")
        st.divider()

        ### Init LLM model
        llm = LLM_model(model_id=st.session_state.llm_model_input)

        # Button to Execute Calculation
        if submit_button:
            st.session_state.med_name_input = med_name_input
            st.session_state.llm_model_input = llm_model_input
            progress_bar = st.progress(10)
            base_links = get_base_links(llm=llm, medication=st.session_state.med_name_input,
                                        use_llm=True, get_links_prompt=get_links_prompt)
            # base_links = get_base_links_gooole(medication=st.session_state.med_name_input)
            progress_bar.progress(30)
            base_content = get_base_content(base_links=base_links)
            progress_bar.progress(60)
            base_info = generate_base_info(llm=llm, content=base_content, system_message_base=system_message_base)
            progress_bar.progress(100)
            st.session_state.base_info = base_info
            st.session_state.list_similar_medications = base_info['similar_medications']
            st.sidebar.success("Base medication data successfully extracted!")

        # Summary of user reviews for the specified medication
        if (len(st.session_state.base_info) > 0):
            base_info = st.session_state.base_info
            st.subheader(f"Summary for {st.session_state.med_name_input}")
            st.markdown(f"**Medication:** {st.session_state.med_name_input}")
            st.markdown(f"**Description:** {base_info['description']}")
            st.markdown(f"**Active Ingredient:** {base_info['active_ingredient']}")
            st.markdown(f"**Therapeutic Effects:** {base_info['therapeutic_effects']}")
            st.markdown(f"**Side Effects:** {base_info['side_effects']}")
            st.markdown(f"**User Rating:** {base_info['rating']} ⭐")
            st.markdown(f"**Positive Reviews:** {base_info['positive_reviews']} 👍")
            st.markdown(f"**Negative Reviews:** {base_info['negative_reviews']} 👎")
            st.markdown(f"**Reviews Sentiment:** {base_info['sentiment_reviews']} 👎")
            st.markdown(f"**Overdose:** {base_info['overdose']}")
            st.markdown(f"**Storage:** {base_info['storage']}")
            st.markdown(f"**Drug Interactions:** {base_info['drug_interactions']}")

        st.markdown("### Summary")
        if len(base_info) > 0:
            st.write(base_info['summary'])
        st.divider()

        get_similar_button = st.button("Find Similar Drugs")
        if get_similar_button:
            progress_bar = st.progress(10)
            list_similar_medications = st.session_state.list_similar_medications
            detailed_content, list_similar_upd = get_detailed_content(list_similar_medications=list_similar_medications)
            progress_bar.progress(50)
            print('Detailed content extracted!')
            detailed_info_df = generate_detailed_info(llm=llm,
                                                   detailed_content=detailed_content,
                                                   list_similar_upd=list_similar_upd,
                                                   system_message1=system_message1,
                                                   system_message2=system_message2)
            print('Detailed info generated!')
            progress_bar.progress(90)
            st.sidebar.success("Detailed medications data successfully extracted!")
            st.session_state.detailed_info_df = detailed_info_df
            st.session_state.med_name_input2 = med_name_input
            progress_bar.progress(100)

        detailed_info_df = st.session_state.detailed_info_df

        # Display the similar medications table
        st.subheader(f"Similar Medications to: {st.session_state.med_name_input2}")
        st.markdown(f"##### Medications and theirs characteristics:")
        st.dataframe(detailed_info_df[
                         ['Medication', 'description', 'active_ingredient', 'side_effects', 'therapeutic_effect',
                          'overdose', 'storage', 'drug_interactions']], width=None, height=220)
        st.markdown(f"##### User reviews and ratings:")
        st.dataframe(
            detailed_info_df[['Medication', 'summary', 'rating', 'number_reviews', 'sentiment_reviews', 'URL']],
            width=None, height=220)
        st.divider()

        # Charts Section
        st.subheader("Data Insights")

        col1, col2 = st.columns(2)

        # Bar Chart: Distribution of User Ratings
        with col1:
            st.subheader("User Ratings Distribution")
            rating_chart = px.histogram(detailed_info_df, x="rating", nbins=7, color_discrete_sequence=['steelblue'],
                                        title="Rating Distribution")
            st.plotly_chart(rating_chart)

        # Pie Chart: Positive vs. Negative Reviews
        with col2:
            st.subheader("Therapeutic Effects Distribution")
            therapeutic_effect = [x.split(",") if type(x)==str else x for x in detailed_info_df.therapeutic_effect]
            therapeutic_effect = sum(therapeutic_effect, [])
            therapeutic_effect = [x.strip().lower() for x in therapeutic_effect]
            temp = pd.DataFrame(therapeutic_effect, columns=['therapeutic_effect'])
            therapeutic_effect_chart = px.bar(temp, x="therapeutic_effect", color_discrete_sequence=['steelblue'])
            therapeutic_effect_chart.update_xaxes(tickfont_size=13, tickangle=45)
            therapeutic_effect_chart.update_layout(xaxis={'categoryorder': 'total descending'},
                                                   xaxis_title="Therapeutic Effect", yaxis_title='Count')
            st.plotly_chart(therapeutic_effect_chart, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("Side Effects Distribution")
            side_effects = [x.split(",") if type(x)==str else x for x in detailed_info_df.side_effects]
            side_effects = sum(side_effects, [])
            side_effects = [x.strip().lower() for x in side_effects]
            temp = pd.DataFrame(side_effects, columns=['side_effect'])
            side_effect_chart = px.bar(temp, x="side_effect", color_discrete_sequence=['steelblue'])
            side_effect_chart.update_xaxes(tickfont_size=13, tickangle=45)
            side_effect_chart.update_layout(xaxis={'categoryorder': 'total descending'},
                                            xaxis_title="Side Effect", yaxis_title='Count')
            st.plotly_chart(side_effect_chart, use_container_width=True)

        with col4:
            st.subheader("Active Ingredient Distribution")
            active_ingredients = [x.split(",") for x in detailed_info_df.active_ingredient]
            active_ingredients = sum(active_ingredients, [])
            active_ingredients = [x.strip().lower() for x in active_ingredients]
            temp = pd.DataFrame(active_ingredients, columns=['active_ingredient'])
            active_ingredients_chart = px.bar(temp, x="active_ingredient", color_discrete_sequence=['steelblue'])
            active_ingredients_chart.update_xaxes(tickfont_size=13, tickangle=45)
            active_ingredients_chart.update_layout(xaxis={'categoryorder': 'total descending'},
                                                   xaxis_title="Active Ingredient", yaxis_title='Count')
            st.plotly_chart(active_ingredients_chart, use_container_width=True)

    elif st.session_state["action"] == "comparing_webpages":
        st.markdown("## 🛠 Medications Comparison")
        st.write("Ask any question about entered web pages.")

        # Initialize chat history in session state if not present
        if "messages" not in st.session_state:
            st.session_state.messages = []

        wp_inputs_form = st.sidebar.form('webpages')

        main_drug_input = wp_inputs_form.selectbox('Selected medication:', (st.session_state.med_name_input))
        similar_drug_input = wp_inputs_form.selectbox('Select similar medication:',
                                                      (st.session_state.list_similar_medications))
        report_template_input = wp_inputs_form.selectbox('Select report template:',
                                                         ('General Report', 'Reviews & Ratings Report'))
        submit_button_wp = wp_inputs_form.form_submit_button(label='Submit')

        if submit_button_wp:
            progress_bar = st.progress(10)
            template_content = get_content_for_template(main_drug_input=main_drug_input,
                                                        similar_drug_input=similar_drug_input,
                                                        process_reviews_pages=True)
            configs.default_variables.template_content = template_content
            progress_bar.progress(60)
            template_report = get_medications_comparison(llm=llm, template_content=template_content,
                                                         template=report_template_input)
            progress_bar.progress(100)
            with st.chat_message("assistant"):
                st.markdown(template_report)

        # Display all messages from the conversation so far
        # Each message is either a ModelRequest or ModelResponse.
        # We iterate over their parts to decide how to display them.
        for msg in st.session_state.messages:
            if isinstance(msg, ModelRequest) or isinstance(msg, ModelResponse):
                for part in msg.parts:
                    display_message_part(part)

        # Chat input for the user
        user_input = st.chat_input("Question?")

        if user_input:
            # We append a new request to the conversation explicitly
            st.session_state.messages.append(
                ModelRequest(parts=[UserPromptPart(content=user_input)])
            )

            # Display user prompt in the UI
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                # web_pages_content = get_web_comparison_content(wp_name_input1=wp_name_input1,
                #                                               wp_name_input2=wp_name_input2)
                if configs.default_variables.template_content=='':
                    template_content = get_content_for_template(main_drug_input=main_drug_input,
                                                                similar_drug_input=similar_drug_input,
                                                                process_reviews_pages=True)
                    configs.default_variables.template_content = template_content
                else:
                    template_content = configs.default_variables.template_content

                chat_question_output = get_web_comparison_chat_answer(llm=llm,
                                                                      question=user_input,
                                                                      web_pages_content=template_content,
                                                                      system_prompt_web_comparison=system_prompt_web_comparison)
                st.markdown(chat_question_output)

    elif st.session_state["action"] == "help_info":
        # st.markdown("## ℹ️ Help Information")
        st.title("ℹ️ Smart Medication Search Engine - Help & Info")

        st.markdown("---")

        st.header("📌 Overview")
        st.write(
            "A smart search engine that aggregates and analyzes medication data, enabling users to find and compare drugs "
            "based on active ingredients, therapeutic effects, and user reviews, facilitating data-driven pharmaceutical decision-making."
        )

        st.markdown("---")

        st.header("💡 Value to Company")
        st.markdown(
            "- **Automates pharmaceutical research**: Reduces manual search efforts for patients, healthcare providers, and pharmacists.\n"
            "- **Enhances decision-making**: Aggregates real-world medication feedback & reviews.\n"
            "- **Monetization potential**: Can be scaled and monetized through partnerships with healthcare providers, pharmacies, or online drug marketplaces.\n"
            "- **Improves patient safety**: Highlights well-reviewed alternatives to enhance drug efficacy awareness."
        )

        st.markdown("---")

        st.header("🎯 Purpose")
        st.write(
            "To automate and simplify the process of searching for medications by providing AI-powered recommendations, "
            "ensuring quick access to the most effective and well-reviewed options while enabling data-backed pharmaceutical insights."
        )

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔽 Inputs")
            st.markdown(
                "- **Medications websites**: drugs information sources.\n"
                "- **User reviews & feedback**: Collected from websites.\n"
                "- **Query inputs**: Medication name, medications to compare."
            )

        with col2:
            st.subheader("🔼 Outputs")
            st.markdown(
                "- **List of similar medications**: Based on active ingredients & therapeutic effects..etc.\n"
                "- **Aggregated insights & statistics**: Effectiveness ratings and sentiment analysis.\n"
                "- **AI-generated recommendations & reports**: Highlights best-rated alternatives. Different reports generated based on template."
            )

        st.markdown("---")

        st.header("🛠 Key Components")
        st.markdown(
            "- **AI-Powered Search Engine**: Retrieves and processes drug-related data from various online sources.\n"
            "- **Comparison & Similarity Module**: Identifies alternative medications based on active ingredients & therapeutic effects.\n"
            "- **Review Aggregation & Sentiment Analysis**: Extracts insights from user feedback, identifying trends in effectiveness and side effects.\n"
            "- **Personalized Recommendation System**: Suggests best-rated alternatives tailored to user queries."
        )

        st.markdown("---")

        st.header("📖 How to use?")
        st.header("💊 Medication Overview & Find Similar")
        st.write(
            "This page allows users to view detailed medical information about a entered medication, including:"
        )
        st.markdown(
            "- 📝 **Description**  \n"
            "- 💡 **Active ingredient**  \n"
            "- ⚠️ **Side effects**  \n"
            "- 🎯 **Therapeutic effects**  \n"
            "- 🚨 **Overdose information**  \n"
            "- 📦 **Storage instructions**  \n"
            "- 🔄 **Drug interactions**"
        )

        st.write(
            "To get this information, enter the medication name, select an LLM model, and press the **▶️ Submit** button."
        )

        st.subheader("🔍 Finding Similar Medications")
        st.write(
            "If you want to see similar medications, press the **Find Similar Drugs** button. "
            "After pressing this button, the system will generate two tables containing medical information for similar drugs."
            "Additionally, interactive visual charts will be displayed to show the distribution of different indicators. 📊"
        )

        st.header("⚖️ Medical Comparison Page")
        st.write(
            "This page allows users to compare two medications:"
            "\n- 🏥 One medication is entered by the user."
            "\n- 📌 The second medication can be selected from a dropdown list of similar drugs."
        )

        st.subheader("📄 Generating Reports")
        st.write(
            "Users can generate a report by selecting an option from the **📑 Select report template** dropdown menu."
        )

        st.subheader("💬 Custom Queries")
        st.write(
            "Users can also ask custom questions about the selected medication and receive an answer based on information gathered from medical websites. 🏥"
        )

        st.markdown("---")

        st.subheader("📢 More Information")
        st.markdown("[📊 View Presentation](" + default_variables.presentation_path + ")")

        st.markdown("---")

        st.info("❓ For any additional assistance, please refer to the documentation or contact support. 📞")

if __name__ == "__main__":
    main()

