
from flask import Flask, request
import flask
import time
import V1
import datetime
import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)


class ChatGPTAskingBot(object):
    def __init__(self):
        config = V1.configure()
        self.answers = dict()
        self.ask_time = dict()
        self.chatgpt_asking = False
        self.asker = V1.Chatbot(
            config,
            conversation_id=config.get("conversation_id"),
            parent_id=config.get("parent_id"),
        )

    def ask(self, question: str):
        answer = self.answers.get(question, "")
        if answer == "":
            if self.chatgpt_asking is True:
                app.logger.error("服务器繁忙，拒绝请求，问题：" + question)
                return False, "目前我正在回答其他人的问题，请稍后再试"
            self.chatgpt_asking = True
            try:
                app.logger.info("尝试询问ChatGPT, 问题：" + question)
                self.answers[question] = "asking"
                self.ask_time[question] = int(datetime.datetime.now().timestamp())
                prev_text = ""
                for data in self.asker.ask(
                        question,
                ):
                    message = data["message"][len(prev_text):]
                    answer += message
                    prev_text = data["message"]
                self.answers[question] = answer
            except:
                return False, "预料之外的错误，请稍后重试"
            finally:
                self.chatgpt_asking = False
            app.logger.info("----------\nChatGPT回答问题：" + question + "\n" + "答案:" + answer + "\n----------")
            return True, answer
        elif answer == "asking":
            for i in range(30):
                answer = self.answers.get(question, "")
                if answer != "asking":
                    app.logger.info("从缓存中得到了答案，问题：" + question)
                    return True, answer
                time.sleep(1)
            if int(datetime.datetime.now().timestamp()) - self.ask_time[question] > 60:
                self.answers.pop(question)
                self.ask_time.pop(question)
                app.logger.error("ChatGPT回答超时，问题：" + question)
            app.logger.info("答案等待超时，问题：" + question)
            return False, "这个问题我暂时还没回答出来，请重试"
        else:
            if int(datetime.datetime.now().timestamp()) - self.ask_time[question] > 86400:
                self.answers.pop(question)
                self.ask_time.pop(question)
                app.logger.error("已有的答案缓存失效，问题：" + question)
            app.logger.info("从缓存中得到了答案，问题：" + question)
            return True, answer


@app.route('/chat')
def chat():
    rsp = flask.make_response("Bad Request")
    rsp.content_type = "text/plain; charset=utf-8"
    rsp.status_code = 400
    rsp.headers["Access-Control-Allow-Origin"] = "*"
    rsp.headers["Access-Control-Expose-Headers"] = "X-Requested-With"
    rsp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    client_ip = request.remote_addr
    question = request.args.get("q", "hello")
    authkey = request.args.get("key", "")
    if authkey != "3BlbmFpLm9wZW5haS5hdXR" and client_ip != "127.0.0.1":
        return rsp
    app.logger.error("合法请求，来源ip：" + client_ip + ", 问题：" + question)
    flag, rsp.data = chatgpt.ask(question)
    if flag is True:
        rsp.status_code = 200
    return rsp


@app.route('/')
def index():
    rsp = flask.make_response("Welcome to michael's server")
    rsp.content_type = "text/plain"
    rsp.status_code = 200
    return rsp


chatgpt = ChatGPTAskingBot()

if __name__ == '__main__':
    handler = logging.FileHandler("./chatgpt_bot_server.log", encoding='UTF-8')
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)
    app.run(host="0.0.0.0", port=8080)

