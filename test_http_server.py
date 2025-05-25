import requests
import json

if __name__ == "__main__":
    url = "http://localhost:8080"
    test_data = {
        "resolution": {
            "width": 1080,
            "height": 1920
        },
        "videoTracks": [
            {
                "trackName": "main_video_track",
                "segments": [
                    {
                        "range": {
                            "start": "0s",
                            "end": "10s"
                        },
                        "resourceUrl": "https://tweet-website.friday.ink/tweet/image/c2c8156fbd9341dbb8d3e37c667d5ed3~tplv-tb4s082cfz-aigc_resize_loss:720:720.webp",
                        "inAnimations": [{"name": "转圈圈"}],
                        "outAnimations": [],
                        "transition": "信号故障"
                    }
                ]
            }
        ],
        "audioTracks": [
            {
                "trackName": "main_audio_track",
                "segments": [
                    {
                        "range": {
                            "start": "0s",
                            "end": "10s"
                        },
                        "volume": 1,
                        "resourceUrl": "https://tweet-website.friday.ink/tweet/audio/1746083753347089831-264318147485874.mp3",
                        "effects": [
                            {
                                "fade": {
                                    "in": "0s",
                                    "out": "1s"
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "trackName": "background_audio_track",
                "segments": [
                    {
                        "range": {
                            "start": "0s",
                            "end": "10s"
                        },
                        "volume": 0.6,
                        "resourceUrl": "https://tweet-website.friday.ink/tweet/audio/1746083753347089831-264318147485874.mp3",
                        "effects": [
                            {
                                "fade": {
                                    "in": "0s",
                                    "out": "1s"
                                }
                            }
                        ]
                    }
                ]
            }
        ],
        "textTracks": [
            {
                "trackName": "main_text_track",
                "segments": [
                    {
                        "range": {
                            "start": "0s",
                            "end": "10s"
                        },
                        "text": "Hello, World!",
                        "font": "文轩体",
                        "style": {
                            "size": 24,
                            "color": [1.0, 1.0, 1.0]
                        },
                        "position": {"x": 1.0, "y": 1.0},
                        "inAnimations": [],
                        "outAnimations": [{"name": "故障闪动"}]
                    }
                ]
            }
        ]
    }

    # 发送 POST 请求测试
    try:
        response = requests.post(url, data=json.dumps(test_data))
        print("Response status code:", response.status_code)
        print("Response body:", response.text)
    except Exception as e:
        print("Error:", str(e))
