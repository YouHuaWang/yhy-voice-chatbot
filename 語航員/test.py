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

# 定義回應邏輯
def respond_to_query(user_input):
    today_date = get_today_date()
    tomorrow_date = get_tomorrow_date()

    # 緊急模式
    if response_mode == "urgent":
        if "今天" in user_input and "CI108" in user_input and "延誤" in user_input:
            return f"{today_date} 航班CI108 延誤。是否順利解決您的問題？", True
        if "明天" in user_input and "CI108" in user_input and "取消" in user_input:
            return f"{tomorrow_date} 航班CI108 取消。是否順利解決您的問題？", True
        if "更改" in user_input and "訂位" in user_input and "機票" in user_input:
            return "可更改官網訂位。是否順利解決您的問題？", True

    # 關懷模式
    elif response_mode == "gentle":
        if "今天" in user_input and "CI108" in user_input and "延誤" in user_input:
            return f"您好，{today_date}的CI108航班因天氣不佳有延誤，其登機時間將由原訂10點延後至14點，若確定停飛，也請您不要擔心，您可取消或更改行程。是否還有其他想詢問？", True
        if "明天" in user_input and "CI108" in user_input and "取消" in user_input:
            return f"您好，{tomorrow_date}的CI108航班因颱風因素已取消。建議您可改搭其他航班或申請退票服務。是否還有其他想詢問？", True
        if "更改" in user_input and "訂位" in user_input and "機票" in user_input:
            return "您好，您可以透過官網的『管理行程』頁面來進行更改，或撥打客服專線獲得協助。是否還有其他想詢問？", True

    # 一般模式
    if "今天" in user_input and "CI108" in user_input and "延誤" in user_input:
        return f"{today_date}的CI108航班因天氣不佳有延誤，其登機時間將由原訂10點延後至14點，是否還有其他想詢問？", True
    if "明天" in user_input and "CI108" in user_input and "取消" in user_input:
        return f"{tomorrow_date}的CI108航班因颱風因素已取消。是否還有其他想詢問？", True
    if "更改" in user_input and "訂位" in user_input and "機票" in user_input:
        return "可使用官網 管理行程/更改行程 網頁更改。是否還有其他想詢問？", True

    return "很抱歉，我無法回答您的問題，請稍後再試。", False

# 確認是否解決問題 (緊急模式)
def check_if_issue_resolved(user_input):
    print(f"使用者：{user_input}") 
    if ("有" in user_input and "沒有" not in user_input) or "是" in user_input:
        ask_satisfaction()
        return False
    elif "沒有" in user_input or "否" in user_input:
        response_text = "很抱歉未能解決您的問題，我們將會再次處理。請問還有其他問題嗎？"
        print(f"語航員：{response_text}")
        speak_response(response_text, response_mode)
        return True
    else:
        response_text = "抱歉，我無法確定問題是否解決。請問還有其他問題嗎？"
        print(f"語航員：{response_text}")
        speak_response(response_text, response_mode)
        return True

# 確認是否還有問題 
def check_more_questions(user_input):
    print(f"使用者：{user_input}") 
    if ("有" in user_input and "沒有" not in user_input) or "是" in user_input:
        response_text = "好的，請問您還有什麼問題？"
        print(f"語航員：{response_text}")
        speak_response(response_text, response_mode)
        return True
    elif "沒有" in user_input or "否" in user_input:
        ask_satisfaction()
        return False
    else:
        response_text = "很抱歉，我無法判斷您的回覆。請問是否還有其他問題？"
        print(f"語航員：{response_text}")
        speak_response(response_text, response_mode)
        return True

# 滿意度
def ask_satisfaction():
    response_text = "感謝您的回覆，請問您對於此次服務之滿意度1到5給幾分？"
    print(f"語航員：{response_text}")
    speak_response(response_text, response_mode)

# 語音設定調整
def adjust_speech_parameters(response_mode):
    if response_mode == "urgent":
        # 緊急模式
        ssml = """
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:lex='http://www.w3.org/2001/10/synthesis/lexicon'>
            <voice name="zh-TW-HsiaoChenNeural">
                <prosody rate="fats">緊急模式語音</prosody>
            </voice>
        </speak>
        """
    elif response_mode == "gentle":
        # 關懷模式
        ssml = """
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:lex='http://www.w3.org/2001/10/synthesis/lexicon'>
            <voice name="zh-TW-HsiaoChenNeural">
                <prosody rate="slow">關懷模式語音</prosody>
            </voice>
        </speak>
        """
    elif response_mode == "normal":
        # 一般模式
        ssml = """
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:lex='http://www.w3.org/2001/10/synthesis/lexicon'>
            <voice name="zh-TW-HsiaoChenNeural">
                <prosody rate="medium">正常語速語音</prosody>
            </voice>
        </speak>
        """
    return ssml

# 播放語音回應時，根據模式調整語音合成參數
def speak_response(response_text, response_mode):
    adjust_speech_parameters(response_mode)
    result = speech_synthesizer.speak_text_async(response_text).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("語音合成失敗：{}".format(result.reason))

# 開始互動
response_mode = "normal"  # 預設模式為一般模式

print("語航員：您好，請問您希望使用哪一種服務模式？1：一般模式，2：緊急模式，3：關懷模式。")
speak_response("您好，請問您希望使用哪一種服務模式？1：一般模式，2：緊急模式，3：關懷模式。", response_mode)

result = speech_recognizer.recognize_once()
if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    user_input = result.text
    print("使用者：{}".format(user_input))

    if "1" in user_input or "一" in user_input or "一般" in user_input:
        response_mode = "normal"
        print("語航員：已切換到一般模式。請問您有什麼問題？")
        speak_response("已切換到一般模式。請問您有什麼問題？", response_mode)
    elif "2" in user_input or "二" in user_input or "緊急" in user_input:
        response_mode = "urgent"
        print("語航員：已切換到緊急模式。請問您有什麼問題？")
        speak_response("已切換到緊急模式。請問您有什麼問題？", response_mode)
    elif "3" in user_input or "三" in user_input or "關懷" in user_input:
        response_mode = "gentle"
        print("語航員：已切換到關懷模式。請問您有什麼問題？")
        speak_response("已切換到關懷模式。請問您有什麼問題？", response_mode)
else:
    print("未能識別語音，將使用一般模式。請問您有什麼問題？")
    speak_response("未能識別語音，將使用普通模式。請問您有什麼問題？", response_mode)

while True:
    user_input_result = speech_recognizer.recognize_once()
    if user_input_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        user_input = user_input_result.text
        print("使用者：{}".format(user_input))

        response, handled = respond_to_query(user_input)
        print(f"語航員：{response}")
        speak_response(response, response_mode)

        if handled:
            if response_mode == "urgent":
                follow_up_result = speech_recognizer.recognize_once()
                if follow_up_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    follow_up_input = follow_up_result.text
                    if not check_if_issue_resolved(follow_up_input):
                        break
            else:
                follow_up_result = speech_recognizer.recognize_once()
                if follow_up_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    follow_up_input = follow_up_result.text
                    if not check_more_questions(follow_up_input):
                        break
    else:
        print("未能識別語音，請再試一次。")
        speak_response("抱歉，我沒有聽清楚，請再說一次。", response_mode)
