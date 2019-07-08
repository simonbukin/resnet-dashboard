import requests
from _utils import pickle_file, open_pickle
from auth.auth import user, password
from datetime import datetime

url = "https://ucsc.service-now.com/api/now/table/incident?"
journal_url = "https://ucsc.service-now.com/api/now/table/sys_journal_field?"
headers = {"Content-Type":"application/json","Accept":"application/json"}

filters = {'all': 'sysparm_query=assignment_group=55e7ddcd0a0a3d280047abc06ed844c8^incident_state=1^ORincident_state=2^ORincident_state=3^ORincident_state=4^ORincident_state=5^incident_state=6^ORincident_state!=7',
           'first_contact': 'sysparm_query=active=true^task.active=true^task.assignment_group=javascript:getMyGroups()^task.state!=-5^sla=562982570a0a3d2800398d4204b0fda1',
           'client_updated': 'sysparm_query=assignment_group=55e7ddcd0a0a3d280047abc06ed844c8^incident_state=1^ORincident_state=2^ORincident_state=3^ORincident_state=4^ORincident_state=5^incident_state!=6^ORincident_state!=7^sys_updated_bySAMEAScaller_id.user_name',
           'unassigned': 'sysparm_query=active=true^assignment_group=55e7ddcd0a0a3d280047abc06ed844c8^assigned_toISEMPTY'}

# not awaiting client and no update in 3 days

def itr_pickle():
    pickle_file(high_priority(), 'itr.pickle')

def get_tickets(filter):
    filter_url = url + filter
    tickets = None
    resp = requests.get(filter_url, auth=(user, password), headers=headers)
    if(resp.status_code != 200):
        raise ConnectionError('Problem with get_tickets')
    else:
        tickets = [elem['number'] + ' ' + elem['short_description'] for elem in resp.json()['result']]
    return tickets

def get_tickets_raw(filter):
    filter_url = url + filter
    resp = requests.get(filter_url, auth=(user, password), headers=headers)
    if(resp.status_code != 200):
        raise ConnectionError('Problem with get_tickets_raw')
    return resp.json()['result']

def get_client_info(url):
    resp = requests.get(url, auth=(user, password), headers=headers)
    if(resp.status_code != 200):
        print(resp)
        # raise ConnectionError('Problem with get_client_info')
        return
    # print(resp.json())
    user_test = None
    try:
        user_test = resp.json()['result']
    except KeyError:
        pass
    return user_test

def get_tickets_in_progress():
    tickets = [ticket for ticket in get_tickets_raw(filters['all'])]
    # print(tickets[0])
    all_tickets = []
    for ticket in tickets:
        # print(ticket['short_description'])
        entries = get_journal_entries(ticket['sys_id'], 'comments')
        client = get_client_info(ticket['caller_id']['link'])
        if client is not None:
            client = client['user_name']
        # print(client)
        # print(entries)
        recent = sorted(entries, key=lambda entry: entry['sys_created_on'], reverse=True)[0]
        # print(recent)
        if recent['sys_created_by'] == client:
            # print('{} === {}'.format(recent['sys_created_by'], ticket['sys_created_by']))
            # print('{} ::: {}'.format(recent['sys_created_by'], recent['value']))
            all_tickets.append(ticket)
    # print(all_tickets)
    # for ticket in all_tickets:
    #     print(ticket['short_description'])
    all_tickets = [ticket['number'] + ' ' + ticket['short_description'] for ticket in all_tickets]
    return all_tickets

# work_notes = tech notes
# comments = comments
def get_journal_entries(element_id, journal_type):
    url = journal_url + 'sysparm_query=^element_id=' + element_id
    resp = requests.get(url, auth=(user, password), headers=headers)
    notes = [note for note in resp.json()['result'] if note['element'] == journal_type]
    for note in notes:
        note['sys_created_on'] = datetime.strptime(note['sys_created_on'], '%Y-%m-%d %H:%M:%S')
        # note['sys_created_on'] = note['sys_created_on'].strftime('%Y-%m-%d %H:%M:%S')
    return notes

def high_priority():
    unassigned = get_tickets(filters['unassigned'])
    client_updated = get_tickets(filters['client_updated'])
    in_progress = get_tickets_in_progress()
    tickets = list(set(unassigned + client_updated + in_progress))
    print(tickets)
    return tickets
