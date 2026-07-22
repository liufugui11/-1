"""
Netlify Function: API Handler
统一处理所有API请求，根据路径路由到对应处理函数
"""
import json
import os
import re
import sys


def _get_api_key():
    """获取大模型API密钥，优先DashScope，其次OpenAI"""
    dashscope_key = os.getenv("DASHSCOPE_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if dashscope_key and dashscope_key.strip():
        return ("dashscope", dashscope_key)
    if openai_key and openai_key.strip():
        return ("openai", openai_key)
    return ("mock", "")


def call_ai(prompt, system_prompt="", model="qwen-turbo"):
    """调用大模型API"""
    provider, api_key = _get_api_key()

    if provider == "dashscope":
        return _call_dashscope(prompt, system_prompt, api_key, model)
    elif provider == "openai":
        return _call_openai(prompt, system_prompt, api_key)
    else:
        return ""


def _call_dashscope(prompt, system_prompt, api_key, model="qwen-turbo"):
    import requests
    try:
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "input": {"messages": messages},
            "parameters": {"temperature": 0.7, "max_tokens": 4000}
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        return result.get("output", {}).get("text", "")
    except Exception as e:
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
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=4000
        )
        return resp.choices[0].message.content
    except Exception:
        return ""


# ========== Safety Video Service ==========

SAFETY_STYLE_ANCHORS = {
    "safety_realistic": "Industrial safety training video, photorealistic, high-quality 4K, professional documentary style, realistic factory environment, safety equipment visible, proper PPE, industrial lighting, cinematic camera work, clear visual hierarchy, no text overlays.",
    "safety_3d": "Industrial safety 3D animation, high-quality CGI rendering, realistic 3D factory environment, professional safety training visuals, clear safety equipment models, accurate PPE representations, clean modern industrial design, cinematic lighting, detailed textures, no text overlays, photorealistic rendering quality.",
    "safety_animation": "Industrial safety animated explainer, clean modern 2D/3D hybrid animation, professional safety training style, clear visual communication, safety icons and symbols, simplified industrial environment, bold colors for safety warnings, clear action sequences, engaging and informative, no text overlays.",
}


def generate_safety_script(topic, length="medium"):
    length_map = {"short": "30-60秒", "medium": "2-3分钟", "long": "5-10分钟"}
    system_prompt = "你是一名专业的安全生产培训内容编写师。请创建清晰、简洁、信息丰富的安全培训脚本。重点关注：安全操作流程、潜在危险和风险点、正确的个人防护装备使用、分步操作说明、真实场景案例。"
    prompt = f"""请为安全生产视频号创建一个关于"{topic}"的视频脚本。

要求：
- 时长：{length_map.get(length, "2-3分钟")}
- 语言：中文
- 风格：专业、严肃、教育性
- 包含5-8个场景
- 每个场景包含画面描述和旁白

主题：{topic}"""
    result = call_ai(prompt, system_prompt)
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
    system_prompt = "你是一名专业的视频分镜设计师。请将安全培训脚本转换为详细的视频分镜描述。每个分镜应包含：shot_number, description, visual_prompt, duration, camera_angle。"
    prompt = f"""请将以下安全培训脚本转换为视频分镜：

脚本内容：
{script}

风格要求：
{style_anchor}

请以JSON格式输出分镜列表。"""
    result = call_ai(prompt, system_prompt)
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
    copy_type_config = {
        "video_title": {"name": "视频标题", "description": "吸引人的标题，突出核心信息", "max_length": 50},
        "video_description": {"name": "视频简介", "description": "详细的视频描述", "max_length": 500},
        "hook": {"name": "开头钩子", "description": "3秒抓住注意力的开头文案", "max_length": 100},
        "cta": {"name": "引导语", "description": "关注点赞评论的引导文案", "max_length": 100},
        "hashtag": {"name": "话题标签", "description": "5-10个相关热门话题标签", "max_length": 200},
        "full_copy": {"name": "完整文案", "description": "一站式全案创作", "max_length": 1000},
    }
    platform_config = {
        "video_channel": {"name": "微信视频号", "style": "专业、可信、有深度"},
        "douyin": {"name": "抖音", "style": "快节奏、强冲击力、口语化"},
        "kuaishou": {"name": "快手", "style": "接地气、真实、亲切"},
        "xiaohongshu": {"name": "小红书", "style": "种草风、干货满满、精致"},
        "bilibili": {"name": "哔哩哔哩", "style": "二次元、梗多、专业深度"},
    }
    tc = copy_type_config.get(copy_type, copy_type_config["video_title"])
    pc = platform_config.get(platform, platform_config["video_channel"])

    system_prompt = "你是一名专业的短视频文案策划师，精通各平台内容运营。"
    prompt = f"""请为以下安全生产视频内容创作{tc['name']}：

视频内容/主题：
{content}

创作要求：
- 文案类型：{tc['name']}
- 类型说明：{tc['description']}
- 目标平台：{pc['name']}
- 平台风格：{pc['style']}
- 字数限制：约{tc['max_length']}字
- 主题：安全生产相关

请直接输出文案内容。"""
    result = call_ai(prompt, system_prompt)
    if result:
        return result
    # Mock fallback
    mock_map = {
        "video_title": f"【安全生产】{content}必知的5个安全要点！",
        "video_description": f"本期视频详细讲解{content}的安全操作规范。\n\n#安全生产 #安全培训",
        "hook": f"90%的安全事故都可以避免！这5个{content}要点一定要记牢！",
        "cta": "觉得有用的话，点赞关注不迷路！评论区告诉我你想了解的安全知识！",
        "hashtag": f"#安全生产 #安全培训 #安全第一 #生命至上",
        "full_copy": f"【安全生产警示】{content}这些要点必须牢记！\n\n安全无小事，生命大于天！\n\n#安全生产 #安全培训",
    }
    return mock_map.get(copy_type, mock_map["full_copy"])


