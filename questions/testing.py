import json

id = 1
with open("ElectricalCircuit.json", 'r', encoding="utf8") as f:
    data = json.load(f)

counter = 1
question = str(counter)
print(data[question]['question'])
for choice in data[question]['choices']:
    print(choice)        
print(data[question]['key_answer'])
        
    

            