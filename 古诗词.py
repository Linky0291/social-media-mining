import time
import csv
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def scrape_gushiwen_multipage():
    # ==========================================
    # 👇 保存路径
    save_path = "D:/python_Lin/爬虫学习实习/爬虫/gushiwen_5_pages.csv"
    # ==========================================

    print("🚀 启动批量爬虫，目标：古诗文网 (前 5 页)...")

    # 设置浏览器
    chrome_options = Options()
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    # chrome_options.add_argument("--headless") # 想看过程就不要取消注释

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    all_data = [] # 用来存放所有页面的数据

    try:
        # ==========================================
        # 🔄 循环开始：从第 1 页爬到第 5 页
        # ==========================================
        for page in range(1, 6): 
            print(f"\n📄 正在读取第 {page} 页...")
            
            # 构造动态 URL
            url = f"https://www.gushiwen.cn/default_{page}.aspx"
            driver.get(url)
            
            # 随机等待 2-4 秒，防止翻页太快被封 IP
            time.sleep(random.uniform(2, 4))

            # 定位诗词卡片
            poem_cards = driver.find_elements(By.CSS_SELECTOR, ".left .sons")
            
            current_page_count = 0

            for card in poem_cards:
                try:
                    # 提取标题 (过滤广告)
                    try:
                        title = card.find_element(By.CSS_SELECTOR, "b").text
                    except:
                        continue

                    # 提取作者
                    source_text = card.find_element(By.CSS_SELECTOR, ".source").text
                    
                    # 提取内容
                    content = card.find_element(By.CSS_SELECTOR, ".contson").text.replace('\n', ' ')

                    # 存入大列表
                    all_data.append([title, source_text, content])
                    current_page_count += 1
                    
                    # 打印一条简略信息证明活着
                    print(f"  抓取: {title} ({source_text})")

                except Exception:
                    continue
            
            print(f"  ✅ 第 {page} 页完成，本页获取 {current_page_count} 首。")

        # ==========================================
        # 💾 所有页面爬完后，统一保存
        # ==========================================
        print("-" * 60)
        print("💾 正在保存所有数据...")
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(["标题", "朝代/作者", "正文"])
            writer.writerows(all_data)

        print(f"🎉 大功告成！共爬取 {len(all_data)} 首诗词。")
        print(f"📄 文件路径: {save_path}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_gushiwen_multipage()