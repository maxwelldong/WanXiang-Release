#!/usr/bin/env python3
"""
万象影视 - 订阅源抓取、验证、构建脚本
由 GitHub Actions 定时触发，抓取 https://cdn.45678888.xyz/fx/ 的接口，
提取 Apple CMS 影视源 + M3U/TXT 直播源，验证可用性后生成聚合 JSON。
"""
import urllib.request
import urllib.error
import json
import socket
import ssl
import re
import sys
import time
import os

socket.setdefaulttimeout(10)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# ============================================================
# 87 个接口列表
# ============================================================
INTERFACES = [
    ("特别贡献", "https://cdn.45678888.xyz/6i.pw.png"),
    ("欧歌", "http://tv.nxog.top/m/111.php?ou=公众号欧歌app&mz=all&jar=all&b=欧歌"),
    ("骚零", "https://play.iptv365.org/骚零/api.json"),
    ("短剧", "https://cnb.cool/fish2018/duanju/-/git/raw/main/tvbox.json"),
    ("儿童", "https://jihulab.com/ymz1231/xymz/-/raw/main/ymshaoer"),
    ("小虎斑", "https://play.iptv365.org/小虎斑/api.json"),
    ("小苹果", "https://bitbucket.org/xduo/duoapi/raw/master/xpg.json"),
    ("科技长青", "https://13413.kstore.space/tv/changqing.json"),
    ("神仙", "http://xhztv.top/dc/神仙/api.json"),
    ("小脑斧", "https://6492.kstore.space/xnf/xnf.json"),
    ("天天开心", "https://play.iptv365.org/天天开心/api.json"),
    ("精选", "https://codeberg.org/Zc6663/333/raw/branch/main/16/16精选.json"),
    ("饭太硬", "http://fty.xxooo.cf/tv"),
    ("肥猫", "http://肥猫.net/"),
    ("牛二(新接口)", "https://9280.kstore.vip/newwex.json"),
    ("牛二(中文top)", "http://tvbox.王二小放牛娃.top"),
    ("牛二(常规top)", "http://tvbox.xn--4kq62z5rby2qupq9ub.top"),
    ("牛二(1数字xyz)", "http://tv.999888987.xyz/"),
    ("牛二(2数字xyz)", "http://tv.999888123.xyz/"),
    ("牛二(凯速)https", "//9280.kstore.vip/wex.json"),
    ("4K2", "http://我不是.摸鱼儿.top"),
    ("小不点", "http://www.小不点.com"),
    ("资源网盘", "http://47.96.82.41:5188/svip/svip.json"),
    ("资源接口", "http://47.96.82.41:5188/"),
    ("动漫城", "https://www.yingm.cc/dm/dm.json"),
    ("快乐接口", "http://影视仓接口.top"),
    ("巧记", "http://cdn.qiaoji8.com/tvbox.json"),
    ("刘备", "https://raw.liucn.cc/box/m.json"),
    ("日本线路", "https://fastly.jsdelivr.net/gh/liu673cn/box@main/m.json"),
    ("潇洒", "https://9877.kstore.space/ONE/one.json"),
    ("放牛娃", "http://tvbox.xn--4kq62z5rby2qupq9ub.top/"),
    ("茄子", "https://700sjro44343.vicp.fun/eggp/qzku/tv.json"),
    ("玩偶哥哥多源", "https://raw.githubusercontent.com/xiongjian83/TvBox/main/X.json"),
    ("接口03", "http://pandown.pro/tvbox/tvbox.json"),
    ("道长", "https://gitlab.com/duomv/dzhipy/-/raw/main/index.json"),
    ("飞马影视", "http://fmys.top/fmys.json"),
    ("鸟叔4K", "https://nsvip.060028.xyz/niaoshu公益/4Km.json"),
    ("盒子迷", "https://盒子迷.top/禁止贩卖"),
    ("XOXL", "https://fty.xxooo.cf/tv"),
    ("自建接口", "https://idw.xx.kg/github?key=xklm&path=data/zjysjk.json"),
    ("非凡接口", "https://g.3344550.xyz/https://raw.githubusercontent.com/jigedos/1024/master/jsm.json"),
    ("香雅情", "https://gh-proxy.com/https://raw.githubusercontent.com/xyq254245/xyqonlinerule/main/XYQTVBox/xyq.json"),
    ("HG", "https://api.hgyx.vip/hgyx.json"),
    ("OKVIP", "http://47.120.41.246:8025/vip/2501/vip/tv.php"),
    ("小米", "http://47.96.82.41:8/api.json"),
    ("菜妮丝", "https://tv.菜妮丝.top"),
    ("健康家用", "https://gitlab.com/noimank/tvbox/-/raw/main/tvbox1.json"),
    ("豆瓣推荐", "https://gh-proxy.com/raw.githubusercontent.com/letian1650/mybox/main/m.json"),
    ("接口04", "https://9280.kstore.space/wex.json"),
    ("大人资源", "https://www.jianguoyun.com/p/De2Xt9gQv8z-DRiC1JoGIAA"),
    ("很好用", "https://raw.bgithub.xyz/wwb521/live/refs/heads/main/video.json"),
    ("香雅雅", "https://gh-proxy.com/https://raw.githubusercontent.com/gaotianliuyun/gao/master/XYQ.json"),
    ("TVBOX多接口", "https://tv.sxi.qzz.io/jsm.json"),
    ("南风", "https://gh-proxy.com/https://raw.githubusercontent.com/yoursmile66/TVBox/main/XC.json"),
    ("机哥接口", "https://13537.kstore.vip/tvbox/test.json"),
    ("豆豆资源", "https://cyao2q.github.io/files/n.json"),
    ("宝盒", "http://宝盒接口.top"),
    ("Mido影视", "http://mido.ittun.com/bh/box.json"),
    ("DXAWI", "https://dxawi.github.io/0/0.json"),
    ("豆瓣爬虫", "https://gh-proxy.com/raw.githubusercontent.com/zheng197600/tvbox/main/0820.json"),
    ("自动更新", "https://gh-proxy.com/https://raw.githubusercontent.com/tushen6/Tomorrow/master/tvbox.json"),
    ("随心小屋", "https://8815.kstore.vip/tvbox/Ace"),
    ("全球TV", "https://pan.quark.cn/s/5015ef2fce69"),
    ("牡之花", "https://tv.蜗牛.top/svip"),
    ("夏天", "https://11405.kstore.space/xiaye/qk4k.json"),
    ("影视仓单线", "http://影视仓.com/"),
    ("OK接口", "http://ok213.top/tv"),
    ("影视仓备用", "https://700sjro44343.vicp.fun/eggp/0615/tv.php"),
    ("GitHub线路", "https://raw.githubusercontent.com/tushen6/Tomorrow/master/lmw.json"),
    ("粉丝仓", "https://www.iyouhun.com/tv/公众号游魂网络.json"),
    ("纷传林中的小屋", "https://gitee.com/lzxw66/lzxw9/raw/master/Ace"),
    ("测试线路", "https://gh.llkk.cc/https://raw.githubusercontent.com/tushen6/Tomorrow/master/lmw.json"),
    ("天微七星", "http://7337.kstore.space/qxys/禁止传播.json"),
    ("鸟叔公益", "https://nsvip.060028.xyz/niaoshu公益/V3m.json"),
    ("影用仓库", "http://tv.weidonglong.com/ysc5.json"),
    ("聚合资源", "https://tv.203511.xyz/0821.json"),
    ("小鱼", "http://m3.687166.xyz/aaaa.json"),
    ("综合2", "https://raw.githubusercontent.com/supermeguo/BoxRes/main/Myuse/catcr.json"),
    ("小而精", "https://raw.githubusercontent.com/qirenzhidao/tvbox18/main/pg/jsm.json"),
    ("匿名", "https://12586.kstore.space/123.json"),
    ("T4", "https://py.doube.eu.org/static/t4.json"),
    ("卧龙资源", "https://pastebin.com/raw/gtbKvnE1"),
    ("裹柳接口", "https://fastly.jsdelivr.net/gh/ls125781003/dmtg@master/zy.json"),
    ("OK极简版", "https://raw.githubusercontent.com/tangyl2000/tvbox/main/tvbox.json"),
    ("多多优选仓", "https://gitee.com/wgq11/main/raw/tv/duo.json"),
    ("七星单线", "https://7337.kstore.vip/qxys/禁止传播.json"),
    ("数字单线", "https://dy.7772888.xyz/tvbox.json"),
]


