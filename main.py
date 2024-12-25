import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from openai import OpenAI
import time

def load_env(file_path=".env"):
    """Loads environment variables from a file."""
    env_vars = {}
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        logging.error(f"Could not find the .env file at {file_path}.")
        raise
    return env_vars

class TestScraper(unittest.TestCase):
    """Scrape HTML from a website using Selenium and integrate OpenAI API"""

    @classmethod
    def setUpClass(cls):
        """Start web driver (only once for all tests)"""
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument("--window-size=1920,1080")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 10)

        # Load environment variables
        env_vars = load_env(".env")
        cls.username = env_vars.get("USERNAME")
        cls.password = env_vars.get("PASSWORD")
        cls.openai_api_key = env_vars.get("OPENAI_API_KEY")

        if not cls.username or not cls.password or not cls.openai_api_key:
            logging.error("Missing critical environment variables (USERNAME, PASSWORD, OPENAI_API_KEY).")
            raise EnvironmentError("Missing environment variables.")

    @classmethod
    def tearDownClass(cls):
        """Stop web driver"""
        cls.driver.quit()

    def get_openai_quote(self):
        """Asynchronous call to OpenAI API."""
        try:
            logging.info("Requesting a quote from OpenAI...")
            client = OpenAI(api_key=self.openai_api_key)
            chat_completion = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'user', 'content': 'give me a wise stoic quote, put the quote in quotation marks and also separate the quote from the part who said it by one line'},
                ]
            )
            output = chat_completion.choices[0].message.content
            logging.info(f"Received quote: {output}")
            return output
        except Exception as e:
            logging.error(f"Error while requesting a quote from OpenAI: {e}")
            raise

    def test_web_navigation_and_openai_integration(self):
        """Navigate the web and use OpenAI API"""
        url = 'https://www.threads.net/login'
        logging.info(f"Navigating to {url}...")
        self.driver.get(url)

        # Clicking Cookie button
        cookie_button = '.x1i10hfl.xjbqb8w.x1ypdohk.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xexx8yu.x18d9i69.x1n2onr6.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x1lku1pv.x1a2a7pz.x6s0dn4.x1a2cdl4.xnhgr82.x1qt0ttw.xgk8upj.x9f619.x3nfvp2.x1s688f.x90ne7k.xl56j7k.x193iq5w.x1swvt13.x1pi30zi.x12w9bfk.x1g2r6go.x11xpdln.xz4gly6.x87ps6o.xuxw1ft.x19kf12q.x6bh95i.x1re03b8.x1hvtcl2.x3ug3ww.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x178xt8z.xm81vs4.xso031l.xy80clv.xp07o12.x11r8ahe.x1iyjqo2.x15x72sd'
        try:
            div = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, cookie_button)))
            div.click()
            logging.info("Clicked the cookie button.")
        except Exception as e:
            logging.error(f"Error finding element for cookie button: {e}")
            raise

        time.sleep(2)

        # Clicking button to login page
        login_page_button = '.x6s0dn4.x78zum5.x1qughib.x10b6aqq.xh8yej3'

        try:
            link_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, login_page_button)))
            link_element.click()
            logging.info("Navigated to login page.")
        except Exception as e:
            logging.error(f"Error finding or clicking the login page link: {e}")
            raise

        time.sleep(3)

        # Logging in
        try:
            actions = ActionChains(self.driver)
            actions.send_keys(self.username).send_keys(Keys.TAB).perform()
            time.sleep(3)
            actions.send_keys(self.password).send_keys(Keys.ENTER).perform()
            logging.info("Logged in successfully.")
        except Exception as e:
            logging.error(f"Error during login: {e}")
            raise

        time.sleep(5)

        # Wait for the quote to be ready
        quote = self.get_openai_quote()

        # Posting the quote
        post_creation_button = '.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xe8uvvx.xdj266r.xat24cr.xexx8yu.x4uap5.x18d9i69.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x6s0dn4.x1a2cdl4.xnhgr82.x1qt0ttw.xgk8upj.x1ed109x.x78zum5.x1iyjqo2.x1i64zmx.x1emribx.x1e558r4.x87ps6o'
        try:
            create_post_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, post_creation_button)))
            create_post_button.click()
            logging.info("Opened post creation dialog.")
        except Exception as e:
            logging.error(f"Error finding or clicking the create-post button: {e}")
            raise

        time.sleep(5)

        try:
            actions.send_keys(quote).perform()
            logging.info("Typed the quote into the post field.")
            time.sleep(2)
            actions.key_down(Keys.CONTROL).send_keys(Keys.RETURN).key_up(Keys.CONTROL).perform()
            logging.info("Posted the quote successfully.")
        except Exception as e:
            logging.error(f"Error while typing or posting the quote: {e}")
            raise

        time.sleep(5)

        # Close the browser
        logging.info("Closing the browser...")
        self.driver.quit()

if __name__ == '__main__':
    unittest.main(verbosity=2)
