"""
Vercel Python Serverless Function
统一处理所有 API 请求
"""
import json
import os
import re
from http.server import BaseHTTPRequestHandler


# ========== AI Service ==========

def _get_api_key():
    dashscope_key = os.getenv("DASHSCOPE_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if dashscope_key and dashscope_key.strip():
        return ("dashscope", dashscope_key)
    if openai_key and openai_key.strip():
        return ("openai", openai_key)
    return ("mock", "")


def call_ai(prompt, system_prompt=""):
    provider, api_key = _get_api_key()
    if provider == "dashscope":
        return _call_dashscope(prompt, system_prompt, api_key)
    elif provider == "openai":
        return _call_openai(prompt, system_prompt, api_key)
    return ""


def _call_dashscope(prompt, system_prompt, api_key):
    import requests
    try:
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": "qwen-turbo",
            "input": {"messages": messages},
            "parameters": {"temperature": 0.7, "max_tokens": 4000}
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json().get("output", {}).get("text", "")
    except:
        return ""


def _call_openai(prompt, system_prompt, api_key):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, temperature=0.7, max_tokens=4000
        )
        return resp.choices[0].message.content
    except:
        return ""


# ========== Safety Video Service ==========

SAFETY_STYLE_ANCHORS = {
    "safety_realistic": "Industrial safety training video, photorealistic, high-quality 4K, professional documentary style, realistic factory environment, safety equipment visible, proper PPE, industrial lighting, cinematic camera work, no text overlays.",
    "safety_3d": "Industrial safety 3D animation, high-quality CGI rendering, realistic 3D factory environment, professional safety training visuals, clear safety equipment models, cinematic lighting, detailed textures, photorealistic rendering quality.",
    "safety_animation": "Industrial safety animated explainer, clean modern 2D/3D hybrid animation, professional safety training style, safety icons and symbols, bold colors for safety warnings, engaging and informative.",
}


def generate_safety_script(topic, length="medium"):
    length_map = {"short": "30-60秒", "medium": "2-3分钟", "long": "5-10分钟"}
    sys_prompt = "你是一名专业的安全生产培训内容编写师。请创建清晰、简洁、信息丰富的安全培训脚本。"
    prompt = f"""请为安全生产视频号创建一个关于"{topic}"的视频脚本。

要求：
- 时长：{length_map.get(length, "2-3分钟")}
- 语言：中文
- 风格：专业、严肃、教育性
- 包含5-8个场景，每个场景包含画面描述和旁白

主题：{topic}"""
    result = call_ai(prompt, sys_prompt)
    if result:
        return result
    return f"""【安全生产培训脚本：{topic}】

场景一：事故警示（10秒）
画面：事故现场，警示灯闪烁
旁白："安全生产，警钟长鸣。每年因安全事故造成的伤亡触目惊心。"

场景二：安全准备（25秒）
画面：工人穿戴安全装备，检查设备
旁白："进行作业前，必须正确佩戴个人防护装备，认真检查设备状态。"

场景三：作业过程（30秒）
画面：工人规范作业，安全监护人员在场
旁白："作业过程中，严格遵守操作规程，严禁违规操作，发现隐患立即制止。"

场景四：应急处置（20秒）
画面：模拟意外情况，工人正确处置
旁白："如发生意外，保持冷静，正确使用应急设备，及时上报。"

场景五：总结提醒（15秒）
画面：安全标语，工人整齐站立
旁白："安全第一，预防为主。让我们共同遵守安全规定，守护生命安全。"
"""


