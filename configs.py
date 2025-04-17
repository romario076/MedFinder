from prompts import *

class default_variables:
    med_name_input = 'Ibuprofen'
    website = 'drugs.com'
    #website = 'drugs-forum.com'
    #website = 'webmd.com'
    #website = 'goodrx.com'
    llm_model = 'claude-3-5-sonnet'
    available_llm_models = [llm_model]
    websites_info = {"drugs_com":{'main':'https://www.drugs.com/{medication}',
                                  'reviews':'https://www.drugs.com/comments/{medication}'
                                  }
                     }
    templates_map = {"General Report": template_base,
                     "Reviews & Ratings Report": template_reviews}

    list_similar_medications = ['ubrelvy','nurtec-odt','qulipta','paracetamol','diclofenac','amitriptyline','hydroxyzine','tramadol','cyclobenzaprine','duloxetine']
    base_info = {'description': 'Ibuprofen is a nonsteroidal anti-inflammatory drug (NSAID) that works by reducing hormones that cause inflammation and pain in the body',
     'active_ingredient': 'ibuprofen',
     'side_effects': 'nausea, vomiting, gas, bleeding, dizziness, headache, stomach/intestinal bleeding, heart attack, stroke, kidney problems, liver problems, low red blood cells, allergic reactions',
     'therapeutic_effects': 'reduce fever, treat pain, reduce inflammation, headache relief, toothache relief, back pain relief, arthritis relief, menstrual cramps relief',
     'number_reviews': '239',
     'rating': '7.4',
     'URL': 'https://www.drugs.com/ibuprofen.html',
     'similar_medications': 'Ubrelvy, Nurtec ODT, Qulipta, Paracetamol, Diclofenac, Amitriptyline, Hydroxyzine, Tramadol, Cyclobenzaprine, Duloxetine',
     'overdose': 'Overdose symptoms include nausea, vomiting, stomach pain, drowsiness, black or bloody stools, coughing up blood, shallow breathing, fainting, or coma',
     'storage': 'Store at room temperature away from moisture and heat. Do not allow the liquid medicine to freeze',
     'drug_interactions': 'Interacts with antidepressants, cyclosporine, lithium, methotrexate, blood thinners, heart/blood pressure medications, diuretics, steroid medicines',
     'summary': 'Reviews indicate ibuprofen is generally effective for pain relief, particularly for period pain, headaches and inflammatory conditions. Many users report good pain relief within 1 hour of taking it. Common complaints include stomach upset and reduced effectiveness for severe pain like toothache.',
     'positive_reviews': '153',
     'negative_reviews': '39',
     'sentiment_reviews': '0.66'}
    template_content = ''

    default_detailed_info_path = './detailed_info.csv'

    presentation_path = 'https://docs.google.com/presentation/d/12Wrmex7PmV-DWyr9e3KvMqnTyeQ78JfSwQt_kGO3gi0/edit?usp=sharing'
