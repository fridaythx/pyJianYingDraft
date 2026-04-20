from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import pyJianYingDraft as draft
from pyJianYingDraft import Intro_type, Outro_type, Transition_type, trange, tim
import requests
import zipfile
from urllib.parse import urlparse
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()


def timerange_from_payload(range_payload):
    start = range_payload["start"]
    if "duration" in range_payload:
        timerange = trange(start, range_payload["duration"])
    elif "end" in range_payload:
        timerange = draft.Timerange(tim(start), tim(range_payload["end"]) - tim(start))
    else:
        raise KeyError("range must include either 'duration' or 'end'")
    if timerange.duration < 0:
        raise ValueError("range end must be greater than or equal to start")
    return timerange


def text_from_payload(segment):
    text = segment["text"]
    prefix = segment.get("textPrefix", segment.get("speaker", ""))
    if prefix and not prefix.endswith((":", "：")):
        prefix = f"{prefix}："
    return f"{prefix}{text}"


class SimpleHandler(BaseHTTPRequestHandler):
    # 生成的草稿文件路径
    draft_path = os.path.join(os.path.dirname(__file__), "draft_content.json")
    # 默认的草稿zip文件路径
    draft_zip_path = os.getenv("DRAFT_ZIP_SAVE_PATH", os.path.dirname(__file__))
    # 最终替换的资源目录
    resource_dir = os.getenv("DRAFT_RESOURCE_DIR_PATH",  r'/Volumes/ftp')
    # 从本地下载文件时的路径前缀，指向ftp目录
    local_download_prefix = os.getenv("LOCAL_DOWNLOAD_PREFIX", r'/Volumes/ftp')

    def do_POST(self):
        if self.path != "/jianying-draft/generate":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

        length = int(self.headers.get('Content-Length'))
        raw_data = self.rfile.read(length)
        params = json.loads(raw_data.decode('utf-8'))

        self.generate_draft(params)
        zip_file_path = self.zip_files(params)

        # 返回 ZIP 文件作为响应
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')  # 允许所有来源
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')  # 允许的 HTTP 方法
        self.send_header('Access-Control-Allow-Headers', '*')  # 允许的请求头
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        print(f"Draft file saved to {zip_file_path}")

        self.wfile.write(json.dumps({
            "filePath": zip_file_path
        }).encode('utf-8'))

    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def download_file(self, url):
        if url.startswith("http"):
            download_dir = os.path.join(os.path.dirname(__file__), 'downloads')
            os.makedirs(download_dir, exist_ok=True)
            parsed_url = urlparse(url)
            path = parsed_url.path
            # 去除第一个/
            path = path[1:] if path.startswith("/") else path
            local_path = os.path.join(download_dir, path)
            print(f"Downloading file from {url} to {local_path}")
            # 获取文件的上级目录
            parent_dir = os.path.dirname(local_path)
            # 如果目录不存在，则创建
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)

            if not os.path.exists(local_path):
                resp = requests.get(url)
                with open(local_path, "wb") as f:
                    f.write(resp.content)
            return local_path
        return url

    def download_file_from_local(self, remote_path):
        download_dir = os.path.join(os.path.dirname(__file__), 'downloads')
        os.makedirs(download_dir, exist_ok=True)
        # 去除第一个/
        path = remote_path[1:] if remote_path.startswith("/") else remote_path
        download_path = os.path.join(self.local_download_prefix, path)
        local_path = os.path.join(download_dir, path)
        print(f"Downloading file from {download_path} to {local_path}")
        # 获取文件的上级目录
        parent_dir = os.path.dirname(local_path)
        # 如果目录不存在，则创建
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        should_copy = not os.path.exists(local_path)
        if not should_copy:
            should_copy = os.path.getsize(local_path) == 0 or os.path.getsize(local_path) != os.path.getsize(download_path)

        if should_copy:
            with open(download_path, "rb") as src_file:
                with open(local_path, "wb") as dest_file:
                    dest_file.write(src_file.read())
        return local_path

    def generate_draft(self, params):
        resolution = params.get("resolution", {"width": 1920, "height": 1080})
        script = draft.Script_file(resolution["width"], resolution["height"])

        # 处理 videoTracks
        for vtrack in params.get("videoTracks", []):
            vtrack_name = vtrack.get("trackName", "main_video_track")
            script.add_track(draft.Track_type.video, vtrack_name)
            for seg in vtrack.get("segments", []):
                # video_material = draft.Video_material(self.download_file(seg["resourceUrl"]))
                video_material = draft.Video_material(self.download_file_from_local(seg["resourcePath"]))

                video_segment = draft.Video_segment(
                    video_material,
                    timerange_from_payload(seg["range"])
                )
                for anim in seg.get("inAnimations", []):
                    in_animation = getattr(Intro_type, anim["name"], None)
                    if in_animation:
                        video_segment.add_animation(in_animation, duration=tim(anim.get("duration", "0s")))
                for anim in seg.get("outAnimations", []):
                    out_animation = getattr(Outro_type, anim["name"], None)
                    if out_animation:
                        video_segment.add_animation(out_animation, duration=tim(anim.get("duration", "0s")))
                if seg.get("transition"):
                    transition = getattr(Transition_type, seg["transition"], None)
                    if transition:
                        video_segment.add_transition(transition)
                script.add_segment(video_segment, track_name=vtrack_name)
        # 处理 audioTracks
        for atrack in params.get("audioTracks", []):
            atrack_name = atrack.get("trackName", "main_audio_track")
            script.add_track(draft.Track_type.audio, atrack_name)
            for seg in atrack.get("segments", []):
                # audio_material = draft.Audio_material(self.download_file(seg["resourceUrl"]))
                audio_material = draft.Audio_material(self.download_file_from_local(seg["resourcePath"]))
                audio_segment = draft.Audio_segment(
                    audio_material,
                    timerange_from_payload(seg["range"]),
                    volume=seg.get("volume", 1)
                )
                for fx in seg.get("effects", []):
                    fade_conf = fx.get("fade", {})
                    if fade_conf:
                        audio_segment.add_fade(fade_conf.get("in", "0s"), fade_conf.get("out", "0s"))
                script.add_segment(audio_segment, track_name=atrack_name)
        # 处理 textTracks
        for ttrack in params.get("textTracks", []):
            ttrack_name = ttrack.get("trackName", "main_text_track")
            script.add_track(draft.Track_type.text, ttrack_name)
            for seg in ttrack.get("segments", []):
                text = text_from_payload(seg)
                # 将字符串每18个字符分成一段
                if len(text) > 18:
                    text = "\n".join([text[i:i + 18] for i in range(0, len(text), 18)])
                txt_segment = draft.Text_segment(
                    text,
                    timerange_from_payload(seg["range"]),
                    font=getattr(draft.Font_type, seg.get("font", ""), draft.Font_type.文轩体),
                    style=draft.Text_style(color=tuple(seg["style"].get("color", [1.0, 1.0, 1.0]))),
                    border=draft.Text_border(
                        alpha=seg["border"].get("alpha", 1.0),
                        color=tuple(seg["border"].get("color", [0.0, 0.0, 0.0])),
                        width=seg["border"].get("width", 0.0)
                    ),
                    background=draft.Text_background(
                        color=seg["background"].get("color", "#000000"),
                        alpha=seg["background"].get("alpha", 1.0),
                        round_radius=seg["background"].get("radius", 0.0)
                    ),
                    clip_settings=draft.Clip_settings(
                        transform_x=seg.get("position", {}).get("x", 0.0),
                        transform_y=seg.get("position", {}).get("y", 0.0)
                    )
                )
                for anim in seg.get("inAnimations", []):
                    in_animation = getattr(draft.Text_intro, anim["name"], None)
                    if in_animation:
                        txt_segment.add_animation(in_animation, duration=tim(anim.get("duration", "0s")))
                for anim in seg.get("outAnimations", []):
                    out_animation = getattr(draft.Text_outro, anim["name"], None)
                    if out_animation:
                        txt_segment.add_animation(out_animation, duration=tim(anim.get("duration", "0s")))
                script.add_segment(txt_segment, track_name=ttrack_name)
        # 保存草稿
        script.dump(self.draft_path)
        self.replace_resource_paths()

    def replace_resource_paths(self):
        with open(self.draft_path, "r", encoding="utf-8") as f:
            content = f.read()
            downloads_dir = os.path.join(os.path.dirname(__file__), "downloads")
            # 替换资源路径
            content = content.replace(downloads_dir, self.resource_dir)
            # 写入文件
            with open(self.draft_path, "w", encoding="utf-8") as f:
                f.write(content)

    def zip_files(self, params):
        draft_name = params.get("draftName")
        draft_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_name = f"{draft_name}{draft_datetime}.zip"
        draft_file_path = os.path.join(self.draft_zip_path, draft_name)
        # 创建 ZIP 文件
        with zipfile.ZipFile(draft_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(self.draft_path, os.path.basename(self.draft_path))
        return draft_file_path


def run_server(port=8082):
    httpd = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"HTTP Server running on port {port}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
