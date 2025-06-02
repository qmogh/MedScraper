from selenium import webdriver
from selenium.webdriver.chrome.service import Service


service = Service("/Users/amoghchaubey/Downloads/chromedriver-mac-arm64/chromedriver")
driver = webdriver.Chrome(service=service)
driver.get("https://google.com")
