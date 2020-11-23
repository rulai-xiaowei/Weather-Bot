import time
import argparse
import requests
import os
import sys
import collections
#from mmdialog.global_utils.FileOps import write_file, write_json, read_json, read_file

request_json = {
    #"botId": "ff041cb6c87e431593c0c1f33f4de2dc",
    "botId": "ea62179bf20d4fd8bb62d5f8d686fa92",
    "start": 1488927463000,
    "messages": [], 
    "version": 15, # bot version
    "slot": { "variables": [
            {
                "name": "user.name",
                "value": "Jack"
            },
            {
                "name": "user.locale",
                "value": "ZH"
            }
        ]
    }
}

class RulaiNLU_Sloter():
    def __init__(self):
        self.base_url = 'https://api-testcn.rulaibot.cn/v1/dialog/{}'.format(request_json['botId'])
        #print(self.base_url)
        self.request_url, self.session = self.creat_session()

    def create_chat_request_json(self, text, turn_index, variables):
        '''
        创建新的请求, variables可以为空, 传递两个参数，当前对话的轮次 以及 输入的内容
        '''
        chat_request_json = {
            "text": text,
            "seq": turn_index,
            "slot": {
                "variables": variables
            }
        }
        return chat_request_json

    def creat_session(self):
        '''
        创建新的session
        '''
        session = requests.session()
        headers = {'Content-Type': 'application/json'}
        session_response = session.put(url=self.base_url, headers=headers, json=request_json)
        if session_response.status_code == 200:
            print("Create Session Successfully!!")
            session_response_json = session_response.json()
            version = session_response_json['session']['version']
            sessionId = session_response_json['session']['id']
            token = session_response_json['session']['token']
            request_url = '{0}/{1}/{2}/?token={3}'.format(self.base_url, version, sessionId, token)
            return request_url, session
        else:
            print(session_response)
            return None, None

    def chat2bot(self, request_url, text, turn_index=1):
        '''
        https://docs.rul.ai/docs/dialog-api#2-chat
        Create chat use the "Post" HTTP Method; Post请求：后一个请求不会把第一个请求覆盖掉。（所以 Post 用来增资源）
        curl -X POST -d 'Hi there'
        request_url = "https://api.rul.ai/v1/dialog/{botId}/{version}/{sessionId}/?token={token}
        :param request_url
        :param text
        '''
        variables = []
        chat_headers = {'Content-Type': 'application/json'}
        chat_request_json = self.create_chat_request_json(text, turn_index, variables)
        #print(chat_request_json)
        chat_response = self.session.post(url=request_url, json=chat_request_json, headers=chat_headers)
        import time
        #time.sleep(1)
        #print("response\n")
        #print(chat_response)

        chat_response_json = chat_response.json()
        #print("resp json\n")
        #print(chat_response_json)
        response_messages = chat_response_json['messages'] # for v4 api
        # 默认返回列表，因为可能有连续的多个回复
        turn_responses = []
        for m_ind in range(len(response_messages)):
            response_text = response_messages[m_ind]['text']
            #print(m_ind)
            #print(response_text)
            response_source = response_messages[m_ind]['source']
            response_task = response_messages[m_ind]['task']
            turn_responses.append([response_text, response_source, response_task])
        return turn_responses

    def nlu_slot_spotter_one_utt(self, one_utterance, cur_turn_index):
        '''
        uttId2texts: one sesssion data
        每次输入一句才能保证每次重新触发，否则会造成各种小错误，需要后处理过滤
        '''
        #print(one_utterance)
        #print(cur_turn_index)
        turn_responses = self.chat2bot(self.request_url, text=one_utterance, turn_index=cur_turn_index)
        #print("返回内容")
        print((turn_responses[1][0]))
        #print(len(turn_responses))
        if turn_responses is None:
            result = None
        else:
            response_text, _, response_task = turn_responses[0] # KFC Bot 只有一个回复，不需要遍历
            if response_task == 'Order':
                result = response_text
            else:
                result = None
        #print(result)
        return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, default="成都明天天气")
    args = parser.parse_args()
    #print(args)
    #sess2userIdtexts_path = './session_id2user_texts.json'
    #nlu_sess2userIdtexts_path = './nlu_session_id2user_texts.json' 
    #print("hello")
    sloter = RulaiNLU_Sloter()
    #sloter.nlu_slot_spotter_one_utt(args.text,1)
    i = 1
    while True:
        query = input()
        #print(i)
        sloter.nlu_slot_spotter_one_utt(query,i)
        i = i + 1
    exit(0)
    time.sleep(5)
    sloter.nlu_slot_spotter_one_utt("成都",2)
    time.sleep(5)
    sloter.nlu_slot_spotter_one_utt("明天",3)
