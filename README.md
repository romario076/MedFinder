## Instructions
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
#### For pre release versions
```
pip install crawl4ai --pre
```

#### Run post-installation setup
```
crawl4ai-setup
```
#### Verify your installation
```
crawl4ai-doctor
```

If you encounter any browser-related issues, you can install them manually:
```
python -m playwright install --with-deps chromium
```

<hr>

### Run application:
```
sreamlit run ui.py
```

<hr>

### Run docker:

#### Build docker image

```
docker build -t image_name .
```

#### Run container
```
docker run --name container_name -p 8000:8000 image_name
```

<hr>

For local use working with drugs.com website. For AWS usage works only with: webmd.com.

For not local usage neccessary to provide SERP API keys.