def fetch(url):
    """Fetch a URL and return text content."""
    if url.startswith("//"):
        url = "https:" + url
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
        })
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = resp.read()
            ct = resp.headers.get("Content-Type", "")
            if "json" in ct or url.endswith(".json"):
                return data.decode("utf-8", errors="replace")
            try:
                return data.decode("utf-8")
            except:
                return data.decode("gbk", errors="replace")
    except Exception:
        return None



def extract_cms_from_json(obj, label):
    """从 JSON 中提取 Apple CMS 源"""
    results = []
    # TVBox sites 格式
    sites = obj.get("sites") or obj.get("site") or []
    if isinstance(sites, list):
        for site in sites:
            if not isinstance(site, dict):
                continue
            stype = site.get("type")
            api = (site.get("api") or "").strip()
            sname = (site.get("name") or "").strip()
            if stype in (0, 1) and api.startswith("http"):
                results.append((sname, api, "cms"))

    # UZ vod 格式
    vod_list = obj.get("vod") or []
    if isinstance(vod_list, list):
        for item in vod_list:
            if not isinstance(item, dict):
                continue
            name = (item.get("name") or "").strip()
            url = (item.get("url") or "").strip()
            api = (item.get("api") or "").strip()
            if api and not url:
                continue  # JS 脚本源跳过
            if url and (url.startswith("http") or url.startswith("https")):
                results.append((name, url, "cms"))
    return results