def generate_distribution_caption(script, platform="video_channel"):
    platform_config = {
        "video_channel": {"name": "视频号", "style": "简洁有力，带话题标签"},
        "douyin": {"name": "抖音", "style": "活泼有趣，带热门话题"},
        "kuaishou": {"name": "快手", "style": "接地气，口语化"},
    }
    config = platform_config.get(platform, platform_config["video_channel"])
    system_prompt = "你是一名短视频运营专家。请根据安全培训脚本生成适合各平台的分发文案。"
    prompt = f"""请为以下安全培训脚本生成适合{config['name']}的分发文案：

脚本内容：{script}

要求：平台{config['name']}，风格{config['style']}，包含话题标签。"""
    result = call_ai(prompt, system_prompt)
    if result:
        return result
    return f"【安全生产警示】安全要点必须牢记！\n\n#安全生产 #安全培训"


# ========== Video Remix Service ==========

def extract_video_url_info(url):
    youtube_patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/|v\/|watch\?v=|watch\?.+&v=)([^&?#]+)',
        r'(?:youtu\.be\/)([^?#]+)'
    ]
    for pattern in youtube_patterns:
        match = re.search(pattern, url)
        if match:
            return {"platform": "youtube", "video_id": match.group(1), "url": url}
    if "bilibili" in url or "b23.tv" in url:
        return {"platform": "bilibili", "video_id": "", "url": url}
    if "douyin" in url or "iesdouyin" in url:
        return {"platform": "douyin", "video_id": "", "url": url}
    return {"platform": "unknown", "video_id": "", "url": url}


def get_youtube_transcript(video_url):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/|v\/|watch\?v=|watch\?.+&v=)([^&?#]+)',
            r'(?:youtu\.be\/)([^?#]+)'
        ]
        video_id = None
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                video_id = match.group(1)
                break
        if not video_id:
            return None

        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        try:
            transcript = transcript_list.find_transcript(['en', 'zh', 'zh-CN', 'zh-TW'])
        except:
            try:
                transcript = next(iter(transcript_list))
            except:
                return None
        transcript_data = transcript.fetch()
        full_text = " ".join([snippet.text for snippet in transcript_data])
        cleaned = re.sub(r'\s*\[[^\]]+\]\s*', ' ', full_text)
        return ' '.join(cleaned.split())
    except Exception:
        return None


def analyze_video_for_remix(video_script, source_type="youtube"):
    system_prompt = "你是一名专业的视频内容分析师和二次创作专家。"
    prompt = f"""请分析以下视频内容，提供详细的二次创作方案：

视频来源：{source_type}
视频内容：{video_script}

请提供JSON格式：
1. summary: 内容摘要
2. key_points: 核心知识点列表
3. remix_suggestions: 二次创作建议
4. new_topics: 可衍生的新话题
5. hook_suggestions: 吸引人的开头建议"""
    result = call_ai(prompt, system_prompt)
    try:
        return json.loads(result)
    except:
        return {
            "summary": "视频内容主要讲述安全生产相关知识。",
            "key_points": ["安全防护", "操作规范", "应急处置", "设备检查", "安全意识"],
            "remix_suggestions": ["制作快节奏短视频版本", "添加3D动画演示", "结合真实案例"],
            "new_topics": ["高处作业", "消防安全", "电气安全", "机械安全", "化学品安全"],
            "hook_suggestions": ["事故现场震撼开场", "数据统计警示"],
            "distribution_tips": ["突出关键词", "添加话题标签"]
        }


def remix_video_script(original_script, remix_type="short"):
    remix_config = {
        "short": {"name": "短视频版", "duration": "30-60秒", "style": "快节奏、强节奏、重点突出"},
        "deep_dive": {"name": "深度解读版", "duration": "5-8分钟", "style": "详细分析、案例丰富"},
        "animation": {"name": "动画演示版", "duration": "2-3分钟", "style": "3D动画演示、生动形象"},
        "case_study": {"name": "案例分析版", "duration": "3-5分钟", "style": "真实案例、事故还原"},
    }
    config = remix_config.get(remix_type, remix_config["short"])
    system_prompt = "你是一名专业的视频脚本改编专家。"
    prompt = f"""请根据以下原始视频内容，重新创作一个{config['name']}的脚本：

原始内容：{original_script}

创作要求：
- 版本：{config['name']}
- 时长：{config['duration']}
- 风格：{config['style']}
- 保留核心知识点，用全新表达方式
- 适合安全生产视频号发布
- 包含画面描述和旁白"""
    result = call_ai(prompt, system_prompt)
    if result:
        return result
    return f"【二创版本：{config['name']}】\n\n{original_script}\n\n（已根据{config['name']}类型重新编排内容结构）"


# ========== Route Handler ==========

def handler(event, context):
    """Netlify Function 主处理器"""
    path = event.get("path", "")
    method = event.get("httpMethod", "GET")

    # CORS preflight
    if method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": "",
        }

    # Parse body
    try:
        body = json.loads(event.get("body", "{}")) if event.get("body") else {}
    except:
        body = {}

    # Route API calls
    try:
        if path.endswith("/api/safety/generate-script"):
            topic = body.get("topic", "").strip()
            length = body.get("length", "medium")
            if not topic:
                return _json_error("请输入安全主题", 400)
            script = generate_safety_script(topic, length)
            return _json_ok({"script": script})

        elif path.endswith("/api/safety/generate-storyboard"):
            script = body.get("script", "").strip()
            style = body.get("style", "safety_realistic")
            if not script:
                return _json_error("请输入脚本内容", 400)
            storyboard = generate_safety_storyboard(script, style)
            return _json_ok({"storyboard": storyboard})

        elif path.endswith("/api/safety/analyze"):
            script = body.get("script", "").strip()
            if not script:
                return _json_error("请输入脚本内容", 400)
            return _json_ok({"analysis": {"safety_topics": ["安全生产"], "risk_level": "medium"}})

        elif path.endswith("/api/safety/generate-caption"):
            script = body.get("script", "").strip()
            platform = body.get("platform", "video_channel")
            if not script:
                return _json_error("请输入脚本内容", 400)
            caption = generate_distribution_caption(script, platform)
            return _json_ok({"caption": caption})

        elif path.endswith("/api/copywriting/generate"):
            content = body.get("content", "").strip()
            copy_type = body.get("copy_type", "video_title")
            platform = body.get("platform", "video_channel")
            if not content:
                return _json_error("请输入创作内容或主题", 400)
            if copy_type == "full_copy":
                types = ["video_title", "video_description", "hook", "cta", "hashtag"]
                result = {t: generate_copywriting(content, t, platform) for t in types}
                return _json_ok({"result": result})
            else:
                copy = generate_copywriting(content, copy_type, platform)
                return _json_ok({"copy": copy})

        elif path.endswith("/api/remix/extract-url"):
            url = body.get("url", "").strip()
            if not url:
                return _json_error("请输入视频链接", 400)
            info = extract_video_url_info(url)
            return _json_ok({"info": info})

        elif path.endswith("/api/remix/get-transcript"):
            url = body.get("url", "").strip()
            if not url:
                return _json_error("请输入视频链接", 400)
            transcript = get_youtube_transcript(url)
            if transcript:
                return _json_ok({"transcript": transcript})
            return _json_error("无法获取视频字幕，请手动输入视频内容")

        elif path.endswith("/api/remix/analyze"):
            script = body.get("script", "").strip()
            if not script:
                return _json_error("请输入视频内容", 400)
            analysis = analyze_video_for_remix(script)
            return _json_ok({"analysis": analysis})

        elif path.endswith("/api/remix/generate-script"):
            script = body.get("script", "").strip()
            remix_type = body.get("remix_type", "short")
            if not script:
                return _json_error("请输入原始视频内容", 400)
            new_script = remix_video_script(script, remix_type)
            return _json_ok({"script": new_script})

        elif path.endswith("/api/remix/generate-storyboard"):
            script = body.get("script", "").strip()
            style = body.get("style", "safety_realistic")
            if not script:
                return _json_error("请输入脚本内容", 400)
            storyboard = generate_safety_storyboard(script, style)
            return _json_ok({"storyboard": storyboard})

        elif path.endswith("/api/remix/generate-captions"):
            script = body.get("script", "").strip()
            if not script:
                return _json_error("请输入脚本内容", 400)
            platforms = ["video_channel", "douyin", "kuaishou"]
            captions = {p: generate_distribution_caption(script, p) for p in platforms}
            return _json_ok({"captions": captions})

        else:
            return _json_error(f"Unknown API path: {path}", 404)

    except Exception as e:
        return _json_error(str(e), 500)


def _json_ok(data):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"success": True, **data}, ensure_ascii=False),
    }


def _json_error(msg, code=400):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps({"success": False, "error": msg}, ensure_ascii=False),
    }
