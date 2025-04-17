## Medical Finder

A smart search engine that aggregates and analyzes medication data, enabling users to find and compare drugs based on different medications characteristics: active ingredients, therapeutic effects, side effects, medical components, user ratings, reviews, facilitating data-driven pharmaceutical decision-making.

- AI-Powered Search Engine: Retrieves and processes drug-related data from various online sources.
- Comparison & Similarity Module: Identifies alternative medications based on active ingredients & therapeutic effects.
- Review Aggregation & Sentiment Analysis: Extracts insights from user feedback, identifying trends in effectiveness and side effects.
- Personalized Recommendation System: Suggests best-rated alternatives tailored to user queries.
- Also possible to ask a custom question about medications. Answer will be generated based on selected medications and based on inforamtion received from medical websites.

System uses medication websites to retriev information. List of the websites can be controlled in config file.

### Benefits

🚀 Efficiency & Automation

✅ Reduces manual search efforts for patients, healthcare providers, and pharmacists by automating pharmaceutical research.

✅ Speeds up medication discovery by providing AI-powered recommendations instantly.

💡 Data-Driven Decision Making

✅ Aggregates real-world medication feedback & reviews, offering insights based on effectiveness ratings and sentiment analysis.

✅ Enhances comparison accuracy by identifying alternative medications based on active ingredients and therapeutic effects.

📈 Scalability & Business Potential

✅ Creates monetization opportunities through partnerships with healthcare providers, pharmacies.

✅ Provides a scalable AI-driven solution that can be expanded to new markets and regions.

⚕️ Patient Safety & Better Outcomes

✅ Improves medication safety by highlighting the most effective and well-reviewed alternatives.

✅ Personalizes recommendations to individual needs, ensuring better treatment outcomes.

<hr>

### Instructions

Create .env file. Where put your keys for Calude LLM model and SERP API.

Structure:

- CLAUDE_MODEL_ID
- PROVIDER=anthropic
- AWS_DEFAULT_REGION
- SERP_API_KEY


To run app firstly need to install web crawler:
https://github.com/unclecode/crawl4ai/tree/main

Then run:
```
pip install -r requirements.txt
```

Install Crawl4AI:
#### Install the package
```
pip install -U crawl4ai
```
##### For pre release versions
```
pip install crawl4ai --pre
```

##### Run post-installation setup
```
crawl4ai-setup
```
##### Verify your installation
```
crawl4ai-doctor
```

If you encounter any browser-related issues, you can install them manually:
```
python -m playwright install --with-deps chromium
```

<hr>

#### Run application:
```
sreamlit run ui.py
```

<hr>

#### Run docker:

##### Build docker image

```
docker build -t image_name .
```

##### Run container
```
docker run --name container_name -p 8000:8000 image_name
```

<hr>

<img width="955" alt="image" src="https://github.com/user-attachments/assets/b1dd00a0-46de-4223-9462-9f732f7ebf84" />

<img width="793" alt="image" src="https://github.com/user-attachments/assets/9b07b0f2-5e97-48a3-8f6f-33d1955fcfd7" />

<img width="929" alt="image" src="https://github.com/user-attachments/assets/e22f0457-b6ad-4ddd-ab8c-d8b8fad78c1d" />

<hr>

For local use working with drugs.com website. For AWS usage works only with: webmd.com.

For not local usage neccessary to provide SERP API keys.
