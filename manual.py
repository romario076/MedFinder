import os
import pandas as pd

import numpy as np
import plotly.express as px
from importlib import reload

import prompts
reload(prompts)
from prompts import get_links_prompt, system_message_base, system_message1, system_message2, system_prompt_web_comparison
from tools import *
from configs import default_variables

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', None)



class medication_info(object):
    def __init__(self, medication):
        self.medication = medication
        self.base_content = ""
        self.bae_info = {}
        self.list_similar_medications = []
        self.detailed_content = ""
        self.detailed_info = {}
        self.template_report = ""

    def get_base_info(self):

        base_links = get_base_links(medication=self.medication,
                                    use_llm=True,
                                    get_links_prompt=get_links_prompt)
        self.base_content = get_base_content(base_links=base_links)
        self.base_info = generate_base_info(content=self.base_content,
                                       system_message_base=system_message_base)
        self.list_similar_medications = [x.strip().replace(" ", "-").lower() for x in
                                    self.base_info['similar_medications'].split(",")]
        return self.base_info

    def get_detailed_info(self):

        detailed_content, list_similar_upd = get_detailed_content(list_similar_medications=self.list_similar_medications)
        self.detailed_content = detailed_content
        self.detailed_info = generate_detailed_info(detailed_content=detailed_content,
                                               list_similar_upd=list_similar_upd,
                                               system_message1=system_message1,
                                               system_message2=system_message2)
        return self.detailed_info

    def get_medication_info(self, get_similar_medication_info=True):
        self.get_base_info()
        if get_similar_medication_info:
            self.get_detailed_info()

    def compare_medications(self, medication1, medication2, report_template_input, process_reviews_pages):

        template_content = get_content_for_template(main_drug_input=medication1,
                                                                similar_drug_input=medication2,
                                                                process_reviews_pages=process_reviews_pages)
        self.template_report = get_medications_comparison(template_content=template_content,
                                                     template=report_template_input)
        return self.template_report



medic = medication_info(medication='aspirin')

### Generate base info
base_info = medic.get_base_info()
print('Similar medications:',medic.list_similar_medications)

### Generate detailed info
detailed_info = medic.get_detailed_info()

### Generate medications comparison
template_report = medic.compare_medications(medication1='adderall',
                                            medication2='advil',
                                            report_template_input="General Report",
                                            process_reviews_pages=True)
print(template_report)