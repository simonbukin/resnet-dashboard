import requests
from _utils import json_file
from auth.auth import user, password
from datetime import datetime

# url for getting incidents (tickets)
url = "https://ucsc.service-now.com/api/now/table/incident?"
# url for journals (comments/tech notes on tickets)
journal_url = "https://ucsc.service-now.com/api/now/table/sys_journal_field?"
# required headers
headers = {"Content-Type": "application/json", "Accept": "application/json"}

# various filters for ITR
filters = {'all': ('sysparm_query=assignment_group=55e7ddcd0a0a3d280047abc06e'
                   'd844c8^incident_state=1^ORincident_state=2^ORincident_sta'
                   'te=3^ORincident_state=4^ORincident_state=5^incident_state'
                   '=6^ORincident_state!=7'),
           'first_contact': ('sysparm_query=active=true^task.active=true^'
                             'task.assignment_group=javascript:getMyGroup'
                             's()^task.state!=-5^sla=562982570a0a3d280039'
                             '8d4204b0fda1'),
           'client_updated': ('sysparm_query=assignment_group=55e7ddcd0a0'
                              'a3d280047abc06ed844c8^incident_state=1^ORi'
                              'ncident_state=2^ORincident_state=3^ORincid'
                              'ent_state=4^ORincident_state=5^incident_st'
                              'ate!=6^ORincident_state!=7^sys_updated_byS'
                              'AMEAScaller_id.user_name'),
           'unassigned': ('sysparm_query=active=true^assignment_group='
                          '55e7ddcd0a0a3d280047abc06ed844c8^assigned_t'
                          'oISEMPTY')}


def itr_json():
    """Write all the high priority tickets to itr.json."""
    json_file(high_priority(), 'itr.json')


def get_tickets(filter):
    """Return all the tickets from ITR given a filter."""
    filter_url = url + filter
    # send a request to get tickets matching the given filter
    resp = requests.get(filter_url, auth=(user, password), headers=headers)
    tickets = None
    if(resp.status_code != 200):  # response is not OK, throw error
        raise ConnectionError('Problem with get_tickets')
    else:
        # filter tickets to just be the incident number and title as a string
        # {big scary json with lots of info} -> ['INC3029103 Computer BROKE']
        tickets = []
        for elem in resp.json()['result']:
            tickets.append('{} {}'.format(elem['number'],
                                          elem['short_description']))
    return tickets


def get_tickets_raw(filter):
    """Return all the tickets from ITR given a filter, as raw JSON."""
    filter_url = url + filter
    # send a request to get tickets matching the given filter
    resp = requests.get(filter_url, auth=(user, password), headers=headers)
    if(resp.status_code != 200):  # response is not OK, throw error
        raise ConnectionError('Problem with get_tickets_raw')
    return resp.json()['result']


def get_client_info(url):
    """Get client information from JSON."""
    # send request to url
    resp = requests.get(url, auth=(user, password), headers=headers)
    if(resp.status_code != 200):  # response not OK, print response and exit
        print('get_client_info error with get request: {}'.format(resp))
        return
    else:
        user_test = None
        try:  # try to get result from request
            user_test = resp.json()['result']
        except KeyError:
            pass
        return user_test


def get_tickets_in_progress():
    """Get every current ticket matching 'ResNet All' into an array."""
    tickets = [ticket for ticket in get_tickets_raw(filters['all'])]
    in_progress = []
    for ticket in tickets:
        print(ticket['short_description'])
        # get the comments and client info
        entries = get_journal_entries(ticket['sys_id'], 'comments')
        client = get_client_info(ticket['caller_id']['link'])
        # TODO check this V
        # if no client info, just use client user_name
        if client is not None:
            client = client['user_name']

        # sort all the comments in a ticket by time
        recent = sorted(entries,
                        key=lambda entry: entry['sys_created_on'],
                        reverse=True)
        if len(recent) == 0:  # no comments? brand new ticket
            in_progress.append(ticket)
        elif recent[0]['sys_created_by'] == client:
            # most recent comment is client? needs response
            in_progress.append(ticket)
    # convert tickets into just strings with incident number and title
    in_progress_text = []
    for ticket in in_progress:
        in_progress_text.append('{} {}'.format(ticket['number'],
                                               ticket['short_description']))
    return in_progress_text


def get_journal_entries(element_id, journal_type):
    """Get the journal entries of a ticket (tech notes or comments)."""
    # work_notes = tech notes
    # comments = comments
    # construct url for sending request
    url = journal_url + 'sysparm_query=^element_id=' + element_id
    # send request
    resp = requests.get(url, auth=(user, password), headers=headers)
    # get every note matching the journal type specified
    notes = [note for note in resp.json()['result']
             if note['element'] == journal_type]
    for note in notes:
        # convert the created time to a python datetime
        # TODO add try except here V
        note['sys_created_on'] = datetime.strptime(note['sys_created_on'],
                                                   '%Y-%m-%d %H:%M:%S')
    return notes

# high priority is defined as:
# unassigned (priority max):
# new ticket or reassigned ticket from different department.
# Needs to be assigned to Stevenson or RCC and worked on
# client updated (priority secondary):
# client is the last responder on the ticket, needs response


def high_priority():
    """Return all the high priority tickets in the queue."""
    # get all unassigned tickets
    unassigned = get_tickets(filters['unassigned'])
    # make an array of tuples, 2nd index being priority
    unassigned = [(ticket, 1) for ticket in unassigned]
    # get all client updated tickets
    client_updated = get_tickets(filters['client_updated'])
    # make an array of tuples, 2nd index being priority
    client_updated = [(ticket, 0) for ticket in client_updated]
    # combine unassigned and client updated tickets into a set, turn into list
    # removes exact duplicate tickets, but not those with different priorities
    all_tickets = list(set(unassigned + client_updated))
    # need to remove the same tickets with different priorities
    # always favor the higher priority
    ticket_no_dupes = {}
    for ticket in all_tickets:
        # TODO check this if V
        if ticket[0] in ticket_no_dupes:  # if ticket already processed
            if ticket[1] > ticket_no_dupes[ticket[0]]:
                # check if new ticket has higher priority
                ticket_no_dupes[ticket[0]] = ticket[1]
                # update to higher priority
        else:  # if not in dict already, add it
            ticket_no_dupes[ticket[0]] = ticket[1]
    tickets_out = {'tickets': []}
    # update formatting of tickets,
    # key being the name of the ticket, value being it's priority
    # this returns an array of dicts
    tickets_out['tickets'] = []
    for key, val in ticket_no_dupes.items():
        tickets_out['tickets'].append({'ticket_name': str(key),
                                       'priority': str(val)})
    return tickets_out
