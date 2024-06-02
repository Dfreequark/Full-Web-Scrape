import os
import requests
from requests_html import HTML # type: ignore
import re
import pandas as pd
import time



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

base_url ='https://www.assamyellowpage.com'
q_type ='/category/classified-ads/'




def get_links(url):

    r =requests.get(url)
    html_text = r.text
    re_html= HTML(html = html_text)

    href_format = re.compile(r'^(/classified/)')
    # time.sleep(1.5)
    node_el = re_html.find(".node-content", first = True)
    a_tags_list = node_el.find("a")
    href_list= [ item.attrs['href'] for item in a_tags_list if 'href' in item.attrs and href_format.match(item.attrs['href'])]

    return href_list

def get_details(end_link):

    r = requests.get(end_link)
    html_text = r.text
    re_html= HTML(html = html_text)

    details ={}

    node_el = re_html.find(".node-content", first = True)
    # time.sleep(1.5)
    fields_list = node_el.find(".field")
    for field in fields_list:
        try:
            field_label = field.find(".field__label", first= True).text
            field_item = field.find(".field-item", first= True).text
            details[field_label]= field_item
    
        except:
            p_tag = field.find('p')
            p_str =''
            for line in p_tag:
                p_str += line.text
            details["extra"] = p_str

        else:
            pass
            
        
    return details
        
def get_title(link):
    r = requests.get(link)
    html_text = r.text
    re_html= HTML(html = html_text)
    return re_html.find('h1', first = True).text

def single_category_details(url):
    category_details= {}
    links = get_links(url)
    for link in links:
        end_link = f'{base_url}{link}'
        # time.sleep(1.5)
        details =get_details(end_link)
        # time.sleep(1.5)
        title = get_title(end_link)
        category_details[title]=details
    return category_details

def get_csv(dictionary,  fname):
    header_names=['Name', 'Phone No', 'Email Id', 'Website', 'Address', 'Additional Details']
    table_data=[]
    for key, dict in dictionary.items():
        name = key
        phone_no = dict["Mobile No"] if "Mobile No" in dict else dict["Contact No"] if "Contact No" in dict else None
        email_id= dict["Email Id"] if "Email Id" in dict else None
        address = dict["Address"] if "Address" in dict else None
        website =dict["Website"] if "Website" in dict else None
        extra = dict["extra"] if "extra" in dict else None
        table_row =[ name, phone_no, email_id, website, address, extra]
        table_data.append(table_row)
    

    #saving data in a csv file
    df = pd.DataFrame(table_data, columns=header_names)
    path = os.path.join(BASE_DIR, "Details")
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join("Details", f'{fname}.csv')
    df.to_csv(file_path, index=True, index_label='Index')
    return True

def crawl_and_save(endpoint):
    page_no = 0
    next_page = True
    grand_dict={}
    while next_page:
        q_str=f"?page={page_no}"
        url =f'{base_url}{q_type}{endpoint}{q_str}'
        links = get_links(url)
        if not links:       #check if list is empty= False
            next_page = False

        details_dict =single_category_details(url)
        grand_dict.update(details_dict)
        print(f"Successfully added {page_no}")

        page_no +=1

    get_csv(dictionary=grand_dict,  fname= f'{endpoint}')
        

def get_categories(base_url):
    r= requests.get(base_url)
    html_text= r.text
    re_html = HTML(html = html_text)

    main_block_el= re_html.find(".view-classified", first = True)

    categories_list = main_block_el.find("a")
    categories=[]
    for item in categories_list:
        categories.append(item.text.lower().replace(" ","-"))
    return categories
if __name__ == "__main__":
    categories= get_categories(base_url=base_url)
    for category in categories:
        crawl_and_save(endpoint=category)
        print(f"{category} completed.\n -------------------")
    
    