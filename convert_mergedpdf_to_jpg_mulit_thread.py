import tool_box as tb
import os
from pdf2image import convert_from_path
import fitz
from tqdm import tqdm
import json
import datetime
import threading
import queue
import sys


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


def page_search(pdf_document, search_term):
    # filename = "example.pdf"
    # search_term = "invoice"
    #pdf_document = fitz.open(filename)
    for current_page in range(len(pdf_document)):
        page = pdf_document.load_page(current_page)
        result = None
        if page.search_for(search_term):
            # print("%s found on page %i" % (search_term, current_page))
            result = current_page
            break
    return result

# Worker 類別，負責處理資料
class Worker(threading.Thread):
  def __init__(self, queue, thread_ID, pdf_document, dict):
    threading.Thread.__init__(self)
    self.queue = queue
    self.thread_ID = thread_ID
    self.pdf_file = pdf_document
    self.dict = dict

  def run(self):
    while self.queue.qsize() > 0:
      # 取得新的資料
      account_ID = self.queue.get()
      # 處理資料
      pageID = page_search(self.pdf_file, account_ID)
      self.dict[account_ID]=pageID
      print("Worker %d: %s->pageNum=%s, queueSize= %d" % (self.thread_ID, account_ID, pageID, self.queue.qsize()))


if __name__ == '__main__':
    #################################################################
    #設定參數
    build_address_index = True # 是否要建立頁碼索引檔，如果不要就會讀取上次已經建立好的 ./data/pdf_merge/address_index.json
    fileName = "112.07.pdf" # 管理費帳單檔案
    address_dict, account_list = load_dict("./data/放翁帳戶地址.csv") #放翁地址帳號索引
    #################################################################
    pdf_file = "./data/pdf_merge/" + fileName
    dict = {}
    not_convert_list = []
    pdf_document = fitz.open(pdf_file)
    # 開始測量
    start = datetime.datetime.now()

    # Get page number
    if build_address_index:
        print("Started Searching")
        # 建立佇列
        my_queue = queue.Queue()
        # 將資料放入佇列
        for account_ID in tqdm(account_list):
            my_queue.put(account_ID)
        # 建立兩個 Worker
        my_worker1 = Worker(my_queue, 1, pdf_document, dict)
        my_worker2 = Worker(my_queue, 2, pdf_document, dict)
        my_worker3 = Worker(my_queue, 3, pdf_document, dict)
        my_worker4 = Worker(my_queue, 4, pdf_document, dict)
        my_worker5 = Worker(my_queue, 5, pdf_document, dict)
        my_worker6 = Worker(my_queue, 6, pdf_document, dict)
        # 讓 Worker 開始處理資料
        my_worker1.start()
        my_worker2.start()
        my_worker3.start()
        my_worker4.start()
        my_worker5.start()
        my_worker6.start()
        # 等待所有 Worker 結束
        my_worker1.join()
        my_worker2.join()
        my_worker3.join()
        my_worker4.join()
        my_worker5.join()
        my_worker6.join()
        #print(dict)
        dict_pageID_address={}
        for account_ID, pageID in dict.items():
            #print(account_ID, pageID)
            if pageID == None:
                not_convert_list.append(str(account_ID) + "\n")
            else:
                address = address_dict.get(account_ID)
                dict_pageID_address[pageID] = address
        print("Started writing dictionary to a file")
        with open("./data/pdf_merge/address_index.json", "w", encoding="utf8") as fp:
            json.dump(dict_pageID_address, fp, ensure_ascii=False)  # encode dict into JSON
        print("Done writing dict into json file")
        # print(dict)
    else:
        with open("./data/pdf_merge/address_index.json", "r", encoding="utf8") as fp:
            # Load the dictionary from the file
            dict = json.load(fp)
    # 結束測量
    end = datetime.datetime.now()
    # 輸出結果
    print("頁面索引執行時間：", end - start)

    # convert pdf to jpg
    print("Started Converting")
    if os.path.exists(pdf_file):
        #pages = convert_from_path(pdf_file, 300, thread_count=8, poppler_path=r'D:\poppler-23.07.0\Library\bin')
        pages = convert_from_path(pdf_file, 300, thread_count=8)
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
