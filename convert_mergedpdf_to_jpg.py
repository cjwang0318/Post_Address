import tool_box as tb
import os
from pdf2image import convert_from_path
import shutil
import fitz
#conda install -c conda-forge poppler
#pip install pdf2image, pillow, protobuf
#pip install --upgrade --force-reinstall pymupdf

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
        if page.search_for(search_term):
            print("%s found on page %i" % (search_term, current_page))
            result=current_page
            break
    return result

if __name__ == '__main__':
    fileName = "112.07"
    address_dict, account_list = load_dict("./data/放翁帳戶地址.csv")
    pdf_file = "./data/pdf_merge/" + fileName + ".pdf"
    dict={}
    not_convert_list = []
    i = 1
    total_num = len(account_list)
    for account_ID in account_list:
        j=0
        address = address_dict.get(account_ID)
        pageID = page_search(pdf_file, account_ID)
        dict[j]=address

    for account_ID in account_list:
        print("目前進度：" + str(i) + "/" + str(total_num))
        converted_file = "./data/converted/" + account_ID + ".pdf"
        # print(os.path.exists(pdf_file))
        address = address_dict.get(account_ID)
        pageID=page_search(pdf_file, account_ID)
        #print(pageID)
        if os.path.exists(pdf_file):
            pages = convert_from_path(pdf_file, 300, thread_count=4)
            for page in pages:
                page.save("./data/jpg/" + address + ".jpg", 'JPEG')
            shutil.move(pdf_file, converted_file)
        else:
            # print(address)
            not_convert_list.append(address + "\n")
        i = i + 1
    tb.write_file("./轉換失敗名單.txt", not_convert_list)
