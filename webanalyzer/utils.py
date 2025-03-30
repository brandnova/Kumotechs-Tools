import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urlparse
import logging
import os
from django.conf import settings
import socket
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_website(url):
    """
    Analyze a website and return information about it
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    result = {
        'url': url,
        'title': None,
        'description': None,
        'technologies': [],
        'server': None,
        'status_code': None,
        'response_time': None,
        'meta_tags': {},
        'social_media': [],
        'favicon': None,
        'mobile_friendly': False,
        'page_size': 0,
    }
    
    try:
        # Parse domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Measure response time
        start_time = time.time()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        response = requests.get(url, headers=headers, timeout=15)
        end_time = time.time()
        
        result['response_time'] = round(end_time - start_time, 2)
        result['status_code'] = response.status_code
        result['page_size'] = len(response.content)
        
        # Get server info from headers
        if 'Server' in response.headers:
            result['server'] = response.headers['Server']
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get title
        title_tag = soup.find('title')
        if title_tag:
            result['title'] = title_tag.text.strip()
        
        # Get meta tags
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            if name:
                content = meta.get('content')
                if content:
                    meta_tags[name] = content
        
        result['meta_tags'] = meta_tags
        
        # Get description
        result['description'] = meta_tags.get('description') or meta_tags.get('og:description')
        
        # Get favicon
        favicon = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
        if favicon and favicon.get('href'):
            favicon_url = favicon['href']
            if not favicon_url.startswith(('http://', 'https://')):
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                if favicon_url.startswith('/'):
                    favicon_url = f"{base_url}{favicon_url}"
                else:
                    favicon_url = f"{base_url}/{favicon_url}"
            result['favicon'] = favicon_url
        
        # Check mobile-friendliness
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport and 'width=device-width' in viewport.get('content', ''):
            result['mobile_friendly'] = True
        
        # Detect social media
        social_media = []
        social_patterns = {
            'Facebook': r'facebook\.com',
            'Twitter': r'twitter\.com|x\.com',
            'Instagram': r'instagram\.com',
            'LinkedIn': r'linkedin\.com',
            'YouTube': r'youtube\.com',
            'Pinterest': r'pinterest\.com',
            'TikTok': r'tiktok\.com',
            'GitHub': r'github\.com',
        }
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            for platform, pattern in social_patterns.items():
                if re.search(pattern, href):
                    social_media.append(platform)
        
        result['social_media'] = list(set(social_media))
        
        # Detect technologies
        technologies = []
        
        # CMS Detection
        # WordPress detection
        if soup.find('meta', attrs={'name': 'generator', 'content': re.compile('WordPress')}):
            technologies.append('WordPress')
        elif soup.find('link', attrs={'rel': 'https://api.w.org/'}):
            technologies.append('WordPress')
        elif 'wp-content' in response.text or 'wp-includes' in response.text:
            technologies.append('WordPress')
        
        # Joomla detection
        if soup.find('meta', attrs={'name': 'generator', 'content': re.compile('Joomla')}):
            technologies.append('Joomla')
        elif '/components/com_' in response.text:
            technologies.append('Joomla')
        
        # Drupal detection
        if soup.find('meta', attrs={'name': 'generator', 'content': re.compile('Drupal')}):
            technologies.append('Drupal')
        elif 'Drupal.settings' in response.text:
            technologies.append('Drupal')
        
        # Magento detection
        if 'Mage.Cookies' in response.text:
            technologies.append('Magento')
        
        # Shopify detection
        if 'shopify' in response.text.lower():
            technologies.append('Shopify')
        
        # Wix detection
        if 'wix.com' in response.text:
            technologies.append('Wix')
        
        # Squarespace detection
        if 'squarespace' in response.text.lower():
            technologies.append('Squarespace')
        
        # Frontend Frameworks
        # React detection
        if 'react' in response.text.lower() and 'reactdom' in response.text.lower():
            technologies.append('React')
        elif '_reactRootContainer' in response.text:
            technologies.append('React')
        
        # Angular detection
        if 'ng-app' in response.text or 'ng-controller' in response.text:
            technologies.append('Angular')
        elif 'angular.js' in response.text or 'angular.min.js' in response.text:
            technologies.append('Angular')
        
        # Vue detection
        if 'vue.js' in response.text or 'vue.min.js' in response.text:
            technologies.append('Vue.js')
        elif 'v-app' in response.text or 'v-bind' in response.text:
            technologies.append('Vue.js')
        
        # Next.js detection
        if 'next/head' in response.text or '__NEXT_DATA__' in response.text:
            technologies.append('Next.js')
        
        # Gatsby detection
        if 'gatsby' in response.text.lower():
            technologies.append('Gatsby')
        
        # Nuxt.js detection
        if 'nuxt' in response.text.lower() or '__NUXT__' in response.text:
            technologies.append('Nuxt.js')
        
        # CSS Frameworks
        # Bootstrap detection
        if 'bootstrap.css' in response.text or 'bootstrap.min.css' in response.text:
            technologies.append('Bootstrap')
        elif 'class="container"' in response.text and 'class="row"' in response.text:
            technologies.append('Bootstrap')
        
        # Tailwind detection
        if 'tailwind.css' in response.text or 'tailwind.min.css' in response.text:
            technologies.append('Tailwind CSS')
        elif re.search(r'class="[^"]*(?:flex|grid|md:|lg:|xl:|2xl:)', response.text):
            technologies.append('Tailwind CSS')
        
        # Bulma detection
        if 'bulma.css' in response.text or 'bulma.min.css' in response.text:
            technologies.append('Bulma')
        
        # Foundation detection
        if 'foundation.css' in response.text or 'foundation.min.css' in response.text:
            technologies.append('Foundation')
        
        # JavaScript Libraries
        # jQuery detection
        if 'jquery' in response.text.lower():
            technologies.append('jQuery')
        
        # Lodash detection
        if 'lodash' in response.text or '_.debounce' in response.text:
            technologies.append('Lodash')
        
        # Moment.js detection
        if 'moment.js' in response.text or 'moment.min.js' in response.text:
            technologies.append('Moment.js')
        
        # Backend Frameworks
        # Django detection
        if 'csrfmiddlewaretoken' in response.text:
            technologies.append('Django')
        elif 'django' in response.text.lower():
            technologies.append('Django')
        
        # Laravel detection
        if 'laravel' in response.text.lower() or 'csrf-token' in response.text:
            technologies.append('Laravel')
        
        # Express.js detection
        if 'x-powered-by' in response.headers and 'express' in response.headers['x-powered-by'].lower():
            technologies.append('Express.js')
        
        # Ruby on Rails detection
        if 'csrf-param' in response.text and 'csrf-token' in response.text:
            technologies.append('Ruby on Rails')
        
        # Services
        # Google Analytics detection
        if 'google-analytics.com' in response.text or 'gtag' in response.text:
            technologies.append('Google Analytics')
        
        # Cloudflare detection
        if 'cloudflare' in response.headers.get('server', '').lower():
            technologies.append('Cloudflare')
        elif 'cloudflare' in response.text.lower():
            technologies.append('Cloudflare')
        
        # Font Awesome detection
        if 'font-awesome' in response.text or 'fontawesome' in response.text:
            technologies.append('Font Awesome')
        
        # Google Fonts detection
        if 'fonts.googleapis.com' in response.text:
            technologies.append('Google Fonts')
        
        # Remove duplicates and sort
        technologies = sorted(list(set(technologies)))
        result['technologies'] = technologies
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error analyzing website {url}: {str(e)}")
        result['status_code'] = 0
        result['description'] = f"Error: {str(e)}"
    
    return result

def capture_screenshot(url, analysis_id):
    """
    Capture a screenshot of a website using Selenium
    Returns the path to the screenshot file
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        from django.db import transaction
        
        # Import the model here to avoid circular imports
        from webanalyzer.models import WebsiteAnalysis
        
        # Check if the analysis still exists
        try:
            analysis = WebsiteAnalysis.objects.get(pk=analysis_id)
        except WebsiteAnalysis.DoesNotExist:
            logger.warning(f"Analysis {analysis_id} no longer exists, cancelling screenshot capture")
            return None
        
        # Create directory if it doesn't exist
        media_root = getattr(settings, 'MEDIA_ROOT', 'media')
        screenshot_dir = os.path.join(media_root, 'screenshots')
        os.makedirs(screenshot_dir, exist_ok=True)
        
        # Generate a unique filename
        filename = f"{uuid.uuid4().hex}.png"
        output_path = os.path.join(screenshot_dir, filename)
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize the Chrome driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        try:
            # Navigate to the URL
            driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Take screenshot
            driver.save_screenshot(output_path)
            
            # Update the analysis with the screenshot path
            relative_path = os.path.join('screenshots', filename)
            
            # Check again if the analysis still exists before updating
            with transaction.atomic():
                try:
                    analysis = WebsiteAnalysis.objects.select_for_update().get(pk=analysis_id)
                    analysis.screenshot = relative_path
                    analysis.save()
                    logger.info(f"Screenshot saved for analysis {analysis_id}")
                except WebsiteAnalysis.DoesNotExist:
                    logger.warning(f"Analysis {analysis_id} was deleted during screenshot capture")
                    # Delete the screenshot file since we won't be using it
                    if os.path.exists(output_path):
                        os.remove(output_path)
            
            return relative_path
        finally:
            # Close the driver
            driver.quit()
    
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}")
        return None

