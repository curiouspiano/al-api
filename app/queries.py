import pymongo
import pandas as pd
import os
db_usn = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')

client = pymongo.MongoClient("mongodb+srv://{}:{}@al.hapcu.mongodb.net/?retryWrites=true&w=majority".format(db_usn, db_pass))
db = client.lootDB
C_upgrades = db.upgrades

SCROLL_COSTS = {
    #SCROLLS
    "scroll0" : 1000,
    "scroll1" : 40000,
    "scroll2" : 1600000,
    "scroll3" : 480000000,
    "scroll4" : 25000000000,
    #CSCROLLS
    "cscroll0" : 6400,
    "cscroll1" : 240000,
    "cscroll2" : 9200000,
    "cscroll3" : 2000000000
}

OFFERINGS = {
    None : 0,
    "nan" : 0,
    float('nan') : 0,
    'offeringp' : 1000000,
    'offering' : 27400000,
    'offeringx' : 600000000
}

def get_relevant_upgrade_data(item_name):
    condition = item_name
    #get all data for the item_name
    res = C_upgrades.find({"name": condition })
    #convert to pandas object
    df = pd.DataFrame(list(res))
    #Filter out anything that isn't 'scrollX' or 'cscrollX'
    df = df[df['scroll'].str.contains('scroll\\d', regex=True)]
    upgrade_data = df.groupby(['level','scroll', 'offering'],dropna=False).median().reset_index()
    return upgrade_data


def get_cheapest_upgrade(level_data, cur_value):
    level_data = level_data.reset_index()
    new_val = None
    results = None
    print(level_data)
    for index, row in level_data.iterrows():
        possible_value = cur_value
        print(index)
        print(row)

        scroll_name = str(level_data.iloc[index, level_data.columns.get_loc('scroll')])
        offering_name = None
        try:
            offering_name = str(level_data.iloc[index, level_data.columns.get_loc('offering')])
        except:
            print("No offering")
        chance = float(level_data.iloc[index, level_data.columns.get_loc('chance')])
        #Floor of chance is 100%
        print(OFFERINGS[offering_name])
        print(SCROLL_COSTS[scroll_name])
        chance = min(1.00, chance)        
        if scroll_name.startswith('c'):
            possible_value *= 3

        possible_value = (possible_value + SCROLL_COSTS[scroll_name] + OFFERINGS[offering_name]) * (1 / chance)

        #if compoundable, multiply value by 3

        if new_val == None or new_val > possible_value:
            new_val = possible_value
            results = {
                "value" : int(new_val),
                "scroll" : scroll_name,
                "offering" : offering_name,
                "chance" : chance
            }

    return results


def calculate_cost(data, base_value):
    max_level = data['level'].max() + 1
    results = {
        0 : {
            "value" : base_value,
            "scroll" : None,
            "offering" : None,
        }
    }
    cur_value = base_value
    cum_chance = 1
    total_required = 1
    for i in range(max_level):
        cost_to_beat = None
        level_data = data[data['level'] == i]


        cheapest = get_cheapest_upgrade(level_data, cur_value)

        
        cur_value = cheapest['value']         
        results[i+1] = cheapest


    return results


def find_item_values(item_name, base_value, primling_price):
    OFFERINGS['offeringp'] = primling_price
    upgrade_data = get_relevant_upgrade_data(item_name)
    results = calculate_cost(upgrade_data, base_value)
    print(results)

    return results



