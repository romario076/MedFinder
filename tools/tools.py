
import sys
import ast
import os
import pandas as pd

from llm.llm import *
from importlib import reload
from datetime import datetime
import requests
import asyncio
from typing import Coroutine, List, Sequence
from googlesearch import search
import time
import configs
reload(configs)

from dotenv import load_dotenv
load_dotenv(override=True)

websites_info = configs.default_variables.websites_info
templates_map = configs.default_variables.templates_map
websites = [websites_info[key]['main'] for key in websites_info.keys()]
websites = [x if x.endswith('.html') else x+".html" for x in websites]
websites_reviews = [websites_info[key]['reviews'] for key in websites_info.keys()]
websites_reviews = [x if x.endswith('.html') else x+".html" for x in websites_reviews]
website = configs.default_variables.website


#from crawler.crawler_base import crawler_main
if configs.default_variables.website!='drugs.com':
    use_serp_logic = True
    from crawler.crawler_base import crawler_main
else:
    use_serp_logic = False
    from crawler.crawler import crawler_main


def get_config_websites():
    websites_info = configs.default_variables.websites_info
    websites = [websites_info[key]['main'] for key in websites_info.keys()]
    websites = [x if x.endswith('.html') else x + ".html" for x in websites]
    return websites

def get_config_review_websites():
    websites_info = configs.default_variables.websites_info
    websites_reviews = [websites_info[key]['reviews'] for key in websites_info.keys()]
    websites_reviews = [x if x.endswith('.html') else x + ".html" for x in websites_reviews]
    return websites_reviews


def get_base_links_gooole(medication):
    query_main = "{medication} site:{website}".format(medication=medication, website=website)
    query_reviews = "{medication} reviews site:{website}".format(medication=medication, website=website)

    # Get the top results
    main_link = next(search(query_main, num_results=1), None)
    time.sleep(2)
    reviews_link = next(search(query_reviews, num_results=1), None)

    result = {
        "main": main_link,
        "reviews": reviews_link
    }
    print('Base Links:', result)
    base_links = list(result.values())

    return(base_links)


def get_base_links_serp(medication):
    ### Extension for multiple websites
    SERP_API_KEY = os.getenv('SERP_API_KEY')
    query_main = "{medication} site:{website}".format(medication=medication, website=website)
    query_reviews = "{medication} reviews site:{website}".format(medication=medication, website=website)

    def get_search_result(query):
        url = f"https://serpapi.com/search.json?q={query}&api_key={SERP_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return data["organic_results"][0]["link"] if "organic_results" in data else None

    result = {
        "main": get_search_result(query_main),
        "reviews": get_search_result(query_reviews)
    }
    print('Base Links:', result)
    base_links = list(result.values())
    return (base_links)


def get_base_links(llm, medication, use_llm, get_links_prompt):
    if not use_serp_logic:
        websites = get_config_websites()
        if use_llm:
            website = ",".join(websites)
            get_links_prompt_format = get_links_prompt.format(website=website, medication=medication)
            res1 = llm.invoke(message=get_links_prompt_format)
            base_links_dict = ast.literal_eval(res1)
            base_links = list(base_links_dict.values())
        else:
            base_links = [link.format(medication=medication) for link in websites]
            base_links.extend([link.format(medication=medication) for link in websites_reviews])
    else:
        base_links = get_base_links_serp(medication=medication)
    base_links = [x for x in base_links if x is not None]
    return(base_links)


