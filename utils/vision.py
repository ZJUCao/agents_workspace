import ollama

def analyze_image(image_path, model="llava"):
    response = ollama.generate(
        model=model,
        prompt="请描述图片中的核心需求信息：",
        images=[image_path]
    )
    return response['response']