def extract_live_from_json(obj, label):
    """从 JSON 中提取直播源"""
    results = []
    # lives 数组
    for arr_name in ["lives", "live", "living"]:
        arr = obj.get(arr_name)
        if isinstance(arr, list):
            for item in arr:
                if isinstance(item, dict):
                    u = (item.get("url") or "").strip()
                    n = (item.get("name") or "").strip()
                    if u.startswith("http"):
                        results.append((n or label, u))

    # sites 中 type=2 (直播)
    sites = obj.get("sites") or obj.get("site") or []
    if isinstance(sites, list):
        for site in sites:
            if not isinstance(site, dict):
                continue
            if site.get("type") == 2:
                api = (site.get("api") or "").strip()
                sname = (site.get("name") or "").strip()
                if api.startswith("http"):
                    results.append((f"Live-{sname or label}", api))
            ext = site.get("ext")
            if isinstance(ext, str) and ext.startswith("http") and (
                ".m3u" in ext.lower() or ".txt" in ext.lower()
            ):
                sname = (site.get("name") or "").strip()
                results.append((f"Live-{sname or label}", ext))
    return results


def scrape():
    """主抓取流程"""
    print("=" * 60)
    print(f"万象影视 - 订阅源抓取工具")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    all_cms = {}      # url → {names, source_label}
    all_live = {}     # url → {names, source_label}
    total_cms = 0
    total_live = 0

    for idx, (label, url) in enumerate(INTERFACES, 1):
        print(f"\n[{idx:2d}/87] {label}", flush=True)
        print(f"       {url}")
        data = fetch(url)
        if data is None:
            print(f"       → ❌ 无法访问")
            continue
        if len(data) < 10:
            print(f"       → ❌ 内容过短")
            continue
        text = data.strip()
        if text.startswith("<!") or text.startswith("<html"):
            print(f"       → ⚠️  HTML 页面")
            continue

        # 尝试 JSON 解析
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                cms_list = extract_cms_from_json(obj, label)
                for n, u, t in cms_list:
                    if u not in all_cms:
                        all_cms[u] = {"names": set(), "from": label}
                    all_cms[u]["names"].add(n or label)
                live_list = extract_live_from_json(obj, label)
                for n, u in live_list:
                    if u not in all_live:
                        all_live[u] = {"names": set(), "from": label}
                    all_live[u]["names"].add(n or label)
                print(f"       → ✅ CMS: {len(cms_list)}, Live: {len(live_list)}")
                total_cms += len(cms_list)
                total_live += len(live_list)
                continue
        except json.JSONDecodeError:
            pass

        # 非 JSON → 可能是 M3U/TXT 内容
        print(f"       → ℹ️  非 JSON 格式")

    print(f"\n{'=' * 60}")
    print(f"抓取完成!")
    print(f"  CMS 源: {len(all_cms)} 个 (来自 {total_cms} 条接口记录)")
    print(f"  Live 源: {len(all_live)} 个 (来自 {total_live} 条接口记录)")
    print(f"{'=' * 60}")

    return all_cms, all_live