def generate_safety_storyboard(script, style="safety_realistic"):
    style_anchor = SAFETY_STYLE_ANCHORS.get(style, SAFETY_STYLE_ANCHORS["safety_realistic"])
    sys_prompt = "你是一名专业的视频分镜设计师。请将安全培训脚本转换为视频分镜描述。每个分镜包含：shot_number, description, visual_prompt, duration, camera_angle。"
    prompt = f"""请将以下安全培训脚本转换为视频分镜：

脚本内容：{script}

风格要求：{style_anchor}

请以JSON格式输出分镜列表。"""
    result = call_ai(prompt, sys_prompt)
    try:
        return json.loads(result)
    except:
        return [
            {"shot_number": 1, "description": "安全生产警示画面", "visual_prompt": f"{style_anchor} Industrial safety warning scene", "duration": "5s", "camera_angle": "wide"},
            {"shot_number": 2, "description": "安全操作演示", "visual_prompt": f"{style_anchor} Safety operation demonstration", "duration": "8s", "camera_angle": "medium"},
            {"shot_number": 3, "description": "工人佩戴防护装备", "visual_prompt": f"{style_anchor} Worker wearing PPE equipment", "duration": "6s", "camera_angle": "close-up"},
            {"shot_number": 4, "description": "设备检查场景", "visual_prompt": f"{style_anchor} Equipment inspection scene", "duration": "7s", "camera_angle": "medium"},
            {"shot_number": 5, "description": "安全总结", "visual_prompt": f"{style_anchor} Safety conclusion scene", "duration": "5s", "camera_angle": "wide"},
        ]


def generate_copywriting(content, copy_type="video_title", platform="video_channel"):
    type_cfg = {
        "video_title": {"name": "视频标题", "desc": "吸引人的标题", "max": 50},
        "video_description": {"name": "视频简介", "desc": "详细的视频描述", "max": 500},
        "hook": {"name": "开头钩子", "desc": "3秒抓住注意力", "max": 100},
        "cta": {"name": "引导语", "desc": "关注点赞评论引导", "max": 100},
        "hashtag": {"name": "话题标签", "desc": "热门话题标签", "max": 200},
        "full_copy": {"name": "完整文案", "desc": "一站式全案创作", "max": 1000},
    }
    plat_cfg = {
        "video_channel": "微信视频号 - 专业、可信、有深度",
        "douyin": "抖音 - 快节奏、强冲击力、口语化",
        "kuaishou": "快手 - 接地气、真实、亲切",
        "xiaohongshu": "小红书 - 种草风、干货满满",
        "bilibili": "哔哩哔哩 - 专业深度",
    }
    tc = type_cfg.get(copy_type, type_cfg["video_title"])
    pc = plat_cfg.get(platform, plat_cfg["video_channel"])
    sys_prompt = "你是一名专业的短视频文案策划师，精通各平台内容运营。"
    prompt = f"""请为以下安全生产视频内容创作{tc['name']}：

视频内容/主题：{content}

创作要求：
- 文案类型：{tc['name']}（{tc['desc']}）
- 目标平台：{pc}
- 字数限制：约{tc['max']}字
- 主题：安全生产相关

请直接输出文案内容。"""
    result = call_ai(prompt, sys_prompt)
    if result:
        return result
    mocks = {
        "video_title": f"【安全生产】{content}必知的5个安全要点！",
        "video_description": f"本期视频详细讲解{content}的安全操作规范。\n\n#安全生产 #安全培训",
        "hook": f"90%的安全事故都可以避免！这5个{content}要点一定要记牢！",
        "cta": "觉得有用的话，点赞关注不迷路！评论区告诉我你想了解的安全知识！",
        "hashtag": "#安全生产 #安全培训 #安全第一 #生命至上",
        "full_copy": f"【安全生产警示】{content}这些要点必须牢记！\n\n安全无小事，生命大于天！\n\n#安全生产 #安全培训",
    }
    return mocks.get(copy_type, mocks["full_copy"])


def generate_distribution_caption(script, platform="video_channel"):
    plat_map = {
        "video_channel": "视频号",
        "douyin": "抖音",
        "kuaishou": "快手",
        "xiaohongshu": "小红书",
    }
    plat_name = plat_map.get(platform, "视频号")
    sys_prompt = "你是一名短视频运营专家。"
    prompt = f"请为以下安全培训脚本生成适合{plat_name}的分发文案，包含话题标签：\n\n{script}"
    result = call_ai(prompt, sys_prompt)
    if result:
        return result
    return f"【安全生产警示】安全要点必须牢记！\n\n#安全生产 #安全培训"


