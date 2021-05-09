# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from bs4 import BeautifulSoup
import requests

# %% [markdown]
# ### Task 1: Get all links to the each event

# %%
base_url = 'http://www.ufcstats.com./statistics/events/completed'
all_urls = [base_url + f"?page={i}" for i in range(2, 23)]
all_urls.insert(0, base_url)
all_urls


# %%
def get_links_event(urls):
    """ Return each link to the UFC events"""
    links = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content)
        info_rows = soup.find_all('tr', class_='b-statistics__table-row')[2:]

        for row in info_rows:
            link = row.find('a')['href']
            links.append(link)
    return links


even_links = get_links_event(all_urls)
even_links[:10]

# %% [markdown]
# ### Task 2: Get information from each event

# %%


def get_links_fight(urls):
    """Return each link to the fight detail"""
    links = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content)
        table = soup.find('table', class_='b-fight-details__table')
        rows = table.find_all('tr')
        for row in rows[1:]:
            links.append(row['data-link'])
    return links


fight_links = get_links_fight(even_links)
fight_links[:10]

# %% [markdown]
# ### Task 3: Create dictionary of data for each fight

# %%


def get_info_box(soup_obj):
    """Return a dictinary about the information box (method, round,time,referee,and detail)"""
    my_dict = {}

    # get info box
    fight_title = soup_obj.find(
        'div', class_='b-fight-details__fight-head').get_text(strip=True)
    my_dict['Fight Type'] = fight_title
    box = soup_obj.find('p', class_='b-fight-details__text')
    method = box.find_all(class_='b-fight-details__text-item_first')
    method = method[0].get_text('\n', strip=True).split('\n')
    if len(method) >= 2:
        my_dict[method[0]] = method[1]

    # get the rest of content of info box
    content = box.find_all(class_='b-fight-details__text-item')
    for item in content:
        pair = item.get_text('\n', strip=True).split('\n')
        if len(pair) >= 2:
            my_dict[pair[0]] = pair[1]
        else:
            my_dict[pair[0]] = None
    detail = box.find_next_sibling("p").get_text(strip=True).split(':')
    my_dict[detail[0]] = detail[1]

    return my_dict


def get_fight_detail(soup_obj):
    """Return a dictionary about fight details (fighter's names, significant strike"""
    my_dict = {}
    table = soup_obj.find('tbody', class_='b-fight-details__table-body')
    info = table.select('.b-fight-details__table-col')
    index = [0, 2, 3, 4]
    info = [info[i].get_text('\n', strip=True) for i in index]

    # Red and blue figters
    fighters = info[0].split('\n')
    my_dict['r_figher'] = fighters[0]
    my_dict['b_figher'] = fighters[1]

    # significant strike
    sig_str = info[1].split('\n')
    my_dict['r_figher_sig_str'] = sig_str[0]
    my_dict['b_figher_sig_str'] = sig_str[1]

    # significant strik percentage
    sig_str_pct = info[2].split('\n')
    my_dict['r_figher_sig_str %'] = sig_str_pct[0]
    my_dict['b_figher_sig_str %'] = sig_str_pct[1]

    # total strike
    total_str = info[3].split('\n')
    my_dict['r_figher_total_str'] = total_str[0]
    my_dict['b_figher_total_str'] = total_str[1]

    return my_dict


def merge(dict1, dict2):
    """Merge two dictionaries"""
    res = {**dict1, **dict2}
    return res


def get_fight_info(url):
    """Return dictionary with information about the fight"""
    r = requests.get(url)
    soup = BeautifulSoup(r.content)

    # get info box
    dict_list = get_info_box(soup)
    # get the winner
    winner = soup.find(
        'i', class_='b-fight-details__person-status_style_green')
    if winner is not None:
        winner = winner.find_next('div', class_='b-fight-details__person-text')
        winner = winner.find('a').get_text(strip=True)
        dict_list['Winner'] = winner
    else:
        dict_list['Winner'] = 'draw'

    # get fight info
    fight_info = get_fight_detail(soup)
    new_dict = merge(dict_list, fight_info)
    return new_dict


# %%
fight_info_list = [get_fight_info(link) for link in fight_links]
