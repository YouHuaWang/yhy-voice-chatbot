import azure.cognitiveservices.speech as speechsdk
import re
from datetime import datetime, timedelta

# 初始化語音設定
speech_key, service_region = "FWnsaJKysYKwZlNTGq4Zyjyoc2v7hZVBf0zsB4MAk1R6E566VcVTJQQJ99AKACYeBjFXJ3w3AAAYACOGAqsJ", "eastus"

# 語音識別設定
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_recognition_language = "zh-TW"

# 語音合成設定
speech_config.speech_synthesis_voice_name = "zh-TW-HsiaoChenNeural"
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

# 初始化語音識別與語音合成
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# 獲取今天的日期
def get_today_date():
    today = datetime.now()
    return today.strftime("%m月%d日")

# 獲取明天的日期
def get_tomorrow_date():
    tomorrow = datetime.now() + timedelta(days=1)
    return tomorrow.strftime("%m月%d日")

# 定義回應邏輯
def respond_to_query(user_input):
    today_date = get_today_date()
    tomorrow_date = get_tomorrow_date()

    # 情境1: 今天的航班延誤
    if "今天" in user_input and "CI108" in user_input and "延誤" in user_input:
        return f"{today_date}的CI108航班因天氣不佳有延誤。是否還有其他想詢問？", True
    
    # 情境2: 明天的航班取消
    if "明天" in user_input and "CI108" in user_input and "取消" in user_input:
        return f"{tomorrow_date}的CI108航班因颱風因素已取消。是否還有其他想詢問？", True
    
    # 情境3: 詢問能否更改機票
    if "更改" in user_input and "訂位" in user_input and "機票" in user_input:
        return "可使用官網 管理行程/更改行程 網頁更改。是否還有其他想詢問？", True
    
    # 預設回應
    return "很抱歉，我無法回答您的問題，請稍後再試。", False

# 處理未識別問題的函數
def handle_unrecognized_question(user_input):
    response_text = f"向您確認一下，您剛才詢問的是：「{user_input}」，對嗎？"
    print(f"語航員：{response_text}")
    speak_response(response_text)

    follow_up_result = speech_recognizer.recognize_once()
    if follow_up_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        confirmation_input = follow_up_result.text
        print("使用者：{}".format(confirmation_input))
        if "是" in confirmation_input or "對" in confirmation_input:
            response_text = "好的，我會將您的問題記錄並協助處理。"
            print(f"語航員：{response_text}")
            speak_response(response_text)
        else:
            response_text = "抱歉，我無法處理您的問題。是否還有其他問題？"
            print(f"語航員：{response_text}")
            speak_response(response_text)
    else:
        print("未能識別語音，請再試一次。")
        speak_response("抱歉，我沒有聽清楚，請再說一次。")

# 問滿意度的函數
def ask_satisfaction():
    response_text = "若無其他問題，請問您對於此次服務之滿意度1到5給幾分？"
    print(f"語航員：{response_text}")
    speak_response(response_text)

# 確認是否還有問題
def check_more_questions(user_input):
    if "有" in user_input or "是" in user_input:
        response_text = "好的，請問您還有什麼問題？"
        print(f"語航員：{response_text}")
        speak_response(response_text)
        return True
    elif "沒有" in user_input or "否" in user_input:
        ask_satisfaction()
        return False
    else:
        response_text = "很抱歉，我無法判斷您的回覆。請問是否還有其他問題？"
        print(f"語航員：{response_text}")
        speak_response(response_text)
        return True

# 播放語音回應
def speak_response(response_text):
    result = speech_synthesizer.speak_text_async(response_text).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("語音合成失敗：{}".format(result.reason))

# 開始互動
print("語航員：您好，請問需要甚麼服務？")
speak_response("您好，請問需要甚麼服務？")

while True:
    print("等待使用者語音輸入...")
    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        user_input = result.text
        print("使用者：{}".format(user_input))

        response_text, is_recognized = respond_to_query(user_input)
        print("語航員：{}".format(response_text))
        speak_response(response_text)

        if not is_recognized:
            handle_unrecognized_question(user_input)

        # 確認是否還有問題
        print("等待使用者是否還有問題...")
        follow_up_result = speech_recognizer.recognize_once()

        if follow_up_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            follow_up_input = follow_up_result.text
            print("使用者：{}".format(follow_up_input))
            if not check_more_questions(follow_up_input):
                break
        elif follow_up_result.reason == speechsdk.ResultReason.NoMatch:
            print("未能識別語音，請再試一次。")
            speak_response("抱歉，我沒有聽清楚，請再說一次。")
        elif follow_up_result.reason == speechsdk.ResultReason.Canceled:
            print("語音識別取消，原因：{}".format(follow_up_result.cancellation_details.reason))
            speak_response("抱歉，語音服務目前不可用。")
            break

    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("未能識別語音，請再試一次。")
        speak_response("抱歉，我沒有聽清楚，請再說一次。")
    elif result.reason == speechsdk.ResultReason.Canceled:
        print("語音識別取消，原因：{}".format(result.cancellation_details.reason))
        speak_response("抱歉，語音服務目前不可用。")
        break

# 中文數字與阿拉伯數字對應字典
# CHINESE_TO_NUM_MAP = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5}

# def extract_number(user_input):
#     """
#     從使用者輸入中提取滿意度分數，支持阿拉伯數字、中文數字或包含'分'的描述。
#     """
#     print(f"提取滿意度: {user_input}")  # 印出用戶輸入

#     # 優先檢查阿拉伯數字
#     match_arabic = re.search(r'(\d)(?:分)?', user_input)
#     if match_arabic:
#         print(f"識別到阿拉伯數字: {match_arabic.group(1)}")  # 打印識別到的阿拉伯數字
#         return int(match_arabic.group(1))

#     # 若無阿拉伯數字，檢查中文數字
#     for chinese_num, arabic_num in CHINESE_TO_NUM_MAP.items():
#         if chinese_num in user_input:
#             print(f"識別到中文數字: {chinese_num} 對應阿拉伯數字: {arabic_num}")  # 打印識別到的中文數字
#             return arabic_num

#     # 若未匹配到數字，返回 None
#     print("未識別到有效的數字")  # 印出未識別數字的情況
#     return None

# def handle_satisfaction(user_input):
#     """
#     根據用戶的滿意度回覆給出相應回應。
#     """
#     # 提取滿意度分數
#     satisfaction = extract_number(user_input)
#     if satisfaction is None:  # 若未提取到有效分數
#         print(f"無法識別滿意度：{user_input}")  # 印出無法識別的情況
#         return "我無法理解您的回答，請以1到5的數字評分。", False

#     # 根據滿意度分數回應
#     if satisfaction in [1, 2]:
#         response = f"請問您給 {satisfaction} 分的原因是什麼呢？"
#         return response, False  # 繼續互動
#     elif satisfaction in [3, 4, 5]:
#         response = f"感謝您給予我們 {satisfaction} 分評價！期待下次為您服務，祝您順心愉快！"
#         return response, True  # 結束互動
#     else:
#         return "很抱歉，我只接受1到5的評分，請您再說一次。", False