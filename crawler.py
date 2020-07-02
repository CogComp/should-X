#!/usr/bin/env python3
import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--window-size=1024x768")
# chrome_options.add_argument("--headless")
chrome_options.add_argument('log-level=3')
driver = webdriver.Chrome(options=chrome_options)

def ask_google(query):
    # Search for query
    query = query.replace(' ', '+')
    driver.get('http://www.google.com/search?q=' + query)

    # Get text from Google answer box
    answer = driver.execute_script("return document.elementFromPoint(350, 230);").text

    description = None
    try:
        description = driver.find_element_by_xpath('//div[@data-dobid="dfn"]/span').text
    except:
        print(" * could not collect the description . . . ")

    result_type = None
    try:
        text = driver.find_element_by_xpath('//div[@id="search"]/div/div/div/div/div').text.strip().lower().replace("\n", " ")
        if text.startswith("dictionary"):
            result_type = "dictionary"
    except:
        print(" * failed to infer the type . . . ")

    categories = None
    try:
        categories = driver.find_element_by_xpath('//div[@id="search"]/div/div/div/div/div').text
        categories = categories.split("\n")[0]
    except:
        print(" * failed to infer the categories . . . ")

    source = None
    try:
        elem = driver.find_element_by_xpath('//div[@id="search"]/div/div/div/div/div/div/div/div[2]/div/div/a')
        source = elem.get_attribute('href')
    except:
        print(" * could not collect the link . . . ")


    output = {
        "result_type": result_type,
        "answer": answer,
        "description": description,
        "categories": categories,
        "source": source,
    }

    return output


# problem: source link is incorrect. It should be empty.
# the_answer = ask_google("Who is the US president?")

# problem: additional content next to "answer"
# the_answer = ask_google("how many calories in 1 cup of cooked red lentils?")

# problem: "categories" should be empty
the_answer = ask_google("what is the difference between red and panang curry?")

# problem: result_type should be conversion
# problem: answer is incorrect
# the_answer = ask_google("50 mm is how long?")

# answer is empty
# source is empty
# the_answer = ask_google("how to export data from excel to another excel file?")

# answer is incorrect
# the_answer = ask_google("are mcgriddles dairy free?")

# answer is incorrect
# source in incorrect
# the_answer = ask_google("what are the levels of earth's atmosphere?")

# source is empty
# the_answer = ask_google("how warm are fur coats?")

# answer is incorrect
# result_type should be translation
# the_answer = ask_google("are you almost here in spanish?")

# the_answer = ask_google("is gk shampoo good for hair?")
# the_answer = ask_google("who caused hysteria in the crucible?")
# the_answer = ask_google("why does my stomach hurt worse when i lay down?")
# the_answer = ask_google("what can someone do with your stolen iphone?")
# the_answer = ask_google("are v8 juice good for you?")


# the_answer = ask_google("who is misty kyd?")
# the_answer = ask_google("What is a car?")
# the_answer = ask_google("how big are cuy guinea pigs?")
print(json.dumps(the_answer, sort_keys=True, indent=4))
# driver.close()
