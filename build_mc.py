import requests
import math
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="print the JSON resp/req",
                    action="store_true")
args = parser.parse_args()

# The URL for the admin interface
base_url = "http://www.portphilio.com:5001"
api_url = "%s%s" % (base_url, "/api/v1/")


def print_color(string, status_code):
    colors = {
        "200": '\033[92m',
        "300": '\033[93m',
        "400": '\033[93m',
        "500": '\033[91m',
        "end": '\033[0m'
    }

    k = str(int(math.floor(int(status_code) / 10) * 10))
    print colors[k] + string + colors['end']


def print_json(s, json_data):
    if args.verbose:
        print s
        print json.dumps(json_data, indent=4, separators=(',', ': '))


def get(url):
    ''' Makes a GET request, prints the response
    '''
    r = requests.get(url, cookies=cookies)
    print_color("GET %s %s" % (url, r.status_code), r.status_code)
    try :
        print_json("RESPONSE: ", r.json())
    except : # Not necessarily JSON...
        pass
    return r


def post(url, data):
    ''' Makes a POST request, prints the response
    '''
    headers = {'content-type': 'application/json'}
    r = requests.post(
        url,
        data=json.dumps(data),
        cookies=cookies,
        headers=headers)
    print_color("POST %s %s" % (url, r.status_code), r.status_code)
    print_json("REQUEST:", data)
    print_json("RESPONSE: ", r.json())
    return r


def put(url, data):
    ''' Makes a PUT request, prints the response
    '''
    headers = {'content-type': 'application/json'}
    r = requests.put(
        url,
        data=json.dumps(data),
        cookies=cookies,
        headers=headers)
    print_color("POST %s %s" % (url, r.status_code), r.status_code)
    print_json("REQUEST:", data)
    print_json("RESPONSE: ", r.json())
    return r

"""
API-specific functions
"""


def login(credentials):
    'Logs into the API'
    url = "%s%s" % (base_url, "/login/")
    r = requests.post(url, data=credentials)
    print_color("POST %s %s" % (url, r.status_code), r.status_code)
    return r.cookies


def clear_db():
    get("%s%s" % (base_url, "/clear_db/"))


def post_work(data):
    r = post(api_url + 'work/', data=data)
    return r.json()["result"]["_id"]


def post_photo(data):
    r = post(api_url + 'photo/', data=data)
    return r.json()["result"]["_id"]


def put_work_succset(id, data):
    r = put(api_url + "work/" + id + '/succset/', data=data)
    return r.json()


def put_cat_succset(id, data):
    r = put(api_url + "category/" + id + '/succset/', data=data)
    return r.json()


def post_cat(data):
    r = post(api_url + 'category/', data=data)
    return r.json()["result"]["_id"]


def put_body_vertex(data):
    r = put(api_url + "body/succset/", data=data)
    return r.json()


# Login
cookies = login({"email": "test_email_address@maggiecasey.com", "password": "a"})

# Clear the database
clear_db()

# Create the categories
ins_id = post_cat({"slug": "installations", "title": "INSTALLATIONS"})
scu_id = post_cat({"slug": "sculpture", "title": "SCULPTURE"})

# Put the categories into the body
put_body_vertex({"succset": [ins_id, scu_id]})

# Create the Works
works = [
    {"data": {
        "title": "Range",
        "slug": "range",
        "medium": "Archival Ink Jet Print on Canvas",
        "size": "13' x 4'",
        "date": "2010",
        "description": "Range is a manipulated photograph taken of a military proving ground in Nevada. The resolution of the photograph was deliberately modified multiple times and layered together in a composite image. The resulting photograph appears to have multiple resolutions determined by the viewing distance.\nCollaboration between Maggie Casey and Jeffrey Stockbridge."
    },
        "photos": [
        "/image/Rangeweb01.jpg",
        "/image/BearingTheEcho01.jpg",
        "/image/Range01.jpg"]
    }
]

ins_works = []

for work in works:
    # Create the work
    work_id = post_work(work["data"])

    # Create the photos
    succset = [post_photo({"href": x}) for x in work["photos"]]

    # Add the photos to the succset of the work
    put_work_succset(work_id, {"succset": succset})

    ins_works.append(work_id)

# Add the work to the category
put_cat_succset(ins_id, {"succset": ins_works})


# Now that everything is build, run some testing stuff
get(api_url + "body/")
get(api_url + "category/")
get(api_url + "category/" + ins_id + "/")


'''
    ins_dict_list = [
        {"title": "Gold Tooth", "slug": "gold-tooth"},
        {"title": "Processions: an Elaborative Cartography", "slug": "processions-an-elaborative-cartography"},
        {"title": "Gold Tooth; Tapestries", "slug": "gold-tooth-tapestries"},
        {"title": "Feathers", "slug": "feathers"},
        {"title": "Staircase", "slug": "staircase"},
        {"title": "Two Chairs", "slug": "two-chairs"},
        {"title": "Duck and Silkworm Celebrate Synthetic Advancement", "slug": "duck-and-silkworm-celebrate-synthetic-advancement"}]

    scu_dict_list = [
        {"title": "Breaker", "slug": "breaker"},
        {"title": "Cover", "slug": "cover"},
        {"title": "Heap", "slug": "heap"},
        {"title": "Comma", "slug": "comma"},
        {"title": "Memorial to Tray Anning", "slug": "memorial-to-tray-anning"},
        {"title": "Hers", "slug": "hers"},
        {"title": "Model: Cloud", "slug": "model-cloud"},
        {"title": "Model: Splitting", "slug": "model-splitting"},
        {"title": "Model: Hanging Angle", "slug": "model-hanging-angle"}]
'''