# ========== Video Remix Service ==========

def extract_video_url_info(url):
    for pattern in [r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', r'(?:embed\/|v\/|watch\?v=|watch\?.+&v=)([^&?#]+)', r'(?:youtu\.be\/)([^?#]+)']:
        m = re.search(pattern, url)
        if m:
            return {"platform": "youtube", "video_id": m.group(1), "url": url}
    if "bilibili" in url or "b23.tv" in url:
        return {"platform": "bilibili", "video_id": "", "url": url}
    if "douyin" in url or "iesdouyin" in url:
        return {"platform": "douyin", "video_id": "", "url": url}
    return {"platform": "unknown", "video_id": "", "url": url}


def get_youtube_transcript(video_url):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        video_id = None
        for pattern in [r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', r'(?:youtu\.be\/)([^?#]+)']:
            m = re.search(pattern, video_url)
            if m:
                video_id = m.group(1)
                break
        if not video_id:
            return None
        api = YouTubeTranscriptApi()
        tl = api.list(video_id)
        try:
            t = tl.find_transcript(['en', 'zh', 'zh-CN'])
        except:
            try:
                t = next(iter(tl))
            except:
                return None
        data = t.fetch()
        text = " ".join([s.text for s in data])
        return ' '.join(re.sub(r'\s*\[[^\]]+\]\s*', ' ', text).split())
    except:
        return None


def analyze_video_for_remix(video_script):
    sys_prompt = "你是一名专业的视频内容分析师和二次创作专家。"
    prompt = f"""请分析以下视频内容，提供JSON格式的二次创作方案：
视频内容：{video_script}

请提供：summary, key_points, remix_suggestions, new_topics, hook_suggestions"""
    result = call_ai(prompt, sys_prompt)
    try:
        return json.loads(result)
    except:
        return {
            "summary": "视频内容主要讲述安全生产相关知识。",
            "key_points": ["安全防护", "操作规范", "应急处置", "设备检查", "安全意识"],
            "remix_suggestions": ["制作快节奏短视频版本", "添加3D动画演示", "结合真实案例"],
            "new_topics": ["高处作业", "消防安全", "电气安全", "机械安全", "化学品安全"],
            "hook_suggestions": ["事故现场震撼开场", "数据统计警示"],
        }


def remix_video_script(original_script, remix_type="short"):
    cfg = {
        "short": {"name": "短视频版", "duration": "30-60秒", "style": "快节奏、重点突出"},
        "deep_dive": {"name": "深度解读版", "duration": "5-8分钟", "style": "详细分析、案例丰富"},
        "animation": {"name": "动画演示版", "duration": "2-3分钟", "style": "3D动画演示"},
        "case_study": {"name": "案例分析版", "duration": "3-5分钟", "style": "真实案例、事故还原"},
    }
    c = cfg.get(remix_type, cfg["short"])
    sys_prompt = "你是一名专业的视频脚本改编专家。"
    prompt = f"""请根据以下原始视频内容，重新创作一个{c['name']}的脚本：

原始内容：{original_script}

创作要求：版本{c['name']}，时长{c['duration']}，风格{c['style']}。保留核心知识点，用全新表达方式。包含画面描述和旁白。"""
    result = call_ai(prompt, sys_prompt)
    if result:
        return result
    return f"【二创版本：{c['name']}】\n\n{original_script}\n\n（已根据{c['name']}类型重新编排内容结构）"


# ========== Route Handler ==========

def handle_api(path, body):
    """Route API requests to appropriate handlers"""
    if path.endswith("/api/safety/generate-script") or path.endswith("/safety/generate-script"):
        topic = body.get("topic", "").strip()
        length = body.get("length", "medium")
        if not topic:
            return _err("请输入安全主题", 400)
        return _ok({"script": generate_safety_script(topic, length)})

    elif path.endswith("/api/safety/generate-storyboard") or path.endswith("/safety/generate-storyboard"):
        script = body.get("script", "").strip()
        style = body.get("style", "safety_realistic")
        if not script:
            return _err("请输入脚本内容", 400)
        return _ok({"storyboard": generate_safety_storyboard(script, style)})

    elif path.endswith("/api/safety/analyze") or path.endswith("/safety/analyze"):
        script = body.get("script", "").strip()
        if not script:
            return _err("请输入脚本内容", 400)
        return _ok({"analysis": {"safety_topics": ["安全生产"], "risk_level": "medium"}})

    elif path.endswith("/api/safety/generate-caption") or path.endswith("/safety/generate-caption"):
        script = body.get("script", "").strip()
        platform = body.get("platform", "video_channel")
        if not script:
            return _err("请输入脚本内容", 400)
        return _ok({"caption": generate_distribution_caption(script, platform)})

    elif path.endswith("/api/copywriting/generate") or path.endswith("/copywriting/generate"):
        content = body.get("content", "").strip()
        copy_type = body.get("copy_type", "video_title")
        platform = body.get("platform", "video_channel")
        if not content:
            return _err("请输入创作内容或主题", 400)
        if copy_type == "full_copy":
            types = ["video_title", "video_description", "hook", "cta", "hashtag"]
            result = {t: generate_copywriting(content, t, platform) for t in types}
            return _ok({"result": result})
        else:
            return _ok({"copy": generate_copywriting(content, copy_type, platform)})

    elif path.endswith("/api/remix/extract-url") or path.endswith("/remix/extract-url"):
        url = body.get("url", "").strip()
        if not url:
            return _err("请输入视频链接", 400)
        return _ok({"info": extract_video_url_info(url)})

    elif path.endswith("/api/remix/get-transcript") or path.endswith("/remix/get-transcript"):
        url = body.get("url", "").strip()
        if not url:
            return _err("请输入视频链接", 400)
        t = get_youtube_transcript(url)
        if t:
            return _ok({"transcript": t})
        return _err("无法获取视频字幕，请手动输入视频内容")

    elif path.endswith("/api/remix/analyze") or path.endswith("/remix/analyze"):
        script = body.get("script", "").strip()
        if not script:
            return _err("请输入视频内容", 400)
        return _ok({"analysis": analyze_video_for_remix(script)})

    elif path.endswith("/api/remix/generate-script") or path.endswith("/remix/generate-script"):
        script = body.get("script", "").strip()
        remix_type = body.get("remix_type", "short")
        if not script:
            return _err("请输入原始视频内容", 400)
        return _ok({"script": remix_video_script(script, remix_type)})

    elif path.endswith("/api/remix/generate-storyboard") or path.endswith("/remix/generate-storyboard"):
        script = body.get("script", "").strip()
        style = body.get("style", "safety_realistic")
        if not script:
            return _err("请输入脚本内容", 400)
        return _ok({"storyboard": generate_safety_storyboard(script, style)})

    elif path.endswith("/api/remix/generate-captions") or path.endswith("/remix/generate-captions"):
        script = body.get("script", "").strip()
        if not script:
            return _err("请输入脚本内容", 400)
        platforms = ["video_channel", "douyin", "kuaishou"]
        captions = {p: generate_distribution_caption(script, p) for p in platforms}
        return _ok({"captions": captions})

    else:
        return _err(f"Unknown API path: {path}", 404)


def _ok(data):
    return {"success": True, **data}


def _err(msg, code=400):
    return {"success": False, "error": msg, "_code": code}


# ========== Vercel Handler ==========

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self._send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "message": "Safety Video Studio API"}, ensure_ascii=False).encode())

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body_str = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'

        try:
            body = json.loads(body_str)
        except:
            body = {}

        path = self.path or ""
        result = handle_api(path, body)
        status_code = result.pop('_code', 200)

        self.send_response(status_code)
        self._send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode())

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, format, *args):
        pass