def _limit_concurrency(coroutines: Sequence[Coroutine], concurrency: int) -> List[Coroutine]:
    """Decorate coroutines to limit concurrency.
    Enforces a limit on the number of coroutines that can run concurrently in higher
    level asyncio-compatible concurrency managers like asyncio.gather(coroutines) and
    asyncio.as_completed(coroutines).
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def with_concurrency_limit(coroutine: Coroutine) -> Coroutine:
        async with semaphore:
            return await coroutine

    return [with_concurrency_limit(coroutine) for coroutine in coroutines]


def get_base_content(base_links):
    #base_links_list = list(base_links.values())
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = []
    for link in base_links:
        tasks.append(crawler_main(url=link))
    #commands = asyncio.gather(*tasks, return_exceptions=False)
    commands = asyncio.gather(*_limit_concurrency(tasks, concurrency=6))
    results = loop.run_until_complete(commands)
    loop.close()
    results = [x for x in results if x is not None]
    base_content = "\n\n".join(results)
    return base_content


def generate_base_info(llm, content, system_message_base):
    try:
        st = datetime.now()
        content2 = system_message_base.format(text=content)
        print('Content len:', len(content2.split(" ")))
        base_info_output = llm.invoke(message=content2)
        print('Extracting and analysing base info Done!')
        print('Time:', datetime.now()-st)
        similar_medications = ast.literal_eval(base_info_output.strip())

        if type(similar_medications['similar_medications']) == str:
            similar_medications['similar_medications'] = [x.strip().replace(" ", "-").lower() for x in similar_medications['similar_medications'].split(",")]

        if type(similar_medications['side_effects']) == str:
            similar_medications['side_effects'] = [x.strip().replace(" ", "-").lower() for x in similar_medications['side_effects'].split(",")]
            similar_medications['side_effects'] = ", ".join(similar_medications['side_effects'])

        if type(similar_medications['therapeutic_effects']) == str:
            similar_medications['therapeutic_effects'] = [x.strip().replace(" ", "-").lower() for x in similar_medications['therapeutic_effects'].split(",")]
            similar_medications['therapeutic_effects'] = ", ".join(similar_medications['therapeutic_effects'])
    except Exception as e:
        print('[ERROR] ' + str(e))
        similar_medications = configs.default_variables.base_info
    return similar_medications


def get_detailed_content(list_similar_medications):
    ### Extension for multiple websites
    if use_serp_logic:
        websites = []
        for medication in list_similar_medications[:6]:
            websites.extend(get_base_links_serp(medication))
    else:
        websites = get_config_websites()
    websites = [x for x in websites if x is not None]
    detailed_content = ''
    list_similar_upd = []
    if len(list_similar_medications)>0:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            loop = asyncio.ProactorEventLoop()
        else:
            loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = []
        if use_serp_logic:
            for website in websites:
                tasks.append(crawler_main(url=website))
        else:
            for website in websites:
                for item in list_similar_medications[:6]:
                    tasks.append(crawler_main(url=website.format(medication=item)))
        #commands = asyncio.gather(*tasks, return_exceptions=True)
        commands = asyncio.gather(*_limit_concurrency(tasks, concurrency=6))
        results = loop.run_until_complete(commands)
        loop.close()
        results = [x for x in results if x is not None]
        detailed_content = "\n\n".join(results)
        list_similar_upd = [x for x in list_similar_medications if x in detailed_content]
    return detailed_content, list_similar_upd


def generate_detailed_info(llm, detailed_content, list_similar_upd, system_message1, system_message2):
    try:
        st = datetime.now()
        detailed_info_output = ""
        if len(list_similar_upd)>0:
            system_message_detailed = system_message1.format(medication_name=','.join(list_similar_upd)) + system_message2
            detailed_content2 = system_message_detailed.format(text=detailed_content)
            similar_info_output = llm.invoke(message=detailed_content2)

            print('Extracting and analysing detailed info DONE!')
            print('Time:', datetime.now() - st)
            detailed_info_output = ast.literal_eval(similar_info_output.strip())
            detailed_info_df = pd.DataFrame(detailed_info_output).T.reset_index(names='Medication')

            # Identify missing columns
            missing_columns = [col for col in get_default_detailed_info(path=configs.default_variables.default_detailed_info_path).columns if col not in detailed_info_df.columns]
            # Add missing columns with NaN values
            for col in missing_columns:
                detailed_info_df[col] = ''
        else:
            temp = get_default_detailed_info(path=configs.default_variables.default_detailed_info_path)
            detailed_info_df = pd.DataFrame(columns=list(temp.columns))

    except Exception as e:
        print('[ERROR] generate_detailed_info: ' + str(e))
        detailed_info_output_df = get_default_detailed_info(path=configs.default_variables.default_detailed_info_path)
        detailed_info_output = {}
        for drug in detailed_info_output_df.Medication:
            temp = detailed_info_output_df[detailed_info_output_df.Medication==drug]
            detailed_info_output[drug] = temp.drop('Medication', axis=1).to_dict('records')[0]
        detailed_info_df = pd.DataFrame(detailed_info_output).T.reset_index(names='Medication')
    return detailed_info_df


def get_web_comparison_content(wp_name_input1, wp_name_input2):
    if wp_name_input1 != "" and wp_name_input2 != "":
        links_to_analyse = [wp_name_input1, wp_name_input2]
    elif wp_name_input1 != "" and wp_name_input2 == "":
        links_to_analyse = [wp_name_input1]
    elif wp_name_input1 == "" and wp_name_input2 != "":
        links_to_analyse = [wp_name_input2]
    else:
        links_to_analyse = []
    if len(links_to_analyse)>0:
        web_pages_content = get_base_content(base_links=[wp_name_input1, wp_name_input2])
    else:
        web_pages_content = ""
    return web_pages_content

def get_web_comparison_chat_answer(llm, question, web_pages_content, system_prompt_web_comparison):
    if web_pages_content !="":
        web_pages_content2 = system_prompt_web_comparison.format(question=question)
        web_pages_content2 =  web_pages_content2.format(text=web_pages_content)
        chat_question_output = llm.invoke(message=web_pages_content2)
    else:
        chat_question_output = 'Links to the web pages are not correctly specified. Cannot answer on your question.'
    return chat_question_output


def get_default_detailed_info(path):
    detailed_info_df = pd.read_csv(path)
    detailed_info_df.rating = detailed_info_df.rating.astype(float)
    detailed_info_df.number_reviews = detailed_info_df.number_reviews.astype(int)
    return detailed_info_df


def process_url_find_medication(url, medication):
    if url == 'https://www.drugs.com/':
        url_medication = url + medication + ".html"
    else:
        print('Unknown URL:', url)
    return url_medication


def get_content_for_template(main_drug_input, similar_drug_input, process_reviews_pages=False):
    medications_to_compare = [main_drug_input, similar_drug_input]
    if use_serp_logic:
        websites = []
        websites_reviews = []
        for medication in medications_to_compare:
            websites.extend(get_base_links_serp(medication))
    else:
        websites = get_config_websites()
        websites_reviews = get_config_review_websites()

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = []
    for website in websites:
        temp = [crawler_main(url=website.format(medication=item)) for item in medications_to_compare]
        tasks.extend(temp)
    if process_reviews_pages:
        for website in websites_reviews:
            temp = [crawler_main(url=website.format(medication=item)) for item in medications_to_compare]
            tasks.extend(temp)
    commands = asyncio.gather(*_limit_concurrency(tasks, concurrency=6))
    results = loop.run_until_complete(commands)
    loop.close()

    if process_reviews_pages:
        template_content = "\n\n".join(results)
    else:
        for link,content in zip(medications_to_compare, results):
            temp = "Document for: " + link + "\nContent:" +content + "\n\n"
            template_content = template_content + temp
    return template_content


def get_medications_comparison(llm, template_content, template):
    prompt_template = templates_map[template]
    if template_content !="":
        template_content2 = prompt_template.format(text=template_content)
        chat_question_output = llm.invoke(message=template_content2)
    else:
        chat_question_output = 'Cannot extract information for selected drugs.'
    return chat_question_output


def max_unique_in_subarray(arr, k):
    from collections import defaultdict

    freq = defaultdict(int)
    unique_count = 0
    max_unique = 0

    for i in range(len(arr)):
        freq[arr[i]] += 1
        if freq[arr[i]] == 1:
            unique_count += 1

        if i >= k:
            freq[arr[i - k]] -= 1
            if freq[arr[i - k]] == 0:
                unique_count -= 1

        if i >= k - 1:
            max_unique = max(max_unique, unique_count)

    return max_unique
