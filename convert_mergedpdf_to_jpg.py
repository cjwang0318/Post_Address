import tool_box as tb
import os
from pdf2image import convert_from_path
import fitz
from tqdm import tqdm
import json


# conda install -c conda-forge poppler
# https://github.com/Belval/pdf2image#how-to-install
# pip install pdf2image pillow protobuf
# pip install --upgrade --force-reinstall pymupdf

def load_dict(dict_path):
    address_dict = {}
    account_list = []
    address_list = tb.read_file(dict_path, 0)
    for line in address_list:
        temp = line.split(",")
        address = temp[0]
        account_ID = temp[1]
        account_list.append(account_ID)
        address_dict[account_ID] = address
    return address_dict, account_list


def page_search(filename, search_term):
    # filename = "example.pdf"
    # search_term = "invoice"
    pdf_document = fitz.open(filename)
    for current_page in range(len(pdf_document)):
        page = pdf_document.load_page(current_page)
        result = None
        if page.search_for(search_term):
            # print("%s found on page %i" % (search_term, current_page))
            result = current_page
            break
    return result


if __name__ == '__main__':
    #################################################################
    #設定參數
    build_address_index = False # 是否要建立頁碼索引檔，如果不要就會讀取上次已經建立好的 ./data/pdf_merge/address_index.json
    fileName = "112.07.pdf" # 管理費帳單檔案
    address_dict, account_list = load_dict("./data/放翁帳戶地址.csv") #放翁地址帳號索引
    #################################################################
    pdf_file = "./data/pdf_merge/" + fileName
    dict = {}
    not_convert_list = []

    # Get page number
    if build_address_index:
        print("Started Searching")
        for account_ID in tqdm(account_list):
            address = address_dict.get(account_ID)
            pageID = page_search(pdf_file, account_ID)
            if pageID == None:
                not_convert_list.append(str(account_ID) + "\n")
            else:
                dict[pageID] = address
        print("Started writing dictionary to a file")
        with open("./data/pdf_merge/address_index.json", "w", encoding="utf8") as fp:
            json.dump(dict, fp, ensure_ascii=False)  # encode dict into JSON
        print("Done writing dict into json file")
        # print(dict)
    else:
        with open("./data/pdf_merge/address_index.json", "r", encoding="utf8") as fp:
            # Load the dictionary from the file
            dict = json.load(fp)

    # convert pdf to jpg
    print("Started Converting")
    if os.path.exists(pdf_file):
        #pages = convert_from_path(pdf_file, 300, thread_count=4, poppler_path=r'D:\poppler-23.07.0\Library\bin')
        pages = convert_from_path(pdf_file, 300, thread_count=4)
        for page in tqdm(pages):
            # print(pages.index(page))
            if build_address_index:
                address = dict.get(pages.index(page))
            else:
                address = dict.get(str(pages.index(page)))
            if address == None:
                page.save("./data/jpg/" + str(pages.index(page)) + ".jpg", 'JPEG')
            else:
                page.save("./data/jpg/" + address + ".jpg", 'JPEG')
    else:
        print("pdf file is not exist...")
    tb.write_file("./轉換失敗名單.txt", not_convert_list)