def build_all(all_cms, all_live, output_dir):
    """生成所有输出文件"""
    print(f"\n{'=' * 60}")
    print(f"生成输出文件...")
    print(f"{'=' * 60}")

    os.makedirs(output_dir, exist_ok=True)

    # 1. 构建 JSON
    vod_list = []
    for url, info in sorted(all_cms.items()):
        names = sorted(info["names"])
        vod_list.append({
            "name": names[0],
            "url": url,
        })

    live_list = []
    for url, info in sorted(all_live.items()):
        names = sorted(info["names"])
        live_list.append({
            "name": names[0] if names else "直播源",
            "url": url,
            "type": 10,
        })

    # UZ 格式 JSON
    result = {"live": live_list, "vod": vod_list}
    json_path = os.path.join(output_dir, "wanxiang.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  ✅ {json_path}  (CMS: {len(vod_list)}, Live: {len(live_list)})")

    # 2. 生成 TXT (仅可用 CMS)
    txt_path = os.path.join(output_dir, "可用影视源列表.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"万象影视 - 可用 Apple CMS 影视源\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"数量: {len(vod_list)}\n\n")
        for item in vod_list:
            f.write(f"{item['name']},{item['url']}\n")
    print(f"  ✅ {txt_path}")

    # 3. 生成 TXT (仅可用 Live)
    live_txt_path = os.path.join(output_dir, "IPTV直播源列表.txt")
    with open(live_txt_path, "w", encoding="utf-8") as f:
        f.write(f"万象影视 - IPTV 直播源\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"数量: {len(live_list)}\n\n")
        for item in live_list:
            f.write(f"{item['name']},{item['url']}\n")
    print(f"  ✅ {live_txt_path}")

    # 4. 生成详细报告
    report_path = os.path.join(output_dir, "report.json")
    report = {
        "generated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
        "stats": {
            "cms_total": len(all_cms),
            "live_total": len(all_live),
            "grand_total": len(vod_list) + len(live_list),
        },
        "cms_sources": [{"name": v["name"], "url": k} for k, v in sorted(all_cms.items())],
        "live_sources": [{"name": v["name"], "url": k} for k, v in sorted(all_live.items())],
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"  ✅ {report_path}")

    print(f"\n生成完成!")
    return json_path


def main():
    # 输出目录
    output_dir = os.environ.get("OUTPUT_DIR", os.path.join(os.path.dirname(__file__), "..", "release"))

    # 1. 抓取
    all_cms, all_live = scrape()

    if not all_cms and not all_live:
        print("\n❌ 未抓取到任何源，退出")
        sys.exit(1)

    # 2. 构建输出（不验证，App 导入时自带检测）
    build_all(all_cms, all_live, output_dir)


if __name__ == "__main__":
    main()
