import requests

# IPTV源列表
urls = [
    "https://gh.999986.xyz/https://raw.githubusercontent.com/fanmingming/live/master/tv/m3u/ipv6.m3u",
    "https://gh.999986.xyz/https://raw.githubusercontent.com/YanG-1989/m3u/master/Gather.m3u",
    "https://gh.999986.xyz/https://raw.githubusercontent.com/YueChan/live/master/APTV.m3u",
    "https://gh.999986.xyz/https://raw.githubusercontent.com/YueChan/live/master/Global.m3u",
    "https://raw.githubusercontent.com/387673116/Tvbox/master/other/jingqu.m3u",
    "https://raw.githubusercontent.com/yoursmile66/TVBox/main/live.txt"
]

# 输出文件路径
output_file = "iptv6.txt"

# 需要删除的关键词列表
exclude_keywords = ["咪咕", "轮播", "解说", "炫舞", "埋堆堆", "斗鱼", "虎牙", "B站"]

def fetch_url_content(url):
    """从指定URL获取内容"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        return response.text
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None

def format_category(category):
    """如果分类包含 '频道'，删除 '频道' 两个字"""
    return category.replace("频道", "") if "频道" in category else category

def clean_line(line):
    """删除符号•、‘IPV6’关键字和‘「」’符号，并检查是否包含排除的关键词"""
    # 删除符号•、‘IPV6’关键字和‘「」’符号
    line = line.replace("•", "").replace("IPV6", "").replace("「", "").replace("」", "")
    
    # 检查是否包含需要排除的关键词
    for keyword in exclude_keywords:
        if keyword in line:
            return None  # 如果包含排除关键词，返回None表示该行应删除
    
    return line

def format_and_merge_sources(urls, output_file):
    """将多个IPTV源内容合并为自定义txt格式"""
    with open(output_file, "w", encoding="utf-8") as outfile:
        last_category = None  # 用于存储最后一次的分类，避免重复输出
        category_channels = {}  # 用于存储每个分类的所有频道及其播放链接

        for url in urls:
            print(f"正在处理: {url}")
            content = fetch_url_content(url)
            if content:
                # 按行处理内容
                lines = content.splitlines()
                category = None  # 当前的分类
                for line in lines:
                    line = line.strip()
                    if not line:  # 忽略空行
                        continue
                    
                    # 清理行中的符号和关键词
                    cleaned_line = clean_line(line)
                    if not cleaned_line:  # 如果该行被删除，跳过
                        continue
                    
                    # 查找频道的相关信息
                    if cleaned_line.startswith("#EXTINF"):
                        # 解析EXTINF，提取分类和频道信息
                        parts = cleaned_line.split(",")
                        if len(parts) >= 2:
                            # 获取group-title（分类）和频道名称
                            group_title_part = [part for part in cleaned_line.split() if part.startswith('group-title')][0]
                            category = group_title_part.split('=')[1].replace('"', "").strip()  # 提取并格式化分类
                            channel_name = parts[1].strip()  # 获取频道名称
                    elif cleaned_line.startswith("http"):  # 播放链接
                        # 存储同一分类下的所有频道及播放链接
                        if category not in category_channels:
                            category_channels[category] = []
                        category_channels[category].append((channel_name, cleaned_line))

        # 将格式化后的分类和频道输出到文件
        for category, channels in category_channels.items():
            # 输出group-title和#genre#
            formatted_category = format_category(category)
            outfile.write(f"{formatted_category},#genre#\n")
            for channel_name, link in channels:
                # 输出频道名称和播放链接
                outfile.write(f"{channel_name},{link}\n")

if __name__ == "__main__":
    format_and_merge_sources(urls, output_file)
    print(f"IPTV源内容已成功合并到 {output_file}")
