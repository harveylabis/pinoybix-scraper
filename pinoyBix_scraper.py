""" One time scrape the questions from the website """

from bs4 import BeautifulSoup
import requests
import re
import json
import time
from pathlib import Path

all_data = {}
data_folder = Path("questions")

# open the topics
with open("url_links.json", 'r') as f:
    topics_urls = json.load(f)
topics = [topic for topic in topics_urls]

# loop through topics
for topic in topics:
    filename = topic + ".json"
    filename = data_folder / filename
    question_counter = 1
    links_counter = 1

    # loop through urls inside a current topic
    question_found = False
    for url in topics_urls[topic]['urls']:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        data_p = []
        #data_p = [line.text for line in soup.find_all(['p', 'a'])]
        # line.text for line in soup.find_all(['p', 'a'])
        for line in soup.find_all(['p', 'a']):
            if '<p>' in str(line):
                data_p.append(line.text)
            elif "<a href=" in str(line):
                data_p.append(str(line))

        que_pattern = "[0-9]+\. " # pattern for question
        choi_pattern1 = "[ABCD]\) " # pattern for choices with letter+parenthesis: pattern 1
        choi_pattern2 = "[ABCD]\. " # pattern for choices with letter+dot: pattern 2
        img_pattern1 = "http.+?\.png" # pattern for links of image attached: png
        img_pattern2 = "http.+?\.gif" # pattern for links of image attached: gif
        # data = {}
        # questions = [] # store the dictionaries of items which to be stored as data
        item = {} # store each inidividual item or question: question, choices, key_answer
        item['choices'] = [] # store the list of choices

        for data in data_p:
            # print(data)
            que = re.search(que_pattern, data)   # search for the question
            choi_pat1 = re.search(choi_pattern1, data) # search if line contains choices with pattern1
            choi_pat2 = re.search(choi_pattern2, data) # search if line contains choices with pattern2
            choi = None # choi pattern is either pattern 1 or 2, store here whichever is match
            img_pat1 = re.search(img_pattern1, data) # search if line contains image url
            img_pat2 = re.search(img_pattern2, data) # search if line contains image url
            img = None
            if choi_pat1:
                # print(choi_pat1)
                choi = choi_pat1
            else:
                choi = choi_pat2

            if img_pat1:
                img = img_pat1
            else:
                img = img_pat2

            # print(img_pat, question_found)
            # time.sleep(0.5)
            key_present = "Option" in data # check if the line contains the answer key; bcs the way website is programmed
            if que and que.span()[0] == 0:
                item['question'] = data # data is question, store data to item
                question_found = True
            elif img and question_found:
                img_url = img.group()
                question_found = False
            elif (not img) and question_found and (not (choi)):
                img_url = None
                question_found = False
            elif choi and choi.span()[0] == 0:
                # print("choice found", choi)
                if choi_pat1:
                    data = data.replace(")", ".")
                    item['choices'].append(data) # data is choice, store data to item
                else:
                    item['choices'].append(data) # data is choice, store data to item
            elif key_present:
                item['key_answer'] = data # data is key answer, store data to item
                # item['question_id'] =     counter
                if img_url:
                    # print(img_url)
                    item['img_url'] = img_url
                else:
                    item['img_url'] = None

                shallow_item = item.copy() # keep a shallow copy of item because it will be replaced / redefined; 
                all_data[question_counter] = shallow_item # key answer is last data; append the item now to question
                item['choices'] = [] # reset choices
                question_counter += 1

            

        print(f"{links_counter}: {topic} from {url} is now saved.")
        links_counter += 1
        time.sleep(2) # pause for 2 seconds to avoid overloading the website

    with open(filename, 'w', encoding='utf8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)