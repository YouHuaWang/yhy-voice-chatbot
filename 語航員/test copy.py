from dotenv import load_dotenv
import os
import azure.cognitiveservices.speech as speechsdk
from datetime import datetime, timedelta

# 載入 .env 檔案
load_dotenv()

# 從 .env 中取得設定值
speech_key = os.getenv("SPEECH_KEY")
service_region = os.getenv("SERVICE_REGION")

# 初始化語音設定
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

# 其餘程式碼保持不變...


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

    # 緊急模式
    if response_mode == "urgent":
        if "今天" in user_input and "CI108" in user_input and "延誤" in user_input:
            return f"{today_date} CI108 延誤。", True
        if "明天" in user_input and "CI108" in user_input and "取消" in user_input:
            return f"{tomorrow_date} CI108 取消。", True
        if "更改" in user_input and "訂位" in user_input and "機票" in user_input:
            return "可更改官網訂位。", True

    # 年長模式
    elif response_mode == "elderly":
        if "今天" in user_input and "CI108" in user_input and "延誤" in user_input:
            return f"您好，{today_date}的CI108航班因天氣不佳有延誤，請您放心，航班調整後會及時通知您。", True
        if "明天" in user_input and "CI108" in user_input and "取消" in user_input:
            return f"您好，{tomorrow_date}的CI108航班因颱風因素已取消。建議您可改搭其他航班或申請退票服務。", True
        if "更改" in user_input and "訂位" in user_input and "機票" in user_input:
            return "您好，您可以透過官網的『管理行程』頁面來進行更改，或撥打客服專線獲得協助。", True

    # 普通模式
    if "今天" in user_input and "CI108" in user_input and "延誤" in user_input:
        return f"{today_date}的CI108航班因天氣不佳有延誤。是否還有其他想詢問？", True
    if "明天" in user_input and "CI108" in user_input and "取消" in user_input:
        return f"{tomorrow_date}的CI108航班因颱風因素已取消。是否還有其他想詢問？", True
    if "更改" in user_input and "訂位" in user_input and "機票" in user_input:
        return "可使用官網 管理行程/更改行程 網頁更改。是否還有其他想詢問？", True

    return "很抱歉，我無法回答您的問題，請稍後再試。", False

# 播放語音回應
def speak_response(response_text):
    result = speech_synthesizer.speak_text_async(response_text).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("語音合成失敗：{}".format(result.reason))

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

# 問滿意度的函數
def ask_satisfaction():
    response_text = "若無其他問題，請問您對於此次服務之滿意度1到5給幾分？"
    print(f"語航員：{response_text}")
    speak_response(response_text)

# 開始互動
response_mode = "normal"  # 預設模式為普通模式

print("語航員：您好，請問您希望使用哪一種服務模式？1：緊急模式，2：年長模式，3：普通模式。")
speak_response("您好，請問您希望使用哪一種服務模式？1：緊急模式，2：年長模式，3：普通模式。")

result = speech_recognizer.recognize_once()
if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    user_input = result.text
    print("使用者：{}".format(user_input))

    if "1" in user_input or "一" in user_input:
        response_mode = "urgent"
        print("語航員：已切換到緊急模式。請問您有什麼問題？")
        speak_response("已切換到緊急模式。請問您有什麼問題？")
    elif "2" in user_input or "二" in user_input:
        response_mode = "elderly"
        print("語航員：已切換到年長模式。請問您有什麼問題？")
        speak_response("已切換到年長模式。請問您有什麼問題？")
    else:
        response_mode = "normal"
        print("語航員：已使用普通模式。請問您有什麼問題？")
        speak_response("已使用普通模式。請問您有什麼問題？")
else:
    print("未能識別語音，將使用普通模式。請問您有什麼問題？")
    speak_response("未能識別語音，將使用普通模式。請問您有什麼問題？")

while True:
    user_input_result = speech_recognizer.recognize_once()
    if user_input_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        user_input = user_input_result.text
        print("使用者：{}".format(user_input))

        response, handled = respond_to_query(user_input)
        print(f"語航員：{response}")
        speak_response(response)

        if handled:
            follow_up_result = speech_recognizer.recognize_once()
            if follow_up_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                follow_up_input = follow_up_result.text
                if not check_more_questions(follow_up_input):
                    break
    else:
        print("未能識別語音，請再試一次。")
        speak_response("抱歉，我沒有聽清楚，請再說一次。")
